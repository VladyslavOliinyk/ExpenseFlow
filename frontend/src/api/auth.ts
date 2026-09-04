import { apiClient } from './client'
import type { User } from '@/types'

export async function loginAs(userId: number): Promise<{ access_token: string }> {
  const { data } = await apiClient.post(`/auth/login-as/${userId}`)
  return data
}

export async function fetchAllUsers(): Promise<User[]> {
  const { data } = await apiClient.get('/auth/users')
  return data
}

export async function fetchMe(): Promise<User> {
  const { data } = await apiClient.get('/me')
  return data
}
