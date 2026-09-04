import { useQuery } from '@tanstack/react-query'
import { fetchAllUsers, loginAs, fetchMe } from '@/api/auth'
import { useAuthStore } from '@/store/authStore'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

export function LoginPage() {
  const { setAuth } = useAuthStore()

  const { data: users = [], isLoading } = useQuery({
    queryKey: ['all-users'],
    queryFn: fetchAllUsers,
  })

  async function handleLogin(userId: number) {
    const { access_token } = await loginAs(userId)
    useAuthStore.setState({ token: access_token })
    const user = await fetchMe()
    setAuth(access_token, user)
    window.location.href = '/claims'
  }

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">ExpenseFlow</h1>
          <p className="text-gray-500 mt-2">Demo — select a user to continue</p>
        </div>
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Sign in as…</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {isLoading && <p className="text-sm text-gray-400">Loading users…</p>}
            {users.map((u) => (
              <button
                key={u.id}
                onClick={() => handleLogin(u.id)}
                className="w-full text-left rounded-md border border-gray-200 p-3 hover:bg-gray-50 hover:border-blue-300 transition-colors"
              >
                <p className="font-medium text-gray-900">{u.name}</p>
                <p className="text-xs text-gray-500">{u.email}</p>
                {u.managed_category_names.length > 0 && (
                  <p className="text-xs text-blue-600 mt-0.5">
                    Manager: {u.managed_category_names.join(', ')}
                  </p>
                )}
              </button>
            ))}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
