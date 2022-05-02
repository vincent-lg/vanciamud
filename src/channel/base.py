# Copyright (c) 2022, LE GOFF Vincent
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


"""Channel base class.

All channels should inherit from this base class.

Most of the configuration is specified in class attributes.  Some methods
can also be altered.

"""

from typing import Sequence, Union, TYPE_CHECKING

from command.base import Command
from command.special.channel import JoinChannel, LeaveChannel, UseChannel
from service.base import BaseService

if TYPE_CHECKING:
    from data.character import Character


class Channel:

    """Base class for channels.

    Channel configuration is mostly stored as class attributes
    (see below).  Some methods can also be overriden to alter behavior.

    Class attributes:
        name (str): the channel name (default to `__name__.lower()`)

    """

    alias: Union[str, Sequence[str]] = ()
    permissions: str = ""
    description: str = "not set"

    # Don't replace this attribute:
    service: BaseService
    character = None

    @classmethod
    def can_access(cls, character: "Character") -> bool:
        """Return whether this character can access this channel.

        Args:
            character (Character): the character accessing this channel.

        """
        if cls.permissions:
            return character.permissions.has(cls.permissions)

        return True

    @classmethod
    def create_commands(cls):
        """Create the commands for this channel."""
        join = type(f"Join{cls.__name__}", (JoinChannel,), dict(channel=cls))
        join.name = f"+{cls.name.lower()}"
        join.permissions = cls.permissions
        Command.service.commands[f"+join_{cls.name}"] = join

        leave = type(
            f"Leave{cls.__name__}", (LeaveChannel,), dict(channel=cls)
        )
        leave.name = f"-{cls.name.lower()}"
        leave.permissions = cls.permissions
        Command.service.commands[f"+leave_{cls.name}"] = leave

        use = type(f"Use{cls.__name__}", (UseChannel,), dict(channel=cls))
        use.name = cls.name
        use.permissions = cls.permissions
        Command.service.commands[f"+use_{cls.name}"] = use

    @classmethod
    @property
    def connected(cls):
        """Return the characters connected to this channel."""
        if (cached := getattr(cls, "_cached_connected", None)) is not None:
            return cached

        storage = cls.service.parent.data.engine
        table = storage.tables["character"]
        model = storage.models["character"]
        connected = model.repository.select(
            table.c.channels.contains(f" {cls.name} ")
        )
        cls._cached_connected = connected
        return connected

    @classmethod
    def add_subscriber(cls, character: "Character"):
        """Add a character to the channel, regardless of permissions.

        Args:
            character (Character): the character to add.

        If needed, the channel's name will be added to the list
        of channels this character currently has.

        """
        if character not in cls.connected:
            cls._cached_connected.append(character)
            character.channels.add(cls.name)

    @classmethod
    def remove_subscriber(cls, character: "Character"):
        """Remove the character from the channel, regardless of permissions.

        Args:
            character (Character): the character to remove from this channel.

        If needed, the channel's name will be remove from the list
        of channels this character currently has.

        """
        if character in cls.connected:
            cls._cached_connected.remove(character)
            character.channels.discard(cls.name)

    @classmethod
    def msg_from(cls, character: "Character", message: str):
        """Send the message to all connected subscribers.

        Args:
            character (Character): the character sending this message.
            message (str: the message to be sent.

        """
        for subscriber in cls.connected:
            if subscriber is character:
                subscriber.msg(f"[{cls.name}] You say: {message}")
            else:
                subscriber.msg(
                    f"[{cls.name}] {character.name} says: {message}"
                )
