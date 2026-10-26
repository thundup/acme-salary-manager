# Trade-offs and what I'd do next

## Trade-offs I made on purpose

| Decision | Cost I accepted | Why |
|---|---|---|
| No authentication (a single implied HR user) | The live demo is open | Real auth needs an identity provider and a role model the brief doesn't define. Faking it would add code without adding safety. The demo holds synthetic data only |
| Fixed, dated exchange rates | Org-wide INR figures go stale | Deterministic, testable, no external dependency. Labelled "≈" with the rate date in the API and UI |
| Stats split by country **and** pay currency | The UAE appears twice (AED and USD) | Averaging two currencies together would be silently wrong |
| Soft delete only, no restore | A rehire needs a new record or a DB fix | Keeps leavers' records, which is what HR expects. Restore wasn't asked for |
| Offset pagination | Rows can shift between pages during edits | HR wants page numbers and a total. At 10k rows the cost is negligible (see PERFORMANCE) |
| `LIKE '%q%'` search | Full scan per search | 4–11 ms at 10k rows. FTS / `pg_trgm` would be premature |
| Native `<select>`, no table or form library | Slightly more hand-written UI code | Fewer dependencies. Behavior is easy to test and accessible by default |
| Migrations run outside the serverless function | Someone must run `alembic upgrade` on schema changes | Running DDL on every cold start is slow and racy |
| Generated name lists combined at random | "Aarav Al Hashimi" in Japan | No names were provided. Realism of salaries mattered more than of names |

## What I'd do next, in order

1. **Salary history.** A `salary_change` table (amount, currency, effective date, reason, who).
   It is the most valuable missing feature for HR and also gives an audit trail.
2. **Bulk import/export (CSV / Excel).** This persona lives in Excel today. Import needs a
   preview step, per-row validation errors (reusing the domain rules), and a duplicate policy.
3. **Authentication and roles.** SSO plus roles (HR admin vs. read-only finance), and
   country-scoped access for regional HR.
4. **Managed FX rates.** Rates as data with an effective date, refreshed from a provider, and
   historical conversion for year-over-year comparisons.
5. **More insights.** Pay bands per role and level, gender-neutral pay-gap analysis (needs data
   we don't hold today), and compa-ratio against bands.
6. **Operational polish.** Rate limiting, structured logging and request IDs, error tracking,
   an end-to-end test (Playwright) for the add → edit → remove flow, and Postgres FTS when
   search needs it.
