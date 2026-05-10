<template>
  <div class="dashboard">
    <el-row :gutter="20" class="stats-cards">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-value">{{ overview.summary?.total_logs || 0 }}</div>
            <div class="stat-label">总日志数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card error-card">
          <div class="stat-content">
            <div class="stat-value">{{ overview.summary?.error_count || 0 }}</div>
            <div class="stat-label">错误数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card warning-card">
          <div class="stat-content">
            <div class="stat-value">{{ overview.summary?.warning_count || 0 }}</div>
            <div class="stat-label">警告数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card rate-card">
          <div class="stat-content">
            <div class="stat-value">{{ overview.summary?.error_rate || '0.00' }}%</div>
            <div class="stat-label">错误率</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <span>日志数量趋势</span>
          </template>
          <div ref="logChart" style="height: 300px;"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <span>错误率趋势</span>
          </template>
          <div ref="errorRateChart" style="height: 300px;"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <span>日志级别分布</span>
          </template>
          <div ref="levelChart" style="height: 300px;"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <span>Top服务（按错误数）</span>
          </template>
          <el-table :data="topErrorServices" style="width: 100%">
            <el-table-column prop="service" label="服务名称"></el-table-column>
            <el-table-column prop="count" label="错误数"></el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card class="chart-card">
          <template #header>
            <span>最新日志</span>
            <el-button type="primary" size="small" style="float: right;" @click="loadData">刷新</el-button>
          </template>
          <el-table :data="recentLogs" style="width: 100%">
            <el-table-column prop="timestamp" label="时间" width="180"></el-table-column>
            <el-table-column prop="level" label="级别" width="100">
              <template #default="{ row }">
                <el-tag :type="getLevelTagType(row.level)" size="small">{{ row.level }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="service_name" label="服务" width="120"></el-table-column>
            <el-table-column prop="module" label="模块" width="150"></el-table-column>
            <el-table-column prop="message" label="消息"></el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import api from '@/utils/api'

const logChart = ref(null)
const errorRateChart = ref(null)
const levelChart = ref(null)

const overview = ref({})
const recentLogs = ref([])
const topErrorServices = ref([])

let logChartInstance = null
let errorRateChartInstance = null
let levelChartInstance = null

const getLevelTagType = (level) => {
  const typeMap = {
    'DEBUG': '',
    'INFO': 'success',
    'WARNING': 'warning',
    'WARN': 'warning',
    'ERROR': 'danger',
    'FATAL': 'danger',
    'ERR': 'danger'
  }
  return typeMap[level] || 'info'
}

const loadData = async () => {
  try {
    const overviewRes = await api.getOverview({ hours: 24 })
    overview.value = overviewRes.data || {}

    const logsRes = await api.getLogs({ page_size: 10 })
    recentLogs.value = logsRes.data?.logs || []

    const topRes = await api.getTopServices({ by_errors: true, limit: 10 })
    topErrorServices.value = topRes.data?.top_services || []

    renderCharts()
  } catch (error) {
    console.error('加载仪表盘数据加载失败:', error)
  }
}

const renderCharts = () => {
  renderLogChart()
  renderErrorRateChart()
  renderLevelChart()
}

const renderLogChart = () => {
  if (!logChart.value) {
    if (logChartInstance) {
      logChartInstance.dispose()
    }
    return
  }

  logChartInstance = echarts.init(logChart.value)

  const trend = overview.value.trend?.total_series || []
  const times = trend.map(item => {
    const date = new Date(item.time)
    return `${date.getHours()}:${String(date.getMinutes()).padStart(2, '0')}`
  })
  const values = trend.map(item => item.value)

  logChartInstance.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: times
    },
    yAxis: { type: 'value' },
    series: [{
      data: values,
      type: 'line',
      smooth: true,
      areaStyle: {}
    }]
  })
}

const renderErrorRateChart = () => {
  if (!errorRateChart.value) {
    if (errorRateChartInstance) {
      errorRateChartInstance.dispose()
    }
    return
  }

  errorRateChartInstance = echarts.init(errorRateChart.value)

  const trend = overview.value.trend?.error_rate_series || []
  const times = trend.map(item => {
    const date = new Date(item.time)
    return `${date.getHours()}:${String(date.getMinutes()).padStart(2, '0')}`
  })
  const values = trend.map(item => item.value)

  errorRateChartInstance.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: times
    },
    yAxis: { type: 'value' },
    series: [{
      data: values,
      type: 'line',
      smooth: true,
      itemStyle: { color: '#f56c6c' }
    }]
  })
}

const renderLevelChart = () => {
  if (!levelChart.value) {
    if (levelChartInstance) {
      levelChartInstance.dispose()
    }
    return
  }

  levelChartInstance = echarts.init(levelChart.value)

  const byLevel = overview.value.by_level || {}
  const data = Object.entries(byLevel).map(([name, value]) => ({ name, value }))

  levelChartInstance.setOption({
    tooltip: { trigger: 'item' },
    legend: { orient: 'vertical', left: 'left' },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      data: data,
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowOffsetX: 0,
          shadowColor: 'rgba(0, 0, 0, 0.5)'
        }
      }
    }]
  })
}

const handleResize = () => {
  if (logChartInstance) logChartInstance.resize()
  if (errorRateChartInstance) errorRateChartInstance.resize()
  if (levelChartInstance) levelChartInstance.resize()
}

onMounted(() => {
  loadData()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (logChartInstance) logChartInstance.dispose()
  if (errorRateChartInstance) errorRateChartInstance.dispose()
  if (levelChartInstance) levelChartInstance.dispose()
})
</script>

<style scoped>
.dashboard {
  padding: 0;
}

.stats-cards {
  margin-bottom: 20px;
}

.stat-card {
  border-radius: 8px;
}

.stat-content {
  text-align: center;
  padding: 10px 0;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #409EFF;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 8px;
}

.error-card .stat-value {
  color: #f56c6c;
}

.warning-card .stat-value {
  color: #e6a23c;
}

.rate-card .stat-value {
  color: #67c23a;
}

.chart-card {
  margin-bottom: 20px;
}
</style>
