from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from sqlalchemy import ColumnElement, func, or_, select
from sqlalchemy.orm import InstrumentedAttribute, Session

from app.domain.employee import EmployeeStatus
from app.models import Currency, Employee

GroupKey = tuple[str, ...]


@dataclass(frozen=True)
class GroupRow:
    headcount: int
    min_minor: int
    max_minor: int
    total_minor: int


@dataclass(frozen=True)
class CurrencySums:
    currency_code: str
    minor_unit: int
    inr_per_unit: Decimal
    headcount: int
    salary_minor: int
    bonus_minor: int


def _active() -> ColumnElement[bool]:
    return Employee.status == EmployeeStatus.ACTIVE


def group_stats(
    session: Session,
    group_by: list[InstrumentedAttribute[str]],
    filters: list[ColumnElement[bool]],
) -> dict[GroupKey, GroupRow]:
    rows = session.execute(
        select(
            *group_by,
            func.count(),
            func.min(Employee.salary_minor),
            func.max(Employee.salary_minor),
            func.sum(Employee.salary_minor),
        )
        .where(_active(), *filters)
        .group_by(*group_by)
    )
    keys = len(group_by)
    return {
        tuple(str(value) for value in row[:keys]): GroupRow(
            headcount=int(row[keys]),
            min_minor=int(row[keys + 1]),
            max_minor=int(row[keys + 2]),
            total_minor=int(row[keys + 3]),
        )
        for row in rows
    }


def salary_range(session: Session, filters: list[ColumnElement[bool]]) -> tuple[int, int] | None:
    low, high = session.execute(
        select(func.min(Employee.salary_minor), func.max(Employee.salary_minor)).where(
            _active(), *filters
        )
    ).one()
    return None if low is None else (low, high)


def group_medians(
    session: Session,
    group_by: list[InstrumentedAttribute[str]],
    filters: list[ColumnElement[bool]],
) -> dict[GroupKey, tuple[int, int]]:
    """Sum and count of the one or two middle salaries per group (portable median)."""
    ranked = (
        select(
            *group_by,
            Employee.salary_minor,
            func.row_number()
            .over(partition_by=group_by, order_by=Employee.salary_minor)
            .label("position"),
            func.count().over(partition_by=group_by).label("size"),
        )
        .where(_active(), *filters)
        .subquery()
    )
    keys = [ranked.c[column.key] for column in group_by]
    middle = or_(
        ranked.c.position == (ranked.c.size + 1) // 2,
        ranked.c.position == (ranked.c.size + 2) // 2,
    )
    rows = session.execute(
        select(*keys, func.sum(ranked.c.salary_minor), func.count()).where(middle).group_by(*keys)
    )
    return {tuple(row[: len(keys)]): (row[-2], row[-1]) for row in rows}


def bucket_counts(
    session: Session,
    filters: list[ColumnElement[bool]],
    *,
    minimum: int,
    maximum: int,
    buckets: int,
) -> dict[int, int]:
    index = ((Employee.salary_minor - minimum) * buckets // (maximum - minimum + 1)).label("index")
    rows = session.execute(select(index, func.count()).where(_active(), *filters).group_by(index))
    return {bucket: count for bucket, count in rows}


def sums_by_currency(session: Session) -> list[CurrencySums]:
    rows = session.execute(
        select(
            Currency.code,
            Currency.minor_unit,
            Currency.inr_per_unit,
            func.count(),
            func.sum(Employee.salary_minor),
            func.coalesce(func.sum(Employee.bonus_minor), 0),
        )
        .join(Currency, Currency.code == Employee.currency_code)
        .where(_active())
        .group_by(Currency.code, Currency.minor_unit, Currency.inr_per_unit)
    )
    return [
        CurrencySums(
            currency_code=code,
            minor_unit=minor_unit,
            inr_per_unit=rate,
            headcount=headcount,
            salary_minor=salary,
            bonus_minor=bonus or 0,
        )
        for code, minor_unit, rate, headcount, salary, bonus in rows
    ]


def rates_as_of(session: Session) -> date | None:
    return session.scalar(select(func.max(Currency.rates_as_of)))
