import { apiClient } from './client'
import type { Claim, ClaimCreate, AiMetrics, CategorySuggestion } from '@/types'

export async function createClaim(body: ClaimCreate): Promise<Claim> {
  const { data } = await apiClient.post('/claims', body)
  return data
}

export async function fetchMyClaims(): Promise<Claim[]> {
  const { data } = await apiClient.get('/claims/mine')
  return data
}

export async function fetchQueue(): Promise<Claim[]> {
  const { data } = await apiClient.get('/claims/queue')
  return data
}

export async function fetchClaim(id: number): Promise<Claim> {
  const { data } = await apiClient.get(`/claims/${id}`)
  return data
}

export async function withdrawClaim(id: number): Promise<Claim> {
  const { data } = await apiClient.post(`/claims/${id}/withdraw`)
  return data
}

export async function approveClaim(id: number): Promise<Claim> {
  const { data } = await apiClient.post(`/claims/${id}/approve`)
  return data
}

export async function rejectClaim(id: number, comment: string): Promise<Claim> {
  const { data } = await apiClient.post(`/claims/${id}/reject`, { comment })
  return data
}

export async function reanalyzeClaim(id: number): Promise<Claim> {
  const { data } = await apiClient.post(`/claims/${id}/reanalyze`)
  return data
}

export async function fetchAiMetrics(): Promise<AiMetrics> {
  const { data } = await apiClient.get('/admin/ai-metrics')
  return data
}

export async function suggestCategory(description: string): Promise<CategorySuggestion> {
  const { data } = await apiClient.post('/claims/suggest-category', { description })
  return data
}
