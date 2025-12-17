<template>
  <div>
    <n-page-header title="数据库配置" subtitle="配置你的数据库连接信息">
      <template #extra>
        <n-button type="primary" @click="showModal = true">
          <template #icon>
            <n-icon><add-outline /></n-icon>
          </template>
          添加数据库配置
        </n-button>
      </template>
    </n-page-header>

    <n-spin :show="loading" style="margin-top: 24px;">
      <n-empty
        v-if="configs.length === 0"
        description="还没有配置数据库，请先添加一个配置"
        style="margin-top: 60px;"
      />

      <n-list v-else hoverable>
        <n-list-item v-for="config in configs" :key="config.id">
          <n-thing>
            <template #avatar>
              <n-avatar>
                <n-icon><server-outline /></n-icon>
              </n-avatar>
            </template>
            <template #header>
              {{ config.db_name }}
              <n-tag v-if="config.is_active" type="success" size="small" style="margin-left: 12px;">
                当前激活
              </n-tag>
            </template>
            <template #header-extra>
              <n-space>
                <n-button
                  v-if="!config.is_active"
                  size="small"
                  type="primary"
                  @click="activateConfig(config.id)"
                >
                  激活
                </n-button>
                <n-button text @click="editConfig(config)">
                  <n-icon><create-outline /></n-icon>
                </n-button>
                <n-button
                  text
                  type="error"
                  :disabled="config.is_active"
                  @click="deleteConfig(config.id)"
                >
                  <n-icon><trash-outline /></n-icon>
                </n-button>
              </n-space>
            </template>
            <template #description>
              <n-space vertical size="small">
                <n-text depth="3">主机: {{ config.db_host }}:{{ config.db_port }}</n-text>
                <n-text depth="3">用户: {{ config.db_user }}</n-text>
                <n-text depth="3">创建时间: {{ config.created_at }}</n-text>
              </n-space>
            </template>
          </n-thing>
        </n-list-item>
      </n-list>
    </n-spin>

    <!-- 添加/编辑对话框 -->
    <n-modal v-model:show="showModal" preset="dialog" :title="isEdit ? '编辑数据库配置' : '添加数据库配置'">
      <n-form ref="formRef" :model="formData" :rules="rules" label-width="100px">
        <n-form-item label="主机地址" path="db_host">
          <n-input
            v-model:value="formData.db_host"
            placeholder="如：localhost 或 192.168.1.100"
          />
        </n-form-item>
        <n-form-item label="端口号" path="db_port">
          <n-input-number
            v-model:value="formData.db_port"
            :min="1"
            :max="65535"
            placeholder="如：3306"
            style="width: 100%;"
          />
        </n-form-item>
        <n-form-item label="用户名" path="db_user">
          <n-input
            v-model:value="formData.db_user"
            placeholder="数据库用户名"
          />
        </n-form-item>
        <n-form-item label="密码" path="db_password">
          <n-input
            v-model:value="formData.db_password"
            type="password"
            show-password-on="click"
            placeholder="数据库密码"
          />
        </n-form-item>
        <n-form-item label="数据库名" path="db_name">
          <n-input
            v-model:value="formData.db_name"
            placeholder="数据库名称"
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
import { dbConfigApi } from '@/api'
import { AddOutline, ServerOutline, CreateOutline, TrashOutline } from '@vicons/ionicons5'

const message = useMessage()
const dialog = useDialog()
const loading = ref(false)
const submitting = ref(false)
const showModal = ref(false)
const isEdit = ref(false)
const userId = ref(1)
const configs = ref([])

const formRef = ref(null)
const formData = ref({
  db_host: 'localhost',
  db_port: 3306,
  db_user: '',
  db_password: '',
  db_name: ''
})

const rules = {
  db_host: [{ required: true, message: '请输入主机地址', trigger: 'blur' }],
  db_port: [{ required: true, type: 'number', message: '请输入端口号', trigger: 'blur' }],
  db_user: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  db_password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  db_name: [{ required: true, message: '请输入数据库名', trigger: 'blur' }]
}

const loadConfigs = async () => {
  loading.value = true
  try {
    configs.value = await dbConfigApi.list(userId.value)
  } catch (error) {
    message.error(error.message || '加载数据库配置失败')
  } finally {
    loading.value = false
  }
}

const editConfig = (config) => {
  isEdit.value = true
  formData.value = {
    id: config.id,
    db_host: config.db_host,
    db_port: config.db_port,
    db_user: config.db_user,
    db_password: config.db_password,
    db_name: config.db_name
  }
  showModal.value = true
}

const handleSubmit = async () => {
  try {
    await formRef.value?.validate()
    submitting.value = true

    if (isEdit.value) {
      await dbConfigApi.update(formData.value.id, {
        db_host: formData.value.db_host,
        db_port: formData.value.db_port,
        db_user: formData.value.db_user,
        db_password: formData.value.db_password,
        db_name: formData.value.db_name
      })
      message.success('数据库配置更新成功')
    } else {
      await dbConfigApi.create({
        user_id: userId.value,
        db_host: formData.value.db_host,
        db_port: formData.value.db_port,
        db_user: formData.value.db_user,
        db_password: formData.value.db_password,
        db_name: formData.value.db_name
      })
      message.success('数据库配置添加成功')
    }

    showModal.value = false
    formData.value = {
      db_host: 'localhost',
      db_port: 3306,
      db_user: '',
      db_password: '',
      db_name: ''
    }
    isEdit.value = false
    loadConfigs()
  } catch (error) {
    if (error.message) {
      message.error(error.message)
    }
  } finally {
    submitting.value = false
  }
}

const activateConfig = async (configId) => {
  try {
    await dbConfigApi.activate(configId, userId.value)
    message.success('数据库配置已激活')
    loadConfigs()
  } catch (error) {
    message.error(error.message || '激活失败')
  }
}

const deleteConfig = (configId) => {
  dialog.warning({
    title: '确认删除',
    content: '确定要删除这个数据库配置吗？',
    positiveText: '确定',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        await dbConfigApi.delete(configId)
        message.success('删除成功')
        loadConfigs()
      } catch (error) {
        message.error(error.message || '删除失败')
      }
    }
  })
}

onMounted(() => {
  loadConfigs()
})
</script>
