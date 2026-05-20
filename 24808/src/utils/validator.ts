import type { FormItemRule } from 'element-plus'

export const required = (message = '该项为必填项'): FormItemRule => ({
  required: true,
  message,
  trigger: 'blur'
})

export const email = (message = '请输入有效的邮箱地址'): FormItemRule => ({
  pattern: /^[\w-]+(\.[\w-]+)*@[\w-]+(\.[\w-]+)+$/,
  message,
  trigger: 'blur'
})

export const phone = (message = '请输入有效的手机号码'): FormItemRule => ({
  pattern: /^1[3-9]\d{9}$/,
  message,
  trigger: 'blur'
})

export const minLength = (min: number, message?: string): FormItemRule => ({
  min,
  message: message || `最少输入 ${min} 个字符`,
  trigger: 'blur'
})

export const maxLength = (max: number, message?: string): FormItemRule => ({
  max,
  message: message || `最多输入 ${max} 个字符`,
  trigger: 'blur'
})

export const rangeLength = (min: number, max: number, message?: string): FormItemRule => ({
  min,
  max,
  message: message || `请输入 ${min}-${max} 个字符`,
  trigger: 'blur'
})

export const number = (message = '请输入数字'): FormItemRule => ({
  pattern: /^\d+(\.\d+)?$/,
  message,
  trigger: 'blur'
})

export const integer = (message = '请输入整数'): FormItemRule => ({
  pattern: /^-?\d+$/,
  message,
  trigger: 'blur'
})

export const positiveNumber = (message = '请输入正数'): FormItemRule => ({
  pattern: /^\d+(\.\d+)?$/,
  validator: (_rule, value, callback) => {
    if (value === '' || value === null || value === undefined) {
      callback()
      return
    }
    const num = Number(value)
    if (isNaN(num) || num <= 0) {
      callback(new Error(message))
    } else {
      callback()
    }
  },
  trigger: 'blur'
})

export const url = (message = '请输入有效的URL'): FormItemRule => ({
  pattern: /^(https?:\/\/)?([\da-z.-]+)\.([a-z.]{2,6})([/\w .-]*)*\/?$/,
  message,
  trigger: 'blur'
})

export const password = (message = '密码需包含字母和数字，长度6-20位'): FormItemRule => ({
  pattern: /^(?=.*[a-zA-Z])(?=.*\d)[a-zA-Z\d]{6,20}$/,
  message,
  trigger: 'blur'
})

export interface AsyncValidatorOptions {
  validator: (value: any) => Promise<boolean>
  message?: string
}

export const asyncValidator = (options: AsyncValidatorOptions): FormItemRule => ({
  validator: async (_rule, value, callback) => {
    if (value === '' || value === null || value === undefined) {
      callback()
      return
    }
    try {
      const isValid = await options.validator(value)
      if (isValid) {
        callback()
      } else {
        callback(new Error(options.message || '校验失败'))
      }
    } catch (error) {
      callback(new Error(options.message || '校验失败'))
    }
  },
  trigger: 'blur'
})

export function createFormRules<T extends Record<string, FormItemRule | FormItemRule[]>>(
  rules: T
): T {
  return rules
}
