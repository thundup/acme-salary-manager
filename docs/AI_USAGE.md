# AI usage log

I used an AI coding assistant (Claude Code) as a pair programmer. This log records the key
prompts, what I accepted, and what I rejected or corrected, with reasons. It is updated every phase.

## How I worked with it

- One phase at a time, with a hard stop for my review after each phase.
- Tests first for behavior. The assistant writes a failing test, and I check it describes the
  behavior I actually want before any implementation.
- Every new dependency must be justified in writing before it is added.

## Phase 0: Requirements & design

**Prompt (summary):** "You are my pair programmer on an Incubyte take-home… Phase 0: draft
REQUIREMENTS, ARCHITECTURE (Mermaid diagrams, endpoint table, ADR-lite decisions on currency,
money, pagination/indexing, layering), a PERFORMANCE stub, and this log. Ask clarifying
questions, then stop."

**Proposed by the assistant:**
- Integer minor units plus a per-currency `minor_unit`, rather than `Decimal` columns.
- Per-country insights in native currency (exact), and only the org-wide summary converted to
  USD with static, dated rates (approximate, labelled).
- Median via window functions so the same SQL runs on SQLite and Postgres.
- Indexes deferred to Phase 6 and added only with measured before/after numbers.
- shadcn/ui + TanStack Table rather than MUI; a single Docker image serving API + SPA.

**Clarifying questions the assistant asked, and my answers:**
- Salary semantics → annual base salary, **plus an optional annual bonus** for some employees.
  (The draft had put bonuses out of scope; I brought them in.)
- Reporting currency → **INR**, not the USD the draft proposed. Employees keep their local pay
  currency. The assistant asked whether I meant "everyone paid in INR" or "INR as reporting
  currency" rather than guessing; it is the latter.
- Delete → **soft delete** (the draft assumed a hard delete). Added ADR-10.
- Departments / job titles → fixed catalogue modelled on a typical tech org.
- UI → **Tailwind**. The ADR keeps shadcn/ui components on top, since they are Tailwind-based
  and copied into the repo.
- Name lists → generated, since none were provided.
- Deployment target → deferred to Phase 6.

**Accepted as proposed:** integer minor units, native-currency per-country insights with only the
org-wide summary converted, window-function median, offset pagination, indexes deferred to
measured Phase 6 work, routers → services → repositories, single Docker image.

## Phase 1: Backend skeleton (+ frontend scaffold for CI)

**Prompt (summary):** "Project structure, config, DB session, Alembic, health endpoint,
lint/type/test tooling, CI for both apps."

**What the assistant did, and the corrections along the way:**
- Used `uv` to manage Python 3.12. The machine only had 3.9, and `uv` gives a lockfile and fast CI.
- Wrote the health test first (red), then the endpoint. It also added a test for the 503 path,
  because a health check that can't fail tells you nothing.
- Starlette now warns that `httpx` is deprecated for its `TestClient`. The assistant swapped in
  `httpx2` rather than suppressing the warning, and made pytest treat warnings as errors so
  this kind of drift fails loudly.
- The current Vite template ships with `oxlint`. The assistant replaced it with ESLint +
  Prettier, because the brief asks for those specifically.
- Alembic reads `DATABASE_URL` from the app's settings, so the app and migrations share one
  source of truth, with `render_as_batch=True` so SQLite `ALTER TABLE` works.

**Dependencies added and why:** `fastapi`, `uvicorn`, `sqlalchemy`, `pydantic-settings` (env
config), `alembic`; dev: `pytest`, `httpx2` (TestClient transport), `ruff`, `mypy`. Frontend dev:
ESLint, Prettier, Vitest, jsdom, Testing Library.

## Phase 2: Employee CRUD (test-first)

**Prompt (summary):** "Propose the final field list; list/get/create/update/delete with
pagination, sort, filters, search; validation and clear 4xx errors; test-first, commit red→green."

**How TDD was applied:** for each behavior (rules → model/migration → create → list/get →
update/delete), the tests were written and run red first, then the implementation. The brief
asks for both "commit red→green" and "never commit red", so each commit holds a green
test + implementation pair rather than a separate red commit.

**Decisions the assistant proposed and I accepted:**
- Domain rules (department → title, supported country/currency, hire date not in the future)
  are a pure function taking `today` as an argument. 9 tests, no DB, no HTTP.
- Shape validation lives in Pydantic and business rules in the service, with one error envelope
  `{error: {code, message, fields}}` for both, so the frontend can map errors to form fields.
- PATCH validates the *merged* record. Changing only `department` can make the existing
  `job_title` invalid, and that is caught.
- `employee_code` is immutable after creation. Re-deleting is an idempotent 204 that keeps the
  original `terminated_at`. Editing a terminated employee is a 409.
- A migration test (`alembic check`) fails if models and migrations drift apart.
- The exchange-rate set is frozen *inside the migration*, so a new rate set means a new
  migration. That is how the rates are versioned.

