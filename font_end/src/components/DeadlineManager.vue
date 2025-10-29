<template>
  <div class="deadline-manager-container">
    <!-- 错误信息提示 -->
    <div v-if="errorMessage" class="error-message">
      <div class="error-content">
        <span class="error-icon">⚠️</span>
        <span class="error-text">{{ errorMessage }}</span>
        <button @click="clearError" class="error-close">×</button>
      </div>
    </div>
    
    <!-- 成功信息提示 -->
    <div v-if="successMessage" class="success-message">
      <div class="success-content">
        <span class="success-icon">✅</span>
        <span class="success-text">{{ successMessage }}</span>
        <button @click="clearSuccess" class="success-close">×</button>
      </div>
    </div>
    
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>正在加载数据...</p>
    </div>
    
    <!-- 截止日期信息展示 -->
    <div v-if="currentDeadline && !loading" class="deadline-info-section">
      <h2 class="section-title">截止日期管理</h2>
      
      <div class="deadline-card">
        <div class="deadline-display">
          <h3 class="card-title">当前截止日期</h3>
          <div class="deadline-datetime">
            <div class="deadline-date">{{ formatDate(currentDeadline) }}</div>
            <div class="deadline-time">{{ formatTime(currentDeadline) }}</div>
          </div>
          
          <div class="deadline-status" :class="getStatusClass()">
            <span class="status-icon">{{ getStatusIcon() }}</span>
            <span class="status-text">{{ getStatusText() }}</span>
          </div>
          
          <div class="days-info">
            <span v-if="isExpired" class="days-expired">已过期 {{ Math.abs(daysDifference) }} 天</span>
            <span v-else class="days-remaining">还剩 {{ daysDifference }} 天</span>
          </div>
        </div>
        
        <div class="deadline-controls">
          <h3 class="card-title">修改截止日期</h3>
          
          <form @submit.prevent="updateDeadline" class="deadline-form">
            <div class="form-group">
              <label for="deadline-date-input" class="form-label">日期:</label>
              <input 
                type="date" 
                id="deadline-date-input"
                v-model="datePart" 
                class="date-input"
                required
              >
            </div>
            
            <div class="form-group">
              <label for="deadline-time-input" class="form-label">时间:</label>
              <input 
                type="time" 
                id="deadline-time-input"
                v-model="timePart" 
                class="time-input"
                step="1"
                required
              >
            </div>
            
            <div class="form-actions">
              <button 
                type="submit" 
                class="submit-btn"
                :disabled="isSubmitting || !newDeadline"
              >
                <span v-if="isSubmitting" class="btn-loading"></span>
                {{ isSubmitting ? '提交中...' : '更新截止日期' }}
              </button>
              
              <button 
                type="button" 
                class="reset-btn"
                @click="resetToToday"
                :disabled="isSubmitting"
              >
                重置为今天
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- 如果没有数据时的提示 -->
    <div v-if="!currentDeadline && !loading && !errorMessage" class="no-data-message">
      <div class="no-data-content">
        <span class="no-data-icon">📅</span>
        <h3>暂无截止日期数据</h3>
        <p>请设置一个新的截止日期</p>
        <div class="set-first-deadline">
          <h4>设置首个截止日期</h4>
          <form @submit.prevent="updateDeadline" class="deadline-form">
            <div class="form-group">
              <label for="first-date-input" class="form-label">日期:</label>
              <input 
                type="date" 
                id="first-date-input"
                v-model="datePart" 
                class="date-input"
                required
              >
            </div>
            <div class="form-group">
              <label for="first-time-input" class="form-label">时间:</label>
              <input 
                type="time" 
                id="first-time-input"
                v-model="timePart" 
                class="time-input"
                step="1"
                required
              >
            </div>
            <div class="form-actions">
              <button 
                type="submit" 
                class="submit-btn"
                :disabled="isSubmitting || !newDeadline"
              >
                <span v-if="isSubmitting" class="btn-loading"></span>
                {{ isSubmitting ? '提交中...' : '设置截止日期' }}
              </button>
              <button 
                type="button" 
                class="reset-btn"
                @click="resetToToday"
                :disabled="isSubmitting"
              >
                重置为今天
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import axios from 'axios'

// 响应式数据
const currentDeadline = ref(null)
const datePart = ref('')
const timePart = ref('23:59:59')
const loading = ref(false)
const isSubmitting = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

// 计算属性
const newDeadline = computed(() => {
  if (!datePart.value || !timePart.value) return ''
  
  // 确保时间部分包含秒数
  const timeWithSeconds = timePart.value.includes(':') 
    ? timePart.value.padEnd(8, ':00').substring(0, 8)
    : '23:59:59'
  
  return `${datePart.value} ${timeWithSeconds}`
})

const daysDifference = computed(() => {
  if (!currentDeadline.value) return 0
  
  const today = new Date()
  const deadline = new Date(currentDeadline.value)
  const diffTime = deadline.getTime() - today.getTime()
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  
  return diffDays
})

