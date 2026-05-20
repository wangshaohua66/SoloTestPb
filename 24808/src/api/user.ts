import request from '@/utils/request'
import type { UserLoginForm, UserLoginResult, User } from '@/types'

export function login(data: UserLoginForm): Promise<UserLoginResult> {
  return request.post('/auth/login', data)
}

export function logout(): Promise<void> {
  return request.post('/auth/logout')
}

export function getUserInfo(): Promise<User> {
  return request.get('/auth/user-info')
}

export function getCurrentUser(): Promise<User> {
  return request.get('/users/current')
}
