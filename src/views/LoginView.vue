<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import BaseInput from '@/components/common/BaseInput.vue'
import { useLoading } from '@/composables/useLoading'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()
const { isLoading, withLoading } = useLoading()

const form = reactive({
  email: '',
  password: '',
  rememberMe: false,
})

const errorMessage = ref('')

async function handleSubmit(): Promise<void> {
  errorMessage.value = ''

  try {
    await withLoading(() =>
      authStore.login({
        email: form.email,
        password: form.password,
        rememberMe: form.rememberMe,
      }),
    )

    const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : '/accounts'
    await router.push(redirect)
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : '登入失敗，請稍後再試'
  }
}
</script>

<template>
  <div class="flex min-h-screen items-center justify-center bg-gradient-to-br from-indigo-50 via-white to-violet-50 px-4 py-10">
    <div class="w-full max-w-md">
      <div class="rounded-2xl border border-white/60 bg-white/90 p-8 shadow-xl shadow-indigo-100/50 backdrop-blur">
        <div class="mb-8 text-center">
          <div class="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-indigo-600 text-2xl text-white shadow-lg shadow-indigo-200">
            🔐
          </div>
          <h1 class="text-2xl font-bold text-slate-900">歡迎回來</h1>
          <p class="mt-2 text-sm text-slate-500">請登入您的帳號以繼續</p>
        </div>

        <form class="space-y-5" @submit.prevent="handleSubmit">
          <BaseInput
            v-model="form.email"
            label="電子郵件"
            type="email"
            placeholder="name@example.com"
            autocomplete="email"
          />

          <BaseInput
            v-model="form.password"
            label="密碼"
            type="password"
            placeholder="請輸入密碼"
            autocomplete="current-password"
          />

          <div class="flex items-center justify-between text-sm">
            <label class="flex cursor-pointer items-center gap-2 text-slate-600">
              <input
                v-model="form.rememberMe"
                type="checkbox"
                class="h-4 w-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500"
              />
              記住我
            </label>
            <button type="button" class="text-indigo-600 transition hover:text-indigo-700">
              忘記密碼？
            </button>
          </div>

          <p v-if="errorMessage" class="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-600">
            {{ errorMessage }}
          </p>

          <button
            type="submit"
            class="w-full rounded-xl bg-indigo-600 py-3 text-sm font-semibold text-white shadow-lg shadow-indigo-200 transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-60"
            :disabled="isLoading"
          >
            {{ isLoading ? '登入中...' : '登入' }}
          </button>
        </form>

        <div class="mt-6 rounded-xl bg-amber-50 px-4 py-3 text-sm text-amber-800">
          💡 提示：輸入任意電子郵件和密碼即可登入
        </div>

        <p class="mt-6 text-center text-sm text-slate-500">
          還沒有帳號？
          <button type="button" class="font-medium text-indigo-600 hover:text-indigo-700">
            立即註冊
          </button>
        </p>
      </div>
    </div>
  </div>
</template>
