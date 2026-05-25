<template>
  <div class="chapter-list">
    <div class="chapter-header">
      <h3>课程章节</h3>
      <el-button type="primary" size="small" @click="handleAddChapter">
        <el-icon><Plus /></el-icon>
        添加章节
      </el-button>
    </div>
    
    <el-table :data="chapters" v-loading="loading" border>
      <el-table-column type="index" label="序号" width="60" />
      <el-table-column prop="title" label="章节名称" />
      <el-table-column prop="description" label="描述" show-overflow-tooltip />
      <el-table-column prop="videoDuration" label="视频时长" width="120">
        <template #default="{ row }">
          {{ row.videoDuration ? formatDuration(row.videoDuration) : '-' }}
        </template>
      </el-table-column>
      <el-table-column label="免费" width="80">
        <template #default="{ row }">
          <el-tag v-if="row.isFree" type="success">免费</el-tag>
          <el-tag v-else type="info">付费</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="测验" width="80">
        <template #default="{ row }">
          {{ row.quizzes?.length || 0 }}
        </template>
      </el-table-column>
      <el-table-column prop="updatedAt" label="更新时间" width="180" />
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" size="small" link @click="handleEdit(row)">编辑</el-button>
          <el-button type="danger" size="small" link @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="800px" @closed="resetForm">
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
          <RichTextEditor v-model="form.content" :height="300" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="视频文件">
              <el-upload
                :action="uploadUrl"
                :show-file-list="false"
                :on-progress="handleVideoProgress"
                :on-success="handleVideoSuccess"
                accept="video/*"
              >
                <el-button>
                  <el-icon><Upload /></el-icon>
                  上传视频
                </el-button>
              </el-upload>
              <div v-if="form.videoUrl" class="video-preview">
                <el-icon><VideoPlay /></el-icon>
                <span>已上传</span>
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
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { Plus, Upload, VideoPlay, Paperclip, Document } from '@element-plus/icons-vue'
import { getChapterList, createChapter, updateChapter, deleteChapter } from '@/api/chapter'
import RichTextEditor from '@/components/RichTextEditor.vue'
import { required } from '@/utils/validator'
import { logAction } from '@/utils/logger'
import type { Chapter, ChapterForm } from '@/types'

const route = useRoute()
const courseId = computed(() => route.params.courseId as string)

const loading = ref(false)
const chapters = ref<Chapter[]>([])
const dialogVisible = ref(false)
const submitting = ref(false)
const formRef = ref<FormInstance>()
const isEdit = ref(false)
const currentChapter = ref<Chapter | null>(null)

const videoUploading = ref(false)
const videoProgress = ref(0)

const uploadUrl = '/api/upload/video'

const form = reactive<ChapterForm>({
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

const dialogTitle = computed(() => isEdit.value ? '编辑章节' : '添加章节')

function formatDuration(seconds: number): string {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

async function loadData() {
  loading.value = true
  try {
    chapters.value = await getChapterList(courseId.value)
  } finally {
    loading.value = false
  }
}

function handleAddChapter() {
  isEdit.value = false
  currentChapter.value = null
  form.courseId = courseId.value
  form.title = ''
  form.description = ''
  form.content = ''
  form.videoUrl = ''
  form.attachmentUrl = ''
  form.sort = chapters.value.length
  dialogVisible.value = true
}

function handleEdit(row: Chapter) {
  isEdit.value = true
  currentChapter.value = row
  form.id = row.id
  form.courseId = row.courseId
  form.title = row.title
  form.description = row.description
  form.content = row.content
  form.videoUrl = row.videoUrl || ''
  form.videoDuration = row.videoDuration || 0
  form.attachmentUrl = row.attachmentUrl || ''
  form.attachmentName = row.attachmentName || ''
  form.sort = row.sort
  form.isFree = row.isFree
  form.quizIds = row.quizzes?.map(q => q.id) || []
  dialogVisible.value = true
}

async function handleDelete(row: Chapter) {
  try {
    await ElMessageBox.confirm(`确定要删除章节「${row.title}」吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await deleteChapter(row.id)
    logAction('Chapter', 'delete', { id: row.id, title: row.title })
    ElMessage.success('删除成功')
    loadData()
  } catch (e) {
    // 用户取消
  }
}

function handleVideoProgress(event: any) {
  if (event.total) {
    videoUploading.value = true
    videoProgress.value = Math.round((event.loaded * 100) / event.total)
  }
}

function handleVideoSuccess(response: any) {
  videoUploading.value = false
  form.videoUrl = response.url
  form.videoDuration = response.duration
  ElMessage.success('视频上传成功')
}

function handleAttachmentSuccess(response: any) {
  form.attachmentUrl = response.url
  form.attachmentName = response.name
  ElMessage.success('附件上传成功')
}

async function handleSubmit() {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    submitting.value = true
    try {
      if (isEdit.value && currentChapter.value) {
        await updateChapter(currentChapter.value.id, form)
        logAction('Chapter', 'update', form)
        ElMessage.success('更新成功')
      } else {
        await createChapter(form)
        logAction('Chapter', 'create', form)
        ElMessage.success('创建成功')
      }
      
      dialogVisible.value = false
      loadData()
    } finally {
      submitting.value = false
    }
  })
}

function resetForm() {
  formRef.value?.resetFields()
  isEdit.value = false
  currentChapter.value = null
  videoProgress.value = 0
}

onMounted(() => {
  loadData()
})
</script>

<style lang="scss" scoped>
.chapter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: $spacing-md;

  h3 {
    font-size: $font-size-md;
    font-weight: 600;
  }
}

.video-preview,
.attachment-preview {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
  margin-top: $spacing-sm;
  color: $success-color;
}
</style>
