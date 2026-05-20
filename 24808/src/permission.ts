import type { Router } from 'vue-router'
import NProgress from 'nprogress'
import { useUserStore } from '@/store/modules/user'

NProgress.configure({ showSpinner: false })

const whiteList = ['/login']

export function setupPermission(router: Router) {
  router.beforeEach(async (to, from, next) => {
    NProgress.start()
    const userStore = useUserStore()
    const hasToken = userStore.token

    if (hasToken) {
      if (to.path === '/login') {
        next({ path: '/' })
        NProgress.done()
      } else {
        const hasRoles = userStore.roles && userStore.roles.length > 0
        if (hasRoles) {
          next()
        } else {
          try {
            await userStore.getUserInfo()
            next({ ...to, replace: true })
          } catch (error) {
            await userStore.resetToken()
            next(`/login?redirect=${to.path}`)
            NProgress.done()
          }
        }
      }
    } else {
      if (whiteList.includes(to.path)) {
        next()
      } else {
        next(`/login?redirect=${to.path}`)
        NProgress.done()
      }
    }
  })

  router.afterEach(() => {
    NProgress.done()
  })
}
