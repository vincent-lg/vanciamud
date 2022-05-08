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

"""Check the password, step in account connection."""

from context.base import Context


class Password(Context):

    """Context displayed when the user has entered the account's password.

    Input:
        <password>: the password to connect.
        /: slash, go back to connection.home.

    """

    hide_input = True
    prompt = "Your account's password:"
    text = """
        Account's password.

        You now need to enter the password for this account.
    """

    def other_input(self, password: str):
        """The user entered something else."""
        account = self.session.db.account
        hashed_password = account.hashed_password

        if account.db.get("wrong_password"):
            self.msg("Please wait, you can't retry your password just yet.")
            return

        if not account.test_password(hashed_password, password):
            self.msg("Incorrect password.  Please wait.")
            self.call_in(3, self.allow_new_password, account)
            return

        self.move("character.choice")

    def allow_new_password(self, account):
        """Allow to enter a new password."""
        _ = account.db.pop("wrong_password", None)
        self.refresh()
