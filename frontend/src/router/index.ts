import { createRouter, createWebHistory } from 'vue-router'
import { ElMessage } from 'element-plus'

/**
 * Role-based access control:
 *   admin      - 管理员：全部功能
 *   leader     - 领导层：查看全部 + 模拟分析 + 审批
 *   department - 部门用户：本部门数据录入 + 全局数据查看
 *   viewer     - 普通员工：只读查看（驾驶舱/项目/支出/预警/报表）
 */

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: () => import('../views/LoginView.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/',
      component: () => import('../components/layout/AppLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          redirect: '/dashboard'
        },
        {
          path: 'dashboard',
          name: 'Dashboard',
          component: () => import('../views/DashboardView.vue'),
          meta: { title: '领导驾驶舱', icon: 'DataBoard', roles: ['admin', 'leader', 'department', 'viewer'] }
        },
        {
          path: 'projects',
          name: 'Projects',
          component: () => import('../views/ProjectListView.vue'),
          meta: { title: '工程项目管理', icon: 'OfficeBuilding', roles: ['admin', 'leader', 'department', 'viewer'] }
        },
        {
          path: 'projects/:id',
          name: 'ProjectDetail',
          component: () => import('../views/ProjectDetailView.vue'),
          meta: { title: '工程详情', roles: ['admin', 'leader', 'department', 'viewer'] }
        },
        {
          path: 'budget',
          name: 'Budget',
          component: () => import('../views/BudgetCategoryView.vue'),
          meta: { title: '预算科目管理', icon: 'Wallet', roles: ['admin', 'leader'] }
        },
        {
          path: 'expenditures',
          name: 'Expenditures',
          component: () => import('../views/ExpenditureView.vue'),
          meta: { title: '支出管理', icon: 'Money', roles: ['admin', 'leader', 'department', 'viewer'] }
        },
        {
          path: 'simulation',
          name: 'Simulation',
          component: () => import('../views/SimulationView.vue'),
          meta: { title: '模拟分析中心', icon: 'TrendCharts', roles: ['admin', 'leader'] }
        },
        {
          path: 'alerts',
          name: 'Alerts',
          component: () => import('../views/AlertsView.vue'),
          meta: { title: '预警管理', icon: 'Bell', roles: ['admin', 'leader', 'department', 'viewer'] }
        },
        {
          path: 'reports',
          name: 'Reports',
          component: () => import('../views/ReportsView.vue'),
          meta: { title: '月度考核报表', icon: 'Document', roles: ['admin', 'leader', 'department', 'viewer'] }
        },
        {
          path: 'users',
          name: 'Users',
          component: () => import('../views/UserManagementView.vue'),
          meta: { title: '用户管理', icon: 'User', roles: ['admin'] }
        },
        {
          path: '/:pathMatch(.*)*',
          redirect: '/dashboard'
        }
      ]
    }
  ]
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const userStr = localStorage.getItem('user')

  // 1. Check authentication
  if (to.meta.requiresAuth !== false && !token) {
    next('/login')
    return
  }

  // 2. Check role-based access
  const allowedRoles = to.meta.roles as string[] | undefined
  if (allowedRoles && userStr) {
    try {
      const user = JSON.parse(userStr)
      if (!allowedRoles.includes(user.role)) {
        ElMessage.warning('您没有访问该页面的权限')
        next('/dashboard')
        return
      }
    } catch {
      // If user data is corrupted, redirect to login
      next('/login')
      return
    }
  }

  next()
})

export default router
