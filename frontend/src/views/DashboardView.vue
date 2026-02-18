<template>
  <div class="dashboard" v-loading="loading">
    <!-- KPI Cards Row -->
    <el-row :gutter="16" class="kpi-row">
      <el-col :xs="12" :sm="8" :md="6">
        <el-card shadow="hover" class="kpi-card">
          <div class="kpi-content">
            <div class="kpi-info">
              <div class="kpi-label">项目总概算</div>
              <div class="kpi-value">{{ formatMoney(data.total_budget) }}</div>
            </div>
            <el-icon :size="40" color="#409EFF"><Wallet /></el-icon>
          </div>
          <el-progress :percentage="data.budget_usage_rate" :color="budgetColor" :stroke-width="6" />
          <div class="kpi-footer">已使用 {{ formatMoney(data.total_spent) }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="kpi-card">
          <div class="kpi-content">
            <div class="kpi-info">
              <div class="kpi-label">整体进度</div>
              <div class="kpi-value">{{ data.overall_progress?.toFixed(1) }}%</div>
            </div>
            <el-icon :size="40" color="#67C23A"><TrendCharts /></el-icon>
          </div>
          <el-progress :percentage="data.overall_progress" color="#67C23A" :stroke-width="6" />
          <div class="kpi-footer">{{ data.completed_count }} 已完成 / {{ data.sub_project_count }} 总计</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="kpi-card">
          <div class="kpi-content">
            <div class="kpi-info">
              <div class="kpi-label">弹性预备金</div>
              <div class="kpi-value">{{ formatMoney(data.reserve_budget) }}</div>
            </div>
            <el-icon :size="40" color="#E6A23C"><CreditCard /></el-icon>
          </div>
          <el-progress :percentage="reserveUsageRate" :color="reserveUsageRate > 50 ? '#F56C6C' : '#E6A23C'" :stroke-width="6" />
          <div class="kpi-footer">已动用 {{ formatMoney(data.reserve_used) }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="kpi-card">
          <div class="kpi-content">
            <div class="kpi-info">
              <div class="kpi-label">现金支出</div>
              <div class="kpi-value">{{ formatMoney(data.cash_outflow_total) }}</div>
            </div>
            <el-icon :size="40" color="#909399"><Coin /></el-icon>
          </div>
          <div class="kpi-footer">
            流入 {{ formatMoney(data.cash_inflow_total) }} | 净额 {{ formatMoney(data.cash_balance) }}
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Charts Row -->
    <el-row :gutter="16" class="chart-row">
      <el-col :span="14">
        <el-card shadow="hover">
          <template #header>
            <span class="card-title">六大费用类别 概算 vs 实际</span>
          </template>
          <div ref="categoryChartRef" style="height: 360px;"></div>
        </el-card>
      </el-col>
      <el-col :span="10">
        <el-card shadow="hover">
          <template #header>
            <span class="card-title">概算分配占比</span>
          </template>
          <div ref="pieChartRef" style="height: 360px;"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Progress & Alerts Row -->
    <el-row :gutter="16" class="detail-row">
      <el-col :span="14">
        <el-card shadow="hover">
          <template #header>
            <span class="card-title">子工程进度概览</span>
          </template>
          <div ref="progressChartRef" style="height: 400px;"></div>
        </el-card>
      </el-col>
      <el-col :span="10">
        <el-card shadow="hover" class="risk-card">
          <template #header>
            <span class="card-title">概算超支风险 Top 5</span>
          </template>
          <div v-if="data.top_risks?.length" class="risk-list">
            <div v-for="risk in data.top_risks" :key="risk.id" class="risk-item">
              <div class="risk-header">
                <span class="risk-name">{{ risk.name }}</span>
                <el-tag :type="risk.risk_level === 'red' ? 'danger' : risk.risk_level === 'yellow' ? 'warning' : 'success'" size="small" effect="dark">
                  {{ risk.usage_rate }}%
                </el-tag>
              </div>
              <el-progress
                :percentage="Math.min(100, risk.usage_rate)"
                :color="getRiskColor(risk.risk_level)"
                :stroke-width="10"
                :show-text="false"
              />
              <div class="risk-detail">
                概算 {{ formatMoney(risk.budget) }} | 已用 {{ formatMoney(risk.spent) }}
              </div>
            </div>
          </div>
          <el-empty v-else description="暂无风险项" :image-size="80" />
        </el-card>
      </el-col>
    </el-row>

    <!-- Monthly Trend -->
    <el-row :gutter="16" class="trend-row">
      <el-col :span="24">
        <el-card shadow="hover">
          <template #header>
            <span class="card-title">月度支出趋势</span>
          </template>
          <div ref="trendChartRef" style="height: 300px;"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, nextTick } from 'vue'
import * as echarts from 'echarts'
import { dashboardApi } from '../api/dashboard'
import { formatMoney, getRiskColor } from '../utils/format'

const loading = ref(true)
const data = ref<any>({})
const categoryChartRef = ref<HTMLElement>()
const pieChartRef = ref<HTMLElement>()
const progressChartRef = ref<HTMLElement>()
const trendChartRef = ref<HTMLElement>()

const budgetColor = computed(() => {
  const r = data.value.budget_usage_rate || 0
  return r >= 90 ? '#F56C6C' : r >= 70 ? '#E6A23C' : '#409EFF'
})

const reserveUsageRate = computed(() => {
  if (!data.value.reserve_budget) return 0
  return Math.min(100, (data.value.reserve_used || 0) / data.value.reserve_budget * 100)
})

async function loadData() {
  loading.value = true
  try {
    const { data: d } = await dashboardApi.getSummary()
    data.value = d
    await nextTick()
    renderCharts()
  } finally {
    loading.value = false
  }
}

function renderCharts() {
  renderCategoryChart()
  renderPieChart()
  renderProgressChart()
  renderTrendChart()
}

function renderCategoryChart() {
  if (!categoryChartRef.value || !data.value.category_breakdown?.length) return
  const chart = echarts.init(categoryChartRef.value)
  const cats = data.value.category_breakdown
  chart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: { data: ['批复概算', '实际支出'], top: 10 },
    grid: { left: 60, right: 20, top: 50, bottom: 40 },
    xAxis: { type: 'category', data: cats.map((c: any) => c.name), axisLabel: { fontSize: 12 } },
    yAxis: { type: 'value', name: '万元', axisLabel: { formatter: (v: number) => v >= 10000 ? (v/10000).toFixed(1) + '万' : v } },
    series: [
      { name: '批复概算', type: 'bar', data: cats.map((c: any) => c.budget), itemStyle: { color: '#409EFF' }, barMaxWidth: 40 },
      { name: '实际支出', type: 'bar', data: cats.map((c: any) => c.spent), itemStyle: { color: '#F56C6C' }, barMaxWidth: 40 },
    ]
  })
  window.addEventListener('resize', () => chart.resize())
}

