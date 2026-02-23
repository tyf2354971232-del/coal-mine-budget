<template>
  <el-container class="app-layout">
    <el-aside :width="isCollapse ? '64px' : '220px'" class="sidebar">
      <div class="logo" @click="$router.push('/dashboard')">
        <el-icon :size="28"><OfficeBuilding /></el-icon>
        <span v-show="!isCollapse" class="logo-text">概算管控系统</span>
      </div>
      <el-menu
        :default-active="activeMenu"
        :collapse="isCollapse"
        background-color="#1d1e1f"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
        router
        class="sidebar-menu"
      >
        <template v-for="item in visibleMenuItems" :key="item.path">
          <el-menu-item :index="item.path">
            <el-icon><component :is="item.icon" /></el-icon>
            <template #title>{{ item.title }}</template>
          </el-menu-item>
        </template>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="header">
        <div class="header-left">
          <el-icon class="collapse-btn" @click="isCollapse = !isCollapse" :size="20">
            <Fold v-if="!isCollapse" />
            <Expand v-else />
          </el-icon>
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/dashboard' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item v-if="$route.meta.title">{{ $route.meta.title }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <el-badge :value="alertCount" :hidden="alertCount === 0" class="alert-badge">
            <el-icon :size="18" @click="$router.push('/alerts')" style="cursor:pointer"><Bell /></el-icon>
          </el-badge>
          <el-dropdown @command="handleCommand">
            <span class="user-info">
              <el-avatar :size="30" style="background:#409EFF">
                {{ authStore.user?.full_name?.charAt(0) }}
              </el-avatar>
              <span class="username">{{ authStore.user?.full_name }}</span>
              <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item disabled>
                  {{ authStore.user?.role === 'admin' ? '管理员' : authStore.user?.role === 'leader' ? '领导' : authStore.user?.role === 'department' ? '部门用户' : '普通用户' }}
                  - {{ authStore.user?.department }}
                </el-dropdown-item>
                <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { alertApi } from '../../api/simulation'

const authStore = useAuthStore()
const route = useRoute()
const router = useRouter()
const isCollapse = ref(false)
const alertCount = ref(0)

const activeMenu = computed(() => '/' + route.path.split('/')[1])

// Menu items with role-based visibility
const allMenuItems = [
  { path: '/dashboard',    title: '领导驾驶舱',   icon: 'DataBoard',       roles: ['admin', 'leader', 'department', 'viewer'] },
  { path: '/projects',     title: '工程项目管理',  icon: 'OfficeBuilding',  roles: ['admin', 'leader', 'department', 'viewer'] },
  { path: '/budget',       title: '概算科目管理',  icon: 'Wallet',          roles: ['admin', 'leader'] },
  { path: '/expenditures', title: '支出管理',      icon: 'Money',           roles: ['admin', 'leader', 'department', 'viewer'] },
  { path: '/cashflow',     title: '现金流管理',    icon: 'Coin',            roles: ['admin', 'leader', 'department', 'viewer'] },
  { path: '/settlement',   title: '决算数据管理',  icon: 'Tickets',         roles: ['admin', 'leader', 'department', 'viewer'] },
  { path: '/simulation',   title: '模拟分析中心',  icon: 'TrendCharts',     roles: ['admin', 'leader'] },
  { path: '/alerts',       title: '预警管理',      icon: 'Bell',            roles: ['admin', 'leader', 'department', 'viewer'] },
  { path: '/reports',      title: '月度考核报表',  icon: 'Document',        roles: ['admin', 'leader', 'department', 'viewer'] },
  { path: '/users',        title: '用户管理',      icon: 'User',            roles: ['admin'] },
]

const visibleMenuItems = computed(() => {
  const role = authStore.user?.role || 'viewer'
  return allMenuItems.filter(item => item.roles.includes(role))
})

async function loadAlertCount() {
  try {
    const { data } = await alertApi.stats()
    alertCount.value = data.unresolved || 0
  } catch {}
}

function handleCommand(cmd: string) {
  if (cmd === 'logout') {
    authStore.logout()
    router.push('/login')
  }
}

onMounted(() => {
  loadAlertCount()
  setInterval(loadAlertCount, 60000)
})
</script>

<style scoped>
.app-layout {
  height: 100vh;
}
.sidebar {
  background: #1d1e1f;
  transition: width 0.3s;
  overflow: hidden;
}
.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: #409EFF;
  cursor: pointer;
  border-bottom: 1px solid #333;
}
.logo-text {
  font-size: 16px;
  font-weight: bold;
  white-space: nowrap;
}
.sidebar-menu {
  border-right: none;
}
.header {
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 1px 4px rgba(0,0,0,0.08);
  padding: 0 20px;
  height: 60px;
}
.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}
.collapse-btn {
  cursor: pointer;
  color: #606266;
}
.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}
.alert-badge {
  line-height: 1;
}
.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  color: #606266;
}
.username {
  font-size: 14px;
}
.main-content {
  background: #f0f2f5;
  min-height: calc(100vh - 60px);
  padding: 20px;
}
</style>
