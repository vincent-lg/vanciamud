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

"""Channel handler, to store channels for a character."""

from typing import Union

from channel.base import Channel
from data.handler.abc import BaseHandler


class ChannelHandler(BaseHandler):

    """A set of channels.

    Channels are saved as strings (their unique name), the channel objects
    themselves are cached when retrieved.

    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._channels = set()

    def __getstate__(self):
        return self._channels

    def __setstate__(self, channels):
        self._channels = channels

    def add(self, channel: str | Channel):
        """Add a channel for this character.

        Args:
            channel (str or Channel): the channel to add.

        """
        if isinstance(channel, str):
            path = channel
            channel = Channel.service.channels.get(path)
            if channel is None:
                raise ValueError(f"cannot find the channel of path {path!r}")
        else:
            path = channel.path

        if path not in self._channels:
            self._channels.add(path)
            self.save()

    def clear(self):
        """Remove all channels."""
        if len(self._channels) > 1:
            self._channels.clear()
            self.save()

    def discard(self, channel: str | Channel):
        """Remove a channel.

        Args:
            channel (str or Channel): the channel to remove.

        """
        if isinstance(channel, str):
            path = channel
        else:
            path = channel.path

        if path in self._channels:
            self._channels.discard(path)
            self.save()

    def has(self, channel: str | Channel) -> bool:
        """Return whether this channel is in the set.

        Args:
            channel (str or Channel): the channel to test.

        Returns:
            has (bool): whether this set has this channel.

        """
        if isinstance(channel, str):
            path = channel
        else:
            path = channel.path

        return path in self._channels

    def remove(self, channel: str | Channel):
        """Remove a channel.

        Args:
            channel (str or Channel): the channel to remove.

        """
        if isinstance(channel, str):
            path = channel
        else:
            path = channel.path

        if path in self._channels:
            self._channels.remove(path)
            self.save()
