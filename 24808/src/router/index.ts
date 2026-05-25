import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'

const Layout = () => import('@/layout/index.vue')

export const asyncRoutes: RouteRecordRaw[] = [
  {
    path: '/course',
    component: Layout,
    meta: { title: '课程管理', icon: 'Reading' },
    children: [
      {
        path: 'catalog',
        name: 'CourseCatalog',
        component: () => import('@/views/course/Catalog.vue'),
        meta: { title: '课程目录', icon: 'Folder' }
      },
      {
        path: 'list',
        name: 'CourseList',
        component: () => import('@/views/course/List.vue'),
        meta: { title: '课程列表', icon: 'List' }
      },
      {
        path: 'create',
        name: 'CourseCreate',
        component: () => import('@/views/course/Create.vue'),
        meta: { title: '创建课程', icon: 'Plus' }
      },
      {
        path: 'edit/:id',
        name: 'CourseEdit',
        component: () => import('@/views/course/Edit.vue'),
        meta: { title: '编辑课程', hidden: true }
      }
    ]
  },
  {
    path: '/chapter',
    component: Layout,
    meta: { title: '章节管理', icon: 'Document' },
    children: [
      {
        path: 'list/:courseId',
        name: 'ChapterList',
        component: () => import('@/views/chapter/List.vue'),
        meta: { title: '章节列表', hidden: true }
      },
      {
        path: 'edit/:id',
        name: 'ChapterEdit',
        component: () => import('@/views/chapter/Edit.vue'),
        meta: { title: '编辑章节', hidden: true }
      }
    ]
  },
  {
    path: '/quiz',
    component: Layout,
    meta: { title: '测验管理', icon: 'Tickets' },
    children: [
      {
        path: 'list',
        name: 'QuizList',
        component: () => import('@/views/quiz/List.vue'),
        meta: { title: '测验列表', icon: 'DocumentCopy' }
      },
      {
        path: 'create',
        name: 'QuizCreate',
        component: () => import('@/views/quiz/Create.vue'),
        meta: { title: '创建测验', icon: 'AddDocument' }
      }
    ]
  },
  {
    path: '/progress',
    component: Layout,
    meta: { title: '学习进度', icon: 'DataLine' },
    children: [
      {
        path: 'tracking',
        name: 'ProgressTracking',
        component: () => import('@/views/progress/Tracking.vue'),
        meta: { title: '进度追踪', icon: 'TrendCharts' }
      },
      {
        path: 'statistics',
        name: 'ProgressStatistics',
        component: () => import('@/views/progress/Statistics.vue'),
        meta: { title: '数据统计', icon: 'DataAnalysis' }
      }
    ]
  }
]

const constantRoutes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/login/index.vue'),
    meta: { title: '登录', hidden: true }
  },
  {
    path: '/',
    component: Layout,
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/index.vue'),
        meta: { title: '首页', icon: 'HomeFilled' }
      }
    ]
  },
  ...asyncRoutes,
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/error/404.vue'),
    meta: { hidden: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes: constantRoutes,
  scrollBehavior: () => ({ top: 0 })
})

export default router
