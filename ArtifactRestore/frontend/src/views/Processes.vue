<template>
  <div class="page-container">
    <el-card class="filter-card">
      <el-form :inline="true" :model="filters" class="filter-form">
        <el-form-item label="文物名称">
          <el-input v-model="filters.artifact_name" placeholder="搜索文物名称" clearable />
        </el-form-item>
        <el-form-item label="开始时间">
          <el-date-picker
            v-model="filters.startDate"
            type="date"
            placeholder="开始日期"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item label="结束时间">
          <el-date-picker
            v-model="filters.endDate"
            type="date"
            placeholder="结束日期"
            value-format="YYYY-MM-DD"
          />
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
          <el-button type="success" @click="openCreateDialog">
            <el-icon><Plus /></el-icon> 新建记录
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="timeline-card">
      <template #header>
        <div class="card-header">
          <span>修复过程时间线</span>
          <el-tag type="info">共 {{ pagination.total }} 条记录</el-tag>
        </div>
      </template>
      <div v-loading="loading" class="timeline-container">
        <el-empty v-if="filteredList.length === 0" description="暂无修复过程记录" />
        <el-timeline v-else>
          <el-timeline-item
            v-for="(item, index) in paginatedList"
            :key="item.id"
            :timestamp="item.record_time"
            placement="top"
            :type="timelineTypes[index % 5]"
            :hollow="index % 2 === 0"
          >
            <el-card class="timeline-item-card" shadow="hover">
              <div class="timeline-item-header">
                <el-tag size="small" class="artifact-tag" @click="goToArtifact(item.artifact_id)">
                  {{ getArtifactName(item.artifact_id) }}
                </el-tag>
                <div class="timeline-actions">
                  <el-button size="small" type="primary" link @click="goToArtifact(item.artifact_id)">
                    查看详情
                  </el-button>
                  <el-button size="small" type="warning" link @click="openEditDialog(item)">
                    编辑
                  </el-button>
                  <el-button size="small" type="danger" link @click="handleDelete(item)">
                    删除
                  </el-button>
                </div>
              </div>
              <div class="timeline-content">
                <div class="content-section">
                  <span class="section-label">操作步骤：</span>
                  <span class="section-value">{{ item.operation_steps || '暂无' }}</span>
                </div>
                <div v-if="item.used_materials" class="content-section">
                  <span class="section-label">使用材料：</span>
                  <span class="section-value">{{ item.used_materials }}</span>
                </div>
                <div v-if="item.tools" class="content-section">
                  <span class="section-label">工具设备：</span>
                  <span class="section-value">{{ item.tools }}</span>
                </div>
                <div v-if="item.problems" class="content-section problems">
                  <span class="section-label">遇到问题：</span>
                  <span class="section-value">{{ item.problems }}</span>
                </div>
              </div>
            </el-card>
          </el-timeline-item>
        </el-timeline>
        <el-pagination
          v-if="pagination.total > pagination.pageSize"
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[5, 10, 20]"
          :total="pagination.total"
          layout="prev, pager, next, total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          style="margin-top: 20px; justify-content: center; display: flex;"
        />
      </div>
    </el-card>

    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
    >
      <el-form :model="form" ref="formRef" :rules="rules" label-width="100px">
        <el-form-item label="文物" prop="artifact_id">
          <el-select v-model="form.artifact_id" placeholder="选择文物" style="width: 100%" :disabled="!!editingId">
            <el-option
              v-for="artifact in artifactList"
              :key="artifact.id"
              :label="artifact.name"
              :value="artifact.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="记录时间" prop="record_time">
          <el-date-picker
            v-model="form.record_time"
            type="datetime"
            placeholder="选择记录时间"
            value-format="YYYY-MM-DD HH:mm:ss"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="操作步骤" prop="operation_steps">
          <el-input v-model="form.operation_steps" type="textarea" :rows="3" placeholder="请输入操作步骤" />
        </el-form-item>
        <el-form-item label="使用材料">
          <el-input v-model="form.used_materials" type="textarea" :rows="2" placeholder="请输入使用材料" />
        </el-form-item>
        <el-form-item label="工具设备">
          <el-input v-model="form.tools" placeholder="如：刷子、放大镜、吹风机等" />
        </el-form-item>
        <el-form-item label="遇到问题">
          <el-input v-model="form.problems" type="textarea" :rows="2" placeholder="请输入遇到的问题" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { processApi, artifactApi } from '../api'

const router = useRouter()

const timelineTypes = ['primary', 'success', 'warning', 'danger', 'info']

const loading = ref(false)
const allProcesses = ref([])
const artifactList = ref([])
const artifactMap = ref({})

const filters = reactive({
  artifact_name: '',
  category: '',
  startDate: '',
  endDate: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0,
  pages: 0
})

const dialogVisible = ref(false)
const dialogTitle = ref('编辑过程记录')
const editingId = ref(null)
const formRef = ref(null)
const form = reactive({
  artifact_id: null,
  operation_steps: '',
  used_materials: '',
  tools: '',
  problems: '',
  record_time: ''
})

