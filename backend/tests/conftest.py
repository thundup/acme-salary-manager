from collections.abc import Iterator
from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.deps import get_today
from app.db import Base, get_session
from app.main import create_app
from app.models import Currency
from app.reference import CURRENCIES, RATES_AS_OF

TODAY = date(2026, 10, 26)


@pytest.fixture
def session() -> Iterator[Session]:
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
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
