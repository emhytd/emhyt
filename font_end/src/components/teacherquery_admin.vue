<template>
  <div class="teacher-query-container">
    <!-- 学期选择器与查询控制区域合并 -->
    <div class="combined-controls">
      <!-- 头部区域 -->
      <div class="controls-header">
        <h2 class="section-title">
          <span class="title-icon">📚</span>
          教师教学总览
        </h2>
        <div class="header-stats">
          <div class="stat-item">
            <span class="stat-number">{{ filteredDataCount }}</span>
            <span class="stat-label">筛选结果</span>
          </div>
          <div class="stat-item">
            <span class="stat-number">{{ totalDataCount }}</span>
            <span class="stat-label">总数据量</span>
          </div>
        </div>
      </div>

      <!-- 控制区域 -->
      <div class="main-controls">
        <!-- 学期选择器 -->
        <div class="control-group semester-group">
          <label class="control-label">选择学期:</label>
          <SemesterSelector 
            ref="semesterSelector"
            @semester-change="handleSemesterChange"
            class="custom-semester-selector"
          />
        </div>

        <!-- 查询按钮 -->
        <div class="control-group query-group">
          <button 
            @click="handleQuery" 
            class="query-action-btn"
            :disabled="loading || !currentSemesterId"
          >
            <span class="btn-icon">🔍</span>
            {{ loading ? '查询中...' : '查询数据' }}
          </button>
        </div>
      </div>

      <!-- 筛选控制区域 -->
      <div v-if="currentSemesterId && teachingData.length > 0" class="filter-controls">
        <div class="filter-group">
          <!-- 搜索框 -->
          <div class="filter-item">
            <label class="filter-label">搜索:</label>
            <input 
              type="text" 
              v-model="filters.search" 
              placeholder="搜索教师、课程、学生姓名或学号..."
              class="filter-input"
            >
          </div>
          
          <!-- 教师筛选 -->
          <div class="filter-item">
            <label class="filter-label">教师:</label>
            <select v-model="filters.selectedTeacher" class="filter-select">
              <option value="">全部教师</option>
              <option 
                v-for="teacher in availableTeachers" 
                :key="teacher.teacher_id" 
                :value="teacher.teacher_id"
              >
                {{ teacher.teacher_name }}
              </option>
            </select>
          </div>
          
          <!-- 成绩筛选 -->
          <div class="filter-item">
            <label class="filter-label">成绩范围:</label>
            <select v-model="filters.gradeRange" class="filter-select">
              <option value="">全部成绩</option>
              <option value="excellent">优秀 (90-100)</option>
              <option value="good">良好 (80-89)</option>
              <option value="pass">及格 (60-79)</option>
              <option value="fail">不及格 (0-59)</option>
            </select>
          </div>
          
          <!-- 重置筛选按钮 -->
          <button @click="resetFilters" class="filter-reset-btn">
            重置筛选
          </button>
        </div>
      </div>
    </div>

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
      <p>正在查询教师数据...</p>
    </div>
    
    <!-- 授课模式数据展示 -->
    <div v-if="filteredTeachingData.length > 0 && !loading" class="query-results">
      <div class="results-header">
        <h3 class="results-title">
          教师教学总览
          <span class="results-count">(共 {{ filteredTeachingData.length }} 位教师)</span>
        </h3>
        <div class="view-controls">
          <span class="view-label">展开状态:</span>
          <div class="view-toggle">
            <button 
              :class="['view-option', { active: expandState === 'all' }]"
              @click="expandAll"
            >
              全部展开
            </button>
            <button 
              :class="['view-option', { active: expandState === 'none' }]"
              @click="collapseAll"
            >
              全部收起
            </button>
          </div>
        </div>
      </div>
      
      <div class="teaching-results-container">
        <div v-for="teacher in filteredTeachingData" :key="teacher.teacher_id" class="teacher-card">
          <div class="teacher-header" @click="toggleTeacherExpansion(teacher.teacher_id)">
            <div class="teacher-info">
              <h4 class="teacher-name">{{ teacher.teacher_name }}</h4>
              <div class="teacher-details">
                <span class="detail-item">教师ID: {{ teacher.teacher_id }}</span>
                <span class="detail-item">教授课程数: {{ teacher.courses.length }}</span>
                <span class="detail-item">学生总数: {{ getTotalStudents(teacher) }}</span>
                <span class="detail-item">教学平均分: {{ getTeacherAverageGrade(teacher).toFixed(1) }}</span>
              </div>
            </div>
            <div class="teacher-status-container">
              <!-- 添加学生按钮 -->
              <button 
                @click.stop="openAddStudentDialog(teacher)"
                class="action-icon-btn add-btn"
                title="添加学生成绩"
              >
                ➕
              </button>
              
              <div class="teacher-status" :class="getTeacherStatusClass(getTeacherAverageGrade(teacher))">
                {{ getTeacherStatusText(getTeacherAverageGrade(teacher)) }}
              </div>
              <div class="collapse-icon">
                {{ teacher.isExpanded ? '▼' : '►' }}
              </div>
            </div>
          </div>
          
          <div v-show="teacher.isExpanded" class="courses-container">
            <div v-for="course in teacher.courses" :key="course.course_id" class="course-card">
              <div class="course-header" @click="toggleCourseExpansion(course.course_id)">
                <div class="course-info">
                  <h5 class="course-name">{{ course.course_name }}</h5>
                  <div class="course-details">
                    <span class="detail-item">课程ID: {{ course.course_id }}</span>
                    <span class="detail-item">课程类型: {{ course.course_type }}</span>
                    <span class="detail-item">学生数: {{ course.students.length }}</span>
                    <span class="detail-item">课程平均分: {{ course.average_grade.toFixed(1) }}</span>
                  </div>
                </div>
                <div class="course-status-container">
                  <div class="course-status" :class="getCourseStatusClass(course.average_grade)">
                    {{ getCourseStatusText(course.average_grade) }}
                  </div>
                  <div class="collapse-icon">
                    {{ course.isExpanded ? '▼' : '►' }}
                  </div>
                </div>
              </div>
              
              <div v-show="course.isExpanded" class="students-table-container">
                <table class="students-table">
                  <thead>
                    <tr>
                      <th>学号</th>
                      <th>姓名</th>
                      <th>班级</th>
                      <th>成绩</th>
                      <th>操作</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="student in course.students" :key="student.student_id">
                      <td>{{ student.student_id }}</td>
                      <td>{{ student.student_name }}</td>
                      <td>
                        <span v-if="student.class_name && student.class_name !== '未知班级'">
                          {{ student.class_name }}
                        </span>
                        <span v-else class="no-class-info">
                          <span class="warning-icon">⚠️</span>
                          班级信息缺失
                        </span>
                      </td>
                      <td :class="getGradeClass(student.grade)">
                        <!-- 成绩编辑功能 -->
                        <div class="grade-container">
                          <span class="grade-value">{{ student.grade }}</span>
                          <button 
                            @click.stop="editGrade(student, course, teacher)"
                            class="grade-edit-btn"
                            title="编辑成绩"
                          >
                            ✏️
                          </button>
                        </div>
                      </td>
                      <td>
                        <button 
                          @click.stop="removeStudentCourse(student, course, teacher)"
                          class="action-icon-btn delete-btn"
                          title="删除课程"
                        >
                          🗑️
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 无数据提示 -->
    <div v-if="filteredTeachingData.length === 0 && !loading && currentSemesterId && hasQueried" class="no-data-container">
      <div class="no-data-content">
        <div class="no-data-icon">📊</div>
        <h3>暂无教师数据</h3>
        <p>当前查询条件下没有找到相关教师数据，请尝试调整筛选条件</p>
        <div class="no-data-actions">
          <button 
            @click="resetFilters"
            class="no-data-action-btn"
          >
            <span class="btn-icon">🔄</span>
            重置筛选条件
          </button>
          <button 
            @click="handleQuery"
            class="no-data-action-btn"
          >
            <span class="btn-icon">🔍</span>
            重新查询
          </button>
        </div>
      </div>
    </div>

    <!-- 初始状态提示 -->
    <div v-if="!hasQueried && !loading && currentSemesterId" class="initial-state-container">
      <div class="initial-state-content">
        <div class="initial-state-icon">📚</div>
        <h3>教师教学查询</h3>
        <p>点击查询按钮获取教师教学数据</p>
        <button 
          @click="handleQuery"
          class="initial-state-btn"
          :disabled="loading"
        >
          <span class="btn-icon">🔍</span>
          开始查询
        </button>
      </div>
    </div>

    <!-- 添加学生成绩弹窗 -->
    <div v-if="showAddStudentDialog" class="modal-overlay" @click.self="closeAddStudentDialog">
      <div class="modal-content">
        <div class="modal-header">
          <h3>为 {{ selectedTeacher?.teacher_name }} 添加学生成绩</h3>
          <button class="close-btn" @click="closeAddStudentDialog">×</button>
        </div>
        
        <div class="modal-body">
          <form @submit.prevent="submitAddStudent">
            <div class="form-group">
              <label>选择课程 *</label>
              <select v-model="newStudent.course_id" required class="form-select">
                <option value="">请选择课程</option>
                <option 
                  v-for="course in selectedTeacher?.courses || []" 
                  :key="course.course_id" 
                  :value="course.course_id"
                >
                  {{ course.course_name }} ({{ course.course_type }})
                </option>
              </select>
            </div>
            
            <div class="form-group">
              <div class="student-search-section">
                <label>选择学生 *</label>
                <div class="search-controls">
                  <div class="search-input-group">
                    <input 
                      v-model="studentSearch" 
                      type="text" 
                      placeholder="搜索学号..."
                      class="filter-input"
                      @input="handleStudentSearch"
                    >
                    <button 
                      v-if="studentSearch" 
                      type="button" 
                      class="clear-search-btn"
                      @click="clearStudentSearch"
                    >
                      ×
                    </button>
                  </div>
                  <div class="search-stats">
                    <span class="search-count">找到 {{ filteredStudents.length }} 个学生</span>
                  </div>
                </div>
              </div>
              <div class="student-select-container">
                <select 
                  v-model="newStudent.student_id" 
                  required 
                  class="form-select student-select"
                  size="8"
                >
                  <option value="">请选择学生</option>
                  <option 
                    v-for="student in filteredStudents" 
                    :key="student.student_id" 
                    :value="student.student_id"
                    class="student-option"
                  >
                    {{ student.student_id }} - {{ student.student_name }}
                    <span v-if="student.class_name" class="student-class">
                      ({{ student.class_name }})
                    </span>
                  </option>
                </select>
              </div>
              <div v-if="filteredStudents.length === 0 && studentSearch" class="no-search-results">
                <span class="warning-icon">⚠️</span>
                未找到学号包含 "{{ studentSearch }}" 的学生
              </div>
            </div>

            <div class="form-group">
              <label>得分 *</label>
              <input 
                v-model="newStudent.grade" 
                type="number" 
                min="0" 
                max="100" 
                step="0.1"
                required 
                placeholder="请输入得分 (0-100)"
                class="form-input"
              >
            </div>

            <div class="form-actions">
              <button type="button" class="cancel-btn" @click="closeAddStudentDialog">取消</button>
              <button type="submit" class="submit-btn" :disabled="addStudentLoading">
                {{ addStudentLoading ? '添加中...' : '添加成绩' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, nextTick } from 'vue'
import axios from 'axios'
import apiConfig from '@/config/apiConfig'
import SemesterSelector from '@/components/SemesterSelector.vue'

// 响应式数据
const currentSemesterId = ref(null)
const rawData = ref([])
const loading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const expandState = ref('none')
const hasQueried = ref(false)

// 弹窗控制
const showAddStudentDialog = ref(false)
const addStudentLoading = ref(false)
const selectedTeacher = ref(null)

// 新增数据
const newStudent = ref({
  student_id: '',
  course_id: '',
  grade: 0
})

// 可用学生列表
const availableStudents = ref([])

// 学生搜索
const studentSearch = ref('')

// 学期选择器引用
const semesterSelector = ref(null)

// 筛选条件
const filters = ref({
  search: '',
  selectedTeacher: '',
  gradeRange: ''
})

// 计算属性 - 筛选后的学生列表
const filteredStudents = computed(() => {
  if (!availableStudents.value.length) return []
  
  let filtered = availableStudents.value
  
  // 根据搜索词筛选学生
  if (studentSearch.value.trim()) {
    const searchTerm = studentSearch.value.trim().toLowerCase()
    filtered = filtered.filter(student => 
      student.student_id.toString().includes(searchTerm) ||
      student.student_name.toLowerCase().includes(searchTerm)
    )
  }
  
  // 按学号排序
  return filtered.sort((a, b) => a.student_id - b.student_id)
})

// 获取所有学生
const fetchAllStudents = async () => {
  try {
    const token = localStorage.getItem('jwt_token')
    console.log('开始获取所有学生信息...')
    
    const response = await axios.get(`${apiConfig.BASE_URL}/admin/student_info`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    
    console.log('获取所有学生响应:', response.data)
    
    if (response.data.status === 'success') {
      // 从返回数据中提取所有学生
      const allStudents = response.data.data.flatMap(classData => 
        classData.students || []
      )
      availableStudents.value = allStudents
      console.log('所有学生列表:', availableStudents.value)
    } else {
      errorMessage.value = response.data.error || '获取学生信息失败'
      availableStudents.value = []
    }
  } catch (error) {
    console.error('获取所有学生失败:', error)
    if (error.response) {
      console.error('错误详情:', error.response.data)
    }
    errorMessage.value = '获取学生信息失败，请检查网络连接'
    availableStudents.value = []
  }
}

// 处理学生搜索
const handleStudentSearch = () => {
  // 搜索逻辑已经在计算属性中处理，这里可以添加其他逻辑
  console.log('搜索学生:', studentSearch.value)
}

// 清除搜索
const clearStudentSearch = () => {
  studentSearch.value = ''
}

// 打开添加学生成绩弹窗
const openAddStudentDialog = async (teacher) => {
  selectedTeacher.value = teacher
  console.log('打开弹窗，教师:', teacher)
  
  await fetchAllStudents()
  
  // 重置搜索条件
  studentSearch.value = ''
  
  console.log('可用学生:', availableStudents.value)
  
  newStudent.value = {
    student_id: '',
    course_id: '',
    grade: 0,
    semester_id: currentSemesterId.value
  }
  showAddStudentDialog.value = true
}

// 关闭添加学生成绩弹窗
const closeAddStudentDialog = () => {
  showAddStudentDialog.value = false
  selectedTeacher.value = null
  availableStudents.value = []
  studentSearch.value = ''
}

// 提交添加学生成绩 - 使用批量导入接口，支持添加新记录
const submitAddStudent = async () => {
  console.log('提交学生成绩数据:', newStudent.value)
  
  if (!newStudent.value.student_id || !newStudent.value.course_id) {
    errorMessage.value = '请选择学生和课程'
    return
  }

  addStudentLoading.value = true

  try {
    const token = localStorage.getItem('jwt_token')
    
    // 获取学期名称
    const semesterResponse = await axios.get(`${apiConfig.BASE_URL}/semesters`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    
    let semesterName = ''
    if (semesterResponse.data.status === 'success') {
      const currentSemester = semesterResponse.data.data.find(s => s.semester_id === currentSemesterId.value)
      semesterName = currentSemester ? currentSemester.semester_name : `学期${currentSemesterId.value}`
    } else {
      semesterName = `学期${currentSemesterId.value}`
    }
    
    // 使用批量导入接口，支持添加新记录
    const response = await axios.post(`${apiConfig.BASE_URL}/bulkimport`, 
      [{
        student_id: parseInt(newStudent.value.student_id),
        course_id: parseInt(newStudent.value.course_id),
        score: parseFloat(newStudent.value.grade),
        semester_name: semesterName
      }],
      {
        headers: { 'Authorization': `Bearer ${token}` }
      }
    )

    console.log('批量导入响应:', response.data)
    
    if (response.data.status === 'success') {
      successMessage.value = '学生成绩添加成功'
      closeAddStudentDialog()
      await handleQuery() // 刷新数据
    } else {
      errorMessage.value = response.data.error || '添加失败'
    }
  } catch (error) {
    console.error('添加学生成绩失败:', error)
    if (error.response) {
      console.error('错误响应:', error.response.data)
      errorMessage.value = error.response.data.error || '添加学生成绩失败'
    } else {
      errorMessage.value = '网络错误，请检查连接'
    }
  } finally {
    addStudentLoading.value = false
  }
}

// 学期变化处理
const handleSemesterChange = async (semesterId) => {
  currentSemesterId.value = semesterId
  console.log('当前选中的学期ID:', semesterId)
  
  // 重置数据
  rawData.value = []
  resetFilters()
  hasQueried.value = false
  
  // 如果有学期ID，自动查询
  if (semesterId) {
    // 短暂延迟确保DOM更新完成
    await nextTick()
    await handleQuery()
  }
}

// 计算属性 - 处理教师数据
const teachingData = computed(() => {
  if (!rawData.value.length) return []
  
  return rawData.value.map(teacher => {
    // 计算每位教师的课程平均分
    teacher.courses.forEach(course => {
      // 计算每门课程的平均分
      const courseTotalGrade = course.students.reduce((sum, student) => sum + student.grade, 0)
      course.average_grade = course.students.length > 0 ? courseTotalGrade / course.students.length : 0
      
      // 确保每个学生都有班级信息
      course.students.forEach(student => {
        if (!student.class_name || student.class_name.trim() === '') {
          student.class_name = '未知班级'
        }
      })
    })
    
    return teacher
  })
})

// 筛选后的教师数据
const filteredTeachingData = computed(() => {
  if (!teachingData.value.length) return []
  
  return teachingData.value
    .filter(teacher => {
      // 教师筛选
      if (filters.value.selectedTeacher && teacher.teacher_id !== filters.value.selectedTeacher) {
        return false
      }
      
      // 搜索筛选
      if (filters.value.search) {
        const searchLower = filters.value.search.toLowerCase()
        const teacherNameMatch = teacher.teacher_name?.toLowerCase().includes(searchLower)
        const courseMatch = teacher.courses.some(course => 
          course.course_name?.toLowerCase().includes(searchLower) ||
          course.course_id?.toString().includes(searchLower)
        )
        const studentMatch = teacher.courses.some(course => 
          course.students.some(student => 
            student.student_name?.toLowerCase().includes(searchLower) ||
            student.student_id?.toString().includes(searchLower)
          )
        )
        
        if (!teacherNameMatch && !courseMatch && !studentMatch) return false
      }
      
      return true
    })
    .map(teacher => {
      // 筛选课程
      const filteredCourses = teacher.courses.filter(course => {
        // 搜索筛选
        if (filters.value.search) {
          const searchLower = filters.value.search.toLowerCase()
          const courseNameMatch = course.course_name?.toLowerCase().includes(searchLower)
          const courseIdMatch = course.course_id?.toString().includes(searchLower)
          const studentMatch = course.students.some(student => 
            student.student_name?.toLowerCase().includes(searchLower) ||
            student.student_id?.toString().includes(searchLower)
          )
          
          if (!courseNameMatch && !courseIdMatch && !studentMatch) return false
        }
        
        // 成绩筛选
        if (filters.value.gradeRange) {
          const avgGrade = course.average_grade
          switch (filters.value.gradeRange) {
            case 'excellent':
              if (avgGrade < 90) return false
              break
            case 'good':
              if (avgGrade < 80 || avgGrade >= 90) return false
              break
            case 'pass':
              if (avgGrade < 60 || avgGrade >= 80) return false
              break
            case 'fail':
              if (avgGrade >= 60) return false
              break
          }
        }
        
        return true
      })
      
      return {
        ...teacher,
        courses: filteredCourses
      }
    })
    .filter(teacher => teacher.courses.length > 0) // 移除没有课程的教师
})

// 可用教师列表（用于筛选）
const availableTeachers = computed(() => {
  if (!teachingData.value.length) return []
  
  return teachingData.value.map(teacher => ({
    teacher_id: teacher.teacher_id,
    teacher_name: teacher.teacher_name
  }))
})

// 筛选后的数据总数
const filteredDataCount = computed(() => {
  return filteredTeachingData.value.reduce((total, teacher) => 
    total + teacher.courses.reduce((courseTotal, course) => courseTotal + course.students.length, 0), 0)
})

// 总数据量
const totalDataCount = computed(() => {
  return teachingData.value.reduce((total, teacher) => 
    total + teacher.courses.reduce((courseTotal, course) => courseTotal + course.students.length, 0), 0)
})

// 处理查询 - 使用POST方法
const handleQuery = async () => {
  if (!currentSemesterId.value) {
    errorMessage.value = '请先选择学期'
    return
  }
  
  loading.value = true
  errorMessage.value = ''
  successMessage.value = ''
  hasQueried.value = true
  
  try {
    const token = localStorage.getItem('jwt_token')
    console.log('开始查询，学期ID:', currentSemesterId.value)
    console.log('JWT Token:', token ? '存在' : '不存在')
    
    // 使用POST方法，符合后端API定义
    const response = await axios.post(`${apiConfig.BASE_URL}/admin_check`, 
      {
        message_check: 'teaching',
        semester_id: currentSemesterId.value
      },
      {
        headers: { 'Authorization': `Bearer ${token}` }
      }
    )
    
    console.log('API响应:', response.data)
    
    if (response.data.status === 'success') {
      console.log('返回的教师数据:', response.data.data)
      
      // 增强数据格式处理
      const processedData = processTeacherData(response.data.data)
      rawData.value = processedData.map(teacher => ({
        ...teacher,
        isExpanded: false,
        courses: (teacher.courses || []).map(course => ({
          ...course,
          isExpanded: false
        }))
      }))
      
      successMessage.value = '教师教学查询成功'
      
      setTimeout(() => {
        successMessage.value = ''
      }, 3000)
    } else {
      errorMessage.value = response.data.error || '查询失败，请稍后重试'
    }
  } catch (error) {
    console.error('查询错误详情:', error)
    if (error.response) {
      console.error('错误响应:', error.response.data)
      console.error('错误状态:', error.response.status)
    }
    handleApiError(error)
  } finally {
    loading.value = false
  }
}

// 数据处理函数
const processTeacherData = (data) => {
  if (!data || !Array.isArray(data)) return []
  
  return data.map(teacher => {
    // 确保教师数据完整性
    const processedTeacher = {
      teacher_id: teacher.teacher_id || 0,
      teacher_name: teacher.teacher_name || '未知教师',
      courses: []
    }
    
    // 处理课程数据
    if (Array.isArray(teacher.courses)) {
      processedTeacher.courses = teacher.courses.map(course => ({
        course_id: course.course_id || 0,
        course_name: course.course_name || '未知课程',
        course_type: course.course_type || '未知类型',
        students: course.students || [],
        average_grade: course.average_grade || 0
      }))
    }
    
    return processedTeacher
  })
}

// 重置筛选条件
const resetFilters = () => {
  filters.value = {
    search: '',
    selectedTeacher: '',
    gradeRange: ''
  }
}

// 展开所有
const expandAll = () => {
  expandState.value = 'all'
  filteredTeachingData.value.forEach(teacher => {
    teacher.isExpanded = true
    teacher.courses.forEach(course => {
      course.isExpanded = true
    })
  })
}

// 收起所有
const collapseAll = () => {
  expandState.value = 'none'
  filteredTeachingData.value.forEach(teacher => {
    teacher.isExpanded = false
    teacher.courses.forEach(course => {
      course.isExpanded = false
    })
  })
}

// 切换教师展开状态
const toggleTeacherExpansion = (teacherId) => {
  const teacher = rawData.value.find(t => t.teacher_id === teacherId)
  if (teacher) {
    teacher.isExpanded = !teacher.isExpanded
  }
}

// 切换课程展开状态
const toggleCourseExpansion = (courseId) => {
  for (const teacher of rawData.value) {
    const course = teacher.courses.find(c => c.course_id === courseId)
    if (course) {
      course.isExpanded = !course.isExpanded
      break
    }
  }
}

// 获取教师的学生总数
const getTotalStudents = (teacher) => {
  return teacher.courses.reduce((total, course) => total + course.students.length, 0)
}

// 获取教师平均分
const getTeacherAverageGrade = (teacher) => {
  let totalGrade = 0
  let totalStudents = 0
  
  teacher.courses.forEach(course => {
    totalGrade += course.average_grade * course.students.length
    totalStudents += course.students.length
  })
  
  return totalStudents > 0 ? totalGrade / totalStudents : 0
}

// 处理API错误
const handleApiError = (error) => {
  if (error.response) {
    const status = error.response.status
    const data = error.response.data
    
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
        localStorage.removeItem('jwt_token')
        setTimeout(() => {
          window.location.reload()
        }, 1500)
        break
      case 403:
        errorMessage.value = '无权限访问，仅限管理员用户'
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
    errorMessage.value = '网络连接错误，请检查网络连接'
  } else {
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

// 获取教师状态样式
const getTeacherStatusClass = (averageGrade) => {
  if (averageGrade >= 90) return 'status-excellent'
  if (averageGrade >= 80) return 'status-good'
  if (averageGrade >= 60) return 'status-pass'
  return 'status-fail'
}

// 获取教师状态文本
const getTeacherStatusText = (averageGrade) => {
  if (averageGrade >= 90) return '教学优秀'
  if (averageGrade >= 80) return '教学良好'
  if (averageGrade >= 60) return '教学合格'
  return '需要改进'
}

// 获取课程状态样式
const getCourseStatusClass = (averageGrade) => {
  if (averageGrade >= 90) return 'status-excellent'
  if (averageGrade >= 80) return 'status-good'
  if (averageGrade >= 60) return 'status-pass'
  return 'status-fail'
}

// 获取课程状态文本
const getCourseStatusText = (averageGrade) => {
  if (averageGrade >= 90) return '教学优秀'
  if (averageGrade >= 80) return '教学良好'
  if (averageGrade >= 60) return '教学合格'
  return '需要改进'
}

// 清除错误信息
const clearError = () => {
  errorMessage.value = ''
}

// 清除成功信息
const clearSuccess = () => {
  successMessage.value = ''
}

// 编辑成绩
const editGrade = (student, course, teacher) => {
  const newGrade = prompt(`请输入 ${student.student_name} 的 ${course.course_name} 新成绩:`, student.grade)
  
  if (newGrade !== null && newGrade !== '') {
    const grade = parseFloat(newGrade)
    if (!isNaN(grade) && grade >= 0 && grade <= 100) {
      updateGrade(student.student_id, course.course_id, grade)
    } else {
      errorMessage.value = '请输入有效的成绩（0-100）'
    }
  }
}

// 更新成绩 - 使用PUT方法，但如果记录不存在则创建
const updateGrade = async (studentId, courseId, grade) => {
  try {
    const token = localStorage.getItem('jwt_token')
    
    // 首先尝试更新现有记录
    const response = await axios.put(`${apiConfig.BASE_URL}/admin/course_selection_info`, {
      student_id: studentId,
      course_id: courseId,
      semester_id: currentSemesterId.value,
      grade: grade
    }, {
      headers: { 'Authorization': `Bearer ${token}` }
    })

    console.log('更新成绩响应:', response.data)

    if (response.data.status === 'success') {
      successMessage.value = '成绩更新成功'
      await handleQuery()
    } else {
      errorMessage.value = response.data.error || '成绩更新失败'
    }
  } catch (error) {
    // 如果更新失败（可能是记录不存在），则尝试添加新记录
    if (error.response && error.response.status === 404) {
      console.log('选课记录不存在，尝试添加新记录...')
      await addCourseSelection(studentId, courseId, grade)
    } else {
      console.error('更新成绩失败:', error)
      if (error.response) {
        console.error('错误详情:', error.response.data)
        errorMessage.value = error.response.data.error || '成绩更新失败'
      }
      handleApiError(error)
    }
  }
}

// 添加选课记录
const addCourseSelection = async (studentId, courseId, grade) => {
  try {
    const token = localStorage.getItem('jwt_token')
    
    // 获取学期名称
    const semesterResponse = await axios.get(`${apiConfig.BASE_URL}/semesters`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    
    let semesterName = ''
    if (semesterResponse.data.status === 'success') {
      const currentSemester = semesterResponse.data.data.find(s => s.semester_id === currentSemesterId.value)
      semesterName = currentSemester ? currentSemester.semester_name : `学期${currentSemesterId.value}`
    } else {
      semesterName = `学期${currentSemesterId.value}`
    }
    
    // 使用批量导入接口添加新记录
    const response = await axios.post(`${apiConfig.BASE_URL}/bulkimport`, 
      [{
        student_id: studentId,
        course_id: courseId,
        score: grade,
        semester_name: semesterName
      }],
      {
        headers: { 'Authorization': `Bearer ${token}` }
      }
    )

    console.log('添加选课记录响应:', response.data)

    if (response.data.status === 'success') {
      successMessage.value = '成绩添加成功'
      await handleQuery()
    } else {
      errorMessage.value = response.data.error || '成绩添加失败'
    }
  } catch (error) {
    console.error('添加选课记录失败:', error)
    if (error.response) {
      console.error('错误详情:', error.response.data)
      errorMessage.value = error.response.data.error || '成绩添加失败'
    }
    handleApiError(error)
  }
}

// 删除学生课程
const removeStudentCourse = async (student, course, teacher) => {
  if (!confirm(`确定要删除 ${student.student_name} 的 ${course.course_name} 课程吗？`)) {
    return
  }

  try {
    const token = localStorage.getItem('jwt_token')
    // 使用DELETE方法删除课程成绩
    const response = await axios.delete(`${apiConfig.BASE_URL}/admin/course_selection_info`, {
      headers: { 'Authorization': `Bearer ${token}` },
      data: {
        student_id: student.student_id,
        course_id: course.course_id,
        semester_id: currentSemesterId.value
      }
    })

    console.log('删除课程响应:', response.data)

    if (response.data.status === 'success') {
      successMessage.value = '课程删除成功'
      await handleQuery()
    } else {
      errorMessage.value = response.data.error || '删除失败'
    }
  } catch (error) {
    console.error('删除课程失败:', error)
    if (error.response) {
      console.error('错误详情:', error.response.data)
      errorMessage.value = error.response.data.error || '删除失败'
    }
    handleApiError(error)
  }
}

// 组件挂载时初始化
onMounted(async () => {
  // 等待学期选择器初始化完成
  await nextTick()
  
  // 如果学期选择器已经有选中的学期，自动触发查询
  if (semesterSelector.value && currentSemesterId.value) {
    console.log('组件挂载，自动查询默认学期数据')
    await handleQuery()
  }
})
</script>

<style scoped>
/* 添加操作按钮样式 */
.teacher-status-container {
  display: flex;
  align-items: center;
  gap: 12px;
}

.action-icon-btn {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 6px;
  color: rgba(255, 255, 255, 0.8);
  padding: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  font-size: 14px;
}

.action-icon-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: scale(1.1);
}

.add-btn:hover {
  background: rgba(76, 175, 80, 0.2);
  border-color: rgba(76, 175, 80, 0.4);
}

.delete-btn:hover {
  background: rgba(244, 67, 54, 0.2);
  border-color: rgba(244, 67, 54, 0.4);
}

/* 成绩编辑样式 */
.grade-container {
  display: flex;
  align-items: center;
  gap: 8px;
}

.grade-value {
  flex: 1;
}

.grade-edit-btn {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  color: rgba(255, 255, 255, 0.7);
  padding: 4px 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 12px;
  opacity: 0;
}

.grade-edit-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  color: rgba(255, 255, 255, 0.9);
}

.students-table tr:hover .grade-edit-btn {
  opacity: 1;
}

/* 弹窗样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  backdrop-filter: blur(5px);
}

.modal-content {
  background: rgba(30, 30, 46, 0.95);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(20px);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.modal-header h3 {
  color: rgba(255, 255, 255, 0.95);
  font-size: 20px;
  font-weight: 600;
  margin: 0;
}

.close-btn {
  background: rgba(255, 255, 255, 0.1);
  border: none;
  color: rgba(255, 255, 255, 0.7);
  font-size: 24px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 8px;
  transition: all 0.3s ease;
  line-height: 1;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  color: rgba(255, 255, 255, 0.9);
}

.modal-body {
  padding: 24px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  color: rgba(255, 255, 255, 0.9);
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 8px;
}

.form-input, .form-select {
  width: 100%;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.9);
  padding: 12px 16px;
  font-size: 14px;
  transition: all 0.3s ease;
  box-sizing: border-box;
}

.form-input:focus, .form-select:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.3);
  background: rgba(255, 255, 255, 0.15);
}

.form-input::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.form-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 24px;
}

.cancel-btn, .submit-btn {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 100px;
}

.cancel-btn {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: rgba(255, 255, 255, 0.9);
}

.cancel-btn:hover {
  background: rgba(255, 255, 255, 0.15);
}

.submit-btn {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}



/* 样式与ClassQueryComponent保持一致 */
.teacher-query-container {
  width: 100%;
  margin-top: 0;
  position: relative;
  z-index: 1;
  min-height: 500px;
}

/* 合并的控制区域样式 */
.combined-controls {
  margin-bottom: 25px;
  padding: 25px;
  background: rgba(30, 30, 46, 0.8);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.3);
  border: 1px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
}

/* 头部区域样式 */
.controls-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
  flex-wrap: wrap;
  gap: 15px;
}

.section-title {
  color: rgba(255, 255, 255, 0.95);
  font-size: 24px;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 0;
}

.title-icon {
  font-size: 28px;
}

.header-stats {
  display: flex;
  gap: 15px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 12px 20px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  min-width: 100px;
}

.stat-number {
  color: #667eea;
  font-size: 24px;
  font-weight: 800;
  line-height: 1;
}

.stat-label {
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
  margin-top: 4px;
  font-weight: 500;
}

/* 主控制区域 */
.main-controls {
  display: flex;
  align-items: flex-end;
  gap: 20px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.control-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.control-label {
  color: rgba(255, 255, 255, 0.9);
  font-size: 14px;
  font-weight: 600;
  white-space: nowrap;
}

.semester-group {
  flex: 1;
  min-width: 300px;
}

.query-group {
  flex-shrink: 0;
}

/* 自定义学期选择器样式 */
.custom-semester-selector {
  width: 100%;
}

.custom-semester-selector :deep(.semester-btn) {
  padding: 12px 20px;
  border: 1px solid rgba(255, 255, 255, 0.25);
  border-radius: 10px;
  font-size: 15px;
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.9);
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(8px);
  font-weight: 600;
  white-space: nowrap;
  flex-shrink: 0;
}

.custom-semester-selector :deep(.semester-btn:hover) {
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.4);
  transform: translateY(-2px);
}

.custom-semester-selector :deep(.semester-btn.active) {
  background: linear-gradient(135deg, #667eea, #764ba2);
  border-color: rgba(102, 126, 234, 0.6);
  color: #fff;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

.custom-semester-selector :deep(.more-btn) {
  padding: 12px 20px;
  border: 1px solid rgba(255, 255, 255, 0.25);
  border-radius: 10px;
  font-size: 15px;
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.9);
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(8px);
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 6px;
  white-space: nowrap;
}

.custom-semester-selector :deep(.more-btn:hover) {
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.4);
}

.custom-semester-selector :deep(.more-btn.expanded) {
  background: rgba(255, 255, 255, 0.2);
}

.custom-semester-selector :deep(.expand-panel) {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: rgba(30, 30, 46, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  margin-top: 10px;
  padding: 12px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  backdrop-filter: blur(20px);
  z-index: 1000;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
}

.custom-semester-selector :deep(.expand-btn) {
  padding: 10px 16px;
  font-size: 14px;
}

/* 查询按钮样式 */
.query-action-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 24px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border: none;
  border-radius: 10px;
  color: white;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
  white-space: nowrap;
  height: fit-content;
}

.query-action-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
}

