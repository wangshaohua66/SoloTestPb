<template>
  <div class="error-page">
    <div class="error-content">
      <h1 class="error-code">404</h1>
      <p class="error-message">抱歉，您访问的页面不存在</p>
      <el-button type="primary" @click="handleBack">返回首页</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

function handleBack() {
  router.push('/')
}
</script>

<style lang="scss" scoped>
.error-page {
  width: 100%;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

  .error-content {
    text-align: center;
    color: #fff;

    .error-code {
      font-size: 120px;
      font-weight: 700;
      margin-bottom: 20px;
      text-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    }

    .error-message {
      font-size: 20px;
      margin-bottom: 40px;
      opacity: 0.9;
    }
  }
}
</style>
