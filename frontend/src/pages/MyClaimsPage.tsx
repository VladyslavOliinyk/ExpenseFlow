import { Link } from 'react-router-dom'
import { FileText } from 'lucide-react'
import { useMyClaims, useWithdrawClaim } from '@/hooks/useMyClaims'
import { ClaimStatusBadge } from '@/components/ClaimStatusBadge'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import type { Claim } from '@/types'

function ClaimRow({ claim }: { claim: Claim }) {
  const withdraw = useWithdrawClaim()

  return (
    <div className="flex items-start justify-between gap-4 py-4 border-b last:border-0">
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 flex-wrap">
          <Link to={`/claims/${claim.id}`} className="font-medium text-gray-900 hover:text-blue-600 truncate">
            {claim.category?.name ?? 'Unknown category'}
          </Link>
          <ClaimStatusBadge status={claim.status} />
        </div>
        <p className="text-sm text-gray-500 mt-0.5 line-clamp-1">{claim.description}</p>
        <p className="text-xs text-gray-400 mt-1">
          ${Number(claim.amount).toFixed(2)} · {claim.expense_date} · submitted {new Date(claim.created_at).toLocaleDateString()}
        </p>
      </div>
      <div className="flex items-center gap-2 shrink-0">
        <Link to={`/claims/${claim.id}`}>
          <Button variant="ghost" size="sm">View</Button>
        </Link>
        {claim.status === 'pending' && (
          <Button
            variant="outline"
            size="sm"
            onClick={() => withdraw.mutate(claim.id)}
            disabled={withdraw.isPending}
          >
            Withdraw
          </Button>
        )}
      </div>
    </div>
  )
}

export function MyClaimsPage() {
  const { data: claims, isLoading } = useMyClaims()

  if (isLoading) {
    return (
      <Card>
        <CardContent className="pt-6 space-y-4">
          {[1, 2, 3].map((i) => <Skeleton key={i} className="h-16 w-full" />)}
        </CardContent>
      </Card>
    )
  }

  if (!claims || claims.length === 0) {
    return (
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col items-center justify-center py-12 text-center text-gray-400">
            <FileText className="h-10 w-10 mb-3 opacity-30" />
            <p className="font-medium">No claims yet</p>
            <p className="text-sm mt-1">
              <Link to="/claims/new" className="text-blue-600 hover:underline">Submit your first claim</Link>
            </p>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold text-gray-900">My Claims</h1>
        <Link to="/claims/new">
          <Button size="sm">New claim</Button>
        </Link>
      </div>
      <Card>
        <CardContent className="pt-4">
          {claims.map((c) => <ClaimRow key={c.id} claim={c} />)}
        </CardContent>
      </Card>
    </div>
  )
}
