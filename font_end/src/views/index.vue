<template>
  <div class="login-container">
    <!-- 粒子背景画布 -->
    <canvas ref="particleCanvas" class="particle-background"></canvas>
    
    <!-- 方形毛玻璃登录框 - 只包含欢迎界面 -->
    <div class="square-login-box">
      <!-- 欢迎界面内容 -->
      <div class="welcome-content">
        <div class="welcome-header">
          <h1 class="welcome-title">学生成绩查询系统</h1>
          <p class="welcome-subtitle">lryzb</p>
        </div>
        
        <div class="welcome-illustration">
          <div class="graphic-element circle-1"></div>
          <div class="graphic-element circle-2"></div>
          <div class="graphic-element circle-3"></div>
          <div class="welcome-icon">✨</div>
        </div>
        
        <div class="welcome-action">
          <button class="login-btn" @click="enterSystem">
            <span class="btn-text">进入系统</span>
            <span class="btn-icon">→</span>
          </button>
          <p class="welcome-note"><div style="text-align: center; padding: 10px 0;">
    
</div>
</p><a href="https://beian.miit.gov.cn" target="_blank" rel="noopener">鲁ICP备2025188758号</a>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router';
const router = useRouter();

const enterSystem = () => {
  router.push('/student')
}

// 粒子系统代码
import { ref, onMounted, onUnmounted } from 'vue'

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
/* 登录容器 */
.login-container {
  min-height: 100vh;
  width: 100vw;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: transparent;
  position: fixed;
  top: 0;
  left: 0;
  overflow: hidden;
  font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
  z-index: 1000;
  padding: 0;
}

/* 粒子背景 */
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

/* 方形毛玻璃登录框 */
.square-login-box {
  position: relative;
  z-index: 2;
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 24px;
  padding: 60px 40px;
  width: 90%;
  max-width: 800px;
  min-height: auto;
  box-shadow: 
    inset 0 1px 0 rgba(255, 255, 255, 0.1), 
    inset 0 -1px 0 rgba(0, 0, 0, 0.05),
    0 8px 32px rgba(0, 0, 0, 0.2);
  animation: fadeIn 1s ease-out;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 欢迎内容样式 */
.welcome-content {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.welcome-header {
  text-align: center;
  margin-bottom: 50px;
  max-width: 700px;
}

.welcome-title {
  font-size: 2.8rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.95);
  margin-bottom: 20px;
  line-height: 1.2;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
}

.welcome-subtitle {
  font-size: 1.2rem;
  color: rgba(255, 255, 255, 0.7);
  font-weight: 500;
  line-height: 1.6;
}

.welcome-illustration {
  position: relative;
  width: 100%;
  max-width: 500px;
  height: 300px;
  margin: 40px 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(168, 237, 234, 0.1) 0%, rgba(254, 214, 227, 0.1) 100%);
  border-radius: 16px;
  overflow: hidden;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.graphic-element {
  position: absolute;
  border-radius: 50%;
  opacity: 0.8;
  animation: float 8s ease-in-out infinite;
  backdrop-filter: blur(5px);
}

.circle-1 {
  width: 120px;
  height: 120px;
  background: rgba(255, 255, 255, 0.15);
  top: 20%;
  left: 15%;
  animation-delay: 0s;
}

.circle-2 {
  width: 80px;
  height: 80px;
  background: rgba(255, 255, 255, 0.1);
  bottom: 25%;
  right: 20%;
  animation-delay: 1.5s;
}

.circle-3 {
  width: 60px;
  height: 60px;
  background: rgba(255, 255, 255, 0.2);
  top: 60%;
  left: 10%;
  animation-delay: 3s;
}

.welcome-icon {
  position: relative;
  z-index: 2;
  font-size: 5rem;
  color: rgba(255, 255, 255, 0.9);
  opacity: 0.9;
  text-shadow: 0 0 20px rgba(90, 103, 216, 0.5);
}

.welcome-action {
  text-align: center;
  margin-top: 30px;
}

.login-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: rgba(90, 103, 216, 0.3);
  color: white;
  border: 1px solid rgba(90, 103, 216, 0.5);
  padding: 16px 40px;
  font-size: 1.2rem;
  border-radius: 50px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 6px 20px rgba(90, 103, 216, 0.3);
  margin-bottom: 20px;
  min-width: 220px;
  backdrop-filter: blur(10px);
}

.login-btn:hover {
  background: rgba(90, 103, 216, 0.5);
  transform: translateY(-3px);
  box-shadow: 0 10px 25px rgba(90, 103, 216, 0.4);
}

.login-btn:active {
  transform: translateY(0);
}

.btn-text {
  margin-right: 12px;
  font-weight: 500;
}

.btn-icon {
  font-size: 1.3rem;
  transition: transform 0.3s ease;
}

.login-btn:hover .btn-icon {
  transform: translateX(5px);
}

.welcome-note {
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.6);
  margin-top: 15px;
}

/* 动画 */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes float {
  0%, 100% {
    transform: translateY(0) rotate(0deg);
  }
  50% {
    transform: translateY(-15px) rotate(5deg);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .square-login-box {
    padding: 40px 30px;
    width: 85%;
  }
  
  .welcome-title {
    font-size: 2.2rem;
  }
  
  .welcome-subtitle {
    font-size: 1.1rem;
  }
  
  .welcome-illustration {
    height: 250px;
  }
  
  .welcome-icon {
    font-size: 4rem;
  }
  
  .circle-1 {
    width: 100px;
    height: 100px;
  }
  
  .circle-2 {
    width: 70px;
    height: 70px;
  }
  
  .circle-3 {
    width: 50px;
    height: 50px;
  }
  
  .login-btn {
    padding: 14px 30px;
    font-size: 1.1rem;
    min-width: 200px;
  }
}

@media (max-width: 480px) {
  .square-login-box {
    padding: 30px 20px;
    width: 90%;
    border-radius: 20px;
  }
  
  .welcome-title {
    font-size: 1.8rem;
  }
  
  .welcome-subtitle {
    font-size: 1rem;
  }
  
  .welcome-illustration {
    height: 200px;
  }
  
  .welcome-icon {
    font-size: 3rem;
  }
  
  .login-btn {
    padding: 12px 25px;
    font-size: 1rem;
    min-width: 180px;
  }
}
</style>