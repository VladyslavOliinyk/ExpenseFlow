import { useQuery } from '@tanstack/react-query'
import { fetchMe } from '@/api/auth'
import { useAuthStore } from '@/store/authStore'

export function useCurrentUser() {
  const token = useAuthStore((s) => s.token)
  return useQuery({
    queryKey: ['me'],
    queryFn: fetchMe,
    enabled: !!token,
    staleTime: 5 * 60 * 1000,
  })
}
