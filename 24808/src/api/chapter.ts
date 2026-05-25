import request from '@/utils/request'
import type { Chapter, ChapterForm } from '@/types'

export function getChapterList(courseId: string): Promise<Chapter[]> {
  return request.get(`/courses/${courseId}/chapters`)
}

export function getChapterDetail(id: string): Promise<Chapter> {
  return request.get(`/chapters/${id}`)
}

export function createChapter(data: ChapterForm): Promise<Chapter> {
  return request.post('/chapters', data)
}

export function updateChapter(id: string, data: ChapterForm): Promise<Chapter> {
  return request.put(`/chapters/${id}`, data)
}

export function deleteChapter(id: string): Promise<void> {
  return request.delete(`/chapters/${id}`)
}

export function updateChapterSort(courseId: string, items: { id: string; sort: number }[]): Promise<void> {
  return request.patch(`/courses/${courseId}/chapters/sort`, { items })
}

export function uploadVideo(formData: FormData, onProgress?: (percentage: number) => void): Promise<{ url: string; duration: number }> {
  return request.post('/upload/video', formData, {
    onUploadProgress: (progressEvent) => {
      if (progressEvent.total && onProgress) {
        const percentage = Math.round((progressEvent.loaded * 100) / progressEvent.total)
        onProgress(percentage)
      }
    }
  })
}

export function uploadAttachment(formData: FormData): Promise<{ url: string; name: string }> {
  return request.post('/upload/attachment', formData)
}
