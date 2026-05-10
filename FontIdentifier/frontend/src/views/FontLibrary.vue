<template>
  <div class="page-container">
    <div class="card">
      <h2 class="card-title">
        <span>📚</span>
        书法字体库
      </h2>
      <p style="color: #666; margin-bottom: 20px;">
        内置常见书法字体信息，包括楷书、行书、草书、隶书、篆书等。点击卡片查看详细信息。
      </p>

      <div v-if="loading" class="loading">
        <div class="loading-spinner"></div>
      </div>

      <div v-else class="font-grid">
        <div
          v-for="font in fonts"
          :key="font.id"
          class="font-card"
          @click="showDetail(font)"
        >
          <div class="font-card-header">
            <span class="font-card-name">{{ font.name }}</span>
            <span class="font-card-english">{{ font.english_name }}</span>
          </div>
          <p class="font-card-desc">{{ font.description }}</p>
        </div>
      </div>
    </div>

    <div v-if="selectedFont" class="modal-overlay" @click.self="closeDetail">
      <div class="modal-content">
        <div class="modal-header">
          <h2>{{ selectedFont.name }} · {{ selectedFont.english_name }}</h2>
          <button class="modal-close" @click="closeDetail">×</button>
        </div>

        <div class="section-title">📖 字体简介</div>
        <p style="color: #555; line-height: 1.8;">{{ selectedFont.description }}</p>

        <div class="section-title">📜 历史沿革</div>
        <p style="color: #555; line-height: 1.8;">{{ selectedFont.history }}</p>

        <div class="section-title">✏️ 笔画特征</div>
        <ul class="feature-list">
          <li v-for="(value, key) in selectedFont.stroke_features" :key="key">
            <strong>{{ key }}：</strong>{{ value }}
          </li>
        </ul>

        <div class="section-title">🏗️ 结构特征</div>
        <ul class="feature-list">
          <li v-for="(value, key) in selectedFont.structure_features" :key="key">
            <strong>{{ key }}：</strong>{{ value }}
          </li>
        </ul>

        <div class="section-title">🎨 风格特征</div>
        <ul class="feature-list">
          <li v-for="(feature, index) in selectedFont.style_features" :key="index">
            {{ feature }}
          </li>
        </ul>

        <div class="section-title">🔑 关键识别特征</div>
        <ul class="feature-list">
          <li v-for="(char, index) in selectedFont.key_characteristics" :key="index">
            {{ char }}
          </li>
        </ul>

        <div class="section-title">📖 代表作品</div>
        <ul class="feature-list">
          <li v-for="(work, index) in selectedFont.representative_works" :key="index">
            {{ work }}
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script>
import { fontApi } from '../api'

export default {
  name: 'FontLibrary',
  data() {
    return {
      fonts: [],
      loading: true,
      selectedFont: null
    }
  },
  mounted() {
    this.loadFonts()
  },
  methods: {
    async loadFonts() {
      try {
        const response = await fontApi.getAllFonts()
        if (response.data.success) {
          this.fonts = response.data.fonts
        }
      } catch (err) {
        console.error('加载字体库失败:', err)
      } finally {
        this.loading = false
      }
    },
    showDetail(font) {
      this.selectedFont = font
    },
    closeDetail() {
      this.selectedFont = null
    }
  }
}
</script>
