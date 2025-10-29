<!-- SemesterSelector.vue -->
<template>
  <div class="semester-selector-wrapper" :class="{ 'expanded-state': isExpanded }">
    <div class="button-container">
      <!-- 主要按钮组 -->
      <div class="main-buttons">
        <div class="buttons-scroll-container">
          <button
            v-for="semester in visibleSemesters"
            :key="semester.semester_id"
            @click="selectSemester(semester)"
            :class="[
              'semester-btn',
              { 'active': selectedSemesterId === semester.semester_id }
            ]"
          >
            <span class="btn-content">
              {{ semester.semester_name }}
              <span class="active-indicator" v-if="selectedSemesterId === semester.semester_id"></span>
            </span>
          </button>
        </div>
        
        <!-- 更多按钮 -->
        <button
          v-if="hasHiddenSemesters"
          @click="toggleExpand"
          class="more-btn"
          :class="{ 'expanded': isExpanded }"
        >
          <span class="btn-content">
            {{ isExpanded ? '收起' : '更多' }}
            <span class="arrow" :class="{ 'up': isExpanded }">▼</span>
          </span>
        </button>
      </div>

      <!-- 展开面板 -->
      <transition name="expand" @enter="onExpandEnter" @leave="onExpandLeave">
        <div 
          v-if="isExpanded && hasHiddenSemesters" 
          class="expand-panel"
          :style="{ height: expandPanelHeight }"
        >
          <div class="expand-panel-content" ref="expandPanelContent">
            <button
              v-for="semester in hiddenSemesters"
              :key="semester.semester_id"
              @click="selectSemester(semester)"
              :class="[
                'semester-btn',
                'expand-btn',
                { 'active': selectedSemesterId === semester.semester_id }
              ]"
            >
              <span class="btn-content">
                {{ semester.semester_name }}
                <span class="active-indicator" v-if="selectedSemesterId === semester.semester_id"></span>
              </span>
            </button>
          </div>
        </div>
      </transition>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, defineEmits, defineProps, watch, nextTick } from 'vue'
import axios from 'axios'

// 定义组件事件
const emit = defineEmits(['semester-change'])

// 定义组件属性
const props = defineProps({
  initialSemesterId: {
    type: String,
    default: '1'
  },
  visibleCount: {
    type: Number,
    default: 4 // 修改为默认显示4个按钮
  }
})

// 响应式数据
const semesterList = ref([])
const selectedSemesterId = ref(props.initialSemesterId)
const isExpanded = ref(false)
const expandPanelHeight = ref('auto')
const expandPanelContent = ref(null)

import apiConfig from '@/config/apiConfig';

// 计算可见的学期
const visibleSemesters = computed(() => {
  if (!semesterList.value.length) return []
  return semesterList.value.slice(0, props.visibleCount)
})

// 计算隐藏的学期
const hiddenSemesters = computed(() => {
  if (!semesterList.value.length) return []
  return semesterList.value.slice(props.visibleCount)
})

// 检查是否有隐藏的学期
const hasHiddenSemesters = computed(() => {
  return hiddenSemesters.value.length > 0
})

// 选择学期
function selectSemester(semester) {
  selectedSemesterId.value = semester.semester_id
  console.log('选中的学期ID:', selectedSemesterId.value)
  
  // 如果是从展开面板选择的，收起面板
  if (isExpanded.value) {
    isExpanded.value = false
  }
  
  // 触发父组件事件
  emit('semester-change', selectedSemesterId.value)
}

// 切换展开状态
function toggleExpand() {
  isExpanded.value = !isExpanded.value
}

// 展开动画开始时的回调
function onExpandEnter(el) {
  // 在下一个tick计算内容高度
  nextTick(() => {
    if (expandPanelContent.value) {
      const height = expandPanelContent.value.scrollHeight
      expandPanelHeight.value = '0px'
      
      // 使用requestAnimationFrame确保样式已应用
      requestAnimationFrame(() => {
        expandPanelHeight.value = `${height}px`
      })
    }
  })
}

// 展开动画结束时的回调
function onExpandLeave(el) {
  expandPanelHeight.value = '0px'
}

// 获取学期列表的函数
async function fetchSemesters() {
  try {
    const token = localStorage.getItem('jwt_token')
    
    if (!token) {
      console.error('未找到JWT token')
      return
    }
    
    const res = await axios.get(apiConfig.STUDENT_API.GET_SEMESTERS, {
      headers: { 'Authorization': `Bearer ${token}` },
    })
    
    if (res.data.status === 'success') {
      semesterList.value = res.data.data
      console.log('学期列表获取成功:', semesterList.value)
      
      // 确保默认值被选中
      if (semesterList.value.length > 0) {
        const defaultSemester = semesterList.value.find(s => s.semester_id === props.initialSemesterId) || semesterList.value[0]
        selectedSemesterId.value = defaultSemester.semester_id
        // 立即触发事件通知父组件
        emit('semester-change', selectedSemesterId.value)
      }
    } else {
      console.error('获取学期列表失败:', res.data)
    }
  } catch (error) {
    console.error('获取学期列表时发生错误:', error)
  }
}

// 组件挂载时获取学期列表
onMounted(() => {
  fetchSemesters()
})

// 监听初始值变化
watch(() => props.initialSemesterId, (newVal) => {
  selectedSemesterId.value = newVal
  emit('semester-change', newVal)
})

