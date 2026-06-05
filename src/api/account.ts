import apiClient from '@/api/client'
import type { Account, AccountFormDto, AccountQueryParams } from '@/types/account'

export async function fetchAccounts(params?: AccountQueryParams): Promise<Account[]> {
  const { data } = await apiClient.get<Account[]>('/accounts', { params })
  return data
}

export async function fetchAccountById(id: string): Promise<Account> {
  const { data } = await apiClient.get<Account>(`/account/${id}`)
  return data
}

export async function createAccount(payload: AccountFormDto): Promise<Account> {
  const { data } = await apiClient.post<Account>('/create-account', payload)
  return data
}

export async function updateAccount(id: string, payload: AccountFormDto): Promise<Account> {
  const { data } = await apiClient.patch<Account>(`/update-account/${id}`, payload)
  return data
}

export async function deleteAccount(id: string): Promise<void> {
  await apiClient.delete(`/delete-account/${id}`)
}
