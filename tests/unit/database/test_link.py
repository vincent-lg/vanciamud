from data.base.link import Link
from data.base.node import Node


class Room(Node):

    """A room."""

    title: str = "no title"
    description: str = "no description"


class Exit(Link):

    """An exit between rooms."""

    name: str = "unknown"


def test_create(db):
    db.bind({Room, Exit})
    center = Room.create(title="center", description="the center")
    side = Room.create(title="side", description="a side-room")
    east = Exit.create(
        key="east", origin_id=center.id, destination_id=side.id, name="east"
    )
    assert east.id


def test_create_and_get_from_DB(db):
    db.bind({Room, Exit})
    center = Room.create(title="center", description="the center")
    side = Room.create(title="side", description="a side-room")
    east = Exit.create(
        key="east", origin_id=center.id, destination_id=side.id, name="east"
    )
    db.clear_cache()
    center = Room.get(id=center.id)
    side = Room.get(id=side.id)
    east = Exit.get(id=east.id)
    assert east.name == "east"
