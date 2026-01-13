/**
 * 論文管理服務
 * Papers service
 */

import api from './api'

export const papersService = {
  /**
   * 導入 BibTeX 文獻
   */
  async importBibTeX(projectId, bibtexContent) {
    const response = await api.post('/api/papers/import/bibtex', {
      project_id: projectId,
      bibtex_content: bibtexContent
    })
    return response.data
  },

  /**
   * 通過 DOI 導入論文
   */
  async importDOI(projectId, doi) {
    const response = await api.post('/api/papers/import/doi', {
      project_id: projectId,
      doi
    })
    return response.data
  },

  /**
   * 獲取論文詳情
   */
  async getPaper(paperId, includeFullText = false) {
    const response = await api.get(`/api/papers/${paperId}`, {
      params: { include_full_text: includeFullText }
    })
    return response.data
  },

  /**
   * 更新論文
   */
  async updatePaper(paperId, paperData) {
    const response = await api.put(`/api/papers/${paperId}`, paperData)
    return response.data
  },

  /**
   * 刪除論文
   */
  async deletePaper(paperId) {
    const response = await api.delete(`/api/papers/${paperId}`)
    return response.data
  },

  /**
   * 更新論文筆記
   */
  async updateNotes(paperId, notes) {
    const response = await api.put(`/api/papers/${paperId}/notes`, { notes })
    return response.data
  },

  /**
   * 更新閱讀狀態
   */
  async updateReadStatus(paperId, status) {
    const response = await api.put(`/api/papers/${paperId}/read-status`, { status })
    return response.data
  },

  /**
   * 更新論文標籤
   */
  async updateTags(paperId, tags) {
    const response = await api.put(`/api/papers/${paperId}/tags`, { tags })
    return response.data
  },

  /**
   * 更新論文高亮
   */
  async updateHighlights(paperId, highlights) {
    const response = await api.put(`/api/papers/${paperId}/highlights`, { highlights })
    return response.data
  },

  /**
   * 從 PDF 提取內容
   */
  async extractPDFContent(paperId, pdfFile) {
    const formData = new FormData()
    formData.append('file', pdfFile)

    const response = await api.post(`/api/papers/${paperId}/extract`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return response.data
  }
}
