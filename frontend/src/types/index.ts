export type ClaimStatus = 'pending' | 'approved' | 'rejected' | 'withdrawn'
export type AiStatus = 'pending' | 'processing' | 'completed' | 'failed'

export interface User {
  id: number
  name: string
  email: string
  managed_category_ids: number[]
  managed_category_names: string[]
}

export interface Category {
  id: number
  name: string
  responsible_manager_id: number
}

export interface Claim {
  id: number
  requester_id: number
  category_id: number
  amount: string
  description: string
  expense_date: string
  payment_details: string
  status: ClaimStatus
  reject_comment: string | null
  ai_status: AiStatus
  ai_summary: string | null
  ai_mismatch_flag: boolean | null
  ai_mismatch_reason: string | null
  ai_provider_used: string | null
  is_potential_duplicate: boolean
  duplicate_of_claim_id: number | null
  created_at: string
  updated_at: string
  resolved_at: string | null
  requester: User | null
  category: Category | null
}

export interface ClaimCreate {
  category_id: number
  amount: string
  description: string
  expense_date: string
  payment_details: string
}

export interface CategorySuggestion {
  suggested_category: string | null
  confidence: string | null
}

export interface AiMetrics {
  total_analyzed: number
  mismatch_count: number
  mismatch_rate: number
  avg_latency_ms: number | null
  provider_breakdown: Record<string, number>
}
