<template>
  <n-config-provider :theme-overrides="themeOverrides">
    <n-message-provider>
      <n-dialog-provider>
        <n-notification-provider>
          <!-- 未登录显示登录弹窗 -->
          <div v-if="!isLoggedIn" style="height: 100vh; display: flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
            <n-card style="width: 400px; border-radius: 12px;" :bordered="false">
              <n-tabs v-model:value="authTab" type="segment" animated>
                <!-- 登录标签页 -->
                <n-tab-pane name="login" tab="登录">
                  <n-form ref="loginFormRef" :model="loginForm" :rules="loginRules" style="margin-top: 20px;">
                    <n-form-item path="username" label="用户名">
                      <n-input 
                        v-model:value="loginForm.username" 
                        placeholder="请输入用户名"
                        @keyup.enter="handleLogin"
                      />
                    </n-form-item>
                    <n-form-item path="password" label="密码">
                      <n-input 
                        v-model:value="loginForm.password" 
                        type="password" 
                        show-password-on="click"
                        placeholder="请输入密码"
                        @keyup.enter="handleLogin"
                      />
                    </n-form-item>
                    <n-button 
                      type="primary" 
                      block 
                      :loading="loading"
                      @click="handleLogin"
                    >
                      登录
                    </n-button>
                  </n-form>
                </n-tab-pane>
                
                <!-- 注册标签页 -->
                <n-tab-pane name="register" tab="注册">
                  <n-form ref="registerFormRef" :model="registerForm" :rules="registerRules" style="margin-top: 20px;">
                    <n-form-item path="username" label="用户名">
                      <n-input 
                        v-model:value="registerForm.username" 
                        placeholder="3-50个字符"
                      />
                    </n-form-item>
                    <n-form-item path="password" label="密码">
                      <n-input 
                        v-model:value="registerForm.password" 
                        type="password" 
                        show-password-on="click"
                        placeholder="至少6个字符"
                      />
                    </n-form-item>
                    <n-form-item path="confirmPassword" label="确认密码">
                      <n-input 
                        v-model:value="registerForm.confirmPassword" 
                        type="password" 
                        show-password-on="click"
                        placeholder="再次输入密码"
                        @keyup.enter="handleRegister"
                      />
                    </n-form-item>
                    <n-button 
                      type="primary" 
                      block 
                      :loading="loading"
                      @click="handleRegister"
                    >
                      注册
                    </n-button>
                  </n-form>
                </n-tab-pane>
              </n-tabs>
            </n-card>
          </div>

          <!-- 已登录显示主界面 -->
          <n-layout v-else style="height: 100vh">
            <n-layout-header bordered style="height: 64px; padding: 0 24px; display: flex; align-items: center;">
              <div style="display: flex; align-items: center; gap: 12px; flex: 1;">
                <img src="./assets/logo.svg" alt="Logo" style="width: 40px; height: 40px;" />
                <h2 style="margin: 0;">神阁卷藏</h2>
              </div>
              <n-space>
                <n-button @click="showSystemInfo">
                  <template #icon>
                    <n-icon><information-circle-outline /></n-icon>
                  </template>
                  系统信息
                </n-button>
                <n-tag type="info">{{ currentUser?.username }}</n-tag>
                <n-button text @click="handleLogout">
                  <template #icon>
                    <n-icon><log-out-outline /></n-icon>
                  </template>
                  退出
                </n-button>
              </n-space>
            </n-layout-header>
            
            <n-layout has-sider style="height: calc(100vh - 64px)">
              <n-layout-sider
                bordered
                show-trigger
                collapse-mode="width"
                :collapsed-width="64"
                :width="240"
                :native-scrollbar="false"
              >
                <n-menu
                  :collapsed-width="64"
                  :collapsed-icon-size="22"
                  :options="menuOptions"
                  :value="activeKey"
                  @update:value="handleMenuSelect"
                />
              </n-layout-sider>
              
              <n-layout-content
                content-style="padding: 24px;"
                :native-scrollbar="false"
              >
                <router-view />
              </n-layout-content>
            </n-layout>
          </n-layout>
        </n-notification-provider>
      </n-dialog-provider>
    </n-message-provider>
  </n-config-provider>
</template>

