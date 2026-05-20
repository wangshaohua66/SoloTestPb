<template>
  <div class="page-container">
    <div class="page-header">
      <h2 class="title">编辑课程 - {{ course?.title }}</h2>
      <div class="actions">
        <el-tag :type="course ? StatusMap[course.status]?.type : 'info'">
          {{ course ? StatusMap[course.status]?.label : '' }}
        </el-tag>
        <el-button @click="handleBack">返回</el-button>
        <el-button type="primary" @click="handleSave" :loading="saving">保存</el-button>
      </div>
    </div>

    <el-tabs v-model="activeTab" type="border-card">
      <el-tab-pane label="基本信息" name="basic">
        <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="课程名称" prop="title">
                <el-input v-model="form.title" maxlength="100" show-word-limit />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="讲师" prop="teacherId">
                <el-select v-model="form.teacherId" filterable>
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
          </el-row>
        </el-form>
      </el-tab-pane>

      <el-tab-pane label="课程内容" name="content">
        <RichTextEditor v-model="form.content" :height="500" />
      </el-tab-pane>

      <el-tab-pane label="章节管理" name="chapters">
        <div class="tab-content">
          <div class="tab-header">
            <h3>章节列表</h3>
            <el-button type="primary" size="small" @click="handleAddChapter">
              <el-icon><Plus /></el-icon>
              添加章节
            </el-button>
          </div>
          <el-table :data="chapters" border v-loading="chaptersLoading">
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
          <el-empty v-if="chapters.length === 0 && !chaptersLoading" description="暂无章节，点击上方按钮添加" />
        </div>
      </el-tab-pane>

      <el-tab-pane label="测验管理" name="quizzes">
        <div class="tab-content">
          <div class="tab-header">
            <h3>测验列表</h3>
            <el-button type="primary" size="small" @click="handleAddQuiz">
              <el-icon><Plus /></el-icon>
              添加测验
            </el-button>
          </div>
          <el-table :data="quizzes" border v-loading="quizzesLoading">
            <el-table-column type="index" label="序号" width="60" />
            <el-table-column prop="title" label="题目标题" />
            <el-table-column label="题型" width="100">
              <template #default="{ row }">
                <el-tag>{{ getQuizTypeLabel(row.type) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="score" label="分值" width="80" />
            <el-table-column label="难度" width="100">
              <template #default="{ row }">
                <el-tag :type="getDifficultyTagType(row.difficulty)">{{ getDifficultyLabel(row.difficulty) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150">
              <template #default="{ row }">
                <el-button type="primary" size="small" link @click="handleEditQuiz(row)">编辑</el-button>
                <el-button type="danger" size="small" link @click="handleDeleteQuiz(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-if="quizzes.length === 0 && !quizzesLoading" description="暂无测验，点击上方按钮添加" />
        </div>
      </el-tab-pane>

      <el-tab-pane label="学习数据" name="progress">
        <div class="placeholder">
          <el-icon><DataLine /></el-icon>
          <p>学习数据统计</p>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { Tickets, DataLine, Plus } from '@element-plus/icons-vue'
import { useCourseStore } from '@/store/modules/course'
import { getCourseDetail, updateCourse } from '@/api/course'
import { getChapterList, deleteChapter } from '@/api/chapter'
import { getQuizList, deleteQuiz } from '@/api/quiz'
import RichTextEditor from '@/components/RichTextEditor.vue'
import { required } from '@/utils/validator'
import { logAction } from '@/utils/logger'
import { StatusMap, type Course, type CourseForm, type CourseCatalog, type Chapter, type Quiz } from '@/types'

const route = useRoute()
const router = useRouter()
const courseStore = useCourseStore()

const courseId = route.params.id as string
const course = ref<Course | null>(null)
const activeTab = ref('basic')
const saving = ref(false)
const formRef = ref<FormInstance>()
const catalogTree = ref<CourseCatalog[]>([])
const chapters = ref<Chapter[]>([])
const quizzes = ref<Quiz[]>([])
const chaptersLoading = ref(false)
const quizzesLoading = ref(false)

const form = reactive<CourseForm & { content: string }>({
  id: '',
  title: '',
  description: '',
  content: '',
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
  teacherId: [required('请选择讲师')]
}

const catalogOptions = ref<any[]>([])

async function loadCourse() {
  try {
    course.value = await getCourseDetail(courseId)
    Object.assign(form, course.value)
  } catch (e) {
    // 错误已在 request 中处理
  }
}

async function loadChapters() {
  chaptersLoading.value = true
  try {
    const result = await getChapterList(courseId, { page: 1, pageSize: 100 })
    chapters.value = result.list
  } catch (e) {
    // 错误已在 request 中处理
  } finally {
    chaptersLoading.value = false
  }
}

async function loadQuizzes() {
  quizzesLoading.value = true
  try {
    const result = await getQuizList({ page: 1, pageSize: 100 })
    quizzes.value = result.list
  } catch (e) {
    // 错误已在 request 中处理
  } finally {
    quizzesLoading.value = false
  }
}

function formatDuration(seconds: number): string {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

function getQuizTypeLabel(type: string): string {
  const map: Record<string, string> = {
    single: '单选题',
    multiple: '多选题',
    judge: '判断题',
    fill: '填空题'
  }
  return map[type] || type
}

function getDifficultyLabel(difficulty: string): string {
  const map: Record<string, string> = {
    easy: '简单',
    medium: '中等',
    hard: '困难'
  }
  return map[difficulty] || difficulty
}

function getDifficultyTagType(difficulty: string): 'success' | 'warning' | 'danger' {
  const map: Record<string, 'success' | 'warning' | 'danger'> = {
    easy: 'success',
    medium: 'warning',
    hard: 'danger'
  }
  return map[difficulty] || 'info' as any
}

function handleAddChapter() {
  router.push(`/chapter/edit/new?courseId=${courseId}`)
}

function handleEditChapter(row: Chapter) {
  router.push(`/chapter/edit/${row.id}`)
}

async function handleDeleteChapter(row: Chapter) {
  try {
    await ElMessageBox.confirm(`确定要删除章节「${row.title}」吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await deleteChapter(row.id)
    logAction('Chapter', 'delete', { id: row.id, title: row.title })
    ElMessage.success('删除成功')
    loadChapters()
  } catch (e) {
    // 用户取消
  }
}

function handleAddQuiz() {
  router.push('/quiz/create')
}

function handleEditQuiz(row: Quiz) {
  router.push({ path: '/quiz/create', query: { id: row.id } })
}

async function handleDeleteQuiz(row: Quiz) {
  try {
    await ElMessageBox.confirm(`确定要删除该题目吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await deleteQuiz(row.id)
    logAction('Quiz', 'delete', { id: row.id })
    ElMessage.success('删除成功')
    loadQuizzes()
  } catch (e) {
    // 用户取消
  }
}

async function loadCatalog() {
  try {
    catalogTree.value = await courseStore.loadCatalogTree()
    catalogOptions.value = catalogTree.value
  } catch (e) {
    // 错误已在 request 中处理
  }
}

async function handleSave() {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    saving.value = true
    try {
      await updateCourse(courseId, form)
      logAction('Course', 'update', form)
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
  loadCatalog()
  loadCourse()
  loadChapters()
  loadQuizzes()
})
</script>

<style lang="scss" scoped>
.placeholder {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 80px;
  color: $text-color-secondary;

  el-icon {
    font-size: 64px;
    margin-bottom: $spacing-md;
  }

  p {
    font-size: 16px;
  }
}

.tab-content {
  padding: $spacing-md;

  .tab-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: $spacing-md;

    h3 {
      font-size: $font-size-md;
      font-weight: 600;
      margin: 0;
    }
  }
}
</style>
