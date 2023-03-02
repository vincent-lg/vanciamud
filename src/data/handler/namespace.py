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

"""Namespace handler to store flexible data."""

from typing import Any

from data.handler.abc import BaseHandler

_NOT_SET = object()


class NamespaceHandler(BaseHandler):

    """A namespace, holding attribute-like flexible data."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._data = {}

    def __getstate__(self):
        return {key: value for key, value in self.__dict__.items() if key.startswith("_")}

    def __setstate__(self, attrs):
        self.__dict__.update(attrs)

    def __getattr__(self, key):
        if key == "model" or key.startswith("_"):
            return object.__getattr__(self, key)

        value = self._data[key]
        return value

    def __setattr__(self, key, value):
        if key == "model" or key.startswith("_"):
            super().__setattr__(key, value)
        else:
            self._data[key] = value
            self.save()

    def __delattr__(self, key):
        if key in ("model", "_data"):
            object.__delattr__(self, key)
        else:
            del self._data[key]
            self.save()

    def __contains__(self, element: Any) -> bool:
        return element in self._data

    def __repr__(self):
        return repr(self._data)

    def __str__(self):
        return str(self._data)

    def __getitem__(self, key):
        value = self._data[key]
        return value

    def __setitem__(self, key, value):
        self._data[key] = value
        self.save()

    def __delitem__(self, key):
        del self._data[key]
        self.save()

    def clear(self):
        if self._data:
            self._data.clear()
            self.save()

    def get(self, key: str, value: Any = _NOT_SET):
        if value is _NOT_SET:
            return self._data.get(key)

        return self._data.get(key, value)

    def items(self):
        return self._data.items()

    def keys(self):
        return self._data.keys()

    def pop(self, key: str, default: any = _NOT_SET):
        if default is _NOT_SET:
            value = self._data.pop(key)
        else:
            value = self._data.pop(key, default)
        self.save()
        return value

    def popitem(self):
        pair = self._data.popitem()
        self.save()
        return pair

    def setdefault(self, key, default=None):
        value = self._data.setdefault(key, default)
        self.save()
        return value

    def update(self, *args, **kwargs):
        self._data.update(*args, **kwargs)
        self.save()

    def values(self):
        return self._data.values()