const rules = {
  artifact_id: [
    { required: true, message: '请选择文物', trigger: 'change' }
  ],
  operation_steps: [
    { required: true, message: '请输入操作步骤', trigger: 'blur' },
    { min: 2, max: 1000, message: '长度在 2 到 1000 个字符', trigger: 'blur' }
  ],
  record_time: [
    { required: true, message: '请选择记录时间', trigger: 'change' }
  ]
}

const getArtifactName = (id) => {
  return artifactMap.value[id]?.name || '未知文物'
}

const goToArtifact = (id) => {
  router.push(`/artifacts/${id}`)
}

const loadArtifacts = async () => {
  try {
    const res = await artifactApi.getList({ per_page: 1000 })
    if (res.code === 200) {
      const items = res.data.items || res.data || []
      artifactList.value = items
      artifactMap.value = {}
      items.forEach(a => {
        artifactMap.value[a.id] = a
      })
    }
  } catch (e) {
    console.error('加载文物列表失败', e)
  }
}

const loadData = async () => {
  loading.value = true
  try {
    const res = await processApi.getList()
    if (res.code === 200) {
      allProcesses.value = (res.data || []).sort((a, b) => {
        return new Date(b.record_time) - new Date(a.record_time)
      })
      filterAndPaginate()
    }
  } catch (e) {
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

const filteredList = computed(() => {
  let result = [...allProcesses.value]
  
  if (filters.artifact_name) {
    result = result.filter(item => {
      const name = artifactMap.value[item.artifact_id]?.name || ''
      return name.includes(filters.artifact_name)
    })
  }
  
  if (filters.category) {
    result = result.filter(item => {
      const category = artifactMap.value[item.artifact_id]?.category || ''
      return category.includes(filters.category)
    })
  }
  
  if (filters.startDate) {
    result = result.filter(item => item.record_time >= filters.startDate)
  }
  
  if (filters.endDate) {
    const endDate = filters.endDate + ' 23:59:59'
    result = result.filter(item => item.record_time <= endDate)
  }
  
  return result
})

const paginatedList = computed(() => {
  pagination.total = filteredList.value.length
  pagination.pages = Math.ceil(filteredList.value.length / pagination.pageSize)
  
  const start = (pagination.page - 1) * pagination.pageSize
  return filteredList.value.slice(start, start + pagination.pageSize)
})

const filterAndPaginate = () => {
  pagination.page = 1
}

const handleSearch = () => {
  pagination.page = 1
}

const resetSearch = () => {
  filters.artifact_name = ''
  filters.category = ''
  filters.startDate = ''
  filters.endDate = ''
  pagination.page = 1
}

const handleSizeChange = (size) => {
  pagination.pageSize = size
  pagination.page = 1
}

const handleCurrentChange = (page) => {
  pagination.page = page
}

const openCreateDialog = () => {
  editingId.value = null
  dialogTitle.value = '新建过程记录'
  Object.assign(form, {
    artifact_id: null,
    operation_steps: '',
    used_materials: '',
    tools: '',
    problems: '',
    record_time: ''
  })
  dialogVisible.value = true
}

const openEditDialog = (row) => {
  editingId.value = row.id
  dialogTitle.value = '编辑过程记录'
  Object.assign(form, {
    artifact_id: row.artifact_id,
    operation_steps: row.operation_steps,
    used_materials: row.used_materials,
    tools: row.tools,
    problems: row.problems,
    record_time: row.record_time
  })
  dialogVisible.value = true
}

const handleSubmit = async () => {
  if (!form.artifact_id) {
    ElMessage.warning('请选择文物')
    return
  }
  
  try {
    let res
    if (editingId.value) {
      res = await processApi.update(editingId.value, form)
    } else {
      res = await processApi.create(form)
    }
    if (res.code === 200) {
      ElMessage.success('保存成功')
      dialogVisible.value = false
      loadData()
    }
  } catch (e) {
    ElMessage.error('保存失败')
  }
}

const handleDelete = (row) => {
  ElMessageBox.confirm('确定要删除该过程记录吗？', '提示', { type: 'warning' }).then(async () => {
    try {
      const res = await processApi.delete(row.id)
      if (res.code === 200) {
        ElMessage.success('删除成功')
        loadData()
      }
    } catch (e) {
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

onMounted(() => {
  loadArtifacts()
  loadData()
})
</script>

<style scoped>
.page-container {
  padding: 10px;
}

.filter-card,
.timeline-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
}

.timeline-container {
  min-height: 200px;
}

.timeline-item-card {
  margin-bottom: 10px;
}

.timeline-item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.artifact-tag {
  cursor: pointer;
}

.timeline-actions {
  display: flex;
  gap: 5px;
}

.timeline-content {
  background: #f9fafb;
  padding: 15px;
  border-radius: 8px;
}

.content-section {
  margin-bottom: 8px;
  line-height: 1.6;
}

.content-section:last-child {
  margin-bottom: 0;
}

.section-label {
  color: #909399;
  font-size: 14px;
  margin-right: 5px;
}

.section-value {
  color: #303133;
  font-size: 14px;
}

.content-section.problems {
  background: #fef0f0;
  padding: 8px;
  border-radius: 4px;
  margin-top: 10px;
}

.content-section.problems .section-label {
  color: #f56c6c;
}
</style>
