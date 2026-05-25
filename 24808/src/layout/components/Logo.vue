<template>
  <div class="logo">
    <img src="/vite.svg" alt="logo" class="logo-img" />
    <h1 v-if="!collapsed" class="logo-title">在线教育平台</h1>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  collapsed: boolean
}>()
</script>

<style lang="scss" scoped>
.logo {
  display: flex;
  align-items: center;
  padding: 0 16px;
  height: 60px;
  border-bottom: 1px solid $border-color;

  .logo-img {
    width: 32px;
    height: 32px;
  }

  .logo-title {
    margin-left: 12px;
    font-size: 18px;
    font-weight: 600;
    color: $primary-color;
    white-space: nowrap;
    overflow: hidden;
  }
}
</style>
