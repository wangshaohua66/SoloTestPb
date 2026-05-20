import request from '@/utils/request'
import type {
  Course,
  CourseForm,
  CourseQueryParams,
  CourseListResult,
  CourseCatalog
} from '@/types'

export function getCourseList(params: CourseQueryParams): Promise<CourseListResult> {
  return request.get('/courses', { params })
}

export function getCourseDetail(id: string): Promise<Course> {
  return request.get(`/courses/${id}`)
}

export function createCourse(data: CourseForm): Promise<Course> {
  return request.post('/courses', data)
}

export function updateCourse(id: string, data: CourseForm): Promise<Course> {
  return request.put(`/courses/${id}`, data)
}

export function deleteCourse(id: string): Promise<void> {
  return request.delete(`/courses/${id}`)
}

export function updateCourseStatus(id: string, status: string): Promise<void> {
  return request.patch(`/courses/${id}/status`, { status })
}

export function publishCourse(id: string): Promise<void> {
  return request.post(`/courses/${id}/publish`)
}

export function offlineCourse(id: string, reason: string): Promise<void> {
  return request.post(`/courses/${id}/offline`, { reason })
}

export function submitReview(id: string): Promise<void> {
  return request.post(`/courses/${id}/submit-review`)
}

export function getCatalogTree(): Promise<CourseCatalog[]> {
  return request.get('/course-catalogs/tree')
}

export function getCatalogList(parentId?: string): Promise<CourseCatalog[]> {
  const params = parentId ? { parentId } : undefined
  return request.get('/course-catalogs', { params })
}

export function createCatalog(data: Partial<CourseCatalog>): Promise<CourseCatalog> {
  return request.post('/course-catalogs', data)
}

export function updateCatalog(id: string, data: Partial<CourseCatalog>): Promise<CourseCatalog> {
  return request.put(`/course-catalogs/${id}`, data)
}

export function deleteCatalog(id: string): Promise<void> {
  return request.delete(`/course-catalogs/${id}`)
}

export function updateCatalogSort(items: { id: string; sort: number }[]): Promise<void> {
  return request.patch('/course-catalogs/sort', { items })
}
