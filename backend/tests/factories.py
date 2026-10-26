from datetime import date
from itertools import count
from typing import Any

from sqlalchemy.orm import Session

from app.models import Employee

_sequence = count(1)


def employee_payload(**overrides: Any) -> dict[str, Any]:
    n = next(_sequence)
    payload: dict[str, Any] = {
        "employee_code": f"ACME-{n:06d}",
        "full_name": f"Asha Rao {n}",
        "email": f"asha.rao{n}@acme-corp.com",
        "job_title": "Senior Software Engineer",
        "department": "Engineering",
        "country_code": "IN",
        "currency_code": "INR",
        "salary_minor": 3_000_000_00,
        "bonus_minor": None,
        "employment_type": "full_time",
        "hire_date": "2024-01-15",
    }
    return {**payload, **overrides}


def add_employee(session: Session, **overrides: Any) -> Employee:
    data = employee_payload(**overrides)
    if isinstance(data["hire_date"], str):
        data["hire_date"] = date.fromisoformat(data["hire_date"])
    employee = Employee(**data)
    session.add(employee)
    session.commit()
    return employee
