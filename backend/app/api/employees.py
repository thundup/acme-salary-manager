from datetime import date
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_today
from app.db import get_session
from app.models import Employee, utc_now
from app.repositories.employees import EmployeeListQuery, SortColumn, StatusFilter
from app.schemas import EmployeeCreate, EmployeeOut, EmployeePage, EmployeeUpdate
from app.services import employees as service

router = APIRouter(prefix="/employees", tags=["employees"])

SessionDep = Annotated[Session, Depends(get_session)]
TodayDep = Annotated[date, Depends(get_today)]


@router.get("", response_model=EmployeePage)
def list_employees(
    session: SessionDep,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 25,
    sort: SortColumn = "full_name",
    order: Literal["asc", "desc"] = "asc",
    country: str | None = None,
    department: str | None = None,
    job_title: str | None = None,
    q: Annotated[str | None, Query(max_length=100)] = None,
    status: StatusFilter = "active",
) -> EmployeePage:
    query = EmployeeListQuery(
        page=page,
        page_size=page_size,
        sort=sort,
        order=order,
        country=country,
        department=department,
        job_title=job_title,
        q=q,
        status=status,
    )
    items, total = service.list_employees(session, query)
    return EmployeePage(
        items=[EmployeeOut.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{employee_id}", response_model=EmployeeOut)
def get_employee(employee_id: int, session: SessionDep) -> Employee:
    return service.get_employee(session, employee_id)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=EmployeeOut)
def create_employee(data: EmployeeCreate, session: SessionDep, today: TodayDep) -> Employee:
    return service.create_employee(session, data, today)


@router.patch("/{employee_id}", response_model=EmployeeOut)
def update_employee(
    employee_id: int, patch: EmployeeUpdate, session: SessionDep, today: TodayDep
) -> Employee:
    return service.update_employee(session, employee_id, patch, today)


@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_employee(employee_id: int, session: SessionDep) -> Response:
    service.terminate_employee(session, employee_id, utc_now())
    return Response(status_code=status.HTTP_204_NO_CONTENT)
