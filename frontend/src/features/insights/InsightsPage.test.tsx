import { screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, describe, expect, it, vi } from 'vitest'
import type { CountryStats, Money } from '@/api/types'
import { reference } from '@/test/fixtures'
import { mockApi, renderWithProviders, requestsTo } from '@/test/render'
import { InsightsPage } from './InsightsPage'

afterEach(() => {
  vi.unstubAllGlobals()
})

const money = (amount_minor: number, currency: string): Money => ({ amount_minor, currency })

function market(
  country_code: string,
  country_name: string,
  currency: string,
  headcount: number,
  amounts: [number, number, number, number],
): CountryStats {
  const [min, median, average, max] = amounts
  return {
    country_code,
    country_name,
    currency_code: currency,
    headcount,
    min: money(min, currency),
    median: money(median, currency),
    average: money(average, currency),
    max: money(max, currency),
  }
}

const markets = [
  market('US', 'United States', 'USD', 40, [60_000_00, 120_000_00, 125_000_00, 240_000_00]),
  market('IN', 'India', 'INR', 120, [9_00_000_00, 21_00_000_00, 24_50_000_00, 80_00_000_00]),
  market('JP', 'Japan', 'JPY', 5, [6_000_000, 9_000_000, 9_500_000, 14_000_000]),
]

function setup(countries: CountryStats[] = markets) {
  const fetchMock = mockApi([
    { path: '/reference', respond: () => ({ body: reference }) },
    { path: '/insights/countries', respond: () => ({ body: countries }) },
    {
      path: '/insights/summary',
      respond: () => ({
        body: {
          headcount: 165,
          total_salary: money(5_018_500_000, 'INR'),
          total_bonus: money(367_000_000, 'INR'),
          average_salary: money(30_415_152, 'INR'),
          approximate: true,
          rates_as_of: '2026-10-01',
        },
      }),
    },
    {
      path: '/insights/countries/IN/breakdown',
      respond: () => ({ body: [] }),
    },
    {
      path: '/insights/countries/IN/distribution',
      respond: () => ({ body: { country_code: 'IN', currency_code: 'INR', buckets: [] } }),
    },
    {
      path: '/insights/countries/JP/breakdown',
      respond: () => ({ body: [] }),
    },
    {
      path: '/insights/countries/JP/distribution',
      respond: () => ({ body: { country_code: 'JP', currency_code: 'JPY', buckets: [] } }),
    },
  ])
  renderWithProviders(<InsightsPage />)
  return { fetchMock, user: userEvent.setup() }
}

describe('InsightsPage', () => {
  it('labels the org-wide INR figures as approximate with the rate date', async () => {
    setup()

    expect(await screen.findByText('≈ ₹5,01,85,000')).toBeInTheDocument()
    expect(
      screen.getByText(/Approximate: converted to INR at fixed rates as of 1 Oct 2026/),
    ).toBeInTheDocument()
  })

  it('starts with the largest market and shows its figures in local currency', async () => {
    setup()

    expect(await screen.findByRole('heading', { name: /India/ })).toBeInTheDocument()
    const median = screen.getAllByText('Median').find((el) => el.closest('[data-slot="card"]'))!
    expect(
      within(median.closest('[data-slot="card"]') as HTMLElement).getByText('₹21,00,000'),
    ).toBeInTheDocument()
  })

  it('lists every market in the pay-by-country table', async () => {
    setup()

    const table = await screen.findByRole('table')
    expect(within(table).getAllByRole('row')).toHaveLength(markets.length + 1)
    expect(within(table).getByText('¥14,000,000')).toBeInTheDocument()
  })

  it('loads charts for the chosen market', async () => {
    const { fetchMock, user } = setup()
    await screen.findByRole('heading', { name: /India/ })

    await user.selectOptions(screen.getByRole('combobox'), 'JP:JPY')

    await waitFor(() => {
      const breakdown = requestsTo(fetchMock, '/insights/countries/JP/breakdown').at(-1)
      expect(breakdown?.searchParams.get('currency')).toBe('JPY')
    })
    expect(requestsTo(fetchMock, '/insights/countries/JP/distribution')).not.toHaveLength(0)
  })

  it('switches the breakdown between job title and department', async () => {
    const { fetchMock, user } = setup()
    await screen.findByRole('heading', { name: /India/ })

    await user.click(screen.getByRole('button', { name: 'Department' }))

    await waitFor(() => {
      const last = requestsTo(fetchMock, '/insights/countries/IN/breakdown').at(-1)
      expect(last?.searchParams.get('by')).toBe('department')
    })
    expect(screen.getByRole('button', { name: 'Department' })).toHaveAttribute(
      'aria-pressed',
      'true',
    )
  })

  it('explains when there is no data yet', async () => {
    setup([])

    expect(await screen.findByText('No salary data yet')).toBeInTheDocument()
  })
})