<script setup>
import { ref, h, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { createDiscreteApi } from 'naive-ui'
import { 
  NIcon,
  NConfigProvider,
  NMessageProvider,
  NDialogProvider,
  NNotificationProvider,
  NLayout,
  NLayoutHeader,
  NLayoutSider,
  NLayoutContent,
  NMenu,
  NSpace,
  NTag,
  NButton,
  NCard,
  NTabs,
  NTabPane,
  NForm,
  NFormItem,
  NInput
} from 'naive-ui'
import {
  HomeOutline,
  BookOutline,
  CloudUploadOutline,
  CreateOutline,
  AlertCircleOutline,
  SettingsOutline,
  ServerOutline,
  LogOutOutline,
  LibraryOutline,
  TimeOutline,
  InformationCircleOutline
} from '@vicons/ionicons5'
import { authApi } from './api'

const router = useRouter()
const route = useRoute()

// 创建独立的 message 和 notification API
const { message, notification } = createDiscreteApi(['message', 'notification'])

// 认证状态
const isLoggedIn = ref(false)
const currentUser = ref(null)
const authTab = ref('login')
const loading = ref(false)

// 登录表单
const loginFormRef = ref(null)
const loginForm = ref({
  username: '',
  password: ''
})

const loginRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' }
  ]
}

// 注册表单
const registerFormRef = ref(null)
const registerForm = ref({
  username: '',
  password: '',
  confirmPassword: ''
})

const registerRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 50, message: '用户名长度为3-50个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少6个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    {
      validator: (rule, value) => {
        return value === registerForm.value.password
      },
      message: '两次输入的密码不一致',
      trigger: 'blur'
    }
  ]
}

// 登录处理
const handleLogin = async () => {
  try {
    await loginFormRef.value?.validate()
    loading.value = true
    
    const response = await authApi.login(loginForm.value)
    
    // 保存token和用户信息
    localStorage.setItem('token', response.token)
    localStorage.setItem('user', JSON.stringify(response.user))
    
    currentUser.value = response.user
    isLoggedIn.value = true
    
    message.success('登录成功！')
  } catch (error) {
    if (error.errors) return // 表单验证错误
    message.error(error.message || '登录失败')
  } finally {
    loading.value = false
  }
}

// 注册处理
const handleRegister = async () => {
  try {
    await registerFormRef.value?.validate()
    loading.value = true
    
    const response = await authApi.register({
      username: registerForm.value.username,
      password: registerForm.value.password
    })
    
    // 保存token和用户信息
    localStorage.setItem('token', response.token)
    localStorage.setItem('user', JSON.stringify(response.user))
    
    currentUser.value = response.user
    isLoggedIn.value = true
    
    message.success('注册成功！')
  } catch (error) {
    if (error.errors) return // 表单验证错误
    message.error(error.message || '注册失败')
  } finally {
    loading.value = false
  }
}

// 登出处理
const handleLogout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  currentUser.value = null
  isLoggedIn.value = false
  message.info('已退出登录')
}

// 显示系统信息
const showSystemInfo = () => {
  notification.info({
    title: '系统信息',
    content: '版本：v1.0.0\n作者：程序员Eighteen\n联系方式：QQ邮箱：3273495516@qq.com',
    meta: '神阁卷藏 - AI智能期末复习系统',
    duration: 5000,
    keepAliveOnHover: true
  })
}

// 初始化检查登录状态
onMounted(() => {
  const token = localStorage.getItem('token')
  const userStr = localStorage.getItem('user')
  
  if (token && userStr) {
    try {
      currentUser.value = JSON.parse(userStr)
      isLoggedIn.value = true
    } catch (error) {
      // 解析失败，清除数据
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    }
  }
})

// 当前用户ID（用于API调用）
const currentUserId = computed(() => currentUser.value?.id || 1)

// 当前激活的菜单项
const activeKey = computed(() => route.path)

// 主题配置
const themeOverrides = {
  common: {
    primaryColor: '#18a058',
    primaryColorHover: '#36ad6a',
    primaryColorPressed: '#0c7a43'
  }
}

// 渲染图标
const renderIcon = (icon) => {
  return () => h(NIcon, null, { default: () => h(icon) })
}

// 菜单选项
const menuOptions = [
  {
    label: '首页',
    key: '/',
    icon: renderIcon(HomeOutline)
  },
  {
    label: '科目管理',
    key: '/subjects',
    icon: renderIcon(BookOutline)
  },
  {
    label: '题库管理',
    key: '/question-bank',
    icon: renderIcon(LibraryOutline)
  },
  {
    label: '导入题目',
    key: '/import',
    icon: renderIcon(CloudUploadOutline)
  },
  {
    label: '开始练习',
    key: '/practice',
    icon: renderIcon(CreateOutline)
  },
  {
    label: '错题集',
    key: '/errors',
    icon: renderIcon(AlertCircleOutline)
  },
  {
    label: '做题记录',
    key: '/practice-history',
    icon: renderIcon(TimeOutline)
  },
  {
    type: 'divider'
  },
  {
    label: '配置',
    key: 'config',
    icon: renderIcon(SettingsOutline),
    children: [
      {
        label: 'AI 模型配置',
        key: '/model-config'
      },
      {
        label: '数据库配置',
        key: '/db-config'
      }
    ]
  }
]

// 菜单选择处理
const handleMenuSelect = (key) => {
  router.push(key)
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

#app {
  height: 100vh;
}
</style>
