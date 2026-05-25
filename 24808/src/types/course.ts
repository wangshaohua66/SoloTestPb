import type { Status, PaginationParams, PaginationResult } from './common'
import type { Chapter } from './chapter'
import type { Quiz } from './quiz'

export interface CourseCatalog {
  id: string
  name: string
  parentId: string | null
  level: number
  sort: number
  description?: string
  children?: CourseCatalog[]
  courseCount?: number
  createdAt: string
  updatedAt: string
}

export interface Course {
  id: string
  title: string
  description: string
  coverImage: string
  catalogId: string
  catalogName?: string
  teacherId: string
  teacherName?: string
  price: number
  originalPrice?: number
  duration: number
  status: Status
  tags: string[]
  difficulty: 'beginner' | 'intermediate' | 'advanced'
  chapters: Chapter[]
  quizzes: Quiz[]
  studentCount: number
  rating: number
  isFree: boolean
  createdAt: string
  updatedAt: string
  publishedAt?: string
}

export interface CourseForm {
  id?: string
  title: string
  description: string
  coverImage: string
  catalogId: string
  teacherId: string
  price: number
  originalPrice?: number
  tags: string[]
  difficulty: 'beginner' | 'intermediate' | 'advanced'
  isFree: boolean
}

export interface CourseQueryParams extends PaginationParams {
  keyword?: string
  catalogId?: string
  status?: Status
  teacherId?: string
  difficulty?: string
}

export type CourseListResult = PaginationResult<Course>
