<template>
  <div>
    <n-page-header title="题库管理" subtitle="查看和管理所有题目">
    </n-page-header>

    <n-space vertical size="large" style="margin-top: 24px;">
      <!-- 筛选区域 -->
      <n-card>
        <n-space>
          <n-select
            v-model:value="filterSubjectId"
            :options="subjectOptions"
            placeholder="选择科目"
            style="width: 200px"
            clearable
            @update:value="loadQuestions"
          />
          <n-select
            v-model:value="filterType"
            :options="typeOptions"
            placeholder="题目类型"
            style="width: 150px"
            clearable
            @update:value="loadQuestions"
          />
          <n-input
            v-model:value="searchKeyword"
            placeholder="搜索题目内容"
            style="width: 300px"
            clearable
            @keyup.enter="loadQuestions"
          >
            <template #prefix>
              <n-icon><search-outline /></n-icon>
            </template>
          </n-input>
          <n-button type="primary" @click="loadQuestions">
            <template #icon>
              <n-icon><search-outline /></n-icon>
            </template>
            搜索
          </n-button>
          <n-button @click="handleReset">
            <template #icon>
              <n-icon><refresh-outline /></n-icon>
            </template>
            重置
          </n-button>
        </n-space>
      </n-card>

      <!-- 题目统计 -->
      <n-card>
        <n-space>
          <n-statistic label="总题数" :value="totalCount" />
          <n-statistic label="单选题" :value="typeCount.single || 0" />
          <n-statistic label="多选题" :value="typeCount.multiple || 0" />
          <n-statistic label="判断题" :value="typeCount.judge || 0" />
          <n-statistic label="填空题" :value="typeCount.fill || 0" />
        </n-space>
      </n-card>

      <!-- 题目列表 -->
      <n-card title="题目列表">
        <n-spin :show="loading">
          <n-empty
            v-if="questions.length === 0"
            description="暂无题目数据"
            style="margin: 40px 0;"
          />
          
          <n-list v-else bordered>
            <n-list-item v-for="(question, index) in paginatedQuestions" :key="question.id">
              <template #prefix>
                <n-tag :type="getTypeTagType(question.type)" size="small">
                  {{ getTypeLabel(question.type) }}
                </n-tag>
              </template>
              
              <n-thing>
                <template #header>
                  <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="font-weight: 500;">{{ (currentPage - 1) * pageSize + index + 1 }}. {{ question.question }}</span>
                  </div>
                </template>
                
                <template #header-extra>
                  <n-space>
                    <n-button text @click="handleView(question)">
                      <template #icon>
                        <n-icon><eye-outline /></n-icon>
                      </template>
                      查看
                    </n-button>
                    <n-button text type="error" @click="handleDelete(question)">
                      <template #icon>
                        <n-icon><trash-outline /></n-icon>
                      </template>
                      删除
                    </n-button>
                  </n-space>
                </template>
                
                <template #description>
                  <n-space vertical size="small" style="margin-top: 8px;">
                    <!-- 选项 -->
                    <div v-if="question.options && question.options.length > 0">
                      <n-space vertical size="small">
                        <div v-for="(option, idx) in question.options" :key="idx" style="font-size: 14px;">
                          {{ option }}
                        </div>
                      </n-space>
                    </div>
                    
                    <!-- 答案 -->
                    <div style="margin-top: 8px;">
                      <n-text strong>答案：</n-text>
                      <n-text type="success">{{ question.answer }}</n-text>
                    </div>
                    
                    <!-- 解析 -->
                    <div style="margin-top: 4px;">
                      <n-text strong>解析：</n-text>
                      <n-text depth="3">{{ question.analysis }}</n-text>
                    </div>
                    
                    <!-- 元信息 -->
                    <div style="margin-top: 8px;">
                      <n-space size="small">
                        <n-tag size="tiny" :bordered="false">
                          科目: {{ getSubjectName(question.subject_id) }}
                        </n-tag>
                        <n-tag size="tiny" :bordered="false">
                          创建时间: {{ question.created_at }}
                        </n-tag>
                      </n-space>
                    </div>
                  </n-space>
                </template>
              </n-thing>
            </n-list-item>
          </n-list>
          
          <!-- 分页 -->
          <div v-if="questions.length > 0" style="margin-top: 16px; display: flex; justify-content: flex-end;">
            <n-pagination
              v-model:page="currentPage"
              :page-count="pageCount"
              :page-size="pageSize"
              show-size-picker
              :page-sizes="[10, 20, 50, 100]"
              @update:page="handlePageChange"
              @update:page-size="handlePageSizeChange"
            />
          </div>
        </n-spin>
      </n-card>
    </n-space>

    <!-- 查看题目详情对话框 -->
    <n-modal v-model:show="showDetailModal" preset="dialog" title="题目详情" style="width: 700px;">
      <div v-if="currentQuestion">
        <n-space vertical size="large">
          <n-descriptions label-placement="left" :column="1" bordered>
            <n-descriptions-item label="题目类型">
              <n-tag :type="getTypeTagType(currentQuestion.type)">
                {{ getTypeLabel(currentQuestion.type) }}
              </n-tag>
            </n-descriptions-item>
            <n-descriptions-item label="所属科目">
              {{ getSubjectName(currentQuestion.subject_id) }}
            </n-descriptions-item>
            <n-descriptions-item label="题目内容">
              {{ currentQuestion.question }}
            </n-descriptions-item>
            <n-descriptions-item label="选项" v-if="currentQuestion.options && currentQuestion.options.length > 0">
              <n-space vertical size="small">
                <div v-for="(option, idx) in currentQuestion.options" :key="idx">
                  {{ option }}
                </div>
              </n-space>
            </n-descriptions-item>
            <n-descriptions-item label="正确答案">
              <n-text type="success" strong>{{ currentQuestion.answer }}</n-text>
            </n-descriptions-item>
            <n-descriptions-item label="题目解析">
              {{ currentQuestion.analysis }}
            </n-descriptions-item>
            <n-descriptions-item label="创建时间">
              {{ currentQuestion.created_at }}
            </n-descriptions-item>
          </n-descriptions>
        </n-space>
      </div>
    </n-modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useMessage, useDialog } from 'naive-ui'
