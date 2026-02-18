<template>
  <div class="budget-view">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span class="card-title">概算科目管理</span>
          <el-button v-if="authStore.isLeader" type="primary" @click="showCreateDialog = true">
            <el-icon><Plus /></el-icon> 新增科目
          </el-button>
        </div>
      </template>

      <el-table :data="categories" v-loading="loading" row-key="id" border default-expand-all
        :tree-props="{ children: 'children', hasChildren: 'hasChildren' }">
        <el-table-column prop="name" label="科目名称" min-width="220" />
        <el-table-column prop="code" label="编码" width="120" />
        <el-table-column prop="level" label="层级" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.level === 1 ? 'danger' : row.level === 2 ? 'warning' : 'info'" size="small">
              {{ row.level === 1 ? '一级' : row.level === 2 ? '二级' : '三级' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="budget_amount" label="概算(万元)" width="130" align="right">
          <template #default="{ row }">{{ row.budget_amount?.toLocaleString() }}</template>
        </el-table-column>
        <el-table-column prop="actual_spent" label="已支出(万元)" width="130" align="right">
          <template #default="{ row }">
            <span :style="{ color: row.actual_spent > row.budget_amount ? '#F56C6C' : '' }">
              {{ (row.actual_spent || 0).toLocaleString() }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="使用率" width="150">
          <template #default="{ row }">
            <el-progress
              v-if="row.budget_amount > 0"
              :percentage="Math.min(100, (row.actual_spent || 0) / row.budget_amount * 100)"
              :color="(row.actual_spent || 0) / row.budget_amount >= 0.9 ? '#F56C6C' : (row.actual_spent || 0) / row.budget_amount >= 0.8 ? '#E6A23C' : '#409EFF'"
              :stroke-width="8"
            />
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" align="center" v-if="authStore.isLeader">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="editCat(row)">编辑</el-button>
            <el-button type="danger" link size="small" @click="deleteCat(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="showCreateDialog" :title="editingCat ? '编辑科目' : '新增科目'" width="500px" @close="resetForm">
      <el-form :model="form" label-width="80px">
        <el-form-item label="科目名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="科目编码"><el-input v-model="form.code" /></el-form-item>
        <el-form-item label="层级">
          <el-radio-group v-model="form.level">
            <el-radio :value="1">一级</el-radio><el-radio :value="2">二级</el-radio><el-radio :value="3">三级</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="父级科目" v-if="form.level > 1">
          <el-select v-model="form.parent_id" filterable style="width:100%">
            <el-option v-for="c in flatCategories.filter(fc => fc.level < form.level)" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="概算金额">
          <el-input-number v-model="form.budget_amount" :min="0" :precision="2" style="width:100%" />
        </el-form-item>
        <el-form-item label="描述"><el-input v-model="form.description" type="textarea" /></el-form-item>
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
import { ElMessage, ElMessageBox } from 'element-plus'
import { budgetApi } from '../api/budget'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const loading = ref(false)
const saving = ref(false)
const categories = ref<any[]>([])
const flatCategories = ref<any[]>([])
const showCreateDialog = ref(false)
const editingCat = ref<any>(null)
const form = reactive({ name: '', code: '', level: 1, parent_id: null as number | null, budget_amount: 0, description: '' })

async function loadData() {
  loading.value = true
  try {
    const [treeRes, flatRes] = await Promise.all([budgetApi.listCategories(), budgetApi.listCategoriesFlat()])
    categories.value = treeRes.data
    flatCategories.value = flatRes.data
  } finally { loading.value = false }
}

function editCat(row: any) {
  editingCat.value = row
  Object.assign(form, { name: row.name, code: row.code, level: row.level, parent_id: row.parent_id, budget_amount: row.budget_amount, description: row.description || '' })
  showCreateDialog.value = true
}

function resetForm() {
  editingCat.value = null
  Object.assign(form, { name: '', code: '', level: 1, parent_id: null, budget_amount: 0, description: '' })
}

async function handleSave() {
  saving.value = true
  try {
    if (editingCat.value) {
      await budgetApi.updateCategory(editingCat.value.id, form)
      ElMessage.success('更新成功')
    } else {
      await budgetApi.createCategory(form)
      ElMessage.success('创建成功')
    }
    showCreateDialog.value = false
    await loadData()
  } finally { saving.value = false }
}

async function deleteCat(row: any) {
  await ElMessageBox.confirm(`确定删除科目「${row.name}」？`, '提示', { type: 'warning' })
  await budgetApi.deleteCategory(row.id)
  ElMessage.success('删除成功')
  await loadData()
}

onMounted(loadData)
</script>

<style scoped>
.card-header { display: flex; justify-content: space-between; align-items: center; }
.card-title { font-weight: bold; font-size: 16px; }
</style>
