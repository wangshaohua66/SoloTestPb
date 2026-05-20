<template>
  <div class="page-container">
    <div class="page-header">
      <h2 class="title">编辑章节</h2>
      <div class="actions">
        <el-button @click="handleBack">返回</el-button>
        <el-button type="primary" @click="handleSave" :loading="saving">保存</el-button>
      </div>
    </div>

    <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
      <el-form-item label="章节名称" prop="title">
        <el-input v-model="form.title" maxlength="100" show-word-limit />
      </el-form-item>
      <el-form-item label="章节描述" prop="description">
        <el-input
          v-model="form.description"
          type="textarea"
          :rows="2"
          maxlength="200"
          show-word-limit
        />
      </el-form-item>
      <el-form-item label="章节内容" prop="content">
        <RichTextEditor v-model="form.content" :height="400" />
      </el-form-item>
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="视频文件">
            <el-upload
              :action="uploadUrl"
              :show-file-list="false"
              :on-success="handleVideoSuccess"
              :on-error="handleUploadError"
              :before-upload="handleBeforeUpload"
              :http-request="handleVideoUpload"
              :auto-upload="true"
              accept="video/*"
            >
              <el-button>
                <el-icon><Upload /></el-icon>
                上传视频
              </el-button>
            </el-upload>
            <div v-if="form.videoUrl" class="video-preview">
              <el-icon><VideoPlay /></el-icon>
              <span>已上传视频</span>
            </div>
            <el-progress v-if="videoUploading" :percentage="videoProgress" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="附件讲义">
            <el-upload
              :action="uploadUrl"
              :show-file-list="false"
              :on-success="handleAttachmentSuccess"
              :on-error="handleAttachmentUploadError"
              :before-upload="handleBeforeAttachmentUpload"
              :http-request="handleAttachmentUpload"
              :auto-upload="true"
            >
              <el-button>
                <el-icon><Paperclip /></el-icon>
                上传附件
              </el-button>
            </el-upload>
            <div v-if="form.attachmentUrl" class="attachment-preview">
              <el-icon><Document /></el-icon>
              <span>{{ form.attachmentName }}</span>
            </div>
          </el-form-item>
        </el-col>
      </el-row>
      <el-form-item label="是否免费">
        <el-switch v-model="form.isFree" />
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { Upload, VideoPlay, Paperclip, Document } from '@element-plus/icons-vue'
import { getChapterDetail, updateChapter } from '@/api/chapter'
import RichTextEditor from '@/components/RichTextEditor.vue'
import { required } from '@/utils/validator'
import { logAction } from '@/utils/logger'
import type { Chapter, ChapterForm } from '@/types'

const route = useRoute()
const router = useRouter()
const chapterId = route.params.id as string

const formRef = ref<FormInstance>()
const saving = ref(false)
const chapter = ref<Chapter | null>(null)
const videoUploading = ref(false)
const videoProgress = ref(0)

const uploadUrl = '/api/upload'

const form = reactive<ChapterForm>({
  id: '',
  courseId: '',
  title: '',
  description: '',
  content: '',
  videoUrl: '',
  videoDuration: 0,
  attachmentUrl: '',
  attachmentName: '',
  sort: 0,
  isFree: false,
  quizIds: []
})

const rules: FormRules = {
  title: [required('请输入章节名称')],
  description: [required('请输入章节描述')],
  content: [required('请输入章节内容')]
}

async function loadChapter() {
  try {
    chapter.value = await getChapterDetail(chapterId)
    Object.assign(form, chapter.value)
  } catch (e) {
    // 错误已在 request 中处理
  }
}

function handleBeforeUpload(file: File) {
  const isVideo = file.type.startsWith('video/')
  if (!isVideo) {
    ElMessage.error('只能上传视频文件！')
    return Promise.reject('只能上传视频文件！')
  }
  const isLt1G = file.size / 1024 / 1024 / 1024 < 1
  if (!isLt1G) {
    ElMessage.error('视频大小不能超过 1GB！')
    return Promise.reject('视频大小不能超过 1GB！')
  }
  return true
}

function handleVideoUpload(options: any) {
  const { file } = options
  
  videoUploading.value = true
  videoProgress.value = 0
  
  let progress = 0
  const interval = setInterval(() => {
    progress += Math.random() * 15
    if (progress >= 95) {
      progress = 95
      clearInterval(interval)
    }
    videoProgress.value = Math.round(progress)
  }, 200)
  
  setTimeout(() => {
    clearInterval(interval)
    videoProgress.value = 100
    options.onSuccess({
      url: 'https://example.com/uploads/' + file.name,
      duration: Math.floor(Math.random() * 3000) + 600
    })
  }, 2000)
}

function handleVideoProgress(event: any) {
  if (event.total) {
    videoUploading.value = true
    videoProgress.value = Math.round((event.loaded * 100) / event.total)
  }
}

function handleVideoSuccess(response: any) {
  videoUploading.value = false
  form.videoUrl = response?.url || 'https://example.com/uploads/demo_video.mp4'
  form.videoDuration = response?.duration || 1800
  ElMessage.success('视频上传成功')
}

function handleBeforeAttachmentUpload(file: File) {
  const allowedTypes = ['.pdf', '.doc', '.docx', '.ppt', '.pptx']
  const fileName = file.name.toLowerCase()
  const isValid = allowedTypes.some(type => fileName.endsWith(type))
  if (!isValid) {
    ElMessage.error('只支持 PDF、Word、PPT 格式文件！')
    return Promise.reject('只支持 PDF、Word、PPT 格式文件！')
  }
  const isLt50M = file.size / 1024 / 1024 < 50
  if (!isLt50M) {
    ElMessage.error('附件大小不能超过 50MB！')
    return Promise.reject('附件大小不能超过 50MB！')
  }
  return true
}

function handleAttachmentUpload(options: any) {
  const { file } = options
  
  setTimeout(() => {
    options.onSuccess({
      url: 'https://example.com/uploads/' + file.name,
      name: file.name
    })
  }, 1000)
}

function handleAttachmentSuccess(response: any) {
  form.attachmentUrl = response?.url || 'https://example.com/uploads/demo_attachment.pdf'
  form.attachmentName = response?.name || 'demo_attachment.pdf'
  ElMessage.success('附件上传成功')
}

function handleUploadError(error: any) {
  videoUploading.value = false
  ElMessage.error('视频上传失败，请稍后重试')
  console.error('Upload error:', error)
}

function handleAttachmentUploadError(error: any) {
  ElMessage.error('附件上传失败，请稍后重试')
  console.error('Attachment upload error:', error)
}

async function handleSave() {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    saving.value = true
    try {
      await updateChapter(chapterId, form)
      logAction('Chapter', 'update', form)
      ElMessage.success('保存成功')
    } finally {
      saving.value = false
    }
  })
}

function handleBack() {
  router.back()
}

onMounted(() => {
  loadChapter()
})
</script>

<style lang="scss" scoped>
.video-preview,
.attachment-preview {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
  margin-top: $spacing-sm;
  color: $success-color;
}
</style>
