from fastapi import APIRouter
from pydantic import BaseModel

from app.domain.employee import EmploymentType
from app.reference import COUNTRIES, CURRENCIES, JOB_TITLES_BY_DEPARTMENT, REPORTING_CURRENCY

router = APIRouter(tags=["reference"])


class CountryOut(BaseModel):
    code: str
    name: str
    currency_code: str


class CurrencyOut(BaseModel):
    code: str
    minor_unit: int


class DepartmentOut(BaseModel):
    name: str
    job_titles: list[str]


class ReferenceOut(BaseModel):
    countries: list[CountryOut]
    currencies: list[CurrencyOut]
    departments: list[DepartmentOut]
    employment_types: list[EmploymentType]
    reporting_currency: str


@router.get("/reference", response_model=ReferenceOut)
def reference() -> ReferenceOut:
    return ReferenceOut(
        countries=[
            CountryOut(code=c.code, name=c.name, currency_code=c.currency_code)
            for c in COUNTRIES.values()
        ],
        currencies=[CurrencyOut(code=c.code, minor_unit=c.minor_unit) for c in CURRENCIES.values()],
        departments=[
            DepartmentOut(name=name, job_titles=list(titles))
            for name, titles in JOB_TITLES_BY_DEPARTMENT.items()
        ],
        employment_types=list(EmploymentType),
        reporting_currency=REPORTING_CURRENCY,
    )
