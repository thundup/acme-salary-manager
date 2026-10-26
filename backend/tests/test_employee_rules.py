from datetime import date

from app.domain.employee import employee_rule_violations

TODAY = date(2026, 10, 26)

VALID = {
    "department": "Engineering",
    "job_title": "Senior Software Engineer",
    "country_code": "IN",
    "currency_code": "INR",
    "hire_date": date(2024, 1, 15),
}


def violations(**overrides: object) -> dict[str, str]:
    return employee_rule_violations(**{**VALID, **overrides}, today=TODAY)  # type: ignore[arg-type]


def test_a_consistent_employee_has_no_violations() -> None:
    assert violations() == {}


def test_unknown_department_is_rejected() -> None:
    assert violations(department="Astrology") == {"department": "Unknown department 'Astrology'"}


def test_job_title_must_belong_to_its_department() -> None:
    assert violations(department="Finance", job_title="Senior Software Engineer") == {
        "job_title": "'Senior Software Engineer' is not a job title in Finance"
    }


def test_country_must_be_one_acme_operates_in() -> None:
    assert violations(country_code="FR") == {"country_code": "ACME has no employees in 'FR'"}


def test_currency_must_have_a_known_exchange_rate() -> None:
    assert violations(currency_code="CHF") == {"currency_code": "Unsupported currency 'CHF'"}


def test_pay_currency_may_differ_from_the_country_currency() -> None:
    assert violations(country_code="AE", currency_code="USD") == {}


def test_hire_date_cannot_be_in_the_future() -> None:
    assert violations(hire_date=date(2026, 10, 27)) == {
        "hire_date": "Hire date cannot be in the future"
    }


def test_hire_date_today_is_allowed() -> None:
    assert violations(hire_date=TODAY) == {}


def test_all_violations_are_reported_together() -> None:
    result = violations(country_code="FR", currency_code="CHF", hire_date=date(2030, 1, 1))

    assert set(result) == {"country_code", "currency_code", "hire_date"}
