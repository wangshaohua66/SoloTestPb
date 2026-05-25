import request from '@/utils/request'
import type { Quiz, QuizQueryParams, QuizGenerateParams } from '@/types'
import type { PaginationResult } from '@/types/common'

export function getQuizList(params: QuizQueryParams): Promise<PaginationResult<Quiz>> {
  return request.get('/quizzes', { params })
}

export function getQuizDetail(id: string): Promise<Quiz> {
  return request.get(`/quizzes/${id}`)
}

export function createQuiz(data: Partial<Quiz>): Promise<Quiz> {
  return request.post('/quizzes', data)
}

export function updateQuiz(id: string, data: Partial<Quiz>): Promise<Quiz> {
  return request.put(`/quizzes/${id}`, data)
}

export function deleteQuiz(id: string): Promise<void> {
  return request.delete(`/quizzes/${id}`)
}

export function generateQuizzes(params: QuizGenerateParams): Promise<Quiz[]> {
  return request.post('/quizzes/generate', params)
}

export function batchDeleteQuizzes(ids: string[]): Promise<void> {
  return request.delete('/quizzes/batch', { data: { ids } })
}
