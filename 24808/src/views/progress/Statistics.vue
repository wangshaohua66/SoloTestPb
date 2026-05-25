<template>
  <div class="page-container">
    <div class="page-header">
      <h2 class="title">数据统计</h2>
    </div>

    <el-row :gutter="20">
      <el-col :xs="24" :sm="12" :lg="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-info">
              <p class="stat-label">学生总数</p>
              <p class="stat-value">{{ statistics?.totalStudents || 0 }}</p>
            </div>
            <div class="stat-icon blue">
              <el-icon><User /></el-icon>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-info">
              <p class="stat-label">课程总数</p>
              <p class="stat-value">{{ statistics?.totalCourses || 0 }}</p>
            </div>
            <div class="stat-icon green">
              <el-icon><Reading /></el-icon>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-info">
              <p class="stat-label">平均进度</p>
              <p class="stat-value">{{ statistics?.averageProgress || 0 }}%</p>
            </div>
            <div class="stat-icon purple">
              <el-icon><TrendCharts /></el-icon>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-info">
              <p class="stat-label">完成率</p>
              <p class="stat-value">{{ statistics?.completionRate || 0 }}%</p>
            </div>
            <div class="stat-icon orange">
              <el-icon><CircleCheck /></el-icon>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="mt-lg">
      <el-col :xs="24" :lg="16">
        <el-card title="每日学习趋势">
          <v-chart class="chart" :option="trendChartOption" autoresize />
        </el-card>
      </el-col>
      <el-col :xs="24" :lg="8">
        <el-card title="课程完成率排行">
          <v-chart class="chart" :option="rankChartOption" autoresize />
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="mt-lg">
      <el-col :xs="24" :lg="12">
        <el-card title="学习时长分布">
          <v-chart class="chart" :option="durationChartOption" autoresize />
        </el-card>
      </el-col>
      <el-col :xs="24" :lg="12">
        <el-card title="课程难度分布">
          <v-chart class="chart" :option="difficultyChartOption" autoresize />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { LineChart, BarChart, PieChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  GridComponent,
  LegendComponent,
  DatasetComponent
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { User, Reading, TrendCharts, CircleCheck } from '@element-plus/icons-vue'
import { getProgressStatistics } from '@/api/progress'
import type { ProgressStatistics } from '@/types'
import { mockProgressStatistics, generateMonthTrendData } from '@/mock'
import dayjs from 'dayjs'

use([LineChart, BarChart, PieChart, TitleComponent, TooltipComponent, GridComponent, LegendComponent, DatasetComponent, CanvasRenderer])

const loading = ref(false)
const statistics = ref<ProgressStatistics | null>(null)

function generateChartData(stats: ProgressStatistics) {
  if (stats.dailyStudyTrend && stats.dailyStudyTrend.length > 0) {
    trendChartOption.value = {
      ...trendChartOption.value,
      xAxis: { ...trendChartOption.value.xAxis, data: stats.dailyStudyTrend.map(d => d.date) },
      series: [
        { ...trendChartOption.value.series[0], data: stats.dailyStudyTrend.map(d => d.studyCount) },
        { ...trendChartOption.value.series[1], data: stats.dailyStudyTrend.map(d => Math.round(d.studyDuration / 60)) }
      ]
    }
  } else {
    const trendData = generateMonthTrendData()
    trendChartOption.value = {
      ...trendChartOption.value,
      xAxis: { ...trendChartOption.value.xAxis, data: trendData.xAxis },
      series: [
        { ...trendChartOption.value.series[0], data: trendData.students },
        { ...trendChartOption.value.series[1], data: trendData.duration }
      ]
    }
  }

  if (stats.courseCompletionRank && stats.courseCompletionRank.length > 0) {
    rankChartOption.value = {
      ...rankChartOption.value,
      yAxis: { ...rankChartOption.value.yAxis, data: stats.courseCompletionRank.map(c => c.courseName) },
      series: [
        { ...rankChartOption.value.series[0], data: stats.courseCompletionRank.map(c => c.completionRate) }
      ]
    }
  } else {
    const courses = ['Vue3入门', 'TS高级', 'Node实战', 'React进阶', '微服务']
    rankChartOption.value = {
      ...rankChartOption.value,
      yAxis: { ...rankChartOption.value.yAxis, data: courses },
      series: [
        { ...rankChartOption.value.series[0], data: [95, 88, 76, 82, 65] }
      ]
    }
  }

  if (stats.studyDurationDistribution && stats.studyDurationDistribution.length > 0) {
    durationChartOption.value = {
      ...durationChartOption.value,
      series: [
        {
          ...durationChartOption.value.series[0],
          data: stats.studyDurationDistribution.map(d => ({
            value: d.value,
            name: d.name,
            itemStyle: d.color ? { color: d.color } : undefined
          }))
        }
      ]
    }
  } else {
    durationChartOption.value = {
      ...durationChartOption.value,
      series: [
        {
          ...durationChartOption.value.series[0],
          data: [
            { value: 1048, name: '<30分钟', itemStyle: { color: '#667eea' } },
            { value: 735, name: '30-60分钟', itemStyle: { color: '#764ba2' } },
            { value: 580, name: '1-2小时', itemStyle: { color: '#f093fb' } },
            { value: 484, name: '2-3小时', itemStyle: { color: '#f5576c' } },
            { value: 300, name: '>3小时', itemStyle: { color: '#4facfe' } }
          ]
        }
      ]
    }
  }

  if (stats.difficultyDistribution && stats.difficultyDistribution.length > 0) {
    difficultyChartOption.value = {
      ...difficultyChartOption.value,
      series: [
        {
          ...difficultyChartOption.value.series[0],
          data: stats.difficultyDistribution.map(d => ({
            value: d.value,
            name: d.name,
            itemStyle: d.color ? { color: d.color } : undefined
          }))
        }
      ]
    }
  } else {
    difficultyChartOption.value = {
      ...difficultyChartOption.value,
      series: [
        {
          ...difficultyChartOption.value.series[0],
          data: [
            { value: 1568, name: '初级', itemStyle: { color: '#67c23a' } },
            { value: 1024, name: '中级', itemStyle: { color: '#e6a23c' } },
            { value: 656, name: '高级', itemStyle: { color: '#f56c6c' } }
          ]
        }
      ]
    }
  }
}

const trendChartOption = ref<any>({
  tooltip: {
    trigger: 'axis'
  },
  legend: {
    data: ['学习人数', '学习时长(小时)']
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
      name: '学习人数',
      type: 'line',
      smooth: true,
      data: []
    },
    {
      name: '学习时长(小时)',
      type: 'line',
      smooth: true,
      data: []
    }
  ]
})

