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

"""Contexts custom field, to hold contexts."""

import pickle

from pygasus.model import CustomField


class Contexts(list):

    """An extended list of contexts for a character."""

    def __init__(self, contexts=None):
        self.parent = None
        self.field = None
        self._contexts = contexts or []

    def save(self):
        """Save the list of contexts in the parent."""
        type(self.parent).repository.update(
            self.parent, self.field, {}, self._contexts
        )


class ContextsField(CustomField):

    """A list stored in a pickled bytestring."""

    field_name = "contexts"

    def add(self):
        """Add this field to a model.

        Returns:
            annotation type (Any): the type of field to store.

        """
        return bytes

    def to_storage(self, value):
        """Return the value to store in the storage engine.

        Args:
            value (Any): the original value in the field.

        Returns:
            to_store (Any): the value to store.
            It must be of the same type as returned by `add`.

        """
        if isinstance(value, Contexts):
            value = value._contexts
        return pickle.dumps(value)

    def to_field(self, value: bytes):
        """Convert the stored value to the field value.

        Args:
            value (Any): the stored value (same type as returned by `add`).

        Returns:
            to_field (Any): the value to store in the field.
            It must be of the same type as the annotation hint used
            in the model.

        """
        data = pickle.loads(value)
        if isinstance(data, Contexts):
            data = data._contexts
        return Contexts(contexts=data)
