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

"""Module containing the `Model` class from which all models should inherit."""

from itertools import chain
from typing import Any, Type, TYPE_CHECKING

from pydantic import Field
from pydantic.main import ModelMetaclass as BaseModelMetaclass
from sqlalchemy.sql.roles import SQLRole

from data.base.sql.registry import BASE

if TYPE_CHECKING:
    from data.base.model import Model


class ModelMetaclass(BaseModelMetaclass):

    """Metaclass common to all models stored in TalisMUD."""

    models = set()
    paths = {}
    engine = None

    def __new__(
        metacls, name: str, bases: tuple[type], attrs: dict[str:Any]
    ) -> None:
        cls = super().__new__(metacls, name, bases, attrs)
        ModelMetaclass.models.add(cls)
        ModelMetaclass.paths[cls.class_path] = cls
        cls.__config__.primary_keys = cls.get_primary_keys_from_class()
        return cls

    @property
    def class_path(cls) -> str:
        return f"{cls.__module__}.{cls.__qualname__}"

    @property
    def base_model(cls) -> Type["Model"]:
        """Return the base model of the specified model class.

        A model class can inherit from a base class that defines
        its structure.  First class models do not have a base class,
        just themselves (so they store all their data in a specific table).
        Models that do have a base class configured record their data in
        a table shared with other classes, thus they need to remember
        the `class_path` for every row in the table.

        Args:
            None.

        Returns:
            base_model (subclass of Model): the model base class.

        """
        base_model = getattr(cls.__config__, "base_model", "")

        # Try to get the base model.
        if not base_model:
            return cls

        base = cls.get_class_from_path(base_model, raise_error=False)
        if base is None:
            raise ValueError(
                f"the {cls} class model defines "
                f"{base_model!r} has base model, but this model "
                "path cannot be found"
            )

        return base

    @property
    def is_first_class(cls) -> bool:
        """Return whether this model is a first class model."""
        return cls.base_model is cls

    @property
    def table(cls) -> BASE:
        """Return the class table from the engine."""
        path = cls.base_model.class_path
        return cls.engine.tables[path]

    def is_base_field(cls, field: Field) -> bool:
        """Return whether this field is a base field.

        Base fields are defined in base models.

        Args:
            field (Field): the field to test.

        Returns:
            base (bool): whether this field is a base field or not.

        """
        base = cls.base_model
        return field.name in base.__fields__

    def create(cls, **kwargs):
        """Create a node and store it in the database.

        Args:
            Other attributes can also be used.
            They should match the object fields.

        Returns:
            node (Node or subclass): the node object.

        """
        return ModelMetaclass.engine.create_model(cls, **kwargs)

    def get(cls, **kwargs):
        """Try to retrieve the object from storage."""
        return ModelMetaclass.engine.get_model(cls, **kwargs)

    def select(cls, query: SQLRole) -> list["Model"]:
        """Select several model objects from the database.

        The query has to be specified using the SQLAlchemy syntax,
        preferably using the `Model.table` property.

        Args:
            mode_class (subclass of Model): the model class.
            query (query): the SQL query object.

        Returns:
            results (list of models): a list of Model objects.

        Example:

            >>> User.select(User.table.name == "something")
            [...]

        """
        return ModelMetaclass.engine.select_models(cls, query)

    def delete(self, model: "Model"):
        """Delete the specified model."""
        ModelMetaclass.engine.delete(model)

    def get_primary_keys_from_class(cls) -> dict[str, Field]:
        """Return the primary key fields in a dictionary.

        Args:
            None.

        Returns:
            primary_keys (dict): the primary key fields, with field names
                    as keys and fields as values.

        """
        pkeys = {}
        for field in cls.__fields__.values():
            if field.field_info.extra.get("primary_key", False):
                pkeys[field.name] = field

        return pkeys

    def get_primary_keys_from_values(cls, *values) -> dict[str, Any]:
        """Return the primary key fields from values in a dictionary.

        Each value is to be speicifed as an additional positional argument.

        Args:
            Values.

        Returns:
            primary_keys (dict): the primary key fields, with field names
                    as keys and matching values as values.

        """
        pkeys = {}
        primary_fields = cls.get_primary_keys_from_class()
        values = iter(list(values))
        for key, field in primary_fields.items():
            value = next(values)
            pkeys[key] = value

        return pkeys

    def get_primary_keys_from_attrs(
        cls, attrs: dict[str, Any], sanitize: bool = True
    ) -> dict[str, Any]:
        """Return the primary key fields from attributes.

        Args:
            attrs (dict): the attributes.
            sanitize (bool): if set to True (the default),
                    attribute values will be "sanitized", converted
                    to their database value if necessary.

        Returns:
            primary_keys (dict): the primary key fields, with field names
                    as keys and values as values.

        """
        if sanitize:
            attrs = ModelMetaclass.engine.as_fields(cls, attrs)

        pkeys = {}
        primary_fields = cls.get_primary_keys_from_class()
        for key, field in primary_fields.items():
            value = attrs.get(key, ...)
            if value is not ...:
                pkeys[key] = value

        return pkeys

    def get_primary_keys_and_uniques_from_attrs(
        cls, attrs: dict[str, Any], sanitize: bool = True
    ) -> dict[str, Any]:
        """Return the primary key and unique fields from attributes.

        Args:
            attrs (dict): the attributes.
            sanitize (bool): if set to True (the default),
                    attribute values will be "sanitized", converted
                    to their database value if necessary.

        Returns:
            primary_keys (dict): the primary key and unique fields,
                    with field names as keys and values as values.

        """
        if sanitize:
            attrs = ModelMetaclass.engine.as_fields(cls, attrs)

        keys = {}
        for key, value in attrs.items():
            field = cls.__fields__[key]
            pk = field.field_info.extra.get("primary_key", False)
            unique = field.field_info.extra.get("unique", False)
            if pk or unique:
                keys[key] = value

        return keys

    def get_primary_keys_from_model(
        cls, model: "Model", as_tuple: bool = False
    ) -> tuple[Any] | dict[str, Any]:
        """Return the primary key values from a model.

        If `as_tuple` is set to `True`, return a flattened tuple of
        `(key1, value1, key2, value2, ...)`.  Otherwise, return a dictionary.

        Args:
            model (Model): the model.
            as_tuple (bool, optional): should a tuple be returned?

        Returns:
            primary_keys (dict or tuple): the primary keys, with field names
                    as keys and model values as values.  If `as_tuple`
                    is set to `True`, return a flattened tuple instead.

        """
        pkeys = {}
        for key in cls.get_primary_keys_from_class().keys():
            value = getattr(model, key)
            pkeys[key] = value

        if as_tuple:
            pkeys = sorted([(key, value) for key, value in pkeys.items()])
            pkeys = tuple(chain.from_iterable(pkeys))

        return pkeys

    def get_primary_key_from_model(cls, model: "Model") -> Any:
        """Return the only primary key for this model.

        If this model has more than one primary key, an exception is raised.

        Args:
            model (Model): the model.

        Returns:
            key (Any): the primary key value for this model.

        Raises:
            ValueError if the model has more than one primary keys.

        """
        pkeys = cls.get_primary_keys_from_model(model)
        if len(pkeys) != 1:
            raise ValueError(
                f"there is {len(pkeys)} primary key attributes "
                f"on {cls}, only one is supported"
            )

        return list(pkeys.values())[0]

    @staticmethod
    def get_class_from_path(
        class_path: str, raise_error: bool = True
    ) -> Type["Model"]:
        """Return, if found, the class matching this class path."""
        cls = ModelMetaclass.paths.get(class_path)
        if cls is None and raise_error:
            raise ValueError(
                f"cannot find the class matching the path: {class_path!r}"
            )

        return cls