const rankChartOption = ref<any>({
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      type: 'shadow'
    }
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    containLabel: true
  },
  xAxis: {
    type: 'value',
    max: 100
  },
  yAxis: {
    type: 'category',
    data: []
  },
  series: [
    {
      type: 'bar',
      data: [],
      itemStyle: {
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 1,
          y2: 0,
          colorStops: [
            { offset: 0, color: '#667eea' },
            { offset:  1, color: '#764ba2' }
          ]
        }
      }
    }
  ]
})

const durationChartOption = ref<any>({
  tooltip: {
    trigger: 'item'
  },
  legend: {
    orient: 'vertical',
    left: 'left'
  },
  series: [
    {
      type: 'pie',
      radius: ['40%', '70%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 10,
        borderColor: '#fff',
        borderWidth: 2
      },
      label: {
        show: false,
        position: 'center'
      },
      emphasis: {
        label: {
          show: true,
          fontSize: 20,
          fontWeight: 'bold'
        }
      },
      labelLine: {
        show: false
      },
      data: []
    }
  ]
})

const difficultyChartOption = ref<any>({
  tooltip: {
    trigger: 'item'
  },
  series: [
    {
      type: 'pie',
      radius: '60%',
      data: [],
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowOffsetX: 0,
          shadowColor: 'rgba(0, 0, 0, 0.5)'
        }
      }
    }
  ]
})

async function loadData() {
  loading.value = true
  try {
    const data = await getProgressStatistics()
    statistics.value = data
    generateChartData(data)
  } catch (e) {
    statistics.value = mockProgressStatistics
    generateChartData(mockProgressStatistics)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>

<style lang="scss" scoped>
.stat-card {
  :deep(.el-card__body) {
    padding: 20px;
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
    }
  }

  .stat-icon {
    width: 56px;
    height: 56px;
    border-radius: 50%;
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 28px;
    color: #fff;

    &.blue {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }

    &.green {
      background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
    }

    &.purple {
      background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    }

    &.orange {
      background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
    }
  }
}

.chart {
  height: 300px;
}
</style>
