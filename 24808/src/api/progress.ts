import request from '@/utils/request'
import type { StudentProgress, ChapterProgress, ProgressStatistics } from '@/types'
import type { PaginationParams, PaginationResult } from '@/types/common'

export interface ProgressQueryParams extends PaginationParams {
  courseId?: string
  studentId?: string
  keyword?: string
}

export function getStudentProgress(params: ProgressQueryParams): Promise<PaginationResult<StudentProgress>> {
  return request.get('/progress/students', { params })
}

export function getChapterProgress(studentId: string, courseId: string): Promise<ChapterProgress[]> {
  return request.get(`/progress/students/${studentId}/courses/${courseId}/chapters`)
}

export function getProgressStatistics(): Promise<ProgressStatistics> {
  return request.get('/progress/statistics')
}

export function getCourseProgress(courseId: string): Promise<{
  courseId: string
  averageProgress: number
  studentCount: number
  completionRate: number
}> {
  return request.get(`/progress/courses/${courseId}`)
}
