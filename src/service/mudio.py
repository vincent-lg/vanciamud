# Copyright (c) 2022, LE GOFF Vincent
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.

# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
# OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
# OF THE POSSIBILITY OF SUCH DAMAGE.

"""MudIO service, set to handle input/output on the game level"""

import asyncio
from collections import defaultdict
from datetime import datetime
from importlib import import_module
from pathlib import Path
import traceback
from typing import Any, Dict, Optional, Sequence, Type, Union

from channel.base import Channel
from channel.log import logger as chn_logger
from command.base import Command
from command.log import logger as cmd_logger
from context.base import Context, CONTEXTS
from context.log import logger as ctx_logger
from data.session import Session, OUTPUT_QUEUE
from service.base import BaseService
from tools.logging import Logger


class Service(BaseService):

    """MudIO service, to handle input/output of users.

    Users, in this context, are players (either just connected,
    interacting through a session, or already playing, interacting through
    a character object).  Input is handled here, as well as output
    from the game to users.

    """

    name = "mudIO"

    async def init(self):
        """Asynchronously initialize the service.

        This method should be overridden in subclasses.  It is called by
        `start`` before sub-services are created.  It plays the role of
        an asynchronous constructor for the service, and service attributes
        often are created there for consistency.

        """
        self.output_lock = asyncio.Lock()
        self.contexts = {}
        self.commands = {}
        self.channels = {}
        self.stats = []

    async def setup(self):
        """Set the MudIO up."""
        self.load_contexts()
        self.load_commands()
        self.load_channels()

    async def cleanup(self):
        """Clean the service up before shutting down."""

    def record_stat(
        self,
        session: Session,
        command: str,
        sent: datetime,
        received: datetime,
        executed: datetime,
    ):
        """Record this statistic line, if greater than the Nth line.

        Args:
            session_id (UUID): the session ID of the input.
            input_id (int): the ID associated with this input.
            command (bytes): the command itself.
            sent (datetime): when this command was sent to the game.
            received (datetime): when this command was received by the game.
            executed (datetime): when this command was executed by the game.

        """
        elapsed = (executed - sent).total_seconds()
        for i, (*_, stat_elapsed) in enumerate(self.stats):
            if stat_elapsed < elapsed:
                self.stats.insert(i, (session.uuid, command, elapsed))
                break
        else:
            self.stats.append((session.uuid, command, elapsed))
        self.stats = self.stats[:5]

    def load_contexts(self):
        """Load the contexts dynamically.

        This method is called when the game starts.

        """
        parent = Path()
        paths = (parent / "context",)

        exclude = (
            parent / "context" / "base.py",
            parent / "context" / "log.py",
        )
        forbidden = (Context,)

        # Search the context files.
        ctx_logger.debug("Preparing to load all contexts...")
        loaded = 0
        for path in paths:
            for file_path in path.rglob("*.py"):
                if file_path in exclude or any(
                    to_ex in file_path.parents for to_ex in exclude
                ):
                    continue

                # Search for the module to begin
                if file_path.name.startswith("_"):
                    continue

                # Assume this is a module containing ONE context.
                relative = file_path.relative_to(path)
                pypath = ".".join(file_path.parts)[:-3]
                py_unique = ".".join(relative.parts)[:-3]

                # Try to import it.
                try:
                    module = import_module(pypath)
                except Exception:
                    ctx_logger.exception(
                        f"  An error occurred when importing {pypath}:"
                    )
                    continue

                # Explore the module to try to import ONE context.
                NewContext = None
                for name, value in module.__dict__.items():
                    if name.startswith("_"):
                        continue

                    if (
                        isinstance(value, type)
                        and value not in forbidden
                        and issubclass(value, Context)
                    ):
                        if value.__module__ != pypath:
                            continue

                        if NewContext is not None:
                            NewContext = ...
                            break
                        else:
                            NewContext = value

                if NewContext is None:
                    ctx_logger.warning(
                        f"No context could be found in {pypath}."
                    )
                    continue
                elif NewContext is ...:
                    ctx_logger.warning(
                        "More than one contexts are present "
                        f"in module {pypath}, not loading any."
                    )
                    continue
                else:
                    loaded += 1
                    ctx_logger.debug(
                        f"  Load the context in {pypath} (name={py_unique!r})"
                    )
                    self.contexts[py_unique] = NewContext
                    NewContext.pyname = py_unique

        s = "s" if loaded > 1 else ""
        was = "were" if loaded > 1 else "was"
        ctx_logger.debug(f"{loaded} context{s} {was} loaded successfully.")
        CONTEXTS.clear()
        CONTEXTS.update(self.contexts)

    def load_commands(self):
        """Load the commands dynamically.

        This method is called when the game starts.

        """
        commands = self.dynamically_load(
            Command,
            cmd_logger,
            parent=Path("command"),
            exclude=(
                Path("command/args"),
                Path("command/base.py"),
                Path("command/log.py"),
                Path("command/namespace.py"),
                Path("command/special"),
            ),
        )
        self.commands.update(commands)
        s = "s" if len(commands) > 1 else ""
        was = "were" if len(commands) > 1 else "was"
        cmd_logger.info(
            f"{len(commands)} command{s} {was} successfully loaded."
        )
        for path, command in commands.items():
            command.pyname = path
            command.extrapolate(command.file_path)

        Command.service = self

    def load_channels(self):
        """Dynamically load channels."""
        channels = self.dynamically_load(
            Channel,
            chn_logger,
            parent=Path("channel"),
            exclude=(Path("channel/log.py"), Path("channel/base.py")),
        )
        self.channels.update(channels)
        s = "s" if len(channels) > 1 else ""
        was = "were" if len(channels) > 1 else "was"
        chn_logger.info(
            f"{len(channels)} channel{s} {was} successfully loaded."
        )
        for channel in channels.values():
            name = getattr(channel, "name", ...)
            if name is ...:
                channel.name = channel.__name__.lower()
            channel.create_commands()

        Channel.service = self

    def handle_input(self, session: Session, command: str, sent: datetime):
        """Handle input from a session.

        Args:
            session (Session): the session sending input.
            command (str): the sent command as a string.

        """
        received = datetime.utcnow()
        context = session.context
        context.handle_input(command)
        if context.hide_input:
            command = "*" * 8

        executed = datetime.utcnow()
        self.record_stat(session, command, sent, received, executed)

    async def send_output(self, input_id: Optional[int] = None):
        """Send output synchronously."""
        host = self.parent.host
        data = self.parent.data
        to_send = defaultdict(list)

        async with self.output_lock:
            while not OUTPUT_QUEUE.empty():
                ssid, msg = OUTPUT_QUEUE.get_nowait()
                to_send[ssid].append(msg)

            # At this point, messages have been sorted by session.
            for ssid, messages in to_send.items():
                session = data.get_session(ssid)
                msg = b"\n".join(messages)

                # Display the context prompt.
                prompt = session.context.get_prompt()
                if isinstance(prompt, str):
                    prompt = prompt.encode(session.encoding, errors="replace")

                if prompt:
                    msg = msg + b"\n\n" + prompt

                # Send the output to the session.
                await host.send_cmd(
                    host.writer,
                    "output",
                    dict(
                        session_id=session.uuid,
                        output=msg,
                        input_id=input_id,
                    ),
                )

    def handle_error(self, session: Session) -> None:
        """Handle an error as an exception.

        This method will be called whenever a traceback occurs while
        executing an input.

        Args:
            session (Session): the session.

        """
        session.msg(traceback.format_exc().strip())

    @staticmethod
    def dynamically_load(
        base_class: Type[Any],
        logger: Logger,
        parent: Union[Path, Sequence[Path]],
        exclude: Optional[Sequence[Path]] = None,
    ) -> Dict[str, Any]:
        """Dynamically load any objects from modules.

        Args:
            base_class (type): any class.
            logger (Logger): the logger to indicate errors.
            parent (Path or sequence of Path): the parent(s).
            exclude (Sequence of Path, optional): the path to exclude.

        Returns:
            loaded (dict): the loaded classes.

        In each parent, all the Python modules will be searched recurisvely
        and loaded.  Inside these files, the one class inheriting
        from the base class will be loaded and returned.  If more
        than one class from this base class is defined in this file,
        log an error.

        """
        paths = (parent,) if isinstance(parent, Path) else parent
        exclude = exclude or ()

        # Search the module files.
        logger.debug("Preparing to load all module files...")
        loaded = {}
        for path in paths:
            for file_path in path.rglob("*.py"):
                if file_path in exclude or any(
                    to_ex in file_path.parents for to_ex in exclude
                ):
                    continue

                # Search for the module to begin.
                if file_path.name.startswith("_"):
                    continue

                # Assume this is a module containing ONE class <- base_class.
                relative = file_path.relative_to(path)
                pypath = ".".join(file_path.parts)[:-3]
                py_unique = ".".join(relative.parts)[:-3]

                # Try to import it.
                try:
                    module = import_module(pypath)
                except Exception:
                    logger.exception(
                        f"  An error occurred when importing {pypath}:"
                    )
                    continue

                # Explore the module to try to import ONE class.
                subclass = None
                for name, value in module.__dict__.items():
                    if name.startswith("_"):
                        continue

                    if (
                        isinstance(value, type)
                        and value is not base_class
                        and issubclass(value, base_class)
                    ):
                        if value.__module__ != pypath:
                            continue

                        if subclass is not None:
                            subclass = ...
                            break
                        else:
                            subclass = value

                if subclass is None:
                    logger.warning(
                        f"No class inheriting from {base_class.__name__!r} "
                        f"could be found in {pypath}."
                    )
                    continue
                elif subclass is ...:
                    logger.warning(
                        "More than one class inheriting from "
                        f"{base_class.__name__!r} are present "
                        f"in module {pypath}, not loading any."
                    )
                    continue
                else:
                    logger.debug(
                        f"  Load the class in {pypath} (name={py_unique!r})"
                    )
                    loaded[py_unique] = subclass
                    subclass.file_path = file_path

        return loaded
