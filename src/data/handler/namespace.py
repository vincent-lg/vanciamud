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

"""Namespace custom field."""

import pickle

from pygasus.model import CustomField

_NOT_SET = object()


class Namespace(dict):

    """A namespace, holding attribute-like flexible data."""

    def __init__(self, *args, **kwargs):
        self.parent = None
        self.field = None
        super().__init__(*args, **kwargs)

    def __getattr__(self, key):
        if key in ("parent", "field"):
            return object.__getattr__(self, key)

        value = super().__getitem__(key)
        return value

    def __setattr__(self, key, value):
        if key in ("parent", "field"):
            object.__setattr__(self, key, value)
        else:
            super().__setitem__(key, value)
            self.save()

    def __delattr__(self, key):
        if key in ("parent", "field"):
            object.__delattr__(self, key)
        else:
            super().__delitem__(key)
            self.save()

    def __getitem__(self, key):
        value = super().__getitem__(key)
        return value

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self.save()

    def __delitem__(self, key):
        super().__delitem__(key)
        self.save()

    def clear(self):
        if self:
            super().clear()
            self.save()

    def pop(self, key, default=_NOT_SET):
        if default is _NOT_SET:
            value = super().pop(key)
        else:
            value = super().pop(key, default)
        self.save()
        return value

    def popitem(self):
        pair = super().popitem()
        self.save()
        return pair

    def setdefault(self, key, default=None):
        super().setdefault(key, default)
        self.save()

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        self.save()

    def save(self):
        """Save the dictionary into the parent."""
        type(self.parent).repository.update(
            self.parent, self.field, {}, self.copy()
        )


class NamespaceField(CustomField):

    """A dictionary stored in a pickled bytestring."""

    field_name = "namespace"

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
        return pickle.dumps(value.copy())

    def to_field(self, value: bytes):
        """Convert the stored value to the field value.

        Args:
            value (Any): the stored value (same type as returned by `add`).

        Returns:
            to_field (Any): the value to store in the field.
            It must be of the same type as the annotation hint used
            in the model.

        """
        return Namespace(pickle.loads(value))
