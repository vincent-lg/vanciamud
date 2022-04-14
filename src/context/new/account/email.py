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

"""Enter an email address, step in account creation."""

from pydantic import EmailStr
from pydantic.errors import EmailError

from context.base import Context
from data.account import Account


class Email(Context):

    """Context displayed when the user has entered a confirmed password.

    Input:
        <email address>: the email address to link to this account.
        no: no email address to link.
        /: slash, go back to connection.home.

    """

    prompt = "The email address to link to this account (or 'no'):"
    text = """
        The email address to link to this account.

        You now can enter an email address to link to this account.
        It is not mandatory, but highly encouraged.

        Having an email address linked with the account would allow
        you to receive emails from the game, to keep you updated on
        events and internal communication.  It will also be used if
        you have forgotten your account's password, for without a valid
        email address, administrators will not be able to restore
        your password safely and check that you are who you say you are.

        Email addresses will not be used by staff directly.  If
        they need to contact you, they will use a system where
        your email address is not displayed.  Only code administrators
        may access your email address, but they will not, under
        any circumstance, use it or transmit it to others.

        If you really don't want to link your account with an email address,
        you can enter 'no' (without quotes).
    """

    def input_no(self):
        """Do not link this account to an email address."""
        self.session.db.email = None
        self.msg(
            "You have chosen not to link this account with an email address.  "
            "You can always change your mind later."
        )
        self.move("new.account.complete")

    def other_input(self, email: str):
        """The user entered something else."""
        try:
            EmailStr.validate(email)
        except EmailError:
            self.msg("This is not a valid email address.  Please try again.")
            return

        # Check that this email isn't already used.
        email = email.lower()
        accounts = Account.repository.select(Account.email == email)
        if accounts:
            self.msg(
                "This email address is in use, please choose another one."
            )
            return

        # That's valid, go on.
        self.session.db.email = email
        self.move("new.account.complete")
