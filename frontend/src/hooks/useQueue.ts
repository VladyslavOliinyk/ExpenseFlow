import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { fetchQueue, approveClaim, rejectClaim } from '@/api/claims'

export function useQueue() {
  return useQuery({
    queryKey: ['claims', 'queue'],
    queryFn: fetchQueue,
    refetchInterval: 30_000,
    refetchOnWindowFocus: true,
  })
}

export function useApproveClaim() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: approveClaim,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['claims'] })
    },
  })
}

export function useRejectClaim() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, comment }: { id: number; comment: string }) => rejectClaim(id, comment),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['claims'] })
    },
  })
}
