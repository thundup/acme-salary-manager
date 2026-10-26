import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { employee, reference } from '@/test/fixtures'
import { mockApi, renderWithProviders } from '@/test/render'
import { EmployeeFormDialog } from './EmployeeFormDialog'

afterEach(() => {
  vi.unstubAllGlobals()
})

function renderForm(props: { employee?: ReturnType<typeof employee> } = {}) {
  const onOpenChange = vi.fn()
  renderWithProviders(
    <EmployeeFormDialog
      open
      onOpenChange={onOpenChange}
      reference={reference}
      today="2026-10-26"
      {...props}
    />,
  )
  return { onOpenChange, user: userEvent.setup() }
}

async function fillValidEmployee(user: ReturnType<typeof userEvent.setup>) {
  await user.type(screen.getByLabelText('Employee code'), 'acme-000042')
  await user.type(screen.getByLabelText('Full name'), 'Priya Nair')
  await user.type(screen.getByLabelText('Work email'), 'priya.nair@acme-corp.com')
  await user.selectOptions(screen.getByLabelText('Department'), 'Engineering')
  await user.selectOptions(screen.getByLabelText('Job title'), 'Software Engineer I')
  await user.selectOptions(screen.getByLabelText('Country'), 'IN')
  await user.type(screen.getByLabelText('Annual salary (INR)'), '18,50,000')
  await user.type(screen.getByLabelText('Hire date'), '2025-02-03')
}

describe('EmployeeFormDialog', () => {
  it('shows field errors and does not call the API when the form is invalid', async () => {
    const fetchMock = mockApi([])
    const { user } = renderForm()

    await user.click(screen.getByRole('button', { name: 'Add employee' }))

    expect(screen.getByText('Use the format ACME-000123')).toBeInTheDocument()
    expect(screen.getByText('Enter an annual salary greater than zero')).toBeInTheDocument()
    expect(fetchMock).not.toHaveBeenCalled()
  })

  it('defaults the pay currency to the chosen country’s currency', async () => {
    mockApi([])
    const { user } = renderForm()

    await user.selectOptions(screen.getByLabelText('Country'), 'JP')

    expect(screen.getByLabelText('Pay currency')).toHaveValue('JPY')
  })

  it('creates an employee with the salary converted to minor units', async () => {
    const fetchMock = mockApi([
      { method: 'POST', path: '/employees', respond: () => ({ status: 201, body: employee() }) },
    ])
    const { user, onOpenChange } = renderForm()

    await fillValidEmployee(user)
    await user.click(screen.getByRole('button', { name: 'Add employee' }))

    await waitFor(() => expect(onOpenChange).toHaveBeenCalledWith(false))
    const body = JSON.parse(fetchMock.mock.calls[0][1]!.body as string)
    expect(body).toMatchObject({
      employee_code: 'ACME-000042',
      currency_code: 'INR',
      salary_minor: 18_50_000_00,
      bonus_minor: null,
    })
  })

  it('shows a duplicate email from the server next to the email field', async () => {
    mockApi([
      {
        method: 'POST',
        path: '/employees',
        respond: () => ({
          status: 409,
          body: {
            error: {
              code: 'duplicate_employee',
              message: 'An employee with this email already exists',
              fields: { email: 'Already in use' },
            },
          },
        }),
      },
    ])
    const { user, onOpenChange } = renderForm()

    await fillValidEmployee(user)
    await user.click(screen.getByRole('button', { name: 'Add employee' }))

    expect(await screen.findByText('Already in use')).toBeInTheDocument()
    expect(screen.getByRole('alert')).toHaveTextContent(
      'An employee with this email already exists',
    )
    expect(onOpenChange).not.toHaveBeenCalled()
  })

  it('edits an existing employee without sending the immutable code', async () => {
    const fetchMock = mockApi([
      { method: 'PATCH', path: '/employees/1', respond: () => ({ body: employee() }) },
    ])
    const { user } = renderForm({ employee: employee() })
    expect(screen.getByLabelText('Employee code')).toBeDisabled()

    const salary = screen.getByLabelText('Annual salary (INR)')
    await user.clear(salary)
    await user.type(salary, '35,00,000')
    await user.click(screen.getByRole('button', { name: 'Save changes' }))

    await waitFor(() => expect(fetchMock).toHaveBeenCalled())
    const body = JSON.parse(fetchMock.mock.calls[0][1]!.body as string)
    expect(body.salary_minor).toBe(35_00_000_00)
    expect(body).not.toHaveProperty('employee_code')
  })
})
