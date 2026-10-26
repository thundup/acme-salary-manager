import { useState } from 'react'
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { useBreakdown } from '@/api/hooks'
import type { Reference } from '@/api/types'
import { EmptyState, ErrorState } from '@/components/states'
import { Button } from '@/components/ui/button'
import { Card, CardAction, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { moneyFormatter } from './format'

type GroupBy = 'job_title' | 'department'

export function BreakdownChart({
  country,
  currency,
  reference,
}: {
  country: string
  currency: string
  reference: Reference
}) {
  const [by, setBy] = useState<GroupBy>('job_title')
  const breakdown = useBreakdown(country, currency, by)
  const full = moneyFormatter(reference, currency)
  const compact = moneyFormatter(reference, currency, true)
  const rows = (breakdown.data ?? []).map((g) => ({
    name: g.key,
    average: g.average.amount_minor,
    headcount: g.headcount,
  }))

  return (
    <Card>
      <CardHeader>
        <CardTitle>Average salary by {by === 'job_title' ? 'job title' : 'department'}</CardTitle>
        <CardAction>
          <div role="group" aria-label="Group by" className="flex gap-1">
            {(['job_title', 'department'] as const).map((option) => (
              <Button
                key={option}
                size="xs"
                variant={by === option ? 'secondary' : 'ghost'}
                aria-pressed={by === option}
                onClick={() => setBy(option)}
              >
                {option === 'job_title' ? 'Job title' : 'Department'}
              </Button>
            ))}
          </div>
        </CardAction>
      </CardHeader>
      <CardContent>
        {breakdown.isError ? (
          <ErrorState message={breakdown.error.message} onRetry={() => void breakdown.refetch()} />
        ) : !breakdown.data ? (
          <Skeleton className="h-72 w-full" />
        ) : rows.length === 0 ? (
          <EmptyState title="No employees in this market" />
        ) : (
          <div style={{ height: Math.max(220, rows.length * 30) }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={rows} layout="vertical" margin={{ left: 8, right: 16 }}>
                <CartesianGrid horizontal={false} strokeDasharray="3 3" />
                <XAxis type="number" tickFormatter={compact} fontSize={12} />
                <YAxis type="category" dataKey="name" width={170} fontSize={12} />
                <Tooltip
                  formatter={(value, _name, item) => [
                    `${full(Number(value))} · ${item.payload.headcount} people`,
                    'Average',
                  ]}
                />
                <Bar dataKey="average" fill="var(--chart-2)" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
