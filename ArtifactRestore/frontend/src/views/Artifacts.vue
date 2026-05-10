<template>
  <div class="artifacts-container">
    <el-card class="search-card">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="关键词">
          <el-input
            v-model="searchForm.keyword"
            placeholder="搜索文物名称、年代、类别"
            clearable
            @keyup.enter="loadData"
            style="width: 300px"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">
            <el-icon><Search /></el-icon> 搜索
          </el-button>
          <el-button @click="resetSearch">
            <el-icon><Refresh /></el-icon> 重置
          </el-button>
          <el-button type="success" @click="openDialog()">
            <el-icon><Plus /></el-icon> 新建文物
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="table-card">
      <el-table :data="tableData" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="文物名称" min-width="150" />
        <el-table-column prop="era" label="年代" width="120" />
        <el-table-column prop="category" label="类别" width="100" />
        <el-table-column prop="material" label="材质" width="120" />
        <el-table-column prop="dimensions" label="尺寸" min-width="120" />
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="scope">
            <el-button size="small" type="primary" @click="viewDetail(scope.row)">
              <el-icon><View /></el-icon> 详情
            </el-button>
            <el-button size="small" type="warning" @click="openDialog(scope.row)">
              <el-icon><Edit /></el-icon> 编辑
            </el-button>
            <el-button size="small" type="danger" @click="handleDelete(scope.row)">
              <el-icon><Delete /></el-icon> 删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50]"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="loadData"
        @current-change="loadData"
        style="margin-top: 20px; text-align: right"
      />
    </el-card>

    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      @close="resetForm"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="文物名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入文物名称" />
        </el-form-item>
        <el-form-item label="年代">
          <el-input v-model="form.era" placeholder="请输入年代" />
        </el-form-item>
        <el-form-item label="类别">
          <el-input v-model="form.category" placeholder="请输入类别" />
        </el-form-item>
        <el-form-item label="尺寸">
          <el-input v-model="form.dimensions" placeholder="请输入尺寸" />
        </el-form-item>
        <el-form-item label="材质">
          <el-input v-model="form.material" placeholder="请输入材质" />
        </el-form-item>
        <el-form-item label="保存状态">
          <el-input v-model="form.preservation_status" type="textarea" :rows="3" placeholder="请输入保存状态" />
        </el-form-item>
        <el-form-item label="病害描述">
          <el-input v-model="form.disease_description" type="textarea" :rows="3" placeholder="请输入病害描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { artifactApi } from '../api'

const router = useRouter()

const loading = ref(false)
const tableData = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

const searchForm = reactive({
  keyword: ''
})

const dialogVisible = ref(false)
const dialogTitle = ref('新建文物')
const editingId = ref(null)
const formRef = ref(null)

const form = reactive({
  name: '',
  era: '',
  category: '',
  dimensions: '',
  material: '',
  preservation_status: '',
  disease_description: ''
})

const rules = {
  name: [
    { required: true, message: '请输入文物名称', trigger: 'blur' }
  ]
}

const loadData = async () => {
  loading.value = true
  try {
    const res = await artifactApi.getList({
      page: currentPage.value,
      per_page: pageSize.value,
      keyword: searchForm.keyword
    })

    if (res.code === 200) {
      tableData.value = res.data.items
      total.value = res.data.total
    }
  } catch (e) {
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

const resetSearch = () => {
  searchForm.keyword = ''
  currentPage.value = 1
  loadData()
}

const openDialog = (row = null) => {
  if (row) {
    dialogTitle.value = '编辑文物'
    editingId.value = row.id
    Object.assign(form, row)
  } else {
    dialogTitle.value = '新建文物'
    editingId.value = null
    resetForm()
  }
  dialogVisible.value = true
}

const resetForm = () => {
  form.name = ''
  form.era = ''
  form.category = ''
  form.dimensions = ''
  form.material = ''
  form.preservation_status = ''
  form.disease_description = ''
  if (formRef.value) {
    formRef.value.resetFields()
  }
}

const submitForm = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return

    try {
      let res
      if (editingId.value) {
        res = await artifactApi.update(editingId.value, form)
      } else {
        res = await artifactApi.create(form)
      }

      if (res.code === 200) {
        ElMessage.success(editingId.value ? '更新成功' : '创建成功')
        dialogVisible.value = false
        loadData()
      } else {
        ElMessage.error(res.message || '操作失败')
      }
    } catch (e) {
      ElMessage.error('操作失败')
    }
  })
}

const handleDelete = (row) => {
  ElMessageBox.confirm(`确定要删除文物"${row.name}"吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      const res = await artifactApi.delete(row.id)
      if (res.code === 200) {
        ElMessage.success('删除成功')
        loadData()
      } else {
        ElMessage.error(res.message || '删除失败')
      }
    } catch (e) {
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

const viewDetail = (row) => {
  router.push(`/artifacts/${row.id}`)
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.artifacts-container {
  padding: 10px;
}

.search-card {
  margin-bottom: 20px;
}

.table-card {
  margin-bottom: 20px;
}
</style>
