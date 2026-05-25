<template>
  <div class="page-container">
    <div class="page-header">
      <h2 class="title">新建课程</h2>
      <div class="actions">
        <el-button @click="handleBack">返回</el-button>
      </div>
    </div>

    <el-steps :active="activeStep" class="course-steps">
      <el-step title="基本信息" />
      <el-step title="课程内容" />
      <el-step title="章节设置" />
    </el-steps>

    <div class="step-content">
      <div v-show="activeStep === 0" class="step-form">
        <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="课程名称" prop="title">
                <el-input v-model="form.title" placeholder="请输入课程名称" maxlength="100" show-word-limit />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="讲师" prop="teacherId">
                <el-select v-model="form.teacherId" placeholder="请选择讲师" filterable>
                  <el-option label="张老师" value="1" />
                  <el-option label="李老师" value="2" />
                  <el-option label="王老师" value="3" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="课程分类" prop="catalogId">
                <el-cascader
                  v-model="form.catalogId"
                  :options="catalogOptions"
                  :props="{ value: 'id', label: 'name', children: 'children' }"
                  placeholder="请选择分类"
                  filterable
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="难度" prop="difficulty">
                <el-radio-group v-model="form.difficulty">
                  <el-radio value="beginner">初级</el-radio>
                  <el-radio value="intermediate">中级</el-radio>
                  <el-radio value="advanced">高级</el-radio>
                </el-radio-group>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="是否免费" prop="isFree">
                <el-switch v-model="form.isFree" />
              </el-form-item>
            </el-col>
            <el-col :span="12" v-if="!form.isFree">
              <el-form-item label="价格" prop="price">
                <el-input-number v-model="form.price" :min="0" :precision="2" />
              </el-form-item>
            </el-col>
            <el-col :span="12" v-if="!form.isFree">
              <el-form-item label="原价">
                <el-input-number v-model="form.originalPrice" :min="0" :precision="2" />
              </el-form-item>
            </el-col>
            <el-col :span="24">
              <el-form-item label="课程标签">
                <el-select v-model="form.tags" multiple filterable allow-create placeholder="请输入标签">
                  <el-option label="Vue3" value="Vue3" />
                  <el-option label="TypeScript" value="TypeScript" />
                  <el-option label="前端" value="前端" />
                  <el-option label="后端" value="后端" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="24">
              <el-form-item label="课程封面" prop="coverImage">
                <el-upload
                  :action="uploadUrl"
                  :show-file-list="false"
                  :on-success="handleCoverUploadSuccess"
                  accept="image/*"
                >
                  <div class="cover-upload">
                    <img v-if="form.coverImage" :src="form.coverImage" />
                    <div v-else class="cover-placeholder">
                      <el-icon><Plus /></el-icon>
                      <p>上传封面</p>
                    </div>
                  </div>
                </el-upload>
              </el-form-item>
            </el-col>
            <el-col :span="24">
              <el-form-item label="课程描述" prop="description">
                <el-input
                  v-model="form.description"
                  type="textarea"
                  :rows="4"
                  placeholder="请输入课程描述"
                  maxlength="500"
                  show-word-limit
                />
              </el-form-item>
            </el-col>
          </el-row>
        </el-form>
      </div>

      <div v-show="activeStep === 1" class="step-form">
        <el-form ref="formRef" :model="form" label-width="100px">
          <el-form-item label="课程详情">
            <RichTextEditor v-model="courseContent" :height="400" />
          </el-form-item>
        </el-form>
      </div>

      <div v-show="activeStep === 2" class="step-form">
        <div class="chapter-list-header">
          <h3>章节列表</h3>
          <el-button type="primary" size="small" @click="handleAddChapter">
            <el-icon><Plus /></el-icon>
            添加章节
          </el-button>
        </div>
        <el-table :data="chapters" border>
          <el-table-column type="index" label="序号" width="60" />
          <el-table-column prop="title" label="章节名称" />
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
          <el-table-column label="操作" width="150">
            <template #default="{ row }">
              <el-button type="primary" size="small" link @click="handleEditChapter(row)">编辑</el-button>
              <el-button type="danger" size="small" link @click="handleDeleteChapter(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <div class="step-actions">
      <el-button v-if="activeStep > 0" @click="prevStep">上一步</el-button>
      <el-button v-if="activeStep < 2" type="primary" @click="nextStep">下一步</el-button>
      <el-button v-if="activeStep === 2" type="primary" @click="handleSubmit">保存</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { useCourseStore } from '@/store/modules/course'
