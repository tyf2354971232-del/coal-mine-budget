<template>
  <div class="cashflow-page" v-loading="loading">
    <!-- Summary Cards -->
    <el-row :gutter="16" class="summary-row">
      <el-col :span="6">
        <el-card shadow="hover" class="summary-card">
          <el-statistic title="累计流入(拨款)" :value="summary.total_inflow" :precision="2" suffix="万元" />
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="summary-card">
          <el-statistic title="累计流出(支出)" :value="summary.total_outflow" :precision="2" suffix="万元" />
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="summary-card">
          <el-statistic title="净额" :value="summary.net_amount" :precision="2" suffix="万元" />
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="summary-card">
          <el-statistic title="待审批" :value="summary.pending_count" suffix="笔" />
        </el-card>
      </el-col>
    </el-row>

    <!-- Chart -->
    <el-card shadow="hover" class="chart-card">
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span class="card-title">月度现金流趋势</span>
          <div>
            <el-button type="primary" @click="showDialog = true" :disabled="!canWrite">新增记录</el-button>
            <el-button @click="exportData">导出Excel</el-button>
          </div>
        </div>
      </template>
      <div ref="chartRef" style="height: 300px;"></div>
    </el-card>

    <!-- Filters -->
    <el-card shadow="hover" style="margin-top:16px">
      <el-row :gutter="16" align="middle">
        <el-col :span="5">
          <el-select v-model="filters.flow_type" placeholder="类型" clearable style="width:100%">
            <el-option label="全部" value="" />
            <el-option label="流入(拨款)" value="inflow" />
            <el-option label="流出(支出)" value="outflow" />
          </el-select>
        </el-col>
        <el-col :span="5">
          <el-select v-model="filters.status" placeholder="状态" clearable style="width:100%">
            <el-option label="全部" value="" />
            <el-option label="待审批" value="pending" />
            <el-option label="已审批" value="approved" />
            <el-option label="已支付" value="paid" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </el-col>
        <el-col :span="8">
          <el-date-picker v-model="dateRange" type="daterange" range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期" style="width:100%" />
        </el-col>
        <el-col :span="3">
          <el-button type="primary" @click="loadData">查询</el-button>
        </el-col>
      </el-row>

      <!-- Data Table -->
      <el-table :data="records" style="margin-top:16px" stripe border>
        <el-table-column prop="record_date" label="日期" width="120" />
        <el-table-column label="类型" width="120">
          <template #default="{ row }">
            <el-tag :type="row.flow_type === 'inflow' ? 'success' : 'danger'" size="small">
              {{ row.flow_type === 'inflow' ? '流入' : '流出' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="amount" label="金额(万元)" width="130" align="right">
          <template #default="{ row }">{{ row.amount?.toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="payee" label="收款方/付款方" min-width="150" show-overflow-tooltip />
        <el-table-column prop="category" label="用途" width="140" show-overflow-tooltip />
        <el-table-column prop="description" label="说明" min-width="200" show-overflow-tooltip />
        <el-table-column prop="voucher_no" label="凭证号" width="120" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'paid' ? 'success' : row.status === 'approved' ? '' : row.status === 'pending' ? 'warning' : 'info'" size="small">
              {{ statusMap[row.status] || row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right" v-if="canWrite">
          <template #default="{ row }">
            <el-button size="small" @click="editRecord(row)">编辑</el-button>
            <el-button size="small" type="success" v-if="row.status === 'pending'" @click="approveRecord(row)">审批</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- Dialog -->
    <el-dialog :title="editingId ? '编辑记录' : '新增现金流记录'" v-model="showDialog" width="600px" @closed="resetForm">
      <el-form :model="form" label-width="100px">
        <el-form-item label="类型" required>
          <el-radio-group v-model="form.flow_type">
            <el-radio value="outflow">流出(支出)</el-radio>
            <el-radio value="inflow">流入(拨款)</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="金额(万元)" required>
          <el-input-number v-model="form.amount" :min="0" :precision="2" style="width:100%" />
        </el-form-item>
        <el-form-item label="日期" required>
          <el-date-picker v-model="form.record_date" type="date" style="width:100%" />
        </el-form-item>
        <el-form-item label="收款方">
          <el-input v-model="form.payee" />
        </el-form-item>
        <el-form-item label="用途分类">
          <el-select v-model="form.category" allow-create filterable style="width:100%">
            <el-option label="工程款" value="工程款" />
            <el-option label="设备款" value="设备款" />
            <el-option label="材料款" value="材料款" />
            <el-option label="人工费" value="人工费" />
            <el-option label="管理费" value="管理费" />
            <el-option label="设计费" value="设计费" />
            <el-option label="监理费" value="监理费" />
            <el-option label="运输费" value="运输费" />
            <el-option label="拨款" value="拨款" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>
        <el-form-item label="付款方式">
          <el-select v-model="form.payment_method" style="width:100%">
            <el-option label="银行转账" value="银行转账" />
            <el-option label="支票" value="支票" />
            <el-option label="现金" value="现金" />
            <el-option label="承兑汇票" value="承兑汇票" />
          </el-select>
        </el-form-item>
        <el-form-item label="凭证号">
          <el-input v-model="form.voucher_no" />
        </el-form-item>
        <el-form-item label="说明">
          <el-input v-model="form.description" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status" style="width:100%">
            <el-option label="待审批" value="pending" />
            <el-option label="已审批" value="approved" />
            <el-option label="已支付" value="paid" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitting">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import { cashflowApi } from '../api/cashflow'
import { useAuthStore } from '../stores/auth'
import dayjs from 'dayjs'

const authStore = useAuthStore()
const canWrite = computed(() => ['admin', 'leader', 'department'].includes(authStore.user?.role || ''))

const loading = ref(false)
const submitting = ref(false)
const records = ref<any[]>([])
const summary = ref<any>({ total_inflow: 0, total_outflow: 0, net_amount: 0, pending_count: 0, monthly_data: [] })
const showDialog = ref(false)
const editingId = ref<number | null>(null)
const chartRef = ref<HTMLElement>()
const dateRange = ref<any>(null)
const filters = ref({ flow_type: '', status: '' })
const statusMap: Record<string, string> = { pending: '待审批', approved: '已审批', paid: '已支付', cancelled: '已取消' }

const form = ref({
  flow_type: 'outflow',
  amount: 0,
  record_date: new Date(),
  payee: '',
  category: '',
  payment_method: '银行转账',
  voucher_no: '',
  description: '',
  status: 'paid',
})

async function loadData() {
  loading.value = true
  try {
    const params: any = {}
    if (filters.value.flow_type) params.flow_type = filters.value.flow_type
    if (filters.value.status) params.status = filters.value.status
    if (dateRange.value?.[0]) params.start_date = dayjs(dateRange.value[0]).format('YYYY-MM-DD')
    if (dateRange.value?.[1]) params.end_date = dayjs(dateRange.value[1]).format('YYYY-MM-DD')
    const [listRes, sumRes] = await Promise.all([cashflowApi.list(params), cashflowApi.summary()])
    records.value = listRes.data
    summary.value = sumRes.data
    await nextTick()
    renderChart()
  } finally {
    loading.value = false
  }
}

function renderChart() {
  if (!chartRef.value) return
  const chart = echarts.init(chartRef.value)
  const data = summary.value.monthly_data || []
  chart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['流入(拨款)', '流出(支出)'], top: 5 },
    grid: { left: 60, right: 20, top: 40, bottom: 30 },
    xAxis: { type: 'category', data: data.map((d: any) => d.month) },
    yAxis: { type: 'value', name: '万元' },
    series: [
      { name: '流入(拨款)', type: 'bar', data: data.map((d: any) => d.inflow), itemStyle: { color: '#67C23A' }, barMaxWidth: 30 },
      { name: '流出(支出)', type: 'bar', data: data.map((d: any) => d.outflow), itemStyle: { color: '#F56C6C' }, barMaxWidth: 30 },
    ]
  })
  window.addEventListener('resize', () => chart.resize())
}

function editRecord(row: any) {
  editingId.value = row.id
  Object.assign(form.value, {
    flow_type: row.flow_type,
    amount: row.amount,
    record_date: row.record_date,
    payee: row.payee || '',
    category: row.category || '',
    payment_method: row.payment_method || '银行转账',
    voucher_no: row.voucher_no || '',
    description: row.description || '',
    status: row.status,
  })
  showDialog.value = true
}

async function approveRecord(row: any) {
  try {
    await cashflowApi.approve(row.id)
    ElMessage.success('审批通过')
    loadData()
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '审批失败')
  }
}

