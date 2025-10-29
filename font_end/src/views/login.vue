<template>
  <div class="login-container">
    <!-- 粒子背景画布 -->
    <canvas ref="particleCanvas" class="particle-background"></canvas>
    
    <!-- 方形毛玻璃登录框 -->
    <div class="square-login-box">
      <div class="login-header">
        <h1>系统登录</h1>
        <p>请输入您的账号信息</p>
      </div>
      
      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group floating">
          <input
            id="username"
            v-model="username"
            type="text"
            required
            autocomplete="username"
            ref="usernameInput"
          />
          <label for="username">用户名</label>
          <div class="underline"></div>
        </div>
        
        <div class="form-group floating">
          <input
            id="password"
            v-model="password"
            type="password"
            required
            autocomplete="current-password"
            ref="passwordInput"
          />
          <label for="password">密码</label>
          <div class="underline"></div>
        </div>
        
        <div class="form-group">
          <label class="role-label">选择身份</label>
          <div class="role-options">
            <div 
              class="role-option" 
              :class="{ active: role === 'student' }"
              @click="selectRole('student')"
            >
              <span>学生</span>
              <div class="selection-indicator"></div>
            </div>
            <div 
              class="role-option" 
              :class="{ active: role === 'teacher' }"
              @click="selectRole('teacher')"
            >
              <span>教师</span>
              <div class="selection-indicator"></div>
            </div>
            <div 
              class="role-option" 
              :class="{ active: role === 'admin' }"
              @click="selectRole('admin')"
            >
              <span>管理员</span>
              <div class="selection-indicator"></div>
            </div>
          </div>
        </div>
        
        <button :disabled="loading" type="submit" class="login-button">
          <span class="button-text" v-if="!loading">登录</span>
          <span class="button-loading" v-else>
            <div class="loading-spinner"></div>
            登录中...
          </span>
        </button>
      </form>
      
      <div v-if="error" class="error-message">
        <span class="error-icon">!</span>
        {{ error }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, watch } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

const router = useRouter()
const username = ref('')
const password = ref('')
const role = ref('student')
const error = ref('')
const loading = ref(false)
const particleCanvas = ref(null)
const usernameInput = ref(null)
const passwordInput = ref(null)

// 修复浏览器自动填充检测
const checkAutoFill = () => {
  nextTick(() => {
    // 检查用户名输入框
    if (usernameInput.value) {
      // 使用多种方式检测值
      const hasValue = usernameInput.value.value || 
                      usernameInput.value.querySelector && 
                      usernameInput.value.querySelector('input')?.value ||
                      document.querySelector('input[autocomplete="username"]')?.value
      
      if (hasValue) {
        usernameInput.value.classList.add('has-value')
        username.value = hasValue
      }
    }
    
    // 检查密码输入框
    if (passwordInput.value) {
      const hasValue = passwordInput.value.value || 
                      passwordInput.value.querySelector && 
                      passwordInput.value.querySelector('input')?.value ||
                      document.querySelector('input[autocomplete="current-password"]')?.value
      
      if (hasValue) {
        passwordInput.value.classList.add('has-value')
        password.value = hasValue
      }
    }
  })
}

// 监听输入变化
watch([username, password], () => {
  nextTick(() => {
    if (username.value) {
      usernameInput.value?.classList.add('has-value')
    } else {
      usernameInput.value?.classList.remove('has-value')
    }
    
    if (password.value) {
      passwordInput.value?.classList.add('has-value')
    } else {
      passwordInput.value?.classList.remove('has-value')
    }
  })
})
import apiConfig from '@/config/apiConfig';
// 选择角色
const selectRole = (selectedRole) => {
  role.value = selectedRole
}

