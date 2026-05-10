<template>
  <div class="page-container">
    <el-card class="filter-card">
      <el-form :inline="true" :model="filters" class="filter-form">
        <el-form-item label="文物名称">
          <el-input v-model="filters.artifact_name" placeholder="搜索文物名称" clearable />
        </el-form-item>
        <el-form-item label="阶段">
          <el-select v-model="filters.stage" placeholder="选择阶段" clearable style="width: 120px">
            <el-option label="修复前" value="before" />
            <el-option label="修复中" value="during" />
            <el-option label="修复后" value="after" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="filters.description" placeholder="搜索描述" clearable />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="resetSearch">重置</el-button>
          <el-button type="success" @click="openCreateDialog">
            <el-icon><Plus /></el-icon> 上传影像
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="gallery-card">
      <template #header>
        <div class="card-header">
          <span>影像资料库</span>
          <el-tag type="info">共 {{ filteredList.length }} 张影像</el-tag>
        </div>
      </template>
      <div v-loading="loading" class="gallery-container">
        <el-empty v-if="filteredList.length === 0" description="暂无影像资料" />
        <el-row v-else :gutter="20">
          <el-col :span="6" v-for="item in paginatedList" :key="item.id">
            <el-card class="image-card" shadow="hover" @click="previewImage(item)">
              <div class="image-wrapper">
                <div class="image-placeholder" v-if="!item.file_path">
                  <el-icon :size="48"><Picture /></el-icon>
                  <span class="placeholder-text">{{ stageLabel(item.stage) }}</span>
                </div>
                <img
                  v-else
                  :src="getImageSrc(item)"
                  :alt="item.description || '影像资料'"
                  @error="handleImageError($event)"
                  class="gallery-image"
                />
                <el-tag :type="stageType(item.stage)" size="small" class="stage-tag">
                  {{ stageLabel(item.stage) }}
                </el-tag>
              </div>
              <div class="image-info">
                <p class="artifact-name" @click.stop="goToArtifact(item.artifact_id)">
                  <el-icon><Collection /></el-icon>
                  {{ getArtifactName(item.artifact_id) }}
                </p>
                <p class="image-desc">{{ item.description || '暂无描述' }}</p>
                <div class="image-footer">
                  <span class="create-time">{{ item.created_at }}</span>
                  <div class="image-actions">
                    <el-button size="small" type="warning" link @click.stop="openEditDialog(item)">
                      编辑
                    </el-button>
                    <el-button size="small" type="danger" link @click.stop="handleDelete(item)">
                      删除
                    </el-button>
                  </div>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
        <el-pagination
          v-if="filteredList.length > pagination.pageSize"
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[8, 16, 24, 40]"
          :total="filteredList.length"
          layout="prev, pager, next, total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          style="margin-top: 20px; justify-content: center; display: flex;"
        />
      </div>
    </el-card>

    <el-image-viewer
      v-if="viewerVisible"
      :url-list="viewerUrlList"
      :initial-index="viewerIndex"
      @close="viewerVisible = false"
    />

    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form :model="form" ref="formRef" :rules="rules" label-width="80px">
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
        <el-form-item label="阶段" prop="stage">
          <el-select v-model="form.stage" style="width: 100%">
            <el-option label="修复前" value="before" />
            <el-option label="修复中" value="during" />
            <el-option label="修复后" value="after" />
          </el-select>
        </el-form-item>
        <el-form-item label="图片" v-if="!editingId">
          <el-upload
            :limit="1"
            :on-exceed="handleExceed"
            :auto-upload="false"
            :show-file-list="true"
            :on-change="handleFileChange"
            :on-remove="handleFileRemove"
            accept="image/*"
            ref="uploadRef"
          >
            <el-button type="primary" size="small">选择图片</el-button>
            <template #tip>
              <div class="el-upload__tip">支持 jpg、png、gif 格式</div>
            </template>
          </el-upload>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入描述（可选）" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { imageApi, artifactApi } from '../api'

const router = useRouter()

const loading = ref(false)
const submitting = ref(false)
const allImages = ref([])
const artifactList = ref([])
const artifactMap = ref({})
const uploadRef = ref(null)
const selectedFile = ref(null)

const filters = reactive({
  artifact_name: '',
  stage: '',
  description: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 8
})

const dialogVisible = ref(false)
const dialogTitle = ref('编辑影像资料')
const editingId = ref(null)
const formRef = ref(null)
const form = reactive({
  artifact_id: null,
  stage: 'before',
  description: ''
})

const viewerVisible = ref(false)
const viewerUrlList = ref([])
const viewerIndex = ref(0)

const rules = {
  artifact_id: [
    { required: true, message: '请选择文物', trigger: 'change' }
  ],
  stage: [
    { required: true, message: '请选择阶段', trigger: 'change' }
  ]
}

const stageLabel = (stage) => {
  const map = { before: '修复前', during: '修复中', after: '修复后' }
  return map[stage] || stage
}

