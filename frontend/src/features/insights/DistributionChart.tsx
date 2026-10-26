import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { useDistribution } from '@/api/hooks'
import type { Reference } from '@/api/types'
import { EmptyState, ErrorState } from '@/components/states'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { moneyFormatter } from './format'

export function DistributionChart({
  country,
  currency,
  reference,
}: {
  country: string
  currency: string
  reference: Reference
}) {
  const distribution = useDistribution(country, currency)
  const compact = moneyFormatter(reference, currency, true)
  const full = moneyFormatter(reference, currency)
  const rows = (distribution.data?.buckets ?? []).map((b) => ({
    label: compact(b.lower_minor),
    range: `${full(b.lower_minor)} – ${full(b.upper_minor)}`,
    count: b.count,
  }))

  return (
    <Card>
      <CardHeader>
        <CardTitle>Salary distribution</CardTitle>
        <CardDescription>Number of people in each salary range</CardDescription>
      </CardHeader>
      <CardContent>
        {distribution.isError ? (
          <ErrorState
            message={distribution.error.message}
            onRetry={() => void distribution.refetch()}
          />
        ) : !distribution.data ? (
          <Skeleton className="h-72 w-full" />
        ) : rows.length === 0 ? (
          <EmptyState title="No employees in this market" />
        ) : (
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={rows} margin={{ right: 8 }}>
                <CartesianGrid vertical={false} strokeDasharray="3 3" />
                <XAxis dataKey="label" fontSize={12} interval="preserveStartEnd" />
                <YAxis allowDecimals={false} fontSize={12} width={40} />
                <Tooltip
                  labelFormatter={(_label, payload) => payload[0]?.payload.range ?? ''}
                  formatter={(value) => [Number(value).toLocaleString(), 'People']}
                />
                <Bar dataKey="count" fill="var(--chart-1)" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
