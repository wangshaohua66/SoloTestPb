import request from '@/utils/request'
import type { ChunkUploadParams, ChunkInfo } from '@/types/api'
import config from '@/config'

async function calculateFileHash(file: File): Promise<string> {
  return new Promise((resolve) => {
    const reader = new FileReader()
    reader.onload = (e) => {
      const buffer = e.target?.result as ArrayBuffer
      const hash = simpleHash(buffer)
      resolve(hash)
    }
    reader.readAsArrayBuffer(file)
  })
}

function simpleHash(buffer: ArrayBuffer): string {
  const view = new Uint8Array(buffer)
  let hash = 0
  for (let i = 0; i < view.length; i++) {
    hash = ((hash << 5) - hash + view[i]) | 0
  }
  return Math.abs(hash).toString(36) + Date.now().toString(36)
}

export async function chunkUpload(params: ChunkUploadParams): Promise<string> {
  const { file, chunkSize = config.upload.chunkSize, onProgress, onChunkComplete } = params
  const totalChunks = Math.ceil(file.size / chunkSize)
  const fileHash = await calculateFileHash(file)

  const checkResponse = await request.post('/upload/check-chunks', {
    fileHash,
    fileName: file.name,
    totalChunks
  })

  const uploadedChunks = (checkResponse as { uploadedChunks: number[] }).uploadedChunks || []

  for (let i = 0; i < totalChunks; i++) {
    if (uploadedChunks.includes(i)) {
      onChunkComplete?.(i, totalChunks)
      continue
    }

    const start = i * chunkSize
    const end = Math.min(start + chunkSize, file.size)
    const chunk = file.slice(start, end)

    const formData = new FormData()
    formData.append('file', chunk)
    formData.append('fileHash', fileHash)
    formData.append('chunkIndex', i.toString())
    formData.append('totalChunks', totalChunks.toString())
    formData.append('fileName', file.name)

    await request.post('/upload/chunk', formData)

    onChunkComplete?.(i, totalChunks)
    const progress = Math.round(((i + 1) / totalChunks) * 100)
    onProgress?.(progress)
  }

  const mergeResponse = await request.post('/upload/merge', {
    fileHash,
    fileName: file.name,
    totalChunks
  })

  return (mergeResponse as { url: string }).url
}

export function uploadImage(file: File): Promise<{ url: string }> {
  const formData = new FormData()
  formData.append('file', file)
  return request.post('/upload/image', formData)
}

export function uploadFile(file: File): Promise<{ url: string; name: string }> {
  const formData = new FormData()
  formData.append('file', file)
  return request.post('/upload/file', formData)
}
