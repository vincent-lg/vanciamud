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

"""Base batch."""

from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING

from tools.logging.message import Message

if TYPE_CHECKING:
    from tools.logging.handler.abc import BaseHandler


class BaseBatch(metaclass=ABCMeta):

    """A batch object on a handler."""

    def __init__(self, handler: "BaseHandler"):
        self.handler = handler
        self.init()

    @abstractmethod
    def init(self):
        """Initialize the batch object."""
        pass

    @abstractmethod
    def should_batch(self, message: Message) -> bool:
        """Return whether this message can run in the current batch."""
        return True

    @abstractmethod
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
        pass
