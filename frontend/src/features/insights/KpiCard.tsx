import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

export function KpiCard({
  label,
  value,
  hint,
  highlight = false,
}: {
  label: string
  value: string
  hint?: string
  highlight?: boolean
}) {
  return (
    <Card size="sm" className={highlight ? 'border-primary/20 bg-primary/5' : 'shadow-sm'}>
      <CardHeader>
        <CardDescription>{label}</CardDescription>
        <CardTitle className="text-xl tabular-nums">{value}</CardTitle>
      </CardHeader>
      {hint && <CardContent className="text-xs text-muted-foreground">{hint}</CardContent>}
    </Card>
  )
}
