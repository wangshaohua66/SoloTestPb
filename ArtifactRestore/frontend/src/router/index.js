import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Home.vue')
  },
  {
    path: '/artifacts',
    name: 'Artifacts',
    component: () => import('../views/Artifacts.vue')
  },
  {
    path: '/artifacts/:id',
    name: 'ArtifactDetail',
    component: () => import('../views/ArtifactDetail.vue')
  },
  {
    path: '/plans',
    name: 'Plans',
    component: () => import('../views/Plans.vue')
  },
  {
    path: '/processes',
    name: 'Processes',
    component: () => import('../views/Processes.vue')
  },
  {
    path: '/images',
    name: 'Images',
    component: () => import('../views/Images.vue')
  },
  {
    path: '/materials',
    name: 'Materials',
    component: () => import('../views/Materials.vue')
  },
  {
    path: '/export',
    name: 'Export',
    component: () => import('../views/Export.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
