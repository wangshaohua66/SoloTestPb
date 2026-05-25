<template>
  <el-menu
    :default-active="activeMenu"
    :collapse="collapsed"
    :collapse-transition="false"
    background-color="#ffffff"
    text-color="#303133"
    active-text-color="#409eff"
    class="sidebar-menu"
  >
    <template v-for="route in menuRoutes" :key="route.path">
      <template v-if="!route.meta?.hidden">
        <el-sub-menu v-if="route.children && route.children.length > 1" :index="route.path">
          <template #title>
            <el-icon><component :is="route.meta?.icon" /></el-icon>
            <span>{{ route.meta?.title }}</span>
          </template>
          <el-menu-item
            v-for="child in route.children"
            :key="child.path"
            :index="resolvePath(route.path, child.path)"
            v-if="!child.meta?.hidden"
          >
            <el-icon v-if="child.meta?.icon"><component :is="child.meta.icon" /></el-icon>
            <span>{{ child.meta?.title }}</span>
          </el-menu-item>
        </el-sub-menu>
        <el-menu-item v-else :index="route.children?.[0]?.path || route.path">
          <el-icon><component :is="route.meta?.icon" /></el-icon>
          <template #title>{{ route.meta?.title }}</template>
        </el-menu-item>
      </template>
    </template>
  </el-menu>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { asyncRoutes } from '@/router'

defineProps<{
  collapsed: boolean
}>()

const route = useRoute()
const router = useRouter()

const menuRoutes = computed(() => asyncRoutes)

const activeMenu = computed(() => route.path)

function resolvePath(parent: string, child: string): string {
  return `${parent}/${child}`.replace(/\/+/g, '/')
}
</script>

<style lang="scss" scoped>
.sidebar-menu {
  border-right: none;
  height: calc(100vh - 60px);
}
</style>
