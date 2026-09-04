import { useQuery } from '@tanstack/react-query'
import { fetchClaim } from '@/api/claims'

export function useClaimDetail(id: number) {
  return useQuery({
    queryKey: ['claims', id],
    queryFn: () => fetchClaim(id),
    refetchInterval: (query) => {
      // Keep polling until AI results appear (max 30s intervals)
      const data = query.state.data
      if (data && data.ai_summary === null && data.status === 'pending') {
        return 5_000
      }
      return 30_000
    },
    refetchOnWindowFocus: true,
  })
}
