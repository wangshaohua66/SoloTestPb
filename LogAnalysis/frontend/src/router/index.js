import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue')
  },
  {
    path: '/logs',
    name: 'Logs',
    component: () => import('@/views/LogList.vue')
  },
  {
    path: '/search',
    name: 'Search',
    component: () => import('@/views/LogSearch.vue')
  },
  {
    path: '/stats',
    name: 'Stats',
    component: () => import('@/views/Statistics.vue')
  },
  {
    path: '/alerts',
    name: 'Alerts',
    component: () => import('@/views/Alerts.vue')
  },
  {
    path: '/reports',
    name: 'Reports',
    component: () => import('@/views/Reports.vue')
  },
  {
    path: '/config',
    name: 'Config',
    component: () => import('@/views/Config.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
