from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Employee


def get(session: Session, employee_id: int) -> Employee | None:
    return session.get(Employee, employee_id)


def email_taken(session: Session, email: str, *, excluding_id: int | None = None) -> bool:
    query = select(Employee.id).where(Employee.email == email)
    if excluding_id is not None:
        query = query.where(Employee.id != excluding_id)
    return session.scalar(query) is not None


def code_taken(session: Session, employee_code: str) -> bool:
    query = select(Employee.id).where(Employee.employee_code == employee_code)
    return session.scalar(query) is not None


def add(session: Session, employee: Employee) -> Employee:
    session.add(employee)
    session.commit()
    session.refresh(employee)
    return employee
