from collections.abc import Mapping
from datetime import date, datetime
from typing import Any

from sqlalchemy.orm import Session

from app.domain.employee import EmployeeStatus, employee_rule_violations
from app.models import Employee
from app.repositories import employees as repo
from app.schemas import EmployeeCreate, EmployeeUpdate
from app.services.errors import (
    DuplicateEmployee,
    EmployeeNotFound,
    EmployeeTerminated,
    RuleViolation,
)

NULLABLE_FIELDS = frozenset({"bonus_minor"})
RULE_FIELDS = ("department", "job_title", "country_code", "currency_code", "hire_date")


def _enforce_rules(values: Mapping[str, Any], today: date) -> None:
    violations = employee_rule_violations(**{f: values[f] for f in RULE_FIELDS}, today=today)
    if violations:
        raise RuleViolation(violations)


def create_employee(session: Session, data: EmployeeCreate, today: date) -> Employee:
    _enforce_rules(data.model_dump(), today)
    if repo.code_taken(session, data.employee_code):
        raise DuplicateEmployee("employee_code")
    if repo.email_taken(session, data.email):
        raise DuplicateEmployee("email")
    return repo.add(session, Employee(**data.model_dump()))


def get_employee(session: Session, employee_id: int) -> Employee:
    employee = repo.get(session, employee_id)
    if employee is None:
        raise EmployeeNotFound()
    return employee


def list_employees(session: Session, query: repo.EmployeeListQuery) -> tuple[list[Employee], int]:
    return repo.list_page(session, query)


def update_employee(
    session: Session, employee_id: int, patch: EmployeeUpdate, today: date
) -> Employee:
    employee = get_employee(session, employee_id)
    if employee.status == EmployeeStatus.TERMINATED:
        raise EmployeeTerminated()

    changes = patch.model_dump(exclude_unset=True)
    emptied = {
        field: "Cannot be empty"
        for field, value in changes.items()
        if value is None and field not in NULLABLE_FIELDS
    }
    if emptied:
        raise RuleViolation(emptied)

    _enforce_rules({f: getattr(employee, f) for f in RULE_FIELDS} | changes, today)
    if "email" in changes and repo.email_taken(session, changes["email"], excluding_id=employee.id):
        raise DuplicateEmployee("email")

    for field, value in changes.items():
        setattr(employee, field, value)
    return repo.save(session, employee)


def terminate_employee(session: Session, employee_id: int, now: datetime) -> None:
    employee = get_employee(session, employee_id)
    if employee.status == EmployeeStatus.TERMINATED:
        return
    employee.status = EmployeeStatus.TERMINATED
    employee.terminated_at = now
    repo.save(session, employee)
