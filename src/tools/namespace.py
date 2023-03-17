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


"""Generic proxy namespace.

This proxy, accessible with `obj.db`, saves
in the parent's namespace.

"""

from typing import Any, Optional, Tuple

_NOT_SET = object()


class ProxyNamespace:

    """Proxy namespace, accessible through `obj.db`."""

    def store_on(self, parent):
        """Return the object with a namespace."""
        raise NotImplementedError

    @property
    def key_pattern(self):
        """Return the key pattern to store the attribute in the namespace."""
        return "_key_"

    def __init__(self, parent: Any):
        self._parent = parent
        self._model = self.store_on(parent)

    def __getattr__(self, key: str) -> Any:
        if key in ("_parent", "_model"):
            return object.__getattribute__(self, key)

        key = self._transform_key(key)
        value = self._model.db[key]
        return value

    def __setattr__(self, key: str, value: Any):
        if key in ("_parent", "_model"):
            object.__setattr__(self, key, value)
        else:
            key = self._transform_key(key)
            self._model.db[key] = value

    def __delattr__(self, key: str):
        if key in ("_parent", "_model"):
            object.__delattr__(self, key)
        else:
            key = self._transform_key(key)
            del self._model.db[key]

    def __getitem__(self, key: str) -> Any:
        key = self._transform_key(key)
        value = self._model.db[key]
        return value

    def __setitem__(self, key: str, value: Any):
        key = self._transform_key(key)
        self._model.db[key] = value

    def __delitem__(self, key: str):
        key = self._transform_key(key)
        del self._model.db[key]

    def clear(self):
        """Clear the command attributes."""
        cmd_key = self._transform_key("")
        for key in tuple(self._model.db.keys()):
            if key.startswith(cmd_key):
                del self._model.db[key]

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """Get the key or a default value.

        Args:
            key (str): the key to get.
            default (any, optional): the value if key isn't found.

        Returns:
            value or default: the found value (or default).

        """
        key = self._transform_key(key)
        value = self._model.db.get(key, default)
        return value

    def pop(self, key: str, default: Any = _NOT_SET) -> Any:
        """Remove and return a value or default."""
        key = self._transform_key(key)
        args = [key]
        if default is not _NOT_SET:
            args.append(default)
        return self._model.db.pop(*args)

    def popitem(self) -> Tuple[str, Any]:
        """Remove and return the last pair (key, value)."""
        cmd_key = self._transform_key("")
        keys = [
            key for key in self._model.db.keys() if key.startswith(cmd_key)
        ]
        if keys:
            key = keys[-1]
            return self._model.db.pop(key)

        raise KeyError("empty namespace")

    def setdefault(self, key: str, default: Optional[Any] = None) -> Any:
        """Return or set with default.

        Args:
            key (str): the key to set.
            default (any): the value to return if key is present.

        Returns:
            self[key] if key in self else default

        """
        key = self._transform_key(key)
        return self._model.db.setdefault(key, default)

    def update(self, *args, **kwargs):
        """Update the namespace."""
        cmd_key = self._transform_key("")
        keys = dict(*args, **kwargs)
        to_update = {}
        for key, value in keys.items():
            key = cmd_key + key
            to_update[key] = value
        self._model.db.update(to_update)

    def _transform_key(self, key: str) -> str:
        """Transform the key in a valid attribute name."""
        transformed = self.key_pattern
        transformed += type(self._parent).pyname.replace(".", "_")
        transformed += f"_{key}"
        return transformed
