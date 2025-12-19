<template>
  <div>
    <n-page-header title="开始练习" subtitle="自定义题量，开始你的练习">
    </n-page-header>

    <!-- 配置练习 -->
    <n-card v-if="!practicing" title="配置练习" style="margin-top: 24px;">
      <n-space vertical size="large">
        <!-- 选择科目 -->
        <n-form-item label="选择科目">
          <n-select
            v-model:value="config.subject_id"
            :options="subjectOptions"
            placeholder="请选择科目"
            :loading="loadingSubjects"
            @update:value="handleSubjectChange"
          />
        </n-form-item>

        <!-- 题型配置 -->
        <n-form-item label="题型与数量">
          <n-space vertical style="width: 100%;">
            <n-alert v-if="availableTypes.length === 0" type="warning">
              该科目下暂无题目，请先导入题目
            </n-alert>
            
            <n-checkbox-group v-model:value="selectedTypes">
              <n-space vertical>
                <n-space v-for="type in typeOptions" :key="type.value" align="center">
                  <n-checkbox
                    :value="type.value"
                    :label="type.label"
                    :disabled="!availableTypes.includes(type.value)"
                  />
                  <n-input-number
                    v-model:value="config.question_counts[type.value]"
                    :min="0"
                    :max="100"
                    :disabled="!selectedTypes.includes(type.value)"
                    style="width: 120px;"
                  >
                    <template #suffix>题</template>
                  </n-input-number>
                </n-space>
              </n-space>
            </n-checkbox-group>
          </n-space>
        </n-form-item>

        <n-button
          type="primary"
          size="large"
          :disabled="!canStart"
          :loading="starting"
          @click="startPractice"
          block
        >
          开始练习
        </n-button>
      </n-space>
    </n-card>

    <!-- 练习中 -->
    <div v-else style="display: flex; gap: 16px; margin-top: 24px;">
      <!-- 左侧题目区域 - 显示所有题目 -->
      <div style="flex: 1;">
        <n-space vertical size="large">
          <n-card 
            v-for="(question, qIndex) in questions" 
            :key="question.id"
            :title="`${qIndex + 1}.(${getTypeLabel(question.type)}) ${question.question}`"
            :id="`question-${qIndex}`"
          >
            <n-space vertical size="large">
              <n-text strong style="font-size: 14px; color: #666;">分值: {{ question.score || 2 }}分</n-text>
              
              <!-- 单选题和判断题 -->
              <div v-if="question.type === 'single' || question.type === 'judge'">
                <n-radio-group v-model:value="answers[question.id]">
                  <n-space vertical>
                    <n-radio
                      v-for="(option, index) in question.options"
                      :key="index"
                      :value="getOptionValue(option)"
                      :label="option"
                      size="large"
                    />
                  </n-space>
                </n-radio-group>
              </div>

              <!-- 多选题 -->
              <div v-else-if="question.type === 'multiple'">
                <n-checkbox-group v-model:value="multiAnswers[question.id]">
                  <n-space vertical>
                    <n-checkbox
                      v-for="(option, index) in question.options"
                      :key="index"
                      :value="getOptionValue(option)"
                      :label="option"
                      size="large"
                    />
                  </n-space>
                </n-checkbox-group>
              </div>

              <!-- 填空题 -->
              <n-input
                v-else
                v-model:value="answers[question.id]"
                placeholder="请输入答案"
                size="large"
              />
            </n-space>
          </n-card>
        </n-space>
      </div>

      <!-- 右侧答题卡 - 固定定位 -->
      <div style="width: 300px; position: sticky; top: 24px; align-self: flex-start;">
        <n-card :title="`答题卡 (${answeredCount}/${questions.length})`" size="small">
          <n-space vertical size="large">
            <!-- 题号网格 -->
            <div style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 8px;">
              <n-button
                v-for="(q, idx) in questions"
                :key="idx"
                :type="isAnswered(idx) ? 'primary' : 'default'"
                size="medium"
                @click="scrollToQuestion(idx)"
                style="width: 100%;"
              >
                {{ idx + 1 }}
              </n-button>
            </div>

            <!-- 提交按钮 -->
            <n-button
              type="primary"
              block
              size="large"
              :loading="submitting"
              @click="submitAnswers"
            >
              提交
            </n-button>
          </n-space>
        </n-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useMessage } from 'naive-ui'
import { useRouter } from 'vue-router'
import { subjectApi, questionApi, practiceApi } from '@/api'
import { useUserStore } from '@/stores/user'
import { storeToRefs } from 'pinia'

const message = useMessage()
const router = useRouter()
const userStore = useUserStore()
const { userId } = storeToRefs(userStore)
const loadingSubjects = ref(false)
const starting = ref(false)
const submitting = ref(false)
const practicing = ref(false)
const subjects = ref([])
const availableTypes = ref([])
const selectedTypes = ref([])
const questions = ref([])
const answers = ref({})
const multiAnswers = ref({})

