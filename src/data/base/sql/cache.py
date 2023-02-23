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

"""Module containing the database cache for TalisMUD."""

from collections import defaultdict
from typing import Callable, Type

from data.base.model import Model


class Cache:

    """Cache for the database engine."""

    def __init__(self):
        self.models = defaultdict(dict)
        self.linked_cache = defaultdict(set)

    def put(self, model: Model) -> None:
        """Cache the given model object.

        Args:
            model (Model): the model object to be cached.

        Write the model in cache, so it can be retrieved later if necessary.

        """
        cls = type(model)
        pkeys = cls.get_primary_keys_from_model(model, as_tuple=True)
        base = cls.base_model
        self.models[base][pkeys] = model

        # Cache unique attributes.
        for key, field in cls.__fields__.items():
            if field.field_info.extra.get("unique", False):
                value = getattr(model, key)
                self.models[cls][(key, value)] = model

        # Cache the linked models.
        pkey = cls.get_primary_key_from_model(model)
        for key, field in cls.__fields__.items():
            value = getattr(model, key)
            if isinstance(value, Model):
                vkey = type(value).get_primary_key_from_model(value)
                self.linked_cache[(type(value), vkey)].add(
                    (type(model), pkey, key)
                )

    def get(self, model_class: Type[Model], **kwargs) -> Model | None:
        """Return an object from cache or None.

        If the model isn't found in cache, return None.

        Args:
            model_class (Node subclass): the model class.

        Additional keyword arguments are used to filter.

        Returns:
            model (subclass of Model): the model or None.

        """
        model_class = model_class.base_model
        for key, value in kwargs.items():
            return self.models.get(model_class, {}).get((key, value))

    def delete(
        self, model: Model, linked_callback: Callable[[Model, str], None]
    ) -> None:
        """Remove a model from cache.

        For each linked attribute, if a model is found,
        call the specificed callback to refresh it.

        Args:
            model (Model): the model to remove from cache.
            linked_Callback (callable): the callback to call for
                    every cached model referring to the model to be deleted.
                    This allows to clear up the cache of deleted models.

        """
        cls = type(model)
        base = cls.base_model
        pkey = cls.get_primary_key_from_model(model)
        self.models.get(base, {}).pop(
            cls.get_primary_keys_from_model(model, as_tuple=True), False
        )

        # Update the linked references.
        linked = self.linked_cache.pop((cls, pkey), [])
        for model_class, vkey, field_name in linked:
            vkeys = model_class.get_primary_keys_from_values(vkey)
            if model := self.get(model_class, **vkeys):
                linked_callback(model, field_name)

    def clear(self):
        """Clear the cache."""
        self.models.clear()
        self.linked_cache.clear()
