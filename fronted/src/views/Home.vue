<template>
  <div>
    <n-page-header title="首页" subtitle="查看你的学习统计数据">
      <template #extra>
        <n-space>
          <n-button @click="loadData" :loading="loading">
            <template #icon>
              <n-icon><refresh-outline /></n-icon>
            </template>
            刷新
          </n-button>
        </n-space>
      </template>
    </n-page-header>

    <n-spin :show="loading">
      <n-space vertical size="large" style="margin-top: 24px;">
        <!-- 今日统计 -->
        <n-card title="📅 今日统计" hoverable>
          <n-grid cols="4" x-gap="12">
            <n-gi>
              <n-statistic label="练习题数" :value="stats.today.total_count" />
            </n-gi>
            <n-gi>
              <n-statistic label="正确题数" :value="stats.today.correct_count">
                <template #suffix>
                  <n-text type="success">题</n-text>
                </template>
              </n-statistic>
            </n-gi>
            <n-gi>
              <n-statistic label="错误题数" :value="stats.today.wrong_count">
                <template #suffix>
                  <n-text type="error">题</n-text>
                </template>
              </n-statistic>
            </n-gi>
            <n-gi>
              <n-statistic label="正确率">
                <template #default>
                  <n-text :type="getAccuracyType(stats.today.accuracy)">
                    {{ stats.today.accuracy }}%
                  </n-text>
                </template>
              </n-statistic>
            </n-gi>
          </n-grid>
          <n-divider />
          <n-space align="center">
            <span>今日等级：</span>
            <n-tag :type="getGradeType(stats.today.grade)" size="large">
              {{ stats.today.grade }}
            </n-tag>
          </n-space>
        </n-card>

        <!-- 本周统计 -->
        <n-card title="📊 本周统计" hoverable>
          <n-grid cols="4" x-gap="12">
            <n-gi>
              <n-statistic label="练习题数" :value="stats.week.total_count" />
            </n-gi>
            <n-gi>
              <n-statistic label="正确题数" :value="stats.week.correct_count">
                <template #suffix>
                  <n-text type="success">题</n-text>
                </template>
              </n-statistic>
            </n-gi>
            <n-gi>
              <n-statistic label="错误题数" :value="stats.week.wrong_count">
                <template #suffix>
                  <n-text type="error">题</n-text>
                </template>
              </n-statistic>
            </n-gi>
            <n-gi>
              <n-statistic label="正确率">
                <template #default>
                  <n-text :type="getAccuracyType(stats.week.accuracy)">
                    {{ stats.week.accuracy }}%
                  </n-text>
                </template>
              </n-statistic>
            </n-gi>
          </n-grid>
          <n-divider />
          <n-space align="center">
            <span>本周等级：</span>
            <n-tag :type="getGradeType(stats.week.grade)" size="large">
              {{ stats.week.grade }}
            </n-tag>
          </n-space>
        </n-card>

        <!-- 全部统计 -->
        <n-card title="📈 全部统计" hoverable>
          <n-grid cols="4" x-gap="12">
            <n-gi>
              <n-statistic label="总练习题数" :value="stats.all.total_count" />
            </n-gi>
            <n-gi>
              <n-statistic label="总正确题数" :value="stats.all.correct_count">
                <template #suffix>
                  <n-text type="success">题</n-text>
                </template>
              </n-statistic>
            </n-gi>
            <n-gi>
              <n-statistic label="总错误题数" :value="stats.all.wrong_count">
                <template #suffix>
                  <n-text type="error">题</n-text>
                </template>
              </n-statistic>
            </n-gi>
            <n-gi>
              <n-statistic label="总正确率">
                <template #default>
                  <n-text :type="getAccuracyType(stats.all.accuracy)">
                    {{ stats.all.accuracy }}%
                  </n-text>
                </template>
              </n-statistic>
            </n-gi>
          </n-grid>
          <n-divider />
          <n-space align="center">
            <span>总体等级：</span>
            <n-tag :type="getGradeType(stats.all.grade)" size="large">
              {{ stats.all.grade }}
            </n-tag>
            <n-divider vertical />
            <span>连续学习：</span>
            <n-tag type="info" size="large">
              {{ stats.consecutive_days }} 天
            </n-tag>
          </n-space>
        </n-card>

        <!-- 等级说明 -->
        <n-card title="📝 等级评价标准">
          <n-space>
            <n-tag type="success">A: ≥90%</n-tag>
            <n-tag type="info">B: 80-89%</n-tag>
            <n-tag type="warning">C: 70-79%</n-tag>
            <n-tag type="warning">D: 60-69%</n-tag>
            <n-tag type="error">F: <60%</n-tag>
          </n-space>
        </n-card>

        <!-- 使用教程 -->
        <n-card title="📚 使用教程" hoverable>
          <n-collapse>
            <n-collapse-item title="1️⃣ 科目管理" name="1">
              <n-space vertical>
                <n-text>• 在「科目管理」页面，点击「添加科目」创建新科目</n-text>
                <n-text>• 每个科目可以单独管理题目和练习记录</n-text>
                <n-text>• 支持编辑科目名称和删除科目（删除后相关题目和记录也会被删除）</n-text>
              </n-space>
            </n-collapse-item>

            <n-collapse-item title="2️⃣ 导入题目（AI智能识别）" name="2">
              <n-space vertical>
                <n-text strong type="success">✨ 核心功能：利用 AI 视觉模型直接识别图片中的题目</n-text>
                <n-divider style="margin: 8px 0;" />
                <n-text>• 在「导入题目」页面，选择对应的科目</n-text>
                <n-text>• 上传包含题目的图片（支持：JPG、PNG、JPEG、BMP、WEBP）</n-text>
                <n-text>• AI 会自动识别图片中的题目类型（单选/多选/判断）、题干、选项和答案</n-text>
                <n-text>• 识别完成后可预览并确认导入，支持编辑题目内容和答案解析</n-text>
                <n-text depth="3">💡 提示：图片清晰度越高，识别准确率越高</n-text>
              </n-space>
            </n-collapse-item>

            <n-collapse-item title="3️⃣ 题库管理" name="3">
              <n-space vertical>
                <n-text>• 在「题库管理」页面可查看所有已导入的题目</n-text>
                <n-text>• 支持按科目、题型筛选题目</n-text>
                <n-text>• 支持关键词搜索题目内容</n-text>
                <n-text>• 可以编辑或删除题目</n-text>
                <n-text>• 每页显示 20 道题，支持翻页查看</n-text>
              </n-space>
            </n-collapse-item>

            <n-collapse-item title="4️⃣ 开始练习" name="4">
              <n-space vertical>
                <n-text>• 在「开始练习」页面选择科目</n-text>
                <n-text>• 所有题目一次性显示，无需逐题翻页</n-text>
                <n-text>• 右侧答题卡可快速跳转到指定题目</n-text>
                <n-text>• 完成答题后点击「提交答案」查看成绩</n-text>
                <n-text>• 系统自动记录每次练习的详细数据（正确率、等级、用时等）</n-text>
              </n-space>
            </n-collapse-item>

            <n-collapse-item title="5️⃣ 错题集" name="5">
              <n-space vertical>
                <n-text>• 在「错题集」页面查看所有答错的题目</n-text>
                <n-text>• 卡片式布局，每道错题独立展示</n-text>
                <n-text>• 显示正确答案和答案解析</n-text>
                <n-text>• 可以进行「错题练习」，针对性复习薄弱环节</n-text>
                <n-text>• 答对的题目会自动从错题集中移除</n-text>
              </n-space>
            </n-collapse-item>

            <n-collapse-item title="6️⃣ 做题记录" name="6">
              <n-space vertical>
                <n-text>• 在「做题记录」页面查看每次练习的详细信息</n-text>
                <n-text>• 记录包括：练习时间、科目、题数、正确率、等级</n-text>
                <n-text>• 点击「查看详情」可以查看每道题的答题情况</n-text>
                <n-text>• 详情中显示：题目内容、你的答案、正确答案、是否正确、答案解析</n-text>
                <n-text>• 支持按科目筛选历史记录</n-text>
              </n-space>
            </n-collapse-item>

            <n-collapse-item title="7️⃣ 配置设置" name="7">
              <n-space vertical>
                <n-text>• 「AI 模型配置」：配置 OpenAI API 密钥和基础 URL</n-text>
                <n-text depth="3">⚠️ 注意：配置 API Key 后即可使用 AI 解析功能</n-text>
              </n-space>
            </n-collapse-item>

            <n-collapse-item title="💡 学习建议" name="8">
              <n-space vertical>
                <n-text type="info">1. 定期导入新题目，保持题库更新</n-text>
                <n-text type="info">2. 每天坚持练习，查看首页统计了解学习进度</n-text>
                <n-text type="info">3. 重点攻克错题集，提高薄弱环节</n-text>
                <n-text type="info">4. 利用做题记录功能，追踪自己的进步</n-text>
                <n-text type="info">5. 争取达到 A 级（正确率 ≥90%），确保知识点掌握扎实</n-text>
              </n-space>
            </n-collapse-item>
          </n-collapse>
        </n-card>
      </n-space>
    </n-spin>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useMessage } from 'naive-ui'
