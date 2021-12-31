# Copyright (c) 2021, LE GOFF Vincent
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

"""Game service."""

import asyncio
from datetime import datetime
from uuid import UUID

from data.session import QUEUES
from service.base import BaseService
from service.origin import Origin


class Service(BaseService):

    """The game's main service."""

    name = "game"
    sub_services = ("host", "data")

    async def init(self):
        """Asynchronously initialize the service.

        This method should be overridden in subclasses.  It is called by
        `start`` before sub-services are created.  It plays the role of
        an asynchronous constructor for the service, and service attributes
        often are created there for consistency.

        """
        self.output_event = asyncio.Event()
        self.game_id = None
        self.spread_output_task = None
        self.sessions = {}

    async def setup(self):
        """Set the game up."""
        self.data = self.services["data"]
        self.host = self.services["host"]
        self.host.schedule_hook("connected", self.connected_to_CRUX)
        await self.start_spread_output()

    async def cleanup(self):
        """Clean the service up before shutting down."""
        if self.spread_output_task:
            self.spread_output.cancel()

    async def start_spread_output(self):
        """Start the task to spread output to all sessions."""
        self.spread_output_task = asyncio.create_task(self.spread_output())

    async def spread_output(self):
        """Read output, send it to the session."""
        await self.output_event.wait()

        # Spread outputs contained in queues.
        for session_id, queue in QUEUES.items():
            # Dump the list of messages.
            if queue.empty():
                continue

            messages = []
            while not queue.empty():
                messages.append(queue.get_nowait())
            messages = b"\n".join(messages)
            print(f"spread {messages} to {session_id}")

            # Send these messages.
            await self.host.send_cmd(
                self.host.writer,
                "output",
                dict(session_id=session_id, output=messages, input_id=0),
            )

    async def connected_to_CRUX(self, writer):
        """The host is connected to the CRUX server."""
        host = self.services["host"]
        self.logger.debug("host: send register_game")
        await host.send_cmd(
            writer, "register_game", dict(pid=self.process.pid, has_admin=True)
        )

    async def error_read(self):
        """Cannot read from CRUX anymore, prepare to shut down."""
        self.logger.warning(
            "A read error happened on the connection to CRUX, "
            "stop the process."
        )
        self.process.should_stop.set()

    async def error_write(self):
        """Cannot write to CRUX anymore, prepare to shut down."""
        self.logger.warning(
            "A write error happened on the connection to CRUX, "
            "stop the process."
        )
        self.process.should_stop.set()

    # Command handlers
    async def handle_registered_game(
        self,
        origin: Origin,
        game_id: str,
        sessions: list[UUID],
        **kwargs,
    ):
        """A new game process wants to be registered."""
        self.logger.info(f"The game is now registered under ID {game_id}")
        self.game_id = game_id

    async def handle_stop_game(self, origin: Origin, game_id: str):
        """Stop this game process."""
        self.logger.info(f"The game of ID {game_id} is asked to stop.")
        if self.game_id == game_id:
            self.logger.debug("Shutting down the game...")
            self.process.should_stop.set()

    async def handle_input(
        self,
        origin: Origin,
        session_id: UUID,
        command: bytes,
        input_id: int,
        **kwargs,
    ):
        """Handle input from Telnet clients.

        Telnet clients send commands and expect output
        (not necessarily right away).

        Args:
            session_id (UUID): the session from which this command come.
            command (bytes): the sent bytes.
            input_id (int): the ID of this command.

        This number, generated by the Telnet portal, is unique to
        this input.  Including it in the answer allows to make sure
        the link between input and output is established.  Of course,
        the MUD can contact other sessions as well, or even contact
        them after a few seconds, in which case this new output
        won't be linked to an input.

        Answer:
            When the command is received (not processed yet), send an answer
            right away.  This is useful for stats.  When the command
            is processed, send an 'output' message.

        """
        host = self.services["host"]
        await host.answer(origin, dict(received=datetime.utcnow()))
        session = self.data.get_session(session_id)
        command = command.decode("utf-8", errors="replace")
        output = f"Old command: {session.db.cmd}"
        session.db.cmd = command
        await host.send_cmd(
            host.writer,
            "output",
            dict(
                session_id=session_id,
                output=output,
                input_id=input_id,
            ),
        )

    async def handle_new_session(
        self,
        origin: Origin,
        session_id: UUID,
        creation: datetime,
        ip_address: str,
        secured: bool,
        **kwargs,
    ):
        """Handle a new connection session.

        The session is connected to Telnet (whether Telnet
        or Telnet-SSL).  The portal then contacts the game process
        to let it know a new session has been created.  The portal
        doesn't store the session except in memory, but the game stores it
        in its database.

        Args:
            session_id (UUID): the new session ID (should be unique).
            creation (datetime): the datetime at which this session connected.
            ip_address (str): the session's IP address.
            secured (bool): is it a secured session (SSL)?

        Answer:
            None.

        """
        await self.data.new_session(session_id, creation, ip_address, secured)
