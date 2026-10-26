from decimal import Decimal

import pytest

from app.domain.stats import Bucket, CurrencyTotal, bucket_ranges, divide_half_up, to_inr_minor


@pytest.mark.parametrize(
    ("total", "count", "expected"),
    [(10, 4, 3), (10, 3, 3), (5, 2, 3), (7, 2, 4), (8, 2, 4)],
)
def test_divide_half_up_rounds_halves_away_from_zero(total: int, count: int, expected: int) -> None:
    assert divide_half_up(total, count) == expected


def test_bucket_ranges_split_the_span_into_equal_integer_ranges() -> None:
    assert bucket_ranges(minimum=100, maximum=400, buckets=3) == [
        Bucket(lower_minor=100, upper_minor=201),
        Bucket(lower_minor=201, upper_minor=301),
        Bucket(lower_minor=301, upper_minor=401),
    ]


def test_bucket_ranges_collapse_to_one_bucket_when_every_salary_is_equal() -> None:
    assert bucket_ranges(minimum=500, maximum=500, buckets=10) == [
        Bucket(lower_minor=500, upper_minor=501)
    ]


def test_bucket_ranges_never_produce_empty_width_buckets() -> None:
    ranges = bucket_ranges(minimum=1, maximum=3, buckets=10)

    assert [(b.lower_minor, b.upper_minor) for b in ranges] == [(1, 2), (2, 3), (3, 4)]


def test_bucket_index_matches_the_ranges() -> None:
    ranges = bucket_ranges(minimum=100, maximum=400, buckets=3)
    for salary in range(100, 401):
        index = Bucket.index_of(salary, minimum=100, maximum=400, buckets=len(ranges))
        assert ranges[index].lower_minor <= salary < ranges[index].upper_minor


def test_to_inr_minor_converts_each_currency_exactly_then_rounds_once() -> None:
    totals = [
        CurrencyTotal(amount_minor=6_000, minor_unit=2, inr_per_unit=Decimal("117.50")),
        CurrencyTotal(amount_minor=1_000, minor_unit=0, inr_per_unit=Decimal("0.58")),
        CurrencyTotal(amount_minor=1, minor_unit=2, inr_per_unit=Decimal("0.5")),
    ]

    assert to_inr_minor(totals) == 705_000 + 58_000 + 1
