import { useState } from 'react'
import { useCountryStats, useOrgSummary, useReference } from '@/api/hooks'
import type { CountryStats, Reference } from '@/api/types'
import { NativeSelect } from '@/components/NativeSelect'
import { EmptyState, ErrorState } from '@/components/states'
import { Skeleton } from '@/components/ui/skeleton'
import { BreakdownChart } from './BreakdownChart'
import { CountryTable } from './CountryTable'
import { DistributionChart } from './DistributionChart'
import { KpiCard } from './KpiCard'
import { OrgSummaryCards } from './OrgSummaryCards'
import { moneyFormatter } from './format'

function marketKey(stats: Pick<CountryStats, 'country_code' | 'currency_code'>): string {
  return `${stats.country_code}:${stats.currency_code}`
}

export function InsightsPage() {
  const reference = useReference()
  const countries = useCountryStats()
  const summary = useOrgSummary()
  const [selectedKey, setSelectedKey] = useState<string | null>(null)

  const error = reference.error ?? countries.error ?? summary.error
  if (error) {
    return (
      <ErrorState
        message={error.message}
        onRetry={() => {
          void reference.refetch()
          void countries.refetch()
          void summary.refetch()
        }}
      />
    )
  }

  const markets = [...(countries.data ?? [])].sort((a, b) => b.headcount - a.headcount)
  const selected = markets.find((m) => marketKey(m) === selectedKey) ?? markets[0]

  return (
    <section className="space-y-8">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Insights</h1>
        <p className="text-sm text-muted-foreground">
          How ACME pays people. Active employees only, annual base salary.
        </p>
      </div>

      {summary.data ? (
        <OrgSummaryCards summary={summary.data} />
      ) : (
        <Skeleton className="h-28 w-full" aria-label="Loading summary" />
      )}

      {!countries.data || !reference.data ? (
        <Skeleton className="h-64 w-full" aria-label="Loading countries" />
      ) : markets.length === 0 || !selected ? (
        <EmptyState title="No salary data yet">Add employees to see insights.</EmptyState>
      ) : (
        <>
          <CountryTable markets={markets} reference={reference.data} />
          <CountryDetail
            market={selected}
            markets={markets}
            reference={reference.data}
            onSelect={setSelectedKey}
          />
        </>
      )}
    </section>
  )
}

function CountryDetail({
  market,
  markets,
  reference,
  onSelect,
}: {
  market: CountryStats
  markets: CountryStats[]
  reference: Reference
  onSelect: (key: string) => void
}) {
  const format = moneyFormatter(reference, market.currency_code)

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <h2 className="text-lg font-semibold">
          {market.country_name}{' '}
          <span className="font-normal text-muted-foreground">
            · paid in {market.currency_code}
          </span>
        </h2>
        <label className="grid gap-1 text-sm">
          <span className="text-muted-foreground">Country and pay currency</span>
          <NativeSelect
            className="w-72"
            value={marketKey(market)}
            onChange={(e) => onSelect(e.target.value)}
          >
            {markets.map((m) => (
              <option key={marketKey(m)} value={marketKey(m)}>
                {m.country_name} · {m.currency_code} ({m.headcount.toLocaleString()})
              </option>
            ))}
          </NativeSelect>
        </label>
      </div>

      <div className="grid gap-3 sm:grid-cols-3 lg:grid-cols-5">
        <KpiCard label="Headcount" value={market.headcount.toLocaleString()} />
        <KpiCard label="Lowest" value={format(market.min.amount_minor)} />
        <KpiCard label="Median" value={format(market.median.amount_minor)} />
        <KpiCard label="Average" value={format(market.average.amount_minor)} />
        <KpiCard label="Highest" value={format(market.max.amount_minor)} />
      </div>

      <div className="grid items-start gap-4 lg:grid-cols-2">
        <BreakdownChart
          country={market.country_code}
          currency={market.currency_code}
          reference={reference}
        />
        <DistributionChart
          country={market.country_code}
          currency={market.currency_code}
          reference={reference}
        />
      </div>
    </div>
  )
}
