<template>
  <div class="question-images">
    <!-- 图片列表 -->
    <div v-if="images.length > 0" class="images-container">
      <div 
        v-for="(img, index) in images" 
        :key="index"
        class="image-item"
        @click="handlePreview(index)"
      >
        <img :src="img" :alt="`题目配图${index + 1}`" />
        <div class="image-mask">
          <n-icon size="24" color="#fff">
            <expand-outline />
          </n-icon>
        </div>
      </div>
    </div>

    <!-- 图片预览对话框 -->
    <n-modal
      v-model:show="showPreview"
      preset="card"
      style="width: 90%; max-width: 1200px;"
      :title="`题目配图 (${currentIndex + 1}/${images.length})`"
    >
      <div class="preview-container">
        <!-- 图片 -->
        <div class="preview-image">
          <img :src="images[currentIndex]" alt="预览图片" />
        </div>

        <!-- 导航按钮 -->
        <div v-if="images.length > 1" class="preview-nav">
          <n-button 
            circle 
            :disabled="currentIndex === 0"
            @click="prevImage"
          >
            <template #icon>
              <n-icon><chevron-back-outline /></n-icon>
            </template>
          </n-button>
          
          <n-text>{{ currentIndex + 1 }} / {{ images.length }}</n-text>
          
          <n-button 
            circle 
            :disabled="currentIndex === images.length - 1"
            @click="nextImage"
          >
            <template #icon>
              <n-icon><chevron-forward-outline /></n-icon>
            </template>
          </n-button>
        </div>
      </div>
    </n-modal>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ExpandOutline, ChevronBackOutline, ChevronForwardOutline } from '@vicons/ionicons5'

const props = defineProps({
  images: {
    type: Array,
    default: () => []
  }
})

const showPreview = ref(false)
const currentIndex = ref(0)

const handlePreview = (index) => {
  currentIndex.value = index
  showPreview.value = true
}

const prevImage = () => {
  if (currentIndex.value > 0) {
    currentIndex.value--
  }
}

const nextImage = () => {
  if (currentIndex.value < props.images.length - 1) {
    currentIndex.value++
  }
}
</script>

<style scoped>
.images-container {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin: 12px 0;
}

.image-item {
  position: relative;
  width: 150px;
  height: 150px;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  border: 1px solid #e0e0e6;
  transition: all 0.3s;
}

.image-item:hover {
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.image-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-mask {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
  opacity: 0;
}

.image-item:hover .image-mask {
  background: rgba(0, 0, 0, 0.4);
  opacity: 1;
}

.preview-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.preview-image {
  width: 100%;
  max-height: 70vh;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: auto;
}

.preview-image img {
  max-width: 100%;
  max-height: 70vh;
  object-fit: contain;
}

.preview-nav {
  display: flex;
  align-items: center;
  gap: 20px;
}
</style>
