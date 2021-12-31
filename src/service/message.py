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

"""Class containing the message logic and mode."""

from enum import Flag
import pickle
from typing import Any

from itsdangerous import Serializer


class MessageMode(Flag):

    """Various message modes, can be combined."""

    UNVERIFIED = 1
    SIGNED = 2
    ENCRYPTED = 4

    def get_content(self, message: bytes) -> tuple[str, int, dict[str, Any]]:
        """Read a message, handling the various modes.

        If successful, return the unpickled message as a tuple of string
        (command name), int (command ID), and dict (command arguments).
        If unsuccessful, raise a ValueError.

        Args:
            message (bytes): the messae as a bytestring.

        Returns:
            message (tuple): the unpickled message if valid.

        """
        # Browse the various members.
        for mode in iter(reversed(MessageMode)):
            if mode in self:
                method = getattr(self, f"get_{mode.name.lower()}_message")
                message = method(message)
                if isinstance(message, tuple):
                    # Stop here.
                    return message

        # If the message isn't unpickled yet.
        if isinstance(message, bytes):
            message = self.get_unverified_message(message)

        return message

    def get_unverified_message(
        self, message: bytes
    ) -> tuple[str, int, dict[str, Any]]:
        """Unpickle a simple unverified message.

        This mode should not be used, even on a local network.

        Args:
            message (bytes): the message as a string of bytes.

        Returns:
            message (tuple): the unpickled message.

        """
        return pickle.loads(message)

    def get_signed_message(
        self, message: bytes
    ) -> tuple[str, int, dict[str, Any]]:
        """Read and unpickled a signed message.

        The message will only be unpickled if it's correctly signed.

        Args:
            message (bytes): the message as a string of bytes.

        Returns:
            message (tuple): the message as an unpickled tuple.

        """
        try:
            obj = self.serializer.loads(message)
        except (pickle.PickleError, EOFError):
            raise ValueError("can't unpickle the signed message")

        return obj

    def compose(self, cmd: str, cmd_id: int, args: dict[str, Any]) -> bytes:
        """Return a message, suitable for sending, following the message mode.

        Args:
            cmd (str): the command name.
            cmd_id (int): the command ID.
            args (dict): the command arguments as a dictionary.

        Returns
            message (bytes): the message as a string of bytes.

        """
        message = b""
        for mode in MessageMode:
            if mode in self:
                method = getattr(self, f"compose_{mode.name.lower()}")
                message = method(cmd, cmd_id, args, message)

        return message

    def compose_unverified(
        self, cmd: str, cmd_id: int, args: dict[str, Any], message: bytes
    ) -> bytes:
        """Return a message in an unverified mode.

        Args:
            cmd (str): the command name.
            cmd_id (int): the command ID.
            args (dict): the command arguments as a dictionary.
            message (bytes): the message passed by others methods (ignored).

        Returns:
            message (bytes): the message as a string of bytes.

        Note:
            The message argument will be ignored at this point.

        """
        return pickle.dumps((cmd, cmd_id, args))

    def compose_signed(
        self, cmd: str, cmd_id: int, args: dict[str, Any], message: bytes
    ) -> bytes:
        """Return a message in a signed mode.

        Args:
            cmd (str): the command name.
            cmd_id (int): the command ID.
            args (dict): the command arguments as a dictionary.
            message (bytes): the message passed by others methods (ignored).

        Returns:
            message (bytes): the message as a string of bytes.

        Note:
            The message argument will be ignored at this point.

        """
        return self.serializer.dumps((cmd, cmd_id, args))

    @classmethod
    def setup(cls, sign_key: bytes, encryption_key: bytes):
        """Setup the enumeration, adding class variables (but not members).

        This method will add configuration class variables in the
        enumeration itself, but these shouldn't be new members.

        Args:
            sign_key (bytes): the key used to sign messages.
            encryption_key (bytes): the key used to encrypt messages.

        """
        cls.serializer = Serializer(sign_key, serializer=pickle)
