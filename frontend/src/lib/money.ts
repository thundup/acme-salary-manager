const LOCALE_BY_CURRENCY: Record<string, string> = { INR: 'en-IN' }

function localeFor(currency: string): string {
  return LOCALE_BY_CURRENCY[currency] ?? 'en-US'
}

export function formatMoney(
  amountMinor: number,
  currency: string,
  minorUnit: number,
  { compact = false, wholeUnits = false }: { compact?: boolean; wholeUnits?: boolean } = {},
): string {
  return new Intl.NumberFormat(localeFor(currency), {
    style: 'currency',
    currency,
    notation: compact ? 'compact' : 'standard',
    minimumFractionDigits: 0,
    maximumFractionDigits: compact ? 1 : wholeUnits ? 0 : minorUnit,
  }).format(amountMinor / 10 ** minorUnit)
}

export function parseMajorToMinor(input: string, minorUnit: number): number | null {
  const cleaned = input.replace(/[\s,]/g, '')
  const pattern = minorUnit === 0 ? /^\d+$/ : new RegExp(`^\\d+(\\.\\d{1,${minorUnit}})?$`)
  if (!pattern.test(cleaned)) {
    return null
  }
  const [whole, fraction = ''] = cleaned.split('.')
  return Number(whole + fraction.padEnd(minorUnit, '0'))
}

export function minorToMajorInput(amountMinor: number, minorUnit: number): string {
  const factor = 10 ** minorUnit
  const whole = Math.trunc(amountMinor / factor)
  const fraction = amountMinor % factor
  return fraction === 0 ? String(whole) : `${whole}.${String(fraction).padStart(minorUnit, '0')}`
}
