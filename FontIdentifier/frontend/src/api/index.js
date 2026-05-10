/**
 * Axios API配置模块
 * 统一配置API请求实例
 */

import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

api.interceptors.request.use(
  config => {
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

api.interceptors.response.use(
  response => {
    return response
  },
  error => {
    console.error('API请求错误:', error)
    return Promise.reject(error)
  }
)

export const fontApi = {
  recognizeByText(description) {
    return api.post('/recognize', { description })
  },

  recognizeByImage(formData) {
    return api.post('/recognize/image', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  getAllFonts() {
    return api.get('/fonts')
  },

  getFontDetail(fontName) {
    return api.get(`/fonts/${fontName}`)
  },

  getFontNames() {
    return api.get('/fonts/names')
  },

  getHistory(limit = 50, offset = 0) {
    return api.get('/history', {
      params: { limit, offset }
    })
  },

  getHistoryDetail(recordId) {
    return api.get(`/history/${recordId}`)
  },

  getStats() {
    return api.get('/stats')
  },

  exportReport(recordId) {
    return api.get(`/export/${recordId}`, {
      responseType: 'blob'
    })
  },

  exportReportDirect(result, inputText) {
    return api.post('/export', {
      result,
      input_text: inputText
    }, {
      responseType: 'blob'
    })
  }
}

export default api
