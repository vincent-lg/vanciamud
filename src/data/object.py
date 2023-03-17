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

"""The object DB Model."""

from typing import TYPE_CHECKING

from data.base.node import Field, Node
from data.handler.namespace import NamespaceHandler
from data.handler.types import TypeHandler

if TYPE_CHECKING:
    from data.character import Character
    from data.prototype.object import ObjectPrototype


class Object(Node):

    """Node to represent an object."""

    barcode: str = Field("unset", unique=True)
    prototype: "ObjectPrototype" = None
    db: NamespaceHandler = Field(default_factory=NamespaceHandler)
    types: TypeHandler = Field(default_factory=TypeHandler)

    def get_name_for(self, character: "Character", number: int = 1) -> str:
        """Return the name for this character in the specified quantity.

        Args:
            character (Character): the character receiving the object's name.
            number (int, optional): the number of objects (default 1).

        Returns:
            name (str): the name to display.

        """
        if prototype := self.prototype:
            name = prototype.get_name_for(character, number)
        else:
            name = "unknown"

        return name