import { createCourse } from '@/api/course'
import RichTextEditor from '@/components/RichTextEditor.vue'
import { required } from '@/utils/validator'
import { logAction } from '@/utils/logger'
import type { CourseForm, Chapter, CourseCatalog } from '@/types'

const router = useRouter()
const courseStore = useCourseStore()

const activeStep = ref(0)
const formRef = ref<FormInstance>()
const courseContent = ref('')
const chapters = ref<Chapter[]>([])
const catalogTree = ref<CourseCatalog[]>([])

const uploadUrl = '/api/upload/image'

const form = reactive<CourseForm>({
  title: '',
  description: '',
  coverImage: '',
  catalogId: '',
  teacherId: '',
  price: 0,
  originalPrice: 0,
  tags: [],
  difficulty: 'beginner',
  isFree: true
})

const rules: FormRules = {
  title: [required('请输入课程名称')],
  catalogId: [required('请选择课程分类')],
  teacherId: [required('请选择讲师')],
  difficulty: [required('请选择难度')],
  coverImage: [required('请上传课程封面')],
  description: [required('请输入课程描述')]
}

const catalogOptions = ref<any[]>([])

function handleCoverUploadSuccess(response: any) {
  form.coverImage = response.url
}

function formatDuration(seconds: number): string {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

function handleAddChapter() {
  chapters.value.push({
    id: `temp-${Date.now()}`,
    courseId: '',
    title: `新章节 ${chapters.value.length + 1}`,
    description: '',
    content: '',
    sort: chapters.value.length,
    isFree: false,
    quizzes: [],
    createdAt: '',
    updatedAt: ''
  })
}

function handleEditChapter(row: Chapter) {
  ElMessage.info('编辑章节功能待实现')
}

function handleDeleteChapter(row: Chapter) {
  const index = chapters.value.findIndex(c => c.id === row.id)
  if (index > -1) {
    chapters.value.splice(index, 1)
  }
}

async function nextStep() {
  if (activeStep.value === 0 && formRef.value) {
    await formRef.value.validate(async (valid) => {
      if (valid) {
        activeStep.value++
      }
    })
  } else {
    activeStep.value++
  }
}

function prevStep() {
  activeStep.value--
}

async function handleSubmit() {
  try {
    const submitData = {
      ...form,
      content: courseContent.value,
      chapters: chapters.value
    }
    const result = await createCourse(submitData)
    logAction('Course', 'create', submitData)
    ElMessage.success('课程创建成功')
    router.push(`/course/edit/${result.id}`)
  } catch (e) {
    // 错误已在 request 中处理
  }
}

function handleBack() {
  router.back()
}

async function loadCatalog() {
  try {
    catalogTree.value = await courseStore.loadCatalogTree()
    catalogOptions.value = catalogTree.value
  } catch (e) {
    // 错误已在 request 中处理
  }
}

onMounted(() => {
  loadCatalog()
})
</script>

<style lang="scss" scoped>
.course-steps {
  margin-bottom: $spacing-xl;
}

.step-content {
  min-height: 400px;
  padding: $spacing-lg 0;
}

.step-actions {
  display: flex;
  justify-content: center;
  gap: $spacing-md;
  padding-top: $spacing-lg;
  border-top: 1px solid $border-color-lighter;
}

.cover-upload {
  width: 320px;
  height: 180px;
  border: 2px dashed $border-color;
  border-radius: $border-radius-base;
  overflow: hidden;
  cursor: pointer;

  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .cover-placeholder {
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    color: $text-color-secondary;

    el-icon {
      font-size: 32px;
      margin-bottom: $spacing-sm;
    }
  }

  &:hover {
    border-color: $primary-color;
  }
}

.chapter-list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: $spacing-md;

  h3 {
    font-size: $font-size-md;
    font-weight: 600;
  }
}
</style>
