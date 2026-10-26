import { describe, expect, it } from 'vitest'
import { employee, reference } from '@/test/fixtures'
import {
  EMPTY_FORM,
  type EmployeeFormValues,
  fieldForServerError,
  formValuesFrom,
  toEmployeeInput,
  toEmployeeUpdate,
  validateEmployeeForm,
} from './form'

const TODAY = '2026-10-26'

const valid: EmployeeFormValues = {
  ...EMPTY_FORM,
  employee_code: 'ACME-000042',
  full_name: '  Asha Rao ',
  email: 'asha@acme-corp.com',
  department: 'Engineering',
  job_title: 'Senior Software Engineer',
  country_code: 'IN',
  currency_code: 'INR',
  salary: '32,00,000',
  bonus: '',
  hire_date: '2024-01-15',
}

describe('validateEmployeeForm', () => {
  it('accepts a complete, consistent employee', () => {
    expect(validateEmployeeForm(valid, reference, TODAY)).toEqual({})
  })

  it('mirrors the backend rules for each field', () => {
    const errors = validateEmployeeForm(
      {
        ...valid,
        employee_code: '42',
        full_name: '   ',
        email: 'nope',
        job_title: 'Accountant',
        salary: '0',
        bonus: '-5',
        hire_date: '2026-10-27',
      },
      reference,
      TODAY,
    )

    expect(Object.keys(errors).sort()).toEqual([
      'bonus',
      'email',
      'employee_code',
      'full_name',
      'hire_date',
      'job_title',
      'salary',
    ])
    expect(errors.job_title).toBe('Choose a job title in Engineering')
  })

  it('uses the currency’s decimals: yen cannot have a fractional part', () => {
    const errors = validateEmployeeForm(
      { ...valid, country_code: 'JP', currency_code: 'JPY', salary: '9500000.5' },
      reference,
      TODAY,
    )

    expect(errors.salary).toBeDefined()
  })

  it('allows a hire date of today', () => {
    expect(validateEmployeeForm({ ...valid, hire_date: TODAY }, reference, TODAY)).toEqual({})
  })
})

describe('toEmployeeInput', () => {
  it('converts major-unit inputs to minor units and trims text', () => {
    expect(toEmployeeInput({ ...valid, bonus: '2,50,000' }, reference)).toMatchObject({
      full_name: 'Asha Rao',
      salary_minor: 32_00_000_00,
      bonus_minor: 2_50_000_00,
    })
  })

  it('sends an empty bonus as null', () => {
    expect(toEmployeeInput(valid, reference).bonus_minor).toBeNull()
  })
})

describe('toEmployeeUpdate', () => {
  it('never sends the immutable employee code', () => {
    expect(toEmployeeUpdate(valid, reference)).not.toHaveProperty('employee_code')
  })
})

describe('formValuesFrom', () => {
  it('round-trips an existing employee into editable strings', () => {
    const values = formValuesFrom(employee({ salary_minor: 9_500_000, currency_code: 'JPY' }), {
      ...reference,
    })

    expect(values.salary).toBe('9500000')
    expect(values.bonus).toBe('')
  })
})

describe('fieldForServerError', () => {
  it('maps API field names onto form fields', () => {
    expect(fieldForServerError('salary_minor')).toBe('salary')
    expect(fieldForServerError('email')).toBe('email')
    expect(fieldForServerError('page')).toBeNull()
  })
})
