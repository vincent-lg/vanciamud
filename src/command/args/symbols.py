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

"""Symbols argument.

This argument consists of one or more characters as delimiters.

"""

from typing import Any, Optional, Union, TYPE_CHECKING

from command.args.base import ArgSpace, Argument
from command.args.error import ArgumentError
from command.args.result import Result

if TYPE_CHECKING:
    from data.character import Character


class Symbols(Argument):

    """Symbols class for argument."""

    name = "symbols"
    space = ArgSpace.STRICT
    in_namespace = False

    def __init__(
        self,
        symbols: str,
        optional: bool = False,
        default: Optional[Any] = None,
        dests: dict[str, Any] | None = None,
        **kwargs,
    ):
        super().__init__(optional=optional, default=default, **kwargs)
        self.symbols = symbols
        self.dests = dests
        self.msg_absent = "You forgot to specify {symbols}."

    def __repr__(self):
        return "<Symbols>"

    def format(self):
        """Return a string description of the arguments.

        Returns:
            description (str): the formatted text.

        """
        text = self.symbols
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
        before_pos = string.find(self.symbols, begin)
        if before_pos != -1:
            after_pos = before_pos + len(self.symbols)
            while before_pos > 1 and string[before_pos - 1].isspace():
                before_pos -= 1
            if after_pos == -1:
                after_pos = None
            else:
                while (
                    after_pos < len(string) - 2
                    and string[after_pos + 1].isspace()
                ):
                    after_pos += 1

            return Result(begin=before_pos, end=after_pos, string=string)

        return ArgumentError(self.msg_absent.format(symbols=self.symbols))

    def add_to_namespace(self, result, namespace):
        """Add the parsed search object to the namespace."""
        dests = self.dests or {}
        for key, value in dests.items():
            setattr(namespace, key, value)
