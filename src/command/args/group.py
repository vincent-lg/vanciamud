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

"""Argument group, containing branches."""

from itertools import permutations, product

from command.args.base import Argument, ArgSpace

# Constants
ROLES = ("|", "+")


class Group:

    """Command argument group, to have several branches.

    A group in command arguments is meant to represent a set of argument
    branches.  An argument branch is a set of arguments, and a branch
    can either be verified or not.  A group in turn can contain
    several branches and help choose which one to execute through
    a partial parsing.  The group can then decide to propagate
    any error it meets, to use the one working branch or
    to generate an error of its own.

    """

    space = ArgSpace.UNKNOWN
    in_namespace = True

    def __init__(self, parser, role):
        self.name = "group"
        self.parser = parser
        self.branches = []
        self.optional = False
        self.msg_error = "Invalid syntax."
        self.msg_mandatory = "You have to specify something."
        if role not in ROLES:
            raise ValueError(
                f"the role {role!r} isn't acceptable: valid values "
                f"are {list(ROLES)}"
            )
        self.role = role

    def add_branch(self, *args, run_in: str = "run") -> None:
        """Add and fill a branch.

        Positional arguments are new arguments and can be created using
        the `new` method of the parser (like `args.new("keyword", ...)`).

        Keyword arguments:
            method_name (str): name of the method to call for this branch.

        """
        self.branches.append(list(args))

        for arg in args:
            arg.run_in = run_in

    def format(self):
        """Return a string description of the arguments.

        Returns:
            description (str): the formatted text.

        """
        if len(self.branches) > 1:
            text = "("
            text += f") {self.role} (".join(
                [
                    " ".join([arg.format() for arg in branch])
                    for branch in self.branches
                ]
            )
            text += ")"
        else:
            text = " ".join([arg.format() for arg in self.branches[0]])

        return text

    def expand(self, possibilities: list[list["Argument"]]) -> None:
        """Expand, if necessary, the list of arguments.

        Args:
            possibilities (list of list of arguments): the possibilities.

        This method does not return anything but will mutate the list.

        """
        if self.role == "|":
            # One of the branches is required.
            possibilities = [
                old + new for old, new in product(possibilities, self.branches)
            ]
        elif self.role == "+":
            # Several branches can be used.
            branches = [
                sum(cb, [])
                for r in range(len(self.branches) + 1)
                for cb in permutations(self.branches, r)
            ]

            possibilities = [
                old + new for old, new in product(possibilities, branches)
            ]

        if not possibilities:
            possibilities = self.branches

        return possibilities
