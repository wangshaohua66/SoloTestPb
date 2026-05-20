export interface User {
  id: string
  username: string
  nickname: string
  avatar: string
  email: string
  phone: string
  roles: string[]
  permissions: string[]
  department: string
  position: string
  createdAt: string
}

export interface UserLoginForm {
  username: string
  password: string
  captcha?: string
}

export interface UserLoginResult {
  token: string
  userInfo: User
}
