import { type FormEvent, type ReactNode, useState } from 'react'
import { ApiError } from '@/api/client'
import { useCreateEmployee, useUpdateEmployee } from '@/api/hooks'
import type { Employee, Reference } from '@/api/types'
import { NativeSelect } from '@/components/NativeSelect'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  EMPTY_FORM,
  type EmployeeFormValues,
  type FormErrors,
  fieldForServerError,
  formValuesFrom,
  toEmployeeInput,
  toEmployeeUpdate,
  validateEmployeeForm,
} from './form'
import { EMPLOYMENT_TYPE_LABELS } from './labels'

interface Props {
  open: boolean
  onOpenChange: (open: boolean) => void
  reference: Reference
  employee?: Employee
  today?: string
}

export function EmployeeFormDialog({ open, onOpenChange, reference, employee, today }: Props) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-h-[90vh] overflow-y-auto sm:max-w-2xl">
        <DialogHeader>
          <DialogTitle>{employee ? `Edit ${employee.full_name}` : 'Add employee'}</DialogTitle>
          <DialogDescription>
            Salaries are annual gross base pay in the employee’s pay currency.
          </DialogDescription>
        </DialogHeader>
        {open && (
          <EmployeeForm
            key={employee?.id ?? 'new'}
            reference={reference}
            employee={employee}
            today={today ?? new Date().toISOString().slice(0, 10)}
            onDone={() => onOpenChange(false)}
          />
        )}
      </DialogContent>
    </Dialog>
  )
}