import { practiceApi } from '@/api'
import { RefreshOutline } from '@vicons/ionicons5'
import { useUserStore } from '@/stores/user'
import { storeToRefs } from 'pinia'

const message = useMessage()
const loading = ref(false)
const userStore = useUserStore()
const { userId } = storeToRefs(userStore)

const stats = ref({
  today: {
    total_count: 0,
    correct_count: 0,
    wrong_count: 0,
    accuracy: 0,
    grade: 'F'
  },
  week: {
    total_count: 0,
    correct_count: 0,
    wrong_count: 0,
    accuracy: 0,
    grade: 'F'
  },
  all: {
    total_count: 0,
    correct_count: 0,
    wrong_count: 0,
    accuracy: 0,
    grade: 'F'
  },
  consecutive_days: 0
})

// 获取正确率颜色类型
const getAccuracyType = (accuracy) => {
  if (accuracy >= 90) return 'success'
  if (accuracy >= 80) return 'info'
  if (accuracy >= 70) return 'warning'
  return 'error'
}

// 获取等级颜色类型
const getGradeType = (grade) => {
  if (grade === 'A') return 'success'
  if (grade === 'B') return 'info'
  if (grade === 'C' || grade === 'D') return 'warning'
  return 'error'
}

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    const data = await practiceApi.homeStats(userId.value)
    stats.value = data
  } catch (error) {
    message.error(error.message || '加载统计数据失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>