.query-action-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

/* 筛选控制区域 */
.filter-controls {
  margin-top: 20px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(20px);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.15);
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
  font-weight: 600;
}

.filter-select {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.9);
  padding: 10px 12px;
  font-size: 14px;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%23ffffff' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 12px center;
  background-size: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 500;
}

.filter-select:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.3);
  background-color: rgba(255, 255, 255, 0.15);
}

.filter-input {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.9);
  padding: 10px 12px;
  font-size: 14px;
  transition: all 0.3s ease;
  font-weight: 500;
}

.filter-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.3);
  background-color: rgba(255, 255, 255, 0.15);
}

.filter-input::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.filter-reset-btn {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.9);
  padding: 10px 16px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  align-self: flex-end;
  height: fit-content;
  min-width: 100px;
}

.filter-reset-btn:hover {
  background: rgba(255, 255, 255, 0.15);
  transform: translateY(-1px);
}

/* 错误信息样式 */
.error-message {
  background: linear-gradient(135deg, rgba(244, 67, 54, 0.15), rgba(244, 67, 54, 0.25));
  backdrop-filter: blur(20px);
  border: 1px solid rgba(244, 67, 54, 0.4);
  border-radius: 12px;
  padding: 16px 20px;
  margin-bottom: 20px;
  animation: slideDown 0.3s ease-out;
  box-shadow: 0 4px 20px rgba(244, 67, 54, 0.15);
}

