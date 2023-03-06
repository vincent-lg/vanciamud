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

"""File handler."""

import codecs
from dataclasses import asdict
from pathlib import Path

from tools.logging.handler.abc import BaseHandler
from tools.logging.level import Level
from tools.logging.message import Message

DEFAULT_FORMAT = (
    "{year}-{month}-{day} {hour}:{minute}:{second},{ms} [{level}] {message}"
)


class File(BaseHandler):

    """File handler."""

    def init(self):
        """Initialize the logger."""
        self.format = DEFAULT_FORMAT if self.format is None else self.format
        self.output_file = None
        self.encoding = "utf-8"

    def setup(self, output_file: str | Path, encoding: str = "utf-8") -> None:
        """Configure the file handler.

        Args:
            output_file (str or Path): the output file.  The parent directory
                    will be selected from the logger's option "directory",
                    if set.
            encoding (str, optional): the encoding.  By default, utf-8.

        """
        directory = self.logger.directory
        path = output_file
        if isinstance(output_file, str):
            path = Path(output_file)

        if not isinstance(path, Path):
            raise TypeError(
                "a pathlib.Path or str should be given as output_file, "
                f"received {output_file} (type={type(output_file)})"
            )

        if not path.is_absolute():
            path = directory / str(path)

        self.output_file = path

        # Check that the encoding exists.
        _ = codecs.lookup(encoding)
        self.encoding = encoding

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

        if self.output_file:
            with self.output_file.open("a", encoding=self.encoding) as file:
                file.write(message)
