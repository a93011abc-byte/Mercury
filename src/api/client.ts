import axios, {
  type AxiosError,
  type AxiosInstance,
  type InternalAxiosRequestConfig,
} from 'axios'

import type { ApiErrorResponse } from '@/types/api'

const TOKEN_KEY = 'auth_token'

export function getStoredToken(): string | null {
  return localStorage.getItem(TOKEN_KEY) ?? sessionStorage.getItem(TOKEN_KEY)
}

export function setStoredToken(token: string, rememberMe: boolean): void {
  clearStoredToken()
  const storage = rememberMe ? localStorage : sessionStorage
  storage.setItem(TOKEN_KEY, token)
}

export function clearStoredToken(): void {
  localStorage.removeItem(TOKEN_KEY)
  sessionStorage.removeItem(TOKEN_KEY)
}

const apiClient: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 15_000,
  headers: {
    'Content-Type': 'application/json',
  },
})

apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  config.headers.set('interviewerName', import.meta.env.VITE_INTERVIEWER_NAME)

  const token = getStoredToken()
  if (token) {
    config.headers.set('Authorization', `Bearer ${token}`)
  }

  return config
})

apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError<ApiErrorResponse>) => {
    const message = extractErrorMessage(error)
    return Promise.reject(new Error(message))
  },
)

function extractErrorMessage(error: AxiosError<ApiErrorResponse>): string {
  const data = error.response?.data

  if (!data) {
    return error.message || '網路連線失敗，請稍後再試'
  }

  if (Array.isArray(data.message)) {
    return data.message.join('、')
  }

  return data.message || '請求失敗，請稍後再試'
}

export default apiClient