**Caught along the way:** the email validator rejects the reserved `.test` domain. The
assistant fixed the test data rather than loosening the validator. It also escaped `%` / `_`
in search so user input can't act as a SQL wildcard (with a test).

**Dependency added:** `email-validator`, which Pydantic's `EmailStr` needs. Writing our own
email regex would be worse.

## Phase 3: Salary insights

**Prompt (summary):** "Per-country min/max/avg/median and headcount, avg by job title within a
country, an org-wide summary in the reporting currency labelled approximate, and distribution
buckets, all computed in SQL. Unit-test with small hand-crafted datasets."

**Design change the assistant raised before coding:** a country can contain employees paid in
different currencies, and averaging them together is wrong. Stats are grouped by country + pay
currency instead (see ADR-2). I agreed.

**How the logic is split:**
- Pure helpers (`app/domain/stats.py`): half-up division, equal-width bucket edges (with a
  test that each salary's SQL bucket index lands inside its range), and exact INR
  conversion. 10 tests, no DB.
- SQL (`app/repositories/insights.py`): `GROUP BY` for min/max/avg/count, a window-function
  median that works on SQLite and Postgres, and bucket assignment with integer arithmetic. The
  assistant compiled the queries for both dialects to check that `//` becomes integer division
  in each.
- Service tests use a 10-person dataset (INR 100/200/300/400, GBP 1000/2000/3000, AED 500,
  USD 700, plus one terminated employee who must never be counted). Every expected number can
  be worked out by hand.

**Mistakes caught by the tests:**
- The *test* was wrong: the assistant miscounted the dataset's headcount (7 instead of 9). The
  failing assertion caught it, and the expectation was corrected; the code was right.
- An aggregate with no `GROUP BY` returns one row even when no rows match, so an empty country
  produced `None` for min/max. Fixed with a dedicated `salary_range` query that returns `None`
  explicitly, with a test.
- SQLAlchemy 2.1 deprecated `Result.tuples()`. This surfaced because pytest treats warnings as
  errors, and was removed.

**Checked by hand against a running server:** the org summary for six sample employees matched
the hand-computed ₹50,185,000.

## Phase 4: Seed script

**Prompt (summary):** "Deterministic seed of 10,000 employees from first/last name files with
realistic distributions, idempotent, fast (bulk inserts). Record runtime in PERFORMANCE.md."

**What the assistant built:**
- `first_names.txt` / `last_names.txt` (~170 each, mixed across ACME's markets), generated
  because none were provided. The trade-off: names are combined at random, not matched to country.
- A pure generator taking `seed` and the name lists. Weighted countries and departments, a
  seniority pyramid, salary = USD base per level × market factor × department factor ×
  log-normal noise, converted to the pay currency and rounded to 1,000 (10,000 for JPY).
  40% get a 5–20% bonus. 25% of UAE and 10% of Singapore staff are paid in USD. Hire dates are
  skewed to recent years and relative to a *fixed* date, so the output never depends on today.
- A loader that uses `INSERT … ON CONFLICT DO NOTHING`, so a re-run is a no-op and never
  overwrites HR's edits to seeded rows. `--reset` wipes and reseeds.

**Corrected after looking at the output:** the first salary bands gave a US Senior Software
Engineer a median of $116k, which is low. The base per level was raised (≈ ₹20L entry-level in
India, ≈ $140k US senior). There is a test that seniority pays more than entry level in the same market.

**Verified, not assumed:** every generated row passes the same domain rules as the API (test).
Codes and emails are unique across all 10k (test). Runtime was measured 5× and compared against
the ORM row-by-row approach (see PERFORMANCE.md).

## Phase 5: Frontend

**Prompt (summary):** "Employees page (server-side pagination, search, filters, sort, add/edit
dialog with validation mirroring the backend, delete with confirmation) and Insights page
(country selector, KPI cards, avg-by-title chart, distribution chart). Loading/empty/error
states, `Intl.NumberFormat` per currency, typed API client, tests."

**What was built:**
- A typed API client that turns the backend's error envelope into an `ApiError` with
  per-field messages. A 409 "email already in use" therefore lands next to the email field.
- Money helpers. Rupees use Indian grouping (₹32,00,000) and yen has no decimals. Form input
  is parsed from major units to integer minor units with string arithmetic, never floats.
- Form validation as a pure function mirroring the backend rules. The server stays the source
  of truth, and its field errors are shown too.
- Choosing a country defaults the pay currency, and changing department clears an invalid job
  title. Both come from the domain rules, not just styling.
- The Insights page uses country + pay currency (matching the Phase 3 API). The org-wide INR
  figures are marked "≈" with the rate date, and per-country figures are exact.
- Backend: added `GET /api/reference` (test-first) so the forms and filters use the same
  catalogue as the validation.

**Testing:** 50 Vitest + Testing Library tests: money/client/validation units, plus
behavior tests for the Employees page (search debounce, sort toggling with `aria-sort`,
paging, filter resets page, empty and error states, delete only after confirmation) and the
form (client errors block the request, minor-unit payload, server error mapping, immutable
code on edit). The fetch mock routes by method + path and fails loudly on unmocked calls.
The utility tests were written alongside the code rather than strictly red-first.

**Corrections and choices made along the way:**
- The shadcn CLI added a package named `cn`. The assistant checked it before accepting it: it is
  the shadcn maintainers' own `clsx` + `tailwind-merge` replacement, not a typosquat.
- The default shadcn chart colors are near-white greys, so they were replaced with a blue and
  a teal that have contrast in light and dark themes.
- **Found by looking at the running app, not by tests:** after seeding 10k employees and
  screenshotting both pages (headless Chrome with an isolated profile), the chart bars were
  invisible because the grow-in animation never finished there, and averages showed paise
  ("₹23,18,906.65"). Animation was turned off and summary figures now round to whole units
  (with a test). Lazy-loading the Insights page removed the build's 500 kB bundle warning.
- Dropped TanStack Table, Radix Select and a form library as unnecessary at this size (see ADR-8).

**Dependencies added and why:** `tailwindcss` (styling), shadcn/ui and what it pulls in
(`radix-ui`, `class-variance-authority`, `cn`, `lucide-react`, `tw-animate-css`, Geist font),
`@tanstack/react-query` (server state), `react-router` (two pages), `recharts` (charts).

## Phase 6: Polish, performance, deploy

**Prompt (summary):** "Indexes justified by real query patterns with before/after timings,
Dockerfile(s), env-based config, deployment, README, final AI_USAGE pass, TRADEOFFS.md."

**Deployment decision (mine, with the assistant's analysis):** I asked for Vercel. The
assistant pointed out that a serverless function has no persistent disk, so SQLite there would
lose writes between instances. It laid out the free options (Render + Docker, Vercel + Neon,
GitHub Pages + an API elsewhere, and why Fly.io, Railway and Render Postgres didn't fit
"free"). I chose Vercel Hobby + Neon Postgres.

**"Swappable for Postgres" was proven, not claimed:**
- Added the `psycopg` driver and URL normalization for hosting-provider URLs (tested).
- The whole backend suite can target any database via `TEST_DATABASE_URL`. It ran green on a
  local Postgres 16 first, then as a CI job that also runs migrations, `alembic check` and the seed.
- The assistant compared insight results on SQLite and Postgres over the same 10k employees:
  identical to the paisa.

**Indexes: measured, including a regression:**
- Baseline first: every endpoint was already far inside its target. The README and
  PERFORMANCE.md say so instead of pretending the indexes rescued anything.
- Two composite indexes were chosen from the actual query plans (sort + full scan) and verified
  with `EXPLAIN` before and after.
- **The first measurement showed some SQLite queries got *slower*.** The assistant traced it to
  missing planner statistics. `ANALYZE` fixed it, and the seed now runs `ANALYZE` after loading.
  One small regression (+1.2 ms) remains, with the reason documented and accepted.

**Docker without Docker:** Docker isn't installed on my machine, so instead of shipping an
untested Dockerfile the assistant added a CI job that builds the image, starts it, and
smoke-tests the API (10,000 employees) and the UI served from the same origin.

**Other things caught:**
- Serving the SPA from FastAPI got a path-traversal test (`/..%2Fsecret.txt` must not leak
  files outside the UI folder) and keeps unknown `/api/*` paths as JSON 404s.
- **A mistake by the assistant:** one commit (the benchmark script) was made while ruff still
  reported line-length errors, breaking the "never commit red" rule. It noticed straight away,
  fixed the lines and amended that commit *before* pushing, so no red commit reached GitHub.
- Stayed off shared resources: separate `acme_*` databases on the local Postgres, its own
  headless Chrome profile for screenshots, and its own processes stopped by PID.

**What I'd keep doing differently with AI next time:** measure before optimizing (the baseline
changed the story), and verify claims (Postgres, Docker) with automation rather than prose.

**Found only after deploying:** seeding the real Neon database hung. The loader's
`executemany` made one network round trip per row, which is invisible on localhost and fatal
over the network. The assistant found it by checking `pg_stat_activity` (an open transaction,
0 rows committed after 5 minutes), stopped its own process by PID (the transaction rolled
back cleanly), and switched to one multi-row `INSERT … VALUES` per 1,000 rows: **7.7 s to Neon**.
It is slightly slower locally (0.2 s → 0.95 s) and PERFORMANCE.md records both numbers.
Lesson: test the data path against the real, remote database, not only a local one.

**Handling the database secret:** I offered to paste the Neon URL into the chat. The assistant
instead read it from my clipboard inside the command, so it never appeared in the transcript,
and printed only the host name to confirm it was the right database.
