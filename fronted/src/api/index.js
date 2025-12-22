import axios from 'axios'

const request = axios.create({
  baseURL: '/api',
  timeout: 120000  // 全局超时改为 120 秒
})

// 请求拦截器 - 添加token
request.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    const message = error.response?.data?.detail || error.message || '请求失败'
    return Promise.reject(new Error(message))
  }
)

// ==================== 用户认证 API ====================
export const authApi = {
  // 用户注册
  register: (data) => request.post('/auth/register', data),

  // 用户登录
  login: (data) => request.post('/auth/login', data),

  // 获取当前用户
  me: (token) => request.get('/auth/me', { params: { token } }),

  // 用户登出
  logout: () => request.post('/auth/logout')
}

// ==================== 科目管理 API ====================
export const subjectApi = {
  // 创建科目
  create: (data) => request.post('/subjects/', data),

  // 获取科目列表
  list: (userId) => request.get('/subjects/', { params: { user_id: userId } }),

  // 获取单个科目
  get: (subjectId) => request.get(`/subjects/${subjectId}`),

  // 删除科目
  delete: (subjectId) => request.delete(`/subjects/${subjectId}`)
}

// ==================== 题目管理 API ====================
export const questionApi = {
  // 创建题目
  create: (data) => request.post('/questions/', data),

  // 获取题目列表
  list: (params) => request.get('/questions/', { params }),

  // 获取科目题型
  getTypes: (subjectId, userId) =>
    request.get(`/questions/types/${subjectId}`, { params: { user_id: userId } }),

  // 获取单个题目
  get: (questionId) => request.get(`/questions/${questionId}`),

  // 删除题目
  delete: (questionId) => request.delete(`/questions/${questionId}`)
}

// ==================== 题目导入 API ====================
export const importApi = {
  // 从文件导入
  fromFile: (userId, subjectId, file) => {
    const formData = new FormData()
    formData.append('user_id', userId)
    formData.append('subject_id', subjectId)
    formData.append('file', file)
    return request.post('/import/file', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 180000  // 文件导入单独设置 180 秒超时
    })
  },

  // 从图片导入
  fromImage: (userId, subjectId, image) => {
    const formData = new FormData()
    formData.append('user_id', userId)
    formData.append('subject_id', subjectId)
    formData.append('image', image)
    return request.post('/import/image', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 180000  // 图片导入单独设置 180 秒超时（AI 识别需要较长时间）
    })
  },

  // 从文本导入
  fromText: (data) => request.post('/import/text', data)
}

// ==================== 练习 API ====================
export const practiceApi = {
  // 开始练习
  start: (data) => request.post('/practice/start', data),

  // 提交答案
  submit: (data) => request.post('/practice/submit', data),

  // 今日统计
  todayStats: (userId) =>
    request.get('/practice/statistics/today', { params: { user_id: userId } }),

  // 本周统计
  weekStats: (userId) =>
    request.get('/practice/statistics/week', { params: { user_id: userId } }),

  // 全部统计
  allStats: (userId) =>
    request.get('/practice/statistics/all', { params: { user_id: userId } }),

  // 首页统计
  homeStats: (userId) =>
    request.get('/practice/statistics/home', { params: { user_id: userId } })
}

// ==================== 错题集 API ====================
export const errorApi = {
  // 获取错题列表
  list: (params) => request.get('/errors/', { params }),

  // 获取错题数量
  count: (params) => request.get('/errors/count', { params }),

  // 获取错题题型
  getTypes: (subjectId, userId) =>
    request.get(`/errors/types/${subjectId}`, { params: { user_id: userId } }),

  // 开始错题练习
  practice: (data) => request.post('/errors/practice', data),

  // 移除错题
  remove: (errorId) => request.delete(`/errors/${errorId}`)
}

// ==================== AI 模型配置 API ====================
export const modelApi = {
  // 创建模型配置
  create: (data) => request.post('/models/', data),

  // 获取模型配置列表
  list: (userId) => request.get('/models/', { params: { user_id: userId } }),

  // 获取单个模型配置
  get: (modelId) => request.get(`/models/${modelId}`),

  // 更新模型配置
  update: (modelId, data) => request.put(`/models/${modelId}`, data),

  // 删除模型配置
  delete: (modelId) => request.delete(`/models/${modelId}`)
}

// ==================== 题目资源 API ====================
export const resourceApi = {
  // 创建资源
  create: (data) => request.post('/resources/', data),

  // 获取题目的所有资源
  getByQuestion: (questionId) => request.get(`/resources/question/${questionId}`),

  // 删除资源
  delete: (resourceId) => request.delete(`/resources/${resourceId}`)
}

// ==================== 共享管理 API ====================
export const shareApi = {
  // 设置共享
  setShare: (data) => request.post('/shares/', data),

  // 取消共享
  cancelShare: (subjectId, params) =>
    request.delete(`/shares/${subjectId}`, { params }),

  // 获取共享状态
  getStatus: (subjectId) => request.get(`/shares/status/${subjectId}`),

  // 获取我共享的科目
  getMyShared: (userId) =>
    request.get('/shares/my-shared', { params: { user_id: userId } }),

  // 搜索用户
  searchUsers: (keyword, userId) =>
    request.get('/shares/users/search', { params: { keyword, current_user_id: userId } })
}

export default request