// 暴露方法给父组件
defineExpose({
  fetchSemesters,
  getSelectedSemester: () => selectedSemesterId.value
})
</script>

<style scoped>
.semester-selector-wrapper {
  width: 100%;
  background: transparent;
  transition: all 0.3s ease;
}

.semester-selector-wrapper.expanded-state {
  margin-bottom: 8px; /* 为展开面板留出空间 */
}

.button-container {
  position: relative;
  width: 100%;
}

.main-buttons {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  min-height: 50px;
}

.buttons-scroll-container {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  overflow-y: hidden;
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none; /* IE and Edge */
  flex: 1;
  padding: 4px 0;
  scroll-behavior: smooth;
}

/* 隐藏滚动条 */
.buttons-scroll-container::-webkit-scrollbar {
  display: none;
}

.semester-btn {
  padding: 10px 16px;
  border: 1px solid rgba(255, 255, 255, 0.25);
  border-radius: 8px;
  font-size: 14px;
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.9);
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(8px);
  font-weight: 500;
  white-space: nowrap;
  flex-shrink: 0;
  min-width: max-content;
  position: relative;
  overflow: hidden;
}

.semester-btn:hover {
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.4);
  transform: translateY(-1px);
}

.semester-btn.active {
  background: rgba(74, 144, 226, 0.25);
  border-color: rgba(100, 180, 255, 0.8);
  color: #fff;
  box-shadow: 
    0 4px 12px rgba(0, 0, 0, 0.3),
    0 0 0 1px rgba(100, 180, 255, 0.4),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
  transform: translateY(-1px);
}

/* 选中状态指示器 */
.active-indicator {
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 60%;
  height: 2px;
  background: linear-gradient(90deg, transparent, #64b4ff, transparent);
  border-radius: 1px;
  animation: pulse-glow 2s infinite;
}

@keyframes pulse-glow {
  0%, 100% {
    box-shadow: 0 0 2px #64b4ff, 0 0 4px #64b4ff;
  }
  50% {
    box-shadow: 0 0 4px #64b4ff, 0 0 8px #64b4ff;
  }
}

.btn-content {
  position: relative;
  display: block;
  z-index: 1;
}

.more-btn {
  padding: 10px 16px;
  border: 1px solid rgba(255, 255, 255, 0.25);
  border-radius: 8px;
  font-size: 14px;
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.9);
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(8px);
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 4px;
  white-space: nowrap;
  flex-shrink: 0;
  position: relative;
  overflow: hidden;
}

.more-btn:hover {
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.4);
}

.more-btn.expanded {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(100, 180, 255, 0.6);
}

.arrow {
  font-size: 10px;
  transition: transform 0.3s ease;
}

.arrow.up {
  transform: rotate(180deg);
}

.expand-panel {
  position: relative;
  background: rgba(30, 30, 40, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  margin-top: 8px;
  overflow: hidden;
  backdrop-filter: blur(12px);
  z-index: 1000;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  transition: height 0.3s ease;
}

.expand-panel-content {
  padding: 8px;
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.expand-btn {
  padding: 8px 12px;
  font-size: 13px;
  flex-shrink: 0;
}

/* 响应式设计 - 在宽度变窄时缩小按钮而不是堆叠 */
@media (max-width: 1200px) {
  .semester-btn,
  .more-btn {
    padding: 9px 15px;
    font-size: 13.5px;
  }
}

@media (max-width: 992px) {
  .semester-btn,
  .more-btn {
    padding: 8px 14px;
    font-size: 13px;
  }
}

@media (max-width: 768px) {
  .main-buttons {
    gap: 6px;
  }
  
  .semester-btn,
  .more-btn {
    padding: 7px 12px;
    font-size: 12.5px;
  }
  
  .expand-btn {
    padding: 6px 10px;
    font-size: 12px;
  }
  
  .expand-panel-content {
    padding: 6px;
    gap: 4px;
  }
}

@media (max-width: 576px) {
  .main-buttons {
    gap: 4px;
  }
  
  .semester-btn,
  .more-btn {
    padding: 6px 10px;
    font-size: 12px;
  }
  
  .expand-btn {
    padding: 5px 8px;
    font-size: 11px;
  }
}

/* 超小屏幕下的最小尺寸 */
@media (max-width: 480px) {
  .semester-btn,
  .more-btn {
    padding: 5px 8px;
    font-size: 11px;
    min-width: 70px;
  }
}

@media (max-width: 360px) {
  .semester-btn,
  .more-btn {
    padding: 4px 6px;
    font-size: 10px;
    min-width: 60px;
  }
}

/* 触摸设备优化 */
@media (hover: none) and (pointer: coarse) {
  .buttons-scroll-container {
    -webkit-overflow-scrolling: touch;
  }
  
  .semester-btn:hover {
    transform: none;
  }
  
  .semester-btn:active {
    background: rgba(255, 255, 255, 0.2);
    transform: scale(0.98);
  }
}

/* 展开动画 */
.expand-enter-active,
.expand-leave-active {
  transition: all 0.3s ease;
}

.expand-enter-from {
  opacity: 0;
  transform: translateY(-10px);
}

.expand-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

.expand-enter-to,
.expand-leave-from {
  opacity: 1;
  transform: translateY(0);
}
</style>