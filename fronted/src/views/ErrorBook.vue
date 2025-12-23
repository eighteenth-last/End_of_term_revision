<template>
  <div>
    <n-page-header title="错题集" subtitle="查看和管理你的错题">
      <template #extra>
        <n-space>
          <n-button type="primary" @click="$router.push('/error-practice')">
            <template #icon>
              <n-icon><create-outline /></n-icon>
            </template>
            错题练习
          </n-button>
        </n-space>
      </template>
    </n-page-header>

    <n-card style="margin-top: 24px;">
      <n-space vertical size="large">
        <!-- 筛选 -->
        <n-space>
          <n-select
            v-model:value="filterSubject"
            :options="subjectOptions"
            placeholder="筛选科目"
            clearable
            style="width: 200px;"
            @update:value="loadErrors"
          />
          <n-text depth="3">共 {{ errorCount }} 道错题</n-text>
        </n-space>

        <!-- 错题列表 - 卡片网格布局 -->
        <n-spin :show="loading">
          <n-empty
            v-if="errors.length === 0"
            description="太棒了！目前没有错题"
            style="margin-top: 60px;"
          />

          <div v-else style="display: grid; grid-template-columns: repeat(auto-fill, minmax(450px, 475px)); gap: 24px; padding: 8px;">
            <n-card
              v-for="(error, index) in errors"
              :key="error.error_id"
              hoverable
              style="height: 460px; display: flex; flex-direction: column;"
            >
              <!-- 卡片头部 -->
              <template #header>
                <n-space align="center">
                  <n-avatar size="small" style="background-color: #18a058;">
                    {{ index + 1 }}
                  </n-avatar>
                  <n-text strong>{{ getTypeLabel(error.type) }}</n-text>
                  <n-tag type="error" size="small">错误 {{ error.wrong_count }} 次</n-tag>
                </n-space>
              </template>

              <!-- 卡片操作区 -->
              <template #header-extra>
                <n-button
                  text
                  type="error"
                  size="small"
                  @click.stop="removeError(error.error_id)"
                  style="margin-left: 16px;"
                >
                  移除
                </n-button>
              </template>

              <!-- 卡片内容 -->
              <n-scrollbar style="max-height: 330px;">
                <n-space vertical size="large">
                  <!-- 题目 -->
                  <div style="font-weight: 500; font-size: 15px; line-height: 1.6;">
                    <TableRenderer :content="error.question" />
                  </div>
                  
                  <!-- 选项 -->
                  <n-space v-if="error.type !== 'fill'" vertical size="small">
                    <div
                      v-for="(option, idx) in error.options"
                      :key="idx"
                      :style="{
                        color: isCorrectOption(option, error.answer) ? '#18a058' : 'inherit',
                        lineHeight: '1.8'
                      }"
                    >
                      <FormulaRenderer :content="option" />
                    </div>
                  </n-space>

                  <!-- 正确答案 -->
                  <n-space align="center">
                    <n-text depth="3">正确答案：</n-text>
                    <n-tag type="success" size="small">
                      <FormulaRenderer :content="error.answer" />
                    </n-tag>
                  </n-space>

                  <!-- 解析 -->
                  <n-collapse accordion>
                    <n-collapse-item title="查看解析" name="analysis">
                      <n-alert type="info" style="font-size: 14px;">
                        <FormulaRenderer :content="error.analysis" />
                      </n-alert>
                    </n-collapse-item>
                  </n-collapse>
                </n-space>
              </n-scrollbar>

              <!-- 卡片底部 -->
              <template #footer>
                <n-text depth="3" style="font-size: 12px;">
                  最后错误时间：{{ error.last_wrong_at }}
                </n-text>
              </template>
            </n-card>
          </div>
        </n-spin>
      </n-space>
    </n-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useMessage, useDialog } from 'naive-ui'
import { subjectApi, errorApi } from '@/api'
import { CreateOutline } from '@vicons/ionicons5'
import { useUserStore } from '@/stores/user'
import { storeToRefs } from 'pinia'
import FormulaRenderer from '@/components/FormulaRenderer.vue'
import TableRenderer from '@/components/TableRenderer.vue'

const message = useMessage()
const dialog = useDialog()
const userStore = useUserStore()
const { userId } = storeToRefs(userStore)
const loading = ref(false)
const subjects = ref([])
const errors = ref([])
const errorCount = ref(0)
const filterSubject = ref(null)

const subjectOptions = computed(() => {
  return subjects.value.map(s => ({
    label: s.name,
    value: s.id
  }))
})

const getTypeLabel = (type) => {
  const map = {
    single: '单选题',
    multiple: '多选题',
    judge: '判断题',
    fill: '填空题',
    major:'大型题'
  }
  return map[type] || type
}

const isCorrectOption = (option, answer) => {
  const optionValue = option.match(/^([A-Z])\./)?.[1] || option
  return answer.includes(optionValue)
}

const loadSubjects = async () => {
  try {
    subjects.value = await subjectApi.list(userId.value)
  } catch (error) {
    message.error(error.message || '加载科目列表失败')
  }
}

const loadErrors = async () => {
  loading.value = true
  try {
    const params = { user_id: userId.value }
    if (filterSubject.value) {
      params.subject_id = filterSubject.value
    }
    
    errors.value = await errorApi.list(params)
    
    const countData = await errorApi.count(params)
    errorCount.value = countData.count
  } catch (error) {
    message.error(error.message || '加载错题失败')
  } finally {
    loading.value = false
  }
}

const removeError = (errorId) => {
  dialog.warning({
    title: '确认移除',
    content: '确定要从错题集中移除这道题吗？',
    positiveText: '确定',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        await errorApi.remove(errorId)
        message.success('已移除')
        loadErrors()
      } catch (error) {
        message.error(error.message || '移除失败')
      }
    }
  })
}

onMounted(() => {
  loadSubjects()
  loadErrors()
})
</script>
