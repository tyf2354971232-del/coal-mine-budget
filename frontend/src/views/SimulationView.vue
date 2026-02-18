<template>
  <div class="simulation-view">
    <el-tabs v-model="activeTab" type="border-card">
      <!-- What-if Analysis Tab -->
      <el-tab-pane label="What-if 分析" name="whatif">
        <el-card shadow="never">
          <template #header><span class="card-title">参数调整 — 拖动滑块查看实时影响</span></template>
          <div class="whatif-params">
            <div v-for="(param, idx) in whatifParams" :key="idx" class="param-row">
              <div class="param-header">
                <el-select v-model="param.target_id" filterable placeholder="选择子工程" style="width:240px">
                  <el-option v-for="sp in subProjects" :key="sp.id" :label="sp.name" :value="sp.id" />
                </el-select>
                <el-tag>{{ param.adjustment_value > 0 ? '+' : '' }}{{ param.adjustment_value }}%</el-tag>
                <el-button type="danger" link @click="whatifParams.splice(idx, 1)"><el-icon><Delete /></el-icon></el-button>
              </div>
              <el-slider v-model="param.adjustment_value" :min="-50" :max="50" :step="1"
                :marks="{ '-50': '-50%', '-25': '-25%', 0: '0', 25: '+25%', 50: '+50%' }"
                @change="runWhatIf" />
            </div>
            <el-button type="primary" plain @click="addWhatIfParam" style="margin-top:12px">
              <el-icon><Plus /></el-icon> 添加调整项
            </el-button>
          </div>

          <!-- What-if Result -->
          <div v-if="whatifResult" class="whatif-result">
            <el-divider />
            <el-row :gutter="16">
              <el-col :span="6">
                <el-statistic title="原始总成本" :value="whatifResult.original_total_cost" :precision="2" suffix="万元" />
              </el-col>
              <el-col :span="6">
                <el-statistic title="调整后总成本" :value="whatifResult.adjusted_total_cost" :precision="2" suffix="万元"
                  :value-style="{ color: whatifResult.cost_change > 0 ? '#F56C6C' : '#67C23A' }" />
              </el-col>
              <el-col :span="6">
                <el-statistic title="成本变化" :value="whatifResult.cost_change" :precision="2" suffix="万元"
                  :prefix="whatifResult.cost_change > 0 ? '↑' : '↓'"
                  :value-style="{ color: whatifResult.cost_change > 0 ? '#F56C6C' : '#67C23A' }" />
              </el-col>
              <el-col :span="6">
                <el-statistic title="概算状态">
                  <template #default>
                    <el-tag :type="whatifResult.budget_status === 'over_budget' ? 'danger' : whatifResult.budget_status === 'near_limit' ? 'warning' : 'success'" size="large" effect="dark">
                      {{ whatifResult.budget_status === 'over_budget' ? '超出概算' : whatifResult.budget_status === 'near_limit' ? '接近上限' : '概算内' }}
                    </el-tag>
                  </template>
                </el-statistic>
              </el-col>
            </el-row>

            <el-row :gutter="16" style="margin-top:20px">
              <el-col :span="12">
                <el-card shadow="hover">
                  <template #header><span>KPI 影响</span></template>
                  <el-descriptions :column="1" border>
                    <el-descriptions-item label="概算控制率">{{ whatifResult.kpi_impact?.budget_control_rate }}%</el-descriptions-item>
                    <el-descriptions-item label="原概算使用率">{{ whatifResult.kpi_impact?.original_budget_usage }}%</el-descriptions-item>
                    <el-descriptions-item label="调整后使用率">{{ whatifResult.kpi_impact?.adjusted_budget_usage }}%</el-descriptions-item>
                  </el-descriptions>
                </el-card>
              </el-col>
              <el-col :span="12">
                <el-card shadow="hover">
                  <template #header><span>弹性预备金影响</span></template>
                  <el-descriptions :column="1" border>
                    <el-descriptions-item label="总预备金">{{ whatifResult.reserve_impact?.total_reserve?.toFixed(2) }}万元</el-descriptions-item>
                    <el-descriptions-item label="需动用">{{ whatifResult.reserve_impact?.reserve_needed?.toFixed(2) }}万元</el-descriptions-item>
                    <el-descriptions-item label="剩余">{{ whatifResult.reserve_impact?.reserve_remaining?.toFixed(2) }}万元</el-descriptions-item>
                  </el-descriptions>
                </el-card>
              </el-col>
            </el-row>
          </div>
        </el-card>
      </el-tab-pane>

      <!-- Scenario Comparison Tab -->
      <el-tab-pane label="情景对比" name="scenario">
        <el-card shadow="never">
          <template #header>
            <div style="display:flex;justify-content:space-between;align-items:center">
              <span class="card-title">多情景方案对比</span>
              <el-button type="primary" @click="createPresetScenarios" :loading="scenarioLoading">生成预置方案对比</el-button>
            </div>
          </template>

          <div v-if="scenarios.length" class="scenario-grid">
            <el-row :gutter="16">
              <el-col :span="8" v-for="sc in scenarios" :key="sc.id">
                <el-card shadow="hover" :class="['scenario-card', sc.name.includes('保守') ? 'conservative' : sc.name.includes('乐观') ? 'optimistic' : '']">
                  <template #header>
                    <span style="font-weight:bold">{{ sc.name }}</span>
                  </template>
                  <el-descriptions :column="1" border size="small">
                    <el-descriptions-item label="调整后概算">{{ sc.total_cost?.toLocaleString() }}万元</el-descriptions-item>
                    <el-descriptions-item label="预计回报">{{ sc.total_return?.toLocaleString() }}万元</el-descriptions-item>
                    <el-descriptions-item label="投资回报率">
                      <el-tag :type="(sc.roi || 0) > 0 ? 'success' : 'danger'">{{ sc.roi }}%</el-tag>
                    </el-descriptions-item>
                    <el-descriptions-item v-if="sc.results" label="预估工期">{{ sc.results.estimated_duration_months }}个月</el-descriptions-item>
                    <el-descriptions-item v-if="sc.results" label="概算节约">{{ sc.results.budget_savings?.toLocaleString() }}万元</el-descriptions-item>
                  </el-descriptions>
                </el-card>
              </el-col>
            </el-row>
            <div ref="scenarioChartRef" style="height:350px;margin-top:20px"></div>
          </div>
          <el-empty v-else description="点击上方按钮生成方案对比" />
        </el-card>
      </el-tab-pane>

      <!-- Sensitivity Analysis Tab -->
      <el-tab-pane label="敏感性分析" name="sensitivity">
        <el-card shadow="never">
          <template #header>
            <div style="display:flex;justify-content:space-between;align-items:center">
              <span class="card-title">龙卷风图 — 各项支出对总成本的影响程度</span>
              <el-button type="primary" @click="runSensitivity" :loading="sensitivityLoading">运行分析</el-button>
            </div>
          </template>
          <div ref="tornadoChartRef" style="height:500px;"></div>
          <el-empty v-if="!sensitivityResult" description="点击按钮运行敏感性分析" />
        </el-card>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'
