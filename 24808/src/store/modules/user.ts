import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login, logout, getUserInfo } from '@/api/user'
import type { User, UserLoginForm } from '@/types'
import config from '@/config'

export const useUserStore = defineStore('user', () => {
  const token = ref<string>(localStorage.getItem(config.storage.tokenKey) || '')
  const userInfo = ref<User | null>(null)
  const roles = ref<string[]>([])
  const permissions = ref<string[]>([])

  const isLoggedIn = computed(() => !!token.value)

  async function handleLogin(form: UserLoginForm): Promise<void> {
    const result = await login(form)
    token.value = result.token
    userInfo.value = result.userInfo
    roles.value = result.userInfo.roles
    permissions.value = result.userInfo.permissions
    localStorage.setItem(config.storage.tokenKey, result.token)
    localStorage.setItem(config.storage.userKey, JSON.stringify(result.userInfo))
  }

  async function getUserInfoAction(): Promise<User> {
    const user = await getUserInfo()
    userInfo.value = user
    roles.value = user.roles
    permissions.value = user.permissions
    return user
  }

  async function handleLogout(): Promise<void> {
    try {
      await logout()
    } finally {
      resetToken()
    }
  }

  function resetToken(): void {
    token.value = ''
    userInfo.value = null
    roles.value = []
    permissions.value = []
    localStorage.removeItem(config.storage.tokenKey)
    localStorage.removeItem(config.storage.userKey)
  }

  function initFromStorage(): void {
    const savedUser = localStorage.getItem(config.storage.userKey)
    if (savedUser) {
      try {
        const user = JSON.parse(savedUser) as User
        userInfo.value = user
        roles.value = user.roles
        permissions.value = user.permissions
      } catch (e) {
        localStorage.removeItem(config.storage.userKey)
      }
    }
  }

  return {
    token,
    userInfo,
    roles,
    permissions,
    isLoggedIn,
    handleLogin,
    getUserInfo: getUserInfoAction,
    handleLogout,
    resetToken,
    initFromStorage
  }
})
