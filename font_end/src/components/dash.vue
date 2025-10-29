<template>
  <div class="dashboard-container">
    <!-- 顶部学期选择器 -->
    <div class="dashboard-header">
      <div class="header-title-section">
        <h1 class="dashboard-title">教务管理系统</h1>
        <p class="dashboard-subtitle">数据概览面板</p>
      </div>
      <div class="header-controls">
        <SemesterSelector 
          @semester-change="handleSemesterChange"
          :initialSemesterId="selectedSemesterId ? String(selectedSemesterId) : ''"
        />
        <div class="user-info">
          <div class="user-avatar">
            <i class="fas fa-user-circle"></i>
          </div>
          <div class="user-details">
            <div class="user-name">{{ userInfo.name }}</div>
            <div class="user-role">{{ userInfo.role }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 未选择学期时的提示 -->
    <div v-if="!selectedSemesterId" class="no-semester-prompt">
      <div class="prompt-content">
        <div class="prompt-icon">
          <i class="fas fa-calendar-alt"></i>
        </div>
        <h2 class="prompt-title">请选择学期</h2>
        <p class="prompt-description">选择一个学期以查看相关的数据统计和图表</p>
        <div class="prompt-hint">
          <i class="fas fa-lightbulb"></i>
          使用上方的学期选择器选择您要查看的学期
        </div>
      </div>
    </div>

    <!-- 数据内容区域（只在选择学期后显示） -->
    <div v-else>
      <!-- 关键指标卡片 -->
      <div class="metrics-grid">
        <div class="metric-card">
          <div class="metric-icon class-icon">
            <i class="fas fa-users"></i>
          </div>
          <div class="metric-content">
            <div class="metric-value">{{ metrics.classCount || 0 }}</div>
            <div class="metric-label">班级总数</div>
          </div>
          <div class="metric-trend" v-if="metrics.classCount > 0">
            <i class="fas fa-arrow-up"></i>
            <span>--</span>
          </div>
        </div>

        <div class="metric-card">
          <div class="metric-icon teacher-icon">
            <i class="fas fa-chalkboard-teacher"></i>
          </div>
          <div class="metric-content">
            <div class="metric-value">{{ metrics.teacherCount || 0 }}</div>
            <div class="metric-label">教师总数</div>
          </div>
          <div class="metric-trend" v-if="metrics.teacherCount > 0">
            <i class="fas fa-arrow-up"></i>
            <span>--</span>
          </div>
        </div>

        <div class="metric-card">
          <div class="metric-icon student-icon">
            <i class="fas fa-user-graduate"></i>
          </div>
          <div class="metric-content">
            <div class="metric-value">{{ metrics.studentCount || 0 }}</div>
            <div class="metric-label">学生总数</div>
          </div>
          <div class="metric-trend" v-if="metrics.studentCount > 0">
            <i class="fas fa-arrow-up"></i>
            <span>--</span>
          </div>
        </div>

        <div class="metric-card">
          <div class="metric-icon course-icon">
            <i class="fas fa-book"></i>
          </div>
          <div class="metric-content">
            <div class="metric-value">{{ metrics.courseCount || 0 }}</div>
            <div class="metric-label">课程总数</div>
          </div>
          <div class="metric-trend" v-if="metrics.courseCount > 0">
            <i class="fas fa-arrow-up"></i>
            <span>--</span>
          </div>
        </div>
      </div>

      <!-- 数据概览区域 -->
      <div class="overview-section">
        <!-- 班级概览 -->
        <div class="overview-card">
          <div class="card-header">
            <h3 class="card-title">
              <i class="fas fa-users"></i>
              班级成绩概览
            </h3>
            <button class="view-all-btn" @click="viewClassDetails" v-if="topClasses.length > 0">
              查看详情 <i class="fas fa-arrow-right"></i>
            </button>
          </div>
          <div class="card-content">
            <div class="class-list" v-if="topClasses.length > 0">
              <div v-for="classItem in topClasses" :key="classItem.class_id" class="class-item">
                <div class="class-avatar">
                  <i class="fas fa-school"></i>
                </div>
                <div class="class-info">
                  <div class="class-name">{{ classItem.class_name }}</div>
                  <div class="class-meta">
                    <span class="teacher-name">
                      <i class="fas fa-user-tie"></i>
                      {{ classItem.teacher_name || '未分配' }}
                    </span>
                    <span class="student-count">
                      <i class="fas fa-user-graduate"></i>
                      {{ classItem.student_count || 0 }}人
                    </span>
                  </div>
                </div>
                <div class="class-performance">
                  <div class="average-grade">
                    {{ (classItem.average_grade || 0).toFixed(1) }}
                  </div>
                  <div class="grade-label">平均分</div>
                </div>
              </div>
            </div>
            <div v-else class="empty-state">
              <i class="fas fa-inbox"></i>
              <p>暂无班级数据</p>
              <p class="empty-hint">当前学期没有找到班级信息</p>
            </div>
          </div>
        </div>

        <!-- 教师概览 -->
        <div class="overview-card">
          <div class="card-header">
            <h3 class="card-title">
              <i class="fas fa-chalkboard-teacher"></i>
              教师教学概览
            </h3>
            <button class="view-all-btn" @click="viewTeacherDetails" v-if="topTeachers.length > 0">
              查看详情 <i class="fas fa-arrow-right"></i>
            </button>
          </div>
          <div class="card-content">
            <div class="teacher-list" v-if="topTeachers.length > 0">
              <div v-for="teacher in topTeachers" :key="teacher.teacher_id" class="teacher-item">
                <div class="teacher-avatar">
                  <i class="fas fa-user-circle"></i>
                </div>
                <div class="teacher-info">
                  <div class="teacher-name">{{ teacher.teacher_name }}</div>
                  <div class="teacher-meta">
                    <span class="course-count">
                      <i class="fas fa-book"></i>
                      {{ teacher.course_count || 0 }}门课程
                    </span>
                    <span class="student-count">
                      <i class="fas fa-users"></i>
                      {{ teacher.student_count || 0 }}名学生
                    </span>
                  </div>
                </div>
                <div class="teacher-performance">
                  <div class="average-grade">
                    {{ (teacher.average_grade || 0).toFixed(1) }}
                  </div>
                  <div class="grade-label">均分</div>
                </div>
              </div>
            </div>
            <div v-else class="empty-state">
              <i class="fas fa-inbox"></i>
              <p>暂无教师数据</p>
              <p class="empty-hint">当前学期没有找到教师教学信息</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 统计图表区域 -->
      <div class="charts-section">
        <div class="chart-card">
          <div class="chart-header">
            <h3 class="chart-title">
              <i class="fas fa-chart-bar"></i>
              成绩分布
            </h3>
          </div>
          <div class="chart-content">
            <div class="grade-distribution" v-if="hasGradeData">
              <div v-for="(range, index) in gradeRanges" :key="index" class="distribution-item">
                <div class="range-label">{{ range.label }}</div>
                <div class="range-bar">
                  <div 
                    class="range-fill" 
                    :style="{ width: calculatePercentage(gradeDistribution[index]) + '%' }"
                  ></div>
                </div>
                <div class="range-count">{{ gradeDistribution[index] || 0 }}人</div>
              </div>
            </div>
            <div v-else class="empty-state">
              <i class="fas fa-chart-bar"></i>
              <p>暂无成绩数据</p>
              <p class="empty-hint">当前学期没有找到成绩分布信息</p>
            </div>
          </div>
        </div>

        <div class="chart-card">
          <div class="chart-header">
            <h3 class="chart-title">
              <i class="fas fa-fire"></i>
              热门课程
            </h3>
          </div>
          <div class="chart-content">
            <div class="popular-courses" v-if="popularCourses.length > 0">
              <div v-for="course in popularCourses" :key="course.course_id" class="course-item">
                <div class="course-info">
                  <div class="course-name">{{ course.course_name || '未知课程' }}</div>
                  <div class="course-type">{{ course.course_type || '未分类' }}</div>
                </div>
                <div class="course-stats">
                  <div class="student-count">
                    {{ course.student_count || 0 }}人
                  </div>
                  <div class="popularity-badge" :class="getPopularityClass(course.student_count)">
                    {{ getPopularityText(course.student_count) }}
                  </div>
                </div>
              </div>
            </div>
            <div v-else class="empty-state">
              <i class="fas fa-book"></i>
              <p>暂无课程数据</p>
              <p class="empty-hint">当前学期没有找到课程信息</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 系统状态 -->
      <div class="status-section">
        <div class="status-card">
          <div class="status-header">
            <h3 class="status-title">
              <i class="fas fa-server"></i>
              系统状态
            </h3>
          </div>
          <div class="status-content">
            <div class="status-item">
              <div class="status-label">数据状态</div>
              <div class="status-value">
                <span class="status-indicator" :class="dataStatus"></span>
                {{ dataStatusText }}
              </div>
            </div>
            <div class="status-item">
              <div class="status-label">最后更新</div>
              <div class="status-value">{{ lastUpdate || '--' }}</div>
            </div>
            <div class="status-item">
              <div class="status-label">当前学期</div>
              <div class="status-value">{{ currentSemesterName || '未选择' }}</div>
            </div>
            <div class="status-item">
              <div class="status-label">数据记录</div>
              <div class="status-value">
                {{ totalRecords || 0 }} 条
              </div>
            </div>
          </div>
        </div>

        <div class="quick-actions-card">
          <div class="actions-header">
            <h3 class="actions-title">
              <i class="fas fa-bolt"></i>
              快捷操作
            </h3>
          </div>
          <div class="actions-content">
            <button class="action-btn" @click="students_edit()">
              <i class="fas fa-user-graduate"></i>
              <span>学生管理</span>
            </button>
            <button class="action-btn" @click="viewTeacherDetails()">
              <i class="fas fa-chalkboard-teacher"></i>
              <span>教师管理</span>
            </button>
            <button class="action-btn" @click="courses_edit()">
              <i class="fas fa-book"></i>
              <span>课程管理</span>
            </button>
            <button class="action-btn" @click="courses_edit()">
              <i class="fas fa-chart-line"></i>
              <span>成绩管理</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-overlay">
      <div class="loading-content">
        <div class="loading-spinner"></div>
        <p>正在加载数据...</p>
      </div>
    </div>

    <!-- 错误提示 -->
    <div v-if="errorMessage" class="error-toast">
      <div class="error-content">
        <i class="fas fa-exclamation-triangle"></i>
        <span>{{ errorMessage }}</span>
        <button @click="clearError" class="error-close">
          <i class="fas fa-times"></i>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import SemesterSelector from './SemesterSelector.vue'

const router = useRouter()

// 响应式数据
const selectedSemesterId = ref('')
const semesterList = ref([])
const classData = ref([])
const teacherData = ref([])
const loading = ref(false)
const errorMessage = ref('')

// 用户信息
const userInfo = computed(() => {
  return {
    name: '管理员',
    role: '系统管理员'
  }
})

// 关键指标
const metrics = computed(() => {
  return {
    classCount: classData.value.length || 0,
    teacherCount: teacherData.value.length || 0,
    studentCount: calculateTotalStudents(),
    courseCount: calculateTotalCourses()
  }
})

// 是否有成绩数据
const hasGradeData = computed(() => {
  return gradeDistribution.value.some(count => count > 0)
})

// 总记录数
const totalRecords = computed(() => {
  return metrics.value.studentCount + metrics.value.courseCount
})

// 顶级班级（按平均分排序）
const topClasses = computed(() => {
  if (!classData.value.length) return []
  
  return classData.value
    .map(classItem => ({
      ...classItem,
      average_grade: calculateClassAverage(classItem),
      student_count: classItem.students?.length || 0
    }))
    .sort((a, b) => b.average_grade - a.average_grade)
    .slice(0, 4)
})

// 顶级教师（按平均分排序）
const topTeachers = computed(() => {
  if (!teacherData.value.length) return []
  
  return teacherData.value
    .map(teacher => ({
      teacher_id: teacher.teacher_id,
      teacher_name: teacher.teacher_name,
      average_grade: calculateTeacherAverage(teacher),
      student_count: calculateTeacherStudents(teacher),
      course_count: teacher.courses?.length || 0
    }))
    .sort((a, b) => b.average_grade - a.average_grade)
    .slice(0, 4)
})

// 成绩分布
const gradeRanges = [
  { label: '90-100', min: 90, max: 100 },
  { label: '80-89', min: 80, max: 89 },
  { label: '70-79', min: 70, max: 79 },
  { label: '60-69', min: 60, max: 69 },
  { label: '0-59', min: 0, max: 59 }
]

const gradeDistribution = computed(() => {
  const distribution = [0, 0, 0, 0, 0]
  
  classData.value.forEach(classItem => {
    classItem.students?.forEach(student => {
      student.courses?.forEach(course => {
        const grade = course.grade
        if (grade >= 90) distribution[0]++
        else if (grade >= 80) distribution[1]++
        else if (grade >= 70) distribution[2]++
        else if (grade >= 60) distribution[3]++
        else distribution[4]++
      })
    })
  })
  
  return distribution
})

// 热门课程
const popularCourses = computed(() => {
  const courseMap = new Map()
  
  classData.value.forEach(classItem => {
    classItem.students?.forEach(student => {
      student.courses?.forEach(course => {
        const courseId = course.course_id
        if (!courseMap.has(courseId)) {
          courseMap.set(courseId, {
            course_id: courseId,
            course_name: course.course_name,
            course_type: course.course_type,
            student_count: 0
          })
        }
        courseMap.get(courseId).student_count++
      })
    })
  })
  
  return Array.from(courseMap.values())
    .sort((a, b) => b.student_count - a.student_count)
    .slice(0, 5)
})

// 系统状态
const lastUpdate = ref('')
const currentSemesterName = computed(() => {
  const semester = semesterList.value.find(s => s.semester_id == selectedSemesterId.value)
  return semester ? semester.semester_name : '未选择'
})

const dataStatus = computed(() => {
  return classData.value.length > 0 || teacherData.value.length > 0 ? 'active' : 'inactive'
})

const dataStatusText = computed(() => {
  return classData.value.length > 0 || teacherData.value.length > 0 ? '数据正常' : '无数据'
})

// 工具函数
function calculateTotalStudents() {
  const studentIds = new Set()
  classData.value.forEach(classItem => {
    classItem.students?.forEach(student => {
      studentIds.add(student.student_id)
    })
  })
  return studentIds.size
}

function calculateTotalCourses() {
  const courseIds = new Set()
  classData.value.forEach(classItem => {
    classItem.students?.forEach(student => {
      student.courses?.forEach(course => {
        courseIds.add(course.course_id)
      })
    })
  })
  return courseIds.size
}

function calculateClassAverage(classItem) {
  if (!classItem.students?.length) return 0
  
  let total = 0
  let count = 0
  
  classItem.students.forEach(student => {
    student.courses?.forEach(course => {
      if (course.grade) {
        total += course.grade
        count++
      }
    })
  })
  
  return count > 0 ? total / count : 0
}

function calculateTeacherAverage(teacher) {
  if (!teacher.courses?.length) return 0
  
  let total = 0
  let count = 0
  
  teacher.courses.forEach(course => {
    course.students?.forEach(student => {
      if (student.grade) {
        total += student.grade
        count++
      }
    })
  })
  
  return count > 0 ? total / count : 0
}

function calculateTeacherStudents(teacher) {
  if (!teacher.courses?.length) return 0
  
  const studentIds = new Set()
  teacher.courses.forEach(course => {
    course.students?.forEach(student => {
      studentIds.add(student.student_id)
    })
  })
  
  return studentIds.size
}

function calculatePercentage(count) {
  const total = gradeDistribution.value.reduce((sum, val) => sum + val, 0)
  return total > 0 ? (count / total) * 100 : 0
}

function getPopularityClass(studentCount) {
  if (!studentCount) return 'low'
  if (studentCount > 100) return 'high'
  if (studentCount > 50) return 'medium'
  return 'low'
}

function getPopularityText(studentCount) {
  if (!studentCount) return '无数据'
  if (studentCount > 100) return '热门'
  if (studentCount > 50) return '一般'
  return '冷门'
}

// 数据获取函数
import apiConfig from '@/config/apiConfig';
async function fetchSemesters() {
  try {
    const token = localStorage.getItem('jwt_token')
    if (!token) {
      throw new Error('未找到认证令牌')
    }

    const response = await axios.get(apiConfig.STUDENT_API.GET_SEMESTERS, {
      headers: { 'Authorization': `Bearer ${token}` }
    })

    if (response.data.status === 'success') {
      semesterList.value = response.data.data
      // 不再默认选择第一个学期，让用户手动选择
    } else {
      throw new Error(response.data.error || '获取学期列表失败')
    }
  } catch (error) {
    handleError(error, '获取学期列表失败')
  }
}



async function fetchDashboardData() {
  if (!selectedSemesterId.value) return
  
  loading.value = true
  errorMessage.value = ''
  // 清空旧数据
  classData.value = []
  teacherData.value = []

  try {
    const token = localStorage.getItem('jwt_token')
    if (!token) {
      throw new Error('未找到认证令牌')
    }

    // 获取班级数据
    const classResponse = await axios.post(
      apiConfig.ADMIN_API.CHECK,
      {
        message_check: 'class',
        semester_id: selectedSemesterId.value
      },
      {
        headers: { 'Authorization': `Bearer ${token}` }
      }
    )

    if (classResponse.data.status !== 'success') {
      throw new Error(classResponse.data.error || '获取班级数据失败')
    }

    classData.value = classResponse.data.data || []

    // 获取教师数据
    const teacherResponse = await axios.post(
      apiConfig.ADMIN_API.CHECK,
      {
        message_check: 'teaching',
        semester_id: selectedSemesterId.value
      },
      {
        headers: { 'Authorization': `Bearer ${token}` }
      }
    )

    if (teacherResponse.data.status !== 'success') {
      throw new Error(teacherResponse.data.error || '获取教师数据失败')
    }

    teacherData.value = teacherResponse.data.data || []
    
    // 更新最后更新时间
    lastUpdate.value = new Date().toLocaleString()

  } catch (error) {
    handleError(error, '获取数据失败')
    // 确保在错误时数据为空
    classData.value = []
    teacherData.value = []
  } finally {
    loading.value = false
  }
}

// 事件处理函数
function handleSemesterChange(semesterId) {
  selectedSemesterId.value = semesterId
  fetchDashboardData()
}

function viewClassDetails() {
 router.push('/admin/grade_input_admin')

}

function viewTeacherDetails() {
  router.push('/admin/teacher_edit')
}
function courses_edit(){
  router.push('/admin/grade_input_admin')
}

function students_edit(){
  router.push('/admin/student_edit')
}

function handleError(error, defaultMessage) {
  if (error.response?.data?.error) {
    errorMessage.value = error.response.data.error
  } else if (error.message) {
    errorMessage.value = error.message
  } else {
    errorMessage.value = defaultMessage
  }
  
  // 如果是认证错误，清除token
  if (error.response?.status === 401) {
    localStorage.removeItem('jwt_token')
    setTimeout(() => {
      window.location.reload()
    }, 2000)
  }
}

function clearError() {
  errorMessage.value = ''
}

// 生命周期
onMounted(() => {
  fetchSemesters()
})
</script>

<style scoped>
/* 样式部分保持不变，与之前相同 */
.dashboard-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
  color: #fff;
  position: relative;
  min-height: 100vh;
}