.error-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.error-icon {
  font-size: 20px;
  margin-right: 12px;
  flex-shrink: 0;
}

.error-text {
  flex: 1;
  color: rgba(255, 255, 255, 0.95);
  font-weight: 600;
  font-size: 14px;
  line-height: 1.4;
}

.error-close {
  background: rgba(255, 255, 255, 0.1);
  border: none;
  color: rgba(255, 255, 255, 0.7);
  font-size: 18px;
  cursor: pointer;
  padding: 4px;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  transition: all 0.3s ease;
  flex-shrink: 0;
  margin-left: 12px;
}

.error-close:hover {
  background: rgba(255, 255, 255, 0.2);
  color: rgba(255, 255, 255, 0.9);
  transform: scale(1.1);
}

/* 成功信息样式 */
.success-message {
  background: linear-gradient(135deg, rgba(76, 175, 80, 0.15), rgba(76, 175, 80, 0.25));
  backdrop-filter: blur(20px);
  border: 1px solid rgba(76, 175, 80, 0.4);
  border-radius: 12px;
  padding: 16px 20px;
  margin-bottom: 20px;
  animation: slideDown 0.3s ease-out;
  box-shadow: 0 4px 20px rgba(76, 175, 80, 0.15);
}

.success-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.success-icon {
  font-size: 20px;
  margin-right: 12px;
  flex-shrink: 0;
}

