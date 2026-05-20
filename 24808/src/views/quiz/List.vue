<template>
  <div class="page-container">
    <div class="page-header">
      <h2 class="title">测验管理</h2>
      <div class="actions">
        <el-button type="primary" @click="handleGenerate">
          <el-icon><MagicStick /></el-icon>
          智能生成
        </el-button>
        <el-button type="success" @click="handleCreate">
          <el-icon><Plus /></el-icon>
          新建测验
        </el-button>
      </div>
    </div>

    <el-form :inline="true" :model="queryForm" class="search-form">
      <el-form-item label="关键词">
        <el-input v-model="queryForm.keyword" placeholder="请输入题目内容" clearable />
      </el-form-item>
      <el-form-item label="类型">
        <el-select v-model="queryForm.type" placeholder="请选择题型" clearable>
          <el-option label="单选题" value="single" />
          <el-option label="多选题" value="multiple" />
          <el-option label="判断题" value="judge" />
          <el-option label="填空题" value="fill" />
        </el-select>
      </el-form-item>
      <el-form-item label="难度">
        <el-select v-model="queryForm.difficulty" placeholder="请选择难度" clearable>
          <el-option label="简单" value="easy" />
          <el-option label="中等" value="medium" />
          <el-option label="困难" value="hard" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="handleSearch">
          <el-icon><Search /></el-icon>
          搜索
        </el-button>
        <el-button @click="handleReset">
          <el-icon><Refresh /></el-icon>
          重置
        </el-button>
      </el-form-item>
    </el-form>

    <el-table :data="quizList" v-loading="loading" stripe>
      <el-table-column type="selection" />
      <el-table-column label="题型" width="100">
        <template #default="{ row }">
          <el-tag :type="getTypeTagType(row.type)">
            {{ getTypeLabel(row.type) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="难度" width="100">
        <template #default="{ row }">
          <el-tag :type="getDifficultyTagType(row.difficulty)">
            {{ getDifficultyLabel(row.difficulty) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="title" label="题目内容" min-width="300" show-overflow-tooltip />
      <el-table-column prop="score" label="分值" width="80" />
      <el-table-column label="标签" width="150">
        <template #default="{ row }">
          <el-tag v-for="tag in row.tags" :key="tag" size="small" class="mr-1">
            {{ tag }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="createdAt" label="创建时间" width="180" />
      <el-table-column label="操作" width="150" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" size="small" link @click="handleEdit(row)">编辑</el-button>
          <el-button type="danger" size="small" link @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination-container">
      <el-pagination
        v-model:current-page="queryForm.page"
        v-model:page-size="queryForm.pageSize"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        :page-sizes="[10, 20, 50, 100]"
        @current-change="handlePageChange"
        @size-change="handleSizeChange"
      />
    </div>

    <el-dialog v-model="generateDialogVisible" title="智能生成测验" width="500px">
      <el-form :model="generateForm" label-width="100px">
        <el-form-item label="生成数量">
          <el-input-number v-model="generateForm.count" :min="1" :max="50" />
        </el-form-item>
        <el-form-item label="难度">
          <el-select v-model="generateForm.difficulty" placeholder="请选择难度" clearable>
            <el-option label="简单" value="easy" />
            <el-option label="中等" value="medium" />
            <el-option label="困难" value="hard" />
          </el-select>
        </el-form-item>
        <el-form-item label="题型">
          <el-select v-model="generateForm.type" placeholder="请选择题型" clearable>
            <el-option label="单选题" value="single" />
            <el-option label="多选题" value="multiple" />
            <el-option label="判断题" value="judge" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="generateDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleGenerateSubmit" :loading="generating">生成</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Refresh, MagicStick } from '@element-plus/icons-vue'
import { getQuizList, deleteQuiz, generateQuizzes } from '@/api/quiz'
import { logAction } from '@/utils/logger'
import type { Quiz, QuizQueryParams, QuizGenerateParams } from '@/types'

const router = useRouter()
const loading = ref(false)
const generating = ref(false)
const quizList = ref<Quiz[]>([])
const total = ref(0)
const generateDialogVisible = ref(false)

const queryForm = reactive<QuizQueryParams>({
  page: 1,
  pageSize: 10,
  keyword: '',
  type: '',
  difficulty: ''
})

const generateForm = reactive<QuizGenerateParams>({
  count: 10,
  difficulty: '',
  type: ''
})

function getTypeLabel(type: string): string {
  const map: Record<string, string> = {
    single: '单选题',
    multiple: '多选题',
    judge: '判断题',
    fill: '填空题'
  }
  return map[type] || type
}

function getTypeTagType(type: string): 'success' | 'warning' | 'info' | 'primary' {
  const map: Record<string, any> = {
    single: 'primary',
    multiple: 'success',
    judge: 'warning',
    fill: 'info'
  }
  return map[type] || 'info'
}

function getDifficultyLabel(difficulty: string): string {
  const map: Record<string, string> = {
    easy: '简单',
    medium: '中等',
    hard: '困难'
  }
  return map[difficulty] || difficulty
}

function getDifficultyTagType(difficulty: string): 'success' | 'warning' | 'danger' {
  const map: Record<string, any> = {
    easy: 'success',
    medium: 'warning',
    hard: 'danger'
  }
  return map[difficulty] || 'info'
}

async function loadData() {
  loading.value = true
  try {
    const result = await getQuizList(queryForm)
    quizList.value = result.list
    total.value = result.total
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  queryForm.page = 1
  loadData()
}

function handleReset() {
  queryForm.keyword = ''
  queryForm.type = ''
  queryForm.difficulty = ''
  handleSearch()
}

function handlePageChange() {
  loadData()
}

function handleSizeChange() {
  queryForm.page = 1
  loadData()
}

function handleCreate() {
  router.push('/quiz/create')
}

function handleEdit(row: Quiz) {
  router.push({ path: '/quiz/create', query: { id: row.id } })
}

async function handleDelete(row: Quiz) {
  try {
    await ElMessageBox.confirm(`确定要删除该题目吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await deleteQuiz(row.id)
    logAction('Quiz', 'delete', { id: row.id })
    ElMessage.success('删除成功')
    loadData()
  } catch (e) {
    // 用户取消
  }
}

function handleGenerate() {
  generateDialogVisible.value = true
}

async function handleGenerateSubmit() {
  generating.value = true
  try {
    const result = await generateQuizzes(generateForm)
    logAction('Quiz', 'generate', generateForm)
    ElMessage.success(`成功生成 ${result.length} 道题目`)
    generateDialogVisible.value = false
    loadData()
  } finally {
    generating.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>

<style lang="scss" scoped>
.pagination-container {
  margin-top: $spacing-md;
  display: flex;
  justify-content: flex-end;
}

.mr-1 {
  margin-right: $spacing-xs;
}
</style>
