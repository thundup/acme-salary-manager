import { lazy, Suspense } from 'react'
import { NavLink, Navigate, Route, Routes } from 'react-router'
import { EmployeesPage } from '@/features/employees/EmployeesPage'
import { Skeleton } from '@/components/ui/skeleton'
import { cn } from '@/lib/utils'

const InsightsPage = lazy(() =>
  import('@/features/insights/InsightsPage').then((m) => ({ default: m.InsightsPage })),
)

const NAV = [
  { to: '/employees', label: 'Employees' },
  { to: '/insights', label: 'Insights' },
]

export default function App() {
  return (
    <div className="flex min-h-screen flex-col bg-muted/40 text-foreground">
      <header className="sticky top-0 z-10 border-b bg-background/85 backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center gap-6 px-4 py-3">
          <span className="flex items-center gap-2 font-semibold">
            <span
              aria-hidden="true"
              className="grid size-7 place-items-center rounded-md bg-primary text-sm text-primary-foreground"
            >
              A
            </span>
            ACME Salary Manager
          </span>
          <nav aria-label="Main" className="flex gap-1">
            {NAV.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  cn(
                    'rounded-md px-3 py-1.5 text-sm text-muted-foreground hover:text-foreground',
                    isActive && 'bg-primary/10 font-medium text-primary',
                  )
                }
              >
                {item.label}
              </NavLink>
            ))}
          </nav>
        </div>
      </header>
      <main className="mx-auto w-full max-w-7xl flex-1 px-4 py-8">
        <Routes>
          <Route path="/" element={<Navigate to="/employees" replace />} />
          <Route path="/employees" element={<EmployeesPage />} />
          <Route
            path="/insights"
            element={
              <Suspense fallback={<Skeleton className="h-96 w-full" />}>
                <InsightsPage />
              </Suspense>
            }
          />
          <Route path="*" element={<Navigate to="/employees" replace />} />
        </Routes>
      </main>
      <footer className="border-t bg-background py-4 text-center text-xs text-muted-foreground">
        ACME Salary Manager · demo with synthetic data
      </footer>
    </div>
  )
}
