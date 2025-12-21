<template>
  <span class="formula-renderer" v-html="renderedContent"></span>
</template>

<script setup>
import { computed } from 'vue'
import katex from 'katex'
import 'katex/dist/katex.min.css'

const props = defineProps({
  content: {
    type: String,
    required: true,
    default: ''
  }
})

/**
 * 渲染包含 LaTeX 公式的文本
 * 支持行内公式 $...$ 和块级公式 $$...$$
 */
const renderedContent = computed(() => {
  if (!props.content) return ''
  
  let text = props.content
  
  try {
    // 先处理块级公式 $$...$$
    text = text.replace(/\$\$([\s\S]+?)\$\$/g, (match, formula) => {
      try {
        const html = katex.renderToString(formula.trim(), {
          displayMode: true,
          throwOnError: false,
          strict: false
        })
        return `<div class="formula-block">${html}</div>`
      } catch (e) {
        console.warn('块级公式渲染失败:', formula, e)
        return match // 渲染失败时返回原文本
      }
    })
    
    // 再处理行内公式 $...$
    text = text.replace(/\$([^\$]+?)\$/g, (match, formula) => {
      try {
        const html = katex.renderToString(formula.trim(), {
          displayMode: false,
          throwOnError: false,
          strict: false
        })
        return `<span class="formula-inline">${html}</span>`
      } catch (e) {
        console.warn('行内公式渲染失败:', formula, e)
        return match // 渲染失败时返回原文本
      }
    })
    
    // 将普通换行符转换为 <br>
    text = text.replace(/\n/g, '<br>')
    
    return text
  } catch (error) {
    console.error('公式渲染出错:', error)
    return props.content
  }
})
</script>

<style scoped>
.formula-renderer {
  display: inline-block;
  word-wrap: break-word;
  overflow-wrap: break-word;
  vertical-align: middle;
}

.formula-renderer :deep(.formula-block) {
  margin: 1em 0;
  text-align: center;
  overflow-x: auto;
  display: block;
}

.formula-renderer :deep(.formula-inline) {
  display: inline;
  margin: 0 0.2em;
  vertical-align: middle;
}

/* KaTeX 公式样式优化 */
.formula-renderer :deep(.katex) {
  font-size: 1.1em;
}

.formula-renderer :deep(.katex-display) {
  margin: 1em 0;
  display: block;
}
</style>
