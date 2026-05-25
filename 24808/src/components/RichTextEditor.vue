<template>
  <div class="rich-text-editor">
    <div ref="editorRef" :id="editorId"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import E from 'wangeditor'

const props = defineProps<{
  modelValue: string
  placeholder?: string
  height?: number
  disabled?: boolean
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
  (e: 'change', value: string): void
}>()

const editorId = `editor-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
const editorRef = ref<HTMLElement>()
let editor: E | null = null

function initEditor() {
  if (!editorRef.value) return

  editor = new E(`#${editorId}`)
  
  editor.config.placeholder = props.placeholder || '请输入内容...'
  editor.config.height = props.height || 500
  editor.config.uploadImgServer = '/api/upload/image'
  editor.config.uploadImgParams = {
    type: 'editor'
  }
  editor.config.uploadImgMaxLength = 5
  editor.config.uploadImgMaxSize = 5 * 1024 * 1024

  editor.config.onchange = (html: string) => {
    emit('update:modelValue', html)
    emit('change', html)
  }

  editor.create()

  if (props.modelValue) {
    editor.txt.html(props.modelValue)
  }

  if (props.disabled) {
    editor.disable()
  }
}

watch(() => props.modelValue, (newVal) => {
  if (editor && editor.txt.html() !== newVal) {
    editor.txt.html(newVal || '')
  }
})

watch(() => props.disabled, (newVal) => {
  if (editor) {
    if (newVal) {
      editor.disable()
    } else {
      editor.enable()
    }
  }
})

onMounted(() => {
  initEditor()
})

onBeforeUnmount(() => {
  if (editor) {
    editor.destroy()
    editor = null
  }
})

defineExpose({
  getHtml: () => editor?.txt.html(),
  getText: () => editor?.txt.text(),
  setHtml: (html: string) => editor?.txt.html(html),
  clear: () => editor?.txt.clear()
})
</script>

<style lang="scss" scoped>
.rich-text-editor {
  :deep(.w-e-text-container) {
    min-height: 300px;
  }
}
</style>
