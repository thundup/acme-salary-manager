from datetime import date

from sqlalchemy.orm import Session

from app.domain.employee import employee_rule_violations
from app.models import Employee
from app.repositories import employees as repo
from app.schemas import EmployeeCreate
from app.services.errors import DuplicateEmployee, RuleViolation


def create_employee(session: Session, data: EmployeeCreate, today: date) -> Employee:
    violations = employee_rule_violations(
        department=data.department,
        job_title=data.job_title,
        country_code=data.country_code,
        currency_code=data.currency_code,
        hire_date=data.hire_date,
        today=today,
    )
    if violations:
        raise RuleViolation(violations)
    if repo.code_taken(session, data.employee_code):
        raise DuplicateEmployee("employee_code")
    if repo.email_taken(session, data.email):
        raise DuplicateEmployee("email")
    return repo.add(session, Employee(**data.model_dump()))
