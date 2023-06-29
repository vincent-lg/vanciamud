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

"""Create a password, step in account creation."""

from dynaconf import settings

from context.base import Context
from data.account import Account


class Password(Context):

    """Context displayed when the user has entered a new username.

    Input:
        <password>: the password to create.
        /: slash, go back to connection.home.

    """

    hide_input = True
    prompt = "Le nouveau mot de passe de ce compte :"
    text = """
        Veuillez entrez un mot de passe pour protéger ce compte.
    """

    def greet(self) -> str:
        """Greet the session or character.

        This method is called when the session first connects to this
        context or when it calls for a "refresh".

        """
        return self.text.format(
            username=self.session.db.get("username", "unknown")
        )

    def other_input(self, password: str):
        """The user entered something else."""
        min_size = settings.MIN_ACCOUNT_PASSWORD

        # Check that the password isn't too short.
        if len(password) < min_size:
            self.msg(
                f"Ce mot de passe est trop court ({min_size} caractères "
                "minimum). Veuillez réesayer."
            )
            return

        self.session.db.password = Account.hash_password(password)
        self.move("new.account.confirm_password")
