/**
 * 認證服務
 * Authentication service
 */

import api from './api'

export const authService = {
  /**
   * 用戶註冊
   */
  async register(userData) {
    const response = await api.post('/api/auth/register', userData)
    if (response.data.success) {
      // 保存 token 和用戶資訊
      localStorage.setItem('access_token', response.data.access_token)
      localStorage.setItem('user', JSON.stringify(response.data.user))
    }
    return response.data
  },

  /**
   * 用戶登入
   */
  async login(email, password) {
    const response = await api.post('/api/auth/login', { email, password })
    if (response.data.success) {
      // 保存 token 和用戶資訊
      localStorage.setItem('access_token', response.data.access_token)
      localStorage.setItem('user', JSON.stringify(response.data.user))
    }
    return response.data
  },

  /**
   * 登出
   */
  logout() {
    localStorage.removeItem('access_token')
    localStorage.removeItem('user')
    window.location.href = '/login'
  },

  /**
   * 獲取當前用戶
   */
  async getCurrentUser() {
    const response = await api.get('/api/auth/me')
    if (response.data.success) {
      localStorage.setItem('user', JSON.stringify(response.data.user))
    }
    return response.data.user
  },

  /**
   * 更新用戶資料
   */
  async updateProfile(userData) {
    const response = await api.put('/api/auth/update-profile', userData)
    if (response.data.success) {
      localStorage.setItem('user', JSON.stringify(response.data.user))
    }
    return response.data
  },

  /**
   * 檢查是否已登入
   */
  isAuthenticated() {
    return !!localStorage.getItem('access_token')
  },

  /**
   * 獲取本地存儲的用戶資訊
   */
  getUser() {
    const userStr = localStorage.getItem('user')
    return userStr ? JSON.parse(userStr) : null
  }
}
