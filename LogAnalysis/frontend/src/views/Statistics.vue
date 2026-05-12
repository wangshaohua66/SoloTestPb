<template>
  <div class="statistics">
    <el-card>
      <template #header>
        <div class="header-actions">
          <span>统计分析</span>
          <div class="filters">
            <el-select v-model="timeRange" placeholder="选择时间范围" style="width: 150px; margin-right: 10px;">
              <el-option label="最近1小时" value="1"></el-option>
              <el-option label="最近6小时" value="6"></el-option>
              <el-option label="最近24小时" value="24"></el-option>
              <el-option label="最近7天" value="168"></el-option>
            </el-select>
            <el-button type="primary" @click="loadStats">查询</el-button>
          </div>
        </div>
      </template>

      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-value">{{ summary.summary?.total_logs || 0 }}</div>
              <div class="stat-label">总日志数</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card error-card">
            <div class="stat-content">
              <div class="stat-value">{{ summary.summary?.error_count || 0 }}</div>
              <div class="stat-label">错误数</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card warning-card">
            <div class="stat-content">
              <div class="stat-value">{{ summary.summary?.warning_count || 0 }}</div>
              <div class="stat-label">警告数</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card rate-card">
            <div class="stat-content">
              <div class="stat-value">{{ summary.summary?.error_rate || '0.00' }}%</div>
              <div class="stat-label">错误率</div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </el-card>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <span>日志级别分布</span>
          </template>
          <div ref="levelChart" style="height: 350px;"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <span>服务日志分布</span>
          </template>
          <div ref="serviceChart" style="height: 350px;"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card class="chart-card">
          <template #header>
            <span>日志数量趋势</span>
          </template>
          <div ref="trendChart" style="height: 350px;"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <span>Top服务（按日志量）</span>
          </template>
          <el-table :data="topServices" style="width: 100%">
            <el-table-column prop="service" label="服务名称"></el-table-column>
            <el-table-column prop="count" label="日志数"></el-table-column>
          </el-table>
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
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import api from '@/utils/api'

const timeRange = ref('24')
const summary = ref({})
const topServices = ref([])
const topErrorServices = ref([])

const levelChart = ref(null)
const serviceChart = ref(null)
const trendChart = ref(null)

let levelChartInstance = null
let serviceChartInstance = null
let trendChartInstance = null

const loadStats = async () => {
  try {
    const hours = parseInt(timeRange.value)
    const summaryRes = await api.getStatsSummary({ hours })
    summary.value = summaryRes.data || {}

    const topRes = await api.getTopServices({ hours, limit: 10 })
    topServices.value = topRes.data?.top_services || []

    const topErrorRes = await api.getTopServices({ hours, limit: 10, by_errors: true })
    topErrorServices.value = topErrorRes.data?.top_services || []

    renderCharts()
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

const renderCharts = () => {
  renderLevelChart()
  renderServiceChart()
  renderTrendChart()
}

const renderLevelChart = () => {
  if (!levelChart.value) return
  if (levelChartInstance) levelChartInstance.dispose()

  levelChartInstance = echarts.init(levelChart.value)

  const byLevel = summary.value.by_level || {}
  const data = Object.entries(byLevel).map(([name, value]) => ({ name, value }))

  levelChartInstance.setOption({
    tooltip: { trigger: 'item' },
    legend: { orient: 'vertical', left: 'left' },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      data: data
    }]
  })
}

const renderServiceChart = () => {
  if (!serviceChart.value) return
  if (serviceChartInstance) serviceChartInstance.dispose()

  serviceChartInstance = echarts.init(serviceChart.value)

  const byService = summary.value.by_service || {}
  const services = Object.entries(byService)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10)

  serviceChartInstance.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'value'
    },
    yAxis: {
      type: 'category',
      data: services.map(s => s[0])
    },
    series: [{
      type: 'bar',
      data: services.map(s => s[1])
    }]
  })
}

const renderTrendChart = () => {
  if (!trendChart.value) return
  if (trendChartInstance) trendChartInstance.dispose()

  trendChartInstance = echarts.init(trendChart.value)

  const trend = summary.value.trend?.total_series || []
  const times = trend.map(item => {
    const date = new Date(item.time)
    return `${date.getMonth() + 1}/${date.getDate()} ${date.getHours()}:${String(date.getMinutes()).padStart(2, '0')}`
  })
  const values = trend.map(item => item.value)

  trendChartInstance.setOption({
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

const handleResize = () => {
  if (levelChartInstance) levelChartInstance.resize()
  if (serviceChartInstance) serviceChartInstance.resize()
  if (trendChartInstance) trendChartInstance.resize()
}

onMounted(() => {
  loadStats()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (levelChartInstance) levelChartInstance.dispose()
  if (serviceChartInstance) serviceChartInstance.dispose()
  if (trendChartInstance) trendChartInstance.dispose()
})
</script>

<style scoped>
.statistics {
  padding: 0;
}

.header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filters {
  display: flex;
  align-items: center;
}

.stat-card {
  border-radius: 8px;
}

.stat-content {
  text-align: center;
  padding: 10px 0;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #409EFF;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 5px;
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
  margin-bottom: 0;
}
</style>
