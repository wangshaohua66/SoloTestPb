import type { Quiz } from './quiz'

export interface Chapter {
  id: string
  courseId: string
  title: string
  description: string
  content: string
  videoUrl?: string
  videoDuration?: number
  attachmentUrl?: string
  attachmentName?: string
  sort: number
  isFree: boolean
  quizzes: Quiz[]
  createdAt: string
  updatedAt: string
}

export interface ChapterForm {
  id?: string
  courseId: string
  title: string
  description: string
  content: string
  videoUrl?: string
  videoDuration?: number
  attachmentUrl?: string
  attachmentName?: string
  sort: number
  isFree: boolean
  quizIds: string[]
}
