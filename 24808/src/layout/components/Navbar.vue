<template>
  <div class="navbar">
    <div class="navbar-left">
      <el-icon class="toggle-btn" @click="appStore.toggleSidebar()">
        <Fold v-if="!appStore.sidebarCollapsed" />
        <Expand v-else />
      </el-icon>
      <el-breadcrumb separator="/">
        <el-breadcrumb-item v-for="item in breadcrumbs" :key="item.path">
          {{ item.meta?.title }}
        </el-breadcrumb-item>
      </el-breadcrumb>
    </div>
    <div class="navbar-right">
      <el-tooltip content="全屏" placement="bottom">
        <el-icon class="nav-icon" @click="toggleFullscreen">
          <FullScreen />
        </el-icon>
      </el-tooltip>
      <el-dropdown @command="handleCommand">
        <div class="user-info">
          <el-avatar :size="32" :src="userStore.userInfo?.avatar">
            {{ userStore.userInfo?.nickname?.charAt(0) }}
          </el-avatar>
          <span class="username">{{ userStore.userInfo?.nickname }}</span>
          <el-icon><CaretBottom /></el-icon>
        </div>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="profile">个人中心</el-dropdown-item>
            <el-dropdown-item command="settings">系统设置</el-dropdown-item>
            <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/store/modules/user'
import { useAppStore } from '@/store/modules/app'
import { ElMessageBox } from 'element-plus'
import { Fold, Expand, FullScreen, CaretBottom } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const appStore = useAppStore()

const breadcrumbs = computed(() => {
  return route.matched.filter(item => item.meta && item.meta.title)
})

function toggleFullscreen() {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen()
  } else {
    document.exitFullscreen()
  }
}

async function handleCommand(command: string) {
  switch (command) {
    case 'profile':
      router.push('/profile')
      break
    case 'settings':
      router.push('/settings')
      break
    case 'logout':
      try {
        await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        await userStore.handleLogout()
        router.push('/login')
      } catch (e) {
        // 用户取消
      }
      break
  }
}
</script>

<style lang="scss" scoped>
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
  padding: 0 20px;

  &-left {
    display: flex;
    align-items: center;
    gap: 16px;
  }

  &-right {
    display: flex;
    align-items: center;
    gap: 20px;
  }

  .toggle-btn {
    font-size: 20px;
    cursor: pointer;
    color: $text-color-regular;

    &:hover {
      color: $primary-color;
    }
  }

  .nav-icon {
    font-size: 18px;
    cursor: pointer;
    color: $text-color-regular;

    &:hover {
      color: $primary-color;
    }
  }

  .user-info {
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;

    .username {
      font-size: 14px;
      color: $text-color-regular;
    }
  }
}
</style>
