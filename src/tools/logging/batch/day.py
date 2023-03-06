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

"""Day batch class."""

from dataclasses import asdict

from tools.logging.batch.abc import BaseBatch
from tools.logging.message import Message

DEFAULT_FORMAT = "-- New hour {year}-{month}-{day}:"


class Day(BaseBatch):

    """Batch to group messages by day."""

    def init(self):
        """Initialize the batch object."""
        self.last_day = None
        self.new_batch_message = DEFAULT_FORMAT

    def should_batch(self, message: Message) -> bool:
        """Return whether this message can run in the current batch."""
        should = False
        if last_day := self.last_day:
            should = last_day == self._get_day(message)

        return should

    def new_batch(self, message: Message) -> None:
        """Method called when the batch has expired.

        This method will be called when `handler.batch.should_batch(message)`
        returns `False` for a new message.  The batch can take opportunity
        to log a new message for a new batch.

        Notice that the batch object itself can be updated but is
        not recreated.

        Args:
            message (Message): the first message in the new batch.

        Returns:
            None

        """
        self.last_day = self._get_day(message)
        self.handler.always_log(
            self.new_batch_message.format(**asdict(message))
        )

    @staticmethod
    def _get_day(message: Message) -> str:
        """Return the message day as a string."""
        return message.time.strftime("%Y-%m-%d")
