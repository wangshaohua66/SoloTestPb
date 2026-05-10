<template>
  <div class="page-container">
    <div class="card">
      <h2 class="card-title">
        <span>🔍</span>
        书法字体识别
      </h2>

      <div class="tabs">
        <div 
          class="tab" 
          :class="{ active: activeTab === 'text' }"
          @click="activeTab = 'text'"
        >
          📝 文字描述
        </div>
        <div 
          class="tab" 
          :class="{ active: activeTab === 'image' }"
          @click="activeTab = 'image'"
        >
          🖼️ 图片上传
        </div>
      </div>

      <div v-if="activeTab === 'text'">
        <div class="tips-box">
          <h4>💡 使用提示</h4>
          <ul>
            <li>请输入您观察到的书法作品特征，如笔画、结构、风格等</li>
            <li>可以描述横画、竖画、撇捺的形态特点</li>
            <li>可以描述整体结构，如方正、扁方、对称等</li>
            <li>可以描述书写风格，如工整、流畅、古朴等</li>
          </ul>
        </div>

        <div>
          <label style="font-weight: 500; color: #333; margin-bottom: 8px; display: block;">
            请输入特征描述：
          </label>
          <textarea
            v-model="description"
            class="textarea"
            placeholder="例如：这幅作品笔画方正，横平竖直，起笔和收笔都有明显的顿笔，结构规整对称，看起来非常工整..."
          ></textarea>
        </div>

        <div class="action-buttons">
          <button class="btn btn-primary" @click="recognizeByText" :disabled="loading || !description.trim()">
            {{ loading ? '识别中...' : '开始识别' }}
          </button>
          <button class="btn btn-secondary" @click="clearAll" :disabled="loading">
            清空
          </button>
        </div>
      </div>

      <div v-if="activeTab === 'image'">
        <div class="tips-box">
          <h4>💡 使用提示</h4>
          <ul>
            <li>支持的图片格式：JPG、PNG、GIF</li>
            <li>图片大小限制：最大5MB</li>
            <li>建议上传清晰的书法作品图片</li>
            <li>可以拖拽图片到上传区域</li>
          </ul>
        </div>

        <div 
          class="upload-area"
          :class="{ 'drag-over': isDragOver }"
          @dragover.prevent="isDragOver = true"
          @dragleave.prevent="isDragOver = false"
          @drop.prevent="handleDrop"
          @click="triggerFileInput"
        >
          <input 
            ref="fileInput"
            type="file" 
            accept="image/jpeg,image/png,image/gif,image/jpg"
            style="display: none;"
            @change="handleFileSelect"
          />
          
          <div v-if="!selectedImage && !uploadedImagePreview" class="upload-placeholder">
            <div class="upload-icon">📤</div>
            <p style="font-size: 16px; color: #333; margin-bottom: 8px;">
              点击或拖拽图片到此处上传
            </p>
            <p style="font-size: 12px; color: #888;">
              支持 JPG、PNG、GIF 格式，最大 5MB
            </p>
          </div>

          <div v-if="selectedImage || uploadedImagePreview" class="image-preview">
            <img 
              :src="selectedImage || uploadedImagePreview" 
              alt="预览图片"
              style="max-width: 100%; max-height: 300px; border-radius: 8px;"
            />
          </div>
        </div>

        <div class="action-buttons">
          <button 
            class="btn btn-primary" 
            @click="recognizeByImage" 
            :disabled="loading || (!selectedImage && !uploadedImagePreview)"
          >
            {{ loading ? '识别中...' : '开始识别' }}
          </button>
          <button 
            class="btn btn-secondary" 
            @click="clearAll" 
            :disabled="loading"
          >
            清空
          </button>
        </div>
      </div>
    </div>

    <div v-if="loading" class="card">
      <div class="loading">
        <div class="loading-spinner"></div>
        <span style="margin-left: 16px; color: #666;">正在分析特征...</span>
      </div>
    </div>

    <div v-if="result" class="card">
      <h2 class="card-title">
        <span>📊</span>
        识别结果
        <span v-if="result.recognition_type === 'image'" class="keyword-tag">图片识别</span>
        <span v-else class="keyword-tag">文字识别</span>
      </h2>

      <div v-if="result.recognition_type === 'image' && imagePreview" class="result-image-preview">
        <img 
          :src="imagePreview" 
          alt="识别图片"
          style="max-width: 200px; max-height: 200px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);"
        />
      </div>

      <div class="result-box">
        <div class="font-result">
          <div class="font-name">{{ result.primary_result.font_name }}</div>
          <div class="confidence-badge">置信度: {{ result.primary_result.confidence }}%</div>
        </div>

        <div v-if="result.primary_result.font_info" class="font-info-section">
          <div class="section-title">📝 字体简介</div>
          <p style="color: #555; line-height: 1.8;">
            {{ result.primary_result.font_info.description }}
          </p>
          <p style="color: #666; margin-top: 8px; font-size: 13px;">
            <strong>历史沿革：</strong>{{ result.primary_result.font_info.history }}
          </p>
        </div>

        <div class="section-title">🔍 识别分析</div>
        <div class="analysis-text">
          {{ result.primary_result.analysis }}
        </div>

        <div v-if="result.generated_description" class="section-title">📋 图片特征描述</div>
        <div v-if="result.generated_description" class="analysis-text" style="background: #f0f9ff; border: 1px solid #bae6fd;">
          {{ result.generated_description }}
        </div>

        <div v-if="result.primary_result.matched_keywords && result.primary_result.matched_keywords.length > 0" class="section-title">
          🎯 匹配关键词
        </div>
        <div v-if="result.primary_result.matched_keywords && result.primary_result.matched_keywords.length > 0">
          <span
            v-for="(kw, index) in result.primary_result.matched_keywords"
            :key="index"
            class="keyword-tag"
          >
            {{ kw.keyword }}
          </span>
        </div>

        <div v-if="result.image_features" class="section-title">
          📸 图像特征分析
        </div>
        <div v-if="result.image_features" style="background: #f8fafc; padding: 16px; border-radius: 8px;">
          <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px;">
            <div>
              <strong>图片信息：</strong>
              <p style="color: #666; font-size: 13px; margin-top: 4px;">
                {{ result.image_features.image_info.width }} x {{ result.image_features.image_info.height }} 像素
              </p>
            </div>
            <div>
              <strong>结构类型：</strong>
              <p style="color: #666; font-size: 13px; margin-top: 4px;">
                {{ result.image_features.structure_features?.structure_type || '未知' }}
              </p>
            </div>
            <div>
              <strong>笔画密度：</strong>
              <p style="color: #666; font-size: 13px; margin-top: 4px;">
                {{ (result.image_features.stroke_features?.ink_density * 100).toFixed(1) }}%
              </p>
            </div>
            <div>
              <strong>笔画粗细：</strong>
              <p style="color: #666; font-size: 13px; margin-top: 4px;">
                约 {{ result.image_features.stroke_features?.estimated_stroke_width?.toFixed(1) || '未知' }} 像素
              </p>
            </div>
          </div>
        </div>

        <div v-if="result.primary_result.font_info" class="section-title">
          ✨ 字体特征说明
        </div>
        <div v-if="result.primary_result.font_info">
          <div style="margin-bottom: 16px;">
            <h4 style="color: #333; margin-bottom: 8px;">笔画特征</h4>
            <ul class="feature-list">
              <li v-for="(value, key) in result.primary_result.font_info.stroke_features" :key="key">
                <strong>{{ key }}：</strong>{{ value }}
              </li>
            </ul>
          </div>

          <div style="margin-bottom: 16px;">
            <h4 style="color: #333; margin-bottom: 8px;">结构特征</h4>
            <ul class="feature-list">
              <li v-for="(value, key) in result.primary_result.font_info.structure_features" :key="key">
                <strong>{{ key }}：</strong>{{ value }}
              </li>
            </ul>
          </div>

          <div style="margin-bottom: 16px;">
            <h4 style="color: #333; margin-bottom: 8px;">风格特征</h4>
            <ul class="feature-list">
              <li v-for="(feature, index) in result.primary_result.font_info.style_features" :key="index">
                {{ feature }}
              </li>
            </ul>
          </div>

          <div>
            <h4 style="color: #333; margin-bottom: 8px;">代表作品</h4>
            <ul class="feature-list">
              <li v-for="(work, index) in result.primary_result.font_info.representative_works" :key="index">
                📖 {{ work }}
              </li>
            </ul>
          </div>
        </div>

        <div class="section-title">📈 所有字体匹配度</div>
        <div class="all-results">
          <div
            v-for="item in sortedAllResults"
            :key="item.font_name"
            class="result-item"
          >
            <div class="result-item-name">{{ item.font_name }}</div>
            <div class="result-item-conf">{{ item.confidence_percent }}%</div>
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: item.confidence_percent + '%' }"></div>
            </div>
          </div>
        </div>

        <div v-if="result.similar_fonts && result.similar_fonts.length > 0" class="section-title">
          🔄 相似字体比对
        </div>
        <div v-if="result.similar_fonts && result.similar_fonts.length > 0">
          <div
            v-for="similar in result.similar_fonts"
            :key="similar.font_name"
            class="similar-font"
          >
            <div class="similar-font-header">
              <span class="similar-font-name">{{ similar.font_name }}</span>
              <span class="confidence-badge" style="font-size: 12px;">
                匹配度: {{ similar.confidence }}%
              </span>
            </div>
            <div class="similar-font-diff">
              <strong>区别要点：</strong>{{ similar.differences }}
            </div>
          </div>
        </div>

        <div class="action-buttons">
          <button class="btn btn-success" @click="exportReport">
            📥 导出报告
          </button>
          <button class="btn btn-secondary" @click="clearAll">
            🔄 重新识别
          </button>
        </div>
      </div>
    </div>

    <div v-if="error" class="card" style="background: #fef2f2; border: 1px solid #fecaca;">
      <p style="color: #dc2626;">❌ {{ error }}</p>
    </div>
  </div>