/* 未选择学期提示样式 */
.no-semester-prompt {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  text-align: center;
}

.prompt-content {
  max-width: 500px;
  padding: 40px;
}

.prompt-icon {
  font-size: 4rem;
  color: rgba(255, 255, 255, 0.3);
  margin-bottom: 20px;
}

.prompt-title {
  font-size: 2rem;
  margin-bottom: 15px;
  color: rgba(255, 255, 255, 0.9);
  font-weight: 600;
}

.prompt-description {
  font-size: 1.1rem;
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 25px;
  line-height: 1.6;
}

.prompt-hint {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  background: rgba(52, 152, 219, 0.1);
  border: 1px solid rgba(52, 152, 219, 0.3);
  border-radius: 8px;
  color: #3498db;
  font-size: 0.95rem;
}

.prompt-hint i {
  font-size: 1.1rem;
}

/* 头部样式 */
.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.header-title-section .dashboard-title {
  font-size: 2.5rem;
  background: linear-gradient(90deg, #3498db, #2ecc71);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  margin-bottom: 5px;
  font-weight: 700;
}

.header-title-section .dashboard-subtitle {
  color: rgba(255, 255, 255, 0.7);
  font-size: 1.1rem;
}

.header-controls {
  display: flex;
  align-items: center;
  gap: 30px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  background: rgba(255, 255, 255, 0.05);
  padding: 10px 15px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.user-avatar {
  font-size: 2rem;
  color: #3498db;
}

.user-details .user-name {
  font-weight: 600;
  font-size: 1rem;
}

.user-details .user-role {
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.6);
}

/* 指标卡片网格 */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 30px;
}

