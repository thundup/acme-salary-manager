from dataclasses import dataclass
from datetime import date
from typing import Literal

from sqlalchemy import ColumnElement
from sqlalchemy.orm import Session

from app.domain.stats import (
    CurrencyTotal,
    bucket_ranges,
    divide_half_up,
    effective_bucket_count,
    to_inr_minor,
)
from app.models import Employee
from app.reference import COUNTRIES, CURRENCIES, REPORTING_CURRENCY
from app.repositories import insights as repo
from app.services.errors import CountryNotFound, RuleViolation

BreakdownField = Literal["job_title", "department"]


@dataclass(frozen=True)
class CountryStats:
    country_code: str
    country_name: str
    currency_code: str
    headcount: int
    min_minor: int
    max_minor: int
    average_minor: int
    median_minor: int


@dataclass(frozen=True)
class GroupStats:
    key: str
    headcount: int
    min_minor: int
    max_minor: int
    average_minor: int


@dataclass(frozen=True)
class BucketCount:
    lower_minor: int
    upper_minor: int
    count: int


@dataclass(frozen=True)
class Distribution:
    country_code: str
    currency_code: str
    buckets: list[BucketCount]


@dataclass(frozen=True)
class OrgSummary:
    headcount: int
    currency_code: str
    total_salary_minor: int
    total_bonus_minor: int
    average_salary_minor: int
    rates_as_of: date | None


def country_stats(session: Session) -> list[CountryStats]:
    group_by = [Employee.country_code, Employee.currency_code]
    groups = repo.group_stats(session, group_by, [])
    medians = repo.group_medians(session, group_by, [])
    return [
        CountryStats(
            country_code=country,
            country_name=COUNTRIES[country].name,
            currency_code=currency,
            headcount=row.headcount,
            min_minor=row.min_minor,
            max_minor=row.max_minor,
            average_minor=divide_half_up(row.total_minor, row.headcount),
            median_minor=divide_half_up(*medians[(country, currency)]),
        )
        for (country, currency), row in sorted(groups.items())
    ]


def breakdown(
    session: Session, *, country: str, currency: str | None, by: BreakdownField
) -> list[GroupStats]:
    filters = _country_filters(country, currency)
    column = Employee.job_title if by == "job_title" else Employee.department
    groups = repo.group_stats(session, [column], filters)
    stats = [
        GroupStats(
            key=key,
            headcount=row.headcount,
            min_minor=row.min_minor,
            max_minor=row.max_minor,
            average_minor=divide_half_up(row.total_minor, row.headcount),
        )
        for (key,), row in groups.items()
    ]
    return sorted(stats, key=lambda g: (-g.average_minor, g.key))


def distribution(
    session: Session, *, country: str, currency: str | None, buckets: int
) -> Distribution:
    filters = _country_filters(country, currency)
    pay_currency = currency or COUNTRIES[country].currency_code
    salary_range = repo.salary_range(session, filters)
    if salary_range is None:
        return Distribution(country, pay_currency, [])

    low, high = salary_range
    count = effective_bucket_count(low, high, buckets)
    counts = repo.bucket_counts(session, filters, minimum=low, maximum=high, buckets=count)
    ranges = bucket_ranges(minimum=low, maximum=high, buckets=count)
    return Distribution(
        country,
        pay_currency,
        [BucketCount(r.lower_minor, r.upper_minor, counts.get(i, 0)) for i, r in enumerate(ranges)],
    )


def org_summary(session: Session) -> OrgSummary:
    sums = repo.sums_by_currency(session)
    headcount = sum(s.headcount for s in sums)
    total_salary = to_inr_minor(
        CurrencyTotal(s.salary_minor, s.minor_unit, s.inr_per_unit) for s in sums
    )
    total_bonus = to_inr_minor(
        CurrencyTotal(s.bonus_minor, s.minor_unit, s.inr_per_unit) for s in sums
    )
    return OrgSummary(
        headcount=headcount,
        currency_code=REPORTING_CURRENCY,
        total_salary_minor=total_salary,
        total_bonus_minor=total_bonus,
        average_salary_minor=divide_half_up(total_salary, headcount) if headcount else 0,
        rates_as_of=repo.rates_as_of(session),
    )


def _country_filters(country: str, currency: str | None) -> list[ColumnElement[bool]]:
    if country not in COUNTRIES:
        raise CountryNotFound()
    if currency is not None and currency not in CURRENCIES:
        raise RuleViolation({"currency": f"Unsupported currency '{currency}'"})
    pay_currency = currency or COUNTRIES[country].currency_code
    return [Employee.country_code == country, Employee.currency_code == pay_currency]
