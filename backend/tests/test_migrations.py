from collections.abc import Iterator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import Currency
from app.reference import CURRENCIES


@pytest.fixture
def migrated_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[str]:
    url = f"sqlite:///{tmp_path / 'migrated.db'}"
    monkeypatch.setenv("DATABASE_URL", url)
    get_settings.cache_clear()
    command.upgrade(Config("alembic.ini"), "head")
    yield url
    get_settings.cache_clear()


def test_migrations_produce_the_schema_the_models_describe(migrated_db: str) -> None:
    command.check(Config("alembic.ini"))


def test_migrations_load_every_reference_currency(migrated_db: str) -> None:
    engine = create_engine(migrated_db)
    with Session(engine) as session:
        codes = set(session.scalars(select(Currency.code)))
        tables = inspect(engine).get_table_names()
    engine.dispose()

    assert codes == set(CURRENCIES)
    assert "employees" in tables