.metric-card {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 25px;
  display: flex;
  align-items: center;
  gap: 15px;
  transition: all 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.1);
  position: relative;
  overflow: hidden;
}

.metric-card:hover {
  transform: translateY(-5px);
  background: rgba(255, 255, 255, 0.08);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.metric-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.8rem;
}

.metric-icon.class-icon {
  background: linear-gradient(135deg, #3498db, #2980b9);
}

.metric-icon.teacher-icon {
  background: linear-gradient(135deg, #9b59b6, #8e44ad);
}

.metric-icon.student-icon {
  background: linear-gradient(135deg, #2ecc71, #27ae60);
}

.metric-icon.course-icon {
  background: linear-gradient(135deg, #e74c3c, #c0392b);
}

.metric-content {
  flex: 1;
}

.metric-value {
  font-size: 2.2rem;
  font-weight: 700;
  margin-bottom: 5px;
  background: linear-gradient(90deg, #fff, #e0e0e0);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.metric-label {
  font-size: 0.95rem;
  color: rgba(255, 255, 255, 0.7);
  font-weight: 500;
}

.metric-trend {
  position: absolute;
  top: 15px;
  right: 15px;
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.8rem;
  color: #2ecc71;
  background: rgba(46, 204, 113, 0.1);
  padding: 4px 8px;
  border-radius: 6px;
}

/* 概览区域 */
.overview-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 30px;
}

.overview-card {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  overflow: hidden;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: rgba(255, 255, 255, 0.08);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.card-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 1.3rem;
  font-weight: 600;
}

.card-title i {
  color: #3498db;
}

.view-all-btn {
  background: rgba(52, 152, 219, 0.2);
  border: 1px solid rgba(52, 152, 219, 0.3);
  color: #3498db;
  padding: 8px 15px;
  border-radius: 6px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 5px;
}

.view-all-btn:hover {
  background: rgba(52, 152, 219, 0.3);
  transform: translateX(3px);
}

.card-content {
  padding: 20px;
}

.class-list, .teacher-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.class-item, .teacher-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 8px;
  transition: all 0.3s ease;
}

.class-item:hover, .teacher-item:hover {
  background: rgba(255, 255, 255, 0.06);
  transform: translateX(5px);
}

.class-avatar, .teacher-avatar {
  width: 50px;
  height: 50px;
  border-radius: 10px;
  background: rgba(52, 152, 219, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  color: #3498db;
  flex-shrink: 0;
}

.class-info, .teacher-info {
  flex: 1;
}

.class-name, .teacher-name {
  font-weight: 600;
  margin-bottom: 5px;
  font-size: 1.1rem;
}

.class-meta, .teacher-meta {
  display: flex;
  gap: 15px;
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.6);
}

.class-meta span, .teacher-meta span {
  display: flex;
  align-items: center;
  gap: 4px;
}

.class-performance, .teacher-performance {
  text-align: center;
  padding: 10px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  min-width: 80px;
}

.average-grade {
  font-size: 1.4rem;
  font-weight: 700;
  color: #2ecc71;
}

.grade-label {
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.6);
  margin-top: 2px;
}

/* 图表区域 */
.charts-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 30px;
}

.chart-card {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  overflow: hidden;
}

.chart-header {
  padding: 20px;
  background: rgba(255, 255, 255, 0.08);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.chart-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 1.3rem;
  font-weight: 600;
}

.chart-title i {
  color: #3498db;
}

.chart-content {
  padding: 20px;
}

.grade-distribution {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.distribution-item {
  display: flex;
  align-items: center;
  gap: 15px;
}

.range-label {
  width: 60px;
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.8);
  font-weight: 500;
}

.range-bar {
  flex: 1;
  height: 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  overflow: hidden;
}

.range-fill {
  height: 100%;
  background: linear-gradient(90deg, #3498db, #2ecc71);
  border-radius: 4px;
  transition: width 0.5s ease;
}

.range-count {
  width: 50px;
  text-align: right;
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.7);
}

.popular-courses {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.course-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 15px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 8px;
  transition: all 0.3s ease;
}

.course-item:hover {
  background: rgba(255, 255, 255, 0.06);
}

.course-info .course-name {
  font-weight: 600;
  margin-bottom: 3px;
}

.course-info .course-type {
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.6);
}

