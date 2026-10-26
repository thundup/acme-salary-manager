import type { OrgSummary } from '@/api/types'
import { formatMoney } from '@/lib/money'
import { KpiCard } from './KpiCard'

export function OrgSummaryCards({ summary }: { summary: OrgSummary }) {
  const inr = (amountMinor: number) =>
    formatMoney(amountMinor, summary.total_salary.currency, 2, { wholeUnits: true })
  const ratesNote = summary.rates_as_of
    ? `Approximate: converted to ${summary.total_salary.currency} at fixed rates as of ${new Date(
        summary.rates_as_of,
      ).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })}`
    : 'Approximate: converted at fixed rates'

  return (
    <div className="space-y-2">
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <KpiCard label="Active employees" value={summary.headcount.toLocaleString()} />
        <KpiCard
          label="Total annual base pay"
          value={`≈ ${inr(summary.total_salary.amount_minor)}`}
        />
        <KpiCard label="Average base pay" value={`≈ ${inr(summary.average_salary.amount_minor)}`} />
        <KpiCard label="Total annual bonus" value={`≈ ${inr(summary.total_bonus.amount_minor)}`} />
      </div>
      <p className="text-xs text-muted-foreground">{ratesNote}. Country figures below are exact.</p>
    </div>
  )
}
