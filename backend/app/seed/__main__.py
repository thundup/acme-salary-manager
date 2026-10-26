import argparse
import time

from app.db import SessionFactory
from app.seed.generator import generate_employees, load_names
from app.seed.loader import seed_employees


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed ACME employees deterministically.")
    parser.add_argument("--count", type=int, default=10_000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--reset", action="store_true", help="delete all employees first")
    args = parser.parse_args()

    started = time.perf_counter()
    first_names, last_names = load_names()
    employees = generate_employees(
        args.count, seed=args.seed, first_names=first_names, last_names=last_names
    )
    generated = time.perf_counter()
    with SessionFactory() as session:
        inserted = seed_employees(session, employees, reset=args.reset)
    finished = time.perf_counter()

    print(
        f"Inserted {inserted} of {len(employees)} employees "
        f"(generate {generated - started:.2f}s, insert {finished - generated:.2f}s, "
        f"total {finished - started:.2f}s)"
    )


if __name__ == "__main__":
    main()
