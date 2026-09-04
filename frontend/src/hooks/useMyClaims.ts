import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { fetchMyClaims, withdrawClaim } from '@/api/claims'

export function useMyClaims() {
  return useQuery({
    queryKey: ['claims', 'mine'],
    queryFn: fetchMyClaims,
    refetchInterval: 30_000,
    refetchOnWindowFocus: true,
  })
}

export function useWithdrawClaim() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: withdrawClaim,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['claims'] })
    },
  })
}