.success-text {
  flex: 1;
  color: rgba(255, 255, 255, 0.95);
  font-weight: 600;
  font-size: 14px;
  line-height: 1.4;
}

.success-close {
  background: rgba(255, 255, 255, 0.1);
  border: none;
  color: rgba(255, 255, 255, 0.7);
  font-size: 18px;
  cursor: pointer;
  padding: 4px;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  transition: all 0.3s ease;
  flex-shrink: 0;
  margin-left: 12px;
}

.success-close:hover {
  background: rgba(255, 255, 255, 0.2);
  color: rgba(255, 255, 255, 0.9);
  transform: scale(1.1);
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
  padding: 60px 40px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  margin: 20px 0;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(255, 255, 255, 0.1);
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-container p {
  color: rgba(255, 255, 255, 0.7);
  font-size: 16px;
  font-weight: 500;
}

/* 查询结果展示 */
.query-results {
  margin-top: 25px;
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 15px;
  padding: 0 10px;
}

.results-title {
  color: rgba(255, 255, 255, 0.95);
  font-size: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 700;
}

.results-count {
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
  font-weight: normal;
}

/* 视图控制 */
.view-controls {
  display: flex;
  align-items: center;
  gap: 10px;
}

.view-label {
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
  font-weight: 500;
}

.view-toggle {
  display: flex;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 4px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.view-option {
  padding: 6px 12px;
  border: none;
  background: transparent;
  color: rgba(255, 255, 255, 0.7);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
  font-weight: 500;
}

.view-option.active {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.4);
}

.view-option:hover:not(.active) {
  background: rgba(255, 255, 255, 0.05);
  color: rgba(255, 255, 255, 0.9);
}

/* 教师查询结果样式 */
.teaching-results-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.teacher-card {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0,0,0,0.2);
  transition: all 0.3s ease;
}

