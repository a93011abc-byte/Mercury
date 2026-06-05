export interface ApiErrorResponse {
  message: string | string[]
  error?: string
  statusCode: number
}

export interface LoginCredentials {
  email: string
  password: string
  rememberMe: boolean
}

export interface AuthToken {
  accessToken: string
  email: string
  expiresAt: number
}
