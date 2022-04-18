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

"""Default context for logged-in characters.

This context is responsible for handling commands, exits and channels.
It always is the default context in the character's command stack
and cannot be entirely removed, though other contexts can be added
and they can "block" user input to make sure it is not sent to the game
context at all.

Note:
    This context can seem close to the "connection.game" context,
    yet the two are really different: the "connection.game" context
    forwards to the character's command stack.  The "character.game"
    context, on the other hand, is the default active context on
    the context stack: therefore, user input is, by default, forwarded
    from "connection.game" to "character.game", but it is possible
    to add new contexts on the character's context stack.  The
    "character.game" context is always available to the context
    stack, but another context might be active at the time.

"""

from command.base import COMMANDS
from context.base import Context


class Game(Context):

    """Default context called when the user is logged in to a character."""

    def get_prompt(self) -> str:
        """Return the active context prompt."""
        return "HP: 100"

    def greet(self) -> str:
        """Return the active context's greeting."""
        room = self.character.room
        if room:
            lines = [
                room.title,
                room.description.format(),
            ]
            return "\n".join(lines)

        return "You are floating in the void..."

    def handle_input(self, user_input: str):
        """Route the user input to the context stack."""
        character = self.session.character
        seps = {sep: () for comm in COMMANDS.values() for sep in comm.seps}
        for sep in seps.keys():
            try:
                before, after = user_input.split(sep, 1)
            except ValueError:
                before = user_input
                after = ""

            seps[sep] = (before, after)

        for command_cls in COMMANDS.values():
            aliases = command_cls.alias
            if isinstance(aliases, str):
                aliases = (aliases,)

            for sep in command_cls.seps:
                before, after = seps[sep]
                if before == command_cls.name or before in aliases:
                    if character and not command_cls.can_run(character):
                        continue

                    command = command_cls(character, sep, after)
                    command.parse_and_run()
                    return True

        return False

    def unknown_input(self, user_input: str) -> str:
        """What to do when the input doesn't match?"""
        return f"Command not found: {user_input}"
