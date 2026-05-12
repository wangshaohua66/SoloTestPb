<template>
  <div class="page-container">
    <el-card class="filter-card">
      <el-form :inline="true" :model="filters" class="filter-form">
        <el-form-item label="文物名称">
          <el-input v-model="filters.artifact_name" placeholder="搜索文物名称" clearable />
        </el-form-item>
        <el-form-item label="目标关键字">
          <el-input v-model="filters.keyword" placeholder="搜索修复目标或方法" clearable />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="resetSearch">重置</el-button>
          <el-button type="success" @click="openCreateDialog">
            <el-icon><Plus /></el-icon> 新建计划
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="list-card">
      <el-table :data="tableData" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="artifact_name" label="文物名称" min-width="150">
          <template #default="scope">
            <el-button type="primary" link @click="goToArtifact(scope.row.artifact_id)">
              {{ getArtifactName(scope.row.artifact_id) }}
            </el-button>
          </template>
        </el-table-column>
        <el-table-column prop="goal" label="修复目标" min-width="200" show-overflow-tooltip />
        <el-table-column prop="method" label="修复方法" min-width="200" show-overflow-tooltip />
        <el-table-column prop="estimated_duration" label="预计工期" width="120" />
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="scope">
            <el-button size="small" type="primary" link @click="goToArtifact(scope.row.artifact_id)">
              查看详情
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
        :total="pagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
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
        <el-form-item label="修复目标" prop="goal">
          <el-input v-model="form.goal" type="textarea" :rows="2" placeholder="请输入修复目标" />
        </el-form-item>
        <el-form-item label="修复方法" prop="method">
          <el-input v-model="form.method" type="textarea" :rows="2" placeholder="请输入修复方法" />
        </el-form-item>
        <el-form-item label="使用材料">
          <el-input v-model="form.materials" type="textarea" :rows="2" placeholder="请输入使用材料" />
        </el-form-item>
        <el-form-item label="预计工期" prop="estimated_duration">
          <el-input v-model="form.estimated_duration" placeholder="如：15天 或 3个月" />
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
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { planApi, artifactApi } from '../api'

const router = useRouter()

const loading = ref(false)
const tableData = ref([])
const allPlans = ref([])
const artifactList = ref([])
const artifactMap = ref({})

const filters = reactive({
  artifact_name: '',
  keyword: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0,
  pages: 0
})

const dialogVisible = ref(false)
const dialogTitle = ref('编辑修复计划')
const editingId = ref(null)
const formRef = ref(null)
const form = reactive({
  artifact_id: null,
  goal: '',
  method: '',
  materials: '',
  estimated_duration: ''
})

const rules = {
  artifact_id: [
    { required: true, message: '请选择文物', trigger: 'change' }
  ],
  goal: [
    { required: true, message: '请输入修复目标', trigger: 'blur' },
    { min: 2, max: 500, message: '长度在 2 到 500 个字符', trigger: 'blur' }
  ],
  method: [
    { required: true, message: '请输入修复方法', trigger: 'blur' },
    { min: 2, max: 500, message: '长度在 2 到 500 个字符', trigger: 'blur' }
  ],
  estimated_duration: [
    { required: true, message: '请输入预计工期', trigger: 'blur' },
    { pattern: /^[\u4e00-\u9fa5a-zA-Z0-9]+$/, message: '请输入有效的工期描述', trigger: 'blur' }
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
    const res = await planApi.getList()
    if (res.code === 200) {
      allPlans.value = res.data || []
      filterAndPaginate()
    }
  } catch (e) {
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

const filterAndPaginate = () => {
  let filtered = [...allPlans.value]
  
  if (filters.artifact_name) {
    filtered = filtered.filter(item => {
      const name = artifactMap.value[item.artifact_id]?.name || ''
      return name.includes(filters.artifact_name)
    })
  }
  
  if (filters.keyword) {
    const keyword = filters.keyword.toLowerCase()
    filtered = filtered.filter(item =>
      (item.goal || '').toLowerCase().includes(keyword) ||
      (item.method || '').toLowerCase().includes(keyword)
    )
  }
  
  pagination.total = filtered.length
  pagination.pages = Math.ceil(filtered.length / pagination.pageSize)
  
  const start = (pagination.page - 1) * pagination.pageSize
  tableData.value = filtered.slice(start, start + pagination.pageSize)
}

const handleSearch = () => {
  pagination.page = 1
  filterAndPaginate()
}

const resetSearch = () => {
  filters.artifact_name = ''
  filters.keyword = ''
  pagination.page = 1
  filterAndPaginate()
}

const handleSizeChange = (size) => {
  pagination.pageSize = size
  pagination.page = 1
  filterAndPaginate()
}

const handleCurrentChange = (page) => {
  pagination.page = page
  filterAndPaginate()
}

const openCreateDialog = () => {
  editingId.value = null
  dialogTitle.value = '新建修复计划'
  Object.assign(form, {
    artifact_id: null,
    goal: '',
    method: '',
    materials: '',
    estimated_duration: ''
  })
  dialogVisible.value = true
}

const openEditDialog = (row) => {
  editingId.value = row.id
  dialogTitle.value = '编辑修复计划'
  Object.assign(form, {
    artifact_id: row.artifact_id,
    goal: row.goal,
    method: row.method,
    materials: row.materials,
    estimated_duration: row.estimated_duration
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
      res = await planApi.update(editingId.value, form)
    } else {
      res = await planApi.create(form)
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
  ElMessageBox.confirm('确定要删除该修复计划吗？', '提示', { type: 'warning' }).then(async () => {
    try {
      const res = await planApi.delete(row.id)
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
.list-card {
  margin-bottom: 20px;
}

.el-pagination {
  margin-top: 20px;
  justify-content: flex-end;
  display: flex;
}
</style>
