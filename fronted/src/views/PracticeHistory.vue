<template>
  <div>
    <n-page-header title="做题记录" subtitle="查看你的练习历史">
    </n-page-header>

    <n-space vertical size="large" style="margin-top: 24px;">
      <!-- 筛选区域 -->
      <n-card>
        <n-space>
          <n-select
            v-model:value="filterSubjectId"
            :options="subjectOptions"
            placeholder="全部科目"
            style="width: 200px"
            clearable
            @update:value="loadHistory"
          />
          <n-button @click="loadHistory">
            <template #icon>
              <n-icon><refresh-outline /></n-icon>
            </template>
            刷新
          </n-button>
        </n-space>
      </n-card>

      <!-- 记录列表 -->
      <n-card title="练习记录">
        <n-spin :show="loading">
          <n-empty
            v-if="records.length === 0"
            description="暂无练习记录"
            style="margin: 40px 0;"
          />
          
          <n-list v-else bordered>
            <n-list-item v-for="(record, index) in records" :key="index">
              <div style="display: flex; align-items: center; justify-content: space-between; width: 100%; padding: 8px 0;">
                <!-- 左侧：头像和信息 -->
                <div style="display: flex; align-items: center; flex: 1; gap: 16px;">
                  <n-avatar :style="{ backgroundColor: getGradeColor(record.grade), fontSize: '20px', width: '48px', height: '48px' }">
                    {{ record.grade }}
                  </n-avatar>
                  
                  <div style="flex: 1;">
                    <!-- 标题行 -->
                    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
                      <n-text strong style="font-size: 18px;">{{ record.subject_name }}</n-text>
                      <n-tag :type="getGradeTagType(record.grade)" size="medium">
                        {{ record.grade }} 级
                      </n-tag>
                      <n-text depth="3" style="font-size: 14px; margin-left: auto;">
                        {{ record.practice_date }}
                      </n-text>
                    </div>
                    
                    <!-- 统计信息 -->
                    <n-space>
                      <n-statistic label="总题数" :value="record.total" style="min-width: 80px;">
                        <template #suffix>题</template>
                      </n-statistic>
                      
                      <n-divider vertical />
                      
                      <n-statistic label="正确" :value="record.correct" style="min-width: 80px;">
                        <template #suffix>
                          <n-text type="success">题</n-text>
                        </template>
                      </n-statistic>
                      
                      <n-divider vertical />
                      
                      <n-statistic label="错误" :value="record.wrong" style="min-width: 80px;">
                        <template #suffix>
                          <n-text type="error">题</n-text>
                        </template>
                      </n-statistic>
                      
                      <n-divider vertical />
                      
                      <n-statistic label="正确率" :value="record.accuracy" style="min-width: 100px;">
                        <template #suffix>
                          <n-text :type="record.accuracy >= 60 ? 'success' : 'error'">%</n-text>
                        </template>
                      </n-statistic>
                    </n-space>
                  </div>
                </div>
                
                <!-- 右侧：查看详情按钮 -->
                <div style="margin-left: 24px;">
                  <n-button type="primary" size="large" @click="viewDetails(record.session_id)">
                    查看详情
                  </n-button>
                </div>
              </div>
            </n-list-item>
          </n-list>
          
          <!-- 加载更多 -->
          <div v-if="records.length > 0 && hasMore" style="margin-top: 16px; text-align: center;">
            <n-button @click="loadMore" :loading="loadingMore">
              加载更多
            </n-button>
          </div>
        </n-spin>
      </n-card>

      <!-- 统计卡片 -->
      <n-card title="练习统计">
        <n-grid cols="4" x-gap="12" responsive="screen">
          <n-gi>
            <n-statistic label="总练习次数" :value="stats.totalSessions">
              <template #suffix>次</template>
            </n-statistic>
          </n-gi>
          <n-gi>
            <n-statistic label="总答题数" :value="stats.totalQuestions">
              <template #suffix>题</template>
            </n-statistic>
          </n-gi>
          <n-gi>
            <n-statistic label="平均正确率" :value="stats.avgAccuracy">
              <template #suffix>%</template>
            </n-statistic>
          </n-gi>
          <n-gi>
            <n-statistic label="最高正确率" :value="stats.maxAccuracy">
              <template #suffix>%</template>
            </n-statistic>
          </n-gi>
        </n-grid>
      </n-card>
    </n-space>

    <!-- 详情弹窗 -->
    <n-modal v-model:show="showDetails" preset="card" title="练习详情" style="width: 90%; max-width: 1200px;">
      <n-spin :show="loadingDetails">
        <n-empty v-if="details.length === 0" description="暂无详情数据" />
        
        <n-list v-else bordered>
          <n-list-item v-for="(detail, idx) in details" :key="idx">
            <n-space vertical size="large" style="width: 100%;">
              <!-- 题目 -->
              <n-space align="center">
                <n-tag :type="detail.is_correct ? 'success' : 'error'" size="small">
                  {{ detail.is_correct ? '✓ 正确' : '✗ 错误' }}
                </n-tag>
                <div style="font-weight: 500; font-size: 15px;">
                  {{ idx + 1 }}. ({{ getTypeLabel(detail.type) }}) <TableRenderer :content="detail.question" />
                </div>
              </n-space>

              <!-- 选项 -->
              <n-space v-if="detail.type !== 'fill'" vertical size="small">
                <div
                  v-for="(option, oidx) in detail.options"
                  :key="oidx"
                  :style="{
                    color: isCorrectOption(option, detail.correct_answer) ? '#18a058' : 'inherit'
                  }"
                >
                  <FormulaRenderer :content="option" />
                </div>
              </n-space>

              <!-- 答案对比 -->
              <n-space>
                <n-text depth="3">你的答案：</n-text>
                <n-tag :type="detail.is_correct ? 'success' : 'error'" size="small">
                  <FormulaRenderer :content="detail.user_answer || '未作答'" />
                </n-tag>
                <n-text depth="3">正确答案：</n-text>
                <n-tag type="success" size="small">
                  <FormulaRenderer :content="detail.correct_answer" />
                </n-tag>
              </n-space>

              <!-- 解析 -->
              <n-alert type="info" title="解析">
                <FormulaRenderer :content="detail.analysis" />
              </n-alert>
            </n-space>
          </n-list-item>
        </n-list>
      </n-spin>
    </n-modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useMessage } from 'naive-ui'
