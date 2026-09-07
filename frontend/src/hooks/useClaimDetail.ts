import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { fetchClaim, reanalyzeClaim } from '@/api/claims'

export function useClaimDetail(id: number, activeAfter?: number) {
  return useQuery({
    queryKey: ['claims', id],
    queryFn: () => fetchClaim(id),
    refetchInterval: (query) => {
      const data = query.state.data
      if (!data || data.ai_summary !== null) return false
      // Append 'Z' to treat backend's naive UTC datetime string as UTC, not local time.
      const createdAtMs = new Date(
        data.created_at.endsWith('Z') ? data.created_at : `${data.created_at}Z`
      ).getTime()
      // Use activeAfter (set on manual reanalyze) when it's more recent than created_at,
      // so polling restarts correctly even for claims created long ago.
      const referenceMs = activeAfter && activeAfter > createdAtMs ? activeAfter : createdAtMs
      // Poll for 35s — 5s beyond the 30s "unavailable" threshold in ClaimDetailPage,
      // ensuring polling outlasts the frontend timer during the full fallback cycle.
      return Date.now() - referenceMs < 35_000 ? 5_000 : false
    },
    refetchOnWindowFocus: true,
  })
}

export function useReanalyzeClaim(claimId: number) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: () => reanalyzeClaim(claimId),
    onSuccess: (updatedClaim) => {
      // Write null-AI-fields claim into cache immediately so the UI shows skeleton
      // without waiting for the next poll. The caller's onSuccess sets reanalyzedAt,
      // which triggers a useEffect refetch to restart the polling interval — see
      // ClaimDetailPage. We do NOT call invalidateQueries here because reanalyzedAt
      // hasn't propagated yet at this point (React state update is async).
      qc.setQueryData(['claims', claimId], updatedClaim)
    },
  })
}
