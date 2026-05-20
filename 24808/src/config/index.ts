import type { App } from 'vue'

const env = import.meta.env

export interface AppConfig {
  app: {
    title: string
    version: string
    env: string
  }
  api: {
    baseUrl: string
    timeout: number
    retryCount: number
    retryDelay: number
  }
  request: {
    timeout: number
    retryCount: number
    retryDelay: number
  }
  upload: {
    chunkSize: number
    maxSize: number
    allowedTypes: string[]
  }
  storage: {
    tokenKey: string
    userKey: string
    expiresIn: number
  }
  features: {
    enableMock: boolean
    enableTrace: boolean
    enableConcurrentControl: boolean
  }
}

const config: AppConfig = {
  app: {
    title: env.VITE_APP_TITLE || '在线教育平台',
    version: '1.0.0',
    env: env.MODE
  },
  api: {
    baseUrl: '/api',
    timeout: parseInt(env.VITE_REQUEST_TIMEOUT || '30000'),
    retryCount: parseInt(env.VITE_MAX_RETRY_COUNT || '3'),
    retryDelay: 1000
  },
  request: {
    timeout: parseInt(env.VITE_REQUEST_TIMEOUT || '30000'),
    retryCount: parseInt(env.VITE_MAX_RETRY_COUNT || '3'),
    retryDelay: 1000
  },
  upload: {
    chunkSize: parseInt(env.VITE_UPLOAD_CHUNK_SIZE || '5242880'),
    maxSize: 500 * 1024 * 1024,
    allowedTypes: ['video/mp4', 'video/avi', 'video/mov', 'application/pdf', 'application/msword', 'image/jpeg', 'image/png']
  },
  storage: {
    tokenKey: 'admin_token',
    userKey: 'admin_user',
    expiresIn: 7 * 24 * 60 * 60 * 1000
  },
  features: {
    enableMock: env.VITE_ENABLE_MOCK === 'true',
    enableTrace: true,
    enableConcurrentControl: true
  }
}

export function setupConfig(app: App): void {
  app.config.globalProperties.$config = config
}

export default config
