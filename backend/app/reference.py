from dataclasses import dataclass
from datetime import date
from decimal import Decimal

REPORTING_CURRENCY = "INR"
RATES_AS_OF = date(2026, 10, 1)


@dataclass(frozen=True)
class CurrencyInfo:
    code: str
    minor_unit: int
    inr_per_unit: Decimal


@dataclass(frozen=True)
class CountryInfo:
    code: str
    name: str
    currency_code: str


CURRENCIES: dict[str, CurrencyInfo] = {
    c.code: c
    for c in (
        CurrencyInfo("INR", 2, Decimal("1")),
        CurrencyInfo("USD", 2, Decimal("88.00")),
        CurrencyInfo("GBP", 2, Decimal("117.50")),
        CurrencyInfo("EUR", 2, Decimal("102.00")),
        CurrencyInfo("AED", 2, Decimal("23.96")),
        CurrencyInfo("SGD", 2, Decimal("68.00")),
        CurrencyInfo("CAD", 2, Decimal("63.00")),
        CurrencyInfo("AUD", 2, Decimal("57.50")),
        CurrencyInfo("JPY", 0, Decimal("0.58")),
    )
}

COUNTRIES: dict[str, CountryInfo] = {
    c.code: c
    for c in (
        CountryInfo("IN", "India", "INR"),
        CountryInfo("US", "United States", "USD"),
        CountryInfo("GB", "United Kingdom", "GBP"),
        CountryInfo("DE", "Germany", "EUR"),
        CountryInfo("NL", "Netherlands", "EUR"),
        CountryInfo("AE", "United Arab Emirates", "AED"),
        CountryInfo("SG", "Singapore", "SGD"),
        CountryInfo("CA", "Canada", "CAD"),
        CountryInfo("AU", "Australia", "AUD"),
        CountryInfo("JP", "Japan", "JPY"),
    )
}

JOB_TITLES_BY_DEPARTMENT: dict[str, tuple[str, ...]] = {
    "Engineering": (
        "Software Engineer I",
        "Software Engineer II",
        "Senior Software Engineer",
        "Staff Software Engineer",
        "Principal Engineer",
        "Engineering Manager",
    ),
    "Product": (
        "Associate Product Manager",
        "Product Manager",
        "Senior Product Manager",
        "Director of Product",
    ),
    "Design": ("Product Designer", "Senior Product Designer", "UX Researcher"),
    "Data": ("Data Analyst", "Data Engineer", "Data Scientist", "Machine Learning Engineer"),
    "Infrastructure": ("DevOps Engineer", "Site Reliability Engineer", "Security Engineer"),
    "QA": ("QA Engineer", "Software Development Engineer in Test"),
    "People": ("Talent Acquisition Specialist", "HR Business Partner", "People Operations Manager"),
    "Finance": ("Accountant", "Financial Analyst", "Finance Manager"),
    "Sales": ("Sales Development Representative", "Account Executive", "Sales Manager"),
    "Customer Success": ("Support Engineer", "Customer Success Manager"),
}
