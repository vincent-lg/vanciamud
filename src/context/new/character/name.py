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

"""Create a character name, first process in character creation."""

from dynaconf import settings

from context.base import Context


class Name(Context):

    """Context displayed when the user has entered 'c' in character.choice.

    Input:
        <new name>: the name of the character to create.
        /: slash, go back to character.choice.

    """

    prompt = "Your new character's name:"
    text = """
        New character.

        You have to enter the name of your new character.  This name
        will be visible to other characters (and players) in the game.
    """

    def other_input(self, name: str):
        """The user entered something else."""
        name = name.strip()
        name = name[0].upper() + name[1:].lower()
        min_size = settings.MIN_CHARACTER_NAME

        # Check that the name isn't too short.
        if len(name) < min_size:
            self.msg(
                f"The name {name!r} is incorrect.  It should be "
                f"at least {min_size} characters in length.  "
                "Please try again."
            )
            return

        # Check that the username isn't a forbidden name.
        forbidden = [
            name.lower() for name in settings.FORBIDDEN_CHARACTER_NAMES
        ]
        if name.lower() in forbidden:
            self.msg(
                f"The name {name!r} is forbidden.  Please "
                "choose another one."
            )
            return

        self.session.db.name = name
        self.move("new.character.complete")
