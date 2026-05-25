<template>
  <div class="tree-catalog">
    <div class="tree-header">
      <el-input
        v-model="filterText"
        placeholder="搜索分类名称"
        clearable
        size="small"
        :prefix-icon="Search"
      />
      <el-button type="primary" size="small" @click="handleAddRoot">
        <el-icon><Plus /></el-icon>
        添加根分类
      </el-button>
    </div>
    
    <div class="tree-content" ref="treeContentRef">
      <el-tree
        ref="treeRef"
        :data="treeData"
        node-key="id"
        default-expand-all
        :expand-on-click-node="false"
        :filter-node-method="filterNode"
        draggable
        allow-drag="allowDrag"
        allow-drop="allowDrop"
        @node-drop="handleNodeDrop"
      >
        <template #default="{ node, data }">
          <div class="custom-tree-node">
            <span class="node-label">{{ data.name }}</span>
            <span class="node-actions">
              <el-tooltip content="添加子分类" placement="top">
                <el-icon class="action-icon" @click.stop="handleAddChild(data)">
                  <Plus />
                </el-icon>
              </el-tooltip>
              <el-tooltip content="编辑" placement="top">
                <el-icon class="action-icon" @click.stop="handleEdit(data)">
                  <Edit />
                </el-icon>
              </el-tooltip>
              <el-tooltip content="删除" placement="top">
                <el-icon class="action-icon delete" @click.stop="handleDelete(data)">
                  <Delete />
                </el-icon>
              </el-tooltip>
            </span>
          </div>
        </template>
      </el-tree>
    </div>

    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="500px"
      @closed="resetForm"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="分类名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入分类名称" maxlength="50" show-word-limit />
        </el-form-item>
        <el-form-item label="描述">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            placeholder="请输入分类描述"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules, type TreeInstance } from 'element-plus'
import { Search, Plus, Edit, Delete } from '@element-plus/icons-vue'
import Sortable from 'sortablejs'
import type { CourseCatalog } from '@/types'
import { createCatalog, updateCatalog, deleteCatalog, updateCatalogSort } from '@/api/course'
import { logAction } from '@/utils/logger'

const props = defineProps<{
  data: CourseCatalog[]
}>()

const emit = defineEmits<{
  (e: 'update:data', value: CourseCatalog[]): void
  (e: 'node-click', node: CourseCatalog): void
  (e: 'refresh'): void
}>()

const treeRef = ref<TreeInstance>()
const treeContentRef = ref<HTMLElement>()
const filterText = ref('')
const dialogVisible = ref(false)
const formRef = ref<FormInstance>()
const form = ref<Partial<CourseCatalog>>({
  name: '',
  description: '',
  parentId: null
})
const isEdit = ref(false)
const currentNode = ref<CourseCatalog | null>(null)

const treeData = ref<CourseCatalog[]>([])
let sortableInstance: Sortable | null = null

const dialogTitle = computed(() => isEdit.value ? '编辑分类' : '添加分类')

const rules: FormRules = {
  name: [
    { required: true, message: '请输入分类名称', trigger: 'blur' },
    { min: 1, max: 50, message: '长度在 1 到 50 个字符', trigger: 'blur' }
  ]
}

watch(filterText, (val) => {
  treeRef.value?.filter(val)
})

watch(() => props.data, (newData) => {
  treeData.value = newData
}, { immediate: true, deep: true })

function filterNode(value: string, data: CourseCatalog): boolean {
  if (!value) return true
  return data.name.includes(value)
}

function allowDrag(draggingNode: any): boolean {
  return true
}

function allowDrop(draggingNode: any, dropNode: any, type: string): boolean {
  if (type === 'inner') {
    return true
  }
  return draggingNode.data.parentId === dropNode.data.parentId
}

function handleAddRoot() {
  isEdit.value = false
  currentNode.value = null
  form.value = {
    name: '',
    description: '',
    parentId: null,
    level: 1
  }
  dialogVisible.value = true
}

