<script setup lang="ts">
import { computed, reactive, watch } from 'vue'

import BaseInput from '@/components/common/BaseInput.vue'
import {
  ACCOUNT_STATUS_LABELS,
  AccountStatus,
  ROLE_LEVEL_LABELS,
  RoleLevel,
  type Account,
  type AccountFormDto,
} from '@/types/account'

const visible = defineModel<boolean>('visible', { required: true })

const props = defineProps<{
  account?: Account | null
  submitting?: boolean
}>()

const emit = defineEmits<{
  submit: [payload: AccountFormDto]
}>()

const form = reactive<AccountFormDto>({
  name: '',
  email: '',
  roleLevel: RoleLevel.User,
  status: AccountStatus.On,
})

const errors = reactive({
  name: '',
  email: '',
})

const isEditMode = computed(() => Boolean(props.account))
const dialogTitle = computed(() => (isEditMode.value ? '編輯帳號' : '新增帳號'))

const roleOptions = Object.values(RoleLevel)
const statusOptions = Object.values(AccountStatus)

watch(
  () => [visible.value, props.account] as const,
  ([isOpen, account]) => {
    if (!isOpen) return

    errors.name = ''
    errors.email = ''

    if (account) {
      form.name = account.name
      form.email = account.email
      form.roleLevel = account.roleLevel
      form.status = account.status
      return
    }

    form.name = ''
    form.email = ''
    form.roleLevel = RoleLevel.User
    form.status = AccountStatus.On
  },
  { immediate: true },
)

function validateForm(): boolean {
  errors.name = form.name.trim() ? '' : '請輸入姓名'
  errors.email = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email) ? '' : '請輸入有效的 Email'

  return !errors.name && !errors.email
}

function handleSubmit(): void {
  if (!validateForm()) return

  emit('submit', {
    name: form.name.trim(),
    email: form.email.trim(),
    roleLevel: form.roleLevel,
    status: form.status,
  })
}

function handleClose(): void {
  visible.value = false
}
</script>

<template>
  <Teleport to="body">
    <div
      v-if="visible"
      class="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 p-4 backdrop-blur-sm"
      @click.self="handleClose"
    >
      <div class="w-full max-w-lg rounded-2xl bg-white p-6 shadow-xl">
        <div class="mb-6 flex items-center justify-between">
          <h2 class="text-lg font-semibold text-slate-900">{{ dialogTitle }}</h2>
          <button
            type="button"
            class="rounded-lg p-1 text-slate-400 transition hover:bg-slate-100 hover:text-slate-600"
            @click="handleClose"
          >
            ✕
          </button>
        </div>

        <form class="space-y-4" @submit.prevent="handleSubmit">
          <BaseInput v-model="form.name" label="姓名" placeholder="請輸入姓名" :error="errors.name" />
          <BaseInput
            v-model="form.email"
            label="電子郵件"
            type="email"
            placeholder="name@example.com"
            :error="errors.email"
          />

          <div class="grid gap-4 sm:grid-cols-2">
            <div class="flex flex-col gap-1.5">
              <label class="text-sm font-medium text-slate-700">角色等級</label>
              <select
                v-model="form.roleLevel"
                class="rounded-lg border border-slate-200 px-4 py-3 text-sm outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20"
              >
                <option v-for="role in roleOptions" :key="role" :value="role">
                  {{ ROLE_LEVEL_LABELS[role] }}
                </option>
              </select>
            </div>

            <div class="flex flex-col gap-1.5">
              <label class="text-sm font-medium text-slate-700">帳號狀態</label>
              <select
                v-model="form.status"
                class="rounded-lg border border-slate-200 px-4 py-3 text-sm outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20"
              >
                <option v-for="status in statusOptions" :key="status" :value="status">
                  {{ ACCOUNT_STATUS_LABELS[status] }}
                </option>
              </select>
            </div>
          </div>

          <div class="flex justify-end gap-3 pt-2">
            <button
              type="button"
              class="rounded-lg border border-slate-200 px-4 py-2.5 text-sm font-medium text-slate-600 transition hover:bg-slate-50"
              @click="handleClose"
            >
              取消
            </button>
            <button
              type="submit"
              class="rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-60"
              :disabled="submitting"
            >
              {{ submitting ? '處理中...' : isEditMode ? '儲存變更' : '建立帳號' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </Teleport>
</template>
