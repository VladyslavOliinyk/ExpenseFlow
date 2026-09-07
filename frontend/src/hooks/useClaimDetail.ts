import { useQuery } from '@tanstack/react-query'
import { fetchClaim } from '@/api/claims'

export function useClaimDetail(id: number) {
  return useQuery({
    queryKey: ['claims', id],
    queryFn: () => fetchClaim(id),
    refetchInterval: (query) => {
      const data = query.state.data
      if (!data || data.ai_summary !== null) return false
      // Poll for 35s — 5s beyond the 30s "unavailable" threshold in ClaimDetailPage,
      // ensuring polling outlasts the frontend timer during the full fallback cycle.
      // Append 'Z' to treat backend's naive UTC datetime string as UTC, not local time.
      const createdAtMs = new Date(
        data.created_at.endsWith('Z') ? data.created_at : `${data.created_at}Z`
      ).getTime()
      return Date.now() - createdAtMs < 35_000 ? 5_000 : false
    },
    refetchOnWindowFocus: true,
  })
}