function renderPieChart() {
  if (!pieChartRef.value || !data.value.category_breakdown?.length) return
  const chart = echarts.init(pieChartRef.value)
  const cats = data.value.category_breakdown
  chart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {c}万元 ({d}%)' },
    legend: { orient: 'vertical', right: 10, top: 'center', textStyle: { fontSize: 12 } },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['40%', '50%'],
      avoidLabelOverlap: true,
      label: { show: false },
      data: cats.map((c: any) => ({ name: c.name, value: c.budget })),
      emphasis: { itemStyle: { shadowBlur: 10, shadowOffsetX: 0, shadowColor: 'rgba(0, 0, 0, 0.5)' } },
    }]
  })
  window.addEventListener('resize', () => chart.resize())
}

function renderProgressChart() {
  if (!progressChartRef.value || !data.value.top_risks?.length) return
  const chart = echarts.init(progressChartRef.value)
  // Use top risks as sample since we don't have all sub-projects in dashboard summary
  const items = data.value.top_risks.slice(0, 10)
  chart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: { data: ['概算使用率'], top: 10 },
    grid: { left: 140, right: 40, top: 50, bottom: 20 },
    xAxis: { type: 'value', max: 100, axisLabel: { formatter: '{value}%' } },
    yAxis: { type: 'category', data: items.map((i: any) => i.name), axisLabel: { fontSize: 11, width: 120, overflow: 'truncate' } },
    series: [{
      name: '概算使用率',
      type: 'bar',
      data: items.map((i: any) => ({
        value: Math.min(100, i.usage_rate),
        itemStyle: { color: getRiskColor(i.risk_level) }
      })),
      barMaxWidth: 20,
      label: { show: true, position: 'right', formatter: '{c}%' }
    }]
  })
  window.addEventListener('resize', () => chart.resize())
}

function renderTrendChart() {
  if (!trendChartRef.value) return
  const chart = echarts.init(trendChartRef.value)
  const trend = data.value.monthly_trend || []
  chart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: 60, right: 20, top: 30, bottom: 40 },
    xAxis: { type: 'category', data: trend.map((t: any) => t.month) },
    yAxis: { type: 'value', name: '万元' },
    series: [{
      name: '月度支出',
      type: 'line',
      data: trend.map((t: any) => t.amount),
      smooth: true,
      areaStyle: { color: 'rgba(64,158,255,0.15)' },
      itemStyle: { color: '#409EFF' },
      lineStyle: { width: 3 }
    }]
  })
  window.addEventListener('resize', () => chart.resize())
}

onMounted(loadData)
</script>

<style scoped>
.dashboard { max-width: 1600px; margin: 0 auto; }
.kpi-row { margin-bottom: 16px; }
.kpi-card { height: 160px; }
.kpi-content { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px; }
.kpi-label { color: #909399; font-size: 14px; margin-bottom: 8px; }
.kpi-value { font-size: 24px; font-weight: bold; color: #303133; }
.kpi-footer { margin-top: 8px; font-size: 12px; color: #909399; }
.chart-row { margin-bottom: 16px; }
.detail-row { margin-bottom: 16px; }
.trend-row { margin-bottom: 16px; }
.card-title { font-weight: bold; font-size: 15px; }
.risk-list { display: flex; flex-direction: column; gap: 16px; }
.risk-item { padding: 8px 0; border-bottom: 1px solid #f0f0f0; }
.risk-item:last-child { border-bottom: none; }
.risk-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
.risk-name { font-size: 14px; color: #303133; font-weight: 500; }
.risk-detail { font-size: 12px; color: #909399; margin-top: 4px; }
</style>
