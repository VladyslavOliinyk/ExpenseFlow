import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { ChevronDown, Users, LogOut } from 'lucide-react'
import { fetchAllUsers, loginAs, fetchMe } from '@/api/auth'
import { useAuthStore } from '@/store/authStore'
import { Button } from '@/components/ui/button'

export function UserSwitcher() {
  const [open, setOpen] = useState(false)
  const { setAuth, clearAuth, user: currentUser } = useAuthStore()

  function handleSignOut() {
    clearAuth()
    window.location.href = '/login'
  }

  const { data: users = [] } = useQuery({
    queryKey: ['all-users'],
    queryFn: fetchAllUsers,
    staleTime: Infinity,
  })

  async function handleSwitch(userId: number) {
    const { access_token } = await loginAs(userId)
    useAuthStore.setState({ token: access_token })
    const user = await fetchMe()
    setAuth(access_token, user)
    setOpen(false)
    window.location.reload()
  }

  return (
    <div className="relative">
      <Button
        variant="outline"
        size="sm"
        onClick={() => setOpen((o) => !o)}
        className="flex items-center gap-2"
      >
        <Users className="h-4 w-4" />
        {currentUser ? (
          <span>
            <span className="font-semibold">{currentUser.name}</span>
            {currentUser.managed_category_names.length > 0 && (
              <span className="text-gray-400 ml-1 text-xs">
                (mgr: {currentUser.managed_category_names.join(', ')})
              </span>
            )}
          </span>
        ) : (
          'Select user'
        )}
        <ChevronDown className="h-3 w-3 opacity-50" />
      </Button>

      {open && (
        <>
          <div className="fixed inset-0 z-40" onClick={() => setOpen(false)} />
          <div className="absolute right-0 z-50 mt-1 w-80 rounded-md border bg-white shadow-lg py-1">
            <p className="px-3 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wide">
              Sign in as…
            </p>
            {users.map((u) => (
              <button
                key={u.id}
                onClick={() => handleSwitch(u.id)}
                className="w-full text-left px-3 py-2 hover:bg-gray-50 flex flex-col"
              >
                <span className="font-medium text-sm">{u.name}</span>
                <span className="text-xs text-gray-500">
                  {u.managed_category_names.length > 0
                    ? `Manager of: ${u.managed_category_names.join(', ')}`
                    : 'Employee (no managed categories)'}
                </span>
              </button>
            ))}
            <div className="border-t my-1" />
            <button
              onClick={handleSignOut}
              className="w-full text-left px-3 py-2 hover:bg-gray-50 flex items-center gap-2 text-sm text-gray-600"
            >
              <LogOut className="h-3.5 w-3.5" />
              Sign out
            </button>
          </div>
        </>
      )}
    </div>
  )
}
