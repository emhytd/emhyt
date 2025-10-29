<!-- StudentGrades.vue -->
<template>
  <div class="student-grades-container">
    <!-- 错误信息提示 -->
    <div v-if="errorMessage" class="error-message">
      <div class="error-content">
        <span class="error-icon">⚠️</span>
        <span class="error-text">{{ errorMessage }}</span>
        <button @click="clearError" class="error-close">×</button>
      </div>
    </div>
    
    <!-- 学生信息和学期信息 -->
    <div v-if="studentInfo && !errorMessage" class="info-section">
      <div class="student-info">
        <h3>学生信息</h3>
        <p>姓名: {{ studentInfo.student_name }}</p>
        <p>学号: {{ studentInfo.student_id }}</p>
        <p>班级: {{ studentInfo.class_id }}</p>
      </div>
      <div v-if="semesterInfo" class="semester-info">
        <h3>学期信息</h3>
        <p>学期: {{ semesterInfo.semester_name }}</p>
        <p>开始日期: {{ semesterInfo.start_date }}</p>
        <p>结束日期: {{ semesterInfo.end_date }}</p>
      </div>
    </div>
    
    <!-- 成绩表格 -->
    <div v-if="!errorMessage" class="grades-table-container">
      <table class="grades-table">
        <thead>
          <tr>
            <th>课程号</th>
            <th>课程名称</th>
            <th>课程类型</th>
            <th>得分</th>
            <th>学期</th>
            <th>授课老师</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="course in courseData" :key="course.course_id">
            <td>{{ course.course_id }}</td>
            <td>{{ course.course_name }}</td>
            <td>{{ course.course_type }}</td>
            <td :class="getGradeClass(course.grade)">{{ course.grade }}</td>
            <td>{{ course.semester_name }}</td>
            <td>{{ course.teacher_name }}</td>
          </tr>
          <tr v-if="courseData.length === 0 && !errorMessage">
            <td colspan="6" class="no-data">暂无成绩数据</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits, ref, watch } from 'vue'

// 定义组件属性
const props = defineProps({
  courseData: {
    type: Array,
    default: () => []
  },
  studentInfo: {
    type: Object,
    default: null
  },
  semesterInfo: {
    type: Object,
    default: null
  },
  errorMessage: {
    type: String,
    default: ''
  }
})

// 定义组件事件
const emit = defineEmits(['clear-error'])

// 根据分数获取样式类名
const getGradeClass = (grade) => {
  if (grade >= 90) return 'grade-excellent'
  if (grade >= 80) return 'grade-good'
  if (grade >= 60) return 'grade-pass'
  return 'grade-fail'
}

// 清除错误信息
const clearError = () => {
  emit('clear-error')
}
</script>

<style scoped>
.student-grades-container {
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

.info-section {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
  padding: 15px;
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(20px);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  position: relative;
  z-index: 1;
}

.student-info, .semester-info {
  flex: 1;
  padding: 0 15px;
}

.student-info h3, .semester-info h3 {
  color: rgba(255, 255, 255, 0.95);
  margin-bottom: 10px;
  font-size: 18px;
}

.student-info p, .semester-info p {
  color: rgba(255, 255, 255, 0.8);
  margin: 5px 0;
  font-size: 14px;
}

.grades-table-container {
  width: 100%;
  overflow-x: auto;
}

.grades-table {
  width: 100%;
  border-collapse: collapse;
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(20px);
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.15);
}

.grades-table th {
  background: rgba(255, 255, 255, 0.12);
  color: rgba(255, 255, 255, 0.95);
  padding: 12px 15px;
  text-align: left;
  font-weight: 600;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

.grades-table td {
  padding: 12px 15px;
  color: rgba(255, 255, 255, 0.8);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.grades-table tr:last-child td {
  border-bottom: none;
}

.grades-table tr:hover {
  background: rgba(255, 255, 255, 0.05);
}

/* 分数样式 */
.grade-excellent {
  color: #4CAF50 !important;
  font-weight: 600;
}

.grade-good {
  color: #8BC34A !important;
  font-weight: 600;
}

.grade-pass {
  color: #FFC107 !important;
  font-weight: 600;
}

.grade-fail {
  color: #F44336 !important;
  font-weight: 600;
}

.no-data {
  text-align: center;
  color: rgba(255, 255, 255, 0.6) !important;
  font-style: italic;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .info-section {
    flex-direction: column;
  }
  
  .student-info, .semester-info {
    padding: 10px 0;
  }
  
  .grades-table {
    font-size: 14px;
  }
  
  .grades-table th,
  .grades-table td {
    padding: 8px 10px;
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
  .grades-table-container {
    font-size: 12px;
  }
  
  .grades-table th,
  .grades-table td {
    padding: 6px 8px;
  }
  
  .error-message {
    padding: 12px 15px;
  }
  
  .error-text {
    font-size: 13px;
  }
}
</style>