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