import { subjectApi } from '@/api'
import { RefreshOutline } from '@vicons/ionicons5'
import axios from 'axios'
import { useUserStore } from '@/stores/user'
import { storeToRefs } from 'pinia'
import FormulaRenderer from '@/components/FormulaRenderer.vue'
import TableRenderer from '@/components/TableRenderer.vue'

const message = useMessage()
const userStore = useUserStore()
const { userId } = storeToRefs(userStore)
const loading = ref(false)
const loadingMore = ref(false)
const loadingDetails = ref(false)
const showDetails = ref(false)
const records = ref([])
const subjects = ref([])
const details = ref([])
const filterSubjectId = ref(null)
const currentLimit = ref(50)
const hasMore = ref(true)

const subjectOptions = computed(() => {
  return [
    { label: '全部科目', value: null },
    ...subjects.value.map(s => ({
      label: s.name,
      value: s.id
    }))
  ]
})

const stats = computed(() => {
  if (records.value.length === 0) {
    return {
      totalSessions: 0,
      totalQuestions: 0,
      avgAccuracy: 0,
      maxAccuracy: 0
    }
  }
  
  const totalQuestions = records.value.reduce((sum, r) => sum + r.total, 0)
  const totalCorrect = records.value.reduce((sum, r) => sum + r.correct, 0)
  const avgAccuracy = totalQuestions > 0 ? (totalCorrect / totalQuestions * 100).toFixed(2) : 0
  const maxAccuracy = Math.max(...records.value.map(r => r.accuracy))
  
  return {
    totalSessions: records.value.length,
    totalQuestions,
    avgAccuracy,
    maxAccuracy
  }
})

const getGradeColor = (grade) => {
  const colors = {
    A: '#18a058',
    B: '#2080f0',
    C: '#f0a020',
    D: '#d03050',
    F: '#d03050'
  }
  return colors[grade] || '#d03050'
}

const getGradeTagType = (grade) => {
  if (grade === 'A') return 'success'
  if (grade === 'B') return 'info'
  if (grade === 'C' || grade === 'D') return 'warning'
  return 'error'
}

const getTypeLabel = (type) => {
  const map = {
    single: '单选题',
    multiple: '多选题',
    judge: '判断题',
    fill: '填空题'
  }
  return map[type] || type
}

const isCorrectOption = (option, answer) => {
  const optionValue = option.match(/^([A-Z])\./)?.[1] || option
  return answer.includes(optionValue)
}

const viewDetails = async (sessionId) => {
  loadingDetails.value = true
  showDetails.value = true
  details.value = []
  
  try {
    const response = await axios.get(`/api/practice/session/${sessionId}/details`)
    details.value = response.data.details
  } catch (error) {
    message.error('加载详情失败')
  } finally {
    loadingDetails.value = false
  }
}

const loadSubjects = async () => {
  try {
    subjects.value = await subjectApi.list(userId.value)
  } catch (error) {
    console.error('加载科目列表失败:', error)
  }
}

const loadHistory = async () => {
  loading.value = true
  currentLimit.value = 50
  try {
    const params = {
      user_id: userId.value,
      limit: currentLimit.value
    }
    
    if (filterSubjectId.value) {
      params.subject_id = filterSubjectId.value
    }
    
    const response = await axios.get('/api/practice/history', { params })
    records.value = response.data.records
    hasMore.value = response.data.records.length >= currentLimit.value
  } catch (error) {
    message.error(error.response?.data?.message || '加载练习记录失败')
  } finally {
    loading.value = false
  }
}

const loadMore = async () => {
  loadingMore.value = true
  currentLimit.value += 50
  try {
    const params = {
      user_id: userId.value,
      limit: currentLimit.value
    }
    
    if (filterSubjectId.value) {
      params.subject_id = filterSubjectId.value
    }
    
    const response = await axios.get('/api/practice/history', { params })
    records.value = response.data.records
    hasMore.value = response.data.records.length >= currentLimit.value
  } catch (error) {
    message.error('加载更多失败')
  } finally {
    loadingMore.value = false
  }
}

onMounted(async () => {
  await loadSubjects()
  await loadHistory()
})
</script>

<style scoped>
:deep(.n-list-item) {
  padding: 20px;
}

:deep(.n-thing-header) {
  margin-bottom: 8px;
}

:deep(.n-statistic) {
  text-align: center;
}
</style>
