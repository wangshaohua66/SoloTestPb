<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :xs="24" :sm="12" :lg="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-info">
              <p class="stat-label">课程总数</p>
              <p class="stat-value">{{ statistics.totalCourses }}</p>
              <p class="stat-change">
                <el-icon class="up"><TrendCharts /></el-icon>
                较上周 +12%
              </p>
            </div>
            <div class="stat-icon course">
              <el-icon><Reading /></el-icon>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-info">
              <p class="stat-label">学生总数</p>
              <p class="stat-value">{{ statistics.totalStudents }}</p>
              <p class="stat-change">
                <el-icon class="up"><TrendCharts /></el-icon>
                较上周 +8%
              </p>
            </div>
            <div class="stat-icon student">
              <el-icon><User /></el-icon>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-info">
              <p class="stat-label">已发布课程</p>
              <p class="stat-value">{{ statistics.publishedCourses }}</p>
              <p class="stat-change">
                <el-icon class="up"><TrendCharts /></el-icon>
                较上周 +15%
              </p>
            </div>
            <div class="stat-icon published">
              <el-icon><CircleCheck /></el-icon>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-info">
              <p class="stat-label">本周活跃</p>
              <p class="stat-value">{{ statistics.weeklyActive }}</p>
              <p class="stat-change">
                <el-icon class="up"><TrendCharts /></el-icon>
                较上周 +5%
              </p>
            </div>
            <div class="stat-icon active">
              <el-icon><DataLine /></el-icon>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="mt-lg">
      <el-col :xs="24" :lg="16">
        <el-card title="学习趋势">
          <v-chart class="chart" :option="chartOption" autoresize />
        </el-card>
      </el-col>
      <el-col :xs="24" :lg="8">
        <el-card title="热门课程排名">
          <div v-for="(item, index) in hotCourses" :key="item.id" class="rank-item">
            <span class="rank-number" :class="`rank-${index + 1}`">{{ index + 1 }}</span>
            <span class="rank-name text-ellipsis">{{ item.name }}</span>
            <span class="rank-count">{{ item.count }}人学习</span>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="mt-lg">
      <el-col :xs="24" :lg="12">
        <el-card title="最近更新课程">
          <el-table :data="recentCourses" stripe>
            <el-table-column prop="title" label="课程名称" />
            <el-table-column prop="teacherName" label="讲师" />
            <el-table-column label="状态">
              <template #default="{ row }">
                <el-tag :type="StatusMap[row.status]?.type">
                  {{ StatusMap[row.status]?.label }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="updatedAt" label="更新时间" />
          </el-table>
        </el-card>
      </el-col>
      <el-col :xs="24" :lg="12">
        <el-card title="待审核课程">
          <el-table :data="pendingCourses" stripe>
            <el-table-column prop="title" label="课程名称" />
            <el-table-column prop="teacherName" label="讲师" />
            <el-table-column label="操作">
              <template #default="{ row }">
                <el-button type="primary" size="small" link @click="handleReview(row)">审核</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Reading, User, CircleCheck, DataLine, TrendCharts } from '@element-plus/icons-vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { LineChart } from 'echarts/charts'
