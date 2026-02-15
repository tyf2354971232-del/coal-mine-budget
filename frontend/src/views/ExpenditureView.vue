<template>
  <div class="expenditure-view">
    <ReadOnlyBanner :edit-roles="['admin', 'leader', 'department']" />
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span class="card-title">支出管理</span>
          <div>
            <el-button v-if="authStore.canEdit" type="success" @click="showUploadDialog = true">
              <el-icon><Upload /></el-icon> Excel导入
            </el-button>
            <el-button v-if="authStore.canEdit" type="primary" @click="showCreateDialog = true">
              <el-icon><Plus /></el-icon> 录入支出
            </el-button>
          </div>
        </div>
      </template>

      <!-- Filters -->
      <el-form :inline="true" class="filter-form">
        <el-form-item label="子工程">
          <el-select v-model="filters.sub_project_id" clearable filterable placeholder="全部" style="width:180px" @change="loadData">
            <el-option v-for="sp in subProjects" :key="sp.id" :label="sp.name" :value="sp.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="日期范围">
          <el-date-picker v-model="dateRange" type="daterange" range-separator="至"
            start-placeholder="开始日期" end-placeholder="结束日期" @change="handleDateChange" />
        </el-form-item>
        <el-form-item label="来源">
          <el-select v-model="filters.source" clearable style="width:120px" @change="loadData">
            <el-option label="手动录入" value="manual" /><el-option label="Excel导入" value="excel_import" />
            <el-option label="ERP同步" value="erp_sync" />
          </el-select>
        </el-form-item>
      </el-form>

      <!-- Summary -->
      <div class="summary-bar" v-if="summary">
        <el-statistic title="总支出" :value="summary.total" :precision="2" suffix="万元" />
      </div>

      <el-table :data="expenditures" v-loading="loading" stripe border style="width:100%;margin-top:16px">
        <el-table-column prop="record_date" label="日期" width="120" sortable />
        <el-table-column prop="amount" label="金额(万元)" width="130" align="right" sortable>
          <template #default="{ row }">{{ row.amount?.toLocaleString(undefined, { minimumFractionDigits: 2 }) }}</template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="voucher_no" label="凭证号" width="120" />
        <el-table-column prop="source" label="来源" width="100" align="center">
          <template #default="{ row }">
            <el-tag size="small" :type="row.source === 'manual' ? '' : row.source === 'excel_import' ? 'success' : 'warning'">
              {{ row.source === 'manual' ? '手动' : row.source === 'excel_import' ? 'Excel' : 'ERP' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="录入时间" width="170">
          <template #default="{ row }">{{ row.created_at?.replace('T', ' ').substring(0, 19) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="80" align="center" v-if="authStore.isAdmin">
          <template #default="{ row }">
            <el-button type="danger" link size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination v-model:current-page="page" :page-size="50" :total="expenditures.length * 2"
        layout="prev, pager, next" style="margin-top:16px;justify-content:center" @current-change="loadData" />
    </el-card>

    <!-- Create Dialog -->
    <el-dialog v-model="showCreateDialog" title="录入支出" width="550px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="子工程">
          <el-select v-model="form.sub_project_id" filterable style="width:100%">
            <el-option v-for="sp in subProjects" :key="sp.id" :label="sp.name" :value="sp.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="日期">
          <el-date-picker v-model="form.record_date" type="date" style="width:100%" />
        </el-form-item>
        <el-form-item label="金额(万元)">
          <el-input-number v-model="form.amount" :min="0" :precision="2" style="width:100%" />
        </el-form-item>
        <el-form-item label="预算科目">
          <el-select v-model="form.category_id" clearable filterable style="width:100%">
            <el-option v-for="c in flatCategories" :key="c.id" :label="`[${c.code}] ${c.name}`" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述"><el-input v-model="form.description" /></el-form-item>
        <el-form-item label="凭证号"><el-input v-model="form.voucher_no" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleCreate">保存</el-button>
      </template>
    </el-dialog>

    <!-- Upload Dialog -->
    <el-dialog v-model="showUploadDialog" title="Excel批量导入" width="500px">
      <el-alert type="info" :closable="false" style="margin-bottom:16px">
        请下载模板，按格式填写后上传。必填列：子工程ID、日期、金额。可选列：描述、凭证号、科目ID、成本项ID
      </el-alert>
      <el-upload ref="uploadRef" drag :auto-upload="false" :limit="1" accept=".xlsx,.xls,.csv"
        :on-change="handleFileChange">
        <el-icon class="el-icon--upload" :size="40"><Upload /></el-icon>
        <div class="el-upload__text">拖拽文件到此处，或 <em>点击上传</em></div>
        <template #tip><div class="el-upload__tip">支持 .xlsx, .xls, .csv 文件</div></template>
      </el-upload>
      <template #footer>
        <el-button @click="showUploadDialog = false">取消</el-button>
        <el-button type="primary" :loading="uploading" @click="handleUpload">上传导入</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { expenditureApi, budgetApi } from '../api/budget'
import { projectApi } from '../api/projects'
import { useAuthStore } from '../stores/auth'
import ReadOnlyBanner from '../components/common/ReadOnlyBanner.vue'
import dayjs from 'dayjs'

const authStore = useAuthStore()
const loading = ref(false)
const saving = ref(false)
const uploading = ref(false)
const expenditures = ref<any[]>([])
const subProjects = ref<any[]>([])
const flatCategories = ref<any[]>([])
const summary = ref<any>(null)
const page = ref(1)
const dateRange = ref<any>(null)
const showCreateDialog = ref(false)
const showUploadDialog = ref(false)
const uploadFile = ref<File | null>(null)

const filters = reactive({ sub_project_id: null as number | null, source: '', start_date: '', end_date: '' })
const form = reactive({ sub_project_id: null as number | null, record_date: new Date(), amount: 0, category_id: null as number | null, description: '', voucher_no: '' })

function handleDateChange(val: any) {
  if (val) {
    filters.start_date = dayjs(val[0]).format('YYYY-MM-DD')
    filters.end_date = dayjs(val[1]).format('YYYY-MM-DD')
  } else {
    filters.start_date = ''
    filters.end_date = ''
  }
  loadData()
}

function handleFileChange(file: any) {
  uploadFile.value = file.raw
}

async function loadData() {
  loading.value = true
  try {
    const params: any = { page: page.value }
    if (filters.sub_project_id) params.sub_project_id = filters.sub_project_id
    if (filters.source) params.source = filters.source
    if (filters.start_date) params.start_date = filters.start_date
    if (filters.end_date) params.end_date = filters.end_date
    const [expRes, sumRes] = await Promise.all([
      expenditureApi.list(params),
      expenditureApi.summary(params),
    ])
    expenditures.value = expRes.data
    summary.value = sumRes.data
  } finally { loading.value = false }
}

async function loadMeta() {
  const [spRes, catRes] = await Promise.all([projectApi.listSubProjects(), budgetApi.listCategoriesFlat()])
  subProjects.value = spRes.data
  flatCategories.value = catRes.data
}

async function handleCreate() {
  if (!form.sub_project_id) { ElMessage.warning('请选择子工程'); return }
  saving.value = true
  try {
    await expenditureApi.create({
      ...form,
      record_date: dayjs(form.record_date).format('YYYY-MM-DD'),
    })
    ElMessage.success('录入成功')
    showCreateDialog.value = false
    await loadData()
  } finally { saving.value = false }
}

async function handleUpload() {
  if (!uploadFile.value) { ElMessage.warning('请选择文件'); return }
  uploading.value = true
  try {
    const { data } = await expenditureApi.uploadExcel(uploadFile.value)
    ElMessage.success(data.message)
    if (data.errors?.length) {
      ElMessage.warning(`有 ${data.errors.length} 条记录导入失败`)
    }
    showUploadDialog.value = false
    await loadData()
  } finally { uploading.value = false }
}

async function handleDelete(row: any) {
  await ElMessageBox.confirm('确定删除该支出记录？', '提示', { type: 'warning' })
  await expenditureApi.delete(row.id)
  ElMessage.success('删除成功')
  await loadData()
}

onMounted(async () => {
  await loadMeta()
  await loadData()
})
</script>

<style scoped>
.card-header { display: flex; justify-content: space-between; align-items: center; }
.card-title { font-weight: bold; font-size: 16px; }
.filter-form { padding: 12px 0; }
.summary-bar { padding: 12px 16px; background: #f5f7fa; border-radius: 6px; }
</style>
