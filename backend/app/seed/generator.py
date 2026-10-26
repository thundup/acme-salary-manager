import random
import re
import unicodedata
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any

from app.domain.employee import EmploymentType
from app.reference import COUNTRIES, CURRENCIES, JOB_TITLES_BY_DEPARTMENT

DATA_DIR = Path(__file__).parent / "data"
SEED_REFERENCE_DATE = date(2026, 10, 1)
EARLIEST_HIRE = date(2012, 1, 1)
EMAIL_DOMAIN = "acme-corp.com"

COUNTRY_WEIGHTS = {
    "IN": 35, "US": 20, "GB": 10, "DE": 7, "AE": 6, "SG": 5, "CA": 5, "NL": 4, "AU": 4, "JP": 4,
}  # fmt: skip
DEPARTMENT_WEIGHTS = {
    "Engineering": 40, "Sales": 10, "Data": 8, "Customer Success": 8, "Product": 7,
    "Infrastructure": 7, "QA": 6, "Design": 5, "People": 5, "Finance": 4,
}  # fmt: skip

# Market pay relative to the US, applied to a USD base salary per seniority level.
MARKET_FACTOR = {
    "US": 1.0, "CA": 0.8, "AU": 0.8, "GB": 0.75, "SG": 0.75, "DE": 0.7, "NL": 0.7,
    "AE": 0.65, "JP": 0.6, "IN": 0.3,
}  # fmt: skip
DEPARTMENT_FACTOR = {
    "Engineering": 1.0, "Data": 1.0, "Infrastructure": 1.0, "Product": 1.0, "Design": 0.9,
    "QA": 0.85, "Finance": 0.85, "Sales": 0.85, "People": 0.75, "Customer Success": 0.7,
}  # fmt: skip
BASE_USD_BY_LEVEL = {1: 75_000, 2: 100_000, 3: 140_000, 4: 180_000, 5: 220_000, 6: 250_000}

USD_PAID_SHARE = {"AE": 0.25, "SG": 0.10}
BONUS_SHARE = 0.4
EMPLOYMENT_WEIGHTS = {
    EmploymentType.FULL_TIME: 88,
    EmploymentType.CONTRACTOR: 7,
    EmploymentType.PART_TIME: 5,
}
PART_TIME_FACTOR = 0.6


def load_names(data_dir: Path = DATA_DIR) -> tuple[list[str], list[str]]:
    def read(name: str) -> list[str]:
        return [line.strip() for line in (data_dir / name).read_text().splitlines() if line.strip()]

    return read("first_names.txt"), read("last_names.txt")


def generate_employees(
    count: int, *, seed: int, first_names: list[str], last_names: list[str]
) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    used_emails: set[str] = set()
    return [
        _employee(number, rng, first_names, last_names, used_emails)
        for number in range(1, count + 1)
    ]


def _employee(
    number: int,
    rng: random.Random,
    first_names: list[str],
    last_names: list[str],
    used_emails: set[str],
) -> dict[str, Any]:
    first, last = rng.choice(first_names), rng.choice(last_names)
    country = _weighted(rng, COUNTRY_WEIGHTS)
    department = _weighted(rng, DEPARTMENT_WEIGHTS)
    titles = JOB_TITLES_BY_DEPARTMENT[department]
    level = _seniority(rng, len(titles))
    employment_type = _weighted(rng, EMPLOYMENT_WEIGHTS)
    currency = (
        "USD"
        if rng.random() < USD_PAID_SHARE.get(country, 0)
        else (COUNTRIES[country].currency_code)
    )
    salary = _salary_minor(rng, country, currency, department, level, employment_type)
    return {
        "employee_code": f"ACME-{number:06d}",
        "full_name": f"{first} {last}",
        "email": _unique_email(first, last, used_emails),
        "job_title": titles[level - 1],
        "department": department,
        "country_code": country,
        "currency_code": currency,
        "salary_minor": salary,
        "bonus_minor": _bonus_minor(rng, salary, currency) if rng.random() < BONUS_SHARE else None,
        "employment_type": employment_type.value,
        "hire_date": _hire_date(rng),
    }


def _weighted[T](rng: random.Random, weights: dict[T, int]) -> T:
    return rng.choices(list(weights), weights=list(weights.values()))[0]


def _seniority(rng: random.Random, levels: int) -> int:
    """Pyramid: each level up is roughly half as common as the one below."""
    return rng.choices(range(1, levels + 1), weights=[2 ** (levels - i) for i in range(levels)])[0]


def _salary_minor(
    rng: random.Random,
    country: str,
    currency: str,
    department: str,
    level: int,
    employment_type: EmploymentType,
) -> int:
    usd = BASE_USD_BY_LEVEL[level] * MARKET_FACTOR[country] * DEPARTMENT_FACTOR[department]
    usd *= rng.lognormvariate(0, 0.12)
    if employment_type is EmploymentType.PART_TIME:
        usd *= PART_TIME_FACTOR
    info = CURRENCIES[currency]
    local = Decimal(usd) * CURRENCIES["USD"].inr_per_unit / info.inr_per_unit
    step = 10_000 if info.minor_unit == 0 else 1_000
    major = max(step, round(local / step) * step)
    return int(major * 10**info.minor_unit)


def _bonus_minor(rng: random.Random, salary_minor: int, currency: str) -> int:
    step = int(10 ** (CURRENCIES[currency].minor_unit + 2))
    return int(round(salary_minor * rng.uniform(0.05, 0.2) / step) * step)


def _hire_date(rng: random.Random) -> date:
    span = (SEED_REFERENCE_DATE - EARLIEST_HIRE).days
    # Skew towards recent hires: a growing company hires more each year.
    return SEED_REFERENCE_DATE - timedelta(days=int(span * rng.random() ** 1.8))


def _slug(name: str) -> str:
    ascii_name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z]", "", ascii_name.lower())


def _unique_email(first: str, last: str, used: set[str]) -> str:
    local = f"{_slug(first)}.{_slug(last)}"
    candidate, suffix = local, 1
    while candidate in used:
        suffix += 1
        candidate = f"{local}{suffix}"
    used.add(candidate)
    return f"{candidate}@{EMAIL_DOMAIN}"
