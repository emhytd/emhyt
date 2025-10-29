<template>
  <div class="login-container">
    <!-- 粒子背景画布 -->
    <canvas ref="particleCanvas" class="particle-background"></canvas>
    
    <!-- index1盒子，放在square-login-box外面 -->
    <div class="role-option index1-box">
      <div class="teacher-top index1-top">
        <div>&nbsp;&nbsp;&nbsp;<get_user_name></get_user_name></div>
        <button class="teacher-btn index1-btn" @click="handleLogout">注销</button>
      </div>
    </div>
    
    <!-- 方形毛玻璃登录框 -->
    <div class="square-login-box">
      <div class="role-options">
        <!-- 原来的教师盒子 -->
        <div class="role-option teacher-box">
          <div class="teacher-top">
            <button class="teacher-btn" @click="serach">成绩查询</button>
            <button class="teacher-btn" @click="info_student">个人信息</button>
            <button class="teacher-btn" @click="resetFilters">重置筛选</button>
          </div>
        </div>
        
        <!-- 展示内容表格 -->
        <div class="content-table">
          <!-- 错误信息提示 -->
          <div v-if="errorMessage" class="error-message">
            <div class="error-content">
              <span class="error-icon">⚠️</span>
              <span class="error-text">{{ errorMessage }}</span>
              <button @click="clearErrorMessage" class="error-close">×</button>
            </div>
          </div>

          <!-- 控制区域 -->
          <div class="controls-container">
            <div class="header-section">
              <h2 class="section-title">
                <span class="title-icon">📊</span>
                成绩查询
              </h2>
              <div class="header-stats" v-if="originalCourseData.length > 0">
                <div class="stat-item">
                  <span class="stat-number">{{ overviewStats.totalCourses }}</span>
                  <span class="stat-label">总课程数</span>
                </div>
                <div class="stat-item">
                  <span class="stat-number">{{ overviewStats.averageGrade.toFixed(2) }}</span>
                  <span class="stat-label">平均成绩</span>
                </div>
                <div class="stat-item">
                  <span class="stat-number">{{ overviewStats.highestGrade }}</span>
                  <span class="stat-label">最高分</span>
                </div>
                <div class="stat-item">
                  <span class="stat-number">{{ overviewStats.creditsEarned }}</span>
                  <span class="stat-label">获得学分</span>
                </div>
              </div>
            </div>
            
            <!-- 学期选择器独立一行 -->
            <div class="semester-row">
              <div class="semester-selector-container">
                <label class="semester-label">选择学期:</label>
                <SemesterSelector 
                  @semester-change="handleSemesterChange"
                  class="semester-selector-main"
                />
              </div>
            </div>
            
            <!-- 筛选控制区域 -->
            <div class="filter-controls">
              <div class="filter-group">
                <!-- 搜索框 -->
                <div class="filter-item">
                  <label class="filter-label">搜索:</label>
                  <input 
                    type="text" 
                    v-model="filters.searchQuery" 
                    placeholder="课程名称、教师..." 
                    class="filter-input"
                    @input="applyFilters"
                  >
                </div>
                
                <!-- 成绩范围筛选 -->
                <div class="filter-item">
                  <label class="filter-label">成绩范围:</label>
                  <select v-model="filters.gradeRange" class="filter-select" @change="applyFilters">
                    <option value="">全部成绩</option>
                    <option value="90-100">90-100分</option>
                    <option value="80-89">80-89分</option>
                    <option value="70-79">70-79分</option>
                    <option value="60-69">60-69分</option>
                    <option value="0-59">0-59分</option>
                  </select>
                </div>
                
                <!-- 课程类型筛选 -->
                <div class="filter-item">
                  <label class="filter-label">课程类型:</label>
                  <select v-model="filters.courseType" class="filter-select" @change="applyFilters">
                    <option value="">全部类型</option>
                    <option v-for="type in availableCourseTypes" :key="type" :value="type">{{ type }}</option>
                  </select>
                </div>
                
                <!-- 排序方式 -->
                <div class="filter-item">
                  <label class="filter-label">排序:</label>
                  <select v-model="sortOption" class="filter-select" @change="applySorting">
                    <option value="courseName">课程名称</option>
                    <option value="gradeDesc">成绩降序</option>
                    <option value="gradeAsc">成绩升序</option>
                  </select>
                </div>
                
                <!-- 重置筛选按钮 -->
                <button @click="resetFilters" class="filter-reset-btn">
                  重置筛选
                </button>
              </div>
            </div>
            
            <!-- 结果统计 -->
            <div class="results-stats" v-if="filteredCourseData.length > 0">
              <span class="results-count">找到 {{ filteredCourseData.length }} 门课程</span>
              <span v-if="filtersApplied" class="filters-applied">（已应用筛选条件）</span>
            </div>
          </div>
          
          <!-- 数据展示区域 -->
          <div v-if="filteredCourseData.length > 0" class="data-container">
            <div class="table-container">
              <table class="grades-table">
                <thead>
                  <tr>
                    <th>课程名称</th>
                    <th>课程类型</th>
                    <th>成绩</th>
                    <th>教师</th>
                    <th>学期</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="course in filteredCourseData" :key="course.course_id">
                    <td>
                      <span class="course-name">{{ course.course_name }}</span>
                    </td>
                    <td>
                      <span class="course-type">{{ course.course_type || '未分类' }}</span>
                    </td>
                    <td>
                      <span class="grade-value" :class="getGradeClass(course.grade)">
                        {{ course.grade || '未评分' }}
                      </span>
                    </td>
                    <td>
                      <span class="teacher-name">{{ course.teacher_name || '-' }}</span>
                    </td>
                    <td>
                      <span class="semester-info">{{ course.semester_name || semesterInfo || '-' }}</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
          
          <!-- 无数据提示 -->
          <div v-if="originalCourseData.length === 0 && !errorMessage" class="no-data-container">
            <div class="no-data-content">
              <div class="no-data-icon">📚</div>
              <h3>暂无成绩数据</h3>
              <p>请先选择学期查看成绩信息</p>
            </div>
          </div>
          
          <div v-if="filteredCourseData.length === 0 && originalCourseData.length > 0" class="no-data-container">
            <div class="no-data-content">
              <div class="no-data-icon">🔍</div>
              <h3>没有找到匹配的课程</h3>
              <p>当前筛选条件下没有找到匹配的课程，请尝试调整筛选条件</p>
              <div class="no-data-actions">
                <button @click="resetFilters" class="no-data-action-btn">
                  <span class="btn-icon">🔄</span>
                  重置筛选
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import get_user_name from '@/components/get_user_name.vue';
import { useRouter } from 'vue-router';
import { ref, onMounted, computed } from 'vue';

