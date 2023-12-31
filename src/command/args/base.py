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

"""Base argument."""

from enum import Enum
from typing import Optional, Union, TYPE_CHECKING

from command.args.error import ArgumentError
from command.args.result import Result

if TYPE_CHECKING:
    from data.character import Character

ARG_TYPES = {}


class ArgSpace(Enum):

    """Enumeration to define the space this argument takes."""

    UNKNOWN = 1  # Anything can be captured
    STRICT = 2  # The command knows what to capture
    WORD = 3  # The command will capture the first word


class ArgMeta(type):

    """Metaclass for arguments."""

    def __init__(cls, name, bases, cls_dict):
        if cls.name:
            ARG_TYPES[cls.name] = cls


class Argument(metaclass=ArgMeta):

    """Base class for arguments."""

    name = ""
    space = ArgSpace.UNKNOWN
    in_namespace = True

    # To not override.
    _NOT_SET = None

    def __init__(self, dest, optional=False, default=None, **kwargs):
        self.dest = dest
        self.optional = optional
        self.default = default
        self.msg_mandatory = "You should specify a {argument}."

    @property
    def has_default(self):
        return self.default is not self._NOT_SET

    def __repr__(self):
        return f"<Arg {self.name}>"

    def format(self):
        """Return a string description of the arguments.

        Returns:
            description (str): the formatted text.

        """
        text = f"<{self.dest}>"

        if self.optional:
            text = f"[{text}]"

        return text

    def expand(self, possibilities: list[list["Argument"]]) -> None:
        """Expand, if necessary, the list of arguments.

        Args:
            possibilities (list of list of arguments): the possibilities.

        This method does not return anything but will mutate the list.

        """
        for possible in possibilities:
            possible += [self]

        return possibilities

    def parse(
        self,
        character: "Character",
        string: str,
        begin: int = 0,
        end: Optional[int] = None,
    ) -> Union[Result, ArgumentError]:
        """Parse the argument.

        Args:
            character (Character): the character running the command.
            string (str): the string to parse.
            begin (int): the beginning of the string to parse.
            end (int, optional): the end of the string to parse.

        Returns:
            result (Result or ArgumentError).

        """
        if type(self).space is ArgSpace.WORD:
            space_pos = string.find(" ", begin)
            if space_pos != -1:
                end = space_pos

            return Result(begin=begin, end=end, string=string)
        else:
            return Result(begin=begin, end=end, string=string)

    def add_to_namespace(self, result, namespace):
        """Add the parsed search object to the namespace."""
        setattr(namespace, self.dest, result.portion)
