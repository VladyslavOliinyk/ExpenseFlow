import { useState } from 'react'
import { AlertTriangle, CheckCircle, ChevronDown, ChevronUp, Bot } from 'lucide-react'
import { Skeleton } from '@/components/ui/skeleton'
import type { Claim } from '@/types'

interface Props {
  claim: Claim
}

export function AiInsightBlock({ claim }: Props) {
  const [expanded, setExpanded] = useState(false)

  if (claim.ai_status === 'pending' || claim.ai_status === 'processing') {
    return (
      <div className="rounded-lg border border-gray-200 p-4 space-y-2">
        <div className="flex items-center gap-2 text-sm text-gray-500">
          <Bot className="h-4 w-4 animate-pulse" />
          <span>Analyzing claim…</span>
        </div>
        <Skeleton className="h-4 w-3/4" />
        <Skeleton className="h-4 w-1/2" />
      </div>
    )
  }

  if (claim.ai_status === 'failed') {
    return (
      <div className="rounded-lg border border-dashed border-gray-200 p-4">
        <div className="flex items-center gap-2 text-sm text-gray-400">
          <Bot className="h-4 w-4" />
          <span>AI insight unavailable</span>
        </div>
      </div>
    )
  }

  return (
    <div
      className={`rounded-lg border p-4 space-y-2 animate-in fade-in duration-300 ${
        claim.ai_mismatch_flag
          ? 'border-amber-200 bg-amber-50'
          : 'border-green-200 bg-green-50'
      }`}
    >
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-center gap-2">
          <Bot className="h-4 w-4 text-gray-500 mt-0.5 shrink-0" />
          <span className="text-xs font-semibold text-gray-500 uppercase tracking-wide">
            AI Insight
            {claim.ai_provider_used && (
              <span className="ml-1 text-gray-400 normal-case font-normal">
                via {claim.ai_provider_used}
              </span>
            )}
          </span>
        </div>
        {claim.ai_mismatch_flag ? (
          <div className="flex items-center gap-1 text-amber-600 text-xs font-medium">
            <AlertTriangle className="h-3.5 w-3.5" />
            Mismatch flagged
          </div>
        ) : (
          <div className="flex items-center gap-1 text-green-600 text-xs font-medium">
            <CheckCircle className="h-3.5 w-3.5" />
            Looks good
          </div>
        )}
      </div>

      <p className="text-sm text-gray-700">{claim.ai_summary}</p>

      {claim.ai_mismatch_flag && claim.ai_mismatch_reason && (
        <div>
          <button
            onClick={() => setExpanded((e) => !e)}
            className="flex items-center gap-1 text-xs text-amber-700 hover:text-amber-900"
          >
            {expanded ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />}
            {expanded ? 'Hide reason' : 'Show reason'}
          </button>
          {expanded && (
            <p className="mt-1 text-xs text-amber-800 bg-amber-100 rounded p-2">
              {claim.ai_mismatch_reason}
            </p>
          )}
        </div>
      )}
    </div>
  )
}