import { simulationApi } from '../api/simulation'
import { projectApi } from '../api/projects'

const activeTab = ref('whatif')
const subProjects = ref<any[]>([])

// What-if
const whatifParams = ref<any[]>([])
const whatifResult = ref<any>(null)

// Scenario
const scenarioLoading = ref(false)
const scenarios = ref<any[]>([])
const scenarioChartRef = ref<HTMLElement>()

// Sensitivity
const sensitivityLoading = ref(false)
const sensitivityResult = ref<any>(null)
const tornadoChartRef = ref<HTMLElement>()

function addWhatIfParam() {
  whatifParams.value.push({
    target_type: 'sub_project',
    target_id: subProjects.value[0]?.id || 1,
    field: 'allocated_budget',
    adjustment_type: 'percent',
    adjustment_value: 0,
  })
}

async function runWhatIf() {
  if (!whatifParams.value.length) return
  try {
    const { data } = await simulationApi.whatIf({ parameters: whatifParams.value })
    whatifResult.value = data
  } catch {}
}

async function createPresetScenarios() {
  scenarioLoading.value = true
  try {
    const { data } = await simulationApi.createScenario({
      name: '三方案对比分析',
      description: '保守/正常/乐观三种情景对比',
      sim_type: 'scenario',
      scenarios: [
        { name: '保守方案 (概算x0.9)', parameters: { budget_factor: 0.9, duration_factor: 1.15, efficiency_factor: 0.85 } },
        { name: '正常方案 (概算x1.0)', parameters: { budget_factor: 1.0, duration_factor: 1.0, efficiency_factor: 1.0 } },
        { name: '乐观方案 (概算x1.05)', parameters: { budget_factor: 1.05, duration_factor: 0.9, efficiency_factor: 1.15 } },
      ]
    })
    scenarios.value = data.scenarios || []
    ElMessage.success('方案生成成功')
    await nextTick()
    renderScenarioChart()
  } finally { scenarioLoading.value = false }
}

