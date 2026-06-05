<script setup lang="ts">
import { computed } from 'vue'

import { ROLE_LEVEL_LABELS, RoleLevel } from '@/types/account'

const props = defineProps<{
  roleLevel: RoleLevel
}>()

const label = computed(() => ROLE_LEVEL_LABELS[props.roleLevel])

const colorClass = computed(() => {
  const map: Record<RoleLevel, string> = {
    [RoleLevel.Admin]: 'bg-violet-50 text-violet-700 ring-violet-600/20',
    [RoleLevel.Editor]: 'bg-blue-50 text-blue-700 ring-blue-600/20',
    [RoleLevel.User]: 'bg-sky-50 text-sky-700 ring-sky-600/20',
    [RoleLevel.Client]: 'bg-amber-50 text-amber-700 ring-amber-600/20',
  }
  return map[props.roleLevel]
})
</script>

<template>
  <span
    class="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ring-1 ring-inset"
    :class="colorClass"
  >
    {{ label }}
  </span>
</template>
