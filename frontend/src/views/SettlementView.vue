<template>
  <div class="settlement-page" v-loading="loading">
    <!-- Summary Cards -->
    <el-row :gutter="16" class="summary-row">
      <el-col :span="8">
        <el-card shadow="hover" class="summary-card civil-card">
          <el-statistic title="土建工程决算入账 (元)" :value="overview.civil_total" :precision="2" />
          <div class="sub-info">共 {{ overview.civil_items }} 项工程</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" class="summary-card proc-card">
          <el-statistic title="塔国采购合计 (索莫尼)" :value="overview.procurement_total_somoni" :precision="2" />
          <div class="sub-info">共 {{ overview.procurement_records }} 条采购明细</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" class="summary-card wh-card">
          <el-statistic title="来塔物资出库合计 (元)" :value="overview.warehouse_total" :precision="2" />
          <div class="sub-info">共 {{ overview.warehouse_records }} 条出库记录</div>
        </el-card>
      </el-col>
    </el-row>

    <el-tabs v-model="activeTab" type="border-card" class="data-tabs">
      <!-- Tab 1: 土建工程决算 -->
      <el-tab-pane label="土建工程决算" name="civil">
        <el-table :data="civilData" stripe border style="width:100%" :span-method="civilSpanMethod">
          <el-table-column prop="seq" label="序号" width="60" align="center" />
          <el-table-column prop="project_name" label="工程名称" min-width="180" show-overflow-tooltip />
          <el-table-column label="审核金额(元)" width="150" align="right">
            <template #default="{ row }">
              {{ row.audit_amount?.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) ?? '-' }}
            </template>
          </el-table-column>
          <el-table-column label="80%入账金额(元)" width="160" align="right">
            <template #default="{ row }">
              {{ row.settlement_amount?.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}
            </template>
          </el-table-column>
          <el-table-column label="拟付款计划(元)" width="150" align="right">
            <template #default="{ row }">
              {{ row.payment_plan?.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) ?? '' }}
            </template>
          </el-table-column>
          <el-table-column label="索莫尼" width="110" align="right">
            <template #default="{ row }">
              {{ row.somoni_amount?.toLocaleString('zh-CN', { minimumFractionDigits: 2 }) ?? '' }}
            </template>
          </el-table-column>
          <el-table-column label="欠款(索莫尼)" width="120" align="right">
            <template #default="{ row }">
              <span v-if="row.debt_somoni" :class="{ 'text-danger': row.debt_somoni > 0 }">
                {{ row.debt_somoni?.toLocaleString('zh-CN', { minimumFractionDigits: 2 }) }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="contractor" label="施工单位" width="90" align="center" />
        </el-table>
        <div class="total-row">
          合计审核金额：<strong>{{ civilAuditTotal.toLocaleString('zh-CN', { minimumFractionDigits: 2 }) }} 元</strong>
          &nbsp;&nbsp;|&nbsp;&nbsp;
          合计入账金额(80%)：<strong>{{ civilTotal.toLocaleString('zh-CN', { minimumFractionDigits: 2 }) }} 元</strong>
          &nbsp;&nbsp;|&nbsp;&nbsp;
          合计欠款：<strong class="text-danger">{{ civilDebtTotal.toLocaleString('zh-CN', { minimumFractionDigits: 2 }) }} 索莫尼</strong>
        </div>
      </el-tab-pane>

      <!-- Tab 2: 塔国采购物资 -->
      <el-tab-pane label="塔国采购物资" name="procurement">
        <!-- Monthly Summary Chart -->
        <el-card shadow="never" style="margin-bottom:16px">
          <template #header><span class="card-title">月度采购趋势（索莫尼）</span></template>
          <div ref="procChartRef" style="height: 280px;"></div>
        </el-card>

        <!-- Filters -->
        <el-row :gutter="16" style="margin-bottom:12px" align="middle">
          <el-col :span="4">
            <el-select v-model="procFilters.month" placeholder="月份" clearable style="width:100%">
              <el-option v-for="m in 12" :key="m" :label="`${m}月`" :value="m" />
            </el-select>
          </el-col>
          <el-col :span="5">
            <el-input v-model="procFilters.material_name" placeholder="物资名称" clearable />
          </el-col>
          <el-col :span="5">
            <el-input v-model="procFilters.project_name" placeholder="工程名称" clearable />
          </el-col>
          <el-col :span="3">
            <el-button type="primary" @click="loadProcurementRecords">查询</el-button>
          </el-col>
          <el-col :span="7" style="text-align:right">
            <span class="record-count">共 {{ procTotal }} 条记录</span>
          </el-col>
        </el-row>

        <el-table :data="procRecords" stripe border style="width:100%" max-height="500">
          <el-table-column prop="seq" label="序号" width="70" align="center" />
          <el-table-column prop="month" label="月份" width="70" align="center">
            <template #default="{ row }">{{ row.month }}月</template>
          </el-table-column>
          <el-table-column prop="material_name" label="物资名称" min-width="150" show-overflow-tooltip />
          <el-table-column prop="specification" label="规格型号" width="130" show-overflow-tooltip />
          <el-table-column prop="unit" label="单位" width="70" align="center" />
          <el-table-column prop="purchase_quantity" label="采购数量" width="100" align="right">
            <template #default="{ row }">{{ row.purchase_quantity ?? '-' }}</template>
          </el-table-column>
          <el-table-column label="采购金额(索莫尼)" width="160" align="right">
            <template #default="{ row }">
              {{ row.purchase_amount_somoni?.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) ?? '-' }}
            </template>
          </el-table-column>
          <el-table-column label="金额(人民币元)" width="140" align="right">
            <template #default="{ row }">
              {{ row.amount_rmb?.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) ?? '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="purchase_method" label="采购方式" width="90" />
          <el-table-column prop="payment_method" label="付款方式" width="90" />
          <el-table-column prop="project_name" label="工程名称" min-width="160" show-overflow-tooltip />
        </el-table>

        <el-pagination
          v-if="procTotal > procPageSize"
          style="margin-top:12px;justify-content:center"
          layout="prev, pager, next, jumper, total"
          :total="procTotal"
          :page-size="procPageSize"
          v-model:current-page="procPage"
          @current-change="loadProcurementRecords"
        />
      </el-tab-pane>

      <!-- Tab 3: 来塔物资出库 -->
      <el-tab-pane label="来塔物资出库" name="warehouse">
        <!-- Stats -->
        <el-row :gutter="16" style="margin-bottom:16px">
          <el-col :span="8">
            <el-card shadow="never">
              <el-statistic title="出库总金额 (元)" :value="whStats.total_amount" :precision="2" />
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card shadow="never">
              <el-statistic title="总记录数" :value="whStats.total_records" />
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card shadow="never">
              <el-statistic title="使用区队数" :value="whStats.team_summary?.length || 0" />
            </el-card>
          </el-col>
        </el-row>

        <!-- Filters -->
        <el-row :gutter="16" style="margin-bottom:12px" align="middle">
          <el-col :span="4">
            <el-input v-model="whFilters.team" placeholder="使用区队" clearable />
          </el-col>
          <el-col :span="4">
            <el-input v-model="whFilters.material_name" placeholder="物料名称" clearable />
          </el-col>
          <el-col :span="4">
            <el-input v-model="whFilters.project_name" placeholder="工程名称" clearable />
          </el-col>
          <el-col :span="6">
            <el-date-picker v-model="whDateRange" type="daterange" range-separator="至" start-placeholder="开始" end-placeholder="结束" style="width:100%" />
          </el-col>
          <el-col :span="3">
            <el-button type="primary" @click="loadWarehouseRecords">查询</el-button>
          </el-col>
          <el-col :span="3" style="text-align:right">
            <span class="record-count">共 {{ whTotal }} 条</span>
          </el-col>
        </el-row>

        <el-table :data="whRecords" stripe border style="width:100%" max-height="500">
          <el-table-column prop="team" label="使用区队" width="130" show-overflow-tooltip />
          <el-table-column prop="apply_date" label="申请日期" width="120" />
          <el-table-column prop="material_name" label="物料名称" min-width="180" show-overflow-tooltip />
          <el-table-column prop="specification" label="规格型号" width="150" show-overflow-tooltip />
          <el-table-column prop="unit" label="单位" width="70" align="center" />
          <el-table-column prop="quantity" label="出库数量" width="100" align="right">
            <template #default="{ row }">{{ row.quantity ?? '-' }}</template>
          </el-table-column>
          <el-table-column label="单价(元)" width="110" align="right">
            <template #default="{ row }">{{ row.unit_price?.toFixed(2) ?? '-' }}</template>
          </el-table-column>
          <el-table-column label="金额(元)" width="120" align="right">
            <template #default="{ row }">
              {{ row.amount?.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) ?? '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="material_code" label="物料编码" width="170" show-overflow-tooltip />
          <el-table-column prop="project_name" label="工程名称" min-width="160" show-overflow-tooltip />
        </el-table>

        <el-pagination
          v-if="whTotal > whPageSize"
          style="margin-top:12px;justify-content:center"
          layout="prev, pager, next, jumper, total"
          :total="whTotal"
          :page-size="whPageSize"
          v-model:current-page="whPage"
          @current-change="loadWarehouseRecords"
        />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, nextTick, watch } from 'vue'
import * as echarts from 'echarts'
import { settlementApi } from '../api/settlement'
import dayjs from 'dayjs'

const loading = ref(false)
const activeTab = ref('civil')

// Overview
const overview = ref<any>({ civil_total: 0, civil_items: 0, procurement_total_somoni: 0, procurement_records: 0, warehouse_total: 0, warehouse_records: 0 })

// Civil
const civilData = ref<any[]>([])
const civilTotal = computed(() => civilData.value.reduce((s: number, r: any) => s + (r.settlement_amount || 0), 0))
const civilAuditTotal = computed(() => civilData.value.reduce((s: number, r: any) => s + (r.audit_amount || 0), 0))
const civilDebtTotal = computed(() => civilData.value.reduce((s: number, r: any) => s + (r.debt_somoni || 0), 0))

function civilSpanMethod({ row, column, rowIndex, columnIndex }: any) {
  return undefined
}

// Procurement
const procRecords = ref<any[]>([])
const procMonthly = ref<any[]>([])
const procChartRef = ref<HTMLElement>()
const procFilters = ref({ month: null as number | null, material_name: '', project_name: '' })
const procPage = ref(1)
const procPageSize = 50
const procTotal = ref(0)

// Warehouse
const whRecords = ref<any[]>([])
const whStats = ref<any>({ total_amount: 0, total_records: 0, team_summary: [] })
const whFilters = ref({ team: '', material_name: '', project_name: '' })
const whDateRange = ref<any>(null)
const whPage = ref(1)
const whPageSize = 50
const whTotal = ref(0)

async function loadOverview() {
  const { data } = await settlementApi.overview()
  overview.value = data
}

async function loadCivil() {
  const { data } = await settlementApi.civilList()
  civilData.value = data
}

async function loadProcurementMonthly() {
  const { data } = await settlementApi.procurementMonthly()
  procMonthly.value = data
  await nextTick()
  renderProcChart()
}

async function loadProcurementRecords() {
  const params: any = { page: procPage.value, page_size: procPageSize }
  if (procFilters.value.month) params.month = procFilters.value.month
  if (procFilters.value.material_name) params.material_name = procFilters.value.material_name
  if (procFilters.value.project_name) params.project_name = procFilters.value.project_name

  const [listRes, countRes] = await Promise.all([
    settlementApi.procurementRecords(params),
    settlementApi.procurementRecordsCount(params),
  ])
  procRecords.value = listRes.data
  procTotal.value = countRes.data.total
}

async function loadWarehouseRecords() {
  const params: any = { page: whPage.value, page_size: whPageSize }
  if (whFilters.value.team) params.team = whFilters.value.team
  if (whFilters.value.material_name) params.material_name = whFilters.value.material_name
  if (whFilters.value.project_name) params.project_name = whFilters.value.project_name
  if (whDateRange.value?.[0]) params.start_date = dayjs(whDateRange.value[0]).format('YYYY-MM-DD')
  if (whDateRange.value?.[1]) params.end_date = dayjs(whDateRange.value[1]).format('YYYY-MM-DD')

  const [listRes, countRes] = await Promise.all([
    settlementApi.warehouseOutbound(params),
    settlementApi.warehouseOutboundCount(params),
  ])
  whRecords.value = listRes.data
  whTotal.value = countRes.data.total
}

async function loadWarehouseStats() {
  const { data } = await settlementApi.warehouseOutboundStats()
  whStats.value = data
}

function renderProcChart() {
  if (!procChartRef.value) return
  const chart = echarts.init(procChartRef.value)
  const months = procMonthly.value.map((d: any) => `${d.month}月`)
  const values = procMonthly.value.map((d: any) => d.amount_somoni)

  chart.setOption({
    tooltip: { trigger: 'axis', formatter: (params: any) => {
      const p = params[0]
      return `${p.name}<br/>采购金额：${Number(p.value).toLocaleString('zh-CN', { minimumFractionDigits: 2 })} 索莫尼`
    }},
    grid: { left: 80, right: 20, top: 20, bottom: 30 },
    xAxis: { type: 'category', data: months },
    yAxis: { type: 'value', name: '索莫尼', axisLabel: { formatter: (v: number) => (v / 10000).toFixed(0) + '万' } },
    series: [{
      type: 'bar',
      data: values,
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: '#409EFF' },
          { offset: 1, color: '#79bbff' },
        ])
      },
      barMaxWidth: 40,
      label: { show: true, position: 'top', formatter: (p: any) => (p.value / 10000).toFixed(1) + '万', fontSize: 10 },
    }]
  })
  window.addEventListener('resize', () => chart.resize())
}

watch(activeTab, async (tab) => {
  if (tab === 'procurement' && procRecords.value.length === 0) {
    await Promise.all([loadProcurementMonthly(), loadProcurementRecords()])
  }
  if (tab === 'warehouse' && whRecords.value.length === 0) {
    await Promise.all([loadWarehouseRecords(), loadWarehouseStats()])
  }
})

onMounted(async () => {
  loading.value = true
  try {
    await Promise.all([loadOverview(), loadCivil()])
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.settlement-page { max-width: 1600px; margin: 0 auto; }
.summary-row { margin-bottom: 16px; }
.summary-card { text-align: center; }
.sub-info { margin-top: 8px; color: #909399; font-size: 13px; }
.data-tabs { min-height: 500px; }
.card-title { font-weight: bold; font-size: 15px; }
.total-row { margin-top: 12px; padding: 10px 16px; background: #f5f7fa; border-radius: 4px; font-size: 14px; }
.record-count { color: #909399; font-size: 13px; }
.text-danger { color: #f56c6c; font-weight: 600; }
</style>
