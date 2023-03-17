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

"""World service, here to handle blueprints."""

from pathlib import Path
from typing import Any, Dict, Sequence

from dynaconf import settings

import yaml

from data.handler.abc import BaseHandler
from data.prototype.object import ObjectPrototype
from data.room import Room
from service.base import BaseService
from tools.logging.frequent import FrequentLogger

logger = FrequentLogger("world")
logger.setup()
MODELS = {
    "object": ObjectPrototype,
    "room": Room,
}


class Service(BaseService):

    """World service, to handle blueprints."""

    name = "world"

    async def init(self):
        """Asynchronously initialize the service.

        This method should be overridden in subclasses.  It is called by
        `start`` before sub-services are created.  It plays the role of
        an asynchronous constructor for the service, and service attributes
        often are created there for consistency.

        """
        self.blueprints = {}

    async def setup(self):
        """Set the MudIO up."""
        self.load_blueprints()
        data = self.parent.services["data"]

        for blueprint in self.blueprints.values():
            if settings.BLUEPRINT_AUTO_APPLY:
                with data.engine.session.begin():
                    blueprint.apply()

    async def cleanup(self):
        """Clean the service up before shutting down."""

    def load_blueprints(self):
        """Load all blueprints."""
        world_dir = (Path() / "../world").resolve()
        for file_path in world_dir.rglob("*.yml"):
            if file_path.is_dir():
                logger.warning(
                    f"{file_path} appears like a world file but is a directory"
                )
                continue

            # Try and read this file.
            try:
                with file_path.open("r", encoding="utf-8") as file:
                    content = file.read()
            except Exception:
                logger.exception(f"Cannot read {file_path}:")
            else:
                try:
                    blueprint = yaml.safe_load_all(content)
                except Exception:
                    logger.exception(f"Cannot parse {file_path}:")
                else:
                    relative = file_path.relative_to(world_dir)
                    bp_name = "/".join(relative.parts[:-1])
                    if bp_name:
                        bp_name += "/"
                    bp_name += file_path.stem
                    logger.debug(
                        f"Loaded {bp_name} in {file_path} successfully."
                    )

                    blueprint = Blueprint(bp_name, file_path, blueprint)
                    self.blueprints[bp_name] = blueprint


class Blueprint:

    """A blueprint object, containing world definitions."""

    def __init__(
        self,
        unique_name: str,
        file_path: Path,
        content: Sequence[Dict[str, Any]],
    ):
        self.unique_name = unique_name
        self.file_path = file_path
        self.content = content

    def apply(self):
        """Apply the entire blueprint."""
        for definition in self.content:
            d_type = definition.pop("type", None)
            if d_type is None:
                logger.warning(
                    f"This blueprint definition has no type: {definition}"
                )
                continue

            if d_type not in MODELS:
                logger.warning("Unknown type: {d_type}")
                continue

            model = MODELS[d_type]
            keys = {}
            for field in model.__fields__.values():
                if field.field_info.extra.get("bpk", False):
                    value = definition.get(field.name, ...)
                    if value is ...:
                        continue

                    keys[field.name] = value

            if not keys:
                logger.warning(
                    f"No blueprint key was identified for {definition}"
                )
                continue

            # Try go get the object from the database.
            obj = model.get(raise_not_found=False, **keys)
            path = model.class_path
            if obj is not None:
                logger.debug(f"{path} {obj} was found and will be updated.")

                for key, value in definition.items():
                    field = model.__fields__[key]
                    if issubclass(field.type_, BaseHandler):
                        getattr(obj, key).from_blueprint(value)
                    else:
                        setattr(obj, key, value)
            else:
                # The object will be created.
                logger.debug(f"Attempting to create {keys}")
                safe, handlers = {}, {}
                for field in model.__fields__.values():
                    value = definition.get(field.name, ...)
                    if value is ...:
                        continue

                    if issubclass(field.type_, BaseHandler):
                        handlers[field.name] = value
                    else:
                        safe[field.name] = value

                try:
                    obj = model.create(**safe)
                except Exception:
                    logger.exception(
                        f"An error occurred while creating {path}:"
                    )

                # Update the handler values.
                for key, value in handlers.items():
                    getattr(obj, key).from_blueprint(value)
