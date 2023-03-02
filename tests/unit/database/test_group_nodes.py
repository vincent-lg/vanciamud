import pytest

from data.base.node import Field, Node


class Character(Node):

    name: str = "not yet"
    age: int = 0


class Player(Character):

    player_name: str = Field("unknown", unique=True)
    log_at: int = 0


class NPC(Character):

    origin: str = "not set"


def test_create_without_index(db):
    db.bind({Character, Player, NPC})
    vincent = NPC.create(name="Vincent", age=20, origin="here")
    assert vincent.id
    assert vincent.name == "Vincent"
    assert vincent.age == 20
    assert vincent.origin == "here"


def test_create_without_index_and_get_from_DB(db):
    db.bind({Character, Player, NPC})
    vincent = NPC.create(name="Vincent", age=20, origin="here")
    db.clear_cache()
    vincent = NPC.get(id=vincent.id)
    assert vincent.id
    assert vincent.name == "Vincent"
    assert vincent.age == 20
    assert vincent.origin == "here"


def test_create_with_index(db):
    db.bind({Character, Player, NPC})
    vincent = Player.create(name="Vincent", age=20, player_name="v", log_at=3)
    assert vincent.id
    assert vincent.name == "Vincent"
    assert vincent.age == 20
    assert vincent.player_name == "v"
    assert vincent.log_at == 3


def test_create_with_index_and_get_from_DB(db):
    db.bind({Character, Player, NPC})
    vincent = Player.create(name="Vincent", age=20, player_name="v", log_at=3)
    db.clear_cache()
    vincent = Player.get(id=vincent.id)
    assert vincent.id
    assert vincent.name == "Vincent"
    assert vincent.age == 20
    assert vincent.player_name == "v"
    assert vincent.log_at == 3


def test_create_get_update_base_without_index(db):
    db.bind({Character, Player, NPC})
    vincent = NPC.create(name="Vincent", age=20, origin="here")
    vincent.name = "Mathilde"
    db.clear_cache()
    vincent = NPC.get(id=vincent.id)
    assert vincent.id
    assert vincent.name == "Mathilde"
    assert vincent.age == 20
    assert vincent.origin == "here"


def test_create_get_update_sub_without_index(db):
    db.bind({Character, Player, NPC})
    vincent = NPC.create(name="Vincent", age=20, origin="here")
    vincent.origin = "away"
    db.clear_cache()
    vincent = NPC.get(id=vincent.id)
    assert vincent.id
    assert vincent.name == "Vincent"
    assert vincent.age == 20
    assert vincent.origin == "away"


def test_create_get_update_base_with_index(db):
    db.bind({Character, Player, NPC})
    vincent = Player.create(name="Vincent", age=20, player_name="v", log_at=3)
    vincent.name = "Mathilde"
    db.clear_cache()
    vincent = Player.get(id=vincent.id)
    assert vincent.id
    assert vincent.name == "Mathilde"
    assert vincent.age == 20
    assert vincent.player_name == "v"
    assert vincent.log_at == 3


def test_create_get_update_sub_with_index(db):
    db.bind({Character, Player, NPC})
    vincent = Player.create(name="Vincent", age=20, player_name="v", log_at=3)
    vincent.player_name = "Mathilde"
    db.clear_cache()
    vincent = Player.get(id=vincent.id)
    assert vincent.id
    assert vincent.name == "Vincent"
    assert vincent.age == 20
    assert vincent.player_name == "Mathilde"
    assert vincent.log_at == 3


def test_count(db):
    db.bind({Character, Player, NPC})
    Player.create(name="Vincent", age=20, player_name="v", log_at=3)
    NPC.create(name="Vincent", age=20, origin="here")
    assert Player.count() == 1
    assert NPC.count() == 1


def test_create_and_get_invalid(db):
    db.bind({Character, Player, NPC})
    v1 = Player.create(name="Vincent", age=20, player_name="v", log_at=3)
    v2 = NPC.create(name="Vincent", age=20, origin="here")
    db.clear_cache()

    with pytest.raises(ValueError):
        NPC.get(id=v1.id)

    with pytest.raises(ValueError):
        Player.get(id=v2.id)
