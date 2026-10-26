import { useDeleteEmployee } from '@/api/hooks'
import type { Employee } from '@/api/types'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog'

interface Props {
  employee: Employee | null
  onClose: () => void
}

export function DeleteEmployeeDialog({ employee, onClose }: Props) {
  const remove = useDeleteEmployee()

  async function confirm() {
    if (employee) {
      await remove.mutateAsync(employee.id)
    }
    onClose()
  }

  return (
    <AlertDialog open={employee !== null} onOpenChange={(open) => !open && onClose()}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Remove {employee?.full_name}?</AlertDialogTitle>
          <AlertDialogDescription>
            They will be marked as terminated, hidden from the employee list and excluded from
            insights. Their record is kept.
          </AlertDialogDescription>
        </AlertDialogHeader>
        {remove.isError && (
          <p role="alert" className="text-sm text-destructive">
            Could not remove this employee. Please try again.
          </p>
        )}
        <AlertDialogFooter>
          <AlertDialogCancel>Cancel</AlertDialogCancel>
          <AlertDialogAction
            variant="destructive"
            disabled={remove.isPending}
            onClick={(event) => {
              event.preventDefault()
              void confirm()
            }}
          >
            {remove.isPending ? 'Removing…' : 'Remove employee'}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  )
}
