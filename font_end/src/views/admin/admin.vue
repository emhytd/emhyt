<template>
  <div class="login-container">
    <!-- 粒子背景画布 -->
    <canvas ref="particleCanvas" class="particle-background"></canvas>
    
    <!-- index1盒子，放在square-login-box外面 -->
    <div class="role-option index1-box">
      
       <div class="teacher-top index1-top">
         <div>&nbsp&nbsp&nbsp<span>你好，管理员</span></div>
          <button class="teacher-btn index1-btn" @click="handleLogout">注销</button>
         </div>


    </div>
    
    <!-- 方形毛玻璃登录框 -->
    <div class="square-login-box">
      <div class="role-options">
        <!-- 原来的教师盒子 -->
        <div class="role-option teacher-box">
          <div class="teacher-top">
          <button class="teacher-btn" @click="index">首页</button>
         <button class="teacher-btn" @click="student_edit">学生信息</button>
           <button class="teacher-btn" @click="teacher_edit">教师信息</button>
           <button class="teacher-btn" @click="class_edit">班级信息</button>
           <button class="teacher-btn" @click="course_edit">选课信息</button>
          <button class="teacher-btn" @click="class_query">班级成绩总览</button>
          <button class="teacher-btn" @click="teacher_query">教师教学总览</button>
          <button class="teacher-btn" @click="bulk_import">批量导入成绩</button>
          
            <!-- <button class="teacher-btn" @click="student_edit">学生信息</button> -->
           <button class="teacher-btn" @click="deadline">设置查询时间段</button>
         </div>
        </div>
        
        <!-- 展示内容表格 -->
        <div class="content-table">
         <router-view></router-view>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router';
const router=useRouter()
const class_query=()=>{
  router.push('/admin/class_query')
}
const teacher_query=()=>{
  router.push('/admin/teacher_query')
}

const index=()=>{
router.push('/admin')
}
const bulk_import=()=>{
  router.push('/admin/bulk_import')
}


const student_edit=()=>{
  router.push('/admin/student_edit')
}

const teacher_edit=()=>{
  router.push('/admin/teacher_edit')
}
const class_edit=()=>{
  router.push('/admin/class_edit')
}
const course_edit=()=>{
  router.push('/admin/course_edit')
}


const deadline=()=>{
  router.push('/admin/deadline')
}

const username = ref('')

onMounted(() => {
  username.value = localStorage.getItem('username')
})


import useAuth from '../../composables/useAuth'

const { logout } = useAuth()
const handleLogout = async () => {
  try {
    await logout()
    // 注销后，logout函数已经跳转到登录页面，所以这里不需要再跳转
  } catch (error) {
    console.error('注销失败', error)
  }
}



import { ref, onMounted, onUnmounted } from 'vue'


import get_user_name from '@/components/get_user_name.vue';