function renderScenarioChart() {
  if (!scenarioChartRef.value || !scenarios.value.length) return
  const chart = echarts.init(scenarioChartRef.value)
  const names = scenarios.value.map(s => s.name)
  chart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['总成本', '预计回报', '投资回报率(%)'], top: 10 },
    grid: { left: 80, right: 80, top: 50, bottom: 30 },
    xAxis: { type: 'category', data: names },
    yAxis: [
      { type: 'value', name: '万元', position: 'left' },
      { type: 'value', name: 'ROI %', position: 'right' }
    ],
    series: [
      { name: '总成本', type: 'bar', data: scenarios.value.map(s => s.total_cost), itemStyle: { color: '#409EFF' } },
      { name: '预计回报', type: 'bar', data: scenarios.value.map(s => s.total_return), itemStyle: { color: '#67C23A' } },
      { name: '投资回报率(%)', type: 'line', yAxisIndex: 1, data: scenarios.value.map(s => s.roi), itemStyle: { color: '#F56C6C' }, lineStyle: { width: 3 } },
    ]
  })
  window.addEventListener('resize', () => chart.resize())
}

async function runSensitivity() {
  sensitivityLoading.value = true
  try {
    const targets = subProjects.value.slice(0, 10).map(sp => ({
      type: 'sub_project', id: sp.id, field: 'allocated_budget', range_min: -20, range_max: 20
    }))
    const { data } = await simulationApi.sensitivity({ target_items: targets })
    sensitivityResult.value = data
    await nextTick()
    renderTornadoChart(data)
  } finally { sensitivityLoading.value = false }
}

function renderTornadoChart(data: any) {
  if (!tornadoChartRef.value || !data?.items?.length) return
  const chart = echarts.init(tornadoChartRef.value)
  const items = data.items.slice(0, 10)
  chart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: { data: ['降低20%影响', '增加20%影响'] },
    grid: { left: 180, right: 60, top: 50, bottom: 30 },
    xAxis: { type: 'value', name: '成本变化(万元)' },
    yAxis: {
      type: 'category',
      data: items.map((i: any) => i.name),
      axisLabel: { width: 160, overflow: 'truncate' }
    },
    series: [
      {
        name: '降低20%影响', type: 'bar', stack: 'total',
        data: items.map((i: any) => i.low_impact),
        itemStyle: { color: '#67C23A' }, barMaxWidth: 20
      },
      {
        name: '增加20%影响', type: 'bar', stack: 'total',
        data: items.map((i: any) => i.high_impact),
        itemStyle: { color: '#F56C6C' }, barMaxWidth: 20
      }
    ]
  })
  window.addEventListener('resize', () => chart.resize())
}

onMounted(async () => {
  const { data } = await projectApi.listSubProjects()
  subProjects.value = data
  if (data.length) addWhatIfParam()
})
</script>

<style scoped>
.card-title { font-weight: bold; font-size: 15px; }
.whatif-params { max-width: 800px; }
.param-row { margin-bottom: 24px; padding: 16px; background: #f5f7fa; border-radius: 8px; }
.param-header { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; }
.whatif-result { margin-top: 20px; }
.scenario-card.conservative { border-top: 3px solid #E6A23C; }
.scenario-card.optimistic { border-top: 3px solid #67C23A; }
</style>
