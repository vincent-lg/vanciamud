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

"""Asynchronous messaging server.

cRUX is a thin layer allowing inter-protocol communication.  CRUX
is a server, a TCP server that accepts messages formatted in a specific
way.  The CRUX protocol is only started once, by the portal process,
and then HOST services connect to it to send messages.  The CRUX
implementation is responsible for deciding what to do with these messages.

Communication implementation (both for the CRUX server and the
HOST clients) can be found in `service/cmd.py`.

"""

import asyncio
from itertools import count
import os
import platform
import secrets
from typing import Any, Optional

import keyring

from service.base import BaseService
from service.cmd import CmdMixin
from service.net_event import NetEvent


class Service(CmdMixin, BaseService):

    """CRUX service, creating a light messaging server.

    This service should be created by the portal (see `service/portal.py`).
    Each process can instantiate a HOST service, which is a client
    designed to connect to the CRUX server.  The CRUX is a simple TCP server
    that can be used to trade data with the various processes.

    """

    name = "CRUX"

    async def init(self):
        """Asynchronously initialize the service.

        This method should be overridden in subclasses.  It is called by
        `start`` before sub-services are created.  It plays the role of
        an asynchronous constructor for the service, and service attributes
        often are created there for consistency.

        """
        await super().init()
        self.net_events = []
        self.serving_task = None
        self.readers = {}
        self.writers = {}
        self.cnx_id = count(1)
        self.reader_ids = {}
        self.writer_ids = {}
        self.type_cnx = {}

        # Create a random secret key which will be used to sign/unsign
        # CRUX messages between server and clients.
        self.logger.debug("Generating a secret key")
        token = secrets.token_urlsafe(32)
        if platform.system() == "Linux":
            with open(".crux", "w", encoding="utf-8") as file:
                file.write(token)
        else:
            keyring.set_password("talismud", "CRUX", token)
        self.read_secret_key()

    async def setup(self):
        """Set the CRUX server up."""
        await super().setup()
        self.schedule_hook("receive", self.hook_receive)
        self.schedule_hook("send", self.hook_send)
        self.schedule_hook("error_read", self.error_read)
        self.schedule_hook("error_write", self.error_write)
        self.serving_task = asyncio.create_task(self.start_serving())

    async def cleanup(self):
        """Clean the service up before shutting down."""
        if self.serving_task:
            self.serving_task.cancel()

        # Remove the secret key.
        if platform.system() == "Linux":
            os.remove(".crux")
        else:
            keyring.delete_password("talismud", "CRUX")

    async def start_serving(self):
        """Prepare to serve."""
        try:
            await self.create_server()
        except asyncio.CancelledError:
            pass
        except Exception:
            self.logger.exception("CRUX: an error occurred while serving")

    async def create_server(self):
        """Create the CRUX server."""
        port = 4005
        self.logger.debug(
            f"CRUX: preparing to listen on localhost, port {port}"
        )
        self.trace_net(
            destination=None,
            name="cnx",
            hint=f"Listening on localhost:{port}",
        )

        try:
            server = await asyncio.start_server(
                self.handle_connection, "localhost", port
            )
        except asyncio.CancelledError:
            pass

        addr = server.sockets[0].getsockname()
        self.logger.debug(f"CRUX: Serving on {addr}")

        async with server:
            try:
                await server.serve_forever()
            except asyncio.CancelledError:
                pass
            except Exception:
                self.logger.exception(
                    "CRUX: An exception was raised when serving:"
                )

    async def handle_connection(self, reader, writer):
        """Handle a new connection."""
        addr = writer.get_extra_info("peername")
        self.logger.debug(f"CRUX: {addr} has just connected.")
        self.readers[reader] = writer
        self.writers[writer] = reader
        cnx_id = next(self.cnx_id)
        self.writer_ids[writer] = cnx_id
        self.reader_ids[reader] = cnx_id
        self.type_cnx[cnx_id] = "?"
        self.trace_net(
            destination=reader,
            name="new_cnx",
            hint=f"new connection from {addr}",
        )

        try:
            await self.read_commands(reader, writer)
        except asyncio.CancelledError:
            pass
        finally:
            if not writer.is_closing():
                await writer.drain()
                writer.close()
                await writer.wait_closed()

    async def broadcast(
        self, cmd_name: str, args: Optional[dict[str, Any]] = None
    ):
        """Broadcast a message to all connected HOST clients.

        Args:
            cmd_name (str): the command to send.
            args (dict): the command arguments.

        For all connected HOST clients, send the command with a different
        command ID.  This cannot effectively be used to retrieve
        answers from clients, but to inform them of a change
        they should note.

        """
        args = {} if args is None else args
        for writer in tuple(self.readers.values()):
            await self.send_cmd(writer, cmd_name, args)

    async def error_read(self, reader):
        """An error occurred when reading from reader."""
        writer = self.readers.pop(reader, None)
        if writer is None:
            self.logger.error(
                "CRUX: connection was lost with a host, but the associated "
                "writer cannot be found."
            )
            self.trace_net(
                destination=reader,
                name="lost_cnx_read",
                hint="connection was lost with this host when reading",
            )
        else:
            self.writers.pop(writer)
            self.logger.info("CRUX: connection to a host was closed.")
            self.trace_net(
                destination=reader,
                name="disc_read",
                hint="normal disconnection when reading",
            )

        await self.parent.error_read(writer)

    async def error_write(self, writer):
        """An error occurred when writing to writer."""
        reader = self.writers.pop(writer, None)
        if reader is None:
            self.logger.error(
                "CRUX: connection was lost with a host, but the associated "
                "reader cannot be found."
            )
            self.trace_net(
                destination=writer,
                name="lost_cnx",
                hint="a connection was lost with this host when writing",
            )
        else:
            self.readers.pop(reader)
            self.logger.info("CRUX: connection to a host was closed.")
            self.trace_net(
                destination=writer,
                name="disc_write",
                hint="normal disconnection when writing",
            )

        await self.parent.error_write(writer)

    async def hook_receive(
        self,
        reader: asyncio.StreamReader,
        cmd_name: str,
        cmd_id: int,
        args: dict[str, Any],
    ) -> None:
        """When a message is received."""
        args = dict(cmd=cmd_name, id=cmd_id, args=args)
        self.trace_net(destination=reader, name="recv", args=args)

    async def hook_send(
        self,
        writer: asyncio.StreamWriter,
        cmd_name: str,
        cmd_id: int,
        args: dict[str, Any],
    ) -> None:
        """When a message is sent."""
        args = dict(cmd=cmd_name, id=cmd_id, args=args)
        self.trace_net(destination=writer, name="send", args=args)

    def trace_net(
        self,
        destination: None | asyncio.StreamWriter | asyncio.StreamReader,
        name: str,
        hint: str | None = None,
        args: None | dict[str, Any] = None,
    ) -> None:
        """Trace a network message."""
        type_cnx = ""
        if destination is not None:
            if isinstance(destination, asyncio.StreamWriter):
                destination = self.writer_ids.get(destination, "?")
            elif isinstance(destination, asyncio.StreamReader):
                destination = self.reader_ids.get(destination, "?")
            type_cnx = self.type_cnx.get(destination, "U")

        self.net_events.append(
            NetEvent(
                destination=destination,
                type=type_cnx,
                name=name,
                hint=hint,
                args=args,
            )
        )
