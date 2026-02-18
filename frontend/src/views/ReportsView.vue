<template>
  <div class="reports-view">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span class="card-title">月度考核报表</span>
          <div>
            <el-date-picker v-model="selectedMonth" type="month" placeholder="选择月份"
              format="YYYY年MM月" value-format="YYYY-MM" style="width:180px;margin-right:12px" @change="loadReport" />
            <el-button v-if="authStore.isLeader" type="success" @click="exportExcel" :disabled="!report">
              <el-icon><Download /></el-icon> 导出Excel
            </el-button>
          </div>
        </div>
      </template>

      <div v-if="report" v-loading="loading">
        <!-- Overview -->
        <h3 style="margin-bottom:16px">{{ report.report_period }} 月度报表</h3>
        <el-row :gutter="16">
          <el-col :span="4"><el-statistic title="总概算" :value="report.overview.total_budget" :precision="2" suffix="万元" /></el-col>
          <el-col :span="4"><el-statistic title="本月支出" :value="report.overview.monthly_spent" :precision="2" suffix="万元" /></el-col>
          <el-col :span="4"><el-statistic title="累计支出" :value="report.overview.cumulative_spent" :precision="2" suffix="万元" /></el-col>
          <el-col :span="4"><el-statistic title="概算剩余" :value="report.overview.budget_remaining" :precision="2" suffix="万元" /></el-col>
          <el-col :span="4"><el-statistic title="概算使用率" :value="report.overview.budget_usage_rate" :precision="2" suffix="%" /></el-col>
          <el-col :span="4"><el-statistic title="弹性预备金" :value="report.overview.reserve_budget" :precision="2" suffix="万元" /></el-col>
        </el-row>

        <el-divider />

        <!-- Category Summary -->
        <h4>费用类别汇总</h4>
        <el-table :data="report.category_summary" border style="width:100%;margin-top:12px" size="small">
          <el-table-column prop="name" label="类别" width="140" />
          <el-table-column prop="budget" label="概算(万元)" width="130" align="right">
            <template #default="{ row }">{{ row.budget?.toLocaleString() }}</template>
          </el-table-column>
          <el-table-column prop="monthly_spent" label="本月支出(万元)" width="140" align="right">
            <template #default="{ row }">{{ row.monthly_spent?.toLocaleString() }}</template>
          </el-table-column>
          <el-table-column prop="cumulative_spent" label="累计支出(万元)" width="140" align="right">
            <template #default="{ row }">{{ row.cumulative_spent?.toLocaleString() }}</template>
          </el-table-column>
          <el-table-column label="使用率" width="160">
            <template #default="{ row }">
              <el-progress :percentage="Math.min(100, row.usage_rate)" :color="row.usage_rate >= 90 ? '#F56C6C' : row.usage_rate >= 80 ? '#E6A23C' : '#409EFF'" :stroke-width="8" />
            </template>
          </el-table-column>
        </el-table>

        <el-divider />

        <!-- Sub-project Details -->
        <h4>子工程执行情况</h4>
        <el-table :data="report.sub_projects" border stripe style="width:100%;margin-top:12px" size="small" max-height="400">
          <el-table-column prop="name" label="工程名称" min-width="180" fixed show-overflow-tooltip />
          <el-table-column prop="category" label="类别" width="100" />
          <el-table-column prop="allocated_budget" label="概算" width="100" align="right">
            <template #default="{ row }">{{ row.allocated_budget?.toLocaleString() }}</template>
          </el-table-column>
          <el-table-column prop="monthly_spent" label="本月支出" width="100" align="right">
            <template #default="{ row }">{{ row.monthly_spent?.toLocaleString() }}</template>
          </el-table-column>
          <el-table-column prop="cumulative_spent" label="累计支出" width="100" align="right">
            <template #default="{ row }">{{ row.cumulative_spent?.toLocaleString() }}</template>
          </el-table-column>
          <el-table-column label="概算使用率" width="130">
            <template #default="{ row }">
              <el-progress :percentage="Math.min(100, row.budget_usage_rate)" :color="row.risk_level === 'red' ? '#F56C6C' : row.risk_level === 'yellow' ? '#E6A23C' : '#409EFF'" :stroke-width="8" />
            </template>
          </el-table-column>
          <el-table-column prop="progress_percent" label="工程进度" width="130">
            <template #default="{ row }">
              <el-progress :percentage="row.progress_percent" color="#67C23A" :stroke-width="8" />
            </template>
          </el-table-column>
          <el-table-column prop="schedule_status" label="工期" width="70" align="center">
            <template #default="{ row }">
              <el-tag :type="row.schedule_status === '滞后' ? 'danger' : row.schedule_status === '超前' ? 'success' : 'info'" size="small">
                {{ row.schedule_status }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="风险" width="60" align="center">
            <template #default="{ row }">
              <span :style="{ color: row.risk_level === 'red' ? '#F56C6C' : row.risk_level === 'yellow' ? '#E6A23C' : '#67C23A', fontSize: '16px' }">●</span>
            </template>
          </el-table-column>
        </el-table>

        <el-divider />

        <!-- Forecast & Recommendations -->
        <el-row :gutter="16">
          <el-col :span="12">
            <el-card shadow="never">
              <template #header><span style="font-weight:bold">下月预测</span></template>
              <el-descriptions :column="1" border>
                <el-descriptions-item label="预估支出">{{ report.forecast?.next_month_estimated?.toLocaleString() }}万元</el-descriptions-item>
                <el-descriptions-item label="概算可撑月数">{{ report.forecast?.remaining_months_budget || '充裕' }}个月</el-descriptions-item>
              </el-descriptions>
            </el-card>
          </el-col>
          <el-col :span="12">
            <el-card shadow="never">
              <template #header><span style="font-weight:bold">系统建议</span></template>
              <div v-for="(rec, i) in report.recommendations" :key="i" style="padding:6px 0;font-size:14px;line-height:1.8">
                {{ rec }}
              </div>
            </el-card>
          </el-col>
        </el-row>

        <!-- Alerts -->
        <el-card shadow="never" style="margin-top:16px">
          <template #header><span style="font-weight:bold">本月预警汇总</span></template>
          <span>红色预警 <el-tag type="danger">{{ report.alerts_count?.red }}</el-tag> 条，
            黄色预警 <el-tag type="warning">{{ report.alerts_count?.yellow }}</el-tag> 条，
            共 <el-tag>{{ report.alerts_count?.total }}</el-tag> 条</span>
        </el-card>
      </div>
      <el-empty v-else description="请选择月份生成报表" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { reportApi } from '../api/simulation'
import { useAuthStore } from '../stores/auth'
import dayjs from 'dayjs'
import * as XLSX from 'xlsx'

const authStore = useAuthStore()

const loading = ref(false)
const selectedMonth = ref(dayjs().format('YYYY-MM'))
const report = ref<any>(null)

async function loadReport() {
  if (!selectedMonth.value) return
  loading.value = true
  try {
    const [y, m] = selectedMonth.value.split('-').map(Number)
    const { data } = await reportApi.monthly(y, m)
    report.value = data
  } catch {
    report.value = null
  } finally { loading.value = false }
}

function exportExcel() {
  if (!report.value) return
  const wb = XLSX.utils.book_new()

  // Sheet 1: 报表概览
  const overviewRows = [
    ['指标', '数值'],
    ['报表周期', report.value.report_period],
    ['总概算(万元)', report.value.overview.total_budget],
    ['弹性预备金(万元)', report.value.overview.reserve_budget],
    ['可用概算(万元)', report.value.overview.usable_budget],
    ['本月支出(万元)', report.value.overview.monthly_spent],
    ['累计支出(万元)', report.value.overview.cumulative_spent],
    ['概算剩余(万元)', report.value.overview.budget_remaining],
    ['概算使用率(%)', report.value.overview.budget_usage_rate],
  ]
  const ws1 = XLSX.utils.aoa_to_sheet(overviewRows)
  ws1['!cols'] = [{ wch: 20 }, { wch: 18 }]
  XLSX.utils.book_append_sheet(wb, ws1, '报表概览')

  // Sheet 2: 费用类别汇总
  const catHeader = ['类别', '概算(万元)', '本月支出(万元)', '累计支出(万元)', '使用率(%)']
  const catRows = (report.value.category_summary || []).map((c: any) => [
    c.name, c.budget, c.monthly_spent, c.cumulative_spent, c.usage_rate
  ])
  const ws2 = XLSX.utils.aoa_to_sheet([catHeader, ...catRows])
  ws2['!cols'] = [{ wch: 16 }, { wch: 14 }, { wch: 16 }, { wch: 16 }, { wch: 12 }]
  XLSX.utils.book_append_sheet(wb, ws2, '费用类别汇总')

  // Sheet 3: 子工程执行情况
  const spHeader = ['工程名称', '类别', '概算(万元)', '本月支出(万元)', '累计支出(万元)', '概算使用率(%)', '工程进度(%)', '工期状态', '风险等级']
  const spRows = (report.value.sub_projects || []).map((sp: any) => [
    sp.name, sp.category, sp.allocated_budget, sp.monthly_spent,
    sp.cumulative_spent, sp.budget_usage_rate, sp.progress_percent,
    sp.schedule_status, sp.risk_level === 'red' ? '红色' : sp.risk_level === 'yellow' ? '黄色' : '绿色'
  ])
  const ws3 = XLSX.utils.aoa_to_sheet([spHeader, ...spRows])
  ws3['!cols'] = [{ wch: 24 }, { wch: 10 }, { wch: 14 }, { wch: 16 }, { wch: 16 }, { wch: 14 }, { wch: 12 }, { wch: 10 }, { wch: 10 }]
  XLSX.utils.book_append_sheet(wb, ws3, '子工程执行情况')

  // Sheet 4: 预测与建议
  const recRows: any[][] = [
    ['下月预测'],
    ['预估支出(万元)', report.value.forecast?.next_month_estimated],
    ['概算可撑月数', report.value.forecast?.remaining_months_budget || '充裕'],
    [],
    ['预警汇总'],
    ['红色预警(条)', report.value.alerts_count?.red],
    ['黄色预警(条)', report.value.alerts_count?.yellow],
    ['总计(条)', report.value.alerts_count?.total],
    [],
    ['系统建议'],
  ]
  ;(report.value.recommendations || []).forEach((r: string) => recRows.push([r]))
  const ws4 = XLSX.utils.aoa_to_sheet(recRows)
  ws4['!cols'] = [{ wch: 50 }, { wch: 18 }]
  XLSX.utils.book_append_sheet(wb, ws4, '预测与建议')

  // 导出文件
  XLSX.writeFile(wb, `月度报表_${report.value.report_period}.xlsx`)
  ElMessage.success('Excel导出成功')
}

onMounted(loadReport)
</script>

<style scoped>
.card-header { display: flex; justify-content: space-between; align-items: center; }
.card-title { font-weight: bold; font-size: 16px; }
</style>
