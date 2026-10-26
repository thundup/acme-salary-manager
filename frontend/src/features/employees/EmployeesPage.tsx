import { useState } from 'react'
import { useEmployees, useReference } from '@/api/hooks'
import type { Employee, EmployeeStatus, SortColumn } from '@/api/types'
import { NativeSelect } from '@/components/NativeSelect'
import { EmptyState, ErrorState } from '@/components/states'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import { useDebouncedValue } from '@/lib/useDebouncedValue'
import { DeleteEmployeeDialog } from './DeleteEmployeeDialog'
import { EmployeeFormDialog } from './EmployeeFormDialog'
import { EmployeeTable, type SortState } from './EmployeeTable'

const PAGE_SIZES = [10, 25, 50, 100]

interface Filters {
  q: string
  country: string
  department: string
  jobTitle: string
  status: EmployeeStatus | 'all'
}

const NO_FILTERS: Filters = { q: '', country: '', department: '', jobTitle: '', status: 'active' }

export function EmployeesPage() {
  const reference = useReference()
  const [filters, setFilters] = useState<Filters>(NO_FILTERS)
  const [sort, setSort] = useState<SortState>({ column: 'full_name', order: 'asc' })
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(25)
  const [editing, setEditing] = useState<Employee | undefined>()
  const [formOpen, setFormOpen] = useState(false)
  const [removing, setRemoving] = useState<Employee | null>(null)
  const q = useDebouncedValue(filters.q.trim())

  const employees = useEmployees({
    page,
    pageSize,
    sort: sort.column,
    order: sort.order,
    q: q || undefined,
    country: filters.country || undefined,
    department: filters.department || undefined,
    jobTitle: filters.jobTitle || undefined,
    status: filters.status,
  })

  function updateFilter<K extends keyof Filters>(key: K, value: Filters[K]) {
    setFilters((current) => ({
      ...current,
      [key]: value,
      ...(key === 'department' ? { jobTitle: '' } : {}),
    }))
    setPage(1)
  }

  function toggleSort(column: SortColumn) {
    setSort((current) => ({
      column,
      order: current.column === column && current.order === 'asc' ? 'desc' : 'asc',
    }))
    setPage(1)
  }

  const titles = filters.department
    ? (reference.data?.departments.find((d) => d.name === filters.department)?.job_titles ?? [])
    : (reference.data?.departments.flatMap((d) => d.job_titles) ?? [])
  const total = employees.data?.total ?? 0
  const lastPage = Math.max(1, Math.ceil(total / pageSize))
  const firstRow = total === 0 ? 0 : (page - 1) * pageSize + 1
  const hasFilters = JSON.stringify(filters) !== JSON.stringify(NO_FILTERS)

  return (
    <section className="space-y-4">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Employees</h1>
          <p className="text-sm text-muted-foreground">
            Salaries are shown in each employee’s pay currency. Filter by country to compare pay.
          </p>
        </div>
        <Button
          onClick={() => {
            setEditing(undefined)
            setFormOpen(true)
          }}
          disabled={!reference.data}
        >
          Add employee
        </Button>
      </div>

      <div className="grid gap-2 rounded-xl border bg-card p-3 shadow-sm sm:grid-cols-2 lg:grid-cols-5">
        <Input
          type="search"
          placeholder="Search name or email"
          aria-label="Search name or email"
          value={filters.q}
          onChange={(e) => updateFilter('q', e.target.value)}
        />
        <NativeSelect
          aria-label="Country"
          value={filters.country}
          onChange={(e) => updateFilter('country', e.target.value)}
        >
          <option value="">All countries</option>
          {reference.data?.countries.map((c) => (
            <option key={c.code} value={c.code}>
              {c.name}
            </option>
          ))}
        </NativeSelect>
        <NativeSelect
          aria-label="Department"
          value={filters.department}
          onChange={(e) => updateFilter('department', e.target.value)}
        >
          <option value="">All departments</option>
          {reference.data?.departments.map((d) => (
            <option key={d.name}>{d.name}</option>
          ))}
        </NativeSelect>
        <NativeSelect
          aria-label="Job title"
          value={filters.jobTitle}
          onChange={(e) => updateFilter('jobTitle', e.target.value)}
        >
          <option value="">All job titles</option>
          {titles.map((title) => (
            <option key={title}>{title}</option>
          ))}
        </NativeSelect>
        <NativeSelect
          aria-label="Status"
          value={filters.status}
          onChange={(e) => updateFilter('status', e.target.value as Filters['status'])}
        >
          <option value="active">Active</option>
          <option value="terminated">Terminated</option>
          <option value="all">All statuses</option>
        </NativeSelect>
      </div>

      {employees.isError || reference.isError ? (
        <ErrorState
          message={(employees.error ?? reference.error)?.message ?? 'Unknown error'}
          onRetry={() => {
            void employees.refetch()
            void reference.refetch()
          }}
        />
      ) : !employees.data || !reference.data ? (
        <div className="space-y-2" aria-label="Loading employees">
          {Array.from({ length: 8 }, (_, i) => (
            <Skeleton key={i} className="h-12 w-full" />
          ))}
        </div>
      ) : employees.data.items.length === 0 ? (
        <EmptyState title="No employees match">
          {hasFilters ? (
            <Button
              variant="link"
              onClick={() => {
                setFilters(NO_FILTERS)
                setPage(1)
              }}
            >
              Clear filters
            </Button>
          ) : (
            'Add your first employee to get started.'
          )}
        </EmptyState>
      ) : (
        <div
          className={`overflow-hidden rounded-xl border bg-card shadow-sm transition-opacity ${employees.isPlaceholderData ? 'opacity-60' : ''}`}
        >
          <EmployeeTable
            employees={employees.data.items}
            reference={reference.data}
            sort={sort}
            onSort={toggleSort}
            onEdit={(employee) => {
              setEditing(employee)
              setFormOpen(true)
            }}
            onDelete={setRemoving}
          />
        </div>
      )}

      <nav
        aria-label="Pagination"
        className="flex flex-wrap items-center justify-between gap-3 text-sm"
      >
        <p className="text-muted-foreground" aria-live="polite">
          Showing {firstRow.toLocaleString()}–{Math.min(page * pageSize, total).toLocaleString()} of{' '}
          {total.toLocaleString()}
        </p>
        <div className="flex items-center gap-2">
          <label className="flex items-center gap-2 text-muted-foreground">
            Rows
            <NativeSelect
              className="w-20"
              value={pageSize}
              onChange={(e) => {
                setPageSize(Number(e.target.value))
                setPage(1)
              }}
            >
              {PAGE_SIZES.map((size) => (
                <option key={size}>{size}</option>
              ))}
            </NativeSelect>
          </label>
          <Button
            variant="outline"
            size="sm"
            disabled={page <= 1}
            onClick={() => setPage(page - 1)}
          >
            Previous
          </Button>
          <span className="tabular-nums">
            Page {page} of {lastPage}
          </span>
          <Button
            variant="outline"
            size="sm"
            disabled={page >= lastPage}
            onClick={() => setPage(page + 1)}
          >
            Next
          </Button>
        </div>
      </nav>

      {reference.data && (
        <EmployeeFormDialog
          open={formOpen}
          onOpenChange={setFormOpen}
          reference={reference.data}
          employee={editing}
        />
      )}
      <DeleteEmployeeDialog employee={removing} onClose={() => setRemoving(null)} />
    </section>
  )
}
