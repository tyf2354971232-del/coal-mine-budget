<template>
  <div class="project-detail" v-loading="loading">
    <el-page-header @back="$router.back()" :title="'返回'" :content="sp?.name || '工程详情'" />

    <el-row :gutter="16" style="margin-top:20px">
      <!-- Basic Info -->
      <el-col :span="8">
        <el-card shadow="hover">
          <template #header><span class="card-title">基本信息</span></template>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="工程名称">{{ sp?.name }}</el-descriptions-item>
            <el-descriptions-item label="费用类别">{{ sp?.category }}</el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag :type="getStatusType(sp?.status)" effect="dark">{{ getStatusLabel(sp?.status) }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="负责部门">{{ sp?.responsible_dept || '-' }}</el-descriptions-item>
            <el-descriptions-item label="计划周期">{{ formatDate(sp?.planned_start) }} ~ {{ formatDate(sp?.planned_end) }}</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>

      <!-- Budget Info -->
      <el-col :span="8">
        <el-card shadow="hover">
          <template #header><span class="card-title">预算信息</span></template>
          <div class="budget-circle">
            <el-progress type="circle" :percentage="Math.min(100, sp?.budget_usage_rate || 0)"
              :color="sp?.budget_usage_rate >= 90 ? '#F56C6C' : sp?.budget_usage_rate >= 80 ? '#E6A23C' : '#409EFF'"
              :width="140">
              <template #default>
                <div style="text-align:center">
                  <div style="font-size:20px;font-weight:bold">{{ (sp?.budget_usage_rate || 0).toFixed(1) }}%</div>
                  <div style="font-size:12px;color:#909399">预算使用率</div>
                </div>
              </template>
            </el-progress>
          </div>
          <el-descriptions :column="1" border style="margin-top:16px">
            <el-descriptions-item label="分配预算">{{ formatMoney(sp?.allocated_budget) }}</el-descriptions-item>
            <el-descriptions-item label="已支出">
              <span :style="{ color: sp?.is_over_budget ? '#F56C6C' : '', fontWeight: 'bold' }">
                {{ formatMoney(sp?.actual_spent) }}
              </span>
            </el-descriptions-item>
            <el-descriptions-item label="预算剩余">
              {{ formatMoney((sp?.allocated_budget || 0) - (sp?.actual_spent || 0)) }}
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>

      <!-- Progress -->
      <el-col :span="8">
        <el-card shadow="hover">
          <template #header>
            <div style="display:flex;justify-content:space-between;align-items:center">
              <span class="card-title">工程进度</span>
              <el-button v-if="authStore.canEdit" type="primary" size="small" @click="showProgressDialog = true">更新进度</el-button>
            </div>
          </template>
          <div class="progress-circle">
            <el-progress type="circle" :percentage="sp?.progress_percent || 0" color="#67C23A" :width="140">
              <template #default>
                <div style="text-align:center">
                  <div style="font-size:20px;font-weight:bold">{{ (sp?.progress_percent || 0).toFixed(1) }}%</div>
                  <div style="font-size:12px;color:#909399">完成进度</div>
                </div>
              </template>
            </el-progress>
          </div>
          <div v-if="progressRecords.length" style="margin-top:16px;max-height:200px;overflow-y:auto">
            <el-timeline>
              <el-timeline-item v-for="pr in progressRecords.slice(0, 5)" :key="pr.id"
                :timestamp="formatDate(pr.record_date)" placement="top">
                进度 {{ pr.percent }}% {{ pr.note ? `- ${pr.note}` : '' }}
              </el-timeline-item>
            </el-timeline>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Expenditures -->
    <el-card shadow="hover" style="margin-top:16px">
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span class="card-title">支出记录</span>
          <el-button v-if="authStore.canEdit" type="primary" size="small" @click="showExpDialog = true">录入支出</el-button>
        </div>
      </template>
      <el-table :data="expenditures" stripe border max-height="400">
        <el-table-column prop="record_date" label="日期" width="120" />
        <el-table-column prop="amount" label="金额(万元)" width="120" align="right">
          <template #default="{ row }">{{ row.amount?.toLocaleString() }}</template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="200" />
        <el-table-column prop="voucher_no" label="凭证号" width="120" />
        <el-table-column prop="source" label="来源" width="100">
          <template #default="{ row }">
            <el-tag size="small" :type="row.source === 'manual' ? '' : 'success'">
              {{ row.source === 'manual' ? '手动' : row.source === 'excel_import' ? 'Excel' : 'ERP' }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- Progress Dialog -->
    <el-dialog v-model="showProgressDialog" title="更新工程进度" width="450px">
      <el-form :model="progressForm" label-width="80px">
        <el-form-item label="日期">
          <el-date-picker v-model="progressForm.record_date" type="date" style="width:100%" />
        </el-form-item>
        <el-form-item label="进度">
          <el-slider v-model="progressForm.percent" :max="100" show-input />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="progressForm.note" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showProgressDialog = false">取消</el-button>
        <el-button type="primary" @click="saveProgress">保存</el-button>
      </template>
    </el-dialog>

    <!-- Expenditure Dialog -->
    <el-dialog v-model="showExpDialog" title="录入支出" width="500px">
      <el-form :model="expForm" label-width="80px">
        <el-form-item label="日期">
          <el-date-picker v-model="expForm.record_date" type="date" style="width:100%" />
        </el-form-item>
        <el-form-item label="金额(万元)">
          <el-input-number v-model="expForm.amount" :min="0" :precision="2" style="width:100%" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="expForm.description" />
        </el-form-item>
        <el-form-item label="凭证号">
          <el-input v-model="expForm.voucher_no" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showExpDialog = false">取消</el-button>
        <el-button type="primary" @click="saveExpenditure">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { projectApi } from '../api/projects'
import { expenditureApi } from '../api/budget'
import { useAuthStore } from '../stores/auth'
import { formatMoney, formatDate, getStatusType, getStatusLabel } from '../utils/format'
import dayjs from 'dayjs'

const route = useRoute()
const authStore = useAuthStore()
const loading = ref(false)
const sp = ref<any>(null)
const expenditures = ref<any[]>([])
const progressRecords = ref<any[]>([])
const showProgressDialog = ref(false)
const showExpDialog = ref(false)

const progressForm = reactive({ record_date: new Date(), percent: 0, note: '' })
const expForm = reactive({ record_date: new Date(), amount: 0, description: '', voucher_no: '' })

async function loadData() {
  loading.value = true
  try {
    const id = Number(route.params.id)
    const { data } = await projectApi.getSubProject(id)
    sp.value = data
    const expRes = await expenditureApi.list({ sub_project_id: id })
    expenditures.value = expRes.data
    const prRes = await projectApi.listProgress(id)
    progressRecords.value = prRes.data
    progressForm.percent = sp.value.progress_percent || 0
  } finally {
    loading.value = false
  }
}

async function saveProgress() {
  try {
    await projectApi.createProgress({
      sub_project_id: Number(route.params.id),
      record_date: dayjs(progressForm.record_date).format('YYYY-MM-DD'),
      percent: progressForm.percent,
      note: progressForm.note,
    })
    ElMessage.success('进度已更新')
    showProgressDialog.value = false
    await loadData()
  } catch {}
}

async function saveExpenditure() {
  try {
    await expenditureApi.create({
      sub_project_id: Number(route.params.id),
      record_date: dayjs(expForm.record_date).format('YYYY-MM-DD'),
      amount: expForm.amount,
      description: expForm.description,
      voucher_no: expForm.voucher_no,
    })
    ElMessage.success('支出已录入')
    showExpDialog.value = false
    await loadData()
  } catch {}
}

onMounted(loadData)
</script>

<style scoped>
.card-title { font-weight: bold; font-size: 15px; }
.budget-circle, .progress-circle { display: flex; justify-content: center; padding: 12px 0; }
</style>
