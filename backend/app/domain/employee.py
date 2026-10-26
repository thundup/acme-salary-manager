from datetime import date
from enum import StrEnum

from app.reference import COUNTRIES, CURRENCIES, JOB_TITLES_BY_DEPARTMENT


class EmploymentType(StrEnum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACTOR = "contractor"


class EmployeeStatus(StrEnum):
    ACTIVE = "active"
    TERMINATED = "terminated"


def employee_rule_violations(
    *,
    department: str,
    job_title: str,
    country_code: str,
    currency_code: str,
    hire_date: date,
    today: date,
) -> dict[str, str]:
    violations: dict[str, str] = {}

    titles = JOB_TITLES_BY_DEPARTMENT.get(department)
    if titles is None:
        violations["department"] = f"Unknown department '{department}'"
    elif job_title not in titles:
        violations["job_title"] = f"'{job_title}' is not a job title in {department}"

    if country_code not in COUNTRIES:
        violations["country_code"] = f"ACME has no employees in '{country_code}'"

    if currency_code not in CURRENCIES:
        violations["currency_code"] = f"Unsupported currency '{currency_code}'"

    if hire_date > today:
        violations["hire_date"] = "Hire date cannot be in the future"

    return violations
