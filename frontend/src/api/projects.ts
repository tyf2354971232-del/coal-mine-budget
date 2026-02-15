import api from './index'

export const projectApi = {
  list() {
    return api.get('/projects')
  },
  get(id: number) {
    return api.get(`/projects/${id}`)
  },
  create(data: any) {
    return api.post('/projects', data)
  },
  update(id: number, data: any) {
    return api.put(`/projects/${id}`, data)
  },
  listSubProjects(params?: any) {
    return api.get('/projects/sub-projects/all', { params })
  },
  getSubProject(id: number) {
    return api.get(`/projects/sub-projects/${id}`)
  },
  createSubProject(data: any) {
    return api.post('/projects/sub-projects', data)
  },
  updateSubProject(id: number, data: any) {
    return api.put(`/projects/sub-projects/${id}`, data)
  },
  deleteSubProject(id: number) {
    return api.delete(`/projects/sub-projects/${id}`)
  },
  listMilestones(spId: number) {
    return api.get(`/projects/sub-projects/${spId}/milestones`)
  },
  createMilestone(data: any) {
    return api.post('/projects/milestones', data)
  },
  updateMilestone(id: number, data: any) {
    return api.put(`/projects/milestones/${id}`, data)
  },
  listProgress(spId: number) {
    return api.get(`/projects/sub-projects/${spId}/progress`)
  },
  createProgress(data: any) {
    return api.post('/projects/progress', data)
  }
}
