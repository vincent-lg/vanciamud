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

"""This module doesn't contain a service, but a mixin.

The `CmdMixin` is used to exchange commands that have been pickled.  It needs
a `reader` and `writer` to work and will cache what it receives until it
can unpickle something useful.

This mixin is used by the CRUX (server) and HOST (client) service, as
communication is similar.

"""

import asyncio
import pickle
from struct import calcsize, error as struct_error, pack, unpack
import time
from typing import Any, Optional

from async_timeout import timeout as async_timeout

# Constants
INITIAL_PACKET_FORMAT_STRING = "!Q"
INITIAL_PACKET_SIZE = calcsize(INITIAL_PACKET_FORMAT_STRING)


class CmdMixin:

    """Command mixin, used to transfer commands with arguments.

    A command and argument are pickled into a tuple and sent over a writer.
    The reader on the opposite side of the connection then caches the
    result in a `BytesIO` object and subsequently tries to unpickle it.  If
    it succeeds, it tries to handle the command, which calls a method
    of a subclass of the mixin, or a parent service's.  See service/host.py
    for an example and more explanation on the process.

    Asynchronous methods:
        write_cmd(writer, command name, arguments): send a command.
        wait_for_cmd(reader, command name, timeout): wait for a command
                to be received.

    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.commands = {}

    async def init(self):
        """The service is initialized."""
        self.register_hook("error_read")
        self.register_hook("error_write")

    async def read_commands(self, reader):
        """Enter an asynchronous loop to read commands from `reader`."""
        # Creates the asynchronous queue for the reader if it doesn't exist:
        queue = self.commands.get(reader)
        if queue is None:
            queue = asyncio.Queue()
            self.commands[reader] = queue

        while True:
            # Read exactly 8 bytes, the length of the packet to read.
            try:
                initial_packet = await reader.readexactly(INITIAL_PACKET_SIZE)
            except ConnectionError:
                await queue.put(None)
                await self.call_hook("error_read", reader)
                return
            except asyncio.CancelledError:
                await queue.put(None)
                return
            except asyncio.IncompleteReadError:
                # An EOF occurred, disconnect.
                await queue.put(None)
                return
            except Exception:
                self.logger.exception(
                    "An exception was raised on read_commands"
                )
                await self.call_hook("error_read", reader)
                return

            # Extract the size, using `struct.unpack`.
            try:
                packet = unpack(INITIAL_PACKET_FORMAT_STRING, initial_packet)
            except struct_error:
                # Not a valid initial packet, disconnect.
                await queue.put(None)
                return

            # Read exactly `size` bytes.  The read byte should contain
            # a pickled collection.
            size = packet[0]
            try:
                data = await reader.readexactly(size)
            except ConnectionError:
                await queue.put(None)
                await self.call_hook("error_read", reader)
                return
            except asyncio.CancelledError:
                await queue.put(None)
                return
            except asyncio.IncompleteReadError:
                # An EOF occurred, disconnect.
                self.logger.warning(
                    f"EOF was encountered while reading a promise of {size} "
                    "bytes.  This connection is closed, but there might "
                    "be unprocessed data."
                )
                await queue.put(None)
            except Exception:
                self.logger.exception(
                    "An exception was raised on read_commands"
                )
                await self.call_hook("error_read", reader)
                return

            # Unpcikle the data.
            try:
                obj = pickle.loads(data)
            except (pickle.PickleError, EOFError):
                # The stream can't be read,t it's an obvious error at
                # that point.
                self.logger.exception(
                    "An error occurred while unpickling a CRUX command:"
                )
                await self.call_hook("error_read", reader)
            else:
                # An object has been unpickled.
                # If it's a command, it should be a tuple (str, {arguments})
                # NOTE: this might benefit from match when match is available.
                await self.parse_and_process_command(reader, queue, obj)

    async def parse_and_process_command(
        self, reader: asyncio.StreamReader, queue: asyncio.Queue, cmd: Any
    ):
        """Parse and process the CRUX command.

        The command object should be a tuple of two elements:
        the command name and the command arguments in a dictionary.
        However, this will be tested in the following method.

        Args:
            reader (StreamReader): the reader object.
            queue (asyncio.Queue): the command queue for this reader.
            cmd (Any): the command object.

        """
        if not isinstance(cmd, tuple):
            self.logger.debug(
                f"Buffer: invalid command, {cmd!r} isn't a tuple"
            )
        elif len(cmd) != 2:
            self.logger.debug(
                f"Buffer: invalid command, {cmd!r} should be of length 2"
            )
        elif not isinstance(cmd[0], str):
            self.logger.debug(
                f"Buffer: invalid command, {cmd[0]!r} should be a string"
            )
        elif not isinstance(cmd[1], dict):
            self.logger.debug(
                f"Buffer: invalid command, {cmd[1]!r} should "
                "be a dictionary"
            )
        elif not all(isinstance(key, str) for key in cmd[1].keys()):
            self.logger.debug(
                f"Buffer: invalid command, {cmd[1]!r} should be "
                "a dictionary with string as keys"
            )
        else:
            # Valid command, process it.
            await queue.put(cmd)
            cmd, kwargs = cmd
            await self.process_command(reader, cmd, kwargs)

    async def process_command(self, reader, cmd: str, kwargs: dict[str, Any]):
        """Process a command sent by `reader`.

        Args:
            reader (StreamReader): the stream reader that read this command.
            cmd (str): the command name.
            kwargs (dict): the command arguments.

        The method to handle this command will be searched in this
        service and in parent services.

        """
        service = self
        while (method := getattr(service, f"handle_{cmd}", None)) is None:
            service = service.parent
            if service is None:
                break

        if method:
            try:
                await method(reader, **kwargs)
            except asyncio.CancelledError:
                pass
            except Exception:
                self.logger.exception(
                    "An exception was raised while calling a handler "
                    f"method: 'handle_{cmd}':"
                )
        else:
            self.logger.warning(
                f"Can't process the {cmd!r} command, no handler for it"
            )

    async def send_cmd(
        self,
        writer: asyncio.StreamWriter,
        cmd_name: str,
        args: Optional[dict[str, Any]] = None,
    ):
        """
        Send a command to writer, as a tuple.

        Args:
            writer (StreamWriter): to whom to send this command.
            cmd_name (str): the command name.
            args (dict, opt): the arguments to pickle.

        """
        args = args or {}
        encoded = pickle.dumps((cmd_name, args))
        initial_packet = pack(INITIAL_PACKET_FORMAT_STRING, len(encoded))
        stream = initial_packet + encoded

        try:
            writer.write(stream)
            await writer.drain()
        except (ConnectionError, asyncio.CancelledError):
            await self.call_hook("error_write", writer)
        except Exception:
            await self.call_hook("error_write", writer)
            self.logger.exception("An error occurred on sending a command:")

    async def wait_for_cmd(
        self,
        reader: asyncio.StreamReader,
        cmd_name: str,
        timeout: Optional[float] = None,
    ):
        """Wait for the specified command, if it happens before a timeout.

        Args:
            reader (StreamReader): reader of the command.
            cmd_name (str): name of the command to wait for.
            timeout (float, optional): how much to wait in seconds.

        If the timeout is not None, waits for the specified number of
        seconds and returns `False` if the command wasn't received.  If
        the command was received, returns `True`.  If the timeout is kept
        to `None`, waits indefinitely for the command to be received
        (this method will return `True` or will have to be cancelled
        somehow).

        """
        begin = time.time()
        while (queue := self.commands.get(reader)) is None and (
            timeout is None or time.time() - begin < timeout
        ):
            await asyncio.sleep(0.1)

        if queue is None:
            return (None, {})

        try:
            if timeout is not None:
                timeout = timeout - (time.time() - begin)
                timeout = max(timeout, 0.5)

            async with async_timeout(timeout):
                while received := await queue.get():
                    if received is None:
                        return (False, {})

                    if cmd_name == "*" or received[0] == cmd_name:
                        return (True, received[1])
        except (asyncio.CancelledError, asyncio.TimeoutError):
            return (False, {})
        except Exception:
            self.logger.exception("An error occurred while waiting.")
