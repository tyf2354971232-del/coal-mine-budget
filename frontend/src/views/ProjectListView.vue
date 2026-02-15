<template>
  <div class="project-list">
    <ReadOnlyBanner :edit-roles="['admin', 'leader', 'department']" />
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span class="card-title">工程项目管理</span>
          <div class="header-actions">
            <el-select v-model="filterCategory" placeholder="按类别筛选" clearable style="width:160px;margin-right:12px">
              <el-option v-for="c in BUDGET_CATEGORIES" :key="c" :label="c" :value="c" />
            </el-select>
            <el-select v-model="filterStatus" placeholder="按状态筛选" clearable style="width:120px;margin-right:12px">
              <el-option label="未开始" value="not_started" /><el-option label="进行中" value="in_progress" />
              <el-option label="已完成" value="completed" /><el-option label="已延期" value="delayed" />
            </el-select>
            <el-button v-if="authStore.canEdit" type="primary" @click="showCreateDialog = true">
              <el-icon><Plus /></el-icon> 新增子工程
            </el-button>
          </div>
        </div>
      </template>

      <el-table :data="filteredProjects" v-loading="loading" stripe border style="width:100%" row-key="id"
        :default-sort="{ prop: 'sort_order', order: 'ascending' }">
        <el-table-column prop="sort_order" label="序号" width="60" align="center" />
        <el-table-column prop="name" label="工程名称" min-width="200">
          <template #default="{ row }">
            <el-link type="primary" @click="$router.push(`/projects/${row.id}`)">{{ row.name }}</el-link>
          </template>
        </el-table-column>
        <el-table-column prop="category" label="费用类别" width="120" />
        <el-table-column prop="allocated_budget" label="预算(万元)" width="120" align="right">
          <template #default="{ row }">{{ row.allocated_budget?.toLocaleString() }}</template>
        </el-table-column>
        <el-table-column prop="actual_spent" label="已支出(万元)" width="120" align="right">
          <template #default="{ row }">
            <span :style="{ color: row.actual_spent > row.allocated_budget ? '#F56C6C' : '' }">
              {{ row.actual_spent?.toLocaleString() }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="预算使用率" width="160">
          <template #default="{ row }">
            <el-progress
              :percentage="Math.min(100, row.budget_usage_rate || 0)"
              :color="row.budget_usage_rate >= 90 ? '#F56C6C' : row.budget_usage_rate >= 80 ? '#E6A23C' : '#409EFF'"
              :stroke-width="10"
            />
          </template>
        </el-table-column>
        <el-table-column label="工程进度" width="160">
          <template #default="{ row }">
            <el-progress :percentage="row.progress_percent" :color="'#67C23A'" :stroke-width="10" />
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small" effect="dark">{{ getStatusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="计划周期" width="200">
          <template #default="{ row }">{{ formatDate(row.planned_start) }} ~ {{ formatDate(row.planned_end) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="100" align="center" v-if="authStore.canEdit">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="editProject(row)">编辑</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="summary-bar">
        共 {{ filteredProjects.length }} 个子工程 |
        总预算 {{ formatMoney(totalBudget) }} |
        总支出 {{ formatMoney(totalSpent) }} |
        总体使用率 {{ totalBudget > 0 ? (totalSpent / totalBudget * 100).toFixed(1) : 0 }}%
      </div>
    </el-card>

    <!-- Create/Edit Dialog -->
    <el-dialog v-model="showCreateDialog" :title="editingProject ? '编辑子工程' : '新增子工程'" width="600px" @close="resetForm">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="工程名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入工程名称" />
        </el-form-item>
        <el-form-item label="费用类别" prop="category">
          <el-select v-model="form.category" style="width:100%">
            <el-option v-for="c in BUDGET_CATEGORIES" :key="c" :label="c" :value="c" />
          </el-select>
        </el-form-item>
        <el-form-item label="预算金额" prop="allocated_budget">
          <el-input-number v-model="form.allocated_budget" :min="0" :precision="2" style="width:100%" />
          <span style="margin-left:8px;color:#909399">万元</span>
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="计划开始">
              <el-date-picker v-model="form.planned_start" type="date" style="width:100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="计划结束">
              <el-date-picker v-model="form.planned_end" type="date" style="width:100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="负责部门">
          <el-input v-model="form.responsible_dept" placeholder="如：工程部" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { projectApi } from '../api/projects'
import { useAuthStore } from '../stores/auth'
import { formatMoney, formatDate, getStatusType, getStatusLabel, BUDGET_CATEGORIES } from '../utils/format'
import ReadOnlyBanner from '../components/common/ReadOnlyBanner.vue'

const authStore = useAuthStore()
const loading = ref(false)
const saving = ref(false)
const subProjects = ref<any[]>([])
const filterCategory = ref('')
const filterStatus = ref('')
const showCreateDialog = ref(false)
const editingProject = ref<any>(null)
const formRef = ref()

const form = reactive({
  name: '', category: '矿建工程费', allocated_budget: 0,
  planned_start: '', planned_end: '', responsible_dept: '', description: '',
})
const rules = {
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }],
  category: [{ required: true, message: '请选择类别', trigger: 'change' }],
}

const filteredProjects = computed(() => {
  return subProjects.value.filter(sp => {
    if (filterCategory.value && sp.category !== filterCategory.value) return false
    if (filterStatus.value && sp.status !== filterStatus.value) return false
    return true
  })
})

const totalBudget = computed(() => filteredProjects.value.reduce((s, p) => s + (p.allocated_budget || 0), 0))
const totalSpent = computed(() => filteredProjects.value.reduce((s, p) => s + (p.actual_spent || 0), 0))

async function loadData() {
  loading.value = true
  try {
    const { data } = await projectApi.listSubProjects()
    subProjects.value = data
  } finally {
    loading.value = false
  }
}

function editProject(row: any) {
  editingProject.value = row
  Object.assign(form, {
    name: row.name, category: row.category, allocated_budget: row.allocated_budget,
    planned_start: row.planned_start, planned_end: row.planned_end,
    responsible_dept: row.responsible_dept || '', description: row.description || '',
  })
  showCreateDialog.value = true
}

function resetForm() {
  editingProject.value = null
  Object.assign(form, { name: '', category: '矿建工程费', allocated_budget: 0, planned_start: '', planned_end: '', responsible_dept: '', description: '' })
}

async function handleSave() {
  try { await formRef.value?.validate() } catch { return }
  saving.value = true
  try {
    if (editingProject.value) {
      await projectApi.updateSubProject(editingProject.value.id, form)
      ElMessage.success('更新成功')
    } else {
      // Find the first project to attach to
      const projects = (await projectApi.list()).data
      if (!projects.length) { ElMessage.error('请先创建主项目'); return }
      await projectApi.createSubProject({ ...form, project_id: projects[0].id })
      ElMessage.success('创建成功')
    }
    showCreateDialog.value = false
    await loadData()
  } finally {
    saving.value = false
  }
}

onMounted(loadData)
</script>

<style scoped>
.card-header { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; }
.card-title { font-weight: bold; font-size: 16px; }
.summary-bar { margin-top: 16px; padding: 12px; background: #f5f7fa; border-radius: 6px; font-size: 14px; color: #606266; }
</style>
