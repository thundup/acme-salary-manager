import { screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, describe, expect, it, vi } from 'vitest'
import type { Employee } from '@/api/types'
import { employee, reference } from '@/test/fixtures'
import { mockApi, renderWithProviders, requestsTo } from '@/test/render'
import { EmployeesPage } from './EmployeesPage'

afterEach(() => {
  vi.unstubAllGlobals()
})

function setup(items: Employee[] = [employee()], total = items.length) {
  const fetchMock = mockApi([
    { path: '/reference', respond: () => ({ body: reference }) },
    { path: '/employees', respond: () => ({ body: { items, total, page: 1, page_size: 25 } }) },
    { method: 'DELETE', path: '/employees/1', respond: () => ({ status: 204 }) },
  ])
  renderWithProviders(<EmployeesPage />)
  return { fetchMock, user: userEvent.setup() }
}

describe('EmployeesPage', () => {
  it('shows each salary in the employee’s own currency', async () => {
    setup([
      employee(),
      employee({
        id: 2,
        full_name: 'Yuki Tanaka',
        country_code: 'JP',
        currency_code: 'JPY',
        salary_minor: 9_500_000,
        bonus_minor: 500_000,
      }),
    ])

    const yuki = (await screen.findByText('Yuki Tanaka')).closest('tr')!
    expect(within(yuki).getByText('¥9,500,000')).toBeInTheDocument()
    expect(within(yuki).getByText('+ ¥500,000 bonus')).toBeInTheDocument()
    expect(screen.getByText('₹32,00,000')).toBeInTheDocument()
  })

  it('searches by name or email after the user stops typing', async () => {
    const { fetchMock, user } = setup()
    await screen.findByText('Asha Rao')

    await user.type(screen.getByRole('searchbox', { name: 'Search name or email' }), 'rao')

    await waitFor(() => {
      expect(requestsTo(fetchMock, '/employees').at(-1)?.searchParams.get('q')).toBe('rao')
    })
    const searches = requestsTo(fetchMock, '/employees').filter((url) => url.searchParams.has('q'))
    expect(searches).toHaveLength(1)
  })

  it('sorts by a column and toggles the direction on a second click', async () => {
    const { fetchMock, user } = setup()
    await screen.findByText('Asha Rao')
    const salaryHeader = screen.getByRole('columnheader', { name: /annual salary/i })

    await user.click(within(salaryHeader).getByRole('button'))
    await user.click(within(salaryHeader).getByRole('button'))

    const last = requestsTo(fetchMock, '/employees').at(-1)!
    expect(last.searchParams.get('sort')).toBe('salary_minor')
    expect(last.searchParams.get('order')).toBe('desc')
    expect(salaryHeader).toHaveAttribute('aria-sort', 'descending')
  })

  it('pages through results', async () => {
    const { fetchMock, user } = setup([employee()], 60)
    await screen.findByText('Asha Rao')
    expect(screen.getByText('Page 1 of 3')).toBeInTheDocument()

    await user.click(screen.getByRole('button', { name: 'Next' }))

    await waitFor(() => {
      expect(requestsTo(fetchMock, '/employees').at(-1)?.searchParams.get('page')).toBe('2')
    })
  })

  it('filters by country and resets to the first page', async () => {
    const { fetchMock, user } = setup([employee()], 60)
    await screen.findByText('Asha Rao')
    await user.click(screen.getByRole('button', { name: 'Next' }))

    await user.selectOptions(screen.getByRole('combobox', { name: 'Country' }), 'JP')

    await waitFor(() => {
      const last = requestsTo(fetchMock, '/employees').at(-1)!
      expect(last.searchParams.get('country')).toBe('JP')
      expect(last.searchParams.get('page')).toBe('1')
    })
  })

  it('offers to clear filters when nothing matches', async () => {
    const { user } = setup([])
    await screen.findByRole('option', { name: 'United States' })
    await user.selectOptions(screen.getByRole('combobox', { name: 'Country' }), 'US')

    expect(await screen.findByText('No employees match')).toBeInTheDocument()
    await user.click(screen.getByRole('button', { name: 'Clear filters' }))
    expect(screen.getByRole('combobox', { name: 'Country' })).toHaveValue('')
  })

  it('shows an error with a retry when the API fails', async () => {
    mockApi([
      { path: '/reference', respond: () => ({ body: reference }) },
      { path: '/employees', respond: () => ({ status: 500, body: {} }) },
    ])
    renderWithProviders(<EmployeesPage />)

    const alert = await screen.findByRole('alert')
    expect(within(alert).getByRole('button', { name: 'Try again' })).toBeInTheDocument()
  })

  it('removes an employee only after confirmation', async () => {
    const { fetchMock, user } = setup()

    await user.click(await screen.findByRole('button', { name: 'Remove Asha Rao' }))
    expect(requestsTo(fetchMock, '/employees/1')).toHaveLength(0)
    await user.click(await screen.findByRole('button', { name: 'Remove employee' }))

    await waitFor(() => expect(requestsTo(fetchMock, '/employees/1')).toHaveLength(1))
  })
})