function EmployeeForm({
  reference,
  employee,
  today,
  onDone,
}: {
  reference: Reference
  employee?: Employee
  today: string
  onDone: () => void
}) {
  const [values, setValues] = useState<EmployeeFormValues>(() =>
    employee ? formValuesFrom(employee, reference) : EMPTY_FORM,
  )
  const [errors, setErrors] = useState<FormErrors>({})
  const [formError, setFormError] = useState<string | null>(null)
  const create = useCreateEmployee()
  const update = useUpdateEmployee()
  const saving = create.isPending || update.isPending

  const titles = reference.departments.find((d) => d.name === values.department)?.job_titles ?? []

  function set<K extends keyof EmployeeFormValues>(field: K, value: EmployeeFormValues[K]) {
    setValues((current) => ({ ...current, [field]: value }))
    setErrors((current) => ({ ...current, [field]: undefined }))
  }

  function changeCountry(code: string) {
    const localCurrency = reference.countries.find((c) => c.code === code)?.currency_code ?? ''
    setValues((current) => ({ ...current, country_code: code, currency_code: localCurrency }))
    setErrors((current) => ({ ...current, country_code: undefined, currency_code: undefined }))
  }

  function changeDepartment(name: string) {
    setValues((current) => ({ ...current, department: name, job_title: '' }))
    setErrors((current) => ({ ...current, department: undefined, job_title: undefined }))
  }

  async function submit(event: FormEvent) {
    event.preventDefault()
    setFormError(null)
    const found = validateEmployeeForm(values, reference, today)
    if (Object.keys(found).length > 0) {
      setErrors(found)
      return
    }
    try {
      if (employee) {
        await update.mutateAsync({ id: employee.id, changes: toEmployeeUpdate(values, reference) })
      } else {
        await create.mutateAsync(toEmployeeInput(values, reference))
      }
      onDone()
    } catch (error) {
      showServerError(error)
    }
  }

  function showServerError(error: unknown) {
    if (!(error instanceof ApiError)) {
      setFormError('Could not reach the server. Please try again.')
      return
    }
    const mapped: FormErrors = {}
    for (const [field, message] of Object.entries(error.fields)) {
      const formField = fieldForServerError(field)
      if (formField) {
        mapped[formField] = message
      }
    }
    setErrors(mapped)
    setFormError(error.message)
  }

  return (
    <form onSubmit={submit} noValidate className="grid gap-4 sm:grid-cols-2">
      {formError && (
        <p role="alert" className="text-sm text-destructive sm:col-span-2">
          {formError}
        </p>
      )}
      <Field label="Employee code" name="employee_code" error={errors.employee_code}>
        <Input
          id="employee_code"
          value={values.employee_code}
          onChange={(e) => set('employee_code', e.target.value.toUpperCase())}
          placeholder="ACME-000123"
          disabled={Boolean(employee)}
          aria-invalid={Boolean(errors.employee_code)}
        />
      </Field>
      <Field label="Full name" name="full_name" error={errors.full_name}>
        <Input
          id="full_name"
          value={values.full_name}
          onChange={(e) => set('full_name', e.target.value)}
          aria-invalid={Boolean(errors.full_name)}
        />
      </Field>
      <Field label="Work email" name="email" error={errors.email}>
        <Input
          id="email"
          type="email"
          value={values.email}
          onChange={(e) => set('email', e.target.value)}
          aria-invalid={Boolean(errors.email)}
        />
      </Field>
      <Field label="Employment type" name="employment_type" error={errors.employment_type}>
        <NativeSelect
          id="employment_type"
          value={values.employment_type}
          onChange={(e) =>
            set('employment_type', e.target.value as EmployeeFormValues['employment_type'])
          }
        >
          {reference.employment_types.map((type) => (
            <option key={type} value={type}>
              {EMPLOYMENT_TYPE_LABELS[type]}
            </option>
          ))}
        </NativeSelect>
      </Field>
      <Field label="Department" name="department" error={errors.department}>
        <NativeSelect
          id="department"
          value={values.department}
          onChange={(e) => changeDepartment(e.target.value)}
          aria-invalid={Boolean(errors.department)}
        >
          <option value="">Choose…</option>
          {reference.departments.map((d) => (
            <option key={d.name}>{d.name}</option>
          ))}
        </NativeSelect>
      </Field>
      <Field label="Job title" name="job_title" error={errors.job_title}>
        <NativeSelect
          id="job_title"
          value={values.job_title}
          onChange={(e) => set('job_title', e.target.value)}
          disabled={!values.department}
          aria-invalid={Boolean(errors.job_title)}
        >
          <option value="">Choose…</option>
          {titles.map((title) => (
            <option key={title}>{title}</option>
          ))}
        </NativeSelect>
      </Field>
      <Field label="Country" name="country_code" error={errors.country_code}>
        <NativeSelect
          id="country_code"
          value={values.country_code}
          onChange={(e) => changeCountry(e.target.value)}
          aria-invalid={Boolean(errors.country_code)}
        >
          <option value="">Choose…</option>
          {reference.countries.map((c) => (
            <option key={c.code} value={c.code}>
              {c.name}
            </option>
          ))}
        </NativeSelect>
      </Field>
      <Field label="Pay currency" name="currency_code" error={errors.currency_code}>
        <NativeSelect
          id="currency_code"
          value={values.currency_code}
          onChange={(e) => set('currency_code', e.target.value)}
          aria-invalid={Boolean(errors.currency_code)}
        >
          <option value="">Choose…</option>
          {reference.currencies.map((c) => (
            <option key={c.code}>{c.code}</option>
          ))}
        </NativeSelect>
      </Field>
      <Field
        label={`Annual salary${suffix(values.currency_code)}`}
        name="salary"
        error={errors.salary}
      >
        <Input
          id="salary"
          inputMode="decimal"
          value={values.salary}
          onChange={(e) => set('salary', e.target.value)}
          aria-invalid={Boolean(errors.salary)}
        />
      </Field>
      <Field
        label={`Annual bonus${suffix(values.currency_code)} (optional)`}
        name="bonus"
        error={errors.bonus}
      >
        <Input
          id="bonus"
          inputMode="decimal"
          value={values.bonus}
          onChange={(e) => set('bonus', e.target.value)}
          aria-invalid={Boolean(errors.bonus)}
        />
      </Field>
      <Field label="Hire date" name="hire_date" error={errors.hire_date}>
        <Input
          id="hire_date"
          type="date"
          max={today}
          value={values.hire_date}
          onChange={(e) => set('hire_date', e.target.value)}
          aria-invalid={Boolean(errors.hire_date)}
        />
      </Field>
      <DialogFooter className="sm:col-span-2">
        <Button type="button" variant="outline" onClick={onDone}>
          Cancel
        </Button>
        <Button type="submit" disabled={saving}>
          {saving ? 'Saving…' : employee ? 'Save changes' : 'Add employee'}
        </Button>
      </DialogFooter>
    </form>
  )
}

function suffix(currency: string): string {
  return currency ? ` (${currency})` : ''
}

function Field({
  label,
  name,
  error,
  children,
}: {
  label: string
  name: string
  error?: string
  children: ReactNode
}) {
  return (
    <div className="grid gap-1.5">
      <Label htmlFor={name}>{label}</Label>
      {children}
      {error && (
        <p id={`${name}-error`} className="text-xs text-destructive">
          {error}
        </p>
      )}
    </div>
  )
}