const handleLogin = async () => {
  error.value = ''
  loading.value = true

  try {
    const response = await axios.post(
      apiConfig.AUTH_API.LOGIN,
      { 
        name: username.value, 
        password: password.value,
        role: role.value
      },
      {
        headers: {
          'Content-Type': 'application/json'
        }
      }
    )

    if (response.data.status === 'success') {
      console.log('登录成功:', response.data)

      // 保存 token 到 localStorage
      localStorage.setItem('username', username.value)
      localStorage.setItem('jwt_token', response.data.token)

      // 路由跳转之前确保异步执行
       if (role.value === 'teacher') {
        await router.push('/teacher')
      } else if (role.value === 'admin') {
        await router.push('/admin')
      } else {
        await router.push('/student')
      }

    } else {
      // 显示错误信息
      error.value = response.data.error || '登录失败'
      document.querySelector('.square-login-box').style.animation = 'shake 0.5s ease'
    }
  } catch (err) {
    console.error('登录错误:', err)

    if (err.response) {
      // 后端返回的错误信息
      error.value = err.response.data.error || '登录失败'
    } 
    else if (err.code === 'ECONNREFUSED') {
      // 网络连接失败
      error.value = '无法连接到服务器，请稍后再试。'
    } 
    else if (err.code === 'ECONNABORTED') {
      // 请求超时
      error.value = '请求超时，请稍后再试。'
    } 
    else {
      // 其他未知错误
      error.value = '发生了未知错误，请稍后再试。'
    }

    // 添加摇动动画
    document.querySelector('.square-login-box').style.animation = 'shake 0.5s ease'
  } finally {
    loading.value = false
  }
}


// 粒子系统变量
let particles = []
let animationId = null
let canvas, ctx

// 粒子类
class Particle {
  constructor() {
    this.reset()
  }
  
  reset() {
    this.x = Math.random() * canvas.width
    this.y = Math.random() * canvas.height
    this.size = Math.random() * 2.5 + 1
    this.speedX = Math.random() * 1.2 - 0.6
    this.speedY = Math.random() * 1.2 - 0.6
    this.alpha = Math.random() * 0.7 + 0.3
    
    // 使用更漂亮的粒子颜色 - 柔和的蓝紫色调
    const colors = [
      'rgba(100, 150, 255, ALPHA)',  // 柔和的蓝色
      'rgba(150, 100, 255, ALPHA)',  // 柔和的紫色
      'rgba(80, 200, 255, ALPHA)',   // 天蓝色
      'rgba(200, 100, 255, ALPHA)'   // 紫红色
    ]
    const color = colors[Math.floor(Math.random() * colors.length)]
    this.color = color.replace('ALPHA', this.alpha)
  }
  
  update() {
    this.x += this.speedX
    this.y += this.speedY
    
    // 边界处理 - 从另一边出现
    if (this.x > canvas.width) this.x = 0
    if (this.x < 0) this.x = canvas.width
    if (this.y > canvas.height) this.y = 0
    if (this.y < 0) this.y = canvas.height
  }
  
  draw() {
    ctx.beginPath()
    ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2)
    ctx.fillStyle = this.color
    ctx.fill()
    
    // 添加光晕效果
    ctx.beginPath()
    ctx.arc(this.x, this.y, this.size * 2, 0, Math.PI * 2)
    ctx.fillStyle = this.color.replace(/[\d\.]+\)$/g, (this.alpha * 0.4) + ')')
    ctx.fill()
  }
}

// 初始化粒子系统
const initParticles = () => {
  canvas = particleCanvas.value
  ctx = canvas.getContext('2d')
  
  // 设置画布尺寸为全屏
  const resizeCanvas = () => {
    canvas.width = window.innerWidth
    canvas.height = window.innerHeight
  }
  
  resizeCanvas()
  window.addEventListener('resize', resizeCanvas)
  
  // 创建粒子
  const particleCount = Math.floor((window.innerWidth * window.innerHeight) / 6000)
  particles = []
  for (let i = 0; i < particleCount; i++) {
    particles.push(new Particle())
  }
  
  // 开始动画
  const animate = () => {
    // 使用半透明填充创造拖尾效果
    ctx.fillStyle = 'rgba(10, 15, 40, 0.03)'
    ctx.fillRect(0, 0, canvas.width, canvas.height)
    
    // 更新和绘制粒子
    particles.forEach(particle => {
      particle.update()
      particle.draw()
    })
    
    // 绘制粒子间的连线
    ctx.lineWidth = 0.8
    
    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        const dx = particles[i].x - particles[j].x
        const dy = particles[i].y - particles[j].y
        const distance = Math.sqrt(dx * dx + dy * dy)
        
        if (distance < 120) {
          const opacity = 1 - (distance / 120)
          // 使用更漂亮的连线颜色
          ctx.strokeStyle = `rgba(120, 160, 255, ${opacity * 0.15})`
          ctx.beginPath()
          ctx.moveTo(particles[i].x, particles[i].y)
          ctx.lineTo(particles[j].x, particles[j].y)
          ctx.stroke()
        }
      }
    }
    
    animationId = requestAnimationFrame(animate)
  }
  
  animate()
  
  return () => {
    window.removeEventListener('resize', resizeCanvas)
  }
}

