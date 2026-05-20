import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAppStore = defineStore('app', () => {
  const sidebarCollapsed = ref<boolean>(false)
  const device = ref<'desktop' | 'mobile'>('desktop')
  const theme = ref<'light' | 'dark'>('light')

  const isMobile = computed(() => device.value === 'mobile')

  function toggleSidebar(): void {
    sidebarCollapsed.value = !sidebarCollapsed.value
  }

  function setDevice(newDevice: 'desktop' | 'mobile'): void {
    device.value = newDevice
  }

  function setTheme(newTheme: 'light' | 'dark'): void {
    theme.value = newTheme
  }

  return {
    sidebarCollapsed,
    device,
    theme,
    isMobile,
    toggleSidebar,
    setDevice,
    setTheme
  }
})
