<template>
  <div class="teacher-query-container">
    <!-- 学期选择器 -->
    <SemesterSelector
      :initial-semester-id="initialSemesterId"
      @semester-change="handleSemesterChange"
      class="semester-selector-section"
    />

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
      <p>正在查询数据...</p>
    </div>
    
    <!-- 查询控制区域 -->
    <div class="query-controls">
      <h2 class="section-title">📚教师查询</h2>
      
      <div class="button-group">
        <button 
          @click="handleQuery('class')" 
          class="query-btn"
          :disabled="loading || !currentSemesterId"
          :class="{ active: currentQueryType === 'class' }"
        >
          <span class="btn-icon">👨‍🏫</span>
          班级管理查询
        </button>
        
        <!-- 隐藏teaching按钮 -->
        <button 
          v-if="false"
          @click="handleQuery('teaching')" 
          class="query-btn"
          :disabled="loading || !currentSemesterId"
          :class="{ active: currentQueryType === 'teaching' }"
        >
          <span class="btn-icon">📚</span>
          授课课程查询
        </button>
      </div>
      
      <div v-if="!currentSemesterId" class="semester-warning">
        <span class="warning-icon">ℹ️</span>
        请先选择学期
      </div>
      
      <!-- 显示当前选中的学期信息 -->
      <!-- <div v-if="currentSemesterId" class="current-semester-info">
        <span class="info-icon">📅</span>
        当前学期: {{ currentSemesterName }}
      </div> -->
    </div>
    
    <!-- 班级模式数据展示 -->
    <div v-if="currentQueryType === 'class' && classData.length > 0 && !loading" class="query-results">
      <div class="results-header">
        <h3 class="results-title">
          班级管理信息
          <span class="results-count">(共 {{ classData.length }} 个班级)</span>
        </h3>
      </div>
      
      <div class="class-results-container">
        <div v-for="classItem in classData" :key="classItem.class_id" class="class-card">
          <div class="class-header" @click="toggleClassExpansion(classItem.class_id)">
            <div class="class-info">
              <h4 class="class-name">{{ classItem.class_name }}</h4>
              <div class="class-details">
                <span class="detail-item">班级ID: {{ classItem.class_id }}</span>
                <span class="detail-item">学生人数: {{ classItem.students.length }}</span>
                <span class="detail-item">班级平均分: {{ classItem.average_grade.toFixed(1) }}</span>
              </div>
            </div>
            <div class="class-status-container">
              <div class="class-status" :class="getClassStatusClass(classItem.average_grade)">
                {{ getClassStatusText(classItem.average_grade) }}
              </div>
              <div class="collapse-icon">
                {{ classItem.isExpanded ? '▼' : '►' }}
              </div>
            </div>
          </div>
          
          <div v-show="classItem.isExpanded" class="students-container">
            <div v-for="student in classItem.students" :key="student.student_id" class="student-card">
              <div class="student-header" @click="toggleStudentExpansion(student.student_id)">
                <div class="student-info">
                  <h5 class="student-name">{{ student.student_name }}</h5>
                  <div class="student-details">
                    <span class="detail-item">学号: {{ student.student_id }}</span>
                    <span class="detail-item">课程数: {{ student.courses.length }}</span>
                    <span class="detail-item">平均分: {{ student.average_grade.toFixed(1) }}</span>
                  </div>
                </div>
                <div class="student-status-container">
                  <div class="student-status" :class="getStudentStatusClass(student.average_grade)">
                    {{ getStudentStatusText(student.average_grade) }}
                  </div>
                  <div class="collapse-icon">
                    {{ student.isExpanded ? '▼' : '►' }}
                  </div>
                </div>
              </div>
              
              <div v-show="student.isExpanded" class="courses-table-container">
                <table class="courses-table">
                  <thead>
                    <tr>
                      <th>课程号</th>
                      <th>课程名称</th>
                      <th>课程类型</th>
                      <th>得分</th>
                      <th>操作</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="course in student.courses" :key="course.course_id">
                      <td>{{ course.course_id }}</td>
                      <td>{{ course.course_name }}</td>
                      <td>{{ course.course_type }}</td>
                      <td 
                        @dblclick="startEditGrade(student.student_id, course.course_id, course.grade)"
                        :class="getGradeClass(course.grade)"
                      >
                        <span v-if="!isEditing(student.student_id, course.course_id)">{{ course.grade }}</span>
                        <input 
                          v-else
                          type="number"
                          min="0"
                          max="100"
                          step="0.1"
                          v-model="editingGrade"
                          @keyup.enter="saveGrade(student.student_id, course.course_id)"
                          @blur="saveGrade(student.student_id, course.course_id)"
                          ref="gradeInput"
                          class="grade-input"
                        >
                      </td>
                      <td>
                        <!-- <button 
                          @click="deleteGrade(student.student_id, course.course_id)"
                          class="action-btn delete-btn"
                          title="删除成绩"
                        >
                          🗑️
                        </button> -->
                      </td>
                    </tr>
                    <!-- 新增成绩行 -->
                    <!-- <tr class="add-grade-row"> -->
                      <!-- <td>
                        <select v-model="newGrade.course_id" class="course-select">
                          <option value="">选择课程</option>
                          <option 
                            v-for="course in availableCourses" 
                            :key="course.course_id" 
                            :value="course.course_id"
                          >
                            {{ course.course_name }} ({{ course.course_id }})
                          </option>
                        </select>
                      </td>
                      <td colspan="2">
                        <span v-if="newGrade.course_id">
                          {{ getCourseName(newGrade.course_id) }}
                        </span>
                      </td>
                      <td>
                        <input 
                          type="number"
                          min="0"
                          max="100"
                          step="0.1"
                          v-model="newGrade.grade"
                          placeholder="输入成绩"
                          class="grade-input"
                        >
                      </td>
                      <td>
                        <button 
                          @click="addNewGrade(student.student_id)"
                          class="action-btn add-btn"
                          :disabled="!canAddGrade(student.student_id)"
                          title="添加成绩"
                        >
                          ➕
                        </button>
                      </td>
                    </tr> -->
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 隐藏授课模式数据展示 -->
    <div v-if="false && currentQueryType === 'teaching' && teachingData.length > 0 && !loading" class="query-results">
      <!-- 原有的teaching功能代码保留但隐藏 -->
    </div>
    
    <!-- 无数据提示 -->
    <div v-if="((currentQueryType === 'class' && classData.length === 0) || 
                (false && currentQueryType === 'teaching' && teachingData.length === 0)) && 
                !loading && currentQueryType && currentSemesterId" class="no-data-message">
      <div class="no-data-content">
        <span class="no-data-icon">📊</span>
        <h3>暂无查询数据</h3>
        <p>当前查询条件下没有找到相关数据</p>
      </div>
    </div>
    
    <!-- 提交按钮 -->
    <div v-if="hasChanges" class="submit-container">
      <!-- <button @click="submitChanges" class="submit-btn">
        <span class="submit-icon">💾</span>
        提交所有更改
      </button> -->
      <span class="changes-count">有 {{ changesCount }} 处更改待提交</span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, defineProps, defineEmits, nextTick } from 'vue'
