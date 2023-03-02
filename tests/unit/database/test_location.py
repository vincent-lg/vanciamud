from random import shuffle

import pytest

from data.base.node import Node


class Room(Node):

    """A room."""

    title: str = "no title"
    description: str = "no description"


class Character(Node):

    """A character (playable or not)."""

    name: str = "unknown"


def test_create(db):
    db.bind({Room, Character})
    center = Room.create(title="center", description="the center")
    kredh = Character.create(name="Kredh")
    kredh.location = center
    assert kredh.location is center
    assert kredh in center.contents


def test_create_inside_move(db):
    db.bind({Room, Character})
    center = Room.create(title="center", description="the center")

    with pytest.raises(ValueError):
        center.location = center


def test_create_loop_move(db):
    db.bind({Room, Character})
    center = Room.create(title="center", description="the center")
    side = Room.create(title="side", description="the side")
    kredh = Character.create(name="Kredh")
    side.location = center
    kredh.location = side

    with pytest.raises(ValueError):
        center.location = kredh


def test_move_well_ordered(db):
    db.bind({Room, Character})
    center = Room.create(title="center", description="the center")
    characters = _create_characters(100)
    ids = [character.id for character in characters.values()]
    shuffle(ids)
    for character_id in ids:
        character = characters[character_id]
        character.location = center

    obtained = [character.id for character in center.contents]
    assert obtained == ids


def test_move_well_ordered_when_not_cached(db):
    db.bind({Room, Character})
    center = Room.create(title="center", description="the center")
    characters = _create_characters(100)
    ids = [character.id for character in characters.values()]
    shuffle(ids)
    for character_id in ids:
        character = characters[character_id]
        character.location = center

    db.clear_cache()
    center = Room.get(id=center.id)
    obtained = [character.id for character in center.contents]
    assert obtained == ids


class Coin(Node):

    """A coin."""

    name: str = "unknown"
    value: int = 1

    class Config:
        stackable = True


def test_stackable_add(db):
    db.bind({Room, Coin})
    center = Room.create(title="center", description="the center")
    dime = Coin.create(name="dime", value=10)
    center.locator.add(dime, 5)
    assert center.locator.how_many(dime) == 5


def test_stackable_add_and_get_from_DB(db):
    db.bind({Room, Coin})
    center = Room.create(title="center", description="the center")
    dime = Coin.create(name="dime", value=10)
    center.locator.add(dime, 5)
    db.clear_cache()
    center = Room.get(id=center.id)
    dime = Coin.get(id=dime.id)
    assert center.locator.how_many(dime) == 5


def test_stackable_transfer(db):
    db.bind({Room, Coin})
    center = Room.create(title="center", description="the center")
    side = Room.create(title="side", description="the side")
    dime = Coin.create(name="dime", value=10)
    center.locator.add(dime, 5)
    side.locator.transfer(dime, center, 3)
    assert center.locator.how_many(dime) == 2
    assert side.locator.how_many(dime) == 3


def test_stackable_transfer_and_clear_cache(db):
    db.bind({Room, Coin})
    center = Room.create(title="center", description="the center")
    side = Room.create(title="side", description="the side")
    dime = Coin.create(name="dime", value=10)
    center.locator.add(dime, 5)
    side.locator.transfer(dime, center, 3)
    db.clear_cache()
    center = Room.get(id=center.id)
    side = Room.get(id=side.id)
    dime = Coin.get(id=dime.id)
    assert center.locator.how_many(dime) == 2
    assert side.locator.how_many(dime) == 3


def test_stackable_add_non_stackables(db):
    db.bind({Room, Character})
    center = Room.create(title="center", description="the center")
    kredh = Character.create(name="Kredh")

    with pytest.raises(ValueError):
        center.locator.add(kredh, 1)


def test_stackable_set_location(db):
    db.bind({Room, Coin})
    center = Room.create(title="center", description="the center")
    dime = Coin.create(name="dime", value=10)

    with pytest.raises(ValueError):
        dime.location = center


def _create_characters(number):
    characters = {}
    for indice in range(1, number + 1):
        character = Character.create(name=f"char_{indice}")
        characters[character.id] = character

    return characters
