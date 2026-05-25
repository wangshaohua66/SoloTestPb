export interface PaginationParams {
  page: number
  pageSize: number
}

export interface PaginationResult<T> {
  list: T[]
  total: number
  page: number
  pageSize: number
}

export interface TreeItem<T = any> {
  id: string | number
  label: string
  children?: TreeItem<T>[]
  parentId?: string | number
  sort?: number
  data?: T
}

export interface ResponseResult<T = any> {
  code: number
  message: string
  data: T
  traceId: string
  timestamp: number
}

export interface SelectOption {
  label: string
  value: string | number
  disabled?: boolean
}

export enum Status {
  DRAFT = 'draft',
  PENDING = 'pending',
  PUBLISHED = 'published',
  OFFLINE = 'offline'
}

export const StatusMap: Record<Status, { label: string; type: 'info' | 'warning' | 'success' | 'danger' }> = {
  [Status.DRAFT]: { label: '草稿', type: 'info' },
  [Status.PENDING]: { label: '审核中', type: 'warning' },
  [Status.PUBLISHED]: { label: '已发布', type: 'success' },
  [Status.OFFLINE]: { label: '已下线', type: 'danger' }
}
