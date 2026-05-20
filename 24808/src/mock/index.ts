import type { Course, Chapter, Quiz, StudentProgress, ProgressStatistics, CourseCatalog } from '@/types'
import dayjs from 'dayjs'

export const mockCourses: Course[] = [
  {
    id: '1',
    title: 'Vue3 从入门到精通',
    description: '全面掌握 Vue3 组合式 API、Pinia 状态管理、Vite 构建工具等核心技术',
    content: '<p>详细内容...</p>',
    coverImage: 'https://picsum.photos/320/180?random=1',
    teacherId: '1',
    teacherName: '张老师',
    catalogId: '1',
    catalogName: '前端开发',
    price: 199,
    originalPrice: 299,
    isFree: false,
    difficulty: 'intermediate',
    status: 'published',
    tags: ['Vue3', 'TypeScript', '前端'],
    studentCount: 1568,
    rating: 4.8,
    chapters: [],
    createdAt: '2024-01-01',
    updatedAt: '2024-01-15'
  },
  {
    id: '2',
    title: 'TypeScript 高级编程',
    description: '深入理解 TypeScript 类型系统、泛型编程、高级类型体操',
    content: '<p>详细内容...</p>',
    coverImage: 'https://picsum.photos/320/180?random=2',
    teacherId: '2',
    teacherName: '李老师',
    catalogId: '1',
    catalogName: '前端开发',
    price: 299,
    originalPrice: 399,
    isFree: false,
    difficulty: 'advanced',
    status: 'published',
    tags: ['TypeScript', '前端'],
    studentCount: 1234,
    rating: 4.9,
    chapters: [],
    createdAt: '2024-01-02',
    updatedAt: '2024-01-16'
  },
  {
    id: '3',
    title: 'Node.js 后端开发实战',
    description: '使用 Node.js + Express + MongoDB 构建企业级后端服务',
    content: '<p>详细内容...</p>',
    coverImage: 'https://picsum.photos/320/180?random=3',
    teacherId: '3',
    teacherName: '王老师',
    catalogId: '2',
    catalogName: '后端开发',
    price: 259,
    originalPrice: 359,
    isFree: false,
    difficulty: 'intermediate',
    status: 'pending',
    tags: ['Node.js', '后端', 'MongoDB'],
    studentCount: 987,
    rating: 4.7,
    chapters: [],
    createdAt: '2024-01-03',
    updatedAt: '2024-01-17'
  },
  {
    id: '4',
    title: 'React 18 全栈开发',
    description: 'React 18 新特性、Hooks 深入、Next.js 全栈开发',
    content: '<p>详细内容...</p>',
    coverImage: 'https://picsum.photos/320/180?random=4',
    teacherId: '1',
    teacherName: '张老师',
    catalogId: '1',
    catalogName: '前端开发',
    price: 0,
    originalPrice: 0,
    isFree: true,
    difficulty: 'beginner',
    status: 'draft',
    tags: ['React', 'Next.js', '前端'],
    studentCount: 876,
    rating: 4.6,
    chapters: [],
    createdAt: '2024-01-04',
    updatedAt: '2024-01-18'
  },
  {
    id: '5',
    title: '微服务架构设计',
    description: 'Spring Cloud 微服务架构、Docker 容器化、Kubernetes 编排',
    content: '<p>详细内容...</p>',
    coverImage: 'https://picsum.photos/320/180?random=5',
    teacherId: '2',
    teacherName: '李老师',
    catalogId: '2',
    catalogName: '后端开发',
    price: 399,
    originalPrice: 499,
    isFree: false,
    difficulty: 'advanced',
    status: 'published',
    tags: ['微服务', 'Docker', 'K8s'],
    studentCount: 654,
    rating: 4.8,
    chapters: [],
    createdAt: '2024-01-05',
    updatedAt: '2024-01-19'
  }
]

