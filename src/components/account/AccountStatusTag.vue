<script setup lang="ts">
import { computed } from 'vue'

import { ACCOUNT_STATUS_LABELS, AccountStatus } from '@/types/account'

const props = defineProps<{
  status: AccountStatus
}>()

const label = computed(() => ACCOUNT_STATUS_LABELS[props.status])

const colorClass = computed(() =>
  props.status === AccountStatus.On
    ? 'bg-emerald-50 text-emerald-700 ring-emerald-600/20'
    : 'bg-slate-100 text-slate-600 ring-slate-500/10',
)
</script>

<template>
  <span
    class="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ring-1 ring-inset"
    :class="colorClass"
  >
    {{ label }}
  </span>
</template>