.teacher-card:hover {
  border-color: rgba(255, 255, 255, 0.2);
  box-shadow: 0 6px 25px rgba(0,0,0,0.3);
  transform: translateY(-2px);
}

.teacher-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: rgba(255, 255, 255, 0.08);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.teacher-header:hover {
  background: rgba(255, 255, 255, 0.12);
}

.teacher-info {
  flex: 1;
}

.teacher-name {
  color: rgba(255, 255, 255, 0.95);
  font-size: 18px;
  margin-bottom: 8px;
  font-weight: 700;
}

.teacher-details {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}

.detail-item {
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
  font-weight: 500;
}

.teacher-status-container {
  display: flex;
  align-items: center;
  gap: 12px;
}

.teacher-status {
  padding: 6px 12px;
  border-radius: 16px;
  font-weight: 600;
  font-size: 12px;
  min-width: 80px;
  text-align: center;
}

.collapse-icon {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.7);
  transition: transform 0.3s ease;
  font-weight: bold;
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

.courses-container {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.course-card {
  background: rgba(255, 255, 255, 0.03);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.05);
  overflow: hidden;
  transition: all 0.3s ease;
}

.course-card:hover {
  border-color: rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.05);
}

.course-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.05);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.course-header:hover {
  background: rgba(255, 255, 255, 0.08);
}