onMounted(() => {
  const cleanup = initParticles()
  
  // 修复自动填充检测 - 使用多种方式确保捕获
  const autoFillCheck = () => {
    checkAutoFill()
    
    // 多次检查，确保捕获各种浏览器的自动填充
    setTimeout(checkAutoFill, 50)
    setTimeout(checkAutoFill, 150)
    setTimeout(checkAutoFill, 300)
    setTimeout(checkAutoFill, 500)
    setTimeout(checkAutoFill, 1000)
  }
  
  // 初始检查
  autoFillCheck()
  
  // 监听各种可能触发自动填充的事件
  window.addEventListener('load', autoFillCheck)
  document.addEventListener('DOMContentLoaded', autoFillCheck)
  window.addEventListener('focus', autoFillCheck)
  document.addEventListener('visibilitychange', autoFillCheck)
  
  // 添加输入事件监听器
  if (usernameInput.value) {
    usernameInput.value.addEventListener('input', () => checkAutoFill())
  }
  if (passwordInput.value) {
    passwordInput.value.addEventListener('input', () => checkAutoFill())
  }
  
  onUnmounted(() => {
    if (animationId) {
      cancelAnimationFrame(animationId)
    }
    window.removeEventListener('load', autoFillCheck)
    document.removeEventListener('DOMContentLoaded', autoFillCheck)
    window.removeEventListener('focus', autoFillCheck)
    document.removeEventListener('visibilitychange', autoFillCheck)
    
    if (usernameInput.value) {
      usernameInput.value.removeEventListener('input', () => checkAutoFill())
    }
    if (passwordInput.value) {
      passwordInput.value.removeEventListener('input', () => checkAutoFill())
    }
    
    cleanup && cleanup()
  })
})
</script>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.login-container {
  min-height: 100vh;
  width: 100vw;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  position: fixed;
  top: 0;
  left: 0;
  overflow: hidden;
  font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
  z-index: 1000;
}

