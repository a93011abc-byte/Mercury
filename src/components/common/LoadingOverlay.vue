<script setup lang="ts">
defineProps<{
  loading: boolean
  text?: string
}>()
</script>

<template>
  <div
    v-if="loading"
    class="absolute inset-0 z-10 flex items-center justify-center rounded-xl bg-white/70 backdrop-blur-sm"
  >
    <div class="flex items-center gap-3 text-sm text-slate-600">
      <span class="inline-block h-5 w-5 animate-spin rounded-full border-2 border-indigo-500 border-t-transparent" />
      {{ text ?? '載入中...' }}
    </div>
  </div>
</template>
