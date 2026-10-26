from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_today
from app.db import get_session
from app.models import Employee
from app.schemas import EmployeeCreate, EmployeeOut
from app.services import employees as service

router = APIRouter(prefix="/employees", tags=["employees"])

SessionDep = Annotated[Session, Depends(get_session)]
TodayDep = Annotated[date, Depends(get_today)]


@router.post("", status_code=status.HTTP_201_CREATED, response_model=EmployeeOut)
def create_employee(data: EmployeeCreate, session: SessionDep, today: TodayDep) -> Employee:
    return service.create_employee(session, data, today)
