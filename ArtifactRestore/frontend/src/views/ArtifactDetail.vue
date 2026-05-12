<template>
  <div class="detail-container">
    <el-card class="breadcrumb-card">
      <el-breadcrumb separator="/">
        <el-breadcrumb-item :to="{ path: '/artifacts' }">文物档案</el-breadcrumb-item>
        <el-breadcrumb-item>文物详情</el-breadcrumb-item>
      </el-breadcrumb>
    </el-card>

    <el-tabs v-model="activeTab" class="detail-tabs" @tab-change="handleTabChange">
      <el-tab-pane label="基本信息" name="basic">
        <el-card class="info-card">
          <template #header>
            <div class="card-header">
              <span>文物基本信息</span>
              <el-button type="primary" size="small" @click="openBasicDialog">
                <el-icon><Edit /></el-icon> 编辑
              </el-button>
            </div>
          </template>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="文物名称">{{ artifact.name }}</el-descriptions-item>
            <el-descriptions-item label="年代">{{ artifact.era || '-' }}</el-descriptions-item>
            <el-descriptions-item label="类别">{{ artifact.category || '-' }}</el-descriptions-item>
            <el-descriptions-item label="尺寸">{{ artifact.dimensions || '-' }}</el-descriptions-item>
            <el-descriptions-item label="材质">{{ artifact.material || '-' }}</el-descriptions-item>
            <el-descriptions-item label="创建时间">{{ artifact.created_at }}</el-descriptions-item>
            <el-descriptions-item label="保存状态" :span="2">
              {{ artifact.preservation_status || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="病害描述" :span="2">
              {{ artifact.disease_description || '-' }}
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="修复计划" name="plans">
        <el-card class="info-card">
          <template #header>
            <div class="card-header">
              <span>修复计划</span>
              <el-button type="success" size="small" @click="openPlanDialog">
                <el-icon><Plus /></el-icon> 添加计划
              </el-button>
            </div>
          </template>
          <el-table :data="plans" v-loading="loading.plans" stripe>
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="goal" label="修复目标" min-width="200" />
            <el-table-column prop="method" label="修复方法" min-width="200" />
            <el-table-column prop="estimated_duration" label="预计工期" width="120" />
            <el-table-column prop="created_at" label="创建时间" width="180" />
            <el-table-column label="操作" width="150">
              <template #default="scope">
                <el-button size="small" type="warning" @click="openPlanDialog(scope.row)">编辑</el-button>
                <el-button size="small" type="danger" @click="deletePlan(scope.row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="过程记录" name="processes">
        <el-card class="info-card">
          <template #header>
            <div class="card-header">
              <span>修复过程记录</span>
              <el-button type="success" size="small" @click="openProcessDialog">
                <el-icon><Plus /></el-icon> 添加记录
              </el-button>
            </div>
          </template>
          <el-table :data="processes" v-loading="loading.processes" stripe>
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="record_time" label="记录时间" width="180" />
            <el-table-column prop="operation_steps" label="操作步骤" min-width="200" />
            <el-table-column prop="tools" label="工具设备" width="150" />
            <el-table-column label="操作" width="150">
              <template #default="scope">
                <el-button size="small" type="warning" @click="openProcessDialog(scope.row)">编辑</el-button>
                <el-button size="small" type="danger" @click="deleteProcess(scope.row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="影像管理" name="images">
        <el-card class="info-card">
          <template #header>
            <div class="card-header">
              <span>影像资料</span>
              <el-button type="success" size="small" @click="openImageDialog">
                <el-icon><Plus /></el-icon> 添加影像
              </el-button>
            </div>
          </template>
          <el-row :gutter="20">
            <el-col :span="24" v-for="stage in imageStages" :key="stage.value">
              <h3 class="stage-title">{{ stage.label }}</h3>
              <el-empty v-if="getImagesByStage(stage.value).length === 0" description="暂无影像" :image-size="80" />
              <el-row :gutter="20" v-else>
                <el-col :span="8" v-for="image in getImagesByStage(stage.value)" :key="image.id">
                  <el-card class="image-card" shadow="hover">
                    <div class="image-wrapper" @click="previewImage(image)">
                      <div class="image-placeholder" v-if="!image.file_path">
                        <el-icon :size="60"><Picture /></el-icon>
                        <span>{{ image.description || '影像记录' }}</span>
                      </div>
                      <img
                        v-else
                        :src="getImageSrc(image)"
                        class="image-preview"
                        @error="handleImageError($event, image)"
                      />
                      <div class="image-overlay">
                        <el-icon :size="32"><ZoomIn /></el-icon>
                        <span>点击放大查看</span>
                      </div>
                    </div>
                    <div class="image-info">
                      <p>{{ image.description || '-' }}</p>
                      <div class="image-actions">
                        <el-button size="small" type="danger" link @click="deleteImage(image)">删除</el-button>
                      </div>
                    </div>
                  </el-card>
                </el-col>
              </el-row>
            </el-col>
          </el-row>
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="材料管理" name="materials">
        <el-card class="info-card">
          <template #header>
            <div class="card-header">
              <span>材料使用记录</span>
              <el-button type="success" size="small" @click="openMaterialDialog">
                <el-icon><Plus /></el-icon> 添加材料
              </el-button>
            </div>
          </template>
          <el-table :data="materials" v-loading="loading.materials" stripe>
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="name" label="材料名称" min-width="150" />
            <el-table-column prop="source" label="材料来源" min-width="150" />
            <el-table-column prop="usage" label="用量" width="120" />
            <el-table-column prop="notes" label="备注" min-width="150" />
            <el-table-column label="操作" width="150">
              <template #default="scope">
                <el-button size="small" type="warning" @click="openMaterialDialog(scope.row)">编辑</el-button>
                <el-button size="small" type="danger" @click="deleteMaterial(scope.row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>
    </el-tabs>

    <el-image-viewer
      v-if="viewerVisible"
      :url-list="viewerUrlList"
      :initial-index="viewerIndex"
      @close="viewerVisible = false"
    />

    <el-dialog
      v-model="basicDialogVisible"
      title="编辑文物信息"
      width="600px"
    >
      <el-form :model="basicForm" ref="basicFormRef" :rules="basicRules" label-width="100px">
        <el-form-item label="文物名称" prop="name">
          <el-input v-model="basicForm.name" placeholder="请输入文物名称" />
        </el-form-item>
        <el-form-item label="年代" prop="era">
          <el-input v-model="basicForm.era" placeholder="如：商代、清代康熙年间" />
        </el-form-item>
        <el-form-item label="类别" prop="category">
          <el-select v-model="basicForm.category" placeholder="请选择类别" style="width: 100%" clearable>
            <el-option label="青铜器" value="青铜器" />
            <el-option label="瓷器" value="瓷器" />
            <el-option label="书画" value="书画" />
            <el-option label="玉器" value="玉器" />
            <el-option label="陶器" value="陶器" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>
        <el-form-item label="尺寸" prop="dimensions">
          <el-input v-model="basicForm.dimensions" placeholder="如：高25cm、宽18cm" />
        </el-form-item>
        <el-form-item label="材质" prop="material">
          <el-input v-model="basicForm.material" placeholder="请输入材质" />
        </el-form-item>
        <el-form-item label="保存状态">
          <el-input v-model="basicForm.preservation_status" type="textarea" :rows="3" placeholder="请输入保存状态" />
        </el-form-item>
        <el-form-item label="病害描述">
          <el-input v-model="basicForm.disease_description" type="textarea" :rows="3" placeholder="请输入病害描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="basicDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveBasicInfo">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="planDialogVisible"
      :title="planDialogTitle"
      width="600px"
    >
      <el-form :model="planForm" ref="planFormRef" :rules="planRules" label-width="100px">
        <el-form-item label="修复目标" prop="goal">
          <el-input v-model="planForm.goal" type="textarea" :rows="2" placeholder="请输入修复目标" />
        </el-form-item>
        <el-form-item label="修复方法" prop="method">
          <el-input v-model="planForm.method" type="textarea" :rows="2" placeholder="请输入修复方法" />
        </el-form-item>
        <el-form-item label="使用材料">
          <el-input v-model="planForm.materials" type="textarea" :rows="2" placeholder="请输入使用材料" />
        </el-form-item>
        <el-form-item label="预计工期" prop="estimated_duration">
          <el-input v-model="planForm.estimated_duration" placeholder="如：15天、3个月" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="planDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="savePlan">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="processDialogVisible"
      :title="processDialogTitle"
      width="600px"
    >
      <el-form :model="processForm" ref="processFormRef" :rules="processRules" label-width="100px">
        <el-form-item label="记录时间" prop="record_time">
          <el-date-picker
            v-model="processForm.record_time"
            type="datetime"
            placeholder="选择记录时间"
            value-format="YYYY-MM-DD HH:mm:ss"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="操作步骤" prop="operation_steps">
          <el-input v-model="processForm.operation_steps" type="textarea" :rows="3" placeholder="请输入操作步骤" />
        </el-form-item>
        <el-form-item label="使用材料">
          <el-input v-model="processForm.used_materials" type="textarea" :rows="2" placeholder="请输入使用材料" />
        </el-form-item>
        <el-form-item label="工具设备">
          <el-input v-model="processForm.tools" placeholder="如：刷子、放大镜、吹风机等" />
        </el-form-item>
        <el-form-item label="遇到问题">
          <el-input v-model="processForm.problems" type="textarea" :rows="2" placeholder="请输入遇到的问题" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="processDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveProcess">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="imageDialogVisible"
      title="添加影像资料"
      width="500px"
    >
      <el-form :model="imageForm" ref="imageFormRef" :rules="imageRules" label-width="100px">
        <el-form-item label="阶段" prop="stage">
          <el-select v-model="imageForm.stage" style="width: 100%">
            <el-option label="修复前" value="before" />
            <el-option label="修复中" value="during" />
            <el-option label="修复后" value="after" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="imageForm.description" type="textarea" :rows="2" placeholder="请输入描述" />
        </el-form-item>
        <el-form-item label="上传文件">
          <el-upload
            :auto-upload="false"
            :on-change="handleFileChange"
            :limit="1"
            accept="image/*"
          >
            <el-button type="primary">选择文件</el-button>
            <template #tip>
              <div class="el-upload__tip">支持 jpg/png/gif 格式</div>
            </template>
          </el-upload>
          <div v-if="imageForm.fileName" class="file-name">{{ imageForm.fileName }}</div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="imageDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveImage">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="materialDialogVisible"
      :title="materialDialogTitle"
      width="600px"
    >
      <el-form :model="materialForm" ref="materialFormRef" :rules="materialRules" label-width="100px">
        <el-form-item label="材料名称" prop="name">
          <el-input v-model="materialForm.name" placeholder="请输入材料名称" />
        </el-form-item>
        <el-form-item label="材料来源">
          <el-input v-model="materialForm.source" placeholder="如：供应商A、自制等" />
        </el-form-item>
        <el-form-item label="用量" prop="usage">
          <el-input v-model="materialForm.usage" placeholder="如：50ml、100g、3块" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="materialForm.notes" type="textarea" :rows="2" placeholder="请输入备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="materialDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveMaterial">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { artifactApi, planApi, processApi, imageApi, materialApi } from '../api'

const route = useRoute()
const artifactId = route.params.id

const activeTab = ref('basic')

const loading = reactive({
  plans: false,
  processes: false,
  images: false,
  materials: false
})

const loadedTabs = ref(new Set(['basic']))

const artifact = ref({})
const plans = ref([])
const processes = ref([])
const images = ref([])
const materials = ref([])

const imageStages = [
  { label: '修复前', value: 'before' },
  { label: '修复中', value: 'during' },
  { label: '修复后', value: 'after' }
]

const viewerVisible = ref(false)
const viewerUrlList = ref([])
const viewerIndex = ref(0)

const basicDialogVisible = ref(false)
const basicFormRef = ref(null)
const basicForm = reactive({
  name: '',
  era: '',
  category: '',
  dimensions: '',
  material: '',
  preservation_status: '',
  disease_description: ''
})

const planDialogVisible = ref(false)
const planDialogTitle = ref('添加修复计划')
const planFormRef = ref(null)
const editingPlanId = ref(null)
const planForm = reactive({
  goal: '',
  method: '',
  materials: '',
  estimated_duration: ''
})

const processDialogVisible = ref(false)
const processDialogTitle = ref('添加过程记录')
const processFormRef = ref(null)
const editingProcessId = ref(null)
const processForm = reactive({
  operation_steps: '',
  used_materials: '',
  tools: '',
  problems: '',
  record_time: ''
})

const imageDialogVisible = ref(false)
const imageFormRef = ref(null)
const imageFile = ref(null)
const imageForm = reactive({
  stage: 'before',
  description: '',
  fileName: ''
})

const materialDialogVisible = ref(false)
const materialDialogTitle = ref('添加材料记录')
const materialFormRef = ref(null)
const editingMaterialId = ref(null)
const materialForm = reactive({
  name: '',
  source: '',
  usage: '',
  notes: ''
})

const basicRules = {
  name: [
    { required: true, message: '请输入文物名称', trigger: 'blur' },
    { min: 1, max: 100, message: '长度在 1 到 100 个字符', trigger: 'blur' }
  ],
  era: [
    { required: true, message: '请输入年代', trigger: 'blur' }
  ],
  category: [
    { required: true, message: '请选择类别', trigger: 'change' }
  ],
  dimensions: [
    { pattern: /^[\u4e00-\u9fa5a-zA-Z0-9\s、,.，。]*$/, message: '尺寸格式不正确', trigger: 'blur' }
  ]
}

const planRules = {
  goal: [
    { required: true, message: '请输入修复目标', trigger: 'blur' },
    { min: 2, max: 500, message: '长度在 2 到 500 个字符', trigger: 'blur' }
  ],
  method: [
    { required: true, message: '请输入修复方法', trigger: 'blur' },
    { min: 2, max: 500, message: '长度在 2 到 500 个字符', trigger: 'blur' }
  ],
  estimated_duration: [
    { required: true, message: '请输入预计工期', trigger: 'blur' }
  ]
}

const processRules = {
  operation_steps: [
    { required: true, message: '请输入操作步骤', trigger: 'blur' },
    { min: 2, max: 1000, message: '长度在 2 到 1000 个字符', trigger: 'blur' }
  ],
  record_time: [
    { required: true, message: '请选择记录时间', trigger: 'change' }
  ]
}

const imageRules = {
  stage: [
    { required: true, message: '请选择阶段', trigger: 'change' }
  ]
}

const materialRules = {
  name: [
    { required: true, message: '请输入材料名称', trigger: 'blur' },
    { min: 1, max: 100, message: '长度在 1 到 100 个字符', trigger: 'blur' }
  ],
  usage: [
    { required: true, message: '请输入用量', trigger: 'blur' }
  ]
}

const getImagesByStage = (stage) => {
  return images.value.filter(img => img.stage === stage)
}

const getImageSrc = (image) => {
  if (!image.file_path) return ''
  if (image.file_path.startsWith('http')) return image.file_path
  return image.file_path
}

const handleTabChange = (tabName) => {
  if (loadedTabs.value.has(tabName)) {
    return
  }
  
  switch (tabName) {
    case 'plans':
      loadPlans()
      break
    case 'processes':
      loadProcesses()
      break
    case 'images':
      loadImages()
      break
    case 'materials':
      loadMaterials()
      break
  }
  
  loadedTabs.value.add(tabName)
}

const loadArtifact = async () => {
  try {
    const res = await artifactApi.getDetail(artifactId)
    if (res.code === 200) {
      artifact.value = res.data
    }
  } catch (e) {
    ElMessage.error('加载文物信息失败')
  }
}

const loadPlans = async () => {
  if (loadedTabs.value.has('plans')) {
    return
  }
  loading.plans = true
  try {
    const res = await planApi.getList({ artifact_id: artifactId })
    if (res.code === 200) {
      plans.value = res.data
    }
  } catch (e) {
    ElMessage.error('加载修复计划失败')
  } finally {
    loading.plans = false
  }
}

const loadProcesses = async () => {
  if (loadedTabs.value.has('processes')) {
    return
  }
  loading.processes = true
  try {
    const res = await processApi.getList({ artifact_id: artifactId })
    if (res.code === 200) {
      processes.value = res.data
    }
  } catch (e) {
    ElMessage.error('加载过程记录失败')
  } finally {
    loading.processes = false
  }
}

const loadImages = async () => {
  if (loadedTabs.value.has('images')) {
    return
  }
  loading.images = true
  try {
    const res = await imageApi.getList({ artifact_id: artifactId })
    if (res.code === 200) {
      images.value = res.data
    }
  } catch (e) {
    ElMessage.error('加载影像资料失败')
  } finally {
    loading.images = false
  }
}

const loadMaterials = async () => {
  if (loadedTabs.value.has('materials')) {
    return
  }
  loading.materials = true
  try {
    const res = await materialApi.getList({ artifact_id: artifactId })
    if (res.code === 200) {
      materials.value = res.data
    }
  } catch (e) {
    ElMessage.error('加载材料记录失败')
  } finally {
    loading.materials = false
  }
}

const previewImage = (item) => {
  if (!item.file_path) {
    ElMessage.info('该影像暂无图片文件')
    return
  }
  
  const imagesWithFile = images.value.filter(img => img.file_path && img.stage === item.stage)
  const index = imagesWithFile.findIndex(img => img.id === item.id)
  
  viewerUrlList.value = imagesWithFile.map(img => getImageSrc(img))
  viewerIndex.value = index >= 0 ? index : 0
  viewerVisible.value = true
}

const handleImageError = (event, item) => {
  ElMessage.warning('图片加载失败')
}

const openBasicDialog = () => {
  Object.assign(basicForm, artifact.value)
  basicDialogVisible.value = true
}

const saveBasicInfo = async () => {
  try {
    await basicFormRef.value.validate()
    const res = await artifactApi.update(artifactId, basicForm)
    if (res.code === 200) {
      ElMessage.success('保存成功')
      basicDialogVisible.value = false
      loadArtifact()
    } else {
      ElMessage.error(res.message || '保存失败')
    }
  } catch (e) {
    if (e !== false) {
      ElMessage.error('保存失败')
    }
  }
}

const openPlanDialog = (row = null) => {
  if (row) {
    planDialogTitle.value = '编辑修复计划'
    editingPlanId.value = row.id
    Object.assign(planForm, row)
  } else {
    planDialogTitle.value = '添加修复计划'
    editingPlanId.value = null
    Object.assign(planForm, { goal: '', method: '', materials: '', estimated_duration: '' })
  }
  planDialogVisible.value = true
}

const savePlan = async () => {
  try {
    await planFormRef.value.validate()
    let res
    if (editingPlanId.value) {
      res = await planApi.update(editingPlanId.value, planForm)
    } else {
      res = await planApi.create({ ...planForm, artifact_id: artifactId })
    }
    if (res.code === 200) {
      ElMessage.success('保存成功')
      planDialogVisible.value = false
      if (loadedTabs.value.has('plans')) {
        loadPlans()
      }
    }
  } catch (e) {
    if (e !== false) {
      ElMessage.error('保存失败')
    }
  }
}

const deletePlan = (row) => {
  ElMessageBox.confirm('确定要删除该修复计划吗？', '提示', { type: 'warning' }).then(async () => {
    const res = await planApi.delete(row.id)
    if (res.code === 200) {
      ElMessage.success('删除成功')
      loadPlans()
    }
  }).catch(() => {})
}

const openProcessDialog = (row = null) => {
  if (row) {
    processDialogTitle.value = '编辑过程记录'
    editingProcessId.value = row.id
    Object.assign(processForm, row)
  } else {
    processDialogTitle.value = '添加过程记录'
    editingProcessId.value = null
    Object.assign(processForm, { operation_steps: '', used_materials: '', tools: '', problems: '', record_time: '' })
  }
  processDialogVisible.value = true
}

const saveProcess = async () => {
  try {
    await processFormRef.value.validate()
    let res
    if (editingProcessId.value) {
      res = await processApi.update(editingProcessId.value, processForm)
    } else {
      res = await processApi.create({ ...processForm, artifact_id: artifactId })
    }
    if (res.code === 200) {
      ElMessage.success('保存成功')
      processDialogVisible.value = false
      if (loadedTabs.value.has('processes')) {
        loadProcesses()
      }
    }
  } catch (e) {
    if (e !== false) {
      ElMessage.error('保存失败')
    }
  }
}

const deleteProcess = (row) => {
  ElMessageBox.confirm('确定要删除该过程记录吗？', '提示', { type: 'warning' }).then(async () => {
    const res = await processApi.delete(row.id)
    if (res.code === 200) {
      ElMessage.success('删除成功')
      loadProcesses()
    }
  }).catch(() => {})
}

const handleFileChange = (file) => {
  imageFile.value = file.raw
  imageForm.fileName = file.name
}

const saveImage = async () => {
  try {
    const formData = new FormData()
    formData.append('artifact_id', artifactId)
    formData.append('stage', imageForm.stage)
    formData.append('description', imageForm.description)
    if (imageFile.value) {
      formData.append('file', imageFile.value)
    }

    const res = await imageApi.create(formData)
    if (res.code === 200) {
      ElMessage.success('保存成功')
      imageDialogVisible.value = false
      imageFile.value = null
      imageForm.fileName = ''
      if (loadedTabs.value.has('images')) {
        loadImages()
      }
    }
  } catch (e) {
    ElMessage.error('保存失败')
  }
}

const deleteImage = (row) => {
  ElMessageBox.confirm('确定要删除该影像吗？', '提示', { type: 'warning' }).then(async () => {
    const res = await imageApi.delete(row.id)
    if (res.code === 200) {
      ElMessage.success('删除成功')
      loadImages()
    }
  }).catch(() => {})
}

const openMaterialDialog = (row = null) => {
  if (row) {
    materialDialogTitle.value = '编辑材料记录'
    editingMaterialId.value = row.id
    Object.assign(materialForm, row)
  } else {
    materialDialogTitle.value = '添加材料记录'
    editingMaterialId.value = null
    Object.assign(materialForm, { name: '', source: '', usage: '', notes: '' })
  }
  materialDialogVisible.value = true
}

const saveMaterial = async () => {
  try {
    await materialFormRef.value.validate()
    let res
    if (editingMaterialId.value) {
      res = await materialApi.update(editingMaterialId.value, materialForm)
    } else {
      res = await materialApi.create({ ...materialForm, artifact_id: artifactId })
    }
    if (res.code === 200) {
      ElMessage.success('保存成功')
      materialDialogVisible.value = false
      if (loadedTabs.value.has('materials')) {
        loadMaterials()
      }
    }
  } catch (e) {
    if (e !== false) {
      ElMessage.error('保存失败')
    }
  }
}

const deleteMaterial = (row) => {
  ElMessageBox.confirm('确定要删除该材料记录吗？', '提示', { type: 'warning' }).then(async () => {
    const res = await materialApi.delete(row.id)
    if (res.code === 200) {
      ElMessage.success('删除成功')
      loadMaterials()
    }
  }).catch(() => {})
}

onMounted(() => {
  loadArtifact()
})
</script>

<style scoped>
.detail-container {
  padding: 10px;
}

.breadcrumb-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.info-card {
  margin-bottom: 20px;
}

.stage-title {
  margin: 20px 0 15px;
  font-size: 16px;
  font-weight: bold;
  color: #303133;
}

.image-card {
  margin-bottom: 20px;
}

.image-wrapper {
  position: relative;
  height: 150px;
  background: #f5f7fa;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  cursor: pointer;
}

.image-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #909399;
  gap: 10px;
}

.image-preview {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s;
}

.image-wrapper:hover .image-preview {
  transform: scale(1.05);
}

.image-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #fff;
  opacity: 0;
  transition: opacity 0.3s;
  gap: 10px;
}

.image-wrapper:hover .image-overlay {
  opacity: 1;
}

.image-info {
  padding: 10px 0;
}

.image-info p {
  margin: 0;
  font-size: 14px;
  color: #606266;
  line-height: 1.5;
}

.image-actions {
  margin-top: 10px;
  text-align: right;
}

.file-name {
  margin-top: 10px;
  font-size: 14px;
  color: #409EFF;
}
</style>
