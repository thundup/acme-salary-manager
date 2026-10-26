import os
from collections.abc import Iterator
from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.deps import get_today
from app.config import Settings
from app.db import Base, build_engine, get_session
from app.main import create_app
from app.models import Currency
from app.reference import CURRENCIES, RATES_AS_OF

TODAY = date(2026, 10, 26)


TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL")


def _test_engine() -> Engine:
    if TEST_DATABASE_URL:
        return build_engine(Settings(database_url=TEST_DATABASE_URL).database_url)
    return create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )


@pytest.fixture
def session() -> Iterator[Session]:
    engine = _test_engine()
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with sessionmaker(bind=engine, expire_on_commit=False)() as session:
        session.add_all(
            Currency(
                code=c.code,
                minor_unit=c.minor_unit,
                inr_per_unit=c.inr_per_unit,
                rates_as_of=RATES_AS_OF,
            )
            for c in CURRENCIES.values()
        )
        session.commit()
        yield session
    engine.dispose()


@pytest.fixture
def client(session: Session) -> Iterator[TestClient]:
    app = create_app()
    app.dependency_overrides[get_session] = lambda: session
    app.dependency_overrides[get_today] = lambda: TODAY
    with TestClient(app) as client:
        yield client
