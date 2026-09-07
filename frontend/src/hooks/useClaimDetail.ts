import { useQuery } from '@tanstack/react-query'
import { fetchClaim } from '@/api/claims'

export function useClaimDetail(id: number) {
  return useQuery({
    queryKey: ['claims', id],
    queryFn: () => fetchClaim(id),
    refetchInterval: (query) => {
      const data = query.state.data
      if (!data || data.ai_summary !== null) return false
      const ageMs = Date.now() - new Date(data.created_at).getTime()
      return ageMs < 20_000 ? 5_000 : false
    },
    refetchOnWindowFocus: true,
  })
}