const router = useRouter();

const serach = () => {
  router.push('/student')
}

const info_student = () => {
  router.push('/info_student')
}

const username = ref('')

onMounted(() => {
  username.value = localStorage.getItem('username')
})

import useAuth from '../composables/useAuth'

const { logout } = useAuth()
const handleLogout = async () => {
  try {
    await logout()
  } catch (error) {
    console.error('注销失败', error)
  }
}

const username_sc = ref('')
const courseData = ref([])
const studentInfo = ref(null)
const semesterInfo = ref(null)
const errorMessage = ref('')

import StudentGrades from "@/components/StudentGrades.vue"
import axios from 'axios';
import SemesterSelector from '@/components/SemesterSelector.vue'
import apiConfig from '@/config/apiConfig';

// 筛选相关数据
const filters = ref({
  searchQuery: '',
  gradeRange: '',
  courseType: '',
});

const sortOption = ref('courseName');

// 存储原始数据
const originalCourseData = ref([]);

// 计算属性：获取所有课程类型
const availableCourseTypes = computed(() => {
  const types = new Set(originalCourseData.value.map(course => course.course_type));
  return Array.from(types);
});

// 计算属性：筛选后的课程数据
const filteredCourseData = computed(() => {
  let result = [...originalCourseData.value];
  
  // 应用搜索查询
  if (filters.value.searchQuery) {
    const query = filters.value.searchQuery.toLowerCase();
    result = result.filter(course => 
      (course.course_name && course.course_name.toLowerCase().includes(query)) ||
      (course.teacher_name && course.teacher_name.toLowerCase().includes(query))
    );
  }
  
  // 应用成绩范围筛选
  if (filters.value.gradeRange) {
    const [min, max] = filters.value.gradeRange.split('-').map(Number);
    result = result.filter(course => {
      const grade = parseFloat(course.grade) || 0;
      if (max === 100) return grade >= min;
      return grade >= min && grade <= max;
    });
  }
  
  // 应用课程类型筛选
  if (filters.value.courseType) {
    result = result.filter(course => course.course_type === filters.value.courseType);
  }
  
  // 应用排序
  switch (sortOption.value) {
    case 'courseName':
      return result.sort((a, b) => (a.course_name || '').localeCompare(b.course_name || ''));
    case 'gradeDesc':
      return result.sort((a, b) => (parseFloat(b.grade) || 0) - (parseFloat(a.grade) || 0));
    case 'gradeAsc':
      return result.sort((a, b) => (parseFloat(a.grade) || 0) - (parseFloat(b.grade) || 0));
    default:
      return result;
  }
});

