import api from './index'

export const cashflowApi = {
  list: (params?: any) => api.get('/cashflow', { params }),
  create: (data: any) => api.post('/cashflow', data),
  update: (id: number, data: any) => api.put(`/cashflow/${id}`, data),
  delete: (id: number) => api.delete(`/cashflow/${id}`),
  approve: (id: number) => api.post(`/cashflow/${id}/approve`),
  summary: () => api.get('/cashflow/summary'),
  export: () => api.get('/cashflow/export', { responseType: 'blob' }),
}
