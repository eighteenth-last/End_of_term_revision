<template>
  <div>
    <n-page-header title="AI 模型配置" subtitle="配置你的 AI 模型（支持任何 OpenAI 兼容 API）">
      <template #extra>
        <n-button type="primary" @click="showModal = true">
          <template #icon>
            <n-icon><add-outline /></n-icon>
          </template>
          添加模型配置
        </n-button>
      </template>
    </n-page-header>

    <n-spin :show="loading" style="margin-top: 24px;">
      <n-empty
        v-if="models.length === 0"
        description="还没有配置 AI 模型，请先添加一个配置"
        style="margin-top: 60px;"
      />

      <div v-else style="display: flex; flex-wrap: wrap; gap: 20px; margin-top: 20px;">
        <n-card
          v-for="model in models"
          :key="model.id"
          hoverable
          :style="{ width: '420px', height: '190px' }"
        >
          <template #header>
            <div style="display: flex; align-items: center; gap: 12px;">
              <n-avatar size="small">
                <n-icon><cube-outline /></n-icon>
              </n-avatar>
              <span style="flex: 1; font-weight: 600;">{{ model.model_name }}</span>
            </div>
          </template>
          <template #header-extra>
            <n-space :size="8">
              <n-button text @click="editModel(model)">
                <n-icon :size="20"><create-outline /></n-icon>
              </n-button>
              <n-button text type="error" @click="deleteModel(model.id)">
                <n-icon :size="20"><trash-outline /></n-icon>
              </n-button>
            </n-space>
          </template>
          <n-space vertical :size="8">
            <div>
              <n-text depth="3" style="font-size: 13px;">API: {{ model.base_url }}</n-text>
            </div>
            <div>
              <n-text depth="3" style="font-size: 13px;">Key: {{ maskApiKey(model.api_key) }}</n-text>
            </div>
            <div>
              <n-text depth="3" style="font-size: 13px;">创建时间: {{ model.created_at }}</n-text>
            </div>
          </n-space>
        </n-card>
      </div>
    </n-spin>

    <!-- 添加/编辑对话框 -->
    <n-modal v-model:show="showModal" preset="dialog" :title="isEdit ? '编辑模型配置' : '添加模型配置'">
      <n-form ref="formRef" :model="formData" :rules="rules" label-width="100px">
        <n-form-item label="模型名称" path="model_name">
          <n-input
            v-model:value="formData.model_name"
            placeholder="如：qwen2-7b, gpt-4"
          />
        </n-form-item>
        <n-form-item label="API 地址" path="base_url">
          <n-input
            v-model:value="formData.base_url"
            placeholder="如：https://api.example.com/v1"
          />
        </n-form-item>
        <n-form-item label="API 密钥" path="api_key">
          <n-input
            v-model:value="formData.api_key"
            type="password"
            show-password-on="click"
            placeholder="sk-xxxxxxxxxxxxxxxx"
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
import { ref, onMounted } from 'vue'
import { useMessage, useDialog } from 'naive-ui'
import { modelApi } from '@/api'
import { AddOutline, CubeOutline, CreateOutline, TrashOutline } from '@vicons/ionicons5'
import { useUserStore } from '@/stores/user'
import { storeToRefs } from 'pinia'

const message = useMessage()
const dialog = useDialog()
const loading = ref(false)
const submitting = ref(false)
const showModal = ref(false)
const isEdit = ref(false)
const userStore = useUserStore()
const { userId } = storeToRefs(userStore)
const models = ref([])

const formRef = ref(null)
const formData = ref({
  model_name: '',
  base_url: '',
  api_key: ''
})

const rules = {
  model_name: [{ required: true, message: '请输入模型名称', trigger: 'blur' }],
  base_url: [{ required: true, message: '请输入 API 地址', trigger: 'blur' }],
  api_key: [{ required: true, message: '请输入 API 密钥', trigger: 'blur' }]
}

const maskApiKey = (key) => {
  if (!key || key.length < 8) return '***'
  return key.substring(0, 7) + '...' + key.substring(key.length - 4)
}

const loadModels = async () => {
  loading.value = true
  try {
    models.value = await modelApi.list(userId.value)
  } catch (error) {
    message.error(error.message || '加载模型配置失败')
  } finally {
    loading.value = false
  }
}

const editModel = (model) => {
  isEdit.value = true
  formData.value = {
    id: model.id,
    model_name: model.model_name,
    base_url: model.base_url,
    api_key: model.api_key
  }
  showModal.value = true
}

const handleSubmit = async () => {
  try {
    await formRef.value?.validate()
    submitting.value = true

    if (isEdit.value) {
      await modelApi.update(formData.value.id, {
        model_name: formData.value.model_name,
        base_url: formData.value.base_url,
        api_key: formData.value.api_key
      })
      message.success('模型配置更新成功')
    } else {
      await modelApi.create({
        user_id: userId.value,
        model_name: formData.value.model_name,
        base_url: formData.value.base_url,
        api_key: formData.value.api_key
      })
      message.success('模型配置添加成功')
    }

    showModal.value = false
    formData.value = { model_name: '', base_url: '', api_key: '' }
    isEdit.value = false
    loadModels()
  } catch (error) {
    if (error.message) {
      message.error(error.message)
    }
  } finally {
    submitting.value = false
  }
}

const deleteModel = (modelId) => {
  dialog.warning({
    title: '确认删除',
    content: '确定要删除这个模型配置吗？',
    positiveText: '确定',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        await modelApi.delete(modelId)
        message.success('删除成功')
        loadModels()
      } catch (error) {
        message.error(error.message || '删除失败')
      }
    }
  })
}

onMounted(() => {
  loadModels()
})
</script>