const isExpired = computed(() => {
  return daysDifference.value < 0
})

// 组件挂载时获取截止日期
onMounted(async () => {
  await fetchDeadline()
})
import apiConfig from '@/config/apiConfig';
// 获取截止日期
const fetchDeadline = async () => {
  loading.value = true
  errorMessage.value = ''
  
  try {
    const token = localStorage.getItem('jwt_token')
    const response = await axios.get(apiConfig.TEACHER_API.CHECK_DEADLINE, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    
    if (response.data.status === 'success') {
      currentDeadline.value = response.data.data.deadline_date
      
      // 分离日期和时间部分
      if (currentDeadline.value) {
        const dateObj = new Date(currentDeadline.value)
        datePart.value = dateObj.toISOString().split('T')[0]
        
        const hours = String(dateObj.getHours()).padStart(2, '0')
        const minutes = String(dateObj.getMinutes()).padStart(2, '0')
        const seconds = String(dateObj.getSeconds()).padStart(2, '0')
        timePart.value = `${hours}:${minutes}:${seconds}`
      }
    } else {
      errorMessage.value = '获取截止日期失败，请稍后重试'
    }
  } catch (error) {
    console.error('获取截止日期失败:', error)
    errorMessage.value = '获取截止日期失败，请检查网络连接或稍后重试'
  } finally {
    loading.value = false
  }
}

// 更新截止日期
const updateDeadline = async () => {
  if (!newDeadline.value) return
  
  isSubmitting.value = true
  errorMessage.value = ''
  successMessage.value = ''
  
  try {
    const token = localStorage.getItem('jwt_token')
    const response = await axios.post(apiConfig.TEACHER_API.SET_DEADLINE, 
      { deadline: newDeadline.value },
      { headers: { 'Authorization': `Bearer ${token}` } }
    )
    
    if (response.data.status === 'success') {
      currentDeadline.value = response.data.data.deadline_date
      successMessage.value = '截止日期更新成功！'
      
      setTimeout(() => {
        successMessage.value = ''
      }, 3000)
    } else {
      errorMessage.value = '更新截止日期失败，请稍后重试'
    }
  } catch (error) {
    console.error('更新截止日期失败:', error)
    errorMessage.value = '更新截止日期失败，请检查网络连接或稍后重试'
  } finally {
    isSubmitting.value = false
  }
}

// 重置为今天
const resetToToday = () => {
  const today = new Date()
  const todayString = today.toISOString().split('T')[0]
  datePart.value = todayString
  timePart.value = '23:59:59'
  errorMessage.value = ''
  successMessage.value = ''
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    weekday: 'long'
  })
}

// 格式化时间
const formatTime = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false
  })
}

// 获取状态样式类
const getStatusClass = () => {
  if (isExpired.value) return 'status-expired'
  if (daysDifference.value <= 7) return 'status-warning'
  return 'status-normal'
}

// 获取状态图标
const getStatusIcon = () => {
  if (isExpired.value) return '⏰'
  if (daysDifference.value <= 7) return '⚠️'
  return '📅'
}

// 获取状态文本
const getStatusText = () => {
  if (isExpired.value) return '已过期'
  if (daysDifference.value <= 7) return '即将到期'
  return '进行中'
}

// 清除错误信息
const clearError = () => {
  errorMessage.value = ''
}

// 清除成功信息
const clearSuccess = () => {
  successMessage.value = ''
}
</script>

<style scoped>
.deadline-manager-container {
  width: 100%;
  min-height: 500px;
  position: relative;
  z-index: 10;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 20px;
}

/* 错误信息样式 */
.error-message {
  background: rgba(244, 67, 54, 0.15);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(244, 67, 54, 0.3);
  border-radius: 12px;
  padding: 15px 20px;
  margin-bottom: 20px;
  animation: slideDown 0.3s ease-out;
}

.error-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.error-icon {
  font-size: 18px;
  margin-right: 10px;
  flex-shrink: 0;
}

.error-text {
  flex: 1;
  color: rgba(255, 255, 255, 0.95);
  font-weight: 500;
  font-size: 14px;
}

.error-close {
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.7);
  font-size: 20px;
  cursor: pointer;
  padding: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: all 0.3s ease;
  flex-shrink: 0;
  margin-left: 10px;
}

.error-close:hover {
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.9);
}

/* 成功信息样式 */
.success-message {
  background: rgba(76, 175, 80, 0.15);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(76, 175, 80, 0.3);
  border-radius: 12px;
  padding: 15px 20px;
  margin-bottom: 20px;
  animation: slideDown 0.3s ease-out;
}

.success-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.success-icon {
  font-size: 18px;
  margin-right: 10px;
  flex-shrink: 0;
}

.success-text {
  flex: 1;
  color: rgba(255, 255, 255, 0.95);
  font-weight: 500;
  font-size: 14px;
}

