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

"""The exit object, not destined to be sotred in the database.

WARNING:
    Contrary to most objects, the exit is not to be stored in
    the database in its own table.  Instead, it is stored
    (pickled) in the room itself.

"""

from enum import Enum
from typing import Optional, Set, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from data.room import Room


class Exit:

    """Simsple object to represent a one-way exit between two rooms."""

    room = None

    def __init__(
        self,
        direction: "Direction",
        origin: Union["Room", str],
        destination: Union["Room", str],
        name: str,
        aliases: Optional[Set[str]] = None,
    ):
        self.direction = direction
        self.origin_barcode = origin = getattr(origin, "barcode", origin)
        self.destination_barcode = getattr(destination, "barcode", destination)
        self.name = name
        self.aliases = aliases and set(aliases) or set()

    def __repr__(self):
        origin = self.origin_barcode
        destination = self.destination_barcode
        return (
            f"<Exit(direction={self.direction}, origin={origin}, "
            f"destination={destination}, name={self.name!r})"
        )

    def __str__(self):
        origin = self.origin_barcode
        destination = self.destination_barcode
        return (
            f"Exit {self.name!r} ({self.direction.value}) "
            f"from {origin} to {destination}"
        )

    @property
    def origin(self):
        """Return the origin."""
        results = Exit.room.repository.select(
            Exit.room.barcode == self.origin_barcode
        )
        return results[0] if results else None

    @property
    def destination(self):
        """Return the destination."""
        results = Exit.room.repository.select(
            Exit.room.barcode == self.destination_barcode
        )
        return results[0] if results else None

    @property
    def back(self):
        """Return the back exit, if found in the destination."""
        room = self.destination
        if room is None:
            return

        opposite = self.direction.opposite
        exit = room.exits.get_in(opposite)
        if exit is None or exit.destination is not self.origin:
            return

        return exit


class Direction(Enum):

    """Direction enumeration."""

    EAST = "east"
    SOUTHEAST = "southeast"
    SOUTH = "south"
    SOUTHWEST = "southwest"
    WEST = "west"
    NORTHWEST = "northwest"
    NORTH = "north"
    NORTHEAST = "northeast"
    DOWN = "down"
    UP = "up"

    @property
    def opposite(self):
        """Return the opposite exit."""
        return _OPPOSITES[self]


_OPPOSITES = {
    Direction.EAST: Direction.WEST,
    Direction.SOUTHEAST: Direction.NORTHWEST,
    Direction.SOUTH: Direction.NORTH,
    Direction.SOUTHWEST: Direction.NORTHEAST,
    Direction.WEST: Direction.EAST,
    Direction.NORTHWEST: Direction.SOUTHEAST,
    Direction.NORTH: Direction.SOUTH,
    Direction.NORTHEAST: Direction.SOUTHWEST,
    Direction.DOWN: Direction.UP,
    Direction.UP: Direction.DOWN,
}
