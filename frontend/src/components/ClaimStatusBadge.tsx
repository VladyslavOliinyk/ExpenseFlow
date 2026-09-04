import { Badge } from '@/components/ui/badge'
import type { ClaimStatus } from '@/types'

const STATUS_CONFIG: Record<ClaimStatus, { label: string; variant: 'default' | 'success' | 'destructive' | 'secondary' | 'warning' }> = {
  pending: { label: 'Pending', variant: 'warning' },
  approved: { label: 'Approved', variant: 'success' },
  rejected: { label: 'Rejected', variant: 'destructive' },
  withdrawn: { label: 'Withdrawn', variant: 'secondary' },
}

export function ClaimStatusBadge({ status }: { status: ClaimStatus }) {
  const config = STATUS_CONFIG[status]
  return <Badge variant={config.variant}>{config.label}</Badge>
}
