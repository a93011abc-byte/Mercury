import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

import { clearStoredToken, getStoredToken, setStoredToken } from '@/api/client'
import type { LoginCredentials } from '@/types/api'

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(getStoredToken())
  const email = ref<string | null>(null)

  const isAuthenticated = computed(() => Boolean(token.value))

  function validateEmail(value: string): boolean {
    return EMAIL_PATTERN.test(value)
  }

  async function login(credentials: LoginCredentials): Promise<void> {
    const { email: inputEmail, password, rememberMe } = credentials

    if (!validateEmail(inputEmail)) {
      throw new Error('請輸入有效的電子郵件格式')
    }

    if (!password.trim()) {
      throw new Error('請輸入密碼')
    }

    // API 未提供登入端點，依測驗說明以任意 Email / 密碼完成前端驗證流程
    const mockToken = btoa(`${inputEmail}:${Date.now()}`)
    setStoredToken(mockToken, rememberMe)

    token.value = mockToken
    email.value = inputEmail
  }

  function logout(): void {
    clearStoredToken()
    token.value = null
    email.value = null
  }

  function hydrate(): void {
    token.value = getStoredToken()
  }

  return {
    token,
    email,
    isAuthenticated,
    login,
    logout,
    hydrate,
    validateEmail,
  }
})
