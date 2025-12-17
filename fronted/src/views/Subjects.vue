<template>
  <div>
    <n-page-header title="科目管理" subtitle="管理你的学习科目">
      <template #extra>
        <n-space>
          <n-button type="primary" @click="showModal = true">
            <template #icon>
              <n-icon><add-outline /></n-icon>
            </template>
            添加科目
          </n-button>
        </n-space>
      </template>
    </n-page-header>

    <n-spin :show="loading" style="margin-top: 24px;">
      <n-empty
        v-if="subjects.length === 0"
        description="还没有科目，快来添加一个吧！"
        style="margin-top: 60px;"
      />
      
      <div v-else style="display: grid; grid-template-columns: repeat(auto-fill, minmax(400px, 420px)); gap: 24px; padding: 8px; margin-top: 24px;">
        <n-card
          v-for="subject in subjects"
          :key="subject.id"
          hoverable
          style="height: 180px; display: flex; flex-direction: column;"
        >
          <template #header>
            <n-space align="center" justify="space-between" style="width: 100%;">
              <n-text strong style="font-size: 18px;">{{ subject.name }}</n-text>
            </n-space>
          </template>
          
          <template #header-extra>
            <n-dropdown :options="getActions(subject)" @select="(key) => handleAction(key, subject)">
              <n-button text circle>
                <template #icon>
                  <n-icon size="20"><ellipsis-horizontal-outline /></n-icon>
                </template>
              </n-button>
            </n-dropdown>
          </template>
          
          <n-space vertical style="flex: 1; justify-content: center;">
            <n-text depth="3" style="font-size: 14px;">
              创建时间：{{ subject.created_at }}
            </n-text>
          </n-space>
        </n-card>
      </div>
    </n-spin>

    <!-- 添加科目对话框 -->
    <n-modal v-model:show="showModal" preset="dialog" title="添加科目">
      <n-form ref="formRef" :model="formData" :rules="rules">
        <n-form-item label="科目名称" path="name">
          <n-input
            v-model:value="formData.name"
            placeholder="请输入科目名称，如：数学、英语"
            @keyup.enter="handleSubmit"
          />
        </n-form-item>
      </n-form>
      <template #action>
        <n-space>
          <n-button @click="showModal = false">取消</n-button>
          <n-button type="primary" @click="handleSubmit" :loading="submitting">
            确定
          </n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup>
import { ref, onMounted, h } from 'vue'
import { useMessage, useDialog } from 'naive-ui'
import { subjectApi } from '@/api'
import { AddOutline, EllipsisHorizontalOutline, TrashOutline } from '@vicons/ionicons5'
import { NIcon } from 'naive-ui'

const message = useMessage()
const dialog = useDialog()
const loading = ref(false)
const submitting = ref(false)
const showModal = ref(false)
const userId = ref(1)
const subjects = ref([])

const formRef = ref(null)
const formData = ref({
  name: ''
})

const rules = {
  name: [
    { required: true, message: '请输入科目名称', trigger: 'blur' }
  ]
}

// 获取操作菜单
const getActions = (subject) => [
  {
    label: '删除',
    key: 'delete',
    icon: () => h(NIcon, null, { default: () => h(TrashOutline) })
  }
]

// 处理操作
const handleAction = (key, subject) => {
  if (key === 'delete') {
    handleDelete(subject)
  }
}

// 加载科目列表
const loadSubjects = async () => {
  loading.value = true
  try {
    subjects.value = await subjectApi.list(userId.value)
  } catch (error) {
    message.error(error.message || '加载科目列表失败')
  } finally {
    loading.value = false
  }
}

// 提交表单
const handleSubmit = async () => {
  try {
    await formRef.value?.validate()
    submitting.value = true
    
    await subjectApi.create({
      name: formData.value.name,
      user_id: userId.value
    })
    
    message.success('科目添加成功')
    showModal.value = false
    formData.value.name = ''
    loadSubjects()
  } catch (error) {
    if (error.message) {
      message.error(error.message)
    }
  } finally {
    submitting.value = false
  }
}

// 删除科目
const handleDelete = (subject) => {
  dialog.warning({
    title: '确认删除',
    content: `确定要删除科目"${subject.name}"吗？删除后该科目下的所有题目也将被删除！`,
    positiveText: '确定',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        await subjectApi.delete(subject.id)
        message.success('科目删除成功')
        loadSubjects()
      } catch (error) {
        message.error(error.message || '删除失败')
      }
    }
  })
}

onMounted(() => {
  loadSubjects()
})
</script>
