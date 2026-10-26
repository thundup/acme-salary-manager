import { describe, expect, it } from 'vitest'
import { formatMoney, minorToMajorInput, parseMajorToMinor } from './money'

describe('formatMoney', () => {
  it('formats rupees with Indian digit grouping', () => {
    expect(formatMoney(3_250_000_00, 'INR', 2)).toBe('₹32,50,000')
  })

  it('formats yen, which has no minor unit', () => {
    expect(formatMoney(9_500_000, 'JPY', 0)).toBe('¥9,500,000')
  })

  it('keeps paise or cents when present', () => {
    expect(formatMoney(12_345_67, 'USD', 2)).toBe('$12,345.67')
  })

  it('can round to whole units for summary figures', () => {
    expect(formatMoney(23_18_906_65, 'INR', 2, { wholeUnits: true })).toBe('₹23,18,907')
  })

  it('can format compactly for chart axes', () => {
    expect(formatMoney(120_000_00, 'USD', 2, { compact: true })).toBe('$120K')
  })
})

describe('parseMajorToMinor', () => {
  it.each([
    ['85000', 2, 85_000_00],
    ['85,000.5', 2, 85_000_50],
    ['32,50,000', 2, 32_50_000_00],
    ['9500000', 0, 9_500_000],
    [' 1 000 ', 2, 1_000_00],
  ])('parses %s with %d decimals', (input, minorUnit, expected) => {
    expect(parseMajorToMinor(input, minorUnit)).toBe(expected)
  })

  it.each([
    ['', 2],
    ['abc', 2],
    ['-5', 2],
    ['1.234', 2],
    ['1.5', 0],
  ])('rejects %s with %d decimals', (input, minorUnit) => {
    expect(parseMajorToMinor(input, minorUnit)).toBeNull()
  })
})

describe('minorToMajorInput', () => {
  it('round-trips amounts for the edit form', () => {
    expect(minorToMajorInput(85_000_50, 2)).toBe('85000.50')
    expect(minorToMajorInput(85_000_00, 2)).toBe('85000')
    expect(minorToMajorInput(9_500_000, 0)).toBe('9500000')
  })
})