import axios from 'axios'
import SemesterSelector from './SemesterSelector.vue' // 导入学期选择器组件
import apiConfig from '@/config/apiConfig';
// 定义组件属性
const props = defineProps({
  semesterId: {
    type: Number,
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
const emit = defineEmits(['update:errorMessage', 'clear-error', 'update:semesterId'])

// 响应式数据
const rawData = ref([])
const loading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const currentQueryType = ref('class') // 默认设置为class
const currentSemesterId = ref(null) // 当前选中的学期ID
const semesterList = ref([]) // 学期列表

// 编辑状态
const editingStudentId = ref(null)
const editingCourseId = ref(null)
const editingGrade = ref(0)
const gradeInput = ref(null)

// 新增成绩
const newGrade = ref({
  student_id: null,
  course_id: null,
  grade: null
})

// 更改记录
const gradeChanges = ref([])
const gradeDeletions = ref([])
const gradeAdditions = ref([])

// 计算属性 - 初始学期ID
const initialSemesterId = computed(() => {
  return props.semesterId ? props.semesterId.toString() : '1'
})

// 计算属性 - 当前学期名称
const currentSemesterName = computed(() => {
  if (!currentSemesterId.value || !semesterList.value.length) return '未知学期'
  const semester = semesterList.value.find(s => s.semester_id === currentSemesterId.value.toString())
  return semester ? semester.semester_name : '未知学期'
})

// 处理学期变化
const handleSemesterChange = (newSemesterId) => {
  console.log('学期选择器返回值:', newSemesterId)
  const semesterId = parseInt(newSemesterId)
  currentSemesterId.value = semesterId
  emit('update:semesterId', semesterId)
  
  // 如果已经有查询类型，自动重新查询
  if (currentQueryType.value) {
    console.log('自动重新查询，查询类型:', currentQueryType.value)
    handleQuery(currentQueryType.value)
  }
}

// 获取学期列表（用于显示学期名称）
const fetchSemesterList = async () => {
  try {
    const token = localStorage.getItem('jwt_token')
    // 这里使用与学生端相同的API获取学期列表
    const response = await axios.get(apiConfig.STUDENT_API.GET_SEMESTERS, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    
    if (response.data.status === 'success') {
      semesterList.value = response.data.data
      console.log('学期列表获取成功:', semesterList.value)
    }
  } catch (error) {
    console.error('获取学期列表失败:', error)
  }
}

// 计算属性 - 处理班级数据
const classData = computed(() => {
  if (currentQueryType.value !== 'class' || !rawData.value.length) return []
  
  return rawData.value.map(classItem => {
    // 计算班级平均分
    let totalGrade = 0
    let totalCourses = 0
    
    classItem.students.forEach(student => {
      // 计算每个学生的平均分
      const studentTotalGrade = student.courses.reduce((sum, course) => sum + course.grade, 0)
      student.average_grade = student.courses.length > 0 ? studentTotalGrade / student.courses.length : 0
      
      // 累加班级总分和课程数
      totalGrade += studentTotalGrade
      totalCourses += student.courses.length
    })
    
    // 计算班级平均分
    classItem.average_grade = totalCourses > 0 ? totalGrade / totalCourses : 0
    
    return classItem
  })
})

// 计算属性 - 处理授课数据（保留但可能不会使用）
const teachingData = computed(() => {
  if (currentQueryType.value !== 'teaching' || !rawData.value.length) return []
  
  return rawData.value.map(course => {
    // 计算课程平均分
    const totalGrade = course.students.reduce((sum, student) => sum + student.grade, 0)
    course.average_grade = course.students.length > 0 ? totalGrade / course.students.length : 0
    
    return course
  })
})

// 计算属性 - 可用课程列表（用于新增成绩）
const availableCourses = computed(() => {
  if (currentQueryType.value !== 'class' || !rawData.value.length) return []
  
  const courses = new Set()
  rawData.value.forEach(classItem => {
    classItem.students.forEach(student => {
      student.courses.forEach(course => {
        courses.add({
          course_id: course.course_id,
          course_name: course.course_name
        })
      })
    })
  })
  
  return Array.from(courses)
})

// 计算属性 - 可用学生列表（用于新增成绩，保留但可能不会使用）
const availableStudents = computed(() => {
  if (currentQueryType.value !== 'teaching' || !rawData.value.length) return []
  
  const students = new Set()
  rawData.value.forEach(course => {
    course.students.forEach(student => {
      students.add({
        student_id: student.student_id,
        student_name: student.student_name,
        class_name: student.class_name
      })
    })
  })
  
  return Array.from(students)
})

// 计算属性 - 是否有更改
const hasChanges = computed(() => {
  return gradeChanges.value.length > 0 || 
         gradeDeletions.value.length > 0 || 
         gradeAdditions.value.length > 0
})

// 计算属性 - 更改数量
const changesCount = computed(() => {
  return gradeChanges.value.length + 
         gradeDeletions.value.length + 
         gradeAdditions.value.length
})

// 处理查询
const handleQuery = async (queryType) => {
  if (!currentSemesterId.value) {
    errorMessage.value = '请先选择学期'
    return
  }
  
  currentQueryType.value = queryType
  loading.value = true
  errorMessage.value = ''
  successMessage.value = ''
  rawData.value = []
  resetChanges()
  
  try {
    const token = localStorage.getItem('jwt_token')
    const response = await axios.post(apiConfig.TEACHER_API.CHECK, 
      {
        message_check: queryType,
        semester_id: currentSemesterId.value
      },
      {
        headers: { 'Authorization': `Bearer ${token}` }
      }
    )
    
    if (response.data.status === 'success') {
      // 为每个班级/课程添加折叠状态
      if (queryType === 'class') {
        rawData.value = response.data.data.map(classItem => {
          return {
            ...classItem,
            isExpanded: false,
            students: classItem.students.map(student => ({
              ...student,
              isExpanded: false,
              average_grade: 0 // 初始化平均分
            }))
          }
        })
      } else {
        rawData.value = response.data.data.map(course => ({
          ...course,
          isExpanded: false
        }))
      }
      
      successMessage.value = queryType === 'class' ? '班级管理查询成功' : '授课课程查询成功'
      
      // 3秒后自动清除成功消息
      setTimeout(() => {
        successMessage.value = ''
      }, 3000)
    } else {
      // 处理其他状态
      errorMessage.value = response.data.error || '查询失败，请稍后重试'
    }
  } catch (error) {
    handleApiError(error)
  } finally {
    loading.value = false
  }
}

// 切换班级展开状态
const toggleClassExpansion = (classId) => {
  const classItem = rawData.value.find(c => c.class_id === classId)
  if (classItem) {
    classItem.isExpanded = !classItem.isExpanded
  }
}

// 切换学生展开状态
const toggleStudentExpansion = (studentId) => {
  for (const classItem of rawData.value) {
    const student = classItem.students.find(s => s.student_id === studentId)
    if (student) {
      student.isExpanded = !student.isExpanded
      break
    }
  }
}

// 开始编辑成绩
const startEditGrade = (studentId, courseId, grade) => {
  editingStudentId.value = studentId
  editingCourseId.value = courseId
  editingGrade.value = grade
  
  nextTick(() => {
    if (gradeInput.value) {
      gradeInput.value.focus()
    }
  })
}

// 检查是否正在编辑
const isEditing = (studentId, courseId) => {
  return editingStudentId.value === studentId && editingCourseId.value === courseId
}

// 保存成绩修改
const saveGrade = (studentId, courseId) => {
  if (editingGrade.value === null || isNaN(editingGrade.value)) {
    resetEditing()
    return
  }
  
  const newGradeValue = parseFloat(editingGrade.value)
  
  // 检查成绩是否在有效范围内
  if (newGradeValue < 0 || newGradeValue > 100) {
    errorMessage.value = '成绩必须在0-100之间'
    return
  }
  
  // 记录更改
  const existingChangeIndex = gradeChanges.value.findIndex(change => 
    change.student_id === studentId && change.course_id === courseId
  )
  
  if (existingChangeIndex !== -1) {
    gradeChanges.value[existingChangeIndex].grade = newGradeValue
  } else {
    gradeChanges.value.push({
      student_id: studentId,
      course_id: courseId,
      semester_id: currentSemesterId.value,
      grade: newGradeValue
    })
  }
  
  // 更新本地数据
  if (currentQueryType.value === 'class') {
    rawData.value.forEach(classItem => {
      classItem.students.forEach(student => {
        if (student.student_id === studentId) {
          student.courses.forEach(course => {
            if (course.course_id === courseId) {
              course.grade = newGradeValue
            }
          })
        }
      })
    })
  }
  
  resetEditing()
}

// 删除成绩
const deleteGrade = (studentId, courseId) => {
  if (!confirm('确定要删除这条成绩记录吗？')) return
  
  // 记录删除
  gradeDeletions.value.push({
    student_id: studentId,
    course_id: courseId,
    semester_id: currentSemesterId.value
  })
  
  // 更新本地数据
  if (currentQueryType.value === 'class') {
    rawData.value.forEach(classItem => {
      classItem.students.forEach(student => {
        if (student.student_id === studentId) {
          student.courses = student.courses.filter(course => course.course_id !== courseId)
        }
      })
    })
  }
}

// 添加新成绩
const addNewGrade = (studentId) => {
  if (!canAddGrade(studentId)) return
  
  const newRecord = {
    student_id: studentId,
    course_id: newGrade.value.course_id,
    semester_id: currentSemesterId.value,
    grade: parseFloat(newGrade.value.grade)
  }
  
  // 检查成绩是否在有效范围内
  if (newRecord.grade < 0 || newRecord.grade > 100) {
    errorMessage.value = '成绩必须在0-100之间'
    return
  }
  
  // 记录新增
  gradeAdditions.value.push(newRecord)
  
  // 更新本地数据
  if (currentQueryType.value === 'class') {
    rawData.value.forEach(classItem => {
      classItem.students.forEach(student => {
        if (student.student_id === studentId) {
          student.courses.push({
            course_id: newRecord.course_id,
            course_name: getCourseName(newRecord.course_id),
            course_type: getCourseType(newRecord.course_id),
            grade: newRecord.grade
          })
        }
      })
    })
  }
  
  // 重置新增表单
  newGrade.value = {
    student_id: null,
    course_id: null,
    grade: null
  }
}

// 检查是否可以添加成绩
const canAddGrade = (studentId) => {
  return newGrade.value.course_id && newGrade.value.grade !== null
}

// 获取课程名称
const getCourseName = (courseId) => {
  const course = availableCourses.value.find(c => c.course_id === courseId)
  return course ? course.course_name : '未知课程'
}

// 获取课程类型
const getCourseType = (courseId) => {
  // 在实际应用中，这里应该从课程数据中获取类型
  return '必修' // 简化处理
}

// 提交所有更改
const submitChanges = async () => {
  if (!hasChanges.value) return
  
  loading.value = true
  const token = localStorage.getItem('jwt_token')
  
  try {
    const response = await axios.post(apiConfig.TEACHER_API.UPDATE_GRADES, 
      {
        updates: gradeChanges.value,
        deletions: gradeDeletions.value,
        additions: gradeAdditions.value
      },
      {
        headers: { 'Authorization': `Bearer ${token}` }
      }
    )
    
    if (response.data.status === 'success') {
      successMessage.value = '成绩更新成功'
      resetChanges()
      
      // 3秒后自动清除成功消息
      setTimeout(() => {
        successMessage.value = ''
      }, 3000)
    } else {
      errorMessage.value = response.data.error || '成绩更新失败'
    }
  } catch (error) {
    handleApiError(error)
  } finally {
    loading.value = false
  }
}

// 重置编辑状态
const resetEditing = () => {
  editingStudentId.value = null
  editingCourseId.value = null
  editingGrade.value = 0
}

// 重置更改记录
const resetChanges = () => {
  gradeChanges.value = []
  gradeDeletions.value = []
  gradeAdditions.value = []
}

// 处理API错误
const handleApiError = (error) => {
  if (error.response) {
    // 服务器返回错误状态码
    const status = error.response.status
    const data = error.response.data
    
    // 根据新的错误格式处理错误信息
    if (data.status === 'failed' && data.error) {
      errorMessage.value = data.error
      return
    }
    
    switch (status) {
      case 400:
        errorMessage.value = '参数错误'
        break
      case 401:
        if (data.error && data.error.includes('过期')) {
          errorMessage.value = '登录已过期，请重新登录'
        } else if (data.error && data.error.includes('无效')) {
          errorMessage.value = '无效的登录凭证，请重新登录'
        } else if (data.error && data.error.includes('未提供')) {
          errorMessage.value = '未提供登录凭证，请重新登录'
        } else {
          errorMessage.value = '认证错误，请重新登录'
        }
        // 清除token并刷新页面
        localStorage.removeItem('jwt_token')
        setTimeout(() => {
          window.location.reload()
        }, 1500)
        break
      case 403:
        errorMessage.value = '无权限访问，仅限教师用户'
        break
      case 404:
        errorMessage.value = '未找到相关数据'
        break
      case 500:
        errorMessage.value = '服务器错误，请稍后重试'
        break
      default:
        errorMessage.value = `请求失败: ${status}`
    }
  } else if (error.request) {
    // 请求发送但无响应
    errorMessage.value = '网络连接错误，请检查网络连接'
  } else {
    // 其他错误
    errorMessage.value = '请求发送失败，请稍后重试'
  }
}

// 根据分数获取样式类名
const getGradeClass = (grade) => {
  if (grade >= 90) return 'grade-excellent'
  if (grade >= 80) return 'grade-good'
  if (grade >= 60) return 'grade-pass'
  return 'grade-fail'
}

// 获取班级状态样式
const getClassStatusClass = (averageGrade) => {
  if (averageGrade >= 90) return 'status-excellent'
  if (averageGrade >= 80) return 'status-good'
  if (averageGrade >= 60) return 'status-pass'
  return 'status-fail'
}

// 获取班级状态文本
const getClassStatusText = (averageGrade) => {
  if (averageGrade >= 90) return '优秀班级'
  if (averageGrade >= 80) return '良好班级'
  if (averageGrade >= 60) return '合格班级'
  return '需改进班级'
}

// 获取学生状态样式
const getStudentStatusClass = (averageGrade) => {
  if (averageGrade >= 90) return 'status-excellent'
  if (averageGrade >= 80) return 'status-good'
  if (averageGrade >= 60) return 'status-pass'
  return 'status-fail'
}

// 获取学生状态文本
const getStudentStatusText = (averageGrade) => {
  if (averageGrade >= 90) return '优秀'
  if (averageGrade >= 80) return '良好'
  if (averageGrade >= 60) return '及格'
  return '不及格'
}

// 清除错误信息
const clearError = () => {
  errorMessage.value = ''
  emit('clear-error')
}

// 清除成功信息
const clearSuccess = () => {
  successMessage.value = ''
}

// 组件挂载时获取学期列表
import { onMounted } from 'vue'
onMounted(() => {
  fetchSemesterList()
  // 初始化当前学期ID
  if (props.semesterId) {
    currentSemesterId.value = props.semesterId
  }
})
</script>

<style scoped>
/* 学期选择器样式 */
.semester-selector-section {
  margin-bottom: 25px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

/* 当前学期信息 */
.current-semester-info {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: rgba(255, 255, 255, 0.8);
  font-weight: 500;
  padding: 10px;
  background: rgba(100, 180, 255, 0.1);
  border-radius: 6px;
  border: 1px solid rgba(100, 180, 255, 0.2);
  margin-top: 10px;
}

.info-icon {
  font-size: 16px;
}

/* 所有原有样式保持不变 */
.teacher-query-container {
  width: 100%;
  margin-top: 0;
  position: relative;
  z-index: 1;
  min-height: 500px;
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

/* 加载状态 */
.loading-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 40px;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 5px solid rgba(255, 255, 255, 0.1);
  border-top: 5px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 15px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-container p {
  color: rgba(255, 255, 255, 0.7);
}

/* 查询控制区域 */
.query-controls {
  margin-bottom: 25px;
  padding-bottom: 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.section-title {
  color: rgba(255, 255, 255, 0.95);
  margin-bottom: 20px;
  font-size: 24px;
  text-align: left;
}

.button-group {
  display: flex;
  gap: 15px;
  justify-content: left;
  margin-bottom: 15px;
}

.query-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.9);
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.query-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.15);
  transform: translateY(-2px);
}

.query-btn.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-color: rgba(102, 126, 234, 0.5);
}

.query-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.btn-icon {
  font-size: 18px;
}

.semester-warning {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: rgba(255, 193, 7, 0.9);
  font-weight: 500;
  padding: 10px;
  background: rgba(255, 193, 7, 0.1);
  border-radius: 6px;
  border: 1px solid rgba(255, 193, 7, 0.2);
}

.warning-icon {
  font-size: 16px;
}

/* 查询结果展示 */
.query-results {
  margin-top: 25px;
}

.results-header {
  margin-bottom: 20px;
}

.results-title {
  color: rgba(255, 255, 255, 0.95);
  font-size: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.results-count {
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
  font-weight: normal;
}

/* 班级查询结果样式 */
.class-results-container {
  display: flex;
  flex-direction: column;
  gap: 25px;
}

.class-card {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  overflow: hidden;
}

.class-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  background: rgba(255, 255, 255, 0.08);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.class-header:hover {
  background: rgba(255, 255, 255, 0.12);
}

.class-info {
  flex: 1;
}

.class-name {
  color: rgba(255, 255, 255, 0.95);
  font-size: 18px;
  margin-bottom: 8px;
}

.class-details {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}

.detail-item {
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
}

.class-status-container {
  display: flex;
  align-items: center;
  gap: 10px;
}

.class-status {
  padding: 6px 12px;
  border-radius: 20px;
  font-weight: 600;
  font-size: 14px;
}

.collapse-icon {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.7);
  transition: transform 0.3s ease;
}

.status-excellent {
  background: rgba(76, 175, 80, 0.2);
  color: #4CAF50;
  border: 1px solid rgba(76, 175, 80, 0.4);
}

.status-good {
  background: rgba(139, 195, 74, 0.2);
  color: #8BC34A;
  border: 1px solid rgba(139, 195, 74, 0.4);
}

.status-pass {
  background: rgba(255, 193, 7, 0.2);
  color: #FFC107;
  border: 1px solid rgba(255, 193, 7, 0.4);
}

.status-fail {
  background: rgba(244, 67, 54, 0.2);
  color: #F44336;
  border: 1px solid rgba(244, 67, 54, 0.4);
}

.students-container {
  padding: 15px;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.student-card {
  background: rgba(255, 255, 255, 0.03);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.05);
  overflow: hidden;
}

.student-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 15px;
  background: rgba(255, 255, 255, 0.05);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.student-header:hover {
  background: rgba(255, 255, 255, 0.08);
}

.student-info {
  flex: 1;
}

.student-name {
  color: rgba(255, 255, 255, 0.9);
  font-size: 16px;
  margin-bottom: 5px;
}

.student-details {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.student-status-container {
  display: flex;
  align-items: center;
  gap: 10px;
}

.student-status {
  padding: 6px 12px;
  border-radius: 20px;
  font-weight: 600;
  font-size: 14px;
}

.courses-table-container {
  width: 100%;
  overflow-x: auto;
}

.courses-table {
  width: 100%;
  border-collapse: collapse;
}

.courses-table th {
  background: rgba(255, 255, 255, 0.08);
  color: rgba(255, 255, 255, 0.95);
  padding: 10px 12px;
  text-align: left;
  font-weight: 600;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.courses-table td {
  padding: 10px 12px;
  color: rgba(255, 255, 255, 0.8);
  border-bottom: 1px solid rgba(255, 255, 255, 0.03);
  position: relative;
}

.courses-table tr:last-child td {
  border-bottom: none;
}

.courses-table tr:hover {
  background: rgba(255, 255, 255, 0.02);
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

/* 输入框样式 */
.grade-input {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  color: white;
  padding: 5px 8px;
  width: 70px;
  font-size: 14px;
}

.grade-input:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.3);
}

/* 下拉框样式 */
.course-select {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  color: rgba(255, 255, 255, 0.8);
  padding: 5px 8px;
  width: 100%;
  font-size: 14px;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%23ffffff' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 8px center;
  background-size: 12px;
}

.course-select:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.3);
}

/* 下拉选项样式 */
.course-select option {
  background: rgba(30, 30, 46, 0.9);
  color: rgba(255, 255, 255, 0.8);
}

/* 操作按钮样式 */
.action-btn {
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.7);
  font-size: 16px;
  cursor: pointer;
  padding: 5px;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: all 0.3s ease;
}

.action-btn:hover {
  background: rgba(255, 255, 255, 0.1);
}

.add-btn:hover {
  color: #4CAF50;
}

.delete-btn:hover {
  color: #F44336;
}

/* 新增成绩行样式 */
.add-grade-row td {
  background: rgba(255, 255, 255, 0.05);
  border-top: 2px dashed rgba(255, 255, 255, 0.1);
}

/* 提交按钮区域 */
.submit-container {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-top: 30px;
  padding: 15px;
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(20px);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.15);
}

