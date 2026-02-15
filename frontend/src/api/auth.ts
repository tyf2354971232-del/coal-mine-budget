import api from './index'

export const authApi = {
  login(username: string, password: string) {
    return api.post('/auth/login', { username, password })
  },
  getMe() {
    return api.get('/auth/me')
  },
  listUsers() {
    return api.get('/auth/users')
  },
  createUser(data: any) {
    return api.post('/auth/users', data)
  },
  updateUser(id: number, data: any) {
    return api.put(`/auth/users/${id}`, data)
  }
}