const config = ref({
  subject_id: null,
  question_counts: {
    single: 0,
    multiple: 0,
    judge: 0,
    fill: 0
  }
})

const typeOptions = [
  { label: '单选题', value: 'single' },
  { label: '多选题', value: 'multiple' },
  { label: '判断题', value: 'judge' },
  { label: '填空题', value: 'fill' }
]

const subjectOptions = computed(() => {
  return subjects.value.map(s => ({
    label: s.name,
    value: s.id
  }))
})

const answeredCount = computed(() => {
  let count = 0
  questions.value.forEach(q => {
    if (q.type === 'multiple') {
      if (multiAnswers.value[q.id] && multiAnswers.value[q.id].length > 0) {
        count++
      }
    } else {
      if (answers.value[q.id]) {
        count++
      }
    }
  })
  return count
})

const canStart = computed(() => {
  if (!config.value.subject_id) return false
  const total = Object.values(config.value.question_counts).reduce((a, b) => a + b, 0)
  return total > 0
})

const getTypeLabel = (type) => {
  const map = {
    single: '单选题',
    multiple: '多选题',
    judge: '判断题',
    fill: '填空题'
  }
  return map[type] || type
}

const getOptionValue = (option) => {
  const match = option.match(/^([A-Z])\./)
  return match ? match[1] : option
}

const isAnswered = (index) => {
  const q = questions.value[index]
  if (!q) return false
  
  if (q.type === 'multiple') {
    return multiAnswers.value[q.id] && multiAnswers.value[q.id].length > 0
  }
  return answers.value[q.id] && answers.value[q.id].trim() !== ''
}

const loadSubjects = async () => {
  loadingSubjects.value = true
  try {
    subjects.value = await subjectApi.list(userId.value)
  } catch (error) {
    message.error(error.message || '加载科目列表失败')
  } finally {
    loadingSubjects.value = false
  }
}

const handleSubjectChange = async (subjectId) => {
  try {
    const data = await questionApi.getTypes(subjectId, userId.value)
    availableTypes.value = data.types
    selectedTypes.value = []
    config.value.question_counts = {
      single: 0,
      multiple: 0,
      judge: 0,
      fill: 0
    }
  } catch (error) {
    message.error(error.message || '获取题型失败')
  }
}

const startPractice = async () => {
  starting.value = true
  try {
    const data = await practiceApi.start({
      user_id: userId.value,
      subject_id: config.value.subject_id,
      question_counts: config.value.question_counts
    })
    
    questions.value = data.questions
    practicing.value = true
    
    // 初始化答案对象，确保每个题目都有对应的空答案
    const newAnswers = {}
    const newMultiAnswers = {}
    data.questions.forEach(q => {
      if (q.type === 'multiple') {
        newMultiAnswers[q.id] = []
      } else {
        newAnswers[q.id] = ''
      }
    })
    answers.value = newAnswers
    multiAnswers.value = newMultiAnswers
  } catch (error) {
    message.error(error.message || '开始练习失败')
  } finally {
    starting.value = false
  }
}

const scrollToQuestion = (index) => {
  const element = document.getElementById(`question-${index}`)
  if (element) {
    element.scrollIntoView({ behavior: 'smooth', block: 'center' })
  }
}

const submitAnswers = async () => {
  // 检查是否所有题都已作答
  const unanswered = questions.value.filter(q => {
    if (q.type === 'multiple') {
      return !multiAnswers.value[q.id] || multiAnswers.value[q.id].length === 0
    }
    return !answers.value[q.id]
  })

  if (unanswered.length > 0) {
    message.warning(`还有 ${unanswered.length} 题未作答`)
    return
  }

  submitting.value = true
  try {
    // 格式化答案
    const formattedAnswers = questions.value.map(q => {
      let userAnswer = ''
      if (q.type === 'multiple') {
        userAnswer = (multiAnswers.value[q.id] || []).sort().join(',')
      } else {
        userAnswer = answers.value[q.id] || ''
      }

      return {
        question_id: q.id,
        user_answer: userAnswer
      }
    })

    const data = await practiceApi.submit({
      user_id: userId.value,
      subject_id: config.value.subject_id,
      answers: formattedAnswers
    })

    // 提交成功后跳转到练习记录页面
    message.success(`提交成功！正确 ${data.correct} 题，错误 ${data.wrong} 题，准确率 ${data.accuracy}%，成绩 ${data.grade}`)
    
    // 延迟跳转，让用户看到成功提示
    setTimeout(() => {
      router.push('/practice-history')
    }, 1500)
  } catch (error) {
    message.error(error.message || '提交失败')
  } finally {
    submitting.value = false
  }
}

const resetPractice = () => {
  practicing.value = false
  questions.value = []
  answers.value = {}
  multiAnswers.value = {}
}

onMounted(() => {
  loadSubjects()
})
</script>