.course-stats {
  display: flex;
  align-items: center;
  gap: 10px;
}

.student-count {
  font-weight: 600;
  color: #3498db;
}

.popularity-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
}

.popularity-badge.high {
  background: rgba(231, 76, 60, 0.2);
  color: #e74c3c;
}

.popularity-badge.medium {
  background: rgba(241, 196, 15, 0.2);
  color: #f1c40f;
}

.popularity-badge.low {
  background: rgba(52, 152, 219, 0.2);
  color: #3498db;
}

/* 状态区域 */
.status-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.status-card, .quick-actions-card {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  overflow: hidden;
}

.status-header, .actions-header {
  padding: 20px;
  background: rgba(255, 255, 255, 0.08);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.status-title, .actions-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 1.3rem;
  font-weight: 600;
}

.status-title i {
  color: #3498db;
}

.actions-title i {
  color: #f39c12;
}

.status-content {
  padding: 20px;
}

.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.status-item:last-child {
  border-bottom: none;
}

.status-label {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.95rem;
}

.status-value {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
}

.status-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.status-indicator.active {
  background: #2ecc71;
}

.status-indicator.inactive {
  background: #e74c3c;
}

.actions-content {
  padding: 20px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
}

.action-btn {
  background: rgba(52, 152, 219, 0.1);
  border: 1px solid rgba(52, 152, 219, 0.2);
  border-radius: 8px;
  color: white;
  padding: 15px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.9rem;
}