.submit-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  background: linear-gradient(135deg, #3498db, #2ecc71);
  border: none;
  border-radius: 8px;
  color: white;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.submit-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(52, 152, 219, 0.4);
}

.submit-icon {
  font-size: 18px;
}

.changes-count {
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
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
  color: rgba(255, 255, 255, 0.3);
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

/* 响应式设计 */
@media (max-width: 768px) {
  .semester-selector-section {
    padding: 15px;
    margin-bottom: 20px;
  }
  
  .button-group {
    flex-direction: column;
  }
  
  .query-btn {
    justify-content: center;
  }
  
  .class-header, .student-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .class-details, .student-details {
    flex-direction: column;
    gap: 5px;
  }
  
  .courses-table {
    font-size: 14px;
  }
  
  .courses-table th,
  .courses-table td {
    padding: 8px 10px;
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
  
  .submit-container {
    flex-direction: column;
    align-items: stretch;
  }
}

@media (max-width: 480px) {
  .query-controls, .query-results {
    padding: 15px;
  }
  
  .section-title {
    font-size: 20px;
  }
  
  .results-title {
    font-size: 18px;
  }
  
  .courses-table-container {
    font-size: 12px;
  }
  
  .courses-table th,
  .courses-table td {
    padding: 6px 8px;
  }
  
  .error-message, .success-message {
    padding: 12px 15px;
  }
  
  .error-text, .success-text {
    font-size: 13px;
  }
  
  .no-data-icon {
    font-size: 48px;
  }
  
  .no-data-message h3 {
    font-size: 20px;
  }
  
  .grade-input {
    width: 60px;
    padding: 4px 6px;
  }
  
  .action-btn {
    width: 26px;
    height: 26px;
    font-size: 14px;
  }
  
  .course-select {
    padding: 4px 6px;
    font-size: 12px;
    background-position: right 6px center;
  }
}
</style>