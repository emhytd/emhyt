<template>
  <div class="user-info-container" :class="containerClasses">
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <span>正在加载用户信息...</span>
    </div>
    
    <div v-else class="content-wrapper">
      <div v-if="error" class="error-state">
        <div class="error-icon">⚠️</div>
        <div class="error-text">错误: {{ error }}</div>
        <button @click="fetchUserName" class="retry-btn">重试</button>
      </div>
      
      <div v-if="userName" class="user-info-display">
        <div class="user-info-main">
          <div class="user-greeting">
            <span class="greeting-text">你好，</span>
            <span class="user-name">{{ userName }}</span>
            <span class="user-role">{{ roleDisplay }}</span>
          </div>
          <div class="user-id">ID: {{ userId }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import axios from 'axios'

// 响应式数据
const userName = ref('')
const userId = ref('')
const role = ref('')
const loading = ref(true)
const error = ref('')
const containerWidth = ref('100%')

// 计算属性 - 角色显示文本
const roleDisplay = computed(() => {
  return role.value === 'teacher' ? '老师' : 
         role.value === 'student' ? '同学' : '未知角色';
})

// 计算属性 - 容器类名
const containerClasses = computed(() => {
  return {
    'loading': loading.value,
    'error': error.value && !loading.value,
    'success': userName.value && !loading.value && !error.value
  }
})

import apiConfig from '@/config/apiConfig';

// 获取用户信息
const fetchUserName = async () => {
  loading.value = true
  error.value = ''
  
  try {
    const token = localStorage.getItem('jwt_token')
    if (!token) {
      throw new Error('未找到登录信息，请重新登录')
    }
    
    const response = await axios.get(
      apiConfig.AUTH_API.GET_USER_NAME,
      {
        headers: { 
          'Authorization': `Bearer ${token}` 
        }
      }
    )
    
    if (response.data.status === 'success') {
      userName.value = response.data.name
      // 从token中解析用户ID和角色
      const tokenPayload = parseJwt(token)
      userId.value = tokenPayload.user_id
      role.value = tokenPayload.role
    } else {
      throw new Error(response.data.error || '获取用户信息失败')
    }
  } catch (err) {
    console.error('获取用户名错误:', err)
    if (err.response) {
      error.value = err.response.data.error || '服务器返回错误'
    } else if (err.message) {
      error.value = err.message
    } else {
      error.value = '发生未知错误'
    }
  } finally {
    loading.value = false
  }
}

// 解析JWT Token的函数
const parseJwt = (token) => {
  try {
    const base64Url = token.split('.')[1]
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
    const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
      return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2)
    }).join(''))
    
    return JSON.parse(jsonPayload)
  } catch (e) {
    console.error('解析Token失败:', e)
    return {}
  }
}

// 监听父容器宽度变化
const updateContainerWidth = () => {
  // 获取父容器宽度
  const parent = document.querySelector('.user-info-container')?.parentElement
  if (parent) {
    containerWidth.value = `${parent.offsetWidth}px`
  }
}

// 组件挂载时获取用户信息
onMounted(() => {
  fetchUserName()
  
  // 监听窗口大小变化
  window.addEventListener('resize', updateContainerWidth)
  
  // 初始更新
  setTimeout(updateContainerWidth, 100)
})

// 组件卸载时移除监听器
import { onUnmounted } from 'vue'
onUnmounted(() => {
  window.removeEventListener('resize', updateContainerWidth)
})
</script>

<style scoped>
/* 基础容器样式 - 确保完全自适应 */
.user-info-container {
  width: 100%;
  min-width: 200px;
  max-width: 100%;
  display: block;
  box-sizing: border-box;
  position: relative;
  transition: all 0.3s ease;
  overflow: hidden;
}

/* 内容包装器 - 确保内容自适应 */
.content-wrapper {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

/* 加载状态样式 */
.loading-state {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  width: 100%;
  box-sizing: border-box;
}

.loading-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-top: 2px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  flex-shrink: 0;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-state span {
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 错误状态样式 */
.error-state {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: rgba(244, 67, 54, 0.1);
  border: 1px solid rgba(244, 67, 54, 0.2);
  border-radius: 8px;
  width: 100%;
  box-sizing: border-box;
  flex-wrap: wrap;
}

.error-icon {
  font-size: 18px;
  flex-shrink: 0;
}

.error-text {
  flex: 1;
  color: rgba(255, 255, 255, 0.9);
  font-size: 14px;
  min-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.retry-btn {
  padding: 6px 12px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  color: rgba(255, 255, 255, 0.9);
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 12px;
  white-space: nowrap;
  flex-shrink: 0;
}

.retry-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-1px);
}

/* 用户信息显示样式 */
.user-info-display {
  width: 100%;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  box-sizing: border-box;
}

.user-info-main {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  gap: 16px;
  flex-wrap: wrap;
}

.user-greeting {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  flex: 1;
  min-width: 200px;
}

.greeting-text {
  color: rgba(255, 255, 255, 0.8);
  font-size: 24px;
  white-space: nowrap;
}

.user-name {
  color: rgba(255, 255, 255, 0.95);
  font-weight: 600;
  font-size: 24px;
  white-space: nowrap;
}

.user-role {
  background: rgba(100, 150, 255, 0.2);
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 24px;
  color: rgba(255, 255, 255, 0.9);
  white-space: nowrap;
}

.user-id {
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
  white-space: nowrap;
  flex-shrink: 0;
}

/* 响应式设计 - 确保在不同宽度下都能良好显示 */
@media (max-width: 768px) {
  .user-info-main {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .user-greeting {
    min-width: 100%;
    justify-content: flex-start;
  }
  
  .user-id {
    align-self: flex-end;
  }
}

@media (max-width: 480px) {
  .user-info-container {
    min-width: 100%;
  }
  
  .loading-state,
  .error-state,
  .user-info-display {
    padding: 10px 12px;
  }
  
  .error-state {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .error-text {
    min-width: 100%;
  }
  
  .retry-btn {
    align-self: flex-end;
  }
  
  .user-greeting {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }
  
  .user-id {
    align-self: flex-start;
    font-size: 13px;
  }
}

/* 极端窄屏适配 */
@media (max-width: 320px) {
  .user-info-container {
    min-width: 100%;
  }
  
  .loading-state span {
    font-size: 12px;
  }
  
  .user-name {
    font-size: 14px;
  }
  
  .greeting-text,
  .user-id {
    font-size: 12px;
  }
}

/* 确保父容器宽度变化时组件能立即响应 */
.user-info-container {
  /* 强制重绘以确保宽度更新 */
  transform: translateZ(0);
}

/* 添加调试边框（可选，用于测试宽度变化） */
.user-info-container.debug {
  border: 1px dashed rgba(255, 0, 0, 0.3);
}
</style>