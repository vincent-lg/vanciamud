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

"""Base handler."""

from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING

from tools.logging.batch.abc import BaseBatch
from tools.logging.level import Level
from tools.logging.message import Message

if TYPE_CHECKING:
    from tools.logging.logger import Logger


class BaseHandler(metaclass=ABCMeta):

    """A basic handler."""

    def __init__(
        self,
        logger: "Logger",
        level: Level,
        batch: BaseBatch | None = None,
        format: str | None = None,
    ):
        self.logger = logger
        self.level = level
        self.batch = batch
        self.format = format
        self.init()

    @abstractmethod
    def init(self):
        """Initialize the logger."""
        pass

    def always_log(self, message: str | Message):
        """Always log this message, no matter its level.

        Args:
            message (str or Message): the message to log.

        If the message is a `Message` object, format it.

        """
        self.log(level=None, message=message)

    @abstractmethod
    def log(self, level: Level | None, message: str | Message) -> None:
        """Log a message.

        Args:
            level (None or Level): the level.  If `None`, always log.
            message (str or Message): the message to log.

        If the message is a `Message` object, format it.

        """
        pass

    def can_process(self, level: Level, message: Message) -> bool:
        """Return whether this handler can process this log message.

        By default, it only compares its level with the message's level.
        You can override this method to perform more filters.

        Args:
            level (Level): the log level.
            message (Message): the message to log.

        Returns:
            can_process (bol): whether this handler can process this message.

        """
        return self.level <= level

    def process(self, level: Level | None, message: str | Message) -> None:
        """Process the log message.

        Args:
            level (None or Level): the level.  If `None`, always log.
            message (str or Message): the message to log.

        If the message is a `Message` object, format it.

        """
        if batch := self.batch:
            if isinstance(message, str):
                raise ValueError("processing log message: received a string")

            if not batch.should_batch(message):
                batch.new_batch(message)

        self.log(level, message)