.course-info {
  flex: 1;
}

.course-name {
  color: rgba(255, 255, 255, 0.9);
  font-size: 16px;
  margin-bottom: 6px;
  font-weight: 600;
}

.course-details {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.course-status-container {
  display: flex;
  align-items: center;
  gap: 10px;
}

.course-status {
  padding: 4px 8px;
  border-radius: 12px;
  font-weight: 600;
  font-size: 11px;
  min-width: 60px;
  text-align: center;
}

.students-table-container {
  width: 100%;
  overflow-x: auto;
  border-radius: 0 0 8px 8px;
}

.students-table {
  width: 100%;
  border-collapse: collapse;
  background: rgba(255, 255, 255, 0.02);
}

.students-table th {
  background: rgba(255, 255, 255, 0.08);
  color: rgba(255, 255, 255, 0.95);
  padding: 12px 16px;
  text-align: left;
  font-weight: 600;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  font-size: 14px;
}

.students-table td {
  padding: 10px 16px;
  color: rgba(255, 255, 255, 0.8);
  border-bottom: 1px solid rgba(255, 255, 255, 0.03);
  font-size: 14px;
}

.students-table tr:last-child td {
  border-bottom: none;
}

.students-table tr:hover {
  background: rgba(255, 255, 255, 0.03);
}

/* 分数样式 */
.grade-excellent {
  color: #4CAF50 !important;
  font-weight: 700;
}

.grade-good {
  color: #8BC34A !important;
  font-weight: 700;
}

.grade-pass {
  color: #FFC107 !important;
  font-weight: 700;
}

.grade-fail {
  color: #F44336 !important;
  font-weight: 700;
}

/* 班级信息缺失样式 */
.no-class-info {
  color: #FF9800 !important;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 6px;
}

.no-class-info .warning-icon {
  font-size: 14px;
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
  border-radius: 16px;
  border: 2px dashed rgba(255, 255, 255, 0.15);
  text-align: center;
  margin-top: 20px;
}

.no-data-content {
  max-width: 500px;
}

.no-data-icon {
  font-size: 60px;
  margin-bottom: 20px;
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
  font-size: 24px;
  font-weight: 700;
}

.no-data-container p {
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 25px;
  font-size: 16px;
  line-height: 1.5;
}

.no-data-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
  flex-wrap: wrap;
}

