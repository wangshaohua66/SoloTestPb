<template>
  <div class="page-container">
    <el-card class="filter-card">
      <el-form :inline="true" :model="filters" class="filter-form">
        <el-form-item label="材料名称">
          <el-input v-model="filters.name" placeholder="搜索材料名称" clearable />
        </el-form-item>
        <el-form-item label="文物名称">
          <el-input v-model="filters.artifact_name" placeholder="搜索文物名称" clearable />
        </el-form-item>
        <el-form-item label="来源">
          <el-input v-model="filters.source" placeholder="搜索来源" clearable />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="resetSearch">重置</el-button>
          <el-button type="success" @click="openCreateDialog">
            <el-icon><Plus /></el-icon> 新增材料
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="stats-card">
      <template #header>
        <div class="card-header">
          <span>材料统计</span>
        </div>
      </template>
      <el-row :gutter="20">
        <el-col :span="8">
          <div class="stat-item">
            <div class="stat-value">{{ materialStats.totalCount }}</div>
            <div class="stat-label">材料记录总数</div>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="stat-item">
            <div class="stat-value">{{ materialStats.uniqueNames }}</div>
            <div class="stat-label">材料种类数</div>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="stat-item">
            <div class="stat-value">{{ materialStats.relatedArtifacts }}</div>
            <div class="stat-label">关联文物数</div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <el-card class="list-card">
      <template #header>
        <div class="card-header">
          <span>材料列表</span>
        </div>
      </template>
      <el-table :data="paginatedList" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="材料名称" min-width="150">
          <template #default="scope">
            <el-tag :type="getMaterialColor(scope.row.name)">{{ scope.row.name }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="artifact_name" label="关联文物" min-width="150">
          <template #default="scope">
            <el-button type="primary" link @click="goToArtifact(scope.row.artifact_id)">
              {{ getArtifactName(scope.row.artifact_id) }}
            </el-button>
          </template>
        </el-table-column>
        <el-table-column prop="source" label="来源" min-width="120" />
        <el-table-column prop="usage" label="用量" width="100" />
        <el-table-column prop="notes" label="备注" min-width="150" show-overflow-tooltip />
        <el-table-column prop="created_at" label="记录时间" width="180" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="scope">
            <el-button size="small" type="primary" link @click="goToArtifact(scope.row.artifact_id)">
              查看文物
            </el-button>
            <el-button size="small" type="warning" link @click="openEditDialog(scope.row)">
              编辑
            </el-button>
            <el-button size="small" type="danger" link @click="handleDelete(scope.row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :page-sizes="[10, 20, 50]"
        :total="filteredList.length"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
        style="margin-top: 20px; justify-content: flex-end; display: flex;"
      />
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
        <el-form-item label="材料名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入材料名称" />
        </el-form-item>
        <el-form-item label="材料来源">
          <el-input v-model="form.source" placeholder="如：供应商A、自制等" />
        </el-form-item>
        <el-form-item label="用量" prop="usage">
          <el-input v-model="form.usage" placeholder="如：50ml、100g、3块" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.notes" type="textarea" :rows="2" placeholder="请输入备注" />
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
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { materialApi, artifactApi } from '../api'

const router = useRouter()

const materialColors = ['primary', 'success', 'warning', 'danger', 'info']
const colorMap = {}

const loading = ref(false)
const allMaterials = ref([])
const artifactList = ref([])
const artifactMap = ref({})

const filters = reactive({
  name: '',
  artifact_name: '',
  source: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 10
})

const dialogVisible = ref(false)
const dialogTitle = ref('编辑材料记录')
const editingId = ref(null)
const formRef = ref(null)
const form = reactive({
  artifact_id: null,
  name: '',
  source: '',
  usage: '',
  notes: ''
})

const rules = {
  artifact_id: [
    { required: true, message: '请选择文物', trigger: 'change' }
  ],
  name: [
    { required: true, message: '请输入材料名称', trigger: 'blur' },
    { min: 1, max: 100, message: '长度在 1 到 100 个字符', trigger: 'blur' }
  ],
  usage: [
    { required: true, message: '请输入用量', trigger: 'blur' }
  ]
}

const getMaterialColor = (name) => {
  if (!colorMap[name]) {
    colorMap[name] = materialColors[Object.keys(colorMap).length % materialColors.length]
  }
  return colorMap[name]
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
    const res = await materialApi.getList()
    if (res.code === 200) {
      allMaterials.value = res.data || []
    }
  } catch (e) {
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

const materialStats = computed(() => {
  const uniqueNames = new Set()
  const uniqueArtifacts = new Set()
  
  allMaterials.value.forEach(item => {
    if (item.name) uniqueNames.add(item.name)
    if (item.artifact_id) uniqueArtifacts.add(item.artifact_id)
  })
  
  return {
    totalCount: allMaterials.value.length,
    uniqueNames: uniqueNames.size,
    relatedArtifacts: uniqueArtifacts.size
  }
})

const filteredList = computed(() => {
  let result = [...allMaterials.value]
  
  if (filters.name) {
    const keyword = filters.name.toLowerCase()
    result = result.filter(item =>
      (item.name || '').toLowerCase().includes(keyword)
    )
  }
  
  if (filters.artifact_name) {
    result = result.filter(item => {
      const name = artifactMap.value[item.artifact_id]?.name || ''
      return name.includes(filters.artifact_name)
    })
  }
  
  if (filters.source) {
    const keyword = filters.source.toLowerCase()
    result = result.filter(item =>
      (item.source || '').toLowerCase().includes(keyword)
    )
  }
  
  return result
})

const paginatedList = computed(() => {
  const start = (pagination.page - 1) * pagination.pageSize
  return filteredList.value.slice(start, start + pagination.pageSize)
})

const handleSearch = () => {
  pagination.page = 1
}

const resetSearch = () => {
  filters.name = ''
  filters.artifact_name = ''
  filters.source = ''
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
  dialogTitle.value = '新增材料记录'
  Object.assign(form, {
    artifact_id: null,
    name: '',
    source: '',
    usage: '',
    notes: ''
  })
  dialogVisible.value = true
}

const openEditDialog = (row) => {
  editingId.value = row.id
  dialogTitle.value = '编辑材料记录'
  Object.assign(form, {
    artifact_id: row.artifact_id,
    name: row.name,
    source: row.source,
    usage: row.usage,
    notes: row.notes
  })
  dialogVisible.value = true
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
  } catch (e) {
    return
  }
  
  try {
    let res
    if (editingId.value) {
      res = await materialApi.update(editingId.value, form)
    } else {
      res = await materialApi.create(form)
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
  ElMessageBox.confirm('确定要删除该材料记录吗？', '提示', { type: 'warning' }).then(async () => {
    try {
      const res = await materialApi.delete(row.id)
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
.stats-card,
.list-card {
  margin-bottom: 20px;
}

.card-header {
  font-weight: bold;
}

.stats-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stats-card :deep(.el-card__header) {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  border-bottom: none;
}

.stats-card :deep(.el-card__body) {
  padding: 30px 20px;
}

.stat-item {
  text-align: center;
  color: #fff;
}

.stat-value {
  font-size: 36px;
  font-weight: bold;
  margin-bottom: 10px;
}

.stat-label {
  font-size: 14px;
  opacity: 0.8;
}
</style>
