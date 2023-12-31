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

"""Keyword argument."""

from typing import Optional, Union, TYPE_CHECKING

from command.args.base import ArgSpace, Argument, ArgumentError, Result

if TYPE_CHECKING:
    from data.character import Character


class Keyword(Argument):

    """Keyword class for argument."""

    name = "keyword"
    space = ArgSpace.STRICT
    in_namespace = False

    def __init__(self, *names, dest, optional=False, default=None):
        super().__init__(dest, optional=optional, default=default)
        self.names = names
        self.msg_cannot_find = "Can't find this argument."

    def __repr__(self):
        return f"<Keyword {'/'.join(self.names)}>"

    def format(self):
        """Return a string description of the arguments.

        Returns:
            description (str): the formatted text.

        """
        text = "/".join(self.names)
        if self.optional:
            text = f"[{text}]"

        return text

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
        for name in self.names:
            if string[begin:].startswith(f"{name} "):
                return Result(
                    begin=begin,
                    end=begin + len(name) + 1,
                    string=string,
                )

            pos = string.find(f" {name} ", begin)
            if pos >= 0 and pos < end:
                return Result(
                    begin=pos,
                    end=pos + len(name) + 2,
                    string=string,
                )

        return ArgumentError(self.msg_cannot_find)

    def add_to_namespace(self, result, namespace):
        """Add the parsed search object to the namespace."""
