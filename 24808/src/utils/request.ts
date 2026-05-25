import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse, AxiosError, InternalAxiosRequestConfig } from 'axios'
import { ElMessage, ElLoading } from 'element-plus'
import { useUserStore } from '@/store/modules/user'
import { getTraceId, logApi } from './logger'
import type { RequestConfig } from '@/types/api'
import type { ResponseResult } from '@/types/common'
import config from '@/config'

const pendingRequests = new Map<string, AbortController>()

const service: AxiosInstance = axios.create({
  baseURL: config.api.baseUrl,
  timeout: config.request.timeout,
  headers: {
    'Content-Type': 'application/json;charset=utf-8'
  }
})

function generateRequestKey(config: AxiosRequestConfig): string {
  const { method, url, params, data } = config
  return [method, url, JSON.stringify(params), JSON.stringify(data)].join('&')
}

function addPendingRequest(config: InternalAxiosRequestConfig): void {
  const key = generateRequestKey(config)
  if (!config.ignoreCancel && pendingRequests.has(key)) {
    const controller = pendingRequests.get(key)
    controller?.abort()
    pendingRequests.delete(key)
  }
  const controller = new AbortController()
  config.signal = controller.signal
  pendingRequests.set(key, controller)
}

function removePendingRequest(config: InternalAxiosRequestConfig): void {
  const key = generateRequestKey(config)
  if (pendingRequests.has(key)) {
    pendingRequests.delete(key)
  }
}

async function retryRequest(error: AxiosError): Promise<AxiosResponse> {
  const config = error.config as AxiosRequestConfig & RequestConfig
  const maxRetryCount = config.retryCount ?? config.request?.retryCount ?? 3
  const retryDelay = config.retryDelay ?? config.request?.retryDelay ?? 1000

  if (!config.__retryCount) {
    config.__retryCount = 0
  }

  if (config.__retryCount >= maxRetryCount) {
    return Promise.reject(error)
  }

  config.__retryCount += 1

  await new Promise(resolve => setTimeout(resolve, retryDelay))
  return service(config)
}

let loadingInstance: ReturnType<typeof ElLoading.service> | null = null
let loadingCount = 0

function showLoading(): void {
  loadingCount += 1
  if (loadingCount === 1 && !loadingInstance) {
    loadingInstance = ElLoading.service({
      lock: true,
      text: '加载中...',
      background: 'rgba(0, 0, 0, 0.7)'
    })
  }
}

function hideLoading(): void {
  loadingCount = Math.max(0, loadingCount - 1)
  if (loadingCount === 0 && loadingInstance) {
    loadingInstance.close()
    loadingInstance = null
  }
}

service.interceptors.request.use(
  (config: InternalAxiosRequestConfig & RequestConfig) => {
    const userStore = useUserStore()
    const traceId = getTraceId()

    addPendingRequest(config)

    if (config.showLoading !== false) {
      showLoading()
    }

    if (userStore.token) {
      config.headers.Authorization = `Bearer ${userStore.token}`
    }

    config.headers['X-Trace-Id'] = traceId
    config.headers['X-Timestamp'] = Date.now().toString()

    if (config.enableTrace !== false) {
      logApi('request', {
        traceId,
        url: config.url,
        method: config.method,
        params: config.params,
        data: config.data
      })
    }

    return config
  },
  (error: AxiosError) => {
    hideLoading()
    return Promise.reject(error)
  }
)

service.interceptors.response.use(
  (response: AxiosResponse) => {
    hideLoading()
    removePendingRequest(response.config as InternalAxiosRequestConfig)

    const res = response.data as ResponseResult
    const traceId = response.headers['x-trace-id'] || getTraceId()

    logApi('response', {
      traceId,
      url: response.config.url,
      status: response.status,
      data: res
    })

    if (res.code !== 200) {
      ElMessage.error(res.message || '请求失败')
      
      if (res.code === 401) {
        const userStore = useUserStore()
        userStore.resetToken()
        window.location.reload()
      }
      
      return Promise.reject(new Error(res.message || '请求失败'))
    }

    return res.data
  },
  async (error: AxiosError) => {
    hideLoading()
    
    if (error.config) {
      removePendingRequest(error.config as InternalAxiosRequestConfig)
    }

    if (error.code === 'ERR_CANCELED') {
      return Promise.reject(error)
    }

    const shouldRetry = !error.response || error.response.status >= 500
    if (shouldRetry && error.config) {
      try {
        return await retryRequest(error)
      } catch (retryError) {
        error = retryError as AxiosError
      }
    }

    const message = error.response?.data?.message || error.message || '网络错误'
    ElMessage.error(message)

    logApi('error', {
      traceId: getTraceId(),
      url: error.config?.url,
      error: message,
      status: error.response?.status
    })

    return Promise.reject(error)
  }
)

export function cancelAllRequests(): void {
  pendingRequests.forEach(controller => controller.abort())
  pendingRequests.clear()
  loadingCount = 0
  if (loadingInstance) {
    loadingInstance.close()
    loadingInstance = null
  }
}

export default service
