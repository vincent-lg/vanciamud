# Copyright (c) 2022 LE GOFF Vincent
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

"""Channel commands."""

from command.base import Command


class ChannelCommand(Command):

    """Abstract command for channels."""

    @classmethod
    def get_help(cls, character=None):
        """Return the help for this command."""
        return (
            super()
            .get_help(character)
            .format(
                channel=cls.channel.name, description=cls.channel.description
            )
        )


class JoinChannel(ChannelCommand):

    """Join the {channel} channel.

    Syntax:
        +{channel}

    This command is used to join the {channel} channel.  Once connected
    to it, you can use the {channel} command to talk on this channel.

    Example:
      {channel} Hello there!

    """

    category = "Channels"
    in_help = False

    def run(self):
        """Join the channel."""
        character = self.character
        channel = self.channel
        if character in channel.connected:
            self.msg(
                f"You are already connected to the {channel.name} channel."
            )
        else:
            channel.add_subscriber(character)
            self.msg(f"You now are connected to the {channel.name} channel.")


class LeaveChannel(ChannelCommand):

    """Leave the {channel} channel.

    Syntax:
        -{channel}

    This command is used to leave the {channel} channel.
    Once disconnected, you can no longer talk on this channel,
    not receive messages from it, unless you reconnect to it.

    """

    category = "Channels"
    in_help = False

    def run(self):
        """Join the channel."""
        character = self.character
        channel = self.channel
        if character not in channel.connected:
            self.msg(f"You are not connected to the {channel.name} channel.")
        else:
            channel.remove_subscriber(character)
            self.msg(
                f"You now are disconnected from the {channel.name} channel."
            )


class UseChannel(ChannelCommand):

    """Use the {channel} channel.

    {description}

    Syntax:
      {channel} <message>

    This command is used to talk on the {channel} channel.

    Example:
      {channel} I have a message for everyone connected to this channel!

    """

    category = "Channels"
    args = Command.new_parser()
    args.add_argument("text", dest="message")

    @classmethod
    def can_run(cls, character) -> bool:
        """Can the command be run by the specified character?

        Args:
            character (Character): the character to run this command.

        """
        return character in cls.channel.connected

    def run(self, message):
        """Join the channel."""
        character = self.character
        channel = self.channel
        channel.msg_from(character, message)
