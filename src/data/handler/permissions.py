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

"""Permissions custom field, to hold permissions."""

from pygasus.model import CustomField


class Permissions(set):

    """A set of permissions."""

    def __init__(self, *args, **kwargs):
        self.parent = None
        self.field = None
        super().__init__(*args, **kwargs)

    def add(self, permission: str):
        """Add permissions.

        Args:
            permission (str): the permission to add.

        """
        if " " in permission:
            raise ValueError("a permission cannot contain spaces")

        if permission not in self:
            super().add(permission)
            self.save()

    def clear(self):
        """Remove all permissions."""
        if len(self) > 1:
            super().clear()
            self.save()

    def discard(self, permission: str):
        """Remove a permission.

        Args:
            permission (str): the permission to remove.

        """
        if permission in self:
            super().discard(permission)
            self.save()

    def has(self, permission: str) -> bool:
        """Return whether this permission is in the set.

        Args:
            permission (str): the permission to test.

        Returns:
            has (bool): whether this set has this permission.

        """
        return permission in self

    def remove(self, permission: str):
        """Remove a permission.

        Args:
            permission (str): the permission to remove.

        """
        if permission in self:
            super().remove(permission)
            self.save()

    def save(self):
        """Save the list of contexts in the parent."""
        type(self.parent).repository.update(
            self.parent, self.field, set(), self.copy()
        )


class PermissionsField(CustomField):

    """A set of permissions stored in a string."""

    field_name = "permissions"

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
            permissions = value.split(" ")
        else:
            permissions = set()

        return Permissions(permissions)
