/** 帳號角色等級 — 對應 API Schema RoleLevel */
export enum RoleLevel {
  Admin = 'ADMIN',
  Editor = 'EDITOR',
  User = 'USER',
  Client = 'CLIENT',
}

/** 帳號啟用狀態 — 對應 API Schema AccountStatus */
export enum AccountStatus {
  On = 'ON',
  Off = 'OFF',
}

export interface Account {
  id: string
  name: string
  email: string
  roleLevel: RoleLevel
  status: AccountStatus
}

export interface AccountFormDto {
  name: string
  email: string
  roleLevel: RoleLevel
  status: AccountStatus
}

export interface AccountQueryParams {
  name?: string
  email?: string
}

export const ROLE_LEVEL_LABELS: Record<RoleLevel, string> = {
  [RoleLevel.Admin]: '管理員',
  [RoleLevel.Editor]: '編輯者',
  [RoleLevel.User]: '一般使用者',
  [RoleLevel.Client]: '客戶',
}

export const ACCOUNT_STATUS_LABELS: Record<AccountStatus, string> = {
  [AccountStatus.On]: '啟用',
  [AccountStatus.Off]: '停用',
}
