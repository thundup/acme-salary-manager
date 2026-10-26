from datetime import date, datetime
from typing import Annotated

from pydantic import AfterValidator, BaseModel, ConfigDict, EmailStr, Field, StringConstraints

from app.domain.employee import EmployeeStatus, EmploymentType

MAX_MINOR_AMOUNT = 10**13

EmployeeCode = Annotated[str, StringConstraints(pattern=r"^ACME-\d{6}$")]
FullName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)]
Email = Annotated[EmailStr, AfterValidator(str.lower)]
Label = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=80)]
CountryCode = Annotated[str, StringConstraints(pattern=r"^[A-Z]{2}$")]
CurrencyCode = Annotated[str, StringConstraints(pattern=r"^[A-Z]{3}$")]
Salary = Annotated[int, Field(gt=0, le=MAX_MINOR_AMOUNT)]
Bonus = Annotated[int, Field(ge=0, le=MAX_MINOR_AMOUNT)]


class EmployeeCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    employee_code: EmployeeCode
    full_name: FullName
    email: Email
    job_title: Label
    department: Label
    country_code: CountryCode
    currency_code: CurrencyCode
    salary_minor: Salary
    bonus_minor: Bonus | None = None
    employment_type: EmploymentType
    hire_date: date


class EmployeeUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    full_name: FullName | None = None
    email: Email | None = None
    job_title: Label | None = None
    department: Label | None = None
    country_code: CountryCode | None = None
    currency_code: CurrencyCode | None = None
    salary_minor: Salary | None = None
    bonus_minor: Bonus | None = None
    employment_type: EmploymentType | None = None
    hire_date: date | None = None


class EmployeeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    employee_code: str
    full_name: str
    email: str
    job_title: str
    department: str
    country_code: str
    currency_code: str
    salary_minor: int
    bonus_minor: int | None
    employment_type: EmploymentType
    hire_date: date
    status: EmployeeStatus
    terminated_at: datetime | None
    created_at: datetime
    updated_at: datetime


class EmployeePage(BaseModel):
    items: list[EmployeeOut]
    total: int
    page: int
    page_size: int


class Money(BaseModel):
    amount_minor: int
    currency: str


class CountryStatsOut(BaseModel):
    country_code: str
    country_name: str
    currency_code: str
    headcount: int
    min: Money
    max: Money
    average: Money
    median: Money


class GroupStatsOut(BaseModel):
    key: str
    headcount: int
    min: Money
    max: Money
    average: Money


class BucketOut(BaseModel):
    lower_minor: int
    upper_minor: int
    count: int


class DistributionOut(BaseModel):
    country_code: str
    currency_code: str
    buckets: list[BucketOut]


class OrgSummaryOut(BaseModel):
    headcount: int
    total_salary: Money
    total_bonus: Money
    average_salary: Money
    approximate: bool = True
    rates_as_of: date | None
