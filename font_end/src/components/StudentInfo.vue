<template>
  <div class="student-info-container">
    <!-- 错误信息提示 -->
    <div v-if="errorMessage" class="error-message">
      <div class="error-content">
        <span class="error-icon">⚠️</span>
        <span class="error-text">{{ errorMessage }}</span>
        <button @click="clearError" class="error-close">×</button>
      </div>
    </div>
    
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>正在加载学生信息...</p>
    </div>
    
    <!-- 学生信息展示 -->
    <div v-if="studentInfo && !errorMessage && !loading" class="info-section">
      <h2 class="section-title">学生个人信息</h2>
      
      <div class="info-grid">
        <!-- 基本信息 -->
        <div class="info-card">
          <h3 class="card-title">基本信息</h3>
          <div class="info-row">
            <span class="info-label">姓名:</span>
            <span class="info-value">{{ studentInfo.student_name }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">学号:</span>
            <span class="info-value">{{ studentInfo.student_id }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">班级:</span>
            <span class="info-value">{{ studentInfo.class_name }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">性别:</span>
            <span class="info-value">{{ studentInfo.student_gender }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">出生日期:</span>
            <span class="info-value">{{ formatDate(studentInfo.birth_date) }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">民族:</span>
            <span class="info-value">{{ studentInfo.ethnicity }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">政治面貌:</span>
            <span class="info-value">{{ studentInfo.political_status }}</span>
          </div>
        </div>
        
        <!-- 联系信息 -->
        <div class="info-card">
          <h3 class="card-title">联系信息</h3>
          <div class="info-row">
            <span class="info-label">手机号:</span>
            <span class="info-value">{{ studentInfo.phone_number }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">邮箱:</span>
            <span class="info-value">{{ studentInfo.email }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">当前住址:</span>
            <span class="info-value">{{ studentInfo.current_residence }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">家庭住址:</span>
            <span class="info-value">{{ studentInfo.home_address }}</span>
          </div>
        </div>
        
        <!-- 其他信息 -->
        <div class="info-card">
          <h3 class="card-title">其他信息</h3>
          <div class="info-row">
            <span class="info-label">身份证号:</span>
            <span class="info-value">{{ studentInfo.id_number }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">籍贯:</span>
            <span class="info-value">{{ studentInfo.native_place }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">出生地:</span>
            <span class="info-value">{{ studentInfo.birthplace }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">血型:</span>
            <span class="info-value">{{ studentInfo.blood_type }}型</span>
          </div>
          <div class="info-row">
            <span class="info-label">身高:</span>
            <span class="info-value">{{ studentInfo.height }} cm</span>
          </div>
          <div class="info-row">
            <span class="info-label">体重:</span>
            <span class="info-value">{{ studentInfo.weight }} kg</span>
          </div>
          <div class="info-row">
            <span class="info-label">特长:</span>
            <span class="info-value">{{ studentInfo.specialty }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

// 响应式数据
const studentInfo = ref(null)
const loading = ref(false)
const errorMessage = ref('')

// 组件挂载时获取数据
onMounted(async () => {
  await fetchStudentInfo()
})
import apiConfig from '@/config/apiConfig';
// 获取学生信息
const fetchStudentInfo = async () => {
  loading.value = true
  errorMessage.value = ''
  
  try {
    const token = localStorage.getItem('jwt_token') 
    const response = await axios.get(apiConfig.STUDENT_API.GET_INFO, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    
    console.log(response)
    
    if (response.data.status === 'success') {
      studentInfo.value = response.data.data
    } else {
      errorMessage.value = '获取学生信息失败，请稍后重试'
    }
  } catch (error) {
    console.error('获取学生信息失败:', error)
    errorMessage.value = '获取学生信息失败，请检查网络连接或稍后重试'
  } finally {
    loading.value = false
  }
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN')
}

// 清除错误信息
const clearError = () => {
  errorMessage.value = ''
}
</script>

<style scoped>
.student-info-container {
  width: 100%;
  margin-top: 0;
  position: relative;
  z-index: 1;
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

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.info-card {
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(20px);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  padding: 20px;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.info-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
}

.card-title {
  color: rgba(255, 255, 255, 0.95);
  margin-bottom: 15px;
  font-size: 18px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  padding-bottom: 8px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
  padding: 8px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.info-row:last-child {
  border-bottom: none;
  margin-bottom: 0;
}

.info-label {
  color: rgba(255, 255, 255, 0.7);
  font-weight: 500;
  flex: 1;
}

.info-value {
  color: rgba(255, 255, 255, 0.9);
  flex: 2;
  text-align: right;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .info-grid {
    grid-template-columns: 1fr;
  }
  
  .info-row {
    flex-direction: column;
  }
  
  .info-value {
    text-align: left;
    margin-top: 5px;
  }
  
  .error-content {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .error-close {
    align-self: flex-end;
    margin-top: 10px;
    margin-left: 0;
  }
}

@media (max-width: 480px) {
  .info-card {
    padding: 15px;
  }
  
  .section-title {
    font-size: 20px;
  }
  
  .card-title {
    font-size: 16px;
  }
  
  .error-message {
    padding: 12px 15px;
  }
  
  .error-text {
    font-size: 13px;
  }
}
</style>