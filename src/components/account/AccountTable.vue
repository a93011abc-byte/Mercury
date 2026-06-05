<script setup lang="ts">
import AccountStatusTag from '@/components/account/AccountStatusTag.vue'
import RoleLevelTag from '@/components/account/RoleLevelTag.vue'
import type { Account } from '@/types/account'

defineProps<{
  accounts: Account[]
  loading?: boolean
}>()

const emit = defineEmits<{
  edit: [account: Account]
  delete: [account: Account]
}>()
</script>

<template>
  <div class="relative overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
    <div class="overflow-x-auto">
      <table class="min-w-full divide-y divide-slate-200 text-sm">
        <thead class="bg-slate-50">
          <tr>
            <th class="px-4 py-3 text-left font-medium text-slate-600">姓名</th>
            <th class="px-4 py-3 text-left font-medium text-slate-600">Email</th>
            <th class="px-4 py-3 text-left font-medium text-slate-600">角色</th>
            <th class="px-4 py-3 text-left font-medium text-slate-600">狀態</th>
            <th class="px-4 py-3 text-right font-medium text-slate-600">操作</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100">
          <tr v-if="loading">
            <td colspan="5" class="px-4 py-10 text-center text-slate-500">載入帳號資料中...</td>
          </tr>
          <tr v-else-if="accounts.length === 0">
            <td colspan="5" class="px-4 py-10 text-center text-slate-500">尚無帳號資料，請點擊新增帳號</td>
          </tr>
          <tr v-for="account in accounts" :key="account.id" class="hover:bg-slate-50/80">
            <td class="px-4 py-3 font-medium text-slate-900">{{ account.name }}</td>
            <td class="px-4 py-3 text-slate-600">{{ account.email }}</td>
            <td class="px-4 py-3">
              <RoleLevelTag :role-level="account.roleLevel" />
            </td>
            <td class="px-4 py-3">
              <AccountStatusTag :status="account.status" />
            </td>
            <td class="px-4 py-3">
              <div class="flex justify-end gap-2">
                <button
                  type="button"
                  class="rounded-lg px-3 py-1.5 text-xs font-medium text-indigo-600 transition hover:bg-indigo-50"
                  @click="emit('edit', account)"
                >
                  編輯
                </button>
                <button
                  type="button"
                  class="rounded-lg px-3 py-1.5 text-xs font-medium text-red-600 transition hover:bg-red-50"
                  @click="emit('delete', account)"
                >
                  刪除
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
