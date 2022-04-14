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

"""Contexts custom field, to hold contexts."""

import pickle
from typing import Optional

from pygasus.model import CustomField

from context.base import Context, CONTEXTS


class Contexts(list):

    """An extended list of contexts for a character."""

    def __init__(self, *args, **kwargs):
        self.parent = None
        self.field = None
        self._contexts = []
        self._default_context = None
        super().__init__(*args, **kwargs)

    @property
    def active(self):
        """Return the active context."""
        self._build_contexts()

        try:
            index = self.index(...)
        except ValueError:
            return self._default_context

        # Ellipsis is before the active context.
        if index + 1 >= len(self):
            return self._default_context

        return self._contexts[index + 1]

    def _build_contexts(self):
        """Build the contexts in cache."""
        if len(self) == len(self._contexts) and self._default_context:
            return

        # Build context objects.
        contexts = []
        for definition in self:
            if definition is ...:
                contexts.append(...)
                continue

            context_path, context_options = definition
            if (context_cls := CONTEXTS.get(context_path)) is not None:
                context = context_cls(
                    self.parent.session, options=context_options
                )
                contexts.append(context)
        self._contexts = contexts

        # Create the default context.
        default_cls = CONTEXTS.get("character.game")
        if default_cls is None:
            raise ValueError("the ddefault context cannot be found")

        self._default_context = default_cls(self.parent.session)

    def add(
        self,
        context_path: str,
        options: Optional[dict] = None,
        active: bool = True,
        silent: bool = False,
    ):
        """Add a new context at the top of the stack.

        This context will become the active one if `active` is set
        to `True` (the default).

        Args:
            context_path (str): the path leading to the context.
            options (dict, optional): the context options.
            active (bool, optional): whether this context should become
                the active one (`True` by default).
            silent (bool): if set to `True`, do not call the new context's
                    `enter` method, which might display text.

        """
        context_cls = CONTEXTS.get(context_path)
        if context_cls is None:
            raise ValueError(f"can't find this context: {context_path!r}")

        # Create the new context, so an exception wouldn't save anything.
        new_context = context_cls(self.parent.session, options)

        # Call `enter`.
        if not silent:
            new_context.enter()

        # Remove the active context if appropriate.
        if active:
            for to_clean in (self, self._contexts):
                while ... in to_clean:
                    to_clean.remove(...)

        # Add the new context.
        self.insert(0, (context_path, options))
        self._contexts.insert(0, new_context)

        # Set this new context to active if appropriate.
        if active:
            for affected in (self, self._contexts):
                affected.insert(0, ...)

        self.save()
        return new_context

    def remove(self, context: Context, silent: bool = False):
        """Remove a context from the context stack.

        To remove a context, specify the context to remove (the context
        object) as argumment.

        If the removed context is the active one, the next in the stack
        will become active.

        Args:
            contexx (Context): the context to remove.
            silent (bool): if set to `True`, do not call the context's
                    `leave` method, which might display text.


        If no context match, raise a ValueError exception.

        """
        if context in self._contexts:
            if not silent:
                context.leave()

            index = self._contexts.index(context)
            del self._contexts[index]
            del self[index]

            # If the last context is active, remove the ellipsis.
            if self._contexts[-1] is ...:
                self._contexts.pop()
                self.pop()

            self.save()
        else:
            raise ValueError("this context isn't present in the context stack")

    def handle_input(self, user_input: str):
        """Find the proper context and send the input to it.

        Args:
            user_input (str): the input to process.

        This method is responsible for selecting the proper context,
        parsing the "change context" characters and handing the input
        to the context.

        """
        active = self.active
        return active.handle_input(user_input)

    def save(self):
        """Save the list of contexts in the parent."""
        type(self.parent).repository.update(
            self.parent, self.field, [], self.copy()
        )


class ContextsField(CustomField):

    """A list stored in a pickled bytestring."""

    field_name = "contexts"

    def add(self):
        """Add this field to a model.

        Returns:
            annotation type (Any): the type of field to store.

        """
        return bytes

    def to_storage(self, value):
        """Return the value to store in the storage engine.

        Args:
            value (Any): the original value in the field.

        Returns:
            to_store (Any): the value to store.
            It must be of the same type as returned by `add`.

        """
        return pickle.dumps(value)

    def to_field(self, value: bytes):
        """Convert the stored value to the field value.

        Args:
            value (Any): the stored value (same type as returned by `add`).

        Returns:
            to_field (Any): the value to store in the field.
            It must be of the same type as the annotation hint used
            in the model.

        """
        data = pickle.loads(value)
        return Contexts(data)
