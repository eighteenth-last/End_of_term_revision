<template>
  <div>
    <n-page-header title="导入题目" subtitle="通过文件、图片或文本导入题目，AI 自动解析">
    </n-page-header>

    <n-space vertical size="large" style="margin-top: 24px;">
      <!-- 选择科目 -->
      <n-card title="1. 选择科目">
        <n-select
          v-model:value="selectedSubject"
          :options="subjectOptions"
          placeholder="请选择科目"
          :loading="loadingSubjects"
        />
      </n-card>

      <!-- 导入方式选择 -->
      <n-card title="2. 选择导入方式">
        <n-tabs v-model:value="importType" type="segment">
          <n-tab-pane name="file" tab="文件导入">
            <n-space vertical style="margin-top: 16px;">
              <n-alert type="info">
                支持 PDF、Word、文本文件。AI 将自动识别题目、选项、答案和解析。
              </n-alert>
              <n-upload
                :custom-request="handleFileUpload"
                :show-file-list="false"
                :disabled="importing"
                accept=".pdf,.docx,.doc,.txt"
              >
                <n-upload-dragger>
                  <div style="margin-bottom: 12px;">
                    <n-icon size="48" :depth="3">
                      <document-text-outline />
                    </n-icon>
                  </div>
                  <n-text style="font-size: 16px;">
                    {{ importing ? '正在导入...' : '点击或拖拽文件到此区域上传' }}
                  </n-text>
                  <n-p depth="3" style="margin: 8px 0 0 0;">
                    支持 PDF、Word (.docx, .doc)、文本 (.txt) 格式
                  </n-p>
                </n-upload-dragger>
              </n-upload>
            </n-space>
          </n-tab-pane>

          <n-tab-pane name="image" tab="图片导入">
            <n-space vertical style="margin-top: 16px;">
              <n-alert type="info">
                支持 JPG、PNG 等图片格式。系统将使用 AI 视觉模型直接识别图片中的题目。
              </n-alert>
              
              <n-upload
                :custom-request="handleImageUpload"
                :show-file-list="false"
                :disabled="importing"
                accept="image/*"
              >
                <n-upload-dragger>
                  <div style="margin-bottom: 12px;">
                    <n-icon size="48" :depth="3">
                      <image-outline />
                    </n-icon>
                  </div>
                  <n-text style="font-size: 16px;">
                    {{ importing ? '正在导入...' : '点击或拖拽图片到此区域上传' }}
                  </n-text>
                  <n-p depth="3" style="margin: 8px 0 0 0;">
                    支持 JPG、PNG、BMP 等图片格式
                  </n-p>
                </n-upload-dragger>
              </n-upload>
            </n-space>
          </n-tab-pane>

          <n-tab-pane name="text" tab="文本导入">
            <n-space vertical style="margin-top: 16px;">
              <n-alert type="info">
                直接粘贴题目文本，AI 将自动解析题目结构。
              </n-alert>
              <n-input
                v-model:value="textContent"
                type="textarea"
                placeholder="请粘贴题目内容，例如：&#10;&#10;1. 1+1等于多少？&#10;A. 1&#10;B. 2&#10;C. 3&#10;D. 4&#10;答案：B&#10;解析：基础加法运算"
                :rows="10"
              />
              <n-button
                type="primary"
                :loading="importing"
                :disabled="!textContent || !selectedSubject"
                @click="handleTextImport"
                block
              >
                开始导入
              </n-button>
            </n-space>
          </n-tab-pane>
        </n-tabs>
      </n-card>

      <!-- 导入进度 -->
      <n-card v-if="importing" title="导入进度">
        <n-space vertical>
          <n-progress type="line" :percentage="100" processing />
          <n-text>正在使用 AI 解析题目，请稍候...</n-text>
          <n-alert type="warning" style="margin-top: 12px;">
            AI 识别可能需要 30-120 秒，请耐心等待，不要关闭页面
          </n-alert>
        </n-space>
      </n-card>
    </n-space>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { createDiscreteApi } from 'naive-ui'
import { subjectApi, importApi } from '@/api'
import { DocumentTextOutline, ImageOutline } from '@vicons/ionicons5'
import axios from 'axios'

const { message } = createDiscreteApi(['message'])
const userId = ref(1)
const importing = ref(false)
const loadingSubjects = ref(false)
const subjects = ref([])
const selectedSubject = ref(null)
const importType = ref('file')
const textContent = ref('')

// 科目选项
const subjectOptions = computed(() => {
  return subjects.value.map(s => ({
    label: s.name,
    value: s.id
  }))
})

// 加载科目列表
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

// 处理文件上传
const handleFileUpload = async ({ file }) => {
  if (!selectedSubject.value) {
    message.warning('请先选择科目')
    return
  }

  // 防止重复上传
  if (importing.value) {
    console.log('[前端] 正在导入中，跳过重复请求')
    return
  }

  importing.value = true
  try {
    const result = await importApi.fromFile(
      userId.value,
      selectedSubject.value,
      file.file
    )
    message.success(result.message || '导入成功')
  } catch (error) {
    message.error(error.message || '导入失败')
  } finally {
    importing.value = false
  }
}

// 处理图片上传
const handleImageUpload = async ({ file }) => {
  if (!selectedSubject.value) {
    message.warning('请先选择科目')
    return
  }

  // 防止重复上传
  if (importing.value) {
    console.log('[前端] 正在导入中，跳过重复请求')
    return
  }

  importing.value = true
  try {
    const result = await importApi.fromImage(
      userId.value,
      selectedSubject.value,
      file.file
    )
    message.success(result.message || '导入成功')
  } catch (error) {
    message.error(error.message || '导入失败')
  } finally {
    importing.value = false
  }
}

// 处理文本导入
const handleTextImport = async () => {
  if (!selectedSubject.value) {
    message.warning('请先选择科目')
    return
  }

  if (!textContent.value.trim()) {
    message.warning('请输入题目文本')
    return
  }

  importing.value = true
  try {
    const result = await importApi.fromText({
      user_id: userId.value,
      subject_id: selectedSubject.value,
      text: textContent.value
    })
    message.success(result.message || '导入成功')
    textContent.value = ''
  } catch (error) {
    message.error(error.message || '导入失败')
  } finally {
    importing.value = false
  }
}

onMounted(() => {
  loadSubjects()
})
</script>
