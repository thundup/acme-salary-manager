from datetime import date

import pytest
from sqlalchemy.orm import Session

from app.services import insights
from app.services.errors import CountryNotFound, RuleViolation
from tests.factories import add_employee


@pytest.fixture
def org(session: Session) -> Session:
    """India pays INR 100/200/300/400, the UK GBP 1000/2000/3000, and the UAE pays one
    person in AED and one in USD. A terminated Indian employee must never be counted."""
    engineer = {"department": "Engineering", "job_title": "Software Engineer II"}
    product = {"department": "Product", "job_title": "Product Manager"}
    for salary, role in ((100, engineer), (200, product), (300, engineer), (400, product)):
        add_employee(session, salary_minor=salary, **role)
    add_employee(session, salary_minor=99_999, status="terminated")
    for salary in (1_000, 3_000, 2_000):
        add_employee(
            session,
            country_code="GB",
            currency_code="GBP",
            salary_minor=salary,
            bonus_minor=100 if salary == 1_000 else None,
        )
    add_employee(session, country_code="AE", currency_code="AED", salary_minor=500)
    add_employee(session, country_code="AE", currency_code="USD", salary_minor=700)
    return session


def test_country_stats_group_by_country_and_pay_currency(org: Session) -> None:
    stats = {(s.country_code, s.currency_code): s for s in insights.country_stats(org)}

    assert set(stats) == {("AE", "AED"), ("AE", "USD"), ("GB", "GBP"), ("IN", "INR")}
    india = stats[("IN", "INR")]
    assert (india.headcount, india.min_minor, india.max_minor) == (4, 100, 400)
    assert (india.average_minor, india.median_minor) == (250, 250)
    assert india.country_name == "India"


def test_median_of_an_odd_sized_group_is_the_middle_salary(org: Session) -> None:
    uk = next(s for s in insights.country_stats(org) if s.country_code == "GB")

    assert (uk.median_minor, uk.average_minor) == (2_000, 2_000)


def test_breakdown_by_job_title_is_sorted_by_average_descending(org: Session) -> None:
    groups = insights.breakdown(org, country="IN", currency=None, by="job_title")

    assert [(g.key, g.headcount, g.average_minor) for g in groups] == [
        ("Product Manager", 2, 300),
        ("Software Engineer II", 2, 200),
    ]


def test_breakdown_uses_the_requested_pay_currency(org: Session) -> None:
    local = insights.breakdown(org, country="AE", currency=None, by="department")
    usd = insights.breakdown(org, country="AE", currency="USD", by="department")

    assert [g.average_minor for g in local] == [500]
    assert [g.average_minor for g in usd] == [700]


def test_distribution_counts_salaries_in_equal_width_buckets(org: Session) -> None:
    result = insights.distribution(org, country="IN", currency=None, buckets=3)

    assert result.currency_code == "INR"
    assert [(b.lower_minor, b.upper_minor, b.count) for b in result.buckets] == [
        (100, 201, 2),
        (201, 301, 1),
        (301, 401, 1),
    ]


def test_distribution_of_a_country_without_employees_is_empty(org: Session) -> None:
    assert insights.distribution(org, country="JP", currency=None, buckets=5).buckets == []


def test_unknown_country_is_rejected(org: Session) -> None:
    with pytest.raises(CountryNotFound):
        insights.breakdown(org, country="FR", currency=None, by="job_title")


def test_unsupported_currency_is_rejected(org: Session) -> None:
    with pytest.raises(RuleViolation):
        insights.distribution(org, country="IN", currency="CHF", buckets=5)


def test_org_summary_converts_each_currency_to_inr(org: Session) -> None:
    summary = insights.org_summary(org)

    # INR 10.00 + GBP 60 x 117.50 + AED 5 x 23.96 + USD 7 x 88, in paise
    assert summary.total_salary_minor == 1_000 + 705_000 + 11_980 + 61_600
    assert summary.total_bonus_minor == 11_750
    assert summary.headcount == 9
    assert summary.average_salary_minor == 86_620
    assert summary.currency_code == "INR"
    assert summary.rates_as_of == date(2026, 10, 1)