import { TitleComponent, TooltipComponent, GridComponent, LegendComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { StatusMap, type Status } from '@/types'
import { getCourseList } from '@/api/course'
import { getProgressStatistics } from '@/api/progress'
import { mockCourses, generateTrendData } from '@/mock'
import type { ProgressStatistics } from '@/types'
import dayjs from 'dayjs'

use([LineChart, TitleComponent, TooltipComponent, GridComponent, LegendComponent, CanvasRenderer])

const router = useRouter()

const loading = ref(false)

const statistics = ref({
  totalCourses: 0,
  totalStudents: 0,
  publishedCourses: 0,
  weeklyActive: 0
})

const hotCourses = ref<any[]>([])
const recentCourses = ref<any[]>([])
const pendingCourses = ref<any[]>([])

const chartOption = ref({
  tooltip: {
    trigger: 'axis'
  },
  legend: {
    data: ['新增学生', '学习时长']
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    containLabel: true
  },
  xAxis: {
    type: 'category',
    boundaryGap: false,
    data: []
  },
  yAxis: {
    type: 'value'
  },
  series: [
    {
      name: '新增学生',
      type: 'line',
      smooth: true,
      data: []
    },
    {
      name: '学习时长',
      type: 'line',
      smooth: true,
      data: []
    }
  ]
})

function loadMockData() {
  statistics.value = {
    totalCourses: 128,
    totalStudents: 5680,
    publishedCourses: 96,
    weeklyActive: 1256
  }

  hotCourses.value = [
    { id: '1', name: 'Vue3 从入门到精通', count: 1568 },
    { id: '2', name: 'TypeScript 高级编程', count: 1234 },
    { id: '3', name: 'Node.js 后端开发', count: 987 },
    { id: '4', name: 'React 实战项目', count: 876 },
    { id: '5', name: '微服务架构设计', count: 654 }
  ]

  recentCourses.value = mockCourses.slice(0, 3).map(course => ({
    id: course.id,
    title: course.title,
    teacherName: course.teacherName,
    status: course.status as Status,
    updatedAt: course.updatedAt
  }))

  pendingCourses.value = mockCourses.filter(c => c.status === 'pending').map(course => ({
    id: course.id,
    title: course.title,
    teacherName: course.teacherName
  }))

  const trendData = generateTrendData()
  chartOption.value.xAxis.data = trendData.xAxis
  chartOption.value.series[0].data = trendData.students
  chartOption.value.series[1].data = trendData.duration
}

async function loadData() {
  loading.value = true
  try {
    const [coursesRes, statsRes] = await Promise.all([
      getCourseList({ page: 1, pageSize: 10 }),
      getProgressStatistics()
    ])
    
    const stats = statsRes as ProgressStatistics
    statistics.value = {
      totalCourses: stats.totalCourses || 128,
      totalStudents: stats.totalStudents || 5680,
      publishedCourses: coursesRes.total || 96,
      weeklyActive: stats.weeklyActiveStudents || 1256
    }

    if (stats.courseCompletionRank && stats.courseCompletionRank.length > 0) {
      hotCourses.value = stats.courseCompletionRank.map(c => ({
        id: c.courseId,
        name: c.courseName,
        count: c.studentCount
      }))
    } else {
      hotCourses.value = coursesRes.list.slice(0, 5).map((c: any) => ({
        id: c.id,
        name: c.title,
        count: c.studentCount
      }))
    }

    recentCourses.value = coursesRes.list.slice(0, 3).map((course: any) => ({
      id: course.id,
      title: course.title,
      teacherName: course.teacherName,
      status: course.status as Status,
      updatedAt: course.updatedAt
    }))

    pendingCourses.value = coursesRes.list.filter((c: any) => c.status === 'pending').map((course: any) => ({
      id: course.id,
      title: course.title,
      teacherName: course.teacherName
    }))

    if (stats.dailyStudyTrend && stats.dailyStudyTrend.length > 0) {
      chartOption.value.xAxis.data = stats.dailyStudyTrend.map(d => d.date)
      chartOption.value.series[0].data = stats.dailyStudyTrend.map(d => d.studyCount)
      chartOption.value.series[1].data = stats.dailyStudyTrend.map(d => Math.round(d.studyDuration / 60))
    } else {
      const trendData = generateTrendData()
      chartOption.value.xAxis.data = trendData.xAxis
      chartOption.value.series[0].data = trendData.students
      chartOption.value.series[1].data = trendData.duration
    }
  } catch (e) {
    loadMockData()
  } finally {
    loading.value = false
  }
}

function handleReview(row: any) {
  router.push(`/course/edit/${row.id}`)
}

onMounted(() => {
  loadData()
})
</script>

<style lang="scss" scoped>
.dashboard {
  .stat-card {
    border-radius: $border-radius-lg;
    box-shadow: $box-shadow-sm;

    :deep(.el-card__body) {
      padding: 20px;
    }
  }

  .stat-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .stat-info {
    .stat-label {
      font-size: 14px;
      color: $text-color-secondary;
      margin-bottom: 8px;
    }

    .stat-value {
      font-size: 28px;
      font-weight: 600;
      color: $text-color-primary;
      margin-bottom: 8px;
    }

    .stat-change {
      font-size: 12px;
      color: $text-color-secondary;
      display: flex;
      align-items: center;
      gap: 4px;

      &.up {
        color: $success-color;
      }
    }
  }

  .stat-icon {
    width: 60px;
    height: 60px;
    border-radius: 50%;
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 28px;
    color: #fff;

    &.course {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }

    &.student {
      background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    }

    &.published {
      background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    }

    &.active {
      background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
    }
  }

  .chart {
    height: 300px;
  }

  .rank-item {
    display: flex;
    align-items: center;
    padding: 12px 0;
    border-bottom: 1px solid $border-color-lighter;

    &:last-child {
      border-bottom: none;
    }

    .rank-number {
      width: 24px;
      height: 24px;
      border-radius: 50%;
      background: $border-color-lighter;
      color: $text-color-secondary;
      font-size: 12px;
      display: flex;
      justify-content: center;
      align-items: center;
      margin-right: 12px;
      font-weight: 600;

      &.rank-1 {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: #fff;
      }

      &.rank-2 {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: #fff;
      }

      &.rank-3 {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        color: #fff;
      }
    }

    .rank-name {
      flex: 1;
      font-size: 14px;
      color: $text-color-regular;
    }

    .rank-count {
      font-size: 12px;
      color: $text-color-secondary;
    }
  }
}
</style>
