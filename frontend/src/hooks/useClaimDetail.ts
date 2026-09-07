import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { fetchClaim, reanalyzeClaim } from '@/api/claims'

export function useClaimDetail(id: number) {
  return useQuery({
    queryKey: ['claims', id],
    queryFn: () => fetchClaim(id),
    refetchInterval: (query) => {
      const status = query.state.data?.ai_status
      return status === 'pending' || status === 'processing' ? 3_000 : false
    },
    refetchOnWindowFocus: true,
  })
}

export function useReanalyzeClaim(claimId: number) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: () => reanalyzeClaim(claimId),
    onSuccess: (updatedClaim) => {
      // Backend already set ai_status='processing' before returning, so writing
      // this into cache immediately restarts the refetchInterval (status is polling).
      qc.setQueryData(['claims', claimId], updatedClaim)
    },
  })
}
