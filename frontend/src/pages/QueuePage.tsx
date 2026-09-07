import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Inbox, AlertTriangle } from 'lucide-react'
import { useQueue, useApproveClaim, useRejectClaim } from '@/hooks/useQueue'
import { getApiError } from '@/api/client'
import { ClaimStatusBadge } from '@/components/ClaimStatusBadge'
import { RejectModal } from '@/components/RejectModal'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import type { Claim } from '@/types'

function QueueRow({ claim }: { claim: Claim }) {
  const [rejectOpen, setRejectOpen] = useState(false)
  const approve = useApproveClaim()
  const reject = useRejectClaim()

  return (
    <>
      <div className="py-4 border-b last:border-0">
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 flex-wrap">
              <Link to={`/claims/${claim.id}`} className="font-medium text-gray-900 hover:text-blue-600">
                {claim.requester?.name ?? 'Unknown'}
              </Link>
              <span className="text-gray-400 text-sm">→</span>
              <span className="text-sm text-gray-600">{claim.category?.name}</span>
              <ClaimStatusBadge status={claim.status} />
              {claim.is_potential_duplicate && (
                <span title="Possible duplicate" className="flex items-center gap-1 text-xs text-yellow-600 font-medium">
                  <AlertTriangle className="h-3.5 w-3.5" />
                  Duplicate?
                </span>
              )}
            </div>
            <p className="text-sm text-gray-500 mt-0.5 line-clamp-1">{claim.description}</p>
            <p className="text-xs text-gray-400 mt-1">
              ${Number(claim.amount).toFixed(2)} · {claim.expense_date}
            </p>
          </div>
          <div className="flex items-center gap-2 shrink-0">
            <Link to={`/claims/${claim.id}`}>
              <Button variant="ghost" size="sm">View</Button>
            </Link>
            <Button
              variant="outline"
              size="sm"
              onClick={() => approve.mutate(claim.id)}
              disabled={approve.isPending || reject.isPending}
            >
              {approve.isPending ? 'Approving…' : 'Approve'}
            </Button>
            <Button
              variant="destructive"
              size="sm"
              onClick={() => setRejectOpen(true)}
              disabled={approve.isPending || reject.isPending}
            >
              Reject
            </Button>
          </div>
        </div>
        {approve.isError && (
          <p className="text-xs text-red-600 text-right mt-1.5">
            {getApiError(approve.error)}
          </p>
        )}
      </div>
      <RejectModal
        open={rejectOpen}
        onClose={() => setRejectOpen(false)}
        onConfirm={(comment) => reject.mutate({ id: claim.id, comment })}
        isLoading={reject.isPending}
        aiReason={claim.ai_mismatch_flag ? (claim.ai_mismatch_reason ?? undefined) : undefined}
        error={reject.isError ? getApiError(reject.error) : undefined}
      />
    </>
  )
}

export function QueuePage() {
  const { data: queue, isLoading } = useQueue()

  if (isLoading) {
    return (
      <Card>
        <CardContent className="pt-6 space-y-4">
          {[1, 2].map((i) => <Skeleton key={i} className="h-16 w-full" />)}
        </CardContent>
      </Card>
    )
  }

  if (!queue || queue.length === 0) {
    return (
      <div className="space-y-4">
        <h1 className="text-xl font-semibold text-gray-900">Review Queue</h1>
        <Card>
          <CardContent className="pt-6">
            <div className="flex flex-col items-center justify-center py-12 text-center text-gray-400">
              <Inbox className="h-10 w-10 mb-3 opacity-30" />
              <p className="font-medium">Queue is empty</p>
              <p className="text-sm mt-1">No pending claims in your categories</p>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-semibold text-gray-900">
        Review Queue <span className="text-gray-400 font-normal text-base">({queue.length})</span>
      </h1>
      <Card>
        <CardContent className="pt-4">
          {queue.map((c) => <QueueRow key={c.id} claim={c} />)}
        </CardContent>
      </Card>
    </div>
  )
}
