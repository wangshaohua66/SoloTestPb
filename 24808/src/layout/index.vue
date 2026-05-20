<template>
  <div class="layout-container" :class="{ 'is-collapsed': appStore.sidebarCollapsed, 'is-mobile': appStore.isMobile }">
    <el-container>
      <el-aside v-if="!appStore.isMobile" width="220px" class="sidebar">
        <Logo :collapsed="appStore.sidebarCollapsed" />
        <SidebarMenu :collapsed="appStore.sidebarCollapsed" />
      </el-aside>
      <el-container>
        <el-header class="header">
          <Navbar />
        </el-header>
        <el-main class="main-content">
          <AppMain />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'
import { useAppStore } from '@/store/modules/app'
import Logo from './components/Logo.vue'
import SidebarMenu from './components/SidebarMenu.vue'
import Navbar from './components/Navbar.vue'
import AppMain from './components/AppMain.vue'

const appStore = useAppStore()

function handleResize() {
  const width = window.innerWidth
  appStore.setDevice(width < 768 ? 'mobile' : 'desktop')
  if (appStore.isMobile) {
    appStore.toggleSidebar()
  }
}

onMounted(() => {
  handleResize()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})
</script>

<style lang="scss" scoped>
.layout-container {
  height: 100vh;
  overflow: hidden;

  &.is-collapsed {
    .sidebar {
      width: 64px !important;
    }
  }

  .sidebar {
    background-color: $sidebar-bg-color;
    border-right: 1px solid $border-color;
    transition: width 0.3s;
    overflow: hidden;
  }

  .header {
    background-color: $header-bg-color;
    border-bottom: 1px solid $border-color;
    padding: 0;
    height: 60px;
  }

  .main-content {
    background-color: $main-bg-color;
    padding: 20px;
    overflow: auto;
  }
}
</style>
