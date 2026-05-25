<template>
  <div class="page-container">
    <div class="page-header">
      <h2 class="title">学习进度追踪</h2>
    </div>

    <el-form :inline="true" :model="queryForm" class="search-form">
      <el-form-item label="课程">
        <el-select v-model="queryForm.courseId" placeholder="请选择课程" filterable clearable style="width: 200px">
          <el-option v-for="course in courseOptions" :key="course.id" :label="course.title" :value="course.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="学生">
        <el-input v-model="queryForm.keyword" placeholder="请输入学生姓名" clearable />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="handleSearch">
          <el-icon><Search /></el-icon>
          搜索
        </el-button>
      </el-form-item>
    </el-form>

    <el-table :data="progressList" v-loading="loading" stripe>
      <el-table-column label="学生信息" width="200">
        <template #default="{ row }">
          <div class="student-info">
            <el-avatar :size="40" :src="row.avatar">
              {{ row.studentName?.charAt(0) }}
            </el-avatar>
            <div class="student-detail">
              <p class="name">{{ row.studentName }}</p>
              <p class="time">最近学习: {{ formatDate(row.lastStudyTime) }}</p>
            </div>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="courseName" label="课程名称" width="200" />
      <el-table-column label="学习进度" width="250">
        <template #default="{ row }">
          <div class="progress-wrapper">
            <el-progress
              :percentage="row.progress"
              :color="getProgressColor(row.progress)"
              :stroke-width="12"
            />
            <span class="progress-text">{{ row.progress }}%</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="章节完成" width="150">
        <template #default="{ row }">
          {{ row.completedChapters }} / {{ row.totalChapters }}
        </template>
      </el-table-column>
      <el-table-column label="学习时长" width="150">
        <template #default="{ row }">
          {{ formatDuration(row.watchedDuration) }}
        </template>
      </el-table-column>
      <el-table-column label="测验得分" width="150">
        <template #default="{ row }">
          {{ row.quizScore }} / {{ row.quizTotalScore }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="100">
        <template #default="{ row }">
          <el-button type="primary" size="small" link @click="handleViewDetail(row)">详情</el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination-container">
      <el-pagination
        v-model:current-page="queryForm.page"
        v-model:page-size="queryForm.pageSize"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        :page-sizes="[10, 20, 50, 100]"
        @current-change="handlePageChange"
        @size-change="handleSizeChange"
      />
    </div>

    <el-dialog v-model="detailVisible" title="学习详情" width="800px">
      <div v-if="currentProgress" class="detail-content">
        <div class="detail-header">
          <el-avatar :size="60" :src="currentProgress.avatar">
            {{ currentProgress.studentName?.charAt(0) }}
          </el-avatar>
          <div>
            <h3>{{ currentProgress.studentName }}</h3>
            <p>{{ currentProgress.courseName }}</p>
          </div>
        </div>
        <el-divider />
        <h4>章节学习情况</h4>
        <el-table :data="chapterProgress" border>
          <el-table-column prop="chapterTitle" label="章节名称" />
          <el-table-column label="观看进度" width="200">
            <template #default="{ row }">
              <el-progress
                :percentage="row.watchedPercentage"
                :color="getProgressColor(row.watchedPercentage)"
              />
            </template>
          </el-table-column>
          <el-table-column label="是否完成" width="100">
            <template #default="{ row }">
              <el-tag v-if="row.isCompleted" type="success">已完成</el-tag>
              <el-tag v-else type="info">进行中</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="测验得分" width="120">
            <template #default="{ row }">
              {{ row.quizScore ?? '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="lastWatchTime" label="最近观看" width="180">
            <template #default="{ row }">
              {{ formatDate(row.lastWatchTime) }}
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { getStudentProgress, getChapterProgress } from '@/api/progress'
import { getCourseList } from '@/api/course'
import { mockCourses, mockStudentProgress } from '@/mock'
import type { StudentProgress, ChapterProgress, Course } from '@/types'
import dayjs from 'dayjs'

const loading = ref(false)
const progressList = ref<StudentProgress[]>([])
const chapterProgress = ref<ChapterProgress[]>([])
const total = ref(0)
const detailVisible = ref(false)
const currentProgress = ref<StudentProgress | null>(null)
const courseOptions = ref<Course[]>([])

const queryForm = reactive({
  page: 1,
  pageSize: 10,
  courseId: '',
  keyword: ''
})

function formatDate(date: string): string {
  return dayjs(date).format('YYYY-MM-DD HH:mm')
}

function formatDuration(seconds: number): string {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  return `${hours}小时${minutes}分钟`
}

function getProgressColor(percentage: number): string {
  if (percentage >= 80) return '#67c23a'
  if (percentage >= 50) return '#e6a23c'
  return '#f56c6c'
}

async function loadData() {
  loading.value = true
  try {
    const result = await getStudentProgress(queryForm)
    progressList.value = result.list
    total.value = result.total
  } catch (e) {
    progressList.value = mockStudentProgress
    total.value = mockStudentProgress.length
  } finally {
    loading.value = false
  }
}

async function loadCourses() {
  try {
    const result = await getCourseList({ page: 1, pageSize: 100 })
    courseOptions.value = result.list
  } catch (e) {
    courseOptions.value = mockCourses
  }
}

function handleSearch() {
  queryForm.page = 1
  loadData()
}

function handlePageChange() {
  loadData()
}

function handleSizeChange() {
  queryForm.page = 1
  loadData()
}

async function handleViewDetail(row: StudentProgress) {
  currentProgress.value = row
  detailVisible.value = true
  chapterProgress.value = await getChapterProgress(row.studentId, row.courseId)
}

onMounted(() => {
  loadCourses()
  loadData()
})
</script>

<style lang="scss" scoped>
.student-info {
  display: flex;
  align-items: center;
  gap: $spacing-sm;

  .student-detail {
    .name {
      font-weight: 500;
    }

    .time {
      font-size: 12px;
      color: $text-color-secondary;
    }
  }
}

.progress-wrapper {
  display: flex;
  align-items: center;
  gap: $spacing-sm;

  .progress-text {
    font-size: 12px;
    color: $text-color-secondary;
    min-width: 40px;
  }
}

.detail-header {
  display: flex;
  align-items: center;
  gap: $spacing-md;

  h3 {
    font-size: $font-size-lg;
    margin-bottom: $spacing-xs;
  }

  p {
    color: $text-color-secondary;
  }
}

.pagination-container {
  margin-top: $spacing-md;
  display: flex;
  justify-content: flex-end;
}
</style>