const stageType = (stage) => {
  const map = { before: 'warning', during: 'primary', after: 'success' }
  return map[stage] || 'info'
}

const getArtifactName = (id) => {
  return artifactMap.value[id]?.name || '未知文物'
}

const getImageSrc = (item) => {
  if (!item.file_path) return ''
  if (item.file_path.startsWith('http')) return item.file_path
  return item.file_path
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
    const res = await imageApi.getList()
    if (res.code === 200) {
      allImages.value = (res.data || []).reverse()
    }
  } catch (e) {
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

const filteredList = computed(() => {
  let result = [...allImages.value]
  
  if (filters.artifact_name) {
    result = result.filter(item => {
      const name = artifactMap.value[item.artifact_id]?.name || ''
      return name.includes(filters.artifact_name)
    })
  }
  
  if (filters.stage) {
    result = result.filter(item => item.stage === filters.stage)
  }
  
  if (filters.description) {
    const keyword = filters.description.toLowerCase()
    result = result.filter(item =>
      (item.description || '').toLowerCase().includes(keyword)
    )
  }
  
  return result
})

const paginatedList = computed(() => {
  const start = (pagination.page - 1) * pagination.pageSize
  return filteredList.value.slice(start, start + pagination.pageSize)
})

const previewImage = (item) => {
  if (!item.file_path) {
    ElMessage.info('该影像暂无图片文件')
    return
  }
  
  const imagesWithFile = filteredList.value.filter(img => img.file_path)
  const index = imagesWithFile.findIndex(img => img.id === item.id)
  
  viewerUrlList.value = imagesWithFile.map(img => getImageSrc(img))
  viewerIndex.value = index >= 0 ? index : 0
  viewerVisible.value = true
}

const handleImageError = (event) => {
  const img = event.target
  img.style.display = 'none'
}

const handleSearch = () => {
  pagination.page = 1
}

const resetSearch = () => {
  filters.artifact_name = ''
  filters.stage = ''
  filters.description = ''
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
  if (artifactList.value.length === 0) {
    ElMessage.warning('请先创建文物档案')
    return
  }
  editingId.value = null
  dialogTitle.value = '上传影像'
  selectedFile.value = null
  Object.assign(form, {
    artifact_id: artifactList.value.length > 0 ? artifactList.value[0].id : null,
    stage: 'before',
    description: ''
  })
  dialogVisible.value = true
}

const openEditDialog = (row) => {
  editingId.value = row.id
  dialogTitle.value = '编辑影像资料'
  selectedFile.value = null
  Object.assign(form, {
    artifact_id: row.artifact_id,
    stage: row.stage,
    description: row.description || ''
  })
  dialogVisible.value = true
}

const handleFileChange = (file) => {
  selectedFile.value = file.raw
}

const handleFileRemove = () => {
  selectedFile.value = null
}

const handleExceed = () => {
  ElMessage.warning('只能选择一个图片文件')
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
  } catch (e) {
    return
  }
  
  submitting.value = true
  try {
    let res
    if (editingId.value) {
      res = await imageApi.update(editingId.value, form)
    } else {
      const formData = new FormData()
      formData.append('artifact_id', form.artifact_id)
      formData.append('stage', form.stage)
      if (form.description) {
        formData.append('description', form.description)
      }
      if (selectedFile.value) {
        formData.append('file', selectedFile.value)
      }
      res = await imageApi.create(formData)
    }
    
    if (res.code === 200) {
      ElMessage.success('保存成功')
      dialogVisible.value = false
      selectedFile.value = null
      if (uploadRef.value) {
        uploadRef.value.clearFiles()
      }
      loadData()
    }
  } catch (e) {
    ElMessage.error('保存失败')
  } finally {
    submitting.value = false
  }
}

const handleDelete = (row) => {
  ElMessageBox.confirm('确定要删除该影像吗？', '提示', { type: 'warning' }).then(async () => {
    try {
      const res = await imageApi.delete(row.id)
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
.gallery-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
}

.gallery-container {
  min-height: 300px;
}

.image-card {
  cursor: pointer;
  transition: transform 0.3s;
  margin-bottom: 20px;
}

.image-card:hover {
  transform: translateY(-5px);
}

.image-wrapper {
  position: relative;
  width: 100%;
  height: 180px;
  background: #f5f7fa;
  border-radius: 4px;
  overflow: hidden;
}

.image-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #909399;
  gap: 10px;
}

.placeholder-text {
  font-size: 14px;
}

.gallery-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.stage-tag {
  position: absolute;
  top: 8px;
  left: 8px;
}

.image-info {
  padding: 10px 0;
}

.artifact-name {
  font-size: 13px;
  color: #409EFF;
  margin-bottom: 5px;
  display: flex;
  align-items: center;
  gap: 4px;
  cursor: pointer;
}

.image-desc {
  font-size: 13px;
  color: #606266;
  line-height: 1.4;
  margin-bottom: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.image-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.create-time {
  font-size: 12px;
  color: #c0c4cc;
}

.image-actions {
  display: flex;
  gap: 5px;
}
</style>
