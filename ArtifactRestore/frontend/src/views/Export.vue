<template>
  <div class="export-container">
    <el-card class="export-card">
      <template #header>
        <div class="card-header">
          <span>档案导出</span>
          <div class="header-actions">
            <el-radio-group v-model="activeTab" size="small">
              <el-radio-button value="export" label="选择导出">选择导出</el-radio-button>
              <el-radio-button value="history" label="导出历史">导出历史</el-radio-button>
            </el-radio-group>
          </div>
        </div>
      </template>

      <div v-if="activeTab === 'export'" class="export-section">
        <div class="filter-bar">
          <el-form :inline="true" :model="filters" class="filter-form">
            <el-form-item label="搜索">
              <el-input v-model="filters.keyword" placeholder="搜索文物名称、年代、类别" clearable style="width: 200px" />
            </el-form-item>
            <el-form-item label="类别">
              <el-select v-model="filters.category" placeholder="选择类别" clearable style="width: 150px">
                <el-option label="青铜器" value="青铜器" />
                <el-option label="瓷器" value="瓷器" />
                <el-option label="书画" value="书画" />
                <el-option label="玉器" value="玉器" />
                <el-option label="陶器" value="陶器" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleSearch">搜索</el-button>
              <el-button @click="resetSearch">重置</el-button>
            </el-form-item>
          </el-form>
        </div>

        <div class="selection-bar">
          <el-checkbox v-model="isAllSelected" :indeterminate="isIndeterminate" @change="handleCheckAll">
            全选
          </el-checkbox>
          <span class="selected-count">已选择 {{ selectedIds.length }} 项</span>
          <div class="export-actions">
            <el-select v-model="exportFormat" placeholder="导出格式" style="width: 120px">
              <el-option label="TXT格式" value="txt" />
              <el-option label="JSON格式" value="json" />
            </el-select>
            <el-button type="primary" :disabled="selectedIds.length === 0" @click="handleBatchExport">
              <el-icon><Download /></el-icon> 批量导出
            </el-button>
          </div>
        </div>

        <el-table
          :data="filteredArtifacts"
          v-loading="loading"
          @selection-change="handleSelectionChange"
          stripe
        >
          <el-table-column type="selection" width="55" />
          <el-table-column prop="id" label="ID" width="100" />
          <el-table-column prop="name" label="文物名称" min-width="200" />
          <el-table-column prop="era" label="年代" width="150" />
          <el-table-column prop="category" label="类别" width="120" />
          <el-table-column label="操作" width="250">
            <template #default="scope">
              <el-button size="small" type="primary" @click="exportSingle(scope.row, 'txt')">
                <el-icon><Download /></el-icon> 导出TXT
              </el-button>
              <el-button size="small" type="success" @click="exportSingle(scope.row, 'json')">
                <el-icon><Download /></el-icon> 导出JSON
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50]"
          :total="allArtifacts.length"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>

      <div v-else class="history-section">
        <el-empty v-if="historyList.length === 0" description="暂无导出历史记录" />
        <el-table v-else :data="historyList" v-loading="historyLoading" stripe>
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="artifact_names" label="导出文物" min-width="200" show-overflow-tooltip>
            <template #default="scope">
              <el-tag
                v-for="name in scope.row.artifact_names.split(',').slice(0, 3)"
                :key="name"
                size="small"
                style="margin: 2px"
              >
                {{ name }}
              </el-tag>
              <span v-if="scope.row.artifact_names.split(',').length > 3" style="color: #909399">
                等{{ scope.row.artifact_names.split(',').length }}个
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="count" label="数量" width="100">
            <template #default="scope">
              <el-tag type="info">{{ scope.row.count }} 个</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="format_type" label="格式" width="100">
            <template #default="scope">
              <el-tag :type="scope.row.format_type === 'json' ? 'success' : 'primary'">
                {{ scope.row.format_type.toUpperCase() }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="导出时间" width="200" />
        </el-table>
        <el-pagination
          v-model:current-page="historyPage"
          v-model:page-size="historyPageSize"
          :page-sizes="[10, 20, 50]"
          :total="historyTotal"
          layout="total, sizes, prev, pager, next"
          @size-change="loadHistory"
          @current-change="loadHistory"
        />
      </div>
    </el-card>

    <el-card class="help-card">
      <template #header>
        <div class="card-header">
          <span>导出说明</span>
        </div>
      </template>
      <el-alert title="导出内容" type="info" :closable="false" show-icon>
        <template #default>
          <ul>
            <li>文物基本信息（名称、年代、类别、尺寸、材质等）</li>
            <li>修复计划（修复目标、方法、材料、预计工期）</li>
            <li>修复过程记录（操作步骤、使用材料、工具设备、遇到问题）</li>
            <li>影像资料（修复前、修复中、修复后）</li>
            <li>材料使用记录（材料名称、来源、用量、备注）</li>
          </ul>
        </template>
      </el-alert>
      <el-alert title="导出格式" type="success" :closable="false" show-icon style="margin-top: 10px">
        <template #default>
          <ul>
            <li><strong>TXT格式</strong>：纯文本格式，便于阅读和打印</li>
            <li><strong>JSON格式</strong>：结构化数据格式，便于数据交换和二次处理</li>
          </ul>
        </template>
      </el-alert>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { exportApi } from '../api'

const loading = ref(false)
const historyLoading = ref(false)
const allArtifacts = ref([])
const selectedIds = ref([])
const exportFormat = ref('txt')
const activeTab = ref('export')

const historyList = ref([])
const historyTotal = ref(0)
const historyPage = ref(1)
const historyPageSize = ref(10)

const filters = reactive({
  keyword: '',
  category: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 10
})

const filteredArtifacts = computed(() => {
  let result = [...allArtifacts.value]
  
  if (filters.keyword) {
    const keyword = filters.keyword.toLowerCase()
    result = result.filter(item =>
      (item.name || '').toLowerCase().includes(keyword) ||
      (item.era || '').toLowerCase().includes(keyword) ||
      (item.category || '').toLowerCase().includes(keyword)
    )
  }
  
  if (filters.category) {
    result = result.filter(item =>
      (item.category || '').includes(filters.category)
    )
  }
  
  return result
})

const isAllSelected = computed(() => {
  return filteredArtifacts.value.length > 0 &&
    selectedIds.value.length === filteredArtifacts.value.length
})

const isIndeterminate = computed(() => {
  return selectedIds.value.length > 0 &&
    selectedIds.value.length < filteredArtifacts.value.length
})

const loadArtifacts = async () => {
  loading.value = true
  try {
    const res = await exportApi.getList()
    if (res.code === 200) {
      allArtifacts.value = res.data || []
    }
  } catch (e) {
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

const loadHistory = async () => {
  historyLoading.value = true
  try {
    const res = await exportApi.getHistory({
      page: historyPage.value,
      per_page: historyPageSize.value
    })
    if (res.code === 200) {
      historyList.value = res.data.items || []
      historyTotal.value = res.data.total || 0
    }
  } catch (e) {
    ElMessage.error('加载导出历史失败')
  } finally {
    historyLoading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
}

const resetSearch = () => {
  filters.keyword = ''
  filters.category = ''
  pagination.page = 1
}

const handleSizeChange = (size) => {
  pagination.pageSize = size
  pagination.page = 1
}

const handleCurrentChange = (page) => {
  pagination.page = page
}

const handleSelectionChange = (selection) => {
  selectedIds.value = selection.map(item => item.id)
}

const handleCheckAll = (checked) => {
  if (checked) {
    selectedIds.value = filteredArtifacts.value.map(item => item.id)
  } else {
    selectedIds.value = []
  }
}

const exportSingle = (row, format) => {
  exportApi.exportArtifact(row.id, format)
  ElMessage.success(`正在生成${format.toUpperCase()}格式报告...`)
}

const handleBatchExport = () => {
  if (selectedIds.value.length === 0) {
    ElMessage.warning('请选择要导出的文物')
    return
  }
  
  exportApi.exportBatch(selectedIds.value, exportFormat.value)
  ElMessage.success(`正在生成${exportFormat.value.toUpperCase()}格式批量报告...`)
}

watch(activeTab, (newVal) => {
  if (newVal === 'history') {
    loadHistory()
  }
})

onMounted(() => {
  loadArtifacts()
})
</script>

<style scoped>
.export-container {
  padding: 10px;
}

.export-card,
.help-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
}

.filter-bar {
  margin-bottom: 15px;
}

.selection-bar {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 10px 0;
  border-bottom: 1px solid #ebeef5;
  margin-bottom: 15px;
}

.selected-count {
  color: #409EFF;
  font-size: 14px;
}

.export-actions {
  margin-left: auto;
  display: flex;
  gap: 10px;
}

.el-pagination {
  margin-top: 20px;
  justify-content: flex-end;
  display: flex;
}

ul {
  margin: 10px 0 0 20px;
  line-height: 2;
}
</style>
