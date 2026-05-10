<template>
  <div class="page-container">
    <div class="card">
      <h2 class="card-title">
        <span>📋</span>
        识别历史记录
      </h2>

      <div v-if="loading" class="loading">
        <div class="loading-spinner"></div>
      </div>

      <div v-else-if="history.length === 0" class="empty-state">
        <div class="empty-icon">📭</div>
        <h3>暂无识别记录</h3>
        <p>开始识别书法字体后，您的记录将显示在这里</p>
      </div>

      <div v-else>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; flex-wrap: wrap; gap: 12px;">
          <p style="color: #666;">共 {{ total }} 条记录</p>
          <div v-if="statsLoaded" style="display: flex; gap: 12px; flex-wrap: wrap;">
            <span
              v-for="stat in stats"
              :key="stat.font"
              class="keyword-tag"
              style="font-size: 12px;"
            >
              {{ stat.font }}: {{ stat.count }}次
            </span>
          </div>
        </div>

        <table class="table">
          <thead>
            <tr>
              <th style="width: 60px;">ID</th>
              <th>输入描述</th>
              <th style="width: 100px;">识别结果</th>
              <th style="width: 100px;">置信度</th>
              <th style="width: 160px;">识别时间</th>
              <th style="width: 160px;">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="record in history" :key="record.id">
              <td>{{ record.id }}</td>
              <td style="max-width: 300px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                {{ record.input_text }}
              </td>
              <td><strong>{{ record.recognized_font }}</strong></td>
              <td>
                <span class="confidence-badge" style="font-size: 12px;">
                  {{ record.confidence }}%
                </span>
              </td>
              <td>{{ formatDate(record.created_at) }}</td>
              <td>
                <button class="btn btn-secondary" style="padding: 6px 12px; font-size: 12px;" @click="viewDetail(record.id)">
                  查看详情
                </button>
                <button class="btn btn-success" style="padding: 6px 12px; font-size: 12px; margin-left: 8px;" @click="exportRecord(record.id)">
                  导出报告
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="selectedRecord" class="modal-overlay" @click.self="closeDetail">
      <div class="modal-content">
        <div class="modal-header">
          <h2>识别记录详情 #{{ selectedRecord.id }}</h2>
          <button class="modal-close" @click="closeDetail">×</button>
        </div>

        <div class="section-title">📝 输入描述</div>
        <p style="color: #555; line-height: 1.8; padding: 12px; background: #f8fafc; border-radius: 8px;">
          {{ selectedRecord.input_text }}
        </p>

        <div class="section-title">🎯 识别结果</div>
        <div class="font-result" style="margin-bottom: 16px;">
          <div class="font-name" style="font-size: 36px;">{{ selectedRecord.recognized_font }}</div>
          <div class="confidence-badge">置信度: {{ selectedRecord.confidence }}%</div>
        </div>

        <div v-if="selectedRecord.result && selectedRecord.result.primary_result">
          <div class="section-title">🔍 识别分析</div>
          <div class="analysis-text">
            {{ selectedRecord.result.primary_result.analysis }}
          </div>

          <div v-if="selectedRecord.result.primary_result.font_info">
            <div class="section-title">✨ 字体特征</div>
            <ul class="feature-list">
              <li v-for="(char, index) in selectedRecord.result.primary_result.font_info.key_characteristics" :key="index">
                {{ char }}
              </li>
            </ul>
          </div>

          <div v-if="selectedRecord.result.similar_fonts && selectedRecord.result.similar_fonts.length > 0">
            <div class="section-title">🔄 相似字体</div>
            <div
              v-for="similar in selectedRecord.result.similar_fonts"
              :key="similar.font_name"
              class="similar-font"
            >
              <div class="similar-font-header">
                <span class="similar-font-name">{{ similar.font_name }}</span>
                <span class="confidence-badge" style="font-size: 12px;">
                  {{ similar.confidence }}%
                </span>
              </div>
              <div class="similar-font-diff">
                <strong>区别要点：</strong>{{ similar.differences }}
              </div>
            </div>
          </div>
        </div>

        <div class="section-title">🕐 识别时间</div>
        <p style="color: #666;">{{ formatDate(selectedRecord.created_at) }}</p>

        <div class="action-buttons">
          <button class="btn btn-success" @click="exportRecord(selectedRecord.id)">
            📥 导出报告
          </button>
          <button class="btn btn-secondary" @click="closeDetail">
            关闭
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { fontApi } from '../api'

export default {
  name: 'History',
  data() {
    return {
      history: [],
      total: 0,
      stats: [],
      loading: true,
      statsLoaded: false,
      selectedRecord: null
    }
  },
  mounted() {
    this.loadAllData()
  },
  methods: {
    async loadAllData() {
      try {
        await Promise.all([
          this.loadHistory(),
          this.loadStats()
        ])
      } catch (err) {
        console.error('加载数据失败:', err)
      } finally {
        this.loading = false
      }
    },

    async loadHistory() {
      try {
        const response = await fontApi.getHistory()
        if (response.data.success) {
          this.history = response.data.history
          this.total = response.data.total
        }
      } catch (err) {
        console.error('加载历史记录失败:', err)
        throw err
      }
    },

    async loadStats() {
      try {
        const response = await fontApi.getStats()
        if (response.data.success) {
          this.stats = response.data.font_statistics
          this.statsLoaded = true
        }
      } catch (err) {
        console.error('加载统计信息失败:', err)
        this.statsLoaded = true
      }
    },

    async viewDetail(recordId) {
      try {
        const response = await fontApi.getHistoryDetail(recordId)
        if (response.data.success) {
          this.selectedRecord = response.data.record
        }
      } catch (err) {
        console.error('加载记录详情失败:', err)
      }
    },

    closeDetail() {
      this.selectedRecord = null
    },

    async exportRecord(recordId) {
      try {
        const response = await fontApi.exportReport(recordId)

        const url = window.URL.createObjectURL(new Blob([response.data], { type: 'text/plain;charset=utf-8' }))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', `历史记录_${recordId}_${new Date().getTime()}.txt`)
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)
      } catch (err) {
        alert('导出失败，请稍后重试')
      }
    },

    formatDate(dateStr) {
      if (!dateStr) return '-'
      const date = new Date(dateStr)
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      })
    }
  }
}
</script>