.action-btn:hover {
  background: rgba(52, 152, 219, 0.2);
  transform: translateY(-3px);
}

.action-btn i {
  font-size: 1.5rem;
  color: #3498db;
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: rgba(255, 255, 255, 0.5);
}

.empty-state i {
  font-size: 3rem;
  margin-bottom: 15px;
  opacity: 0.5;
}

.empty-state p {
  font-size: 1rem;
  margin-bottom: 8px;
}

.empty-hint {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.4);
}

/* 加载状态 */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.loading-content {
  text-align: center;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  padding: 30px;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(255, 255, 255, 0.1);
  border-top: 3px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 15px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 错误提示 */
.error-toast {
  position: fixed;
  top: 20px;
  right: 20px;
  background: rgba(231, 76, 60, 0.9);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(231, 76, 60, 0.3);
  border-radius: 8px;
  padding: 15px 20px;
  max-width: 400px;
  z-index: 1000;
  animation: slideInRight 0.3s ease-out;
}

.error-content {
  display: flex;
  align-items: center;
  gap: 10px;
  color: white;
}

.error-content i {
  font-size: 1.2rem;
  flex-shrink: 0;
}

.error-content span {
  flex: 1;
  font-size: 0.95rem;
  font-weight: 500;
}

.error-close {
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.8);
  cursor: pointer;
  padding: 5px;
  border-radius: 4px;
  transition: all 0.3s ease;
  flex-shrink: 0;
}

