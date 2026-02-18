<template>
  <div class="user-management">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span class="card-title">用户管理</span>
          <el-button type="primary" @click="showCreateDialog = true"><el-icon><Plus /></el-icon> 新增用户</el-button>
        </div>
      </template>

      <el-table :data="users" v-loading="loading" stripe border>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column prop="full_name" label="姓名" width="120" />
        <el-table-column prop="role" label="角色" width="120">
          <template #default="{ row }">
            <el-tag :type="row.role === 'admin' ? 'danger' : row.role === 'leader' ? 'warning' : row.role === 'department' ? '' : 'info'">
              {{ roleLabel(row.role) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="department" label="部门" width="140" />
        <el-table-column prop="is_active" label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">{{ row.is_active ? '正常' : '禁用' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="170">
          <template #default="{ row }">{{ formatDateTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="editUser(row)">编辑</el-button>
            <el-button :type="row.is_active ? 'danger' : 'success'" link size="small" @click="toggleActive(row)">
              {{ row.is_active ? '禁用' : '启用' }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="showCreateDialog" :title="editingUser ? '编辑用户' : '新增用户'" width="450px" @close="resetForm">
      <el-form :model="form" label-width="80px">
        <el-form-item label="用户名"><el-input v-model="form.username" :disabled="!!editingUser" /></el-form-item>
        <el-form-item label="姓名"><el-input v-model="form.full_name" /></el-form-item>
        <el-form-item label="密码" v-if="!editingUser"><el-input v-model="form.password" type="password" show-password /></el-form-item>
        <el-form-item label="角色">
          <el-select v-model="form.role" style="width:100%">
            <el-option label="管理员" value="admin" /><el-option label="领导" value="leader" />
            <el-option label="部门用户" value="department" /><el-option label="普通用户" value="viewer" />
          </el-select>
        </el-form-item>
        <el-form-item label="部门"><el-input v-model="form.department" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { authApi } from '../api/auth'
import { formatDateTime } from '../utils/format'

const loading = ref(false)
const saving = ref(false)
const users = ref<any[]>([])
const showCreateDialog = ref(false)
const editingUser = ref<any>(null)
const form = reactive({ username: '', full_name: '', password: '', role: 'viewer', department: '' })

const roleLabel = (r: string) => ({ admin: '管理员', leader: '领导', department: '部门用户', viewer: '普通用户' }[r] || r)

async function loadData() {
  loading.value = true
  try {
    const { data } = await authApi.listUsers()
    users.value = data
  } finally { loading.value = false }
}

function editUser(row: any) {
  editingUser.value = row
  Object.assign(form, { username: row.username, full_name: row.full_name, role: row.role, department: row.department || '' })
  showCreateDialog.value = true
}

function resetForm() {
  editingUser.value = null
  Object.assign(form, { username: '', full_name: '', password: '', role: 'viewer', department: '' })
}

async function handleSave() {
  saving.value = true
  try {
    if (editingUser.value) {
      await authApi.updateUser(editingUser.value.id, { full_name: form.full_name, role: form.role, department: form.department })
    } else {
      await authApi.createUser(form)
    }
    ElMessage.success(editingUser.value ? '更新成功' : '创建成功')
    showCreateDialog.value = false
    await loadData()
  } finally { saving.value = false }
}

async function toggleActive(row: any) {
  await authApi.updateUser(row.id, { is_active: !row.is_active })
  ElMessage.success(row.is_active ? '已禁用' : '已启用')
  await loadData()
}

onMounted(loadData)
</script>

<style scoped>
.card-header { display: flex; justify-content: space-between; align-items: center; }
.card-title { font-weight: bold; font-size: 16px; }
</style>
