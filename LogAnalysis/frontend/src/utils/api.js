import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000
})

api.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

export default {
  getLogs(params = {}) {
    return api.get('/logs', { params })
  },
  getLogById(id) {
    return api.get(`/logs/${id}`)
  },
  ingestLog(data) {
    return api.post('/logs', data)
  },
  ingestBatchLogs(data) {
    return api.post('/logs/batch', data)
  },
  getLogLevels() {
    return api.get('/logs/levels')
  },
  getServices() {
    return api.get('/logs/services')
  },
  
  searchLogs(params = {}) {
    return api.post('/search', params)
  },
  searchCount(params = {}) {
    return api.post('/search/count', params)
  },
  
  getOverview(params = {}) {
    return api.get('/stats/overview', { params })
  },
  getStatsSummary(params = {}) {
    return api.get('/stats/summary', { params })
  },
  getStatsByLevel(params = {}) {
    return api.get('/stats/by-level', { params })
  },
  getStatsByService(params = {}) {
    return api.get('/stats/by-service', { params })
  },
  getStatsByModule(params = {}) {
    return api.get('/stats/by-module', { params })
  },
  getTimeSeries(params = {}) {
    return api.get('/stats/time-series', { params })
  },
  getTrend(params = {}) {
    return api.get('/stats/trend', { params })
  },
  getTopServices(params = {}) {
    return api.get('/stats/top-services', { params })
  },
  getErrorRate(params = {}) {
    return api.get('/stats/error-rate', { params })
  },
  
  getAlerts(params = {}) {
    return api.get('/alerts', { params })
  },
  getAlertById(id) {
    return api.get(`/alerts/${id}`)
  },
  acknowledgeAlert(id, data = {}) {
    return api.post(`/alerts/${id}/acknowledge`, data)
  },
  resolveAlert(id, data = {}) {
    return api.post(`/alerts/${id}/resolve`, data)
  },
  getAlertRules(params = {}) {
    return api.get('/alerts/rules', { params })
  },
  createAlertRule(data) {
    return api.post('/alerts/rules', data)
  },
  updateAlertRule(id, data) {
    return api.put(`/alerts/rules/${id}`, data)
  },
  deleteAlertRule(id) {
    return api.delete(`/alerts/rules/${id}`)
  },
  toggleAlertRule(id) {
    return api.post(`/alerts/rules/${id}/toggle`)
  },
  getAlertStats(params = {}) {
    return api.get('/alerts/stats', { params })
  },
  
  getSummaryReport(params = {}) {
    return api.get('/reports/summary', { params })
  },
  getDetailedReport(params = {}) {
    return api.get('/reports/detailed', { params })
  },
  exportReport(params = {}) {
    return api.get('/reports/export', { params, responseType: 'blob' })
  },
  
  getSources(params = {}) {
    return api.get('/collect/sources', { params })
  },
  createSource(data) {
    return api.post('/collect/sources', data)
  },
  updateSource(id, data) {
    return api.put(`/collect/sources/${id}`, data)
  },
  deleteSource(id) {
    return api.delete(`/collect/sources/${id}`)
  },
  toggleSource(id) {
    return api.post(`/collect/sources/${id}/toggle`)
  },
  getParseRules(params = {}) {
    return api.get('/collect/parse-rules', { params })
  },
  createParseRule(data) {
    return api.post('/collect/parse-rules', data)
  },
  updateParseRule(id, data) {
    return api.put(`/collect/parse-rules/${id}`, data)
  },
  deleteParseRule(id) {
    return api.delete(`/collect/parse-rules/${id}`)
  },
  testParse(data) {
    return api.post('/collect/test-parse', data)
  },
  getSourceTypes() {
    return api.get('/collect/source-types')
  }
}
