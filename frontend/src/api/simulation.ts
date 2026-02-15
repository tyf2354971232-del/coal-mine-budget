import api from './index'

export const simulationApi = {
  whatIf(data: any) {
    return api.post('/simulation/whatif', data)
  },
  sensitivity(data: any) {
    return api.post('/simulation/sensitivity', data)
  },
  createScenario(data: any) {
    return api.post('/simulation/scenarios', data)
  },
  listScenarios() {
    return api.get('/simulation/scenarios')
  },
  getScenario(id: number) {
    return api.get(`/simulation/scenarios/${id}`)
  },
  deleteScenario(id: number) {
    return api.delete(`/simulation/scenarios/${id}`)
  }
}

export const alertApi = {
  list(params?: any) {
    return api.get('/alerts', { params })
  },
  check() {
    return api.post('/alerts/check')
  },
  markRead(id: number) {
    return api.put(`/alerts/${id}/read`)
  },
  resolve(id: number) {
    return api.put(`/alerts/${id}/resolve`)
  },
  stats() {
    return api.get('/alerts/stats')
  }
}

export const reportApi = {
  monthly(year: number, month: number) {
    return api.get('/reports/monthly', { params: { year, month } })
  },
  exportData(year: number, month: number) {
    return api.get('/reports/export-data', { params: { year, month } })
  }
}