function handleAddChild(data: CourseCatalog) {
  isEdit.value = false
  currentNode.value = null
  form.value = {
    name: '',
    description: '',
    parentId: data.id,
    level: data.level + 1
  }
  dialogVisible.value = true
}

function handleEdit(data: CourseCatalog) {
  isEdit.value = true
  currentNode.value = data
  form.value = {
    id: data.id,
    name: data.name,
    description: data.description || '',
    parentId: data.parentId,
    level: data.level
  }
  dialogVisible.value = true
}

async function handleDelete(data: CourseCatalog) {
  try {
    await ElMessageBox.confirm(`确定要删除分类「${data.name}」吗？删除后子分类也将被删除。`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await deleteCatalog(data.id)
    logAction('CourseCatalog', 'delete', { id: data.id, name: data.name })
    ElMessage.success('删除成功')
    emit('refresh')
  } catch (e) {
    // 用户取消
  }
}

async function handleNodeDrop(draggingNode: any, dropNode: any, dropType: string) {
  const parentId = draggingNode.data.parentId
  
  let siblings: CourseCatalog[] = []
  if (parentId === null || parentId === undefined) {
    siblings = treeData.value
  } else {
    const parentNode = findNodeById(treeData.value, parentId)
    siblings = parentNode?.children || []
  }
  
  const sortItems = siblings.map((node, index) => ({
    id: node.id,
    sort: index
  }))
  
  try {
    await updateCatalogSort(sortItems)
    logAction('CourseCatalog', 'sort', { items: sortItems, parentId })
    emit('refresh')
  } catch (e) {
    ElMessage.error('排序更新失败')
  }
}

function findNodeById(tree: CourseCatalog[], id: string): CourseCatalog | null {
  for (const node of tree) {
    if (node.id === id) return node
    if (node.children && node.children.length > 0) {
      const found = findNodeById(node.children, id)
      if (found) return found
    }
  }
  return null
}

function flattenTree(tree: CourseCatalog[], result: CourseCatalog[] = []): CourseCatalog[] {
  for (const node of tree) {
    result.push(node)
    if (node.children && node.children.length > 0) {
      flattenTree(node.children, result)
    }
  }
  return result
}

async function handleSubmit() {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    try {
      if (isEdit.value && currentNode.value) {
        await updateCatalog(currentNode.value.id, form.value)
        logAction('CourseCatalog', 'update', form.value)
        ElMessage.success('更新成功')
      } else {
        await createCatalog(form.value)
        logAction('CourseCatalog', 'create', form.value)
        ElMessage.success('创建成功')
      }
      
      dialogVisible.value = false
      emit('refresh')
    } catch (e) {
      // 错误已在 request 中处理
    }
  })
}

function resetForm() {
  formRef.value?.resetFields()
  form.value = {
    name: '',
    description: '',
    parentId: null
  }
  isEdit.value = false
  currentNode.value = null
}

onMounted(() => {
  // 使用 Element Plus 自带的拖拽功能，不需要手动初始化 Sortable
})
</script>

<style lang="scss" scoped>
.tree-catalog {
  .tree-header {
    display: flex;
    gap: $spacing-md;
    margin-bottom: $spacing-md;
    align-items: center;
  }

  .tree-content {
    max-height: calc(100vh - 300px);
    overflow-y: auto;
    padding: $spacing-sm;
    background: #fafafa;
    border-radius: $border-radius-base;
  }

  .custom-tree-node {
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;
    padding-right: $spacing-sm;

    .node-label {
      flex: 1;
    }

    .node-actions {
      display: none;
      gap: $spacing-xs;

      .action-icon {
        font-size: 14px;
        cursor: pointer;
        color: $text-color-secondary;

        &:hover {
          color: $primary-color;
        }

        &.delete:hover {
          color: $danger-color;
        }
      }
    }

    &:hover .node-actions {
      display: flex;
    }
  }
}
</style>
