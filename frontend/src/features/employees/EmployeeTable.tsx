import type { Employee, Reference, SortColumn } from '@/api/types'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { flagEmoji, initials } from '@/lib/display'
import { formatMoney } from '@/lib/money'
import { minorUnitOf } from './form'
import { EMPLOYMENT_TYPE_LABELS } from './labels'

export interface SortState {
  column: SortColumn
  order: 'asc' | 'desc'
}

interface Props {
  employees: Employee[]
  reference: Reference
  sort: SortState
  onSort: (column: SortColumn) => void
  onEdit: (employee: Employee) => void
  onDelete: (employee: Employee) => void
}

const COLUMNS: { key: SortColumn; label: string; align?: 'right' }[] = [
  { key: 'employee_code', label: 'Code' },
  { key: 'full_name', label: 'Name' },
  { key: 'job_title', label: 'Job title' },
  { key: 'department', label: 'Department' },
  { key: 'country_code', label: 'Country' },
  { key: 'salary_minor', label: 'Annual salary', align: 'right' },
  { key: 'hire_date', label: 'Hired' },
]

export function EmployeeTable({ employees, reference, sort, onSort, onEdit, onDelete }: Props) {
  const countryName = (code: string) =>
    reference.countries.find((c) => c.code === code)?.name ?? code

  return (
    <Table>
      <TableHeader className="bg-muted/60">
        <TableRow className="hover:bg-transparent">
          {COLUMNS.map((column) => {
            const active = sort.column === column.key
            return (
              <TableHead
                key={column.key}
                aria-sort={active ? (sort.order === 'asc' ? 'ascending' : 'descending') : 'none'}
                className={column.align === 'right' ? 'text-right' : undefined}
              >
                <button
                  type="button"
                  onClick={() => onSort(column.key)}
                  className="inline-flex items-center gap-1 font-medium hover:text-foreground"
                >
                  {column.label}
                  <span aria-hidden="true" className="text-xs text-muted-foreground">
                    {active ? (sort.order === 'asc' ? '▲' : '▼') : '↕'}
                  </span>
                </button>
              </TableHead>
            )
          })}
          <TableHead>
            <span className="sr-only">Actions</span>
          </TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {employees.map((employee) => {
          const minorUnit = minorUnitOf(reference, employee.currency_code)
          const terminated = employee.status === 'terminated'
          return (
            <TableRow
              key={employee.id}
              className={terminated ? 'text-muted-foreground' : undefined}
            >
              <TableCell className="font-mono text-xs">{employee.employee_code}</TableCell>
              <TableCell>
                <div className="flex items-center gap-3">
                  <span
                    aria-hidden="true"
                    className="grid size-8 shrink-0 place-items-center rounded-full bg-primary/10 text-xs font-semibold text-primary"
                  >
                    {initials(employee.full_name)}
                  </span>
                  <div>
                    <div className="font-medium">{employee.full_name}</div>
                    <div className="text-xs text-muted-foreground">{employee.email}</div>
                  </div>
                </div>
              </TableCell>
              <TableCell>
                <div>{employee.job_title}</div>
                {employee.employment_type !== 'full_time' && (
                  <Badge variant="outline" className="mt-1">
                    {EMPLOYMENT_TYPE_LABELS[employee.employment_type]}
                  </Badge>
                )}
              </TableCell>
              <TableCell>{employee.department}</TableCell>
              <TableCell className="whitespace-nowrap">
                <span aria-hidden="true" className="mr-1.5">
                  {flagEmoji(employee.country_code)}
                </span>
                {countryName(employee.country_code)}
              </TableCell>
              <TableCell className="text-right tabular-nums">
                <div>{formatMoney(employee.salary_minor, employee.currency_code, minorUnit)}</div>
                {employee.bonus_minor !== null && (
                  <div className="text-xs text-muted-foreground">
                    + {formatMoney(employee.bonus_minor, employee.currency_code, minorUnit)} bonus
                  </div>
                )}
              </TableCell>
              <TableCell className="tabular-nums">{employee.hire_date}</TableCell>
              <TableCell className="text-right">
                {terminated ? (
                  <Badge variant="secondary">Terminated</Badge>
                ) : (
                  <div className="flex justify-end gap-1">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => onEdit(employee)}
                      aria-label={`Edit ${employee.full_name}`}
                    >
                      Edit
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="text-destructive"
                      onClick={() => onDelete(employee)}
                      aria-label={`Remove ${employee.full_name}`}
                    >
                      Remove
                    </Button>
                  </div>
                )}
              </TableCell>
            </TableRow>
          )
        })}
      </TableBody>
    </Table>
  )
}
