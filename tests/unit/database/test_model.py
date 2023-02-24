import pytest

from data.base.model import Field, Model


class User(Model):

    id: int = Field(primary_key=True)
    name: str


def test_create(db):
    db.bind({User})
    vincent = User.create(name="Vincent")
    assert vincent.id
    assert vincent.name == "Vincent"


def test_create_and_retrieve_from_cache(db):
    db.bind({User})
    vincent = User.create(name="Vincent")
    user = User.get(id=vincent.id)
    assert user is vincent


def test_create_and_retrieve_from_db(db):
    db.bind({User})
    vincent = User.create(name="Vincent")
    db.cache.clear()
    user = User.get(id=vincent.id)
    assert user is not vincent
    assert user.id == vincent.id
    assert user.name == vincent.name


def test_create_and_update(db):
    db.bind({User})
    vincent = User.create(name="Vincent")
    vincent.name = "Mark"
    assert vincent.name == "Mark"


def test_create_and_updateand_receive_from_cache(db):
    db.bind({User})
    vincent = User.create(name="Vincent")
    vincent.name = "Mark"
    user = User.get(id=vincent.id)
    assert user.name == "Mark"


def test_create_and_updateand_receive_from_db(db):
    db.bind({User})
    vincent = User.create(name="Vincent")
    vincent.name = "Mark"
    db.cache.clear()
    user = User.get(id=vincent.id)
    assert user.name == "Mark"


def test_create_and_delete_and_retrieve_From_cache(db):
    db.bind({User})
    vincent = User.create(name="Vincent")
    User.delete(vincent)

    with pytest.raises(ValueError):
        User.get(id=vincent.id)


def test_create_and_delete_and_retrieve_From_db(db):
    db.bind({User})
    vincent = User.create(name="Vincent")
    User.delete(vincent)
    db.cache.clear()

    with pytest.raises(ValueError):
        User.get(id=vincent.id)


class Person(Model):

    id: int = Field(primary_key=True)
    name: str
    age: int


def test_create_and_select_with_cache(db):
    db.bind({Person})
    vincent = Person.create(name="Vincent", age=34)
    vanessa = Person.create(name="Vanessa", age=28)
    anthony = Person.create(name="Anthony", age=33)
    results = Person.select(Person.table.age > 30)
    assert vincent in results
    assert anthony in results
    assert vanessa not in results


def test_create_and_select_with_db(db):
    db.bind({Person})
    vincent = Person.create(name="Vincent", age=34)
    vanessa = Person.create(name="Vanessa", age=28)
    anthony = Person.create(name="Anthony", age=33)
    db.cache.clear()
    results = Person.select(Person.table.age > 30)
    assert [person for person in results if person.id == vincent.id]
    assert [person for person in results if person.id == anthony.id]
    assert not [person for person in results if person.id == vanessa.id]
