import { Link, useLocation } from 'react-router-dom'
import { FileText, Inbox, PlusCircle, BarChart2 } from 'lucide-react'
import { UserSwitcher } from './UserSwitcher'
import { useAuthStore } from '@/store/authStore'
import { cn } from '@/lib/utils'

interface Props {
  children: React.ReactNode
}

export function Layout({ children }: Props) {
  const location = useLocation()
  const user = useAuthStore((s) => s.user)
  const isManager = user && user.managed_category_ids.length > 0

  const navItems = [
    { to: '/claims/new', label: 'New Claim', icon: PlusCircle },
    { to: '/claims', label: 'My Claims', icon: FileText },
    ...(isManager ? [{ to: '/queue', label: 'Queue', icon: Inbox }] : []),
    { to: '/metrics', label: 'AI Metrics', icon: BarChart2 },
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b sticky top-0 z-30">
        <div className="max-w-5xl mx-auto px-4 h-14 flex items-center justify-between">
          <div className="flex items-center gap-6">
            <Link to="/" className="font-bold text-gray-900 text-lg">
              ExpenseFlow
            </Link>
            {user && (
              <nav className="flex items-center gap-1">
                {navItems.map(({ to, label, icon: Icon }) => (
                  <Link
                    key={to}
                    to={to}
                    className={cn(
                      'flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm font-medium transition-colors',
                      location.pathname === to || location.pathname.startsWith(to + '/')
                        ? 'bg-blue-50 text-blue-700'
                        : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                    )}
                  >
                    <Icon className="h-4 w-4" />
                    {label}
                  </Link>
                ))}
              </nav>
            )}
          </div>
          <UserSwitcher />
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-4 py-6">{children}</main>
    </div>
  )
}
