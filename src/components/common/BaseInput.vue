<script setup lang="ts">
defineProps<{
  label: string
  type?: string
  placeholder?: string
  error?: string
  autocomplete?: string
}>()

const model = defineModel<string>({ required: true })
</script>

<template>
  <div class="flex flex-col gap-1.5">
    <label class="text-sm font-medium text-slate-700">{{ label }}</label>
    <input
      v-model="model"
      :type="type ?? 'text'"
      :placeholder="placeholder"
      :autocomplete="autocomplete"
      class="w-full rounded-lg border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20"
      :class="{ 'border-red-400 focus:border-red-400 focus:ring-red-400/20': error }"
    />
    <p v-if="error" class="text-xs text-red-500">{{ error }}</p>
  </div>
</template>
