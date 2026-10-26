from collections.abc import Sequence
from itertools import batched
from typing import Any

from sqlalchemy import Insert, delete, func, select
from sqlalchemy.dialects import postgresql, sqlite
from sqlalchemy.orm import Session

from app.models import Employee, utc_now

CHUNK_SIZE = 1_000


def seed_employees(
    session: Session, employees: Sequence[dict[str, Any]], *, reset: bool = False
) -> int:
    if reset:
        session.execute(delete(Employee))
    before = _count(session)
    now = utc_now()
    for chunk in batched(employees, CHUNK_SIZE):
        session.execute(
            _insert_ignoring_conflicts(session),
            [{**row, "status": "active", "created_at": now, "updated_at": now} for row in chunk],
        )
    session.commit()
    return _count(session) - before


def _insert_ignoring_conflicts(session: Session) -> Insert:
    if session.get_bind().dialect.name == "postgresql":
        return postgresql.insert(Employee).on_conflict_do_nothing()
    return sqlite.insert(Employee).on_conflict_do_nothing()


def _count(session: Session) -> int:
    return session.scalar(select(func.count()).select_from(Employee)) or 0
