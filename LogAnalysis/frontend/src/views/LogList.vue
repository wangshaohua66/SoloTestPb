<template>
  <div class="log-list">
    <el-card>
      <template #header>
        <div class="header-actions">
          <span>日志列表</span>
          <div class="filters">
            <el-select v-model="filterForm.level" placeholder="日志级别" clearable style="width: 150px; margin-right: 10px;">
              <el-option v-for="level in logLevels" :key="level" :label="level" :value="level"></el-option>
            </el-select>
            <el-input v-model="filterForm.service_name" placeholder="服务名称" clearable style="width: 200px; margin-right: 10px;"></el-input>
            <el-button type="primary" @click="loadLogs">查询</el-button>
            <el-button @click="resetFilter">重置</el-button>
          </div>
        </div>
      </template>

      <el-table :data="logs" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80"></el-table-column>
        <el-table-column prop="timestamp" label="时间" width="180"></el-table-column>
        <el-table-column prop="level" label="级别" width="100">
          <template #default="{ row }">
            <el-tag :type="getLevelTagType(row.level)" size="small">{{ row.level }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="service_name" label="服务" width="120"></el-table-column>
        <el-table-column prop="module" label="模块" width="150"></el-table-column>
        <el-table-column prop="message" label="消息" show-overflow-tooltip></el-table-column>
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button type="text" @click="showDetail(row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        background
        layout="prev, pager, next, jumper, ->, total"
        :total="total"
        :page-size="filterForm.page_size"
        :current-page="filterForm.page"
        @current-change="handlePageChange"
        style="margin-top: 20px; justify-content: flex-end;"
      ></el-pagination>
    </el-card>

    <el-dialog v-model="detailVisible" title="日志详情" width="800px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="ID">{{ currentLog?.id }}</el-descriptions-item>
        <el-descriptions-item label="时间">{{ currentLog?.timestamp }}</el-descriptions-item>
        <el-descriptions-item label="级别">
          <el-tag :type="getLevelTagType(currentLog?.level)">{{ currentLog?.level }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="服务">{{ currentLog?.service_name }}</el-descriptions-item>
        <el-descriptions-item label="模块">{{ currentLog?.module }}</el-descriptions-item>
        <el-descriptions-item label="主机">{{ currentLog?.host || '-' }}</el-descriptions-item>
        <el-descriptions-item label="Trace ID">{{ currentLog?.trace_id || '-' }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ currentLog?.created_at }}</el-descriptions-item>
        <el-descriptions-item label="消息" :span="2">
          <pre style="white-space: pre-wrap; word-break: break-all;">{{ currentLog?.message }}</pre>
        </el-descriptions-item>
        <el-descriptions-item label="原始数据" :span="2">
          <pre style="white-space: pre-wrap; word-break: break-all;">{{ currentLog?.raw_data }}</pre>
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import api from '@/utils/api'

const logs = ref([])
const total = ref(0)
const logLevels = ref(['DEBUG', 'INFO', 'WARNING', 'ERROR', 'FATAL', 'TRACE'])

const filterForm = reactive({
  page: 1,
  page_size: 20,
  level: '',
  service_name: ''
})

const detailVisible = ref(false)
const currentLog = ref(null)

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

const loadLogs = async () => {
  try {
    const res = await api.getLogs(filterForm)
    logs.value = res.data?.logs || []
    total.value = res.data?.pagination?.total || 0
  } catch (error) {
    console.error('加载日志失败:', error)
  }
}

const resetFilter = () => {
  filterForm.page = 1
  filterForm.level = ''
  filterForm.service_name = ''
  loadLogs()
}

const handlePageChange = (page) => {
  filterForm.page = page
  loadLogs()
}

const showDetail = (log) => {
  currentLog.value = log
  detailVisible.value = true
}

onMounted(() => {
  loadLogs()
})
</script>

<style scoped>
.log-list {
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
</style>
