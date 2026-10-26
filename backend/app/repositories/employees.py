from dataclasses import dataclass
from typing import Literal

from sqlalchemy import ColumnElement, func, or_, select
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


SORTABLE_COLUMNS = {
    "full_name": Employee.full_name,
    "email": Employee.email,
    "employee_code": Employee.employee_code,
    "job_title": Employee.job_title,
    "department": Employee.department,
    "country_code": Employee.country_code,
    "salary_minor": Employee.salary_minor,
    "hire_date": Employee.hire_date,
}

SortColumn = Literal[
    "full_name",
    "email",
    "employee_code",
    "job_title",
    "department",
    "country_code",
    "salary_minor",
    "hire_date",
]
StatusFilter = Literal["active", "terminated", "all"]


@dataclass(frozen=True)
class EmployeeListQuery:
    page: int = 1
    page_size: int = 25
    sort: SortColumn = "full_name"
    order: Literal["asc", "desc"] = "asc"
    country: str | None = None
    department: str | None = None
    job_title: str | None = None
    q: str | None = None
    status: StatusFilter = "active"


def _filters(query: EmployeeListQuery) -> list[ColumnElement[bool]]:
    filters: list[ColumnElement[bool]] = []
    if query.status != "all":
        filters.append(Employee.status == query.status)
    if query.country:
        filters.append(Employee.country_code == query.country)
    if query.department:
        filters.append(Employee.department == query.department)
    if query.job_title:
        filters.append(Employee.job_title == query.job_title)
    if query.q:
        pattern = f"%{_escape_like(query.q.lower())}%"
        filters.append(
            or_(
                func.lower(Employee.full_name).like(pattern, escape="\\"),
                Employee.email.like(pattern, escape="\\"),
            )
        )
    return filters


def _escape_like(text: str) -> str:
    return text.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def list_page(session: Session, query: EmployeeListQuery) -> tuple[list[Employee], int]:
    filters = _filters(query)
    total = session.scalar(select(func.count()).select_from(Employee).where(*filters)) or 0

    column = SORTABLE_COLUMNS[query.sort]
    ordering = column.desc() if query.order == "desc" else column.asc()
    rows = session.scalars(
        select(Employee)
        .where(*filters)
        .order_by(ordering, Employee.id)
        .limit(query.page_size)
        .offset((query.page - 1) * query.page_size)
    )
    return list(rows), total


def save(session: Session, employee: Employee) -> Employee:
    session.commit()
    session.refresh(employee)
    return employee
