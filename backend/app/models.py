from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.domain.employee import EmployeeStatus


def utc_now() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


class Currency(Base):
    __tablename__ = "currencies"

    code: Mapped[str] = mapped_column(String(3), primary_key=True)
    minor_unit: Mapped[int]
    inr_per_unit: Mapped[Decimal] = mapped_column(Numeric(18, 6))
    rates_as_of: Mapped[date] = mapped_column(Date)


class Employee(Base):
    __tablename__ = "employees"
    __table_args__ = (
        CheckConstraint("salary_minor > 0", name="ck_employees_salary_positive"),
        CheckConstraint(
            "bonus_minor IS NULL OR bonus_minor >= 0", name="ck_employees_bonus_non_negative"
        ),
        Index("ix_employees_status_full_name", "status", "full_name", "id"),
        Index(
            "ix_employees_status_market_salary",
            "status",
            "country_code",
            "currency_code",
            "salary_minor",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    employee_code: Mapped[str] = mapped_column(String(12), unique=True)
    full_name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(254), unique=True)
    job_title: Mapped[str] = mapped_column(String(80))
    department: Mapped[str] = mapped_column(String(40))
    country_code: Mapped[str] = mapped_column(String(2))
    currency_code: Mapped[str] = mapped_column(ForeignKey("currencies.code"))
    salary_minor: Mapped[int] = mapped_column(BigInteger)
    bonus_minor: Mapped[int | None] = mapped_column(BigInteger)
    employment_type: Mapped[str] = mapped_column(String(20))
    hire_date: Mapped[date] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(12), default=EmployeeStatus.ACTIVE)
    terminated_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, onupdate=utc_now)
