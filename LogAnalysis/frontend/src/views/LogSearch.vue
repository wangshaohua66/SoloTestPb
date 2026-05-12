<template>
  <div class="log-search">
    <el-card>
      <template #header>
        <span>日志检索</span>
      </template>

      <el-form :model="searchForm" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="关键词">
              <el-input v-model="searchForm.keyword" placeholder="输入搜索关键词"></el-input>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="日志级别">
              <el-select v-model="searchForm.level" placeholder="选择级别" clearable style="width: 100%;">
                <el-option v-for="level in logLevels" :key="level" :label="level" :value="level"></el-option>
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="服务名称">
              <el-input v-model="searchForm.service_name" placeholder="服务名称"></el-input>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="开始时间">
              <el-date-picker
                v-model="searchForm.start_time"
                type="datetime"
                placeholder="选择开始时间"
                style="width: 100%;"
              ></el-date-picker>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="结束时间">
              <el-date-picker
                v-model="searchForm.end_time"
                type="datetime"
                placeholder="选择结束时间"
                style="width: 100%;"
              ></el-date-picker>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item>
          <el-button type="primary" @click="doSearch">搜索</el-button>
          <el-button @click="resetForm">重置</el-button>
          <span style="margin-left: 20px;">
            搜索结果：<strong>{{ total }}</strong> 条
          </span>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card style="margin-top: 20px;">
      <template #header>
        <span>搜索结果</span>
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
      </el-table>

      <el-pagination
        background
        layout="prev, pager, next, jumper"
        :total="total"
        :page-size="pageSize"
        :current-page="currentPage"
        @current-change="handlePageChange"
        style="margin-top: 20px; justify-content: flex-end;"
      ></el-pagination>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import api from '@/utils/api'

const logs = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = 20
const logLevels = ref(['DEBUG', 'INFO', 'WARNING', 'ERROR', 'FATAL', 'TRACE'])

const searchForm = reactive({
  keyword: '',
  level: '',
  service_name: '',
  start_time: null,
  end_time: null
})

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

const formatDateTime = (date) => {
  if (!date) return null
  return date.toISOString()
}

const doSearch = async () => {
  currentPage.value = 1
  await searchLogs()
}

const searchLogs = async () => {
  try {
    const params = {
      keyword: searchForm.keyword,
      level: searchForm.level,
      service_name: searchForm.service_name,
      start_time: formatDateTime(searchForm.start_time),
      end_time: formatDateTime(searchForm.end_time),
      page: currentPage.value,
      page_size: pageSize
    }

    const res = await api.searchLogs(params)
    logs.value = res.data?.logs || []
    total.value = res.data?.pagination?.total || 0
  } catch (error) {
    console.error('搜索日志失败:', error)
  }
}

const resetForm = () => {
  searchForm.keyword = ''
  searchForm.level = ''
  searchForm.service_name = ''
  searchForm.start_time = null
  searchForm.end_time = null
  currentPage.value = 1
  logs.value = []
  total.value = 0
}

const handlePageChange = (page) => {
  currentPage.value = page
  searchLogs()
}
</script>

<style scoped>
.log-search {
  padding: 0;
}
</style>
