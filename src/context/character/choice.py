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

"""Display the meny to connect to a character."""

from context.base import Context


class Choice(Context):

    """Context displayed when the user has entered the account's password.

    Input:
        <number>: a character's number.
        /: slash, go back to connection.home.

    """

    prompt = "Your choice:"

    def refresh(self):
        """When entering the context."""
        # Move to create a character if none exists in this account.
        account = self.session.db.account
        if not account.players:
            self.move("new.character.name")
        else:
            super().refresh()

    def greet(self):
        """Return the text to display."""
        account = self.session.db.account
        lines = [
            f"Welcome to your account, {account.username}!",
            "Please enter one of the following choices:",
        ]

        i = 1
        for player in account.players:
            lines.append(
                f"  {i:>2} to connect to the character {player.name}."
            )
            i += 1

        lines.append("  C to create a new character in this account.")
        return "\n".join(lines)

    def input_c(self):
        """Create a new character in this account."""
        self.move("new.character.name")

    def other_input(self, user_input: str):
        """The user entered something else."""
        account = self.session.db.account
        i = 1
        for player in account.players:
            if user_input == str(i):
                self.session.db.character = player
                self.move("character.login")
                return True
            i += 1

        self.msg("This is not a valid option.")