export const mockChapters: Chapter[] = [
  {
    id: 'c1',
    courseId: '1',
    title: 'Vue3 基础入门',
    description: '了解 Vue3 的基本概念和项目搭建',
    content: '<p>第一章内容...</p>',
    videoUrl: 'https://example.com/video1.mp4',
    videoDuration: 1200,
    attachmentUrl: '',
    attachmentName: '',
    sort: 1,
    isFree: true,
    quizzes: [],
    createdAt: '2024-01-01',
    updatedAt: '2024-01-01'
  },
  {
    id: 'c2',
    courseId: '1',
    title: '组合式 API 详解',
    description: '深入理解 Composition API',
    content: '<p>第二章内容...</p>',
    videoUrl: 'https://example.com/video2.mp4',
    videoDuration: 1800,
    attachmentUrl: '',
    attachmentName: '',
    sort: 2,
    isFree: false,
    quizzes: [],
    createdAt: '2024-01-02',
    updatedAt: '2024-01-02'
  },
  {
    id: 'c3',
    courseId: '1',
    title: 'Pinia 状态管理',
    description: '使用 Pinia 进行全局状态管理',
    content: '<p>第三章内容...</p>',
    videoUrl: 'https://example.com/video3.mp4',
    videoDuration: 1500,
    attachmentUrl: '',
    attachmentName: '',
    sort: 3,
    isFree: false,
    quizzes: [],
    createdAt: '2024-01-03',
    updatedAt: '2024-01-03'
  }
]

export const mockQuizzes: Quiz[] = [
  {
    id: 'q1',
    title: 'Vue3 中 ref 和 reactive 的区别是什么？',
    type: 'single',
    difficulty: 'easy',
    score: 5,
    options: [
      { label: 'A', value: 'ref 用于基本类型，reactive 用于对象', isAnswer: true },
      { label: 'B', value: 'ref 用于对象，reactive 用于基本类型', isAnswer: false },
      { label: 'C', value: '两者没有区别', isAnswer: false },
      { label: 'D', value: 'ref 是 Vue2 的，reactive 是 Vue3 的', isAnswer: false }
    ],
    answer: 'A',
    analysis: 'ref 主要用于包装基本类型数据，reactive 用于创建响应式对象。',
    tags: ['Vue3', '基础'],
    createdAt: '2024-01-01',
    updatedAt: '2024-01-01'
  },
  {
    id: 'q2',
    title: '以下哪些是 Vue3 的新特性？',
    type: 'multiple',
    difficulty: 'medium',
    score: 10,
    options: [
      { label: 'A', value: '组合式 API', isAnswer: true },
      { label: 'B', value: 'Teleport', isAnswer: true },
      { label: 'C', value: 'Fragments', isAnswer: true },
      { label: 'D', value: 'Vuex', isAnswer: false }
    ],
    answer: ['A', 'B', 'C'],
    analysis: 'Vue3 引入了组合式 API、Teleport、Fragments 等新特性，Vuex 是 Vue2 就有的状态管理方案。',
    tags: ['Vue3', '新特性'],
    createdAt: '2024-01-02',
    updatedAt: '2024-01-02'
  },
  {
    id: 'q3',
    title: 'TypeScript 中 interface 和 type 是完全等价的。',
    type: 'judge',
    difficulty: 'easy',
    score: 5,
    options: [],
    answer: 'false',
    analysis: 'interface 和 type 在很多场景下可以互换，但也有一些区别。interface 可以被 extends 和 implements，而 type 可以使用联合类型、交叉类型等更复杂的类型操作。',
    tags: ['TypeScript', '基础'],
    createdAt: '2024-01-03',
    updatedAt: '2024-01-03'
  }
]

export const mockStudentProgress: StudentProgress[] = [
  {
    id: 'sp1',
    studentId: 's1',
    studentName: '张三',
    avatar: '',
    courseId: '1',
    courseName: 'Vue3 从入门到精通',
    progress: 75,
    totalChapters: 10,
    completedChapters: 7,
    watchedDuration: 36000,
    quizScore: 85,
    quizTotalScore: 100,
    lastStudyTime: '2024-01-15 14:30:00'
  },
  {
    id: 'sp2',
    studentId: 's2',
    studentName: '李四',
    avatar: '',
    courseId: '1',
    courseName: 'Vue3 从入门到精通',
    progress: 45,
    totalChapters: 10,
    completedChapters: 4,
    watchedDuration: 18000,
    quizScore: 72,
    quizTotalScore: 100,
    lastStudyTime: '2024-01-14 10:20:00'
  },
  {
    id: 'sp3',
    studentId: 's3',
    studentName: '王五',
    avatar: '',
    courseId: '2',
    courseName: 'TypeScript 高级编程',
    progress: 90,
    totalChapters: 8,
    completedChapters: 7,
    watchedDuration: 45000,
    quizScore: 95,
    quizTotalScore: 100,
    lastStudyTime: '2024-01-15 16:45:00'
  }
]

