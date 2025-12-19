/**
 * 用户状态管理 Store
 * 使用 Pinia 管理全局用户状态
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useUserStore = defineStore('user', () => {
  // 状态
  const currentUser = ref(null)
  const isLoggedIn = ref(false)

  // 计算属性
  const userId = computed(() => currentUser.value?.id || null)
  const username = computed(() => currentUser.value?.username || '')

  // 初始化用户信息（从 localStorage 恢复）
  const initUser = () => {
    const token = localStorage.getItem('token')
    const userStr = localStorage.getItem('user')
    
    if (token && userStr) {
      try {
        currentUser.value = JSON.parse(userStr)
        isLoggedIn.value = true
        return true
      } catch (error) {
        console.error('解析用户信息失败:', error)
        clearUser()
        return false
      }
    }
    return false
  }

  // 设置用户信息
  const setUser = (user, token) => {
    currentUser.value = user
    isLoggedIn.value = true
    localStorage.setItem('token', token)
    localStorage.setItem('user', JSON.stringify(user))
  }

  // 清除用户信息
  const clearUser = () => {
    currentUser.value = null
    isLoggedIn.value = false
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  // 登出
  const logout = () => {
    clearUser()
  }

  return {
    // 状态
    currentUser,
    isLoggedIn,
    // 计算属性
    userId,
    username,
    // 方法
    initUser,
    setUser,
    clearUser,
    logout
  }
})
