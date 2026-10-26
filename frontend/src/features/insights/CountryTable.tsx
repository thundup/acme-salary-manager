import type { CountryStats, Reference } from '@/api/types'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { flagEmoji } from '@/lib/display'
import { moneyFormatter } from './format'

export function CountryTable({
  markets,
  reference,
}: {
  markets: CountryStats[]
  reference: Reference
}) {
  return (
    <div className="space-y-2">
      <h2 className="text-lg font-semibold">Pay by country</h2>
      <div className="overflow-hidden rounded-xl border bg-card shadow-sm">
        <Table>
          <TableHeader className="bg-muted/60">
            <TableRow className="hover:bg-transparent">
              <TableHead>Country</TableHead>
              <TableHead>Pay currency</TableHead>
              <TableHead className="text-right">Headcount</TableHead>
              <TableHead className="text-right">Lowest</TableHead>
              <TableHead className="text-right">Median</TableHead>
              <TableHead className="text-right">Average</TableHead>
              <TableHead className="text-right">Highest</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {markets.map((m) => {
              const format = moneyFormatter(reference, m.currency_code)
              return (
                <TableRow key={`${m.country_code}:${m.currency_code}`}>
                  <TableCell className="font-medium whitespace-nowrap">
                    <span aria-hidden="true" className="mr-1.5">
                      {flagEmoji(m.country_code)}
                    </span>
                    {m.country_name}
                  </TableCell>
                  <TableCell>{m.currency_code}</TableCell>
                  <TableCell className="text-right tabular-nums">
                    {m.headcount.toLocaleString()}
                  </TableCell>
                  <TableCell className="text-right tabular-nums">
                    {format(m.min.amount_minor)}
                  </TableCell>
                  <TableCell className="text-right tabular-nums">
                    {format(m.median.amount_minor)}
                  </TableCell>
                  <TableCell className="text-right tabular-nums">
                    {format(m.average.amount_minor)}
                  </TableCell>
                  <TableCell className="text-right tabular-nums">
                    {format(m.max.amount_minor)}
                  </TableCell>
                </TableRow>
              )
            })}
          </TableBody>
        </Table>
      </div>
    </div>
  )
}
