<template>
  <div class="page-container">
    <div class="page-header">
      <h2 class="title">课程目录管理</h2>
      <div class="actions">
      </div>
    </div>
    <TreeCatalog :data="catalogTree" @refresh="loadData" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useCourseStore } from '@/store/modules/course'
import TreeCatalog from '@/components/TreeCatalog.vue'
import type { CourseCatalog } from '@/types'

const courseStore = useCourseStore()
const catalogTree = ref<CourseCatalog[]>([])

async function loadData() {
  try {
    catalogTree.value = await courseStore.loadCatalogTree()
  } catch (e) {
    // 错误已在 request 中处理
  }
}

onMounted(() => {
  loadData()
})
</script>
