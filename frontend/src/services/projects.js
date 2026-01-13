/**
 * 專案管理服務
 * Projects service
 */

import api from './api'

export const projectsService = {
  /**
   * 獲取所有專案
   */
  async getProjects() {
    const response = await api.get('/api/projects')
    return response.data
  },

  /**
   * 創建新專案
   */
  async createProject(projectData) {
    const response = await api.post('/api/projects', projectData)
    return response.data
  },

  /**
   * 獲取專案詳情
   */
  async getProject(projectId, includePapers = false) {
    const response = await api.get(`/api/projects/${projectId}`, {
      params: { include_papers: includePapers }
    })
    return response.data
  },

  /**
   * 更新專案
   */
  async updateProject(projectId, projectData) {
    const response = await api.put(`/api/projects/${projectId}`, projectData)
    return response.data
  },

  /**
   * 刪除專案
   */
  async deleteProject(projectId) {
    const response = await api.delete(`/api/projects/${projectId}`)
    return response.data
  },

  /**
   * 獲取專案的論文列表
   */
  async getProjectPapers(projectId, sortBy = 'year', order = 'asc') {
    const response = await api.get(`/api/projects/${projectId}/papers`, {
      params: { sort: sortBy, order }
    })
    return response.data
  },

  /**
   * 獲取專案統計
   */
  async getProjectStats(projectId) {
    const response = await api.get(`/api/projects/${projectId}/stats`)
    return response.data
  }
}
