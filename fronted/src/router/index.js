import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue')
  },
  {
    path: '/subjects',
    name: 'Subjects',
    component: () => import('@/views/Subjects.vue')
  },
  {
    path: '/import',
    name: 'ImportQuestion',
    component: () => import('@/views/ImportQuestion.vue')
  },
  {
    path: '/practice',
    name: 'Practice',
    component: () => import('@/views/Practice.vue')
  },
  {
    path: '/errors',
    name: 'ErrorBook',
    component: () => import('@/views/ErrorBook.vue')
  },
  {
    path: '/error-practice',
    name: 'ErrorPractice',
    component: () => import('@/views/ErrorPractice.vue')
  },
  {
    path: '/model-config',
    name: 'ModelConfig',
    component: () => import('@/views/ModelConfig.vue')
  },
  {
    path: '/question-bank',
    name: 'QuestionBank',
    component: () => import('@/views/QuestionBank.vue')
  },
  {
    path: '/practice-history',
    name: 'PracticeHistory',
    component: () => import('@/views/PracticeHistory.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
