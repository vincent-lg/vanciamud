# Copyright (c) 2023, LE GOFF Vincent
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

"""Stream handler."""

from typing import Text, TextIO

from dataclasses import asdict

from tools.logging.handler.abc import BaseHandler
from tools.logging.level import Level
from tools.logging.message import Message

DEFAULT_FORMAT = "[{level}] {message}"


class Stream(BaseHandler):

    """Stream handler."""

    def init(self):
        """Initialize the logger."""
        self.format = DEFAULT_FORMAT if self.format is None else self.format
        self.output = None

    def setup(self, output: Text | TextIO) -> None:
        """Configure the stream handler.

        Args:
            output (stream): the output stream.

        """
        self.output = output

    def log(self, level: Level | None, message: str | Message) -> None:
        """Log a message.

        Args:
            level (None or Level): the level.  If `None`, always log.
            message (str or Message): the message to log.

        If the message is a `Message` object, format it.

        """
        if isinstance(message, Message):
            message = self.format.format(**asdict(message))

        if not message.endswith("\n"):
            message = message + "\n"

        self.output.write(message)
