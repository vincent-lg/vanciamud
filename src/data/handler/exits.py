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

"""Exits custom field, to hold room exits."""

import pickle
from typing import Optional, Set, Tuple, TYPE_CHECKING

from pygasus.model import CustomField

from data.exit import Exit, Direction

if TYPE_CHECKING:
    from data.character import Character
    from data.room import Room


class ExitHandler(dict):

    """A dictionary-like handler for exits."""

    def __init__(self, *args, **kwargs):
        self.parent = None
        self.field = None
        super().__init__(*args, **kwargs)

    def __str__(self):
        exits = []
        for direction in Direction:
            exits.append(str(self.get(direction)))

        return f"[{', '.join(exits)}]"

    @property
    def linked(self) -> Tuple[Exit]:
        """Only return linked exits in the direction order."""
        exits = []
        for direction in Direction:
            exit = self.get(direction)
            if exit:
                exits.append(exit)

        return tuple(exits)

    def get_in(self, direction: Direction) -> Optional[Exit]:
        """Return the exit in this direction or None.

        Args:
            direction (Direction): the direction.

        If the exit doesn't exist, returns None.

        """
        return self.get(direction)

    def get_visible_by(self, character: "Character") -> Tuple[Exit]:
        """Only return visible exits by this character."""
        return [exit for exit in self.linked if exit.can_see(character)]

    def add(
        self,
        direction: Direction,
        destination: "Room",
        name: str,
        aliases: Optional[Set[str]] = None,
    ) -> Exit:
        """Add a new exit, if no exit exists in this direction.

        Args:
            direction (Direction): the direction in which to build this exit.
            destination (Room): the destination of this exit.
            name (str): the exit's name.
            aliases (set, opt): the optional aliases of this exit.

        If an exit already exists in this direction, raisess a ValueError.

        """
        if self.get_in(direction):
            raise ValueError(
                f"an exit already exists in the direction: {direction}"
            )

        origin = self.parent
        exit = Exit(direction, origin, destination, name, aliases)
        self[direction] = exit
        self.save()
        return exit

    def save(self):
        """Save the exits."""
        type(self.parent).repository.update(
            self.parent, self.field, {}, self.copy()
        )


class ExitsField(CustomField):

    """A dictionary of exits, stored in a bytestring."""

    field_name = "exits"

    def add(self):
        """Add this field to a model.

        Returns:
            annotation type (Any): the type of field to store.

        """
        return bytes

    def to_storage(self, value: dict):
        """Return the value to store in the storage engine.

        Args:
            value (Any): the original value in the field.

        Returns:
            to_store (Any): the value to store.
            It must be of the same type as returned by `add`.

        """
        return pickle.dumps(value)

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
            value = pickle.loads(value)
        else:
            value = {}

        return ExitHandler(value)

    @staticmethod
    def from_blueprint(handler: ExitHandler, blueprint: dict):
        """Set the exits according to the dictionary."""
        pass
