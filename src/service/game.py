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

from uuid import UUID

from service.base import BaseService
from service.origin import Origin


class Service(BaseService):

    """The game's main service."""

    name = "game"
    sub_services = ("host",)

    async def init(self):
        """Asynchronously initialize the service.

        This method should be overridden in subclasses.  It is called by
        `start`` before sub-services are created.  It plays the role of
        an asynchronous constructor for the service, and service attributes
        often are created there for consistency.

        """
        self.game_id = None
        self.output_tasks = {}
        self.cmds_task = None
        self.sessions = {}

    async def setup(self):
        """Set the game up."""
        self.services["host"].schedule_hook(
            "connected", self.connected_to_CRUX
        )

    async def cleanup(self):
        """Clean the service up before shutting down."""
        for uuid, task in tuple(self.output_tasks.items()):
            task.cancel()
            self.output_tasks.pop(uuid, None)

        if self.cmds_task:
            self.cmds_task.cancel()

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
