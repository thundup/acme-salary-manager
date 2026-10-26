import type { Employee, Reference } from '@/api/types'

export const reference: Reference = {
  countries: [
    { code: 'IN', name: 'India', currency_code: 'INR' },
    { code: 'US', name: 'United States', currency_code: 'USD' },
    { code: 'JP', name: 'Japan', currency_code: 'JPY' },
  ],
  currencies: [
    { code: 'INR', minor_unit: 2 },
    { code: 'USD', minor_unit: 2 },
    { code: 'JPY', minor_unit: 0 },
  ],
  departments: [
    { name: 'Engineering', job_titles: ['Software Engineer I', 'Senior Software Engineer'] },
    { name: 'Finance', job_titles: ['Accountant'] },
  ],
  employment_types: ['full_time', 'part_time', 'contractor'],
  reporting_currency: 'INR',
}

export function employee(overrides: Partial<Employee> = {}): Employee {
  return {
    id: 1,
    employee_code: 'ACME-000001',
    full_name: 'Asha Rao',
    email: 'asha.rao@acme-corp.com',
    job_title: 'Senior Software Engineer',
    department: 'Engineering',
    country_code: 'IN',
    currency_code: 'INR',
    salary_minor: 32_00_000_00,
    bonus_minor: null,
    employment_type: 'full_time',
    hire_date: '2021-06-01',
    status: 'active',
    terminated_at: null,
    created_at: '2026-10-01T00:00:00',
    updated_at: '2026-10-01T00:00:00',
    ...overrides,
  }
}
