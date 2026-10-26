# Performance

Numbers below are **measured**, not estimated. Machine: Apple M3 Pro, Python 3.12.15,
SQLite 3.53.1 (bundled with Python) on local SSD, and PostgreSQL 16.15 (local Homebrew).
Dataset: the 10,000 seeded employees.

## Targets (from REQUIREMENTS.md)

| Operation | Target | Measured |
|---|---|---|
| Seed 10,000 employees | < 5 s | **0.20 s** (generate 0.06 s + insert 0.13 s) |
| `GET /api/employees` (any page / filter / sort) | < 100 ms | **≤ 4 ms SQLite, ≤ 11 ms Postgres** (median) |
| `GET /api/insights/*` | < 300 ms | **≤ 15 ms SQLite, ≤ 8 ms Postgres** (median) |

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
- API timings: `uv run python -m app.bench` sends each request through the full FastAPI
  stack in-process (routing, validation, SQL, serialization; no network). One warm-up request,
  then the median and p95 of 30 runs.
- Query plans: `EXPLAIN QUERY PLAN` (SQLite) and `EXPLAIN ANALYZE` (Postgres), before and after.

## API timings and indexes (Phase 6)

Before Phase 6 the only indexes were the unique ones on `email` and `employee_code`. Every
endpoint was already well inside its target at 10k rows, so indexes are justified by **query
plans and growth**, not by a target being missed. Each index serves a query the app actually runs:

| Index | Serves |
|---|---|
| `ix_employees_status_full_name (status, full_name, id)` | Default list order (`WHERE status='active' ORDER BY full_name, id`), so pages are read in index order instead of sorting every row |
| `ix_employees_status_market_salary (status, country_code, currency_code, salary_minor)` | Every insight: filter active + country + currency, order / min / max by salary (median window, distribution, breakdown) |

**Query plans, before → after:**

| Query | Before | After |
|---|---|---|
| List page 300 | SQLite: `SCAN` + temp B-tree sort. PG: seq scan + sort of 10k rows, **35.3 ms** | Covering index scan, no sort. PG: index-only scan, **2.7 ms** |
| Median window per country + currency | SQLite: `SCAN` + temp B-tree sort. PG: seq scan + sort | Covering index read in partition order, no sort step |
| Breakdown IN / INR | Full scan | Index range on (status, country, currency) |

**Endpoint medians (ms), before → after:**

| Request | SQLite before | SQLite after | Postgres before | Postgres after |
|---|---|---|---|---|
| list, default page | 2.7 | **1.5** | 5.0 | **2.5** |
| list, page 300 | 10.1 | **1.6** | 29.9 | **4.1** |
| list, country + sort by salary | 2.6 | 3.8 ⚠️ | 6.2 | **2.8** |
| list, department + title | 2.6 | **2.1** | 5.8 | **3.6** |
| list, search 'sharma' | 4.7 | **4.3** | 14.6 | **11.2** |
| insights, all countries | 20.7 | **14.9** | 19.8 | **8.1** |
| insights, IN by job title | 2.6 | 2.7 | 4.4 | 4.2 |
| insights, IN distribution | 2.7 | **1.8** | 5.3 | 5.6 |
| insights, org summary | 5.0 | 5.0 | 10.2 | **6.3** |

**What didn't go to plan, and the fix:** the first run after adding the indexes made several
SQLite queries *slower* (search 4.7 → 6.1 ms, department + title 2.6 → 3.6 ms). With no table
statistics, SQLite picked the low-selectivity `status` prefix too eagerly. Running `ANALYZE`
fixed the plans (numbers above are after `ANALYZE`), so the seed now runs `ANALYZE` after
every load.

**Remaining regression, accepted:** `country + sort by salary` on SQLite is 1.2 ms slower. It
sorts by salary across *all* pay currencies in a country, which the market index can't fully
order. It is 25× under budget, and the more meaningful query (one country *and* currency) is
covered.

**Not indexed, on purpose:** search uses `LIKE '%q%'`, which no B-tree can serve. At 10k
rows a scan is 4–11 ms. Past ~1M rows the next step is SQLite FTS5 or Postgres `pg_trgm`.
