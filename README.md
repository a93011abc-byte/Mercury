# Vue 前端工程師面試測驗 — 帳號管理系統

基於 Vue 3 + Vite + TypeScript 的帳號管理前端專案，串接水星工程面試 API，實作登入與帳號 CRUD 功能。

## 技術堆疊

- **Vue 3** — Composition API、`<script setup>`
- **Vite** — 開發與建置工具
- **TypeScript** — 完整型別標註
- **Pinia** — 狀態管理（auth / account）
- **Vue Router** — 路由與導航守衛
- **Axios** — API 封裝與攔截器
- **Tailwind CSS** — RWD 版面樣式

## 功能說明

| 頁面 | 功能 |
|------|------|
| 登入頁 `/login` | Email 格式驗證、記住我、登入後導向帳號列表 |
| 帳號管理 `/accounts` | 列表查詢（姓名 / Email debounce 搜尋）、新增、編輯、刪除 |

## 環境設定

複製環境變數範本並填入您的英文姓名（API 必要 Header）：

```sh
cp .env.example .env
```

編輯 `.env`：

```env
VITE_API_BASE_URL=https://api-frontend-interview-server.metcfire.com.tw
VITE_INTERVIEWER_NAME=JarvisWang
```

> **重要**：請將 `VITE_INTERVIEWER_NAME` 改為您的英文姓名，否則 API 無法辨識身份。

## 啟動專案

```sh
# 安裝依賴
npm install

# 開發模式（預設 http://localhost:5173）
npm run dev

# TypeScript 型別檢查
npm run type-check

# 正式環境建置
npm run build

# 預覽建置結果
npm run preview
```

## 專案結構

```
src/
├── api/              # Axios 客戶端與 API 方法
├── components/       # 可重用元件
│   ├── account/      # 帳號相關元件
│   ├── common/       # 通用元件（BaseInput、LoadingOverlay）
│   └── layout/       # 版面配置
├── composables/      # 組合式函式（debounce、loading）
├── router/           # 路由設定與守衛
├── stores/           # Pinia stores
├── types/            # TypeScript 型別與 Enum
└── views/            # 頁面元件
```

## API 說明

- Base URL：`https://api-frontend-interview-server.metcfire.com.tw`
- 文件：https://api-frontend-interview-server.metcfire.com.tw/api-docs
- 所有請求自動帶上 `interviewerName` Header
- 登入頁依測驗說明以前端驗證流程處理（任意 Email / 密碼即可登入）

### Enum 值（依 Swagger Schema）

- **RoleLevel**：`ADMIN` | `EDITOR` | `USER` | `CLIENT`
- **AccountStatus**：`ON` | `OFF`

## 測試帳號

登入頁可輸入任意有效 Email 格式與密碼，例如：

- Email：`test@example.com`
- 密碼：`password123`
