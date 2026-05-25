export interface Quiz {
  id: string
  title: string
  description: string
  type: 'single' | 'multiple' | 'judge' | 'fill'
  difficulty: 'easy' | 'medium' | 'hard'
  score: number
  options: QuizOption[]
  answer: string | string[]
  analysis: string
  tags: string[]
  chapterId?: string
  courseId?: string
  createdAt: string
  updatedAt: string
}

export interface QuizOption {
  label: string
  value: string
}

export interface QuizQueryParams {
  keyword?: string
  type?: string
  difficulty?: string
  chapterId?: string
  courseId?: string
  page: number
  pageSize: number
}

export interface QuizGenerateParams {
  count: number
  difficulty?: string
  type?: string
  chapterIds?: string[]
  courseId?: string
}
