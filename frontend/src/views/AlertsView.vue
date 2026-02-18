<template>
  <div class="alerts-view">
    <ReadOnlyBanner :edit-roles="['admin', 'leader']" />
    <!-- Stats Cards -->
    <el-row :gutter="16" style="margin-bottom:16px">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <el-statistic title="未解决预警" :value="stats.unresolved || 0" value-style="font-size:30px;font-weight:bold" />
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <el-statistic title="红色预警" :value="stats.red || 0" :value-style="{ fontSize: '30px', fontWeight: 'bold', color: '#F56C6C' }" />
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <el-statistic title="黄色预警" :value="stats.yellow || 0" :value-style="{ fontSize: '30px', fontWeight: 'bold', color: '#E6A23C' }" />
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <el-button v-if="authStore.isLeader" type="primary" size="large" @click="runCheck" :loading="checking" style="width:100%">
            <el-icon><Refresh /></el-icon> 运行预警检查
          </el-button>
          <el-statistic v-else title="您的角色" :value="authStore.user?.role === 'department' ? '部门用户' : '普通用户'" />
        </el-card>
      </el-col>
    </el-row>

    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span class="card-title">预警列表</span>
          <div>
            <el-select v-model="filterLevel" clearable placeholder="级别筛选" style="width:120px;margin-right:8px" @change="loadData">
              <el-option label="红色" value="red" /><el-option label="黄色" value="yellow" /><el-option label="信息" value="info" />
            </el-select>
            <el-switch v-model="showResolved" active-text="显示已解决" @change="loadData" style="margin-right:12px" />
          </div>
        </div>
      </template>

      <el-table :data="alerts" v-loading="loading" stripe border>
        <el-table-column label="级别" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.level === 'red' ? 'danger' : row.level === 'yellow' ? 'warning' : 'info'" effect="dark" round>
              {{ row.level === 'red' ? '红' : row.level === 'yellow' ? '黄' : '信息' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="alert_type" label="类型" width="120">
          <template #default="{ row }">
            {{ row.alert_type === 'budget_overrun' ? '概算超支' : row.alert_type === 'schedule_delay' ? '工期延误' : row.alert_type === 'burn_rate' ? '消耗速率' : row.alert_type }}
          </template>
        </el-table-column>
        <el-table-column prop="title" label="标题" min-width="200" />
        <el-table-column prop="message" label="详情" min-width="300" show-overflow-tooltip />
        <el-table-column prop="related_name" label="关联对象" width="150" />
        <el-table-column prop="created_at" label="时间" width="170">
          <template #default="{ row }">{{ formatDateTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.is_resolved" type="success" size="small">已解决</el-tag>
            <el-tag v-else-if="row.is_read" type="info" size="small">已读</el-tag>
            <el-tag v-else type="danger" size="small" effect="dark">未读</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" align="center" v-if="authStore.isLeader">
          <template #default="{ row }">
            <el-button v-if="!row.is_read" type="primary" link size="small" @click="markRead(row)">标记已读</el-button>
            <el-button v-if="!row.is_resolved && authStore.isLeader" type="success" link size="small" @click="resolveAlert(row)">解决</el-button>
          </template>
        </el-table-column>
        <!-- 非领导角色：只读提示 -->
        <el-table-column label="" width="100" align="center" v-if="!authStore.isLeader">
          <template #default>
            <el-tag type="info" size="small">只读</el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { alertApi } from '../api/simulation'
import { formatDateTime } from '../utils/format'
import { useAuthStore } from '../stores/auth'
import ReadOnlyBanner from '../components/common/ReadOnlyBanner.vue'

const authStore = useAuthStore()
const loading = ref(false)
const checking = ref(false)
const alerts = ref<any[]>([])
const stats = ref<any>({})
const filterLevel = ref('')
const showResolved = ref(false)

async function loadData() {
  loading.value = true
  try {
    const params: any = { limit: 100 }
    if (filterLevel.value) params.level = filterLevel.value
    if (!showResolved.value) params.is_resolved = false
    const [alertRes, statsRes] = await Promise.all([alertApi.list(params), alertApi.stats()])
    alerts.value = alertRes.data
    stats.value = statsRes.data
  } finally { loading.value = false }
}

async function runCheck() {
  checking.value = true
  try {
    const { data } = await alertApi.check()
    ElMessage.success(data.message)
    await loadData()
  } finally { checking.value = false }
}

async function markRead(row: any) {
  await alertApi.markRead(row.id)
  row.is_read = true
}

async function resolveAlert(row: any) {
  await alertApi.resolve(row.id)
  row.is_resolved = true
  await loadData()
}

onMounted(loadData)
</script>

<style scoped>
.card-header { display: flex; justify-content: space-between; align-items: center; }
.card-title { font-weight: bold; font-size: 16px; }
.stat-card { text-align: center; }
</style>