// 检查是否有筛选条件应用
const filtersApplied = computed(() => {
  return filters.value.searchQuery !== '' || 
         filters.value.gradeRange !== '' || 
         filters.value.courseType !== '' ||
         sortOption.value !== 'courseName';
});

// 成绩总览统计信息
const overviewStats = computed(() => {
  const courses = originalCourseData.value;
  const totalCourses = courses.length;
  
  // 计算平均成绩
  const validGrades = courses.filter(course => course.grade && !isNaN(parseFloat(course.grade)));
  const averageGrade = validGrades.length > 0 
    ? validGrades.reduce((sum, course) => sum + parseFloat(course.grade), 0) / validGrades.length 
    : 0;
  
  // 计算最高分
  const highestGrade = validGrades.length > 0 
    ? Math.max(...validGrades.map(course => parseFloat(course.grade))) 
    : 0;
  
  const creditsEarned = courses.reduce((total, course) => {
    const grade = parseFloat(course.grade) || 0;
    
    // 只有成绩达到60分以上才计入学分
    if (grade >= 60) {
      // 按成绩百分比折算学分（满分为100分，满学分为5分）
      const earnedCredit = (grade / 100) * 5;
      return total + earnedCredit;
    }
    return total;
  }, 0);
  
  return {
    totalCourses,
    averageGrade,
    highestGrade,
    creditsEarned: parseFloat(creditsEarned.toFixed(2)) // 保留两位小数
  };
});

// 获取成绩样式类
const getGradeClass = (grade) => {
  const numGrade = parseFloat(grade);
  if (isNaN(numGrade)) return '';
  if (numGrade >= 90) return 'grade-excellent';
  if (numGrade >= 80) return 'grade-good';
  if (numGrade >= 70) return 'grade-medium';
  if (numGrade >= 60) return 'grade-pass';
  return 'grade-fail';
};

// 应用筛选
const applyFilters = () => {
  // 计算属性会自动更新
};

// 应用排序
const applySorting = () => {
  // 计算属性会自动更新
};

// 重置筛选条件
const resetFilters = () => {
  filters.value = {
    searchQuery: '',
    gradeRange: '',
    courseType: '',
  };
  sortOption.value = 'courseName';
};

// 处理学期变化
const handleSemesterChange = (semesterId) => {
  console.log('父组件接收到学期ID:', semesterId)
  student_check(semesterId)
}

