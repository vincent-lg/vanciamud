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

"""Type handler, to store object types."""

from data.decorators import lazy_property
from data.handler.abc import BaseHandler
from data.type.abc import TypeMetaclass


class TypeHandler(BaseHandler):

    """A handler to hold object types."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._names = {}

    def __iter__(self):
        return iter(self._names.items())

    def __getstate__(self):
        attrs = {"_names": {key: None for key in self._names.keys()}}
        return attrs

    def __setstate__(self, attrs):
        self.__dict__.update(attrs)

    def __repr__(self):
        types = []
        for name in self._names.keys():
            type_name = name
            if type_name not in TypeMetaclass.types:
                type_name += " (INVALID)"

            types.append(type_name)

        types = ", ".join(types)
        return f"TypeHandler({types})"

    @property
    def stackable(self):
        """Return True if at least one type exists which is stackable."""
        types = [
            TypeMetaclass.types.get(type_name)
            for type_name in self._names.keys()
            if type_name in TypeMetaclass.types
        ]
        return any(type_.stackable for type_ in types)

    @lazy_property
    def prototype(self):
        """Return the prototype or None."""
        model, _ = self.model
        prototype = None
        if model.is_from("data.prototype.object"):
            prototype = model

        return prototype

    @lazy_property
    def object(self):
        """Return the object or None."""
        model, _ = self.model
        obj = None
        if model.is_from("data.object"):
            obj = model

        return obj

    def get(self, type_name: str):
        """Return the type of this name or None."""
        self._load_types()
        return self._names.get(type_name.lower())

    def add(
        self,
        type_name: str,
        quiet: bool = False,
        save: bool = True,
        setup: bool = True,
    ) -> None:
        """Add a type to this prototype or object.

        Args:
            type_name (str): the name of the type to add.
            quiet (bool): if True and the type doesn't exist,
                    raise an exception.
            save (bool): if True (the default), save in the database.
            setup (bool): if True (default), setup the individual object types.
                    Note that if `False`, the types are still copied but
                    not setup.

        """
        self._load_types()
        type_name = type_name.lower()
        o_type = TypeMetaclass.types.get(type_name)
        instance = None
        if o_type is None:
            if not quiet:
                raise ValueError(f"unknown type: {type_name!r}")

        else:
            if self._names and not self.stackable and o_type.stackable:
                if not quiet:
                    model, _ = self.model
                    types = ", ".join(
                        [type_.name for type_ in self._names.values()]
                    )
                    raise ValueError(
                        f"{model!r} is considered unique (non-stackable) "
                        f"because it has types {types} but adding type "
                        f"{type_name!r} would be inconsistent, since "
                        "this type is stackable"
                    )
            else:
                if prototype := self.prototype:
                    obj = None
                else:
                    obj = self.object
                    prototype = obj.prototype

                instance = o_type(prototype, obj)
                self._names[type_name] = instance

                if save:
                    self.save()

                if prototype := self.prototype:
                    for obj in prototype.objects:
                        obj.types.add(type_name, quiet=quiet, save=save)

                    # Setup the individual types.
                    if setup:
                        for _, o_type in obj.types:
                            o_type.setup_object()

        return instance

    def remove(
        self, type_name: str, quiet: bool = False, save: bool = True
    ) -> None:
        """Remove a type given its name.

        Args:
            type_name (str): the name of the type to remove.
            quiet (bool): if True and the type isn't present,
                    raise an exception.
            save (bool): if True (the default), save in the database.

        """
        self._load_types()
        type_name = type_name.lower()
        old = self._names.pop(type_name, None)
        if old is None:
            if not quiet:
                raise ValueError(f"no type {type_name!r} to remove")
        elif save:
            self.save()

    def from_blueprint(self, types: list[dict]):
        """Recover the types from a blueprint."""
        for definition in types:
            type_name = definition.pop("type", None)
            if type_name is None:
                continue

            instance = self.get(type_name)
            if instance is None:
                instance = self.add(
                    type_name, quiet=True, save=False, setup=False
                )
            instance.setup_prototype(**definition)

        if types:
            self.save()

    def _load_types(self):
        """Load the types if necessary."""
        for key, value in tuple(self._names.items()):
            if value is None:
                o_type = TypeMetaclass.types.get(key)

                if prototype := self.prototype:
                    obj = None
                else:
                    obj = self.object
                    prototype = obj.prototype

                instance = o_type(prototype, obj)
                self._names[key] = instance