const particleCanvas = ref(null)

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
      'rgba(100, 150, 255, ALPHA)', // 柔和的蓝色
      'rgba(150, 100, 255, ALPHA)', // 柔和的紫色
      'rgba(80, 200, 255, ALPHA)',  // 天蓝色
      'rgba(200, 100, 255, ALPHA)'  // 紫红色
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
  
  onUnmounted(() => {
    if (animationId) {
      cancelAnimationFrame(animationId)
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
  flex-direction: column;
  align-items: center;
  background: transparent;
  position: fixed;
  top: 0;
  left: 0;
  overflow: hidden;
  font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
  z-index: 1000;
  padding: 0;
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

/* index1盒子样式 - 减小高度 */
.index1-box {
  position: relative;
  z-index: 3;
  display: flex;
  justify-content: flex-start;
  align-items: center;
  padding: 12px 20px;
  background: rgba(255, 200, 100, 0.08);
  backdrop-filter: blur(30px) saturate(200%);
  -webkit-backdrop-filter: blur(30px) saturate(200%);
  border: 1px solid rgba(255, 180, 80, 0.4);
  border-radius: 0;
  font-weight: 600;
  color: rgba(255, 240, 200, 0.95);
  font-size: 24px;
  width: 100%;
  max-width: none;
  min-height: 50px;
  margin-bottom: 0;
  box-shadow: 
    inset 0 1px 0 rgba(255, 255, 255, 0.1),
    0 4px 20px rgba(0, 0, 0, 0.15),
    0 0 15px rgba(255, 180, 80, 0.2);
  transition: none;
  cursor: default;
  animation: slideUp 0.8s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

/* 取消index1的悬停效果 */
.index1-box:hover {
  background: rgba(255, 200, 100, 0.08);
  transform: none;
  box-shadow: 
    inset 0 1px 0 rgba(255, 255, 255, 0.1),
    0 4px 20px rgba(0, 0, 0, 0.15),
    0 0 15px rgba(255, 180, 80, 0.2);
}

.square-login-box {
  position: relative;
  z-index: 2;
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 16px 16px 16px 16px;
  padding: 40px;
  width: 100%;
  height: calc(100vh - 50px);
  max-width: none;
  min-height: auto;
  box-shadow: 
    inset 0 1px 0 rgba(255, 255, 255, 0.1), 
    inset 0 -1px 0 rgba(0, 0, 0, 0.05),
    0 8px 32px rgba(0, 0, 0, 0.2);
  animation: slideUp 0.8s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  display: flex;
  align-items: flex-start;
  justify-content: flex-start;
  overflow-y: auto;
  margin-top: 0;
}

.role-options {
  display: flex;
  flex-direction: row;
  width: 100%;
  height: 100%;
  align-items: stretch;
  justify-content: flex-start;
  gap: 20px;
}

.content-table {
  flex: 1;
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: 10px;
  text-align: center;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

th {
  background-color: rgba(244, 244, 244, 0.1);
  color: rgba(255, 255, 255, 0.9);
}

td {
  color: rgba(255, 255, 255, 0.8);
  background-color: rgba(255, 255, 255, 0.05);
}

.role-option {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.95);
  font-size: 24px;
}

/* 教师盒子样式 */
.teacher-box {
  flex: 0 0 13%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  color: rgba(255, 255, 255, 0.95);
  font-size: 20px;
  font-weight: 600;
  flex-direction: column;
  padding: 15px;
}

/* 教师盒子的悬停动画 */
.teacher-box:hover {
  background: rgba(255, 255, 255, 0.12);
  transform: translateY(-5px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
}

.index-box, .content-box {
  width: 45%;
  height: 94vh;
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

/* 响应式设计 */
@media (max-width: 768px) {
  .square-login-box {
    padding: 20px 15px;
    height: calc(100vh - 50px);
  }
  
  .index1-box {
    font-size: 20px;
    padding: 10px 15px;
    min-height: 45px;
  }
  
  .role-option {
    font-size: 20px;
    padding: 15px;
  }
  
  .content-table {
    width: 95%;
  }
}

@media (max-width: 480px) {
  .square-login-box {
    padding: 15px 10px;
    height: calc(100vh - 45px);
    border-radius: 12px 12px 12px 12px;
  }
  
  .index1-box {
    font-size: 18px;
    padding: 8px 12px;
    min-height: 40px;
    backdrop-filter: blur(20px) saturate(180%);
    -webkit-backdrop-filter: blur(20px) saturate(180%);
  }
  
  .role-option {
    font-size: 18px;
    padding: 12px;
  }
  
  .teacher-box {
    min-height: 50px;
  }
  
  th, td {
    padding: 6px 4px;
    font-size: 14px;
  }
}

/* ========== 教师盒子内按钮样式 ========== */
/* 顶部按钮容器（竖向排列） */
.teacher-top {
  width: 90%;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
  margin-top: 10px;
}

/* 教师盒子内按钮样式 - 使用更具体的选择器 */
.teacher-box .teacher-btn {
  width: 100%;
  padding: 12px 0;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.25);
  border-radius: 10px;
  color: rgba(255, 255, 255, 0.95);
  font-size: 18px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(8px);
  text-align: center;
}

.teacher-box .teacher-btn:hover {
  background: rgba(255, 255, 255, 0.25);
  transform: translateY(-3px);
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.25);
}

/* ========== index1盒子内样式 ========== */
/* index1盒子内顶部容器 - 确保横向排列且文字在左按钮在右 */
.index1-top {
  display: flex;
  flex-direction: row !important; /* 强制横向排列 */
  justify-content: space-between !important; /* 强制两端对齐 */
  align-items: center;
  width: 100%;
  height: 100%;
  gap: 0; /* 确保没有间隙 */
}

/* index1盒子内文字样式 - 确保靠左 */
.index1-top div {
  font-size: 28px;
  display: flex;
  align-items: center;
  height: 100%;
  flex-shrink: 0; /* 防止文字被压缩 */
  margin-right: auto; /* 确保文字靠左 */
}

/* index1盒子内按钮样式 - 确保靠右 */
.index1-btn {
  font-size: 16px;
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.25);
  border-radius: 10px;
  color: rgba(255, 255, 255, 0.95);
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(8px);
  width: auto;
  height: auto;
  min-width: 100px;
  max-width: 150px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-left: auto; /* 确保按钮靠右 */
  flex-shrink: 0; /* 防止按钮被压缩 */
}

.index1-btn:hover {
  background: rgba(255, 255, 255, 0.25);
  transform: translateY(-3px);
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.25);
}

/* 确保index1-top不会被其他样式覆盖 */
.teacher-top.index1-top {
  flex-direction: row !important;
  justify-content: space-between !important;
}
</style>