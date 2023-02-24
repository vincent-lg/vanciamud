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

"""Module containing the database engine for TalisMUD.

This engine makes the link between database storage and the data being
stored.

The data is defined in a Pydantic class in Python.  Its table
structure can be automatically generated but this can be overridden.
Two types of data exist:

1.  Data without an in-game location.  Accounts, sessions and some
    world data can fall into that category.  These classes should
    inherit from `data.base.model.Model`.
2.  Data that has an in-game location.  Rooms, characters, in-game objects,
    vehicles, all have an optional location.  These classes
    should inherit from `data.base.node.Node` or
    `data.base.link.Link` (see these modules for details).

Data without any in-game location are usually stored in their specific
database table.  On the contrary, data with a specific in-game
location will be stored in a shared table (node or link).  This system
is used because all in-game objects have to remember where their location
is stored, therefore it is more convenient to have them reference
another row on the same table.

"""

from contextlib import contextmanager
from pathlib import Path
import pickle
from queue import Queue
from typing import Any, Callable, Tuple, Type

from pydantic import Field
from sqlalchemy import create_engine, delete, event, insert, select, update
from sqlalchemy import Column, Index, UniqueConstraint
from sqlalchemy import ForeignKey, Integer, LargeBinary, String
from sqlalchemy.sql.roles import SQLRole
from sqlalchemy.sql.type_api import TypeEngine

from data.base.abc import ModelMetaclass
from data.base.model import Model
from data.base.sql.cache import Cache
from data.base.sql.locator import Locator
from data.base.sql.registry import BASE, REGISTRY
from data.base.sql.session import TalisMUDSession
from data.base.sql.types import SQL_TYPES
from data.decorators import LazyPropertyDescriptor
from data.handler.abc import BaseHandler


