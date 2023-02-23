import pytest

from data.base.sql.engine import SqliteEngine

@pytest.fixture(scope="function")
def db():
    engine = SqliteEngine()
    engine.init(memory=True, logging=False)
    yield engine
    engine.destroy()
