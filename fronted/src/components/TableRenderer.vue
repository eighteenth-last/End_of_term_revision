<template>
  <div class="table-renderer">
    <!-- 如果内容包含ASCII表格，则渲染为HTML表格，并保留表格前的普通文本 -->
    <template v-if="isTable">
      <div class="text-content" v-if="tablePrefixText">
        <FormulaRenderer :content="tablePrefixText" />
      </div>
      <div class="table-container">
        <table class="probability-table">
          <thead v-if="parsedTable.headers.length > 0">
            <tr>
              <th v-for="(header, index) in parsedTable.headers" :key="index">
                <FormulaRenderer :content="header" />
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, rowIndex) in parsedTable.rows" :key="rowIndex">
              <td 
                v-for="(cell, cellIndex) in row" 
                :key="cellIndex"
                :class="{ 'header-cell': cellIndex === 0 }"
              >
                <FormulaRenderer :content="cell" />
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>
    <!-- 否则使用普通文本渲染 -->
    <div v-else class="text-content">
      <FormulaRenderer :content="content" />
    </div>
  </div>
</template>

<script setup>
// 获取表格前的普通文本（如题干描述），不包含表头行
const tablePrefixText = computed(() => {
  if (!props.content || !isTable.value) return ''
  const lines = props.content.split('\n')
  // 找到第一个表格分隔符行的位置
  const tableSepIdx = lines.findIndex(line => line.includes('|') && line.includes('---'))
  if (tableSepIdx <= 0) return ''
  // 如果上一行是表头，则只取表头前的内容
  let endIdx = tableSepIdx
  if (lines[tableSepIdx - 1] && lines[tableSepIdx - 1].includes('|')) {
    endIdx = tableSepIdx - 1
  }
  return lines.slice(0, endIdx).join('\n').trim()
})
import { computed } from 'vue'
import FormulaRenderer from './FormulaRenderer.vue'

const props = defineProps({
  content: {
    type: String,
    required: true,
    default: ''
  }
})

/**
 * 判断内容是否包含表格
 */
const isTable = computed(() => {
  if (!props.content) return false
  // 检查是否包含表格分隔符
  return props.content.includes('|') && props.content.includes('---')
})

/**
 * 解析ASCII表格为结构化数据
 */
const parsedTable = computed(() => {
  if (!props.content) return { headers: [], rows: [] }
  
  const lines = props.content.split('\n').map(line => line.trim()).filter(line => line)
  const result = { headers: [], rows: [] }
  
  try {
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i]
      
      // 跳过分隔线
      if (line.includes('---')) continue
      
      // 解析包含 | 的行
      if (line.includes('|')) {
        const cells = line.split('|')
          .map(cell => cell.trim())
          .filter(cell => cell)
        
        // 第一行作为表头
        if (result.headers.length === 0 && result.rows.length === 0) {
          result.headers = cells
        } else {
          result.rows.push(cells)
        }
      }
    }
    
    return result
  } catch (error) {
    console.warn('表格解析失败:', error)
    return { headers: [], rows: [] }
  }
})
</script>

<style scoped>
.table-container {
  margin: 12px 0;
  overflow-x: auto;
}

.probability-table {
  width: 100%;
  border-collapse: collapse;
  border: 1px solid #e0e0e6;
  background: #fff;
}

.probability-table th,
.probability-table td {
  padding: 12px;
  text-align: center;
  border: 1px solid #e0e0e6;
  min-width: 80px;
}

.probability-table thead th {
  background: #f5f5f7;
  font-weight: 600;
  color: #333;
}

.probability-table tbody td.header-cell {
  background: #f5f5f7;
  font-weight: 500;
}

.probability-table tbody tr:hover {
  background: #fafafa;
}

.text-content {
  white-space: pre-wrap;
  word-wrap: break-word;
}
</style>
