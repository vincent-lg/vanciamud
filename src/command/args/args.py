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

"""Command arguments."""

from typing import Any, Optional, Union, TYPE_CHECKING

from command.args.base import ARG_TYPES, Argument
from command.args.error import ArgumentError
from command.args.helpers import parse_possibilities
from command.args.group import Group
from command.args.namespace import Namespace

if TYPE_CHECKING:
    from data.character import Character

_NOT_SET = object()
Argument._NOT_SET = _NOT_SET


class CommandArgs:

    """Command arguments, to be parsed BEFORE the command is called.

    Command arguments can be seen as a parser, somewhat identical
    to the one defined in the `argparse` module.  It has a focus on the
    order of argument parsing, however, and can be configured in
    an incremental way.

    For instance, if you want a command to take an optional argument
    which can be a number, and then a required argument that can be
    an object name, you would do something like this:

    ```python
    class MyCommand(Command):

        args = CommandArgs()
        args.add_argument("number", optional=True)
        args.add_argument("object")
    ```

    This parser will work for:

        '5 apples'
        '1 gold piece'
        'sword'

    The parser will check for two things:

    1.  Does the command argument begins with a number?  If so,
        feed it to the first argument (number).  If not,
        go on.
    2.  It checks that there is a word in the command arguments.  This
        word, the object name, will be checked against the valid
        object names the character has.  In other words, if the
        character entered an invalid objedct name, the command
        will not even be executed.

    Valid methods on the command arguments parser are:
        add_argument: add an argument.
        add_branch: add a branch in which arguments can be set.
        add_keyword: add a keyword argument.
        add_delimiter: add a delimiter argument.

    Adding a keyword or a delimiter is so common a task that helper
    methods have been created to do so, but you can also use `add_argument`
    to add these argument types.

    """

    def __init__(self):
        self.arguments = []
        self.msg_invalid = "Invalid syntax."

    def new(
        self,
        arg_type: str,
        *args,
        dest: Optional[str] = None,
        optional: bool = False,
        default: Any = _NOT_SET,
        **kwargs,
    ):
        """Return a new argument not linked to the parser.

        Args:
            arg_type (str): the argument type.
            dest (str, optional): the attribute name in the namespace.
            optional (bool, optional): is this argument optional?

        Additional positional or keyword arguments are sent to
        the argument class.

        """
        arg_class = ARG_TYPES.get(arg_type)
        if arg_class is None:
            raise KeyError(f"invalid argument type: {arg_type!r}")

        dest = dest or arg_type
        argument = arg_class(
            *args, dest=dest, optional=optional, default=default, **kwargs
        )
        return argument

    def add_argument(
        self,
        arg_type: str,
        *args,
        dest: Optional[str] = None,
        optional: bool = False,
        default: Any = _NOT_SET,
        **kwargs,
    ):
        """Add a new argument to the parser.

        Args:
            arg_type (str): the argument type.
            dest (str, optional): the attribute name in the namespace.
            optional (bool, optional): is this argument optional?

        Additional positional or keyword arguments are sent to
        the argument class.

        """
        argument = self.new(
            arg_type, *args, dest=dest, optional=optional, **kwargs
        )
        self.arguments.append(argument)
        return argument

    def add_group(self, role):
        """Add an argument group."""
        group = Group(self, role)
        self.arguments.append(group)
        return group

    def format(self) -> str:
        """Return a string description of the arguments.

        Args:
            arguments (list of Argument): the list of arguments.

        Returns:
            description (str): the formatted text.

        """
        possibilities = [[]]
        for arg in self.arguments:
            possibilities = arg.expand(possibilities)

        return "\n".join(
            [
                " ".join([arg.format() for arg in line])
                for line in possibilities
            ]
        )

    def parse(
        self,
        character: "Character",
        string: str,
        begin: int = 0,
        end: Optional[int] = None,
    ) -> Union[Namespace, ArgumentError]:
        """Try to parse the command arguments.

        This method returns either a parsed namespace containing the
        parsed arguments, or an error represented by `ArgumentError`.

        Args:
            character (Character): the character running the command.
            string (str): the unparsed arguments as a string.
            begin (int, opt): the optional parse beginning.
            end (int, opt): the optional parse ending.

        Returns:
            result (`Namespace` or `ArgumentError`): the parsed result.

        """
        possibilities = [[]]
        for arg in self.arguments:
            possibilities = arg.expand(possibilities)

        return parse_possibilities(
            possibilities, character, string, begin, end, self.msg_invalid
        )
