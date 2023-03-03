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

"""The account DB Model.

An account is a storage for player characters.  Each account is protected
by a username and a password.  General options and contact information
are also stored in the account as a rule.

An account is a player feature, NPCs don't use them at all.

"""

from datetime import datetime
import hashlib
import os
from typing import TYPE_CHECKING

from dynaconf import settings
from pydantic import EmailStr

from data.base.model import Field, Model
from data.handler.collections import List
from data.handler.namespace import NamespaceHandler

if TYPE_CHECKING:
    from data.player import Player


class Account(Model):

    """Model to represent an account."""

    id: int = Field(primary_key=True)
    username: str = Field(unique=True)
    hashed_password: bytes
    email: EmailStr | None = Field(None, unique=True)
    created_on: datetime = Field(default_factory=datetime.utcnow)
    updated_on: datetime = Field(default_factory=datetime.utcnow)
    db: NamespaceHandler = Field(
        default_factory=NamespaceHandler, external=True
    )
    players: List["Player"] = Field(default_factory=List, external=True)

    @staticmethod
    def hash_password(plain_password: str, salt: bytes | None = None) -> bytes:
        """Hash the given plain text password, return it hashed.

        If the salt is provided, it is used for hashing.  If not,
        it is randomly generated.

        Args:
            plain_password (str): the plain password.
            salt (bytes, optional): the salt to use to hash the password.

        Returns:
            hashed_password (bytes): the hashed passowrd containing
                    the salt and key.

        """
        if salt is None:
            # Generate a random salt.
            salt = os.urandom(settings.SALT_SIZE)

        # Hash the password with pbkdf2_hmac.
        key_size = settings.KEY_SIZE or None
        key = hashlib.pbkdf2_hmac(
            settings.HASH_ALGORITHM,
            plain_password.encode("utf-8"),
            salt,
            settings.HASH_ITERATIONS,
            key_size,
        )

        return salt + key

    @staticmethod
    def test_password(hashed_password: bytes, plain_password: str) -> bool:
        """Return whether the hashed and non hashed password match.

        Args:
            hashed_password (bytes): the already-hashed password.
            plain_password (str): the plain password to test.

        Returns:
            match (bool): whether plain_password match hashed_password.

        """
        salt = hashed_password[: settings.SALT_SIZE]
        hashed_attempt = Account.hash_password(plain_password, salt)
        return hashed_password == hashed_attempt
