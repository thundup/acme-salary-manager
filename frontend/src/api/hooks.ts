import { keepPreviousData, useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { apiFetch, toQueryString } from './client'
import type {
  CountryStats,
  Distribution,
  Employee,
  EmployeeInput,
  EmployeeListParams,
  EmployeePage,
  EmployeeUpdate,
  GroupStats,
  OrgSummary,
  Reference,
} from './types'

export const queryKeys = {
  reference: ['reference'] as const,
  employees: ['employees'] as const,
  employeeList: (params: EmployeeListParams) => ['employees', 'list', params] as const,
  insights: ['insights'] as const,
}

export function useReference() {
  return useQuery({
    queryKey: queryKeys.reference,
    queryFn: () => apiFetch<Reference>('/reference'),
    staleTime: Infinity,
  })
}

export function useEmployees(params: EmployeeListParams) {
  return useQuery({
    queryKey: queryKeys.employeeList(params),
    queryFn: () =>
      apiFetch<EmployeePage>(
        `/employees${toQueryString({
          page: params.page,
          page_size: params.pageSize,
          sort: params.sort,
          order: params.order,
          q: params.q,
          country: params.country,
          department: params.department,
          job_title: params.jobTitle,
          status: params.status,
        })}`,
      ),
    placeholderData: keepPreviousData,
  })
}

function useInvalidateEmployeeData() {
  const queryClient = useQueryClient()
  return () =>
    Promise.all([
      queryClient.invalidateQueries({ queryKey: queryKeys.employees }),
      queryClient.invalidateQueries({ queryKey: queryKeys.insights }),
    ])
}

export function useCreateEmployee() {
  const invalidate = useInvalidateEmployeeData()
  return useMutation({
    mutationFn: (input: EmployeeInput) =>
      apiFetch<Employee>('/employees', { method: 'POST', body: JSON.stringify(input) }),
    onSuccess: invalidate,
  })
}

export function useUpdateEmployee() {
  const invalidate = useInvalidateEmployeeData()
  return useMutation({
    mutationFn: ({ id, changes }: { id: number; changes: EmployeeUpdate }) =>
      apiFetch<Employee>(`/employees/${id}`, { method: 'PATCH', body: JSON.stringify(changes) }),
    onSuccess: invalidate,
  })
}

export function useDeleteEmployee() {
  const invalidate = useInvalidateEmployeeData()
  return useMutation({
    mutationFn: (id: number) => apiFetch<void>(`/employees/${id}`, { method: 'DELETE' }),
    onSuccess: invalidate,
  })
}

export function useCountryStats() {
  return useQuery({
    queryKey: [...queryKeys.insights, 'countries'],
    queryFn: () => apiFetch<CountryStats[]>('/insights/countries'),
  })
}

export function useOrgSummary() {
  return useQuery({
    queryKey: [...queryKeys.insights, 'summary'],
    queryFn: () => apiFetch<OrgSummary>('/insights/summary'),
  })
}

export function useBreakdown(
  country: string | undefined,
  currency: string | undefined,
  by: 'job_title' | 'department',
) {
  return useQuery({
    queryKey: [...queryKeys.insights, 'breakdown', country, currency, by],
    queryFn: () =>
      apiFetch<GroupStats[]>(
        `/insights/countries/${country}/breakdown${toQueryString({ by, currency })}`,
      ),
    enabled: Boolean(country),
  })
}

export function useDistribution(country: string | undefined, currency: string | undefined) {
  return useQuery({
    queryKey: [...queryKeys.insights, 'distribution', country, currency],
    queryFn: () =>
      apiFetch<Distribution>(
        `/insights/countries/${country}/distribution${toQueryString({ currency, buckets: 12 })}`,
      ),
    enabled: Boolean(country),
  })
}
