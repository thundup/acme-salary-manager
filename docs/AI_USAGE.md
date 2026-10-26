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
