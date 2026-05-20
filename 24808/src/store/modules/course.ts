import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Course, CourseCatalog } from '@/types'
import { getCatalogTree } from '@/api/course'

export const useCourseStore = defineStore('course', () => {
  const catalogTree = ref<CourseCatalog[]>([])
  const currentCourse = ref<Course | null>(null)

  async function loadCatalogTree(): Promise<CourseCatalog[]> {
    const tree = await getCatalogTree()
    catalogTree.value = tree
    return tree
  }

  function setCurrentCourse(course: Course | null): void {
    currentCourse.value = course
  }

  function findCatalogById(id: string, tree: CourseCatalog[] = catalogTree.value): CourseCatalog | null {
    for (const item of tree) {
      if (item.id === id) return item
      if (item.children) {
        const found = findCatalogById(id, item.children)
        if (found) return found
      }
    }
    return null
  }

  return {
    catalogTree,
    currentCourse,
    loadCatalogTree,
    setCurrentCourse,
    findCatalogById
  }
})