.particle-background {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: 1;
  display: block;
  background: linear-gradient(135deg, #1a1f35 0%, #2d1b69 100%);
}

.square-login-box {
  position: relative;
  z-index: 2;
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 16px;
  padding: 50px 45px;
  width: 60%;
  max-width: 520px;
  min-height: 520px;
  box-shadow: 
    inset 0 1px 0 rgba(255, 255, 255, 0.1),
    inset 0 -1px 0 rgba(0, 0, 0, 0.05);
  animation: slideUp 0.8s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.login-header {
  text-align: center;
  margin-bottom: 42px;
}

.login-header h1 {
  color: rgba(255, 255, 255, 0.95);
  font-size: 30px;
  font-weight: 700;
  margin-bottom: 10px;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  letter-spacing: 0.5px;
}

.login-header p {
  color: rgba(255, 255, 255, 0.8);
  font-size: 15px;
  font-weight: 500;
  letter-spacing: 0.3px;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.form-group {
  position: relative;
}

.form-group.floating {
  margin-top: 18px;
}

.form-group.floating input {
  width: 100%;
  padding: 18px 12px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.95);
  font-size: 18px;
  font-weight: 500;
  outline: none;
  transition: all 0.3s ease;
  font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* 输入框聚焦状态 - 加强显示 */
.form-group.floating input:focus {
  background: rgba(255, 255, 255, 0.12);
  border-color: rgba(255, 255, 255, 0.5);
  box-shadow: 0 0 0 2px rgba(100, 150, 255, 0.3);
  transform: translateY(-2px);
}

.form-group.floating label {
  position: absolute;
  top: 18px;
  left: 12px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 18px;
  pointer-events: none;
  transition: all 0.3s ease;
  font-weight: 500;
  background: transparent;
  padding: 0 4px;
}

/* 修复浏览器自动填充时的标签动画 */
.form-group.floating input:focus ~ label,
.form-group.floating input.has-value ~ label,
.form-group.floating input:valid ~ label {
  top: -10px;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.95);
  font-weight: 600;
  background: rgba(26, 31, 53, 0.8);
  backdrop-filter: blur(5px);
  border-radius: 4px;
  padding: 0 6px;
}

.underline {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 0;
  height: 2px;
  background: linear-gradient(90deg, #64b5f6, #9575cd);
  transition: width 0.4s ease;
  border-radius: 1px;
}

.form-group.floating input:focus ~ .underline {
  width: 100%;
}

.role-label {
  display: block;
  color: rgba(255, 255, 255, 0.95);
  margin-bottom: 14px;
  font-weight: 600;
  font-size: 16px;
}

.role-options {
  display: flex;
  gap: 14px;
  flex-wrap: wrap;
}

.role-option {
  flex: 1;
  min-width: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px 18px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.95);
  font-size: 16px;
}

.role-option:hover {
  background: rgba(255, 255, 255, 0.12);
  transform: translateY(-2px);
}

.role-option.active {
  background: rgba(255, 255, 255, 0.18);
  border-color: rgba(255, 255, 255, 0.4);
  color: white;
}

.selection-indicator {
  position: absolute;
  top: 10px;
  right: 10px;
  width: 8px;
  height: 8px;
  background: rgba(255, 255, 255, 0.7);
  border-radius: 50%;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.role-option.active .selection-indicator {
  background: #64b5f6;
  opacity: 1;
}

.login-button {
  width: 100%;
  padding: 18px;
  background: linear-gradient(135deg, #64b5f6 0%, #9575cd 100%);
  border: none;
  border-radius: 8px;
  color: white;
  font-size: 18px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 12px;
  position: relative;
  overflow: hidden;
  letter-spacing: 0.5px;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
  font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
}

.login-button:hover:not(:disabled) {
  transform: translateY(-2px);
  background: linear-gradient(135deg, #42a5f5 0%, #7e57c2 100%);
  box-shadow: 0 4px 12px rgba(100, 181, 246, 0.4);
}

.login-button:active:not(:disabled) {
  transform: translateY(0);
}

.login-button:disabled {
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.5);
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.login-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(255, 255, 255, 0.3),
    transparent
  );
  transition: left 0.6s ease;
}

.login-button:hover:not(:disabled)::before {
  left: 100%;
}

.button-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  font-size: 18px;
}

.loading-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid transparent;
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.error-message {
  margin-top: 20px;
  padding: 14px 16px;
  background: rgba(239, 83, 80, 0.15);
  border: 1px solid rgba(239, 83, 80, 0.3);
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.95);
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  animation: fadeIn 0.3s ease;
  font-size: 16px;
  font-weight: 500;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}

.error-icon {
  font-size: 18px;
  font-weight: bold;
  color: #ff5252;
}

/* 动画定义 */
@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(100px) scale(0.9);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes shake {
  0%, 100% {
    transform: translateX(0);
  }
  10%, 30%, 50%, 70%, 90% {
    transform: translateX(-5px);
  }
  20%, 40%, 60%, 80% {
    transform: translateX(5px);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .square-login-box {
    width: 85%;
    padding: 40px 30px;
    min-height: auto;
  }
  
  .form-group.floating input {
    font-size: 16px;
    padding: 16px 12px;
  }
  
  .form-group.floating label {
    font-size: 16px;
  }
}

@media (max-width: 480px) {
  .square-login-box {
    width: 90%;
    padding: 35px 25px;
  }
  
  .role-options {
    flex-direction: column;
  }
  
  .login-header h1 {
    font-size: 26px;
  }
  
  .form-group.floating input {
    padding: 14px 12px;
  }
}
@media (max-width: 480px) {
  .role-options {
    flex-direction: column;
  }
  
  .role-option {
    width: 100%;
  }
}
</style>