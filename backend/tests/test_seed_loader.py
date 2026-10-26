from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Employee
from app.seed.generator import generate_employees, load_names
from app.seed.loader import seed_employees
from tests.factories import add_employee

FIRST, LAST = load_names()


def rows(count: int) -> list[dict[str, object]]:
    return generate_employees(count, seed=42, first_names=FIRST, last_names=LAST)


def employee_count(session: Session) -> int:
    return session.scalar(select(func.count()).select_from(Employee)) or 0


def test_inserts_every_generated_employee(session: Session) -> None:
    inserted = seed_employees(session, rows(250))

    assert inserted == 250
    assert employee_count(session) == 250


def test_running_twice_inserts_nothing_new(session: Session) -> None:
    seed_employees(session, rows(250))

    assert seed_employees(session, rows(250)) == 0
    assert employee_count(session) == 250


def test_does_not_overwrite_edits_to_seeded_employees(session: Session) -> None:
    seed_employees(session, rows(10))
    edited = session.scalars(select(Employee).where(Employee.employee_code == "ACME-000001")).one()
    edited.salary_minor = 1
    session.commit()

    seed_employees(session, rows(10))

    session.refresh(edited)
    assert edited.salary_minor == 1


def test_reset_replaces_all_employees(session: Session) -> None:
    add_employee(session, employee_code="ACME-999999")

    inserted = seed_employees(session, rows(20), reset=True)

    assert inserted == 20
    assert employee_count(session) == 20
