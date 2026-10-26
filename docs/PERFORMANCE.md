# Performance

Numbers below are **measured**, not estimated. Machine: Apple M3 Pro, Python 3.12.15,
SQLite 3.53.1 (bundled with Python), SQLite file on local SSD.

## Targets (from REQUIREMENTS.md)

| Operation | Target | Measured |
|---|---|---|
| Seed 10,000 employees | < 5 s | **0.20 s** (generate 0.06 s + insert 0.13 s) |
| `GET /api/employees` (any page / filter / sort) | < 100 ms | _Phase 6_ |
| `GET /api/insights/*` | < 300 ms | _Phase 6_ |

## Seed (Phase 4)

`make seed` → `python -m app.seed` (10,000 employees, `--seed 42`). Five runs each on a fresh,
migrated database. Results were identical within ±0.01 s:

| Scenario | Inserted | Total |
|---|---|---|
| First run on an empty DB | 10,000 | 0.19–0.20 s |
| Re-run (idempotent: `ON CONFLICT DO NOTHING`) | 0 | 0.18–0.19 s |
| `--reset` (delete all, re-insert) | 10,000 | 0.20 s |

**Why it is fast:** rows are generated as plain dicts with no ORM objects, then inserted with
one Core `INSERT … ON CONFLICT DO NOTHING` `executemany` per 1,000-row chunk, inside a single
transaction.

**Measured alternatives, for comparison (same 10k rows):**

| Approach | Time for 10k |
|---|---|
| ORM `session.add()` + `commit()` per row | ~4.2 s (measured 0.84 s for 2,000) |
| ORM `add_all()` + one commit | ~0.28 s |
| **Core bulk insert, chunked (chosen)** | **0.13 s** |

Committing per row is about 30× slower than the chosen approach, because every commit is a disk sync.
`add_all` is acceptable, but it builds 10k ORM objects for no benefit and can't express
`ON CONFLICT DO NOTHING`, which is what makes re-running safe.

**Determinism:** a fixed `random.Random(seed)` and a fixed reference date (2026-10-01) for hire
dates, so the output never depends on the day the seed runs. Covered by tests.

## Method

- Timings: `time.perf_counter()` inside the process, so interpreter start-up is excluded.
- API timings (Phase 6): median of N runs, warm cache, measured over HTTP.
- Index changes (Phase 6): `EXPLAIN QUERY PLAN` before/after, alongside timings.

## Index changes

_Phase 6: a before/after table per index, with the query it serves._
