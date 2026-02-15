import dayjs from 'dayjs'

/** Format number as currency (万元) */
export function formatMoney(val: number | undefined | null, suffix = '万元'): string {
  if (val === undefined || val === null) return '-'
  return val.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + suffix
}

/** Format percentage */
export function formatPercent(val: number | undefined | null): string {
  if (val === undefined || val === null) return '-'
  return val.toFixed(2) + '%'
}

/** Format date */
export function formatDate(val: string | undefined | null): string {
  if (!val) return '-'
  return dayjs(val).format('YYYY-MM-DD')
}

/** Get status tag type for Element Plus */
export function getStatusType(status: string): string {
  const map: Record<string, string> = {
    completed: 'success',
    in_progress: 'primary',
    not_started: 'info',
    delayed: 'danger',
    suspended: 'warning',
    planning: 'info',
  }
  return map[status] || 'info'
}

/** Get status label in Chinese */
export function getStatusLabel(status: string): string {
  const map: Record<string, string> = {
    completed: '已完成',
    in_progress: '进行中',
    not_started: '未开始',
    delayed: '已延期',
    suspended: '已暂停',
    planning: '规划中',
  }
  return map[status] || status
}

/** Get risk level color */
export function getRiskColor(level: string): string {
  const map: Record<string, string> = {
    green: '#67C23A',
    yellow: '#E6A23C',
    red: '#F56C6C',
  }
  return map[level] || '#909399'
}

/** Budget category labels */
export const BUDGET_CATEGORIES = [
  '矿建工程费', '土建工程费', '安装工程费', '设备购置费', '其他费用', '预备费'
]
