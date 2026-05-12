<template>
  <div class="alerts">
    <el-card>
      <template #header>
        <div class="header-actions">
          <span>告警列表</span>
          <div class="actions">
            <el-button type="primary" @click="loadAlerts">刷新</el-button>
          </div>
        </div>
      </template>

      <el-table :data="alerts" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80"></el-table-column>
        <el-table-column prop="title" label="标题"></el-table-column>
        <el-table-column prop="level" label="级别" width="100">
          <template #default="{ row }">
            <el-tag :type="getLevelTagType(row.level)" size="small">{{ row.level }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_acknowledged" label="确认状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_acknowledged ? 'success' : 'warning'" size="small">
              {{ row.is_acknowledged ? '已确认' : '未确认' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_resolved" label="解决状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_resolved ? 'info' : 'danger'" size="small">
              {{ row.is_resolved ? '已解决' : '活跃' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="trigger_count" label="触发次数" width="100"></el-table-column>
        <el-table-column prop="last_triggered_at" label="最后触发" width="180"></el-table-column>
        <el-table-column label="操作" width="180">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="acknowledgeAlert(row)" :disabled="row.is_acknowledged">
              确认
            </el-button>
            <el-button type="success" size="small" @click="resolveAlert(row)" :disabled="row.is_resolved">
              解决
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-card style="margin-top: 20px;">
      <template #header>
        <div class="header-actions">
          <span>告警规则</span>
          <div class="actions">
            <el-button type="primary" @click="openRuleDialog">新增规则</el-button>
            <el-button @click="loadRules">刷新</el-button>
          </div>
        </div>
      </template>

      <el-table :data="rules" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80"></el-table-column>
        <el-table-column prop="name" label="规则名称"></el-table-column>
        <el-table-column prop="condition_type" label="条件类型" width="120"></el-table-column>
        <el-table-column prop="level" label="告警级别" width="100">
          <template #default="{ row }">
            <el-tag :type="getLevelTagType(row.level)" size="small">{{ row.level }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="100">
          <template #default="{ row }">
            <el-switch v-model="row.is_active" @change="toggleRule(row)"></el-switch>
          </template>
        </el-table-column>
        <el-table-column prop="check_interval" label="检查间隔" width="100">
          <template #default="{ row }">
            {{ row.check_interval }}秒
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button type="danger" size="small" @click="deleteRule(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="ruleDialogVisible" title="新增告警规则" width="600px">
      <el-form :model="ruleForm" label-width="100px">
        <el-form-item label="规则名称">
          <el-input v-model="ruleForm.name" placeholder="请输入规则名称"></el-input>
        </el-form-item>
        <el-form-item label="条件类型">
          <el-select v-model="ruleForm.condition_type" placeholder="选择条件类型" style="width: 100%;">
            <el-option label="关键词" value="keyword"></el-option>
            <el-option label="级别阈值" value="level_threshold"></el-option>
            <el-option label="错误率" value="error_rate"></el-option>
            <el-option label="自定义查询" value="custom_query"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="告警级别">
          <el-select v-model="ruleForm.level" placeholder="选择告警级别" style="width: 100%;">
            <el-option label="INFO" value="INFO"></el-option>
            <el-option label="WARNING" value="WARNING"></el-option>
            <el-option label="ERROR" value="ERROR"></el-option>
            <el-option label="FATAL" value="FATAL"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="检查间隔">
          <el-input-number v-model="ruleForm.check_interval" :min="10" :max="3600"></el-input-number>
          <span style="margin-left: 10px;">秒</span>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="ruleForm.description" type="textarea" :rows="2"></el-input>
        </el-form-item>
        <el-form-item label="条件配置">
          <el-input v-model="ruleForm.condition_value_str" type="textarea" :rows="4" placeholder="JSON格式的条件配置"></el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="ruleDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="createRule">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/utils/api'

const alerts = ref([])
const rules = ref([])
const ruleDialogVisible = ref(false)

const ruleForm = reactive({
  name: '',
  condition_type: 'keyword',
  level: 'WARNING',
  check_interval: 60,
  description: '',
  condition_value_str: '{"keywords": ["error", "exception"], "time_window_minutes": 5, "threshold": 1}'
})

const getLevelTagType = (level) => {
  const typeMap = {
    'DEBUG': '',
    'INFO': 'success',
    'WARNING': 'warning',
    'WARN': 'warning',
    'ERROR': 'danger',
    'FATAL': 'danger',
    'ERR': 'danger'
  }
  return typeMap[level] || 'info'
}

const loadAlerts = async () => {
  try {
    const res = await api.getAlerts({ page_size: 50 })
    alerts.value = res.data?.alerts || []
  } catch (error) {
    console.error('加载告警失败:', error)
  }
}

const loadRules = async () => {
  try {
    const res = await api.getAlertRules()
    rules.value = res.data?.rules || []
  } catch (error) {
    console.error('加载告警规则失败:', error)
  }
}

const acknowledgeAlert = async (alert) => {
  try {
    await api.acknowledgeAlert(alert.id)
    ElMessage.success('告警已确认')
    loadAlerts()
  } catch (error) {
    ElMessage.error('确认失败')
  }
}

const resolveAlert = async (alert) => {
  try {
    await api.resolveAlert(alert.id)
    ElMessage.success('告警已解决')
    loadAlerts()
  } catch (error) {
    ElMessage.error('解决失败')
  }
}

const openRuleDialog = () => {
  ruleForm.name = ''
  ruleForm.condition_type = 'keyword'
  ruleForm.level = 'WARNING'
  ruleForm.check_interval = 60
  ruleForm.description = ''
  ruleForm.condition_value_str = '{"keywords": ["error", "exception"], "time_window_minutes": 5, "threshold": 1}'
  ruleDialogVisible.value = true
}

const createRule = async () => {
  try {
    let condition_value = null
    try {
      condition_value = JSON.parse(ruleForm.condition_value_str)
    } catch (e) {
      ElMessage.error('条件配置必须是有效的JSON格式')
      return
    }

    await api.createAlertRule({
      name: ruleForm.name,
      condition_type: ruleForm.condition_type,
      condition_value: condition_value,
      level: ruleForm.level,
      check_interval: ruleForm.check_interval,
      description: ruleForm.description,
      is_active: true
    })

    ElMessage.success('规则创建成功')
    ruleDialogVisible.value = false
    loadRules()
  } catch (error) {
    ElMessage.error('创建失败')
  }
}

const toggleRule = async (rule) => {
  try {
    await api.toggleAlertRule(rule.id)
    ElMessage.success('规则状态已更新')
  } catch (error) {
    rule.is_active = !rule.is_active
    ElMessage.error('更新失败')
  }
}

const deleteRule = async (rule) => {
  try {
    await ElMessageBox.confirm('确定要删除该规则吗？', '提示', { type: 'warning' })
    await api.deleteAlertRule(rule.id)
    ElMessage.success('删除成功')
    loadRules()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

onMounted(() => {
  loadAlerts()
  loadRules()
})
</script>

<style scoped>
.alerts {
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
</style>
