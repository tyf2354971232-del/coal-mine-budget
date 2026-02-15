<template>
  <el-alert
    v-if="show"
    :title="message"
    type="info"
    show-icon
    :closable="false"
    style="margin-bottom: 16px"
  />
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useAuthStore } from '../../stores/auth'

const props = defineProps<{
  /** Roles that are allowed to edit on this page */
  editRoles?: string[]
}>()

const authStore = useAuthStore()

const show = computed(() => {
  const roles = props.editRoles || ['admin', 'leader', 'department']
  return !roles.includes(authStore.user?.role || '')
})

const message = computed(() => {
  const role = authStore.user?.role
  if (role === 'viewer') return '当前为只读模式 — 普通员工仅可查看数据，如需操作请联系管理员'
  if (role === 'department') return '当前为部门用户模式 — 仅可操作本部门相关数据'
  return '当前为只读模式'
})
</script>
