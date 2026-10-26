import type { Reference } from '@/api/types'
import { minorUnitOf } from '@/features/employees/form'
import { formatMoney } from '@/lib/money'

export function moneyFormatter(reference: Reference, currency: string, compact = false) {
  const minorUnit = minorUnitOf(reference, currency)
  return (amountMinor: number) =>
    formatMoney(amountMinor, currency, minorUnit, { compact, wholeUnits: true })
}
