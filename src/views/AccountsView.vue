<script setup lang="ts">
import { onMounted, ref } from 'vue'

import AccountFormDialog from '@/components/account/AccountFormDialog.vue'
import AccountSearchBar from '@/components/account/AccountSearchBar.vue'
import AccountTable from '@/components/account/AccountTable.vue'
import AppLayout from '@/components/layout/AppLayout.vue'
import LoadingOverlay from '@/components/common/LoadingOverlay.vue'
import { useLoading } from '@/composables/useLoading'
import { useAccountStore } from '@/stores/account'
import type { Account, AccountFormDto } from '@/types/account'

const accountStore = useAccountStore()
const { isLoading: isSubmitting, withLoading } = useLoading()

const dialogVisible = ref(false)
const editingAccount = ref<Account | null>(null)
const feedbackMessage = ref('')
const feedbackType = ref<'success' | 'error'>('success')

const searchParams = ref({ name: '', email: '' })

onMounted(() => {
  void loadAccounts()
})

async function loadAccounts(): Promise<void> {
  const params = {
    ...(searchParams.value.name ? { name: searchParams.value.name } : {}),
    ...(searchParams.value.email ? { email: searchParams.value.email } : {}),
  }

  try {
    console.log('params', params)
    await accountStore.loadAccounts(params)
  } catch {
    showFeedback('載入帳號失敗，請稍後再試', 'error')
  }
}

function handleSearch(params: { name: string; email: string }): void {
  searchParams.value = params
  void loadAccounts()
}

function openCreateDialog(): void {
  editingAccount.value = null
  dialogVisible.value = true
}

function openEditDialog(account: Account): void {
  editingAccount.value = account
  dialogVisible.value = true
}

async function handleFormSubmit(payload: AccountFormDto): Promise<void> {
  try {
    await withLoading(async () => {
      if (editingAccount.value) {
        await accountStore.updateAccount(editingAccount.value.id, payload)
        showFeedback('帳號更新成功', 'success')
      } else {
        await accountStore.createAccount(payload)
        showFeedback('帳號建立成功', 'success')
      }
    })

    dialogVisible.value = false
    await loadAccounts()
  } catch (error) {
    showFeedback(error instanceof Error ? error.message : '操作失敗', 'error')
  }
}

async function handleDelete(account: Account): Promise<void> {
  const confirmed = window.confirm(`確定要刪除「${account.name}」嗎？此操作無法復原。`)
  if (!confirmed) return

  try {
    await accountStore.removeAccount(account.id)
    showFeedback('帳號已刪除', 'success')
  } catch (error) {
    showFeedback(error instanceof Error ? error.message : '刪除失敗', 'error')
  }
}

function showFeedback(message: string, type: 'success' | 'error'): void {
  feedbackMessage.value = message
  feedbackType.value = type
}
</script>

<template>
  <AppLayout>
    <div class="space-y-6">
      <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 class="text-2xl font-bold text-slate-900">帳號列表</h2>
          <p class="mt-1 text-sm text-slate-500">管理系統內的所有使用者帳號</p>
        </div>
        <button
          type="button"
          class="inline-flex items-center justify-center rounded-xl bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-indigo-700"
          @click="openCreateDialog"
        >
          + 新增帳號
        </button>
      </div>

      <p
        v-if="feedbackMessage"
        class="rounded-lg px-4 py-3 text-sm"
        :class="feedbackType === 'success' ? 'bg-emerald-50 text-emerald-700' : 'bg-red-50 text-red-600'"
      >
        {{ feedbackMessage }}
      </p>

      <AccountSearchBar @search="handleSearch" />

      <div class="relative">
        <LoadingOverlay :loading="accountStore.loading" />
        <AccountTable
          :accounts="accountStore.accounts"
          :loading="accountStore.loading"
          @edit="openEditDialog"
          @delete="handleDelete"
        />
      </div>
    </div>

    <AccountFormDialog
      v-model:visible="dialogVisible"
      :account="editingAccount"
      :submitting="isSubmitting"
      @submit="handleFormSubmit"
    />
  </AppLayout>
</template>