export const mockProgressStatistics: ProgressStatistics = {
  totalStudents: 5680,
  totalCourses: 128,
  averageProgress: 65,
  completionRate: 42,
  weeklyActiveStudents: 1256,
  dailyStudyTrend: [
    { date: '05-14', studyCount: 120, studyDuration: 820 },
    { date: '05-15', studyCount: 132, studyDuration: 932 },
    { date: '05-16', studyCount: 145, studyDuration: 1001 },
    { date: '05-17', studyCount: 134, studyDuration: 934 },
    { date: '05-18', studyCount: 156, studyDuration: 1290 },
    { date: '05-19', studyCount: 189, studyDuration: 1330 },
    { date: '05-20', studyCount: 210, studyDuration: 1420 }
  ],
  courseCompletionRank: [
    { courseId: '1', courseName: 'Vue3 从入门到精通', completionRate: 95, studentCount: 1568 },
    { courseId: '2', courseName: 'TypeScript 高级编程', completionRate: 88, studentCount: 1234 },
    { courseId: '3', courseName: 'Node.js 后端开发', completionRate: 76, studentCount: 987 },
    { courseId: '4', courseName: 'React 实战项目', completionRate: 82, studentCount: 876 },
    { courseId: '5', courseName: '微服务架构设计', completionRate: 65, studentCount: 654 }
  ],
  studyDurationDistribution: [
    { name: '<30分钟', value: 1048, color: '#667eea' },
    { name: '30-60分钟', value: 735, color: '#764ba2' },
    { name: '1-2小时', value: 580, color: '#f093fb' },
    { name: '2-3小时', value: 484, color: '#f5576c' },
    { name: '>3小时', value: 300, color: '#4facfe' }
  ],
  difficultyDistribution: [
    { name: '初级', value: 1568, color: '#67c23a' },
    { name: '中级', value: 1024, color: '#e6a23c' },
    { name: '高级', value: 656, color: '#f56c6c' }
  ]
}

export const mockCatalogTree: CourseCatalog[] = [
  {
    id: '1',
    name: '前端开发',
    description: '前端开发相关课程',
    parentId: null,
    level: 1,
    sort: 1,
    children: [
      {
        id: '1-1',
        name: 'Vue.js',
        description: 'Vue.js 系列课程',
        parentId: '1',
        level: 2,
        sort: 1,
        children: []
      },
      {
        id: '1-2',
        name: 'React',
        description: 'React 系列课程',
        parentId: '1',
        level: 2,
        sort: 2,
        children: []
      }
    ]
  },
  {
    id: '2',
    name: '后端开发',
    description: '后端开发相关课程',
    parentId: null,
    level: 1,
    sort: 2,
    children: [
      {
        id: '2-1',
        name: 'Node.js',
        description: 'Node.js 系列课程',
        parentId: '2',
        level: 2,
        sort: 1,
        children: []
      },
      {
        id: '2-2',
        name: 'Java',
        description: 'Java 系列课程',
        parentId: '2',
        level: 2,
        sort: 2,
        children: []
      }
    ]
  }
]

export function getMockCourses() {
  return {
    list: mockCourses,
    total: mockCourses.length
  }
}

export function getMockChapters(courseId?: string) {
  const chapters = courseId ? mockChapters.filter(c => c.courseId === courseId) : mockChapters
  return {
    list: chapters,
    total: chapters.length
  }
}

export function getMockQuizzes() {
  return {
    list: mockQuizzes,
    total: mockQuizzes.length
  }
}

export function getMockStudentProgress() {
  return {
    list: mockStudentProgress,
    total: mockStudentProgress.length
  }
}

export function generateTrendData() {
  const last7Days = Array.from({ length: 7 }, (_, i) =>
    dayjs().subtract(6 - i, 'day').format('MM-DD')
  )
  return {
    xAxis: last7Days,
    students: [120, 132, 145, 134, 156, 189, 210],
    duration: [820, 932, 1001, 934, 1290, 1330, 1420]
  }
}

export function generateMonthTrendData() {
  const last7Months = Array.from({ length: 7 }, (_, i) =>
    dayjs().subtract(6 - i, 'month').format('M月')
  )
  return {
    xAxis: last7Months,
    students: [520, 632, 701, 634, 890, 930, 1020],
    duration: [2820, 3932, 4001, 3934, 4290, 4330, 4420]
  }
}
