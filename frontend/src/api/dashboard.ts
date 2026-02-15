import api from './index'

export const dashboardApi = {
  getSummary() {
    return api.get('/dashboard/summary')
  },
  getAlerts(limit = 10) {
    return api.get('/dashboard/alerts', { params: { limit } })
  }
}
