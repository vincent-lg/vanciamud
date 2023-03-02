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

"""Game context, displayed while a character is logged in.

This is the most important context: once logged in to a character,
all inputs from the session will flow through this context.  Its role
is to simply route the user input to the character's context stack
and display errors if necessary.

Note:
    This context can seem close to the "character.game" context,
    yet the two are really different: the "connection.game" context
    forwards to the character's command stack.  The "character.game"
    context, on the other hand, is the default active context on
    the context stack: therefore, user input is, by default, forwarded
    from "connection.game" to "character.game", but it is possible
    to add new contexts on the character's context stack.  The
    "character.game" context is always available to the context
    stack, but another context might be active at the time.

"""

from context.base import Context


class Game(Context):

    """Context called when the user is logged in to a character."""

    def get_prompt(self) -> str:
        """Return the active context prompt."""
        if character := self.session.character:
            return character.contexts.active.get_prompt()

    def greet(self) -> str:
        """Return the active context's greeting."""
        if character := self.session.character:
            return character.contexts.active.greet()

    def handle_input(self, user_input: str):
        """Route the user input to the context stack."""
        res = False
        if character := self.session.character:
            res = character.contexts.handle_input(user_input)

        if not res:
            if character := self.session.character:
                self.msg(character.contexts.active.unknown_input(user_input))