async function submitForm() {
  submitting.value = true
  try {
    const payload = {
      ...form.value,
      record_date: dayjs(form.value.record_date).format('YYYY-MM-DD'),
    }
    if (editingId.value) {
      await cashflowApi.update(editingId.value, payload)
      ElMessage.success('更新成功')
    } else {
      await cashflowApi.create(payload)
      ElMessage.success('创建成功')
    }
    showDialog.value = false
    loadData()
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '操作失败')
  } finally {
    submitting.value = false
  }
}

function resetForm() {
  editingId.value = null
  Object.assign(form.value, {
    flow_type: 'outflow', amount: 0, record_date: new Date(),
    payee: '', category: '', payment_method: '银行转账',
    voucher_no: '', description: '', status: 'paid',
  })
}

async function exportData() {
  try {
    const res = await cashflowApi.export()
    const blob = new Blob([res.data])
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    const ct = res.headers['content-type'] || ''
    link.download = ct.includes('spreadsheet') ? '现金流记录.xlsx' : '现金流记录.json'
    link.click()
    URL.revokeObjectURL(url)
  } catch {
    ElMessage.error('导出失败')
  }
}

onMounted(loadData)
</script>

<style scoped>
.cashflow-page { max-width: 1600px; margin: 0 auto; }
.summary-row { margin-bottom: 16px; }
.summary-card { text-align: center; }
.chart-card { margin-bottom: 0; }
.card-title { font-weight: bold; font-size: 15px; }
</style>
