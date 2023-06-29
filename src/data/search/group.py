# Copyright (c) 2023, LE GOFF Vincent
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

"""Search group, used to keep informations about a character and container.

A character will use a group to display what she can see, and also what
she can do.  A group links a character with a container and builds
on the objects contained within this container to group them by name.
Each time a character undergoes a change of perception (that would
affect what she can see), the group should be cleared.  Groups aren't stored.
Groups can be merged (this is particularly useful to handle manipulation
in several containers).

"""

from collections import defaultdict
from typing import Type, TYPE_CHECKING

from parse import compile

from data.base.node import Node
from data.search.nodes import GroupedNodes

if TYPE_CHECKING:
    from data.character import Character

# Format constants
BEFORE_ANY = ", "
BEFORE_LAST = ", and "
NUMBER_MATCH = compile("{number:d}.{name}")


class Group:

    """A group, linking a character with a container.

    The API to use groups is pretty simple:

        from data.search import Group
        seen = Group.get_for(character, node)
        character.msg(f"You have: {group.format()}")

    If the character is in a room, for instance, a group can be created
    between this character and the room's content (a room contains
    the objects on the ground).  The `get_for` class method will return
    a new (or cached) group where each contained nodes (objects
    or other characters more likely) are displayed.  These contained
    nodes are formatted according to their number (the singular
    or plural form will be used).  Nodes have a different way
    to handle grouping (see `Group.`).

    """

    CACHED = {}

    def __init__(
        self,
        character: "Character",
        *nodes: list[Node],
        contents: list[tuple[Node, int, str | None]] | None = None,
    ) -> None:
        self.character = character
        self.nodes = nodes
        if contents is None:
            self.contents = sum(
                [node.locator.all_contents for node in nodes], []
            )
        elif nodes:
            raise ValueError("a group cannot have both nodes and contents")
        else:
            self.contents = contents

        self.names = defaultdict(list)
        self.matches = []
        self.pluralized = []

    def group_by_name(self):
        """Group the nodes by name.

        Not all nodes have singular and plural names.  These are kept unique.

        """
        for node, quantity, filter in self.contents:
            name = getattr(node, "name", None)
            if method := getattr(node, "get_name_for", None):
                name = method(self.character, 1)
            elif name is not None:
                name = node

            if name is not None:
                self.names[name].append((node, quantity, filter))

        self.pluralized = self.pluralize(self.names)
        self.matches = {
            match: tups
            for name, tups in self.pluralized
            for match in self._get_matches(name)
        }

    def pluralize(
        self, names: dict[str, list[Node, int, str | None]]
    ) -> list[str, list[tuple[Node, int]]]:
        """Return the pluralized version of the names.

        Args:
            names (dict): the names to format.

        Returns:
            pluralized (list): the list of formatted names.

        """
        pluralized = []
        for tups in names.values():
            nodes = [tup[0] for tup in tups]
            quantity = sum(tup[1] for tup in tups)
            if not nodes:
                continue

            node = nodes[0]
            if method := getattr(node, "get_name_for", None):
                name = method(self.character, quantity)
            else:
                name = getattr(node, "name", None)

            if name is not None:
                pluralized.append((name, tups))

        return pluralized

    def get_names(self, only_of_class: Type[Node] | None = None) -> list[str]:
        """Get the names as a list of strings.

        Arguments:
            only_of_class (subclass of Node): only return the names of noddes
                    from this class.

        Returns:
            names (list of str): the names.

        """
        name_list = self.pluralized
        if only_of_class is not None:
            names = {
                singular: [
                    (node, quantity, filter)
                    for node, quantity, filter in tups
                    if isinstance(node, only_of_class)
                ]
                for singular, tups in self.names.items()
            }
            name_list = self.pluralize(names)

        return [name for name, _ in name_list]

    def match(self, search_string: str) -> list["GroupedNodes"]:
        """Search through the list of names, returning only these who match.

        This method will return an empty list if no match is found.
        Otherwise, it will return a list of grouped nodes.
        The search is performed on the stored names
        (singular or pluralized depending on their quantity).
        A search can also be restrictive if the search string starts with
        a number, then a delimiter (a dot by default) and then a name.
        In this case, the list will contain either zero or one element.

        Args:
            search_string (str): the formatted search strings.

        Note:
            By default, the search string can be of two forms:
                "tree"
                    In this case, returns all the node names within this
                    container having a name matching "tree".  A name matches
                    if it begins by the specified search string or if
                    one of its words begins by a search string.
                    The search process is broken down
                    into methods that can easily be adjusted for
                    other languages.
                "3.apple"
                    In this case, the 3rd node named "apple" will
                    be retrieved.  The other apples are ignored.

        """
        number = None
        if result := NUMBER_MATCH.parse(search_string):
            search_string = result["name"]
            number = result["number"]

        matches = []
        matching = 1
        for name, tups in self.matches.items():
            if self._match_name(name, search_string):
                group = []
                total = 0
                for node, quantity, filter in tups:
                    if number is None or number == matching:
                        group.append((node, quantity, filter))
                        total += quantity
                        if number is not None:
                            matches.append(
                                GroupedNodes(nodes=group, quantity=total)
                            )
                            break

                    matching += 1

                matches.append(GroupedNodes(nodes=group, quantity=total))

            if matches:
                break

        return matches

    def format(
        self,
        before: str = "",
        before_any: str = BEFORE_ANY,
        before_last: str = BEFORE_LAST,
        after: str = "",
        nothing: str = "",
        only_of_class: Type[Node] | None = None,
    ) -> str:
        """Return a formatted string, ready to be displayed.

        Parameters in this method hadle displaying or filtering the list
        of names.

        Args:
            before (str): the optional string to display before
                    the entire list of names.  If the list is empty,
                    `befor` is not displayed at all.
            before_any (str): the optional string to place between
                    the 2nd and 3rd name, the 3rd and 4th name... and so on.
                    This string is not placedd BEFORE the last name
                    (see `before_last`) since most languages have
                    a different way to format the last item.
            before_last (str): the optional string to be placed
                    just before the last element instead of `before_any`.
            after (str): the optional string to place after the list
                    of names.  If the list of names is empty,
                    `after` is not displayed (see `nothing`).
            nothing (str): the optional string to be displayed if the list
                    of names is empty.  Neither `before` not `after`
                    are displayed.
            only_of_class (subclass of Node): only include names of
                    this node type.

        Returns:
            formatted (str): the list of names.

        """
        names = self.get_names(only_of_class)
        if names:
            formatted = before
            formatted += before_any.join(names[:-1])
            if len(names) > 1:
                formatted += before_last
            formatted += names[-1]
            formatted += after
        else:
            formatted = nothing

        return formatted

    def _match_name(self, name: str, search: str) -> bool:
        """Returns whether this search string matches this name.

        You can modify this method to handle specific languages.

        Args:
            name (str): the full name.
            search (str): the search string.

        Returns:
            matches (bool): whether this search matches this name.

        """
        search = self._prepare_name(search)

        return name.startswith(search)

    def _prepare_name(self, name: str) -> str:
        """Return a name ready to be matched.

        Usually, case is removed.  Other languages might want to remove
        accents or special characters.  This is done both on individual
        object names and on the search string in the `match` method.

        Args:
            name (str): the name or search string.

        Returns:
            name (str): the prepared name or search string.

        """
        return name.lower()

    def _get_matches(self, name: str) -> set[str]:
        """Return the set of parts of this name.

        A part is usually one or several word.  For instance, a name like that:
            "a beautiful flower"
        Should return something like:
            {"a", "beautiful", "flower", "a beautiful",
            "beautiful flower", "a beautiful flower"}
        This is used to find matches for a future search.

        Args:
            name (str): the full name.

        Returns:
            parts (set of str): the parts.

        """
        name = self._prepare_name(name)
        seps = [" "]
        parts = {name}
        for sep in seps:
            words = name.split(sep)
            for i in range(len(words)):
                for j in range(i, len(words)):
                    part = sep.join(words[i : j + 1])
                    parts.add(part)

        return parts

    @classmethod
    def get_for(
        cls,
        character: "Character",
        *nodes: list[Node],
        contents: list[tuple[Node, int, str | None]] | None = None,
    ) -> "Group":
        """Retrieve the group matching this character and container(s).

        Args:
            character (Character): the character seeing the node(s).

        Additional position arguments specify the node(s) to watch
        (more than one node can be specified).  The group will be built
        using the node(s)' contents.  Alternatively, you can specify
        the `contents` keyword argument to override this behavior.
        You have to specify a node contents in the form of a list
        of tuples, with each tuple containing the node, its quantity
        and a location filter (the second and third elements are useful
        for stackable objects).

        Note:
            A group built with an overriddent contents (using the
            `contents` keyword) will NOT be cached.

        Note:
            A group built for a character with nodes will be cached
            for this character and nodes in the same order.  Therefore,
            a cache for node 1, 2 and 3 will not be retrieved
            if you ask for a group containing node 2, 1 and 3
            (the order isn't the same and a new group will be created).
            This is due to the fact that groups can be used for matches,
            and the order of nodes matter a lot for matches.

        Returns:
            group (Group): a cached or new group.

        """
        group = None
        if contents is None:
            group = Group.CACHED.get((character, nodes))

        if group is None:
            group = Group(character, *nodes, contents=contents)
            group.group_by_name()

            if contents is None:
                Group.CACHED[(character, nodes)] = group

        return group

    @staticmethod
    def limit(
        objects: list[tuple[Node, int, str | None]], limit: int
    ) -> list[tuple[Node, int, str | None]]:
        """Return a limited version of the group.

        Args:
            objects (list of tuple): the objects to filter.
            limit (int): the limit itself.

        Returns:
            objects (list of tuple): the limited objects.

        """
        current = 0
        filtered = []
        for node, quantity, filter in objects:
            if current + quantity > limit:
                quantity = limit - current

            filtered.append((node, quantity, filter))
            current += quantity
            if current >= limit:
                break

        return filtered
