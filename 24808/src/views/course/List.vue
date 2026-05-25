<template>
  <div class="page-container">
    <div class="page-header">
      <h2 class="title">课程列表</h2>
      <div class="actions">
        <el-button type="primary" @click="handleCreate">
          <el-icon><Plus /></el-icon>
          新建课程
        </el-button>
      </div>
    </div>

    <el-form :inline="true" :model="queryForm" class="search-form">
      <el-form-item label="关键词">
        <el-input v-model="queryForm.keyword" placeholder="请输入课程名称" clearable />
      </el-form-item>
      <el-form-item label="分类">
        <el-cascader
          v-model="queryForm.catalogId"
          :options="catalogOptions"
          :props="{ value: 'id', label: 'name', children: 'children' }"
          placeholder="请选择分类"
          clearable
          filterable
        />
      </el-form-item>
      <el-form-item label="状态">
        <el-select v-model="queryForm.status" placeholder="请选择状态" clearable>
          <el-option
          v-for="item in statusOptions" :key="item.value" :label="item.label" :value="item.value" />
        </el-select>
      </el-form-item>
      <el-form-item label="难度">
        <el-select v-model="queryForm.difficulty" placeholder="请选择难度" clearable>
          <el-option label="初级" value="beginner" />
          <el-option label="中级" value="intermediate" />
          <el-option label="高级" value="advanced" />
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

    <el-table :data="tableData" v-loading="loading" stripe>
      <el-table-column type="selection" />
      <el-table-column prop="coverImage" label="封面" width="120">
        <template #default="{ row }">
          <el-image :src="row.coverImage" style="width: 100px; height: 60px;" fit="cover" />
        </template>
      </el-table-column>
      <el-table-column prop="title" label="课程名称" min-width="200">
        <template #default="{ row }">
          <div class="text-ellipsis" :title="row.title">{{ row.title }}</div>
        </template>
      </el-table-column>
      <el-table-column prop="teacherName" label="讲师" width="100" />
      <el-table-column prop="catalogName" label="分类" width="120" />
      <el-table-column label="价格" width="100">
        <template #default="{ row }">
          <span v-if="row.isFree" class="free-tag">免费</span>
          <span v-else class="price">¥{{ row.price }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="studentCount" label="学习人数" width="100" />
      <el-table-column prop="rating" label="评分" width="120">
        <template #default="{ row }">
          <el-rate v-model="row.rating" disabled show-score />
        </template>
      </el-table-column>
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="StatusMap[row.status]?.type">
            {{ StatusMap[row.status]?.label }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="updatedAt" label="更新时间" width="180" />
      <el-table-column label="操作" width="280" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" size="small" link @click="handleEdit(row)">编辑</el-button>
          <el-button type="success" size="small" link @click="handleChapters(row)">章节</el-button>
          <el-dropdown @command="(cmd) => handleStatusCommand(cmd, row)">
            <el-button type="primary" size="small" link>
              更多
              <el-icon><CaretBottom /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item :disabled="row.status === 'pending'" command="submit">提交审核</el-dropdown-item>
                <el-dropdown-item :disabled="row.status !== 'pending'" command="publish">发布</el-dropdown-item>
                <el-dropdown-item :disabled="row.status !== 'published'" command="offline">下线</el-dropdown-item>
                <el-dropdown-item divided command="delete" class="text-red-600">删除</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
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
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Refresh, CaretBottom } from '@element-plus/icons-vue'
import { useCourseStore } from '@/store/modules/course'
import { getCourseList, deleteCourse, submitReview, publishCourse, offlineCourse } from '@/api/course'
import { StatusMap, type Status, type Course, type CourseCatalog } from '@/types'
import { logAction } from '@/utils/logger'
import { mockCourses, mockCatalogTree } from '@/mock'

const router = useRouter()
const courseStore = useCourseStore()

const loading = ref(false)
const tableData = ref<Course[]>([])
const total = ref(0)
const catalogTree = ref<CourseCatalog[]>([])

const queryForm = reactive({
  page: 1,
  pageSize: 10,
  keyword: '',
  catalogId: '',
  status: '',
  difficulty: ''
})

const statusOptions = computed(() => {
  return Object.entries(StatusMap).map(([value, config]) => ({
    value,
    label: config.label
  }))
})

const catalogOptions = computed(() => catalogTree.value)

async function loadData() {
  loading.value = true
  try {
    const result = await getCourseList(queryForm)
    tableData.value = result.list
    total.value = result.total
  } catch (e) {
    tableData.value = mockCourses
    total.value = mockCourses.length
  } finally {
    loading.value = false
  }
}

async function loadCatalog() {
  try {
    catalogTree.value = await courseStore.loadCatalogTree()
  } catch (e) {
    catalogTree.value = mockCatalogTree
  }
}

function handleSearch() {
  queryForm.page = 1
  loadData()
}

function handleReset() {
  queryForm.keyword = ''
  queryForm.catalogId = ''
  queryForm.status = ''
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
  router.push('/course/create')
}

function handleEdit(row: Course) {
  router.push(`/course/edit/${row.id}`)
}

function handleChapters(row: Course) {
  router.push(`/chapter/list/${row.id}`)
}

async function handleStatusCommand(command: string, row: Course) {
  try {
    switch (command) {
      case 'submit':
        await ElMessageBox.confirm(`确定要提交「${row.title}」审核吗？`, '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        await submitReview(row.id)
        logAction('Course', 'submitReview', { id: row.id, title: row.title })
        ElMessage.success('提交成功')
        break
      case 'publish':
        await ElMessageBox.confirm(`确定要发布「${row.title}」吗？`, '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        await publishCourse(row.id)
        logAction('Course', 'publish', { id: row.id, title: row.title })
        ElMessage.success('发布成功')
        break
      case 'offline':
        const { value: reason } = await ElMessageBox.prompt('请输入下线原因', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          inputValidator: (value) => {
            if (!value) return '请输入下线原因'
            return true
          }
        })
        await offlineCourse(row.id, reason)
        logAction('Course', 'offline', { id: row.id, title: row.title, reason })
        ElMessage.success('下线成功')
        break
      case 'delete':
        await ElMessageBox.confirm(`确定要删除「${row.title}」吗？`, '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        await deleteCourse(row.id)
        logAction('Course', 'delete', { id: row.id, title: row.title })
        ElMessage.success('删除成功')
        break
    }
    loadData()
  } catch (e) {
    // 用户取消或错误已处理
  }
}

onMounted(() => {
  loadCatalog()
  loadData()
})
</script>

<style lang="scss" scoped>
.free-tag {
  color: $success-color;
  font-weight: 600;
}

.price {
  color: $danger-color;
  font-weight: 600;
}

.pagination-container {
  margin-top: $spacing-md;
  display: flex;
  justify-content: flex-end;
}
</style>