// 学生成绩查询函数
async function student_check(semesterId) {
  try {
    const token = localStorage.getItem('jwt_token') 
    const res = await axios.post(
      apiConfig.STUDENT_API.CHECK,
      {"semester_id": semesterId},
      {
        headers: { 'Authorization': `Bearer ${token}` }
      }
    )
    
    console.log(res.data)
    
    if (res.data.status === 'success') {
      // 更新数据
      originalCourseData.value = res.data.data;
      courseData.value = res.data.data;
      studentInfo.value = res.data.student_info;
      semesterInfo.value = res.data.semester_info;
      errorMessage.value = '';
    } else {
      errorMessage.value = res.data.error || '获取成绩数据失败';
      originalCourseData.value = [];
      courseData.value = [];
      studentInfo.value = null;
      semesterInfo.value = null;
    }
  } catch (error) {
    console.error('获取成绩数据时发生错误:', error);
    if (error.response && error.response.data && error.response.data.error) {
      errorMessage.value = error.response.data.error;
    } else {
      errorMessage.value = '获取成绩数据时发生错误';
    }
    originalCourseData.value = [];
    courseData.value = [];
    studentInfo.value = null;
    semesterInfo.value = null;
  }
}

// 清除错误信息
const clearErrorMessage = () => {
  errorMessage.value = ''
}

onMounted(() => {
  username_sc.value = localStorage.getItem('username')
})

// 粒子系统代码保持不变...
</script>

<style scoped>
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

/* 控制区域 - 优化样式 */
.controls-container {
  margin-bottom: 25px;
  padding: 25px;
  background: rgba(30, 30, 46, 0.9);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.3);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 15px;
}

.section-title {
  color: rgba(255, 255, 255, 0.95);
  font-size: 28px;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 0;
}

.title-icon {
  font-size: 32px;
}

.header-stats {
  display: flex;
  gap: 20px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 12px 20px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.stat-number {
  color: #667eea;
  font-size: 24px;
  font-weight: 700;
}

.stat-label {
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
  margin-top: 4px;
}

/* 学期选择器独立一行 */
.semester-row {
  width: 100%;
  margin-bottom: 20px;
  padding: 15px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
  min-height: 60px; /* 确保有足够的高度 */
  display: flex;
  align-items: center;
}

.semester-selector-container {
  display: flex;
  align-items: center;
  gap: 15px;
  width: 100%;
  transition: all 0.3s ease;
}

.semester-label {
  color: rgba(255, 255, 255, 0.9);
  font-size: 16px;
  font-weight: 600;
  white-space: nowrap;
  flex-shrink: 0;
}

.semester-selector-main {
  flex: 1;
  width: 100%;
  transition: all 0.3s ease;
}

/* 确保学期选择器折叠时下面内容下移 */
.semester-selector-main.collapsed + .filter-controls {
  margin-top: 20px;
}

/* 筛选控制区域 */
.filter-controls {
  margin-bottom: 20px;
  transition: all 0.3s ease;
}

.filter-group {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  align-items: flex-end;
}

.filter-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 180px;
  flex: 1;
}

.filter-label {
  color: rgba(255, 255, 255, 0.9);
  font-size: 14px;
  font-weight: 500;
}

.filter-input, .filter-select {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 6px;
  color: rgba(255, 255, 255, 0.9);
  padding: 10px 12px;
  font-size: 14px;
  transition: all 0.3s ease;
}

.filter-select {
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%23ffffff' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 12px center;
  background-size: 12px;
  cursor: pointer;
}

.filter-input:focus, .filter-select:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.3);
}

.filter-input::placeholder {
  color: rgba(255, 255, 255, 0.6);
}

.filter-reset-btn {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 6px;
  color: rgba(255, 255, 255, 0.9);
  padding: 10px 16px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  align-self: flex-end;
  height: fit-content;
}

.filter-reset-btn:hover {
  background: rgba(255, 255, 255, 0.15);
  transform: translateY(-1px);
}

