from collections.abc import Sequence
from itertools import batched
from typing import Any

from sqlalchemy import Insert, delete, func, select, text
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
        rows = [{**row, "status": "active", "created_at": now, "updated_at": now} for row in chunk]
        session.execute(_insert_ignoring_conflicts(session).values(rows))
    session.commit()
    _refresh_planner_statistics(session)
    return _count(session) - before


def _refresh_planner_statistics(session: Session) -> None:
    session.execute(text("ANALYZE"))
    session.commit()


def _insert_ignoring_conflicts(session: Session) -> Insert:
    if session.get_bind().dialect.name == "postgresql":
        return postgresql.insert(Employee).on_conflict_do_nothing()
    return sqlite.insert(Employee).on_conflict_do_nothing()


def _count(session: Session) -> int:
    return session.scalar(select(func.count()).select_from(Employee)) or 0
