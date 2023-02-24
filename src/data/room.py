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

"""The room DB Model."""

from typing import TYPE_CHECKING

from data.base.node import Field, Node
from data.handler.description import DescriptionHandler
from data.handler.exits import ExitHandler
from data.exit import Exit

if TYPE_CHECKING:
    from data.character import Character


class Room(Node):

    """Node to represent a room."""

    barcode: str = Field(bpk=True, default="unknown", unique=True)
    title: str = "no title"
    description: DescriptionHandler = Field(default_factory=DescriptionHandler)
    exits: ExitHandler = Field(default_factory=ExitHandler)

    def look(self, character: "Character") -> str:
        """The character wants to look at this room.

        Args:
            character (Character): who looks at this room.

        """
        description = self.description.format()
        exits = self.exits.get_visible_by(character)
        if exits:
            exits = "Obvious exits: " + ", ".join(
                [exit.get_name_for(character) for exit in exits]
            )
        else:
            exits = "There is no obvious exit."

        lines = [
            self.title,
            "",
            description,
            "",
            exits,
        ]

        return "\n".join(lines)
