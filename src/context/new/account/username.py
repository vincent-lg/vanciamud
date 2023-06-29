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

"""Create a username, first process in account creation."""

from dynaconf import settings

from context.base import Context
from data.account import Account


class Username(Context):

    """Context displayed when the user has entered 'new' in MOTD.

    Input:
        <new username>: the username to create.
        /: slash, go back to connection.home.

    """

    prompt = "Votre nouveau nom d'utilisateur :"
    text = """
        Veuillez entre le nom de votre futur compte. Un personnage
        du même nom sera également créé.
    """

    def other_input(self, username: str):
        """The user entered something else."""
        username = username.lower().strip()
        min_size = settings.MIN_ACCOUNT_USERNAME

        # Check that the name isn't too short.
        if len(username) < min_size:
            self.msg(
                f"Le nom d'utilisateur {username!r} est incorrect. "
                f"Il doit être de {min_size} caractères au minimum. "
                "Veuillez essayer à nouveau."
            )
            return

        # Check that the username isn't a forbidden name.
        account = Account.get(username=username, raise_not_found=False)
        forbidden = [name.lower() for name in settings.FORBIDDEN_USERNAMES]
        if username in forbidden or account:
            self.msg(
                f"Le nom d'utilisateur {username!r} est interdit. Veuillez "
                "en choisir un autre."
            )
            return

        self.msg(f"Vous avez choisi le nom d'utilisateur {username!r}.")
        self.session.db.username = username
        self.move("new.account.password")
