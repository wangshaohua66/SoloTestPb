export interface StudentProgress {
  id: string
  studentId: string
  studentName: string
  courseId: string
  courseName: string
  progress: number
  totalDuration: number
  watchedDuration: number
  completedChapters: number
  totalChapters: number
  quizScore: number
  quizTotalScore: number
  lastStudyTime: string
  startTime: string
  expectedFinishTime?: string
}

export interface ChapterProgress {
  id: string
  chapterId: string
  chapterTitle: string
  studentId: string
  isCompleted: boolean
  watchedPercentage: number
  watchedDuration: number
  quizScore?: number
  lastWatchTime: string
}

export interface ProgressStatistics {
  totalStudents: number
  totalCourses: number
  averageProgress: number
  completionRate: number
  weeklyActiveStudents: number
  dailyStudyTrend: DailyStudyData[]
  courseCompletionRank: CourseRankItem[]
  studyDurationDistribution: DistributionItem[]
  difficultyDistribution: DistributionItem[]
}

export interface DistributionItem {
  name: string
  value: number
  color?: string
}

export interface DailyStudyData {
  date: string
  studyCount: number
  studyDuration: number
}

export interface CourseRankItem {
  courseId: string
  courseName: string
  completionRate: number
  studentCount: number
}
