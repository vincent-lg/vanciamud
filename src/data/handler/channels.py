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

"""Channels custom field, to hold channels."""

from typing import Union

from pygasus.model import CustomField

from channel.base import Channel


class Channels(set):

    """A set of channels.

    Channels are saved as strings (their unique name), the channel objects
    themselves are cached when retrieved.

    """

    def __init__(self, *args, **kwargs):
        self.parent = None
        self.field = None
        super().__init__(*args, **kwargs)
        self._cache = {}

    def add(self, channel: Union[str, Channel]):
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

        if path not in self:
            super().add(path)
            self._cache[path] = channel
            self.save()

    def clear(self):
        """Remove all channels."""
        if len(self) > 1:
            super().clear()
            self._cache.clear()
            self.save()

    def discard(self, channel: Union[str, Channel]):
        """Remove a channel.

        Args:
            channel (str or Channel): the channel to remove.

        """
        if isinstance(channel, str):
            path = channel
        else:
            path = channel.path

        if path in self:
            super().discard(path)
            self.save()

    def has(self, channel: Union[str, Channel]) -> bool:
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

        return path in self

    def remove(self, channel: Union[str, Channel]):
        """Remove a channel.

        Args:
            channel (str or Channel): the channel to remove.

        """
        if isinstance(channel, str):
            path = channel
        else:
            path = channel.path

        if path in self:
            super().remove(path)
            self.save()

    def save(self):
        """Save the list of channels in the parent."""
        type(self.parent).repository.update(
            self.parent, self.field, set(), self.copy()
        )


class ChannelsField(CustomField):

    """A set of channels stored in a string."""

    field_name = "channels"

    def add(self):
        """Add this field to a model.

        Returns:
            annotation type (Any): the type of field to store.

        """
        return str

    def to_storage(self, value):
        """Return the value to store in the storage engine.

        Args:
            value (Any): the original value in the field.

        Returns:
            to_store (Any): the value to store.
            It must be of the same type as returned by `add`.

        """
        return " ".join(value)

    def to_field(self, value: str):
        """Convert the stored value to the field value.

        Args:
            value (Any): the stored value (same type as returned by `add`).

        Returns:
            to_field (Any): the value to store in the field.
            It must be of the same type as the annotation hint used
            in the model.

        """
        if value:
            channels = value.split(" ")
        else:
            channels = set()

        return Channels(channels)
