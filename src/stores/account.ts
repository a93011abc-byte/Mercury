import { ref } from 'vue'
import { defineStore } from 'pinia'

import * as accountApi from '@/api/account'
import type { Account, AccountFormDto, AccountQueryParams } from '@/types/account'

export const useAccountStore = defineStore('account', () => {
  const accounts = ref<Account[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function loadAccounts(params?: AccountQueryParams): Promise<void> {
    loading.value = true
    error.value = null

    try {
      accounts.value = await accountApi.fetchAccounts(params)
    } catch (err) {
      error.value = err instanceof Error ? err.message : '載入帳號失敗'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function createAccount(payload: AccountFormDto): Promise<Account> {
    const created = await accountApi.createAccount(payload)
    accounts.value = [created, ...accounts.value]
    return created
  }

  async function updateAccount(id: string, payload: AccountFormDto): Promise<Account> {
    const updated = await accountApi.updateAccount(id, payload)
    const index = accounts.value.findIndex((item) => item.id === id)
    if (index !== -1) {
      accounts.value[index] = updated
    }
    return updated
  }

  async function removeAccount(id: string): Promise<void> {
    await accountApi.deleteAccount(id)
    accounts.value = accounts.value.filter((item) => item.id !== id)
  }

  return {
    accounts,
    loading,
    error,
    loadAccounts,
    createAccount,
    updateAccount,
    removeAccount,
  }
})
