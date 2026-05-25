<template>
  <div class="page-container">
    <div class="page-header">
      <h2 class="title">新建测验</h2>
      <div class="actions">
        <el-button @click="handleBack">返回</el-button>
        <el-button type="primary" @click="handleSave" :loading="saving">保存</el-button>
      </div>
    </div>

    <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
      <el-row :gutter="20">
        <el-col :span="8">
          <el-form-item label="题型" prop="type">
            <el-select v-model="form.type" placeholder="请选择题型">
              <el-option label="单选题" value="single" />
              <el-option label="多选题" value="multiple" />
              <el-option label="判断题" value="judge" />
              <el-option label="填空题" value="fill" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="难度" prop="difficulty">
            <el-select v-model="form.difficulty" placeholder="请选择难度">
              <el-option label="简单" value="easy" />
              <el-option label="中等" value="medium" />
              <el-option label="困难" value="hard" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="分值" prop="score">
            <el-input-number v-model="form.score" :min="1" :max="100" />
          </el-form-item>
        </el-col>
      </el-row>

      <el-form-item label="题目" prop="title">
        <el-input
          v-model="form.title"
          type="textarea"
          :rows="3"
          placeholder="请输入题目内容"
          maxlength="500"
          show-word-limit
        />
      </el-form-item>

      <template v-if="form.type === 'single' || form.type === 'multiple'">
        <el-form-item label="选项">
          <div v-for="(option, index) in form.options" :key="index" class="option-item">
            <span class="option-label">{{ String.fromCharCode(65 + index) }}.</span>
            <el-input v-model="option.value" placeholder="选项内容" />
            <el-checkbox
              v-model="option.isAnswer"
              :disabled="form.type === 'single' && !option.isAnswer"
              @change="handleAnswerChange(index)"
            >
              正确答案
            </el-checkbox>
            <el-button
              v-if="form.options.length > 2"
              type="danger"
              size="small"
              link
              @click="removeOption(index)"
            >
              删除
            </el-button>
          </div>
          <el-button type="primary" size="small" link @click="addOption" :disabled="form.options.length >= 8">
            + 添加选项
          </el-button>
        </el-form-item>
      </template>

      <template v-else-if="form.type === 'judge'">
        <el-form-item label="正确答案" prop="answer">
          <el-radio-group v-model="form.answer">
            <el-radio value="true">正确</el-radio>
            <el-radio value="false">错误</el-radio>
          </el-radio-group>
        </el-form-item>
      </template>

      <template v-else-if="form.type === 'fill'">
        <el-form-item label="正确答案" prop="answer">
          <el-input v-model="form.answer" placeholder="请输入正确答案" />
        </el-form-item>
      </template>

      <el-form-item label="答案解析">
        <el-input
          v-model="form.analysis"
          type="textarea"
          :rows="3"
          placeholder="请输入答案解析"
          maxlength="500"
          show-word-limit
        />
      </el-form-item>

      <el-form-item label="标签">
        <el-select v-model="form.tags" multiple filterable allow-create placeholder="请输入标签">
          <el-option label="Vue" value="Vue" />
          <el-option label="React" value="React" />
          <el-option label="JavaScript" value="JavaScript" />
          <el-option label="TypeScript" value="TypeScript" />
        </el-select>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { createQuiz, getQuizDetail, updateQuiz } from '@/api/quiz'
import { required } from '@/utils/validator'
import { logAction } from '@/utils/logger'
import { mockQuizzes } from '@/mock'
import type { Quiz, QuizOption } from '@/types'

const router = useRouter()
const route = useRoute()
const formRef = ref<FormInstance>()
const saving = ref(false)
const loading = ref(false)
const isEdit = ref(false)
const quizId = ref('')

const form = reactive<Partial<Quiz>>({
  type: 'single',
  difficulty: 'easy',
  score: 5,
  title: '',
  options: [
    { label: 'A', value: '', isAnswer: false },
    { label: 'B', value: '', isAnswer: false },
    { label: 'C', value: '', isAnswer: false },
    { label: 'D', value: '', isAnswer: false }
  ] as QuizOption[],
  answer: '',
  analysis: '',
  tags: []
})

const rules: FormRules = {
  type: [required('请选择题型')],
  difficulty: [required('请选择难度')],
  title: [required('请输入题目内容')],
  score: [required('请输入分值')],
  answer: [required('请输入正确答案')]
}

function addOption() {
  if (form.options && form.options.length < 8) {
    const index = form.options.length
    form.options.push({
      label: String.fromCharCode(65 + index),
      value: '',
      isAnswer: false
    })
  }
}

function removeOption(index: number) {
  if (form.options && form.options.length > 2) {
    form.options.splice(index, 1)
    form.options.forEach((opt, i) => {
      opt.label = String.fromCharCode(65 + i)
    })
  }
}

function handleAnswerChange(index: number) {
  if (form.type === 'single') {
    form.options?.forEach((opt, i) => {
      if (i !== index) {
        opt.isAnswer = false
      }
    })
  }
}

async function loadQuizDetail(id: string) {
  loading.value = true
  try {
    const quiz = await getQuizDetail(id)
    Object.assign(form, quiz)
    if ((form.type === 'single' || form.type === 'multiple') && form.answer) {
      const answers = Array.isArray(form.answer) ? form.answer : [form.answer]
      form.options?.forEach(opt => {
        opt.isAnswer = answers.includes(opt.label)
      })
    }
  } catch (e) {
    const mockQuiz = mockQuizzes.find(q => q.id === id)
    if (mockQuiz) {
      Object.assign(form, mockQuiz)
      if ((form.type === 'single' || form.type === 'multiple') && form.answer) {
        const answers = Array.isArray(form.answer) ? form.answer : [form.answer]
        form.options?.forEach(opt => {
          opt.isAnswer = answers.includes(opt.label)
        })
      }
    }
  } finally {
    loading.value = false
  }
}

async function handleSave() {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    if (form.type === 'single' || form.type === 'multiple') {
      const answers = form.options?.filter(o => o.isAnswer).map(o => o.label) || []
      if (answers.length === 0) {
        ElMessage.error('请选择正确答案')
        return
      }
      form.answer = form.type === 'single' ? answers[0] : answers
    }
    
    saving.value = true
    try {
      if (isEdit.value && quizId.value) {
        await updateQuiz(quizId.value, form)
        logAction('Quiz', 'update', { id: quizId.value, ...form })
        ElMessage.success('更新成功')
      } else {
        await createQuiz(form)
        logAction('Quiz', 'create', form)
        ElMessage.success('创建成功')
      }
      router.back()
    } finally {
      saving.value = false
    }
  })
}

function handleBack() {
  router.back()
}

onMounted(() => {
  const id = route.query.id as string
  if (id) {
    isEdit.value = true
    quizId.value = id
    loadQuizDetail(id)
  }
})
</script>

<style lang="scss" scoped>
.option-item {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
  margin-bottom: $spacing-sm;

  .option-label {
    font-weight: 600;
    min-width: 24px;
  }

  .el-input {
    flex: 1;
  }
}
</style>
