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

"""Base type, from which all types should inherit."""

from typing import Optional, TYPE_CHECKING

from data.decorators import lazy_property
from data.type.abc import TypeMetaclass
from data.type.namespace import TypeNamespace

if TYPE_CHECKING:
    from data.object import Object
    from data.prototype.object import ObjectPrototype


class BaseType(metaclass=TypeMetaclass):

    """Base type, from which all type inherit."""

    name: str
    allowed = set()
    forbidden = set()
    stackable: bool = False

    def __init__(
        self,
        prototype: Optional["ObjectPrototype"],
        object: Optional["Object"],
    ) -> None:
        self.prototype = prototype
        self.object = object

    @lazy_property
    def db(self):
        """Return the proxy namespace for this type."""
        return TypeNamespace(self)

    def setup_prototype(self, **kwargs):
        """Setup the prototype with options."""
        pass

    def setup_object(self, **kwargs):
        """Setup the object with options."""
        pass
