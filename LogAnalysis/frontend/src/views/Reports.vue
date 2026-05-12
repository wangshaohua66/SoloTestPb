<template>
  <div class="reports">
    <el-card>
      <template #header>
        <span>报表导出</span>
      </template>

      <el-form :model="reportForm" label-width="120px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="报表类型">
              <el-select v-model="reportForm.type" placeholder="选择报表类型" style="width: 100%;">
                <el-option label="汇总报表" value="summary"></el-option>
                <el-option label="详细报表" value="detailed"></el-option>
                <el-option label="日报" value="daily"></el-option>
                <el-option label="周报" value="weekly"></el-option>
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="导出格式">
              <el-select v-model="reportForm.format" placeholder="选择导出格式" style="width: 100%;">
                <el-option label="JSON格式" value="json"></el-option>
                <el-option label="文本格式" value="text"></el-option>
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="开始时间">
              <el-date-picker
                v-model="reportForm.start_time"
                type="datetime"
                placeholder="选择开始时间"
                style="width: 100%;"
              ></el-date-picker>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="结束时间">
              <el-date-picker
                v-model="reportForm.end_time"
                type="datetime"
                placeholder="选择结束时间"
                style="width: 100%;"
              ></el-date-picker>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="服务名称">
              <el-input v-model="reportForm.service_name" placeholder="可选，按服务过滤"></el-input>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="作为附件下载">
              <el-switch v-model="reportForm.download"></el-switch>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item>
          <el-button type="primary" @click="generateReport">生成报表</el-button>
          <el-button type="success" @click="downloadReport">下载报表</el-button>
          <el-button @click="previewReport">预览报表</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card v-if="previewData" style="margin-top: 20px;">
      <template #header>
        <span>报表预览</span>
      </template>

      <el-tabs v-model="activeTab">
        <el-tab-pane label="概览" name="overview">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="报表类型">{{ reportForm.type }}</el-descriptions-item>
            <el-descriptions-item label="总日志数">{{ previewData.summary?.total_logs || 0 }}</el-descriptions-item>
            <el-descriptions-item label="错误数">{{ previewData.summary?.error_count || 0 }}</el-descriptions-item>
            <el-descriptions-item label="警告数">{{ previewData.summary?.warning_count || 0 }}</el-descriptions-item>
            <el-descriptions-item label="错误率">{{ previewData.summary?.error_rate || 0 }}%</el-descriptions-item>
          </el-descriptions>
        </el-tab-pane>
        <el-tab-pane label="级别分布" name="level">
          <el-table :data="levelDistribution" style="width: 100%">
            <el-table-column prop="level" label="日志级别"></el-table-column>
            <el-table-column prop="count" label="数量"></el-table-column>
          </el-table>
        </el-tab-pane>
        <el-tab-pane label="服务分布" name="service">
          <el-table :data="serviceDistribution" style="width: 100%">
            <el-table-column prop="service" label="服务名称"></el-table-column>
            <el-table-column prop="count" label="日志数"></el-table-column>
          </el-table>
        </el-tab-pane>
        <el-tab-pane v-if="previewData.logs" label="日志列表" name="logs">
          <el-table :data="previewData.logs.slice(0, 50)" style="width: 100%">
            <el-table-column prop="timestamp" label="时间" width="180"></el-table-column>
            <el-table-column prop="level" label="级别" width="100"></el-table-column>
            <el-table-column prop="service_name" label="服务" width="120"></el-table-column>
            <el-table-column prop="message" label="消息"></el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/utils/api'

const activeTab = ref('overview')
const previewData = ref(null)

const reportForm = reactive({
  type: 'summary',
  format: 'json',
  start_time: null,
  end_time: null,
  service_name: '',
  download: false
})

const levelDistribution = computed(() => {
  if (!previewData.value?.by_level) return []
  return Object.entries(previewData.value.by_level).map(([level, count]) => ({ level, count }))
})

const serviceDistribution = computed(() => {
  if (!previewData.value?.by_service) return []
  return Object.entries(previewData.value.by_service).map(([service, count]) => ({ service, count }))
})

const formatDateTime = (date) => {
  if (!date) return null
  return date.toISOString()
}

const getReportParams = () => {
  const params = {
    type: reportForm.type,
    format: reportForm.format,
    download: reportForm.download ? 1 : 0
  }

  if (reportForm.start_time) {
    params.start_time = formatDateTime(reportForm.start_time)
  }
  if (reportForm.end_time) {
    params.end_time = formatDateTime(reportForm.end_time)
  }
  if (reportForm.service_name) {
    params.service_name = reportForm.service_name
  }

  return params
}

const generateReport = async () => {
  try {
    const params = getReportParams()
    const res = await api.getSummaryReport(params)
    previewData.value = res.data
    ElMessage.success('报表生成成功')
  } catch (error) {
    ElMessage.error('报表生成失败')
  }
}

const previewReport = async () => {
  await generateReport()
}

const downloadReport = async () => {
  try {
    const params = getReportParams()
    params.download = 1

    const response = await api.exportReport(params)
    const blob = new Blob([response], { type: reportForm.format === 'json' ? 'application/json' : 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `report_${reportForm.type}_${Date.now()}.${reportForm.format}`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)

    ElMessage.success('报表下载成功')
  } catch (error) {
    ElMessage.error('报表下载失败')
  }
}
</script>

<style scoped>
.reports {
  padding: 0;
}
</style>
