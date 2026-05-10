import axios from 'axios'
import { ElMessage } from 'element-plus'

const request = axios.create({
  baseURL: '',
  timeout: 30000
})

request.interceptors.request.use(
  config => {
    return config
  },
  error => {
    ElMessage.error('请求发送失败')
    return Promise.reject(error)
  }
)

request.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    if (error.response) {
      const status = error.response.status
      switch (status) {
        case 400:
          ElMessage.error('请求参数错误')
          break
        case 404:
          ElMessage.error('请求资源不存在')
          break
        case 500:
          ElMessage.error('服务器内部错误')
          break
        default:
          ElMessage.error(`请求失败 (${status})`)
      }
    } else if (error.request) {
      ElMessage.error('网络错误，请检查网络连接')
    } else {
      ElMessage.error(error.message || '请求失败')
    }
    return Promise.reject(error)
  }
)

export const artifactApi = {
  getList(params) {
    return request({ url: '/api/artifacts/', method: 'get', params })
  },
  getDetail(id) {
    return request({ url: `/api/artifacts/${id}`, method: 'get' })
  },
  create(data) {
    return request({ url: '/api/artifacts/', method: 'post', data })
  },
  update(id, data) {
    return request({ url: `/api/artifacts/${id}`, method: 'put', data })
  },
  delete(id) {
    return request({ url: `/api/artifacts/${id}`, method: 'delete' })
  }
}

export const planApi = {
  getList(params) {
    return request({ url: '/api/plans/', method: 'get', params })
  },
  getDetail(id) {
    return request({ url: `/api/plans/${id}`, method: 'get' })
  },
  create(data) {
    return request({ url: '/api/plans/', method: 'post', data })
  },
  update(id, data) {
    return request({ url: `/api/plans/${id}`, method: 'put', data })
  },
  delete(id) {
    return request({ url: `/api/plans/${id}`, method: 'delete' })
  }
}

export const processApi = {
  getList(params) {
    return request({ url: '/api/processes/', method: 'get', params })
  },
  getDetail(id) {
    return request({ url: `/api/processes/${id}`, method: 'get' })
  },
  create(data) {
    return request({ url: '/api/processes/', method: 'post', data })
  },
  update(id, data) {
    return request({ url: `/api/processes/${id}`, method: 'put', data })
  },
  delete(id) {
    return request({ url: `/api/processes/${id}`, method: 'delete' })
  }
}

export const imageApi = {
  getList(params) {
    return request({ url: '/api/images/', method: 'get', params })
  },
  getDetail(id) {
    return request({ url: `/api/images/${id}`, method: 'get' })
  },
  create(formData) {
    return request({
      url: '/api/images/',
      method: 'post',
      data: formData,
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  update(id, data) {
    return request({ url: `/api/images/${id}`, method: 'put', data })
  },
  delete(id) {
    return request({ url: `/api/images/${id}`, method: 'delete' })
  }
}

export const materialApi = {
  getList(params) {
    return request({ url: '/api/materials/', method: 'get', params })
  },
  getDetail(id) {
    return request({ url: `/api/materials/${id}`, method: 'get' })
  },
  create(data) {
    return request({ url: '/api/materials/', method: 'post', data })
  },
  update(id, data) {
    return request({ url: `/api/materials/${id}`, method: 'put', data })
  },
  delete(id) {
    return request({ url: `/api/materials/${id}`, method: 'delete' })
  }
}

export const exportApi = {
  getStats() {
    return request({ url: '/api/export/stats', method: 'get' })
  },
  getList(params) {
    return request({ url: '/api/export/list', method: 'get', params })
  },
  exportArtifact(id, format = 'txt') {
    window.open(`/api/export/artifact/${id}?format=${format}`, '_blank')
  },
  exportBatch(ids, format = 'txt') {
    const url = `/api/export/batch?ids=${ids.join(',')}&format=${format}`
    window.open(url, '_blank')
  },
  getHistory(params) {
    return request({ url: '/api/export/history', method: 'get', params })
  }
}
