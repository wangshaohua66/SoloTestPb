<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-header">
        <img src="/vite.svg" class="logo" alt="logo" />
        <h1 class="title">在线教育平台</h1>
        <p class="subtitle">课程管理系统</p>
      </div>
      <el-form ref="formRef" :model="form" :rules="rules" class="login-form">
        <el-form-item prop="username">
          <el-input
            v-model="form.username"
            placeholder="请输入用户名"
            :prefix-icon="User"
            size="large"
            autocomplete="username"
          />
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="请输入密码"
            :prefix-icon="Lock"
            size="large"
            show-password
            autocomplete="current-password"
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        <el-button type="primary" size="large" class="login-btn" :loading="loading" @click="handleLogin">
          登录
        </el-button>
      </el-form>
      <div class="login-footer">
        <p>演示账号：admin / 123456</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import { useUserStore } from '@/store/modules/user'
import { required } from '@/utils/validator'
import { logAction } from '@/utils/logger'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const formRef = ref<FormInstance>()
const loading = ref(false)

const form = reactive({
  username: 'admin',
  password: '123456'
})

const rules: FormRules = {
  username: [required('请输入用户名')],
  password: [required('请输入密码')]
}

async function handleLogin() {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    loading.value = true
    try {
      await userStore.handleLogin(form)
      logAction('Auth', 'login', { username: form.username })
      
      const redirect = (route.query.redirect as string) || '/'
      ElMessage.success('登录成功')
      router.replace(redirect)
    } catch (error) {
      // 错误已在 request 中处理
    } finally {
      loading.value = false
    }
  })
}
</script>

<style lang="scss" scoped>
.login-container {
  width: 100%;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-box {
  width: 400px;
  padding: 40px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.login-header {
  text-align: center;
  margin-bottom: 30px;

  .logo {
    width: 60px;
    height: 60px;
  }

  .title {
    margin: 16px 0 8px;
    font-size: 24px;
    font-weight: 600;
    color: $text-color-primary;
  }

  .subtitle {
    font-size: 14px;
    color: $text-color-secondary;
  }
}

.login-form {
  .login-btn {
    width: 100%;
    margin-top: 10px;
  }
}

.login-footer {
  margin-top: 20px;
  text-align: center;
  color: $text-color-secondary;
  font-size: 12px;
}
</style>
