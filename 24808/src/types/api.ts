export interface RequestConfig {
  showLoading?: boolean
  showError?: boolean
  retryCount?: number
  retryDelay?: number
  enableTrace?: boolean
  ignoreCancel?: boolean
}

export interface UploadFile {
  file: File
  name: string
  percentage?: number
  status: 'pending' | 'uploading' | 'success' | 'error'
  response?: any
  error?: Error
}

export interface ChunkUploadParams {
  file: File
  chunkSize?: number
  onProgress?: (percentage: number) => void
  onChunkComplete?: (chunkIndex: number, total: number) => void
}

export interface ChunkInfo {
  fileHash: string
  chunkIndex: number
  totalChunks: number
  chunk: Blob
  chunkHash: string
}
