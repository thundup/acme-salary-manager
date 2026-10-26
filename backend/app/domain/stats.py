from collections.abc import Iterable
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from itertools import pairwise

INR_MINOR_UNIT = 2


def divide_half_up(total: int, count: int) -> int:
    return int((Decimal(total) / Decimal(count)).quantize(Decimal(1), rounding=ROUND_HALF_UP))


@dataclass(frozen=True)
class Bucket:
    lower_minor: int
    upper_minor: int

    @staticmethod
    def index_of(salary: int, *, minimum: int, maximum: int, buckets: int) -> int:
        return (salary - minimum) * buckets // (maximum - minimum + 1)


def effective_bucket_count(minimum: int, maximum: int, buckets: int) -> int:
    return min(buckets, maximum - minimum + 1)


def _ceil_div(numerator: int, denominator: int) -> int:
    return -(-numerator // denominator)


def bucket_ranges(*, minimum: int, maximum: int, buckets: int) -> list[Bucket]:
    span = maximum - minimum + 1
    count = effective_bucket_count(minimum, maximum, buckets)
    edges = [minimum + _ceil_div(i * span, count) for i in range(count + 1)]
    return [Bucket(lower, upper) for lower, upper in pairwise(edges)]


@dataclass(frozen=True)
class CurrencyTotal:
    amount_minor: int
    minor_unit: int
    inr_per_unit: Decimal


def to_inr_minor(totals: Iterable[CurrencyTotal]) -> int:
    inr = sum(
        (
            Decimal(t.amount_minor).scaleb(INR_MINOR_UNIT - t.minor_unit) * t.inr_per_unit
            for t in totals
        ),
        start=Decimal(0),
    )
    return int(inr.quantize(Decimal(1), rounding=ROUND_HALF_UP))
