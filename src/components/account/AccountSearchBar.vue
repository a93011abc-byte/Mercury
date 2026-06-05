<script setup lang="ts">
import { ref, watch } from 'vue'

import { useDebouncedRef } from '@/composables/useDebounce'

const emit = defineEmits<{
  search: [params: { name: string; email: string }]
}>()

const name = ref('')
const email = ref('')
const debouncedName = useDebouncedRef(name, 400)
const debouncedEmail = useDebouncedRef(email, 400)

watch([debouncedName, debouncedEmail], ([nextName, nextEmail]) => {
  emit('search', { name: nextName.trim(), email: nextEmail.trim() })
})

function handleReset(): void {
  name.value = ''
  email.value = ''
}
</script>

<template>
  <div class="flex flex-col gap-4 rounded-xl border border-slate-200 bg-white p-4 shadow-sm md:flex-row md:items-end">
    <div class="flex-1">
      <label class="mb-1.5 block text-sm font-medium text-slate-700">姓名搜尋</label>
      <input
        v-model="name"
        type="text"
        placeholder="輸入姓名關鍵字"
        class="w-full rounded-lg border border-slate-200 px-4 py-2.5 text-sm outline-none transition focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20"
      />
    </div>
    <div class="flex-1">
      <label class="mb-1.5 block text-sm font-medium text-slate-700">Email 搜尋</label>
      <input
        v-model="email"
        type="email"
        placeholder="輸入 Email 關鍵字"
        class="w-full rounded-lg border border-slate-200 px-4 py-2.5 text-sm outline-none transition focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20"
      />
    </div>
    <button
      type="button"
      class="rounded-lg border border-slate-200 px-4 py-2.5 text-sm font-medium text-slate-600 transition hover:bg-slate-50"
      @click="handleReset"
    >
      清除
    </button>
  </div>
</template>