.error-close:hover {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(100%);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .metrics-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .dashboard-container {
    padding: 15px;
  }
  
  .dashboard-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 20px;
  }
  
  .header-controls {
    width: 100%;
    flex-direction: column;
    gap: 15px;
  }
  
  .metrics-grid {
    grid-template-columns: 1fr;
  }
  
  .overview-section,
  .charts-section,
  .status-section {
    grid-template-columns: 1fr;
  }
  
  .actions-content {
    grid-template-columns: 1fr;
  }
  
  .class-meta,
  .teacher-meta {
    flex-direction: column;
    gap: 5px;
  }
}

@media (max-width: 480px) {
  .dashboard-title {
    font-size: 2rem;
  }
  
  .metric-card {
    padding: 20px;
  }
  
  .metric-value {
    font-size: 1.8rem;
  }
  
  .card-header {
    padding: 15px;
    flex-direction: column;
    gap: 10px;
    align-items: flex-start;
  }
  
  .view-all-btn {
    align-self: stretch;
    text-align: center;
  }
  
  .no-semester-prompt {
    min-height: 50vh;
  }
  
  .prompt-content {
    padding: 20px;
  }
  
  .prompt-icon {
    font-size: 3rem;
  }
  
  .prompt-title {
    font-size: 1.5rem;
  }
}
</style>