from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db import get_session
from app.schemas import (
    BucketOut,
    CountryStatsOut,
    DistributionOut,
    GroupStatsOut,
    Money,
    OrgSummaryOut,
)
from app.services import insights as service
from app.services.insights import BreakdownField

router = APIRouter(prefix="/insights", tags=["insights"])

SessionDep = Annotated[Session, Depends(get_session)]
CurrencyParam = Annotated[str | None, Query(pattern=r"^[A-Z]{3}$")]


@router.get("/countries", response_model=list[CountryStatsOut])
def country_stats(session: SessionDep) -> list[CountryStatsOut]:
    return [
        CountryStatsOut(
            country_code=s.country_code,
            country_name=s.country_name,
            currency_code=s.currency_code,
            headcount=s.headcount,
            min=Money(amount_minor=s.min_minor, currency=s.currency_code),
            max=Money(amount_minor=s.max_minor, currency=s.currency_code),
            average=Money(amount_minor=s.average_minor, currency=s.currency_code),
            median=Money(amount_minor=s.median_minor, currency=s.currency_code),
        )
        for s in service.country_stats(session)
    ]


@router.get("/countries/{country}/breakdown", response_model=list[GroupStatsOut])
def breakdown(
    country: str, by: BreakdownField, session: SessionDep, currency: CurrencyParam = None
) -> list[GroupStatsOut]:
    groups = service.breakdown(session, country=country, currency=currency, by=by)
    pay_currency = service.pay_currency(country, currency)
    return [
        GroupStatsOut(
            key=g.key,
            headcount=g.headcount,
            min=Money(amount_minor=g.min_minor, currency=pay_currency),
            max=Money(amount_minor=g.max_minor, currency=pay_currency),
            average=Money(amount_minor=g.average_minor, currency=pay_currency),
        )
        for g in groups
    ]


@router.get("/countries/{country}/distribution", response_model=DistributionOut)
def distribution(
    country: str,
    session: SessionDep,
    currency: CurrencyParam = None,
    buckets: Annotated[int, Query(ge=1, le=50)] = 10,
) -> DistributionOut:
    result = service.distribution(session, country=country, currency=currency, buckets=buckets)
    return DistributionOut(
        country_code=result.country_code,
        currency_code=result.currency_code,
        buckets=[
            BucketOut(lower_minor=b.lower_minor, upper_minor=b.upper_minor, count=b.count)
            for b in result.buckets
        ],
    )


@router.get("/summary", response_model=OrgSummaryOut)
def summary(session: SessionDep) -> OrgSummaryOut:
    s = service.org_summary(session)
    return OrgSummaryOut(
        headcount=s.headcount,
        total_salary=Money(amount_minor=s.total_salary_minor, currency=s.currency_code),
        total_bonus=Money(amount_minor=s.total_bonus_minor, currency=s.currency_code),
        average_salary=Money(amount_minor=s.average_salary_minor, currency=s.currency_code),
        rates_as_of=s.rates_as_of,
    )