</template>

<script>
import { fontApi } from '../api'

export default {
  name: 'Recognize',
  data() {
    return {
      activeTab: 'text',
      description: '',
      selectedImage: null,
      uploadedImagePreview: null,
      imagePreview: null,
      isDragOver: false,
      loading: false,
      result: null,
      error: null,
      lastInput: ''
    }
  },
  computed: {
    sortedAllResults() {
      if (!this.result || !this.result.all_results) return []
      return this.result.all_results
        .map(item => ({
          ...item,
          confidence_percent: item.confidence <= 1 ? item.confidence * 100 : item.confidence
        }))
        .sort((a, b) => b.confidence_percent - a.confidence_percent)
    }
  },
  methods: {
    triggerFileInput() {
      this.$refs.fileInput.click()
    },

    handleFileSelect(event) {
      const file = event.target.files[0]
      if (file) {
        this.processFile(file)
      }
    },

    handleDrop(event) {
      this.isDragOver = false
      const files = event.dataTransfer.files
      if (files.length > 0) {
        this.processFile(files[0])
      }
    },

    processFile(file) {
      const validTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/jpg']
      if (!validTypes.includes(file.type)) {
        this.error = '请上传 JPG、PNG 或 GIF 格式的图片'
        return
      }

      if (file.size > 5 * 1024 * 1024) {
        this.error = '图片大小不能超过 5MB'
        return
      }

      this.error = null
      this.selectedImage = file
      
      const reader = new FileReader()
      reader.onload = (e) => {
        this.uploadedImagePreview = e.target.result
      }
      reader.readAsDataURL(file)
    },

    async recognizeByText() {
      if (!this.description.trim()) {
        this.error = '请输入字体特征描述'
        return
      }

      this.loading = true
      this.error = null
      this.lastInput = this.description
      this.imagePreview = null

      try {
        const response = await fontApi.recognizeByText(this.description)

        if (response.data.success) {
          this.result = response.data.result
        } else {
          this.error = response.data.message || '识别失败'
        }
      } catch (err) {
        this.error = err.response?.data?.message || '网络错误，请稍后重试'
      } finally {
        this.loading = false
      }
    },

    async recognizeByImage() {
      if (!this.selectedImage) {
        this.error = '请先选择要识别的图片'
        return
      }

      this.loading = true
      this.error = null
      this.lastInput = '[图片识别] ' + (this.selectedImage.name || '上传的图片')

      try {
        const formData = new FormData()
        formData.append('image', this.selectedImage)

        const response = await fontApi.recognizeByImage(formData)

        if (response.data.success) {
          this.result = response.data.result
          this.imagePreview = response.data.image_preview
        } else {
          this.error = response.data.message || '识别失败'
        }
      } catch (err) {
        this.error = err.response?.data?.message || '网络错误，请稍后重试'
      } finally {
        this.loading = false
      }
    },

    clearAll() {
      this.description = ''
      this.selectedImage = null
      this.uploadedImagePreview = null
      this.imagePreview = null
      this.result = null
      this.error = null
      if (this.$refs.fileInput) {
        this.$refs.fileInput.value = ''
      }
    },

    async exportReport() {
      try {
        const response = await fontApi.exportReportDirect(this.result, this.lastInput)

        const url = window.URL.createObjectURL(new Blob([response.data], { type: 'text/plain;charset=utf-8' }))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', `字体识别报告_${this.result.primary_result.font_name}_${new Date().getTime()}.txt`)
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)
      } catch (err) {
        this.error = '导出失败，请稍后重试'
      }
    }
  }
}
</script>

<style scoped>
.tabs {
  display: flex;
  border-bottom: 2px solid #e5e7eb;
  margin-bottom: 20px;
}

.tab {
  padding: 12px 24px;
  cursor: pointer;
  font-weight: 500;
  color: #6b7280;
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
  transition: all 0.3s ease;
}

.tab:hover {
  color: #667eea;
}

.tab.active {
  color: #667eea;
  border-bottom-color: #667eea;
}

.upload-area {
  border: 2px dashed #d1d5db;
  border-radius: 12px;
  padding: 40px 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background: #fafafa;
}

.upload-area:hover {
  border-color: #667eea;
  background: #f5f3ff;
}

.upload-area.drag-over {
  border-color: #667eea;
  background: #ede9fe;
}

.upload-placeholder {
  color: #6b7280;
}

.upload-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.image-preview {
  display: flex;
  justify-content: center;
  align-items: center;
}

.result-image-preview {
  text-align: center;
  margin-bottom: 20px;
}
</style>