.success-close {
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.7);
  font-size: 20px;
  cursor: pointer;
  padding: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: all 0.3s ease;
  flex-shrink: 0;
  margin-left: 10px;
}

.success-close:hover {
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.9);
}

/* 加载状态样式 */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(20px);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.15);
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(255, 255, 255, 0.1);
  border-left: 4px solid rgba(255, 255, 255, 0.8);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 15px;
}

.loading-container p {
  color: rgba(255, 255, 255, 0.8);
  font-size: 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 信息展示样式 */
.section-title {
  color: rgba(255, 255, 255, 0.95);
  margin-bottom: 20px;
  font-size: 24px;
  text-align: center;
}

.deadline-card {
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(20px);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  padding: 30px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30px;
}

.deadline-display {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 20px;
}

.card-title {
  color: rgba(255, 255, 255, 0.95);
  margin-bottom: 20px;
  font-size: 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  padding-bottom: 10px;
  width: 100%;
  text-align: center;
}

.deadline-datetime {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  margin: 15px 0;
}

.deadline-date {
  font-size: 24px;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.95);
}

.deadline-time {
  font-size: 20px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.85);
  background: rgba(255, 255, 255, 0.1);
  padding: 6px 12px;
  border-radius: 6px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.deadline-status {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 16px;
  border-radius: 20px;
  margin: 10px 0;
  font-weight: 600;
}

.status-expired {
  background: rgba(244, 67, 54, 0.2);
  color: #F44336;
  border: 1px solid rgba(244, 67, 54, 0.4);
}

.status-warning {
  background: rgba(255, 193, 7, 0.2);
  color: #FFC107;
  border: 1px solid rgba(255, 193, 7, 0.4);
}

.status-normal {
  background: rgba(76, 175, 80, 0.2);
  color: #4CAF50;
  border: 1px solid rgba(76, 175, 80, 0.4);
}

.status-icon {
  font-size: 18px;
}

.days-info {
  margin-top: 10px;
  font-size: 18px;
  font-weight: 600;
}

.days-expired {
  color: #F44336;
}

.days-remaining {
  color: #4CAF50;
}

/* 表单样式 */
.deadline-controls {
  padding: 20px;
}

.deadline-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  color: rgba(255, 255, 255, 0.9);
  font-weight: 500;
  font-size: 16px;
}

.date-input, .time-input {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  padding: 12px 15px;
  color: rgba(255, 255, 255, 0.9);
  font-size: 16px;
  transition: all 0.3s ease;
}

.date-input:focus, .time-input:focus {
  outline: none;
  border-color: rgba(100, 150, 255, 0.6);
  background: rgba(255, 255, 255, 0.15);
  box-shadow: 0 0 0 2px rgba(100, 150, 255, 0.2);
}

.form-actions {
  display: flex;
  gap: 15px;
  margin-top: 10px;
}

.submit-btn, .reset-btn {
  flex: 1;
  padding: 12px 20px;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.submit-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.reset-btn {
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.reset-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.15);
  transform: translateY(-2px);
}

.btn-loading {
  width: 16px;
  height: 16px;
  border: 2px solid transparent;
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

/* 无数据时的提示样式 */
.no-data-message {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(20px);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  text-align: center;
}

.no-data-content {
  max-width: 500px;
}

.no-data-icon {
  font-size: 64px;
  margin-bottom: 20px;
  display: block;
}

.no-data-message h3 {
  color: rgba(255, 255, 255, 0.95);
  margin-bottom: 10px;
  font-size: 24px;
}

.no-data-message p {
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 30px;
  font-size: 16px;
}

.set-first-deadline {
  margin-top: 30px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.set-first-deadline h4 {
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 15px;
  font-size: 18px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .deadline-card {
    grid-template-columns: 1fr;
    gap: 20px;
    padding: 20px;
  }
  
  .form-actions {
    flex-direction: column;
  }
  
  .deadline-date {
    font-size: 22px;
  }
  
  .deadline-time {
    font-size: 18px;
  }
  
  .error-content, .success-content {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .error-close, .success-close {
    align-self: flex-end;
    margin-top: 10px;
    margin-left: 0;
  }
}

@media (max-width: 480px) {
  .deadline-manager-container {
    padding: 15px;
  }
  
  .deadline-card {
    padding: 15px;
  }
  
  .section-title {
    font-size: 20px;
  }
  
  .card-title {
    font-size: 18px;
  }
  
  .deadline-date {
    font-size: 18px;
  }
  
  .deadline-time {
    font-size: 16px;
  }
  
  .error-message, .success-message {
    padding: 12px 15px;
  }
  
  .error-text, .success-text {
    font-size: 13px;
  }
  
  .submit-btn, .reset-btn {
    padding: 10px 15px;
    font-size: 14px;
  }
  
  .no-data-icon {
    font-size: 48px;
  }
  
  .no-data-message h3 {
    font-size: 20px;
  }
}
</style>