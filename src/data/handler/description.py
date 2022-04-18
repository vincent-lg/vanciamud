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

"""Description custom field, to hold descriptons."""

from textwrap import fill, wrap
from typing import Dict, Optional

from pygasus.model import CustomField


class Description(str):

    """A description handler, behaving like a string."""

    def __init__(self, *args, **kwargs):
        self.parent = None
        self.field = None
        self.text = args[0]

    def __repr__(self):
        return repr(self.text)

    def __str__(self):
        return self.text

    def set(self, text: str):
        """Set the description and save it."""
        self.text = text
        self.save()

    def format(
        self,
        vars: Optional[Dict[str, str]] = None,
        indent_with: str = " " * 3,
        indent_no_wrap: bool = False,
        width: Optional[int] = 78,
    ) -> str:
        """Format the description and return a formatted string.

        Args:
            vars (dict, optional): the variables for dynamic descriptions.
            indent_with (str, optional): the text to add before
                    each paragraph to indent, usually three spaces
                    or nothing.
            indent_no_wrap (bool, optional): add `indent_with` before
                    a paragraph, even if doing so wouldn't require
                    wrapping it to several lines.  If False (the default),
                    a paragraph that only contains one line will not
                    be indented.
            width (int, optional): the maximum width of each line.  If
                    set to None, do not wrap anything.

        """
        vars = vars or {}
        paragraphs = self.text.splitlines()

        for num_line, paragraph in enumerate(paragraphs):
            words = paragraph.split(" ")
            for num_word, word in enumerate(words):
                if word.startswith("$"):
                    # Get the variable name, removing punctuation.
                    index = max(
                        (
                            i
                            for i in range(1, len(word))
                            if word[i : i + 1].isalpha()
                        ),
                        default=0,
                    )
                    if index > 0:
                        variable = word[1 : index + 1]
                        value = vars.get(variable, "")
                        words[num_word] = value + word[index + 1 :]

            paragraph = " ".join(words)
            limit = width
            if not indent_no_wrap:
                limit -= len(indent_with)

            if len(paragraph) > limit:
                paragraph = indent_with + paragraph
                paragraph = fill(paragraph, width)
            paragraphs[num_line] = paragraph

        return "\n".join(paragraphs)

    def raw(
        self,
        indent_all: str = "",
        indent_with: str = " " * 3,
        indent_no_wrap: bool = False,
        width: Optional[int] = 78,
        show_line_numbers: bool = False,
    ) -> str:
        """Return a raw description, with variables intact.

        Args:
            indent_all (str): the text to add before every line.
            indent_with (str, optional): the text to add before
                    each paragraph to indent, usually three spaces
                    or nothing.
            indent_no_wrap (bool, optional): add `indent_with` before
                    a paragraph, even if doing so wouldn't require
                    wrapping it to several lines.  If False (the default),
                    a paragraph that only contains one line will not
                    be indented.
            width (int, optional): the maximum width of each line.  If
                    set to None, do not wrap anything.
            show_line_numbers (bool, opt): show paragraph line numbers.

        """
        paragraphs = self.text.splitlines()

        if show_line_numbers:
            number_width = max(2, len(str(len(paragraphs))))

        for num_line, paragraph in enumerate(paragraphs):
            limit = width - len(indent_all)
            if not indent_no_wrap:
                limit -= len(indent_with)

            if show_line_numbers:
                number = str(num_line + 1)
                req_indent = f"{number:>{number_width}} "
            else:
                req_indent = ""

            limit -= len(req_indent)
            if len(paragraph) > limit:
                paragraph = indent_all + req_indent + indent_with + paragraph
                paragraph = f"\n{indent_all}{' ' * len(req_indent)}".join(
                    wrap(paragraph, width - len(indent_all) - len(req_indent))
                )
            else:
                indent = indent_all + req_indent
                if indent_no_wrap:
                    indent += indent_with
                paragraph = indent + paragraph

            paragraphs[num_line] = paragraph

        return "\n".join(paragraphs)

    def save(self):
        """Save the description."""
        type(self.parent).repository.update(
            self.parent, self.field, "", self.text
        )


class DescriptionField(CustomField):

    """A description stored in a string."""

    field_name = "description"

    def add(self):
        """Add this field to a model.

        Returns:
            annotation type (Any): the type of field to store.

        """
        return str

    def to_storage(self, value):
        """Return the value to store in the storage engine.

        Args:
            value (Any): the original value in the field.

        Returns:
            to_store (Any): the value to store.
            It must be of the same type as returned by `add`.

        """
        return str(value)

    def to_field(self, value: str):
        """Convert the stored value to the field value.

        Args:
            value (Any): the stored value (same type as returned by `add`).

        Returns:
            to_field (Any): the value to store in the field.
            It must be of the same type as the annotation hint used
            in the model.

        """
        return Description(value)
