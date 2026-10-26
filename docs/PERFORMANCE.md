# Performance

> Stub. This page will be filled in with **measured** numbers in Phases 4 and 6. Nothing below is a claim yet.

## Targets (from REQUIREMENTS.md)

| Operation | Target | Measured |
|---|---|---|
| Seed 10,000 employees | < 5 s | _Phase 4_ |
| `GET /api/employees` (any page / filter / sort) | < 100 ms | _Phase 6_ |
| `GET /api/insights/*` | < 300 ms | _Phase 6_ |

## Method

- Machine, Python / SQLite versions, and dataset (seeded 10k) will be recorded here.
- Timings: median of N runs, warm cache, measured at the service layer and over HTTP.
- Index changes: `EXPLAIN QUERY PLAN` before/after, alongside timings.

## Index changes

_Phase 6: before/after table per index, with the query it serves._
