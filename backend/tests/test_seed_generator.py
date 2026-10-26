from collections import Counter
from datetime import date

from app.domain.employee import employee_rule_violations
from app.seed.generator import SEED_REFERENCE_DATE, generate_employees, load_names

FIRST, LAST = load_names()


def test_same_seed_produces_identical_employees() -> None:
    assert generate_employees(200, seed=7, first_names=FIRST, last_names=LAST) == (
        generate_employees(200, seed=7, first_names=FIRST, last_names=LAST)
    )


def test_different_seeds_produce_different_employees() -> None:
    a = generate_employees(50, seed=1, first_names=FIRST, last_names=LAST)
    b = generate_employees(50, seed=2, first_names=FIRST, last_names=LAST)

    assert a != b


def test_codes_and_emails_are_unique() -> None:
    employees = generate_employees(10_000, seed=42, first_names=FIRST, last_names=LAST)

    assert len({e["employee_code"] for e in employees}) == 10_000
    assert len({e["email"] for e in employees}) == 10_000
    assert employees[0]["employee_code"] == "ACME-000001"


def test_every_generated_employee_passes_the_domain_rules() -> None:
    employees = generate_employees(2_000, seed=42, first_names=FIRST, last_names=LAST)

    for e in employees:
        assert e["salary_minor"] > 0
        assert e["bonus_minor"] is None or e["bonus_minor"] >= 0
        assert e["hire_date"] <= SEED_REFERENCE_DATE
        assert (
            employee_rule_violations(
                department=e["department"],
                job_title=e["job_title"],
                country_code=e["country_code"],
                currency_code=e["currency_code"],
                hire_date=e["hire_date"],
                today=SEED_REFERENCE_DATE,
            )
            == {}
        )


def test_distributions_look_like_a_tech_company() -> None:
    employees = generate_employees(10_000, seed=42, first_names=FIRST, last_names=LAST)
    countries = Counter(e["country_code"] for e in employees)
    departments = Counter(e["department"] for e in employees)

    assert countries.most_common(1)[0][0] == "IN"
    assert departments.most_common(1)[0][0] == "Engineering"
    assert len(countries) == 10
    assert 0.3 < sum(e["bonus_minor"] is not None for e in employees) / 10_000 < 0.5
    assert any(e["country_code"] == "AE" and e["currency_code"] == "USD" for e in employees)


def test_seniority_pays_more_than_entry_level_in_the_same_market() -> None:
    employees = generate_employees(10_000, seed=42, first_names=FIRST, last_names=LAST)

    def median_salary(title: str) -> int:
        salaries = sorted(
            e["salary_minor"]
            for e in employees
            if e["job_title"] == title and e["currency_code"] == "INR"
        )
        return int(salaries[len(salaries) // 2])

    assert median_salary("Staff Software Engineer") > median_salary("Software Engineer I")


def test_hire_dates_do_not_depend_on_the_day_the_seed_runs() -> None:
    employees = generate_employees(100, seed=42, first_names=FIRST, last_names=LAST)

    assert all(date(2012, 1, 1) <= e["hire_date"] <= SEED_REFERENCE_DATE for e in employees)
