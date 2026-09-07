import { useState, useRef, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, RefreshCw } from 'lucide-react'
import { useClaimDetail, useReanalyzeClaim } from '@/hooks/useClaimDetail'
import { useApproveClaim, useRejectClaim } from '@/hooks/useQueue'
import { useWithdrawClaim } from '@/hooks/useMyClaims'
import { AiInsightBlock } from '@/components/AiInsightBlock'
import { ClaimStatusBadge } from '@/components/ClaimStatusBadge'
import { RejectModal } from '@/components/RejectModal'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { Separator } from '@/components/ui/separator'
import { useAuthStore } from '@/store/authStore'

export function ClaimDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const claimId = Number(id)
  const user = useAuthStore((s) => s.user)
  const [rejectOpen, setRejectOpen] = useState(false)
  const [reanalyzeFailedNote, setReanalyzeFailedNote] = useState(false)
  const prevSummaryRef = useRef<string | null | undefined>(undefined)

  const { data: claim, isLoading } = useClaimDetail(claimId)
  const reanalyze = useReanalyzeClaim(claimId)

  // Detect when a reanalyze attempt completes and the result didn't change
  // (meaning all providers failed but the old result was preserved).
  useEffect(() => {
    if (prevSummaryRef.current === undefined) return
    if (claim?.ai_status === 'pending' || claim?.ai_status === 'processing') return
    if (claim?.ai_status === 'completed' && claim.ai_summary === prevSummaryRef.current) {
      setReanalyzeFailedNote(true)
    } else {
      setReanalyzeFailedNote(false)
    }
    prevSummaryRef.current = undefined
  }, [claim?.ai_status, claim?.ai_summary])
  const approve = useApproveClaim()
  const reject = useRejectClaim()
  const withdraw = useWithdrawClaim()

  if (isLoading) {
    return (
      <div className="max-w-2xl mx-auto space-y-4">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-64 w-full" />
        <Skeleton className="h-24 w-full" />
      </div>
    )
  }

  if (!claim) {
    return <p className="text-gray-500">Claim not found.</p>
  }

  const isRequester = user?.id === claim.requester_id
  const isManager = user?.managed_category_ids.includes(claim.category_id) ?? false
  const isOwnClaim = isRequester

  function handleApprove() {
    approve.mutate(claimId, { onSuccess: () => navigate('/queue') })
  }

  function handleReject(comment: string) {
    reject.mutate({ id: claimId, comment }, {
      onSuccess: () => {
        setRejectOpen(false)
        navigate('/queue')
      },
    })
  }

  function handleWithdraw() {
    withdraw.mutate(claimId, { onSuccess: () => navigate('/claims') })
  }

  return (
    <div className="max-w-2xl mx-auto space-y-4">
      <button
        onClick={() => navigate(-1)}
        className="flex items-center gap-1 text-sm text-gray-500 hover:text-gray-800"
      >
        <ArrowLeft className="h-4 w-4" />
        Back
      </button>

      <Card>
        <CardHeader>
          <div className="flex items-start justify-between">
            <div>
              <CardTitle className="text-lg">
                {claim.category?.name ?? 'Expense'} claim #{claim.id}
              </CardTitle>
              <p className="text-sm text-gray-500 mt-1">
                by {claim.requester?.name ?? 'Unknown'} · {claim.expense_date}
              </p>
            </div>
            <ClaimStatusBadge status={claim.status} />
          </div>
        </CardHeader>

        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">Amount</p>
              <p className="text-2xl font-semibold text-gray-900">${Number(claim.amount).toFixed(2)}</p>
            </div>
            <div>
              <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">Category</p>
              <p className="font-medium">{claim.category?.name}</p>
            </div>
          </div>

          <div>
            <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-1">Description</p>
            <p className="text-sm text-gray-700">{claim.description}</p>
          </div>

          <div>
            <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-1">Payment details</p>
            <p className="text-sm text-gray-700 font-mono break-all">{claim.payment_details}</p>
          </div>

          {claim.reject_comment && (
            <div className="rounded-md bg-red-50 border border-red-200 p-3">
              <p className="text-xs font-medium text-red-700 uppercase tracking-wide mb-1">Rejection reason</p>
              <p className="text-sm text-red-800">{claim.reject_comment}</p>
            </div>
          )}

          <Separator />

          <AiInsightBlock claim={claim} reanalyzeFailedNote={reanalyzeFailedNote} />

          {claim.status === 'pending' && (
            <div className="flex justify-end">
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  prevSummaryRef.current = claim.ai_summary
                  setReanalyzeFailedNote(false)
                  reanalyze.mutate(undefined)
                }}
                disabled={reanalyze.isPending}
              >
                <RefreshCw className={`h-3.5 w-3.5 mr-1.5 ${reanalyze.isPending ? 'animate-spin' : ''}`} />
                {reanalyze.isPending ? 'Requesting…' : 'Re-run AI analysis'}
              </Button>
            </div>
          )}

          {/* Actions */}
          {claim.status === 'pending' && (
            <div className="flex gap-2 justify-end">
              {isManager && isOwnClaim && (
                <p className="text-xs text-gray-400 self-center">
                  You submitted this claim — you cannot approve or reject your own submission.
                </p>
              )}
              {isRequester && !isManager && (
                <Button
                  variant="outline"
                  onClick={handleWithdraw}
                  disabled={withdraw.isPending}
                >
                  {withdraw.isPending ? 'Withdrawing…' : 'Withdraw'}
                </Button>
              )}
              {isManager && !isOwnClaim && (
                <>
                  <Button
                    variant="outline"
                    onClick={handleApprove}
                    disabled={approve.isPending || reject.isPending}
                  >
                    {approve.isPending ? 'Approving…' : 'Approve'}
                  </Button>
                  <Button
                    variant="destructive"
                    onClick={() => setRejectOpen(true)}
                    disabled={approve.isPending || reject.isPending}
                  >
                    Reject
                  </Button>
                </>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      <RejectModal
        open={rejectOpen}
        onClose={() => setRejectOpen(false)}
        onConfirm={handleReject}
        isLoading={reject.isPending}
      />
    </div>
  )
}