.no-data-action-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 12px;
  padding: 12px 24px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

.no-data-action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
}

/* 初始状态样式 */
.initial-state-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 40px;
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(20px);
  border-radius: 16px;
  border: 2px dashed rgba(255, 255, 255, 0.15);
  text-align: center;
  margin-top: 20px;
}

.initial-state-content {
  max-width: 500px;
}

.initial-state-icon {
  font-size: 80px;
  margin-bottom: 25px;
  display: block;
  color: rgba(255, 255, 255, 0.3);
  animation: float 3s ease-in-out infinite;
}

.initial-state-container h3 {
  color: rgba(255, 255, 255, 0.95);
  margin-bottom: 15px;
  font-size: 24px;
  font-weight: 700;
}

.initial-state-container p {
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 30px;
  font-size: 16px;
  line-height: 1.5;
}

.initial-state-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 12px;
  padding: 14px 28px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 10px;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

.initial-state-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
}

.initial-state-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.btn-icon {
  font-size: 16px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .controls-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .main-controls {
    flex-direction: column;
    align-items: stretch;
  }
  
  .semester-group {
    min-width: auto;
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
  
  .results-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .view-controls {
    width: 100%;
    justify-content: space-between;
  }
  
  .teacher-header, .course-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .teacher-details, .course-details {
    flex-direction: column;
    gap: 5px;
  }
  
  .students-table {
    font-size: 12px;
  }
  
  .students-table th,
  .students-table td {
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
}

@media (max-width: 480px) {
  .combined-controls, .query-results {
    padding: 15px;
  }
  
  .section-title {
    font-size: 20px;
  }
  
  .title-icon {
    font-size: 24px;
  }
  
  .results-title {
    font-size: 18px;
  }
  
  .students-table-container {
    font-size: 12px;
  }
  
  .students-table th,
  .students-table td {
    padding: 6px 8px;
  }
  
  .error-message, .success-message {
    padding: 12px 15px;
  }
  
  .error-text, .success-text {
    font-size: 13px;
  }
  
  .no-data-icon, .initial-state-icon {
    font-size: 50px;
  }
  
  .no-data-container h3, .initial-state-container h3 {
    font-size: 20px;
  }
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
</style>