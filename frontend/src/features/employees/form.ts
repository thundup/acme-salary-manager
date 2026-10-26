import type { Employee, EmployeeInput, EmploymentType, Reference } from '@/api/types'
import { minorToMajorInput, parseMajorToMinor } from '@/lib/money'

export interface EmployeeFormValues {
  employee_code: string
  full_name: string
  email: string
  department: string
  job_title: string
  country_code: string
  currency_code: string
  salary: string
  bonus: string
  employment_type: EmploymentType | ''
  hire_date: string
}

export type FormErrors = Partial<Record<keyof EmployeeFormValues, string>>

const MAX_MINOR_AMOUNT = 10 ** 13
const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
const CODE_PATTERN = /^ACME-\d{6}$/

export const EMPTY_FORM: EmployeeFormValues = {
  employee_code: '',
  full_name: '',
  email: '',
  department: '',
  job_title: '',
  country_code: '',
  currency_code: '',
  salary: '',
  bonus: '',
  employment_type: 'full_time',
  hire_date: '',
}

export function minorUnitOf(reference: Reference, currency: string): number {
  return reference.currencies.find((c) => c.code === currency)?.minor_unit ?? 2
}

export function formValuesFrom(employee: Employee, reference: Reference): EmployeeFormValues {
  const minorUnit = minorUnitOf(reference, employee.currency_code)
  return {
    employee_code: employee.employee_code,
    full_name: employee.full_name,
    email: employee.email,
    department: employee.department,
    job_title: employee.job_title,
    country_code: employee.country_code,
    currency_code: employee.currency_code,
    salary: minorToMajorInput(employee.salary_minor, minorUnit),
    bonus: employee.bonus_minor === null ? '' : minorToMajorInput(employee.bonus_minor, minorUnit),
    employment_type: employee.employment_type,
    hire_date: employee.hire_date,
  }
}

export function validateEmployeeForm(
  values: EmployeeFormValues,
  reference: Reference,
  today: string,
): FormErrors {
  const errors: FormErrors = {}
  const minorUnit = minorUnitOf(reference, values.currency_code)
  const department = reference.departments.find((d) => d.name === values.department)

  if (!CODE_PATTERN.test(values.employee_code)) {
    errors.employee_code = 'Use the format ACME-000123'
  }
  const name = values.full_name.trim()
  if (!name) {
    errors.full_name = 'Full name is required'
  } else if (name.length > 120) {
    errors.full_name = 'Keep the name under 120 characters'
  }
  if (!EMAIL_PATTERN.test(values.email.trim())) {
    errors.email = 'Enter a valid email address'
  }
  if (!department) {
    errors.department = 'Choose a department'
  } else if (!department.job_titles.includes(values.job_title)) {
    errors.job_title = `Choose a job title in ${department.name}`
  }
  if (!reference.countries.some((c) => c.code === values.country_code)) {
    errors.country_code = 'Choose a country'
  }
  if (!reference.currencies.some((c) => c.code === values.currency_code)) {
    errors.currency_code = 'Choose a currency'
  }

  const salary = parseMajorToMinor(values.salary, minorUnit)
  if (salary === null || salary <= 0) {
    errors.salary = 'Enter an annual salary greater than zero'
  } else if (salary > MAX_MINOR_AMOUNT) {
    errors.salary = 'That salary looks too large'
  }
  if (values.bonus.trim()) {
    const bonus = parseMajorToMinor(values.bonus, minorUnit)
    if (bonus === null) {
      errors.bonus = 'Enter a bonus of zero or more, or leave it empty'
    } else if (bonus > MAX_MINOR_AMOUNT) {
      errors.bonus = 'That bonus looks too large'
    }
  }
  if (!values.employment_type) {
    errors.employment_type = 'Choose an employment type'
  }
  if (!values.hire_date) {
    errors.hire_date = 'Hire date is required'
  } else if (values.hire_date > today) {
    errors.hire_date = 'Hire date cannot be in the future'
  }
  return errors
}

export function toEmployeeInput(values: EmployeeFormValues, reference: Reference): EmployeeInput {
  const minorUnit = minorUnitOf(reference, values.currency_code)
  return {
    employee_code: values.employee_code,
    full_name: values.full_name.trim(),
    email: values.email.trim(),
    department: values.department,
    job_title: values.job_title,
    country_code: values.country_code,
    currency_code: values.currency_code,
    salary_minor: parseMajorToMinor(values.salary, minorUnit) ?? 0,
    bonus_minor: values.bonus.trim() ? parseMajorToMinor(values.bonus, minorUnit) : null,
    employment_type: values.employment_type || 'full_time',
    hire_date: values.hire_date,
  }
}

export function fieldForServerError(field: string): keyof EmployeeFormValues | null {
  const mapping: Record<string, keyof EmployeeFormValues> = {
    salary_minor: 'salary',
    bonus_minor: 'bonus',
  }
  if (field in mapping) {
    return mapping[field]
  }
  return field in EMPTY_FORM ? (field as keyof EmployeeFormValues) : null
}
