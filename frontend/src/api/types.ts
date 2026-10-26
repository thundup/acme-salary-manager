export type EmploymentType = 'full_time' | 'part_time' | 'contractor'
export type EmployeeStatus = 'active' | 'terminated'

export interface Employee {
  id: number
  employee_code: string
  full_name: string
  email: string
  job_title: string
  department: string
  country_code: string
  currency_code: string
  salary_minor: number
  bonus_minor: number | null
  employment_type: EmploymentType
  hire_date: string
  status: EmployeeStatus
  terminated_at: string | null
  created_at: string
  updated_at: string
}

export interface EmployeeInput {
  employee_code: string
  full_name: string
  email: string
  job_title: string
  department: string
  country_code: string
  currency_code: string
  salary_minor: number
  bonus_minor: number | null
  employment_type: EmploymentType
  hire_date: string
}

export type EmployeeUpdate = Partial<Omit<EmployeeInput, 'employee_code'>>

export interface EmployeePage {
  items: Employee[]
  total: number
  page: number
  page_size: number
}

export type SortColumn =
  | 'full_name'
  | 'email'
  | 'employee_code'
  | 'job_title'
  | 'department'
  | 'country_code'
  | 'salary_minor'
  | 'hire_date'

export interface EmployeeListParams {
  page: number
  pageSize: number
  sort: SortColumn
  order: 'asc' | 'desc'
  q?: string
  country?: string
  department?: string
  jobTitle?: string
  status?: EmployeeStatus | 'all'
}

export interface Reference {
  countries: { code: string; name: string; currency_code: string }[]
  currencies: { code: string; minor_unit: number }[]
  departments: { name: string; job_titles: string[] }[]
  employment_types: EmploymentType[]
  reporting_currency: string
}

export interface Money {
  amount_minor: number
  currency: string
}

export interface CountryStats {
  country_code: string
  country_name: string
  currency_code: string
  headcount: number
  min: Money
  max: Money
  average: Money
  median: Money
}

export interface GroupStats {
  key: string
  headcount: number
  min: Money
  max: Money
  average: Money
}

export interface Distribution {
  country_code: string
  currency_code: string
  buckets: { lower_minor: number; upper_minor: number; count: number }[]
}

export interface OrgSummary {
  headcount: number
  total_salary: Money
  total_bonus: Money
  average_salary: Money
  approximate: boolean
  rates_as_of: string | null
}
