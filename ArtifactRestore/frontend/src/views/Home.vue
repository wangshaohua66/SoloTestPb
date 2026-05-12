<template>
  <div class="home-container">
    <el-card class="welcome-card">
      <template #header>
        <div class="card-header">
          <span>欢迎使用文物修复记录系统</span>
        </div>
      </template>
      <div class="welcome-content">
        <el-empty description="文物修复记录系统">
          <el-button type="primary" @click="goToArtifacts">开始使用</el-button>
        </el-empty>
      </div>
    </el-card>

    <el-row :gutter="20" class="stats-row">
      <el-col :span="4" v-for="stat in statCards" :key="stat.key">
        <el-card class="stat-card" shadow="hover" @click="goToPage(stat.path)">
          <div class="stat-icon" :style="{ background: stat.gradient }">
            <el-icon :size="32"><component :is="stat.icon" /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats[stat.key] }}</div>
            <div class="stat-label">{{ stat.label }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="features-card">
      <template #header>
        <div class="card-header">
          <span>系统功能</span>
        </div>
      </template>
      <el-row :gutter="20">
        <el-col :span="8" v-for="feature in features" :key="feature.title">
          <div class="feature-item" @click="goToPage(feature.path)">
            <el-icon :size="24" :color="feature.color">
              <component :is="feature.icon" />
            </el-icon>
            <h3>{{ feature.title }}</h3>
            <p>{{ feature.desc }}</p>
          </div>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { exportApi } from '../api'

const router = useRouter()

const stats = ref({
  artifacts: 0,
  plans: 0,
  processes: 0,
  images: 0,
  materials: 0
})

const statCards = [
  { key: 'artifacts', label: '文物档案', icon: 'Collection', path: '/artifacts', gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' },
  { key: 'plans', label: '修复计划', icon: 'Document', path: '/plans', gradient: 'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)' },
  { key: 'processes', label: '过程记录', icon: 'Timer', path: '/processes', gradient: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)' },
  { key: 'images', label: '影像资料', icon: 'Picture', path: '/images', gradient: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)' },
  { key: 'materials', label: '材料记录', icon: 'Box', path: '/materials', gradient: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)' }
]

const features = [
  { title: '文物档案', desc: '录入文物基本信息，包括名称、年代、类别等', icon: 'Collection', color: '#409EFF', path: '/artifacts' },
  { title: '修复计划', desc: '制定修复方案，记录修复目标、方法、工期', icon: 'Document', color: '#67C23A', path: '/plans' },
  { title: '过程记录', desc: '按时间顺序记录修复过程和操作细节', icon: 'Timer', color: '#E6A23C', path: '/processes' },
  { title: '影像管理', desc: '记录修复前、中、后的影像资料', icon: 'Picture', color: '#F56C6C', path: '/images' },
  { title: '材料管理', desc: '记录修复使用的材料信息和用量', icon: 'Box', color: '#909399', path: '/materials' },
  { title: '档案导出', desc: '生成完整的修复档案报告，支持导出', icon: 'Download', color: '#409EFF', path: '/export' }
]

const goToArtifacts = () => {
  router.push('/artifacts')
}

const goToPage = (path) => {
  if (path) {
    router.push(path)
  }
}

const loadStats = async () => {
  try {
    const res = await exportApi.getStats()
    if (res.code === 200) {
      stats.value = {
        artifacts: res.data.artifacts || 0,
        plans: res.data.plans || 0,
        processes: res.data.processes || 0,
        images: res.data.images || 0,
        materials: res.data.materials || 0
      }
    }
  } catch (e) {
    console.error('加载统计数据失败', e)
    ElMessage.error('加载统计数据失败')
  }
}

onMounted(() => {
  loadStats()
})
</script>

<style scoped>
.home-container {
  padding: 10px;
}

.welcome-card {
  margin-bottom: 20px;
}

.card-header {
  font-size: 16px;
  font-weight: bold;
}

.welcome-content {
  text-align: center;
  padding: 40px 0;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 20px;
  color: #fff;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 5px;
}

.feature-item {
  text-align: center;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s;
  border-radius: 8px;
}

.feature-item:hover {
  background: #f5f7fa;
}

.feature-item h3 {
  margin: 15px 0 10px;
  font-size: 16px;
  color: #303133;
}

.feature-item p {
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
}
</style>