class SqliteEngine:

    """A data storage engine using Sqlite."""

    def __init__(self):
        self.file_name = ""
        self.tables = {}
        self.models = {}
        self.engine = None
        self.metadata = REGISTRY.metadata
        self.cache = Cache()
        self.locator = Locator(self)
        self.session = None
        self.loading = 0

    def init(
        self,
        file_name: str | Path | None = None,
        memory: bool = False,
        logging: bool | Callable[[str, Tuple[Any]], None] = True,
    ) -> None:
        """Initialize the data engine.

        Args:
            file_name (str or Path): the file_name in which the database
                    is stored, or will be stored.  It can be a relative
                    or absolute file name.  If you want to just store
                    in memory, don't specify a file name and just set
                    the `memory` argument to `True`.
            memory (bool): whether to store this database in memory or
                    not?  If `True`, the file name is ignored.
            logging (bool or callable): if True (the default), log SQL queries.
                    A callable can also be specified: in this case,
                    the callable will be called whenever a query is
                    being sent, with two arguments: the query itself
                    as a string and the tuple of optional arguments (any type).

        """
        self.file_name = file_name if not memory else None
        self.logging = logging

        # Connect to the database.
        if memory:
            sql_file_name = ":memory:"
        else:
            if isinstance(file_name, str):
                file_name = Path(file_name)

            if file_name.absolute():
                sql_file_name = str(file_name)
            else:
                sql_file_name = str(file_name.resolve())
            self.file_name = file_name
        self.engine = create_engine(
            f"sqlite+pysqlite:///{sql_file_name}", future=True
        )
        self.session = TalisMUDSession(self.engine)
        self.session.talismud_engine = self

        # Add a function to override lower, as it only supports
        # ASCII in sqlite3.
        @event.listens_for(self.engine, "connect")
        def setup_lower(dbapi_connection, conn_rec):
            dbapi_connection.create_function("pylower", 1, str.lower)

        # Intercept requests to log them, if set.
        @event.listens_for(self.engine, "before_cursor_execute")
        def log_query(conn, cr, statement, parameters, *_):
            log = self.logging
            log = log if callable(log) else print
            if self.logging:
                log(statement.strip(), parameters)

        self.connection = self.engine.connect()
        self.tables = {}
        self.attr_tables = {}
        self.iattr_tables = {}

    def close(self):
        """Close the connection to the storage engine."""
        pass

    def destroy(self):
        """Close and destroy the storage engine."""
        for model in self.models.values():
            if not model.is_first_class:
                continue

            tables = self._get_three_tables(model)
            for table in tables:
                if table is not None:
                    instance = self.metadata.tables[table.__tablename__]
                    self.metadata.remove(instance)
                    REGISTRY._dispose_cls(table)
        self.close()
        if self.file_name:
            self.file_name.unlink()

    def bind(self, models: set[Model] | None = None) -> None:
        """Bind the models to this engine.

        Args:
            models (set, optional): the set of models.

        """
        ModelMetaclass.engine = self
        to_bind = ModelMetaclass.models if models is None else models

        # Force models without a clear base model to be set as first-class
        # models.
        models = []
        for model in to_bind:
            if getattr(model.__config__, "external_attrs", False):
                for field in model.__fields__.values():
                    info = field.field_info
                    if not info.extra.get("primary_key", False):
                        info.extra["external"] = True

            base_model = getattr(model.__config__, "base_model", "")
            path = model.class_path
            self.models[path] = model
            first_class = base_model != path
            if table := getattr(model.__config__, "table", None):
                self._record_table(model, table)
            if attr_table := getattr(model.__config__, "attr_table", None):
                self._record_nattr(model, attr_table)
            if iattr_table := getattr(model.__config__, "iattr_table", None):
                self._record_inattr(model, iattr_table)

            if path in self.tables:
                continue

            setattr(model.__config__, "first_class", first_class)
            if first_class:
                models.append(model)

        for model in models:
            self.bind_model(model)

        self.metadata.create_all(self.engine)

    def bind_model(self, model: Type[Model]) -> None:
        """Bind a new model, creating one or several tables.

        Models are Pydantic classes.  Each Pydantic field will match
        a SQL column in a table, unless this field is a specific attribute.
        Attributes are kept in a different table.  A third table can also
        be created to store indexed attributes with unique values
        for this model.

        Args:
            model (subclass of Model): the model class.

        """
        fields = {}
        external = indexed = False
        for key, field in model.__fields__.items():
            info = field.field_info
            external_attrs = getattr(model.__config__, "external_attrs", False)
            pickle_field = info.extra.get("pickled", False)
            if external_attrs or pickle_field:
                external = True
                if info.extra.get("unique", False):
                    indexed = True
            else:
                column, kwargs = self.get_model_column(model, field)
                if field.field_info.extra.get("primary_key", False):
                    pkey_name = key
                    pkey_column = column
                    kwargs["primary_key"] = True
                    if field.type_ is int:
                        kwargs["autoincrement"] = True

                fields[key] = Column(column, **kwargs)

        model_name = model.__name__
        fields["__tablename__"] = model_name
        table = type(model_name, (BASE,), fields)
        table.metadata = self.metadata
        self._record_table(model, table)

        # If necessary, create the table to store external attributes.
        if external:
            table_name = f"{model_name}_attr"
            fields = {
                "__tablename__": table_name,
                "id": Column(Integer, primary_key=True),
                "name": Column(String),
                "value": Column(LargeBinary),
                "model": Column(
                    pkey_column, ForeignKey(f"{model_name}.{pkey_name}")
                ),
                "uix_nn": UniqueConstraint("name", "model", name="uix_nn"),
                "un_nn": Index("un_nn", "name", "model", unique=True),
            }
            table = type(table_name, (BASE,), fields)
            table.metadata = self.metadata
            self._record_nattr(model, table)

            # If there are external attributes to index.
            if indexed:
                table_name = f"{model_name}_iattr"
                fields = {
                    "__tablename__": table_name,
                    "id": Column(Integer, primary_key=True),
                    "name": Column(String),
                    "value": Column(LargeBinary),
                    "class_path": Column(String),
                    "model": Column(
                        pkey_column, ForeignKey(f"{model_name}.{pkey_name}")
                    ),
                    "uix_inn": UniqueConstraint(
                        "name", "value", "class_path", name="uix_inn"
                    ),
                    "un_inn": Index(
                        "un_inn", "name", "value", "class_path", unique=True
                    ),
                }
                table = type(table_name, (BASE,), fields)
                table.metadata = self.metadata
                self._record_inattr(model, table)

    def clear_cache(self):
        """Clear all the engine's cache."""
        self.cache.clear()
        self.locator.clear()
        LazyPropertyDescriptor.memory.clear()

    def log(self, message: str, arguments: list[Any] | None = None):
        """Log the message, if appropriate.

        Args:
            message (str): the message.
            arguments (list, optional): the list of arguments.

        """
        if log := self.logging:
            log(message, arguments)

    def get_model_column(
        self, model: Type[Model], field: Field
    ) -> tuple[TypeEngine, dict[str, Any]]:
        """Retrieve the column type for a given field.

        This method is called to determine the column type (and keyword
        arguments) of an internal field.

        Args:
            model (subclass of Model): the model object.
            field (Field): the field.

        Returns:
            (column, kwargs): where `column` is a column type used in
                SQLAlchemy and `kwargs` is a dictionary of strings
                to options.

        """
        if column_data := SQL_TYPES.get(field.type_):
            column, kwargs, *_ = column_data
            return (column, dict(kwargs))

        return (LargeBinary, {})

    def create_model(self, model_class: Type[Model], **kwargs) -> Model:
        """Create a new model object, storing it in the database.

        Args:
            model_class (Model subclass): the model class.

        Returns:
            model (Model): the newly-created model.

        """
        path = model_class.class_path
        table, nattr, inattr = self._get_three_tables(model_class)
        if model_class.is_first_class:
            fields = self.as_fields(model_class, kwargs)
        else:
            if "class_path" in kwargs:
                raise ValueError(
                    "the field 'class_path' is reserved.  "
                    "This name cannot be used"
                )

            fields = {"class_path": path}

            for key, value in kwargs.items():
                field = model_class.__fields__[key]
                if model_class.is_base_field(field):
                    fields.update(self.as_fields(model_class, {key: value}))

        # Save in the database.
        statement = insert(table).values(**fields)
        result = self.session.execute(statement)

        # Iterate over primary key fields.
        values = iter(tuple(result.inserted_primary_key))
        pkey = None
        pkeys = {}
        for field in model_class.__fields__.values():
            is_pk = field.field_info.extra.get("primary_key", False)
            if field.name not in kwargs and is_pk:
                value = next(values)
                pkeys[field.name] = value
                pkey = value

        # Save the model external attributes.
        if nattr:
            for key, value in kwargs.items():
                field = model_class.__fields__[key]
                is_pk = field.field_info.extra.get("primary_key", False)
                is_external = field.field_info.extra.get("external", False)
                is_external = (
                    is_external
                    and not model_class.is_base_field(field)
                    or False
                )
                if is_pk or not is_external:
                    continue

                statement = insert(nattr).values(
                    name=key,
                    value=pickle.dumps(value),
                    model=pkey,
                )
                self.session.execute(statement)

        # Save the indexed node attributes (INattr.
        if inattr:
            for key, value in kwargs.items():
                field = model_class.__fields__[key]
                is_pk = field.field_info.extra.get("primary_key", False)
                is_external = field.field_info.extra.get("external", False)
                is_unique = field.field_info.extra.get("unique", False)
                if is_pk or not is_external or not is_unique:
                    continue
                value = kwargs[key]
                statement = insert(inattr).values(
                    name=key,
                    value=pickle.dumps(value),
                    class_path=path,
                    model=pkey,
                )
                self.session.execute(statement)

        # Build and return the model.
        kwargs.update(pkeys)
        kwargs.pop("class_path", None)

        with self._load_model():
            model = self._prepare_model(model_class, kwargs)
        self.cache.put(model)

        # Write the optional fields.
        if nattr:
            for key, value in model.__dict__.items():
                field = model_class.__fields__[key]
                is_pk = field.field_info.extra.get("primary_key", False)
                is_external = field.field_info.extra.get("external", False)
                is_external = (
                    is_external
                    and not model_class.is_base_field(field)
                    or False
                )
                if not is_pk and is_external and key not in kwargs:
                    statement = insert(nattr).values(
                        name=key,
                        value=pickle.dumps(value),
                        model=pkey,
                    )
                    self.session.execute(statement)

        return model

    def get_model(
        self, model_class: Type[Model], raise_not_found: bool = True, **kwargs
    ) -> Model | None:
        """Return the model with this class and ID.

        Args:
            model_class (Model subclass): the class.
            raise_not_found (bool, optional): if True (the default),
                    raise a NotFound exception if the model cannot be found.
                    Otherwise, return None.

        Additional keyword arguments are supported and should
        filter the result.

        Returns:
            model (instance of model class): if found, the model.
            None: the model couldn't be found and raise_not_found is False.

        Raises:
            NotFound if the model is not found and raise_not_found is True.

        """
        model = self.cache.get(model_class, **kwargs)
        if model is None:
            table, nattr, inattr = self._get_three_tables(model_class)
            keys = model_class.get_primary_keys_and_uniques_from_attrs(kwargs)
            where = [
                getattr(table, key) == value for key, value in keys.items()
            ]
            if not keys and inattr:
                statement = (
                    select(table, nattr)
                    .join_from(table, nattr)
                    .join_from(table, inattr)
                )

                for name, value in kwargs.items():
                    statement = statement.where(
                        (inattr.name == name)
                        & (inattr.value == pickle.dumps(value))
                    )
            elif nattr:
                statement = (
                    select(table, nattr).join_from(table, nattr).where(*where)
                )
            else:
                statement = select(table).where(*where)

            with self._load_model():
                rows = self.session.execute(statement).all()

            if len(rows) == 0:
                if raise_not_found:
                    raise ValueError("not found")

                return None

            obj = rows[0][0]
            if not model_class.is_first_class:
                model_class = ModelMetaclass.get_class_from_path(
                    obj.class_path
                )

            # Build and cache the object immediately.
            # No external attributes are read at this point.
            attrs = {
                column.name: getattr(obj, column.name)
                for column in obj.__table__.columns
                if getattr(obj, column.name, None) is not None
            }
            attrs.pop("class_path", ...)
            attrs = self.as_attributes(model_class, attrs)

            with self._load_model():
                model = self._prepare_model(model_class, attrs)

            self.cache.put(model)

            # Build attributes.
            for row in rows:
                try:
                    attr = row[1]
                except IndexError:
                    pass
                else:
                    with self._load_model():
                        setattr(model, attr.name, pickle.loads(attr.value))

            return model

        return model

    def select_models(
        self, model_class: Type[Model], query: SQLRole
    ) -> list[Model]:
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
        table, nattr, inattr = self._get_three_tables(model_class)
        if nattr:
            statement = (
                select(table, nattr).join_from(table, nattr).where(query)
            )
        else:
            statement = select(table).where(query)

        with self._load_model():
            rows = self.session.execute(statement).all()

        models = []
        for row in rows:
            if path := getattr(row[0], "class_path", None):
                model_class = ModelMetaclass.get_class_from_path(path)

            if len(row) > 1:
                external = row[1:]
                row = row[0]
            else:
                external = ()
                row = row[0]

            # Check whether the object is cached.
            attrs = {
                column.name: getattr(row, column.name)
                for column in row.__table__.columns
                if getattr(row, column.name, None) is not None
            }
            attrs.pop("class_path", False)
            pkeys = model_class.get_primary_keys_from_attrs(attrs)
            model = self.cache.get(model_class, **pkeys)
            if model is None:
                attrs = self.as_attributes(model_class, attrs)

                with self._load_model():
                    model = self._prepare_model(model_class, attrs)

                self.cache.put(model)

            # Build attributes.
            for attr in external:
                with self._load_model():
                    setattr(model, attr.name, pickle.loads(attr.value))

            if model not in models:
                models.append(model)

        return models

    def update(self, model: Model, key: str, value: Any):
        """Update the object.

        Args:
            model (Model): the model object.
            key (str): the key.
            value (Any): the new value.

        """
        if not self.loading:
            cls = type(model)
            field = cls.__fields__[key]
            info = field.field_info
            path = cls.class_path
            table, nattr, inattr = self._get_three_tables(cls)
            external_attrs = (
                not info.extra.get("primary_ke", False)
                and getattr(cls.__config__, "external_attrs", False)
                or False
            )
            pickle_field = info.extra.get("pickled", False)
            pkey = cls.get_primary_key_from_model(model)
            if cls.is_base_field(field):
                nattr = None

            if nattr and (external_attrs or pickle_field):
                statement = (
                    update(nattr)
                    .where((nattr.name == key) & (nattr.model == pkey))
                    .values(value=pickle.dumps(value))
                )
            else:
                pkeys = self.as_fields(
                    cls, cls.get_primary_keys_from_model(model)
                )
                pkey_column = getattr(table, list(pkeys.keys())[0])
                pkey_value = list(pkeys.values())[0]
                attrs = self.as_fields(type(model), {key: value})
                statement = (
                    update(table)
                    .where(pkey_column == pkey_value)
                    .values(**attrs)
                )
            self.session.execute(statement)

            # Update unique indexes.
            if inattr and info.extra.get("unique", False):
                statement = (
                    update(inattr)
                    .where(
                        (inattr.name == key)
                        & (inattr.class_path == path)
                        & (inattr.model == pkey)
                    )
                    .values(value=pickle.dumps(value))
                )

                self.session.execute(statement)

        self.cache.put(model)

    def delete(self, model: Model):
        """Delete the specified model.

        Args:
            model (Model): the model object.

        The model will be removed from the database.  Using the linked cache,
        the references to the now-deleted object will be updated.

        """
        cls = type(model)
        table, nattr, inattr = self._get_three_tables(cls)
        pkeys = cls.get_primary_keys_from_model(model)
        pkey_column = getattr(table, list(pkeys.keys())[0])
        pkey_value = list(self.as_fields(type(model), pkeys).values())[0]
        statement = delete(table).where(pkey_column == pkey_value)
        self.session.execute(statement)

        # Remove attributes, if need be.
        if nattr:
            statement = delete(nattr).where(nattr.model == pkey_value)
            self.session.execute(statement)

        # Remove indexesd attributes, if need be.
        if inattr:
            statement = delete(inattr).where(inattr.model == pkey_value)
            self.session.execute(statement)

        # Remove from cache.
        self.cache.delete(model, self.refresh_field_for)

    def refresh_field_for(self, model: Model, key: str):
        """Refresh the model field from database."""
        cls = type(model)
        table, nattr, inattr = self._get_three_tables(cls)
        pkey = cls.get_primary_key_from_model(model)
        field = cls.__fields__[key]
        info = field.field_info
        external_attrs = (
            not info.extra.get("primary_key", False)
            and getattr(cls.__config__, "external_attrs", False)
            or False
        )
        pickle_field = info.extra.get("pickled", False)
        if external_attrs or pickle_field:
            statement = select(nattr.value).where(
                (nattr.name == key) & (nattr.model == pkey)
            )
        else:
            column = list(cls.get_primary_keys_from_class().keys())[0]
            pkey_column = getattr(table, column)
            statement = select(getattr(table, key)).where(pkey_column == pkey)
        self.session.execute(statement)

        with self._load_model():
            values = self.session.execute(statement).one()
            if not values:
                return

        value = values[0]
        old_value = getattr(model, key, ...)
        new_value = pickle.loads(value)
        if old_value is not new_value:
            # Update the model.
            setattr(model, key, new_value)

    @contextmanager
    def _load_model(self):
        self.loading += 1
        try:
            yield
        finally:
            self.loading -= 1

    def _get_three_tables(
        self, model_class: Type[Model]
    ) -> tuple[BASE, BASE | None, BASE | None]:
        """Return table, attr, iattr tables."""
        path = model_class.class_path
        table = self.tables[path]
        attr_table = self.attr_tables.get(path)
        iattr_table = self.iattr_tables.get(path)
        return table, attr_table, iattr_table

    def _record_table(self, model_class: Type[Model], table: BASE) -> None:
        model_classes = Queue()
        model_classes.put(model_class)
        base = model_class.base_model
        while not model_classes.empty():
            model_class = model_classes.get()
            path = model_class.class_path
            self.tables[path] = table

            if model_class is base:
                continue

            for parent in model_class.__bases__:
                if issubclass(parent, Model):
                    model_classes.put(parent)

    def _record_nattr(self, model_class: Type[Model], table: BASE) -> None:
        model_classes = Queue()
        model_classes.put(model_class)
        base = model_class.base_model
        while not model_classes.empty():
            model_class = model_classes.get()
            path = model_class.class_path
            self.attr_tables[path] = table

            if model_class is base:
                continue

            for parent in model_class.__bases__:
                if issubclass(parent, Model):
                    model_classes.put(parent)

    def _record_inattr(self, model_class: Type[Model], table: BASE) -> None:
        model_classes = Queue()
        model_classes.put(model_class)
        base = model_class.base_model
        while not model_classes.empty():
            model_class = model_classes.get()
            path = model_class.class_path
            self.iattr_tables[path] = table

            if model_class is base:
                continue

            for parent in model_class.__bases__:
                if issubclass(parent, Model):
                    model_classes.put(parent)

    @staticmethod
    def as_fields(
        model_class: Type[Model], attributes: dict[str, Any]
    ) -> dict[str, Any]:
        """Return a dictionary of values ready to be stored.

        The returned dictionary is of the same length as
        the given dictionary, but its value are converted (if necessary),
        so that they can be directly stored in database.

        Args:
            model_class (subclass of Model): the model class.
            attributes (dict): the attributes.

        Returns:
            fields (dict): the field keys and values.

        """
        fields = {}
        default = (..., ..., pickle.dumps, ...)
        for key, value in attributes.items():
            field = model_class.__fields__[key]
            _, _, convert, _ = SQL_TYPES.get(field.type_, default)
            if convert is not ...:
                value = convert(value)
            fields[key] = value

        return fields

    @staticmethod
    def as_attributes(
        model_class: Type[Model], fields: dict[str, Any]
    ) -> dict[str, Any]:
        """Convert a dictionary of stored attributes to model fields.

        The returned dictionary is of the same length as
        the given dictionary, but its value are converted (if necessary),
        so that they can be directly placed in a Pydantic model.

        Args:
            model_class (subclass of Model): the model class.
            fields (dict): the fields as stored.

        Returns:
            attributes (dict): the attribute keys and values.

        """
        attributes = {}
        default = (...,) * 3 + (pickle.loads,)
        for key, value in fields.items():
            field = model_class.__fields__[key]
            _, _, _, convert = SQL_TYPES.get(field.type_, default)
            if convert is not ...:
                value = convert(value)
            attributes[key] = value

        return attributes

    @staticmethod
    def _prepare_model(
        model_class: Type[Model], attributes: dict[str, Any]
    ) -> Model:
        model = model_class(**attributes)
        for key, value in model.__dict__.items():
            if isinstance(value, BaseHandler):
                value.model = (model, key)

        return model
