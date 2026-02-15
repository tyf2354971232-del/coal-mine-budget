import api from './index'

export const budgetApi = {
  listCategories() {
    return api.get('/budget/categories')
  },
  listCategoriesFlat() {
    return api.get('/budget/categories/flat')
  },
  createCategory(data: any) {
    return api.post('/budget/categories', data)
  },
  updateCategory(id: number, data: any) {
    return api.put(`/budget/categories/${id}`, data)
  },
  deleteCategory(id: number) {
    return api.delete(`/budget/categories/${id}`)
  },
  listCostItems(params?: any) {
    return api.get('/budget/cost-items', { params })
  },
  createCostItem(data: any) {
    return api.post('/budget/cost-items', data)
  },
  updateCostItem(id: number, data: any) {
    return api.put(`/budget/cost-items/${id}`, data)
  },
  deleteCostItem(id: number) {
    return api.delete(`/budget/cost-items/${id}`)
  }
}

export const expenditureApi = {
  list(params?: any) {
    return api.get('/expenditures', { params })
  },
  summary(params?: any) {
    return api.get('/expenditures/summary', { params })
  },
  create(data: any) {
    return api.post('/expenditures', data)
  },
  batchImport(data: any) {
    return api.post('/expenditures/batch', data)
  },
  uploadExcel(file: File) {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/expenditures/upload-excel', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  delete(id: number) {
    return api.delete(`/expenditures/${id}`)
  }
}
