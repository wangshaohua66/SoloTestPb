import { useUserStore } from '@/store/modules/user'

const TRACE_ID_KEY = 'X-Trace-Id'
let currentTraceId = ''

export function generateTraceId(): string {
  const timestamp = Date.now().toString(36)
  const random = Math.random().toString(36).substring(2, 10)
  return `${timestamp}-${random}`
}

export function getTraceId(): string {
  if (!currentTraceId) {
    currentTraceId = generateTraceId()
  }
  return currentTraceId
}

export function setTraceId(traceId: string): void {
  currentTraceId = traceId
  sessionStorage.setItem(TRACE_ID_KEY, traceId)
}

export function clearTraceId(): void {
  currentTraceId = ''
  sessionStorage.removeItem(TRACE_ID_KEY)
}

export interface LogEntry {
  timestamp: number
  traceId: string
  userId?: string
  username?: string
  type: 'request' | 'response' | 'error' | 'action' | 'info'
  module: string
  content: any
}

const logBuffer: LogEntry[] = []
const MAX_BUFFER_SIZE = 100
const FLUSH_INTERVAL = 5000

function flushLogs(): void {
  if (logBuffer.length === 0) return

  const logs = [...logBuffer]
  logBuffer.length = 0

  if (import.meta.env.DEV) {
    logs.forEach(log => {
      const prefix = `[${new Date(log.timestamp).toISOString()}] [${log.type.toUpperCase()}] [${log.traceId}]`
      if (log.type === 'error') {
        console.error(prefix, log.module, log.content)
      } else {
        console.log(prefix, log.module, log.content)
      }
    })
  } else {
    console.log('[LOGGER] Flushing logs:', logs.length)
  }
}

setInterval(flushLogs, FLUSH_INTERVAL)

export function log(type: LogEntry['type'], module: string, content: any): void {
  const userStore = useUserStore()
  
  const entry: LogEntry = {
    timestamp: Date.now(),
    traceId: getTraceId(),
    userId: userStore.userInfo?.id,
    username: userStore.userInfo?.username,
    type,
    module,
    content
  }

  logBuffer.push(entry)

  if (logBuffer.length >= MAX_BUFFER_SIZE) {
    flushLogs()
  }
}

export function logApi(type: 'request' | 'response' | 'error', content: any): void {
  log(type, 'API', content)
}

export function logAction(module: string, action: string, data?: any): void {
  log('action', module, { action, data })
}

export function logInfo(module: string, message: string, data?: any): void {
  log('info', module, { message, data })
}

export function logError(module: string, error: Error | string, data?: any): void {
  log('error', module, {
    message: error instanceof Error ? error.message : error,
    stack: error instanceof Error ? error.stack : undefined,
    data
  })
}

export function setupLogger(): void {
  const savedTraceId = sessionStorage.getItem(TRACE_ID_KEY)
  if (savedTraceId) {
    currentTraceId = savedTraceId
  } else {
    setTraceId(generateTraceId())
  }

  window.addEventListener('beforeunload', flushLogs)
  
  logInfo('Logger', 'Logger initialized', {
    traceId: getTraceId(),
    env: import.meta.env.MODE
  })
}
