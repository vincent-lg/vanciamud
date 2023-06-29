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

"""Home, the first active node in the login/chargen process."""

from context.base import Context
from data.account import Account


class Home(Context):

    """Context displayed just after MOTD.

    Input:
        new: the user wishes to create a new account.
        <existing account>: the user has an account and wishes to connect.

    """

    prompt = "Entrez votre nom d'utilisateur :"
    text = """
        Si vous avez déjà un compte, entrez simplement son nom ici.
        Sinon, entrez nouveau pour en créer un.
    """

    def input_nouveau(self):
        """The user has input 'nouveau' to create a new account."""
        self.move("new.account.username")

    def other_input(self, username: str):
        """The user entered something else."""
        username = username.lower()
        account = Account.get(username=username, raise_not_found=False)
        if account:
            self.session.db.account = account
            self.move("connection.password")
        else:
            self.msg(
                f"Malheureusement, {username} n'existe pas comme nom "
                "de compte. Si vous souhaitez le créer, entrez nouveau."
            )
