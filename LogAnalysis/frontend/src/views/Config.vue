<template>
  <div class="config">
    <el-tabs v-model="activeTab">
      <el-tab-pane label="日志来源" name="sources">
        <el-card>
          <template #header>
            <div class="header-actions">
              <span>日志来源配置</span>
              <div class="actions">
                <el-button type="primary" @click="openSourceDialog">新增来源</el-button>
                <el-button @click="loadSources">刷新</el-button>
              </div>
            </div>
          </template>

          <el-table :data="sources" style="width: 100%">
            <el-table-column prop="id" label="ID" width="80"></el-table-column>
            <el-table-column prop="name" label="名称"></el-table-column>
            <el-table-column prop="source_type" label="类型" width="120">
              <template #default="{ row }">
                <el-tag size="small">{{ getSourceTypeName(row.source_type) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="配置" min-width="200">
              <template #default="{ row }">
                <el-popover placement="top" width="300" trigger="hover">
                  <template #reference>
                    <el-link type="primary">查看配置</el-link>
                  </template>
                  <pre>{{ formatConfig(row.config) }}</pre>
                </el-popover>
              </template>
            </el-table-column>
            <el-table-column prop="is_active" label="状态" width="100">
              <template #default="{ row }">
                <el-switch v-model="row.is_active" @change="toggleSource(row)"></el-switch>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" width="180"></el-table-column>
            <el-table-column label="操作" width="120">
              <template #default="{ row }">
                <el-button type="danger" size="small" @click="deleteSource(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="解析规则" name="rules">
        <el-card>
          <template #header>
            <div class="header-actions">
              <span>解析规则管理</span>
              <div class="actions">
                <el-button type="primary" @click="openRuleDialog">新增规则</el-button>
                <el-button @click="loadRules">刷新</el-button>
              </div>
            </div>
          </template>

          <el-table :data="rules" style="width: 100%">
            <el-table-column prop="id" label="ID" width="80"></el-table-column>
            <el-table-column prop="name" label="名称"></el-table-column>
            <el-table-column prop="pattern" label="正则表达式" min-width="300">
              <template #default="{ row }">
                <el-popover placement="top" width="400" trigger="hover">
                  <template #reference>
                    <span class="pattern-text">{{ row.pattern }}</span>
                  </template>
                  <pre>{{ row.pattern }}</pre>
                </el-popover>
              </template>
            </el-table-column>
            <el-table-column prop="format_description" label="描述" min-width="150"></el-table-column>
            <el-table-column prop="priority" label="优先级" width="100"></el-table-column>
            <el-table-column prop="is_active" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
                  {{ row.is_active ? '启用' : '禁用' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150">
              <template #default="{ row }">
                <el-button type="primary" size="small" @click="editRule(row)">编辑</el-button>
                <el-button type="danger" size="small" @click="deleteRule(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="解析测试" name="test">
        <el-card>
          <template #header>
            <span>日志解析测试</span>
          </template>

          <el-form :model="testForm" label-width="100px">
            <el-form-item label="日志内容">
              <el-input
                v-model="testForm.log_line"
                type="textarea"
                :rows="4"
                placeholder="输入要测试解析的日志行"
              ></el-input>
            </el-form-item>
            <el-form-item label="自定义正则">
              <el-input
                v-model="testForm.pattern"
                placeholder="可选，自定义正则表达式（留空则使用内置规则）"
              ></el-input>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="testParse">测试解析</el-button>
              <el-button @click="clearTest">清空</el-button>
            </el-form-item>
          </el-form>

          <el-card v-if="testResult" style="margin-top: 20px;">
            <template #header>
              <span>解析结果</span>
            </template>

            <el-descriptions :column="1" border v-if="testResult.detected_format">
              <el-descriptions-item label="检测格式">
                <el-tag type="success">{{ testResult.detected_format }}</el-tag>
              </el-descriptions-item>
            </el-descriptions>

            <div v-if="testResult.matched === false" style="margin-top: 10px;">
              <el-alert type="warning" :closable="false">
                {{ testResult.message || '正则表达式不匹配' }}
              </el-alert>
            </div>

            <el-table
              v-if="testResult.parsed || testResult.groups"
              :data="parseResultTable"
              style="width: 100%; margin-top: 20px;"
            >
              <el-table-column prop="key" label="字段" width="150"></el-table-column>
              <el-table-column prop="value" label="值"></el-table-column>
            </el-table>

            <pre v-if="!testResult.parsed && !testResult.groups && testResult.matched !== false"
                 style="margin-top: 10px; padding: 10px; background: #f5f7fa; border-radius: 4px;">
{{ JSON.stringify(testResult, null, 2) }}</pre>
          </el-card>
        </el-card>
      </el-tab-pane>
    </el-tabs>

    <el-dialog v-model="sourceDialogVisible" title="新增日志来源" width="600px">
      <el-form :model="sourceForm" label-width="100px">
        <el-form-item label="来源名称">
          <el-input v-model="sourceForm.name" placeholder="请输入来源名称"></el-input>
        </el-form-item>
        <el-form-item label="来源类型">
          <el-select v-model="sourceForm.source_type" placeholder="选择来源类型" style="width: 100%;"
                     @change="onSourceTypeChange">
            <el-option v-for="type in sourceTypes" :key="type.id" :label="type.name" :value="type.id">
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="文件路径" v-if="sourceForm.source_type === 'file'">
          <el-input v-model="sourceForm.config.file_path" placeholder="日志文件的绝对路径"></el-input>
        </el-form-item>
        <el-form-item label="端口" v-if="sourceForm.source_type === 'network'">
          <el-input-number v-model="sourceForm.config.port" :min="1" :max="65535"></el-input-number>
        </el-form-item>
        <el-form-item label="协议" v-if="sourceForm.source_type === 'network'">
          <el-select v-model="sourceForm.config.protocol" placeholder="选择协议" style="width: 100%;">
            <el-option label="TCP" value="tcp"></el-option>
            <el-option label="UDP" value="udp"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="服务名称">
          <el-input v-model="sourceForm.config.service_name" placeholder="可选，关联的服务名称"></el-input>
        </el-form-item>
        <el-form-item label="启用">
          <el-switch v-model="sourceForm.is_active"></el-switch>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="sourceDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="createSource">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="ruleDialogVisible" :title="editingRule ? '编辑解析规则' : '新增解析规则'" width="600px">
      <el-form :model="ruleForm" label-width="100px">
        <el-form-item label="规则名称">
          <el-input v-model="ruleForm.name" placeholder="请输入规则名称"></el-input>
        </el-form-item>
        <el-form-item label="正则表达式">
          <el-input
            v-model="ruleForm.pattern"
            type="textarea"
            :rows="3"
            placeholder="请输入正则表达式，使用命名捕获组如 (?P<timestamp>\\d{4}-\\d{2}-\\d{2} \\d{2}:\\d{2}:\\d{2})"
          ></el-input>
        </el-form-item>
        <el-form-item label="格式描述">
          <el-input v-model="ruleForm.format_description" placeholder="描述此规则适用的日志格式"></el-input>
        </el-form-item>
        <el-form-item label="优先级">
          <el-input-number v-model="ruleForm.priority" :min="1" :max="100"></el-input-number>
          <span style="margin-left: 10px; color: #909399;">数值越小优先级越高</span>
        </el-form-item>
        <el-form-item label="启用">
          <el-switch v-model="ruleForm.is_active"></el-switch>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="ruleDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveRule">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/utils/api'

const activeTab = ref('sources')
const sources = ref([])
const rules = ref([])
const sourceTypes = ref([])

const sourceDialogVisible = ref(false)
const ruleDialogVisible = ref(false)
const editingRule = ref(null)

const sourceForm = reactive({
  name: '',
  source_type: 'file',
  is_active: true,
  config: {
    file_path: '',
    port: 9999,
    protocol: 'tcp',
    service_name: ''
  }
})

const ruleForm = reactive({
  id: null,
  name: '',
  pattern: '',
  format_description: '',
  priority: 10,
  is_active: true
})

const testForm = reactive({
  log_line: '',
  pattern: ''
})

const testResult = ref(null)

const parseResultTable = computed(() => {
  const data = testResult.value?.parsed || testResult.value?.groups
  if (!data) return []
  return Object.entries(data).map(([key, value]) => ({ key, value }))
})

const getSourceTypeName = (type) => {
  const nameMap = {
    'file': '文件',
    'network': '网络端口',
    'api': 'API'
  }
  return nameMap[type] || type
}

const formatConfig = (config) => {
  if (!config) return '无配置'
  try {
    return JSON.stringify(typeof config === 'string' ? JSON.parse(config) : config, null, 2)
  } catch {
    return config
  }
}

const loadSources = async () => {
  try {
    const res = await api.getSources()
    sources.value = res.data?.sources || []
  } catch (error) {
    console.error('加载来源失败:', error)
  }
}

const loadRules = async () => {
  try {
    const res = await api.getParseRules()
    rules.value = res.data?.rules || []
  } catch (error) {
    console.error('加载规则失败:', error)
  }
}

const loadSourceTypes = async () => {
  try {
    const res = await api.getSourceTypes()
    sourceTypes.value = res.data?.types || []
  } catch (error) {
    console.error('加载来源类型失败:', error)
  }
}

const onSourceTypeChange = () => {
  sourceForm.config = {
    file_path: '',
    port: 9999,
    protocol: 'tcp',
    service_name: ''
  }
}

const openSourceDialog = () => {
  sourceForm.name = ''
  sourceForm.source_type = 'file'
  sourceForm.is_active = true
  sourceForm.config = {
    file_path: '',
    port: 9999,
    protocol: 'tcp',
    service_name: ''
  }
  sourceDialogVisible.value = true
}

const createSource = async () => {
  try {
    const config = {}
    if (sourceForm.source_type === 'file') {
      config.file_path = sourceForm.config.file_path
    } else if (sourceForm.source_type === 'network') {
      config.port = sourceForm.config.port
      config.protocol = sourceForm.config.protocol
    }
    if (sourceForm.config.service_name) {
      config.service_name = sourceForm.config.service_name
    }

    await api.createSource({
      name: sourceForm.name,
      source_type: sourceForm.source_type,
      config,
      is_active: sourceForm.is_active
    })

    ElMessage.success('来源创建成功')
    sourceDialogVisible.value = false
    loadSources()
  } catch (error) {
    ElMessage.error(error?.response?.data?.error || '创建失败')
  }
}

const toggleSource = async (source) => {
  try {
    await api.toggleSource(source.id)
    ElMessage.success('状态已更新')
  } catch (error) {
    source.is_active = !source.is_active
    ElMessage.error('更新失败')
  }
}

const deleteSource = async (source) => {
  try {
    await ElMessageBox.confirm('确定要删除该日志来源吗？', '提示', { type: 'warning' })
    await api.deleteSource(source.id)
    ElMessage.success('删除成功')
    loadSources()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const openRuleDialog = () => {
  editingRule.value = null
  ruleForm.id = null
  ruleForm.name = ''
  ruleForm.pattern = ''
  ruleForm.format_description = ''
  ruleForm.priority = 10
  ruleForm.is_active = true
  ruleDialogVisible.value = true
}

const editRule = (rule) => {
  editingRule.value = rule
  ruleForm.id = rule.id
  ruleForm.name = rule.name
  ruleForm.pattern = rule.pattern
  ruleForm.format_description = rule.format_description || ''
  ruleForm.priority = rule.priority
  ruleForm.is_active = rule.is_active
  ruleDialogVisible.value = true
}

const saveRule = async () => {
  try {
    if (editingRule.value) {
      await api.updateParseRule(ruleForm.id, {
        name: ruleForm.name,
        pattern: ruleForm.pattern,
        format_description: ruleForm.format_description,
        priority: ruleForm.priority,
        is_active: ruleForm.is_active
      })
      ElMessage.success('规则更新成功')
    } else {
      await api.createParseRule({
        name: ruleForm.name,
        pattern: ruleForm.pattern,
        format_description: ruleForm.format_description,
        priority: ruleForm.priority,
        is_active: ruleForm.is_active
      })
      ElMessage.success('规则创建成功')
    }

    ruleDialogVisible.value = false
    loadRules()
  } catch (error) {
    ElMessage.error(error?.response?.data?.error || '保存失败')
  }
}

const deleteRule = async (rule) => {
  try {
    await ElMessageBox.confirm('确定要删除该解析规则吗？', '提示', { type: 'warning' })
    await api.deleteParseRule(rule.id)
    ElMessage.success('删除成功')
    loadRules()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const testParse = async () => {
  if (!testForm.log_line) {
    ElMessage.warning('请输入要测试的日志内容')
    return
  }

  try {
    const data = { log_line: testForm.log_line }
    if (testForm.pattern) {
      data.pattern = testForm.pattern
    }

    const res = await api.testParse(data)
    testResult.value = res.data
  } catch (error) {
    ElMessage.error('解析测试失败')
  }
}

const clearTest = () => {
  testForm.log_line = ''
  testForm.pattern = ''
  testResult.value = null
}

onMounted(() => {
  loadSources()
  loadRules()
  loadSourceTypes()
})
</script>

<style scoped>
.config {
  padding: 0;
}

.header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.actions {
  display: flex;
  gap: 10px;
}

.pattern-text {
  font-family: monospace;
  font-size: 12px;
  color: #606266;
  word-break: break-all;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
