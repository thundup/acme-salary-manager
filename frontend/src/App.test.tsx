import { screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import App from './App'
import { reference } from '@/test/fixtures'
import { mockApi, renderWithProviders } from '@/test/render'

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('App', () => {
  it('opens on the employees page with navigation to insights', async () => {
    mockApi([
      { path: '/reference', respond: () => ({ body: reference }) },
      {
        path: '/employees',
        respond: () => ({ body: { items: [], total: 0, page: 1, page_size: 25 } }),
      },
    ])

    renderWithProviders(<App />, { route: '/' })

    expect(await screen.findByRole('heading', { name: 'Employees', level: 1 })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Insights' })).toHaveAttribute('href', '/insights')
  })
})
