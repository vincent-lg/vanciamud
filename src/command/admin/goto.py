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

from command import Command
from data.room import Room


class Goto(Command):

    """Go to a new room or location.

    Usage:
      goto
      goto <alias>
      goto <room barcode>
      goto =<alias>
      goto -<alias>

    This command allows to move from room to room with no constraint.
    To move to a room, specify its barcode as argument:
      goto <barcode>
    You can associate aliases with some rooms you frequently visit.
    To do so, enter the alias to assign to this room after an equal sign:
      goto =office
    This will associate the current room where you are with the alias
    'office'.  You can then move back to this room like this:
      goto office
    (If your alias is an active room barcode, the latter will have
    precedence.  You cannot override barcodes.)
    To see your current aliases, just type `goto` without arguments:
      goto
    If you want to remove an alias, you can specify the alias name
    following a dash:
      goto -office

    """

    args = Command.new_parser()
    group = args.add_group()
    group.optional = True
    nothing = group.add_branch("list_aliases")
    equal_alias = group.add_branch("add_alias")
    equal_alias.add_argument("symbols", "=")
    equal_alias.add_argument("word", dest="destination")
    minus_alias = group.add_branch("del_alias")
    minus_alias.add_argument("symbols", "-")
    minus_alias.add_argument("word", dest="destination")
    destination = group.add_branch("move")
    destination.add_argument("word", dest="destination")

    def list_aliases(self):
        """List the current aliases."""
        aliases = self.db.setdefault("aliases", {})
        if not aliases:
            self.msg("You don't have any goto alias yet.")
            return

        max_key = max(len(key) for key in aliases.keys())
        aliases = sorted(aliases.items())
        lines = ["Your current goto aliases:"]
        for key, alias in aliases:
            lines.append(f"  {key:<{max_key}}: {alias}")
        self.msg("\n".join(lines))

    def add_alias(self, destination: str):
        """Add an alias."""
        aliases = self.db.setdefault("aliases", {})
        room = self.character.location
        if room is None:
            self.msg("You aren't in any room yet.")
            return

        aliases[destination.lower()] = room.barcode
        self.db.aliases = aliases
        self.msg(
            f"You've succesfully created the alias {destination} "
            f"pointing to {room.barcode}."
        )

    def del_alias(self, destination: str):
        """Remove an alias."""
        aliases = self.db.setdefault("aliases", {})
        if aliases.pop(destination.lower(), None) is None:
            self.msg(
                f"This goto alias {destination} isn't defined "
                "for your character."
            )
            return

        self.db.aliases = aliases
        self.msg(f"You've removed the goto alias {destination}.")

    def move(self, destination):
        """Command body."""
        aliases = self.db.setdefault("aliases", {})
        room = None

        # First, test room barcodes.
        room = Room.get(barcode=destination.lower(), raise_not_found=False)

        if room is None:
            # Maybe it's an alias.
            barcode = aliases.get(destination.lower())
            if barcode:
                room = Room.get(barcode=barcode, raise_not_found=False)
                if room is None:
                    self.msg(
                        f"The goto alias {destination} is linked to room "
                        f"of barcode {barcode}, but this room "
                        "cannot be found."
                    )
                    return

        if room:
            self.character.room = room
            self.character.location = room
            self.msg(room.look(self.character))
        else:
            self.msg(f"Cannot find the room or location {destination}.")