import { questionApi, subjectApi } from '@/api'
import {
  SearchOutline,
  RefreshOutline,
  EyeOutline,
  TrashOutline
} from '@vicons/ionicons5'

const message = useMessage()
const dialog = useDialog()

const userId = ref(1)
const loading = ref(false)
const questions = ref([])
const subjects = ref([])
const filterSubjectId = ref(null)
const filterType = ref(null)
const searchKeyword = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const showDetailModal = ref(false)
const currentQuestion = ref(null)

// 题型选项
const typeOptions = [
  { label: '单选题', value: 'single' },
  { label: '多选题', value: 'multiple' },
  { label: '判断题', value: 'judge' },
  { label: '填空题', value: 'fill' }
]

// 科目选项
const subjectOptions = computed(() => {
  return subjects.value.map(s => ({
    label: s.name,
    value: s.id
  }))
})

// 统计数据
const totalCount = computed(() => questions.value.length)
const typeCount = computed(() => {
  const count = {}
  questions.value.forEach(q => {
    count[q.type] = (count[q.type] || 0) + 1
  })
  return count
})

// 分页
const pageCount = computed(() => Math.ceil(totalCount.value / pageSize.value))
const paginatedQuestions = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return questions.value.slice(start, end)
})

// 获取题型标签类型
const getTypeTagType = (type) => {
  const map = {
    single: 'info',
    multiple: 'success',
    judge: 'warning',
    fill: 'error'
  }
  return map[type] || 'default'
}

// 获取题型标签文本
const getTypeLabel = (type) => {
  const map = {
    single: '单选',
    multiple: '多选',
    judge: '判断',
    fill: '填空'
  }
  return map[type] || type
}

// 获取科目名称
const getSubjectName = (subjectId) => {
  const subject = subjects.value.find(s => s.id === subjectId)
  return subject ? subject.name : '未知科目'
}

// 加载科目列表
const loadSubjects = async () => {
  try {
    subjects.value = await subjectApi.list(userId.value)
  } catch (error) {
    message.error('加载科目列表失败')
  }
}

// 加载题目列表
const loadQuestions = async () => {
  loading.value = true
  try {
    const params = {
      user_id: userId.value
    }
    
    if (filterSubjectId.value) {
      params.subject_id = filterSubjectId.value
    }
    
    if (filterType.value) {
      params.question_type = filterType.value
    }
    
    // 获取所有题目（后续可以改为服务器端分页）
    const allQuestions = filterSubjectId.value
      ? await questionApi.list(params)
      : []
    
    // 如果没有选择科目，获取所有科目的题目
    if (!filterSubjectId.value && subjects.value.length > 0) {
      const promises = subjects.value.map(subject =>
        questionApi.list({ user_id: userId.value, subject_id: subject.id })
      )
      const results = await Promise.all(promises)
      questions.value = results.flat()
    } else {
      questions.value = allQuestions
    }
    
    // 客户端题型过滤
    if (filterType.value) {
      questions.value = questions.value.filter(q => q.type === filterType.value)
    }
    
    // 客户端搜索过滤
    if (searchKeyword.value) {
      const keyword = searchKeyword.value.toLowerCase()
      questions.value = questions.value.filter(q =>
        q.question.toLowerCase().includes(keyword) ||
        q.answer.toLowerCase().includes(keyword) ||
        q.analysis.toLowerCase().includes(keyword)
      )
    }
    
    currentPage.value = 1
  } catch (error) {
    message.error(error.message || '加载题目失败')
  } finally {
    loading.value = false
  }
}

// 重置筛选
const handleReset = () => {
  filterSubjectId.value = null
  filterType.value = null
  searchKeyword.value = ''
  loadQuestions()
}

// 查看题目详情
const handleView = (question) => {
  currentQuestion.value = question
  showDetailModal.value = true
}

// 删除题目
const handleDelete = (question) => {
  dialog.warning({
    title: '确认删除',
    content: `确定要删除题目「${question.question.substring(0, 30)}...」吗？`,
    positiveText: '确定',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        await questionApi.delete(question.id)
        message.success('删除成功')
        loadQuestions()
      } catch (error) {
        message.error(error.message || '删除失败')
      }
    }
  })
}

// 分页处理
const handlePageChange = (page) => {
  currentPage.value = page
}

const handlePageSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
}

onMounted(() => {
  loadSubjects().then(() => {
    loadQuestions()
  })
})
</script>

<style scoped>
:deep(.n-list-item) {
  padding: 16px;
}

:deep(.n-thing-header) {
  margin-bottom: 8px;
}
</style>
