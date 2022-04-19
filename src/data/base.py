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

"""The base data model, responsible for all data storage."""

from typing import Callable

from pygasus.storage import SQLStorageEngine

from data.account import Account
from data.character import Character
from data.delay import Delay
from data.handler.contexts import ContextsField
from data.handler.description import DescriptionField
from data.handler.exits import ExitsField
from data.handler.namespace import NamespaceField
from data.handler.permissions import PermissionsField
from data.room import Room
from data.session import Session


def handle_data(
    logging: Callable[[str, str], None] = None
) -> SQLStorageEngine:
    """Connect to the database and bind models."""
    engine = SQLStorageEngine()
    engine.init("talismud.db", logging=logging)
    engine.bind({Account, Character, Delay, Room, Session})
    engine.add_custom_field(ContextsField)
    engine.add_custom_field(DescriptionField)
    engine.add_custom_field(ExitsField)
    engine.add_custom_field(NamespaceField)
    engine.add_custom_field(PermissionsField)
    return engine
