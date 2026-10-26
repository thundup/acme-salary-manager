# Requirements — ACME Salary Manager

## Goal

Replace ACME's Excel-based salary tracking with a web app where HR can keep salary data for
~10,000 employees in many countries correct, and quickly answer "how do we pay people?"

## Persona

**HR Manager**: comfortable with Excel but not technical. Works across countries and thinks in
each country's local currency. Needs answers in seconds, not a pivot table rebuilt every month.

## User stories

| # | As an HR Manager I want to… | So that… |
|---|---|---|
| 1 | browse employees page by page, sorted by any column | I can scan the data without loading 10k rows |
| 2 | search by name or email and filter by country, department or job title | I can find a person or a cohort in seconds |
| 3 | add an employee with their salary | new hires are recorded on day one |
| 4 | edit an employee's details or salary | raises and transfers are reflected |
| 5 | mark an employee as having left, after confirming | leavers drop out of the list and the numbers but stay on record |
| 6 | see min / max / average / median salary and headcount per country | I can compare pay levels within a market |
| 7 | see average salary by job title and by department within a country | I can spot pay inconsistencies for the same role |
| 8 | see how salaries are distributed in a country | I can see the shape of pay, not just its average |
| 9 | see an org-wide summary in INR, clearly marked approximate | I can answer leadership's "what do we spend in total?" |

## In scope

- Employee CRUD with server-side validation (positive salary, optional non-negative bonus,
  ISO 3166-1 country, ISO 4217 currency, unique email and employee code) and clear 4xx errors.
- Soft delete: removing an employee marks them `terminated`; they are hidden by default.
- Paginated, sortable, filterable, searchable employee list.
- Insights computed in SQL: per-country stats, per-job-title/department breakdown, distribution
  buckets, org-wide summary in INR using static, dated exchange rates.
- A deterministic seed of 10,000 realistic employees that runs in seconds.
- Deployable as a single Docker image.

## Out of scope (and why)

| Item | Why not now |
|---|---|
| Real authentication / RBAC | Needs an identity provider and a role model the brief doesn't define. A single stub "HR Manager" user keeps the seams visible without pretending to be secure. **The deployed demo is therefore open; it holds only synthetic data.** |
| Payroll processing, tax, deductions, payslips | A different product with legal requirements per country. This app records *contracted base salary*, not what gets paid. |
| Live FX rates | Adds an external dependency, failure modes and non-deterministic tests. Static dated rates are enough for approximate comparisons and are labelled as such. |
| Salary history / audit trail | Valuable (and the obvious next step), but it doubles the data model. The current salary is stored; `updated_at` records when it last changed. |
| Restoring / rehiring a terminated employee | Soft delete keeps the record, so this is cheap to add later; it isn't in the brief. |
| Bulk Excel/CSV import and export | The most likely next feature for this persona, but it needs mapping, partial-failure and duplicate rules that deserve their own design. |
| Equity, allowances, bonus schedules / targets | Different shapes per country. Base salary + one optional annual bonus amount answers the brief's questions. |
| Multi-tenancy, i18n of the UI | One org (ACME), English UI. Money *is* formatted per currency. |

## Assumptions (confirmed)

1. **Salary = annual gross base salary**, in the employee's pay currency. Some employees also
   have an **optional annual bonus** (same currency, ≥ 0). Pay statistics are on base salary;
   the org-wide summary also reports total bonus.
2. **Pay currency is stored separately from country** (it defaults to the country's currency in
   the form). **INR is the reporting currency** for cross-country figures.
3. **Delete is a soft delete**: `status = terminated` plus `terminated_at`. Terminated
   employees are hidden from the list by default and excluded from all insights.
4. **Departments and job titles come from a fixed catalogue modelled on a typical tech
   company** (Engineering, Product, Design, Data, Infrastructure, QA, People, Finance, Sales,
   Customer Success), so filters and groupings stay clean.
5. A single HR user. No concurrent-edit conflict handling (last write wins).

## Success criteria

- An HR Manager can find, add, edit and remove an employee, with each action under 3 clicks from the list.
- Every insight in stories 6–9 is one page away and loads in **< 300 ms** on 10k employees
  (measured, recorded in `PERFORMANCE.md`).
- The list endpoint stays **< 100 ms** for any page, filter or sort on 10k rows.
- The seed creates 10,000 employees in **< 5 s** and gives identical data on every run.
- Domain rules (money, validation, statistics) are covered by fast tests; the backend suite
  runs in seconds with no network.
- A reviewer can run the app locally in ≤ 3 commands and open a live URL.