/* 结果统计 */
.results-stats {
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.results-count {
  color: rgba(255, 255, 255, 0.9);
  font-weight: 500;
}

.filters-applied {
  color: rgba(255, 255, 255, 0.6);
  font-size: 14px;
}

/* 数据展示区域 */
.data-container {
  margin-top: 25px;
}

.table-container {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

/* 成绩表格样式 */
.grades-table {
  width: 100%;
  border-collapse: collapse;
}

.grades-table th {
  background: rgba(255, 255, 255, 0.08);
  color: rgba(255, 255, 255, 0.95);
  padding: 15px;
  text-align: left;
  font-weight: 600;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.grades-table td {
  padding: 15px;
  color: rgba(255, 255, 255, 0.8);
  border-bottom: 1px solid rgba(255, 255, 255, 0.03);
}

.grades-table tr:last-child td {
  border-bottom: none;
}

.grades-table tr:hover {
  background: rgba(255, 255, 255, 0.02);
}

.course-name {
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
}

.course-type, .teacher-name, .semester-info {
  color: rgba(255, 255, 255, 0.8);
}

/* 成绩样式 */
.grade-value {
  font-weight: 600;
  padding: 4px 8px;
  border-radius: 6px;
  display: inline-block;
}

.grade-excellent {
  background: rgba(76, 175, 80, 0.2);
  color: #4CAF50;
}

.grade-good {
  background: rgba(33, 150, 243, 0.2);
  color: #2196F3;
}

.grade-medium {
  background: rgba(255, 152, 0, 0.2);
  color: #FF9800;
}

.grade-pass {
  background: rgba(156, 39, 176, 0.2);
  color: #9C27B0;
}

.grade-fail {
  background: rgba(244, 67, 54, 0.2);
  color: #F44336;
}

/* 无数据提示样式 */
.no-data-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 40px;
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  border: 2px dashed rgba(255, 255, 255, 0.15);
  text-align: center;
  margin-top: 20px;
}

.no-data-content {
  max-width: 500px;
}

.no-data-icon {
  font-size: 80px;
  margin-bottom: 25px;
  display: block;
  color: rgba(255, 255, 255, 0.3);
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

.no-data-container h3 {
  color: rgba(255, 255, 255, 0.95);
  margin-bottom: 15px;
  font-size: 28px;
  font-weight: 700;
}

.no-data-container p {
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 30px;
  font-size: 16px;
  line-height: 1.5;
}

.no-data-actions {
  display: flex;
  gap: 15px;
  justify-content: center;
  flex-wrap: wrap;
}

.no-data-action-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 12px;
  padding: 15px 30px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 10px;
}

.no-data-action-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.5);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header-section {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .header-stats {
    width: 100%;
    justify-content: space-between;
  }
  
  .stat-item {
    flex: 1;
    min-width: 120px;
  }
  
  .semester-selector-container {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .filter-group {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filter-item {
    min-width: auto;
  }
  
  .filter-reset-btn {
    align-self: stretch;
  }
  
  .grades-table {
    font-size: 14px;
  }
  
  .grades-table th,
  .grades-table td {
    padding: 10px 8px;
  }
  
  .controls-container {
    padding: 20px;
  }
}

@media (max-width: 480px) {
  .controls-container {
    padding: 15px;
  }
  
  .section-title {
    font-size: 24px;
  }
  
  .title-icon {
    font-size: 28px;
  }
  
  .header-stats {
    flex-direction: column;
    gap: 10px;
  }
  
  .stat-item {
    flex-direction: row;
    justify-content: space-between;
    width: 100%;
  }
  
  .grades-table {
    font-size: 12px;
  }
  
  .grades-table th,
  .grades-table td {
    padding: 8px 6px;
  }
  
  .no-data-icon {
    font-size: 60px;
  }
  
  .no-data-container h3 {
    font-size: 24px;
  }
}

/* 原有样式保持不变 */
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
  display: flex;
  flex-direction: column;
  align-items: stretch;
  justify-content: flex-start;
  gap: 20px;
  padding: 0;
  margin: 0;
}

.content-table table {
  margin-top: 0px;
  width: 100%;
  border-collapse: collapse;
}

.semester-selector-wrapper {
  margin-bottom: 0 !important;
  padding-bottom: 0 !important;
  height: 46px !important;
  min-height: 46px !important;
  max-height: 46px !important;
  display: block !important;
  overflow: visible !important;
  position: relative !important;
  z-index: 100 !important;
}

@media (max-width: 768px) {
  .semester-selector-wrapper {
    height: 44px !important;
    min-height: 44px !important;
    max-height: 44px !important;
  }
  
  .content-table {
    gap: 15px;
  }
}

@media (max-width: 480px) {
  .semester-selector-wrapper {
    height: 42px !important;
    min-height: 42px !important;
    max-height: 42px !important;
  }
  
  .content-table {
    gap: 10px;
  }
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

.teacher-box:hover {
  background: rgba(255, 255, 255, 0.12);
  transform: translateY(-5px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
}

.index-box, .content-box {
  width: 45%;
  height: 94vh;
}

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

.teacher-top {
  width: 90%;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
  margin-top: 10px;
}

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

.index1-top {
  display: flex;
  flex-direction: row !important;
  justify-content: space-between !important;
  align-items: center;
  width: 100%;
  height: 100%;
  gap: 0;
}

.index1-top div {
  font-size: 28px;
  display: flex;
  align-items: center;
  height: 100%;
  flex-shrink: 0;
  margin-right: auto;
}

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
  margin-left: auto;
  flex-shrink: 0;
}

.index1-btn:hover {
  background: rgba(255, 255, 255, 0.25);
  transform: translateY(-3px);
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.25);
}

.teacher-top.index1-top {
  flex-direction: row !important;
  justify-content: space-between !important;
}

/* 为所有下拉选项设置深色背景 */
select option {
  background: rgba(30, 30, 46, 0.95) !important;
  color: rgba(255, 255, 255, 0.9) !important;
  border: none;
  outline: none;
}

/* 为下拉选择框设置样式 */
select {
  background: rgba(255, 255, 255, 0.1) !important;
  color: rgba(255, 255, 255, 0.9) !important;
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
}

/* 鼠标悬停效果 */
select option:hover {
  background: rgba(102, 126, 234, 0.3) !important;
}

/* 选中状态 */
select option:checked {
  background: rgba(102, 126, 234, 0.5) !important;
}

/* 深度选择器样式，确保影响子组件 */
:deep(.semester-buttons-container) {
  display: flex !important;
  flex-direction: row !important;
  flex-wrap: wrap !important;
  gap: 8px !important;
  width: 100% !important;
  transition: all 0.3s ease !important;
}

:deep(.semester-button) {
  flex: 1 !important;
  min-width: 120px !important;
  padding: 10px 12px !important;
  background: rgba(255, 255, 255, 0.1) !important;
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
  border-radius: 6px !important;
  color: rgba(255, 255, 255, 0.9) !important;
  font-size: 14px !important;
  cursor: pointer !important;
  transition: all 0.3s ease !important;
  white-space: nowrap !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
  text-align: center !important;
}

:deep(.semester-button:hover) {
  background: rgba(255, 255, 255, 0.15) !important;
  border-color: rgba(255, 255, 255, 0.3) !important;
}

:deep(.semester-button.active) {
  background: rgba(102, 126, 234, 0.3) !important;
  border-color: #667eea !important;
  color: #fff !important;
}

/* 响应式调整学期选择器 */
@media (max-width: 768px) {
  :deep(.semester-buttons-container) {
    flex-direction: column !important;
  }
  
  :deep(.semester-button) {
    min-width: 100% !important;
  }
}
</style>