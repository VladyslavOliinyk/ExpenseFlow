import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useAuthStore } from '@/store/authStore'
import { Layout } from '@/components/Layout'
import { LoginPage } from '@/pages/LoginPage'
import { NewClaimPage } from '@/pages/NewClaimPage'
import { MyClaimsPage } from '@/pages/MyClaimsPage'
import { QueuePage } from '@/pages/QueuePage'
import { ClaimDetailPage } from '@/pages/ClaimDetailPage'
import { AiMetricsDashboard } from '@/pages/AiMetricsDashboard'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 10_000,
    },
  },
})

function isTokenExpired(token: string): boolean {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]))
    return payload.exp * 1000 < Date.now()
  } catch {
    return true
  }
}

function RequireAuth({ children }: { children: React.ReactNode }) {
  const { token, clearAuth } = useAuthStore()
  if (!token || isTokenExpired(token)) {
    if (token) clearAuth()
    return <Navigate to="/login" replace />
  }
  return <>{children}</>
}

export function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route
            path="/*"
            element={
              <RequireAuth>
                <Layout>
                  <Routes>
                    <Route path="/" element={<Navigate to="/claims" replace />} />
                    <Route path="/claims" element={<MyClaimsPage />} />
                    <Route path="/claims/new" element={<NewClaimPage />} />
                    <Route path="/claims/:id" element={<ClaimDetailPage />} />
                    <Route path="/queue" element={<QueuePage />} />
                    <Route path="/metrics" element={<AiMetricsDashboard />} />
                  </Routes>
                </Layout>
              </RequireAuth>
            }
          />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  )
}

export default App
