<template>
  <div class="query-container">
    <!-- 学期选择器与查询控制区域合并 -->
    <div class="combined-controls">
      <!-- 头部区域 -->
      <div class="controls-header">
        <h2 class="section-title">
          <span class="title-icon">👨‍🏫</span>
          班级成绩管理系统
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
      <div v-if="currentSemesterId && classData.length > 0" class="filter-controls">
        <div class="filter-group">
          <!-- 搜索框 -->
          <div class="filter-item">
            <label class="filter-label">搜索:</label>
            <input 
              type="text" 
              v-model="filters.search" 
              placeholder="搜索班级、教师、学生..."
              class="filter-input"
            >
          </div>
          
          <!-- 班级筛选 -->
          <div class="filter-item">
            <label class="filter-label">班级:</label>
            <select v-model="filters.selectedClass" class="filter-select">
              <option value="">全部班级</option>
              <option 
                v-for="classItem in availableClasses" 
                :key="classItem.class_id" 
                :value="classItem.class_id"
              >
                {{ classItem.class_name }}
              </option>
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
      <p>正在查询班级数据...</p>
    </div>
    
    <!-- 班级模式数据展示 -->
    <div v-if="filteredClassData.length > 0 && !loading" class="query-results">
      <div class="results-header">
        <h3 class="results-title">
          班级成绩总览
          <span class="results-count">(共 {{ filteredClassData.length }} 个班级)</span>
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
      
      <div class="class-results-container">
        <div v-for="classItem in filteredClassData" :key="classItem.class_id" class="class-card">
          <!-- 班级头部 - 简化操作按钮 -->
          <div class="class-header" @click="toggleClassExpansion(classItem.class_id)">
            <div class="class-info">
              <h4 class="class-name">{{ classItem.class_name }}</h4>
              <div class="class-details">
                <span class="detail-item">班级ID: {{ classItem.class_id }}</span>
                <span class="detail-item">学生人数: {{ classItem.students.length }}</span>
                <span class="detail-item">班主任: {{ getTeacherDisplay(classItem.teacher_name, classItem.teacher_id) }}</span>
                <span class="detail-item">班级平均分: {{ classItem.average_grade.toFixed(1) }}</span>
              </div>
            </div>
            <div class="class-status-container">
              <!-- 添加学生按钮 -->
              <button 
                @click.stop="openAddStudentDialog(classItem)"
                class="action-icon-btn add-btn"
                title="添加学生成绩"
              >
                ➕
              </button>
              
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
              <!-- 学生头部 - 简化操作按钮 -->
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
                  <!-- 简化学生操作按钮 -->
                  <div class="student-actions">
                    <button 
                      @click.stop="openAddCourseDialog(student)"
                      class="action-icon-btn course-btn"
                      title="添加课程"
                    >
                      📚
                    </button>
                    <button 
                      @click.stop="deleteStudent(student)"
                      class="action-icon-btn delete-btn"
                      title="删除学生"
                    >
                      🗑️
                    </button>
                  </div>
                  
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
                      <th>授课教师</th>
                      <th>得分</th>
                      <th>操作</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="course in student.courses" :key="course.course_id">
                      <td>{{ course.course_id }}</td>
                      <td>{{ course.course_name }}</td>
                      <td>{{ course.course_type }}</td>
                      <td>
                        <span v-if="hasTeacherInfo(course)">
                          {{ getTeacherDisplay(course.teacher_name, course.teacher_id) }}
                        </span>
                        <span v-else class="no-teacher-info">
                          <span class="warning-icon">⚠️</span>
                          教师未分配
                        </span>
                      </td>
                      <td :class="getGradeClass(course.grade)">
                        <!-- 成绩编辑功能 -->
                        <div class="grade-container">
                          <span class="grade-value">{{ course.grade }}</span>
                          <button 
                            @click.stop="editGrade(student, course)"
                            class="grade-edit-btn"
                            title="编辑成绩"
                          >
                            ✏️
                          </button>
                        </div>
                      </td>
                      <td>
                        <button 
                          @click.stop="removeStudentCourse(student, course)"
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
    <div v-if="filteredClassData.length === 0 && !loading && currentSemesterId && hasQueried" class="no-data-container">
      <div class="no-data-content">
        <div class="no-data-icon">📊</div>
        <h3>暂无班级数据</h3>
        <p>当前查询条件下没有找到相关班级数据，请尝试调整筛选条件</p>
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
        <div class="initial-state-icon">👨‍🏫</div>
        <h3>班级成绩查询</h3>
        <p>点击查询按钮获取班级成绩数据</p>
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
          <h3>为 {{ selectedClass?.class_name }} 添加学生成绩</h3>
          <button class="close-btn" @click="closeAddStudentDialog">×</button>
        </div>
        
        <div class="modal-body">
          <form @submit.prevent="submitAddStudent">
            <div class="form-group">
              <label>选择学生 *</label>
              <select v-model="newStudent.student_id" required class="form-select">
                <option value="">请选择学生</option>
                <option 
                  v-for="student in availableStudents" 
                  :key="student.student_id" 
                  :value="student.student_id"
                >
                  {{ student.student_name }} ({{ student.student_id }})
                </option>
              </select>
            </div>
            
            <div class="form-group">
              <label>选择课程 *</label>
              <select v-model="newStudent.course_id" required class="form-select">
                <option value="">请选择课程</option>
                <option 
                  v-for="course in availableCourses" 
                  :key="course.course_id" 
                  :value="course.course_id"
                >
                  {{ course.course_name }} ({{ course.course_type }})
                </option>
              </select>
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

    <!-- 添加课程弹窗 -->
    <div v-if="showAddCourseDialog" class="modal-overlay" @click.self="closeAddCourseDialog">
      <div class="modal-content">
        <div class="modal-header">
          <h3>为学生 {{ selectedStudent?.student_name }} 添加课程</h3>
          <button class="close-btn" @click="closeAddCourseDialog">×</button>
        </div>
        
        <div class="modal-body">
          <form @submit.prevent="submitAddCourse">
            <div class="form-group">
              <label>选择课程 *</label>
              <select v-model="newCourse.course_id" required class="form-select">
                <option value="">请选择课程</option>
                <option 
                  v-for="course in availableCourses" 
                  :key="course.course_id" 
                  :value="course.course_id"
                >
                  {{ course.course_name }} ({{ course.course_type }})
                </option>
              </select>
            </div>

            <div class="form-group">
              <label>得分 *</label>
              <input 
                v-model="newCourse.grade" 
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
              <button type="button" class="cancel-btn" @click="closeAddCourseDialog">取消</button>
              <button type="submit" class="submit-btn" :disabled="addCourseLoading">
                {{ addCourseLoading ? '添加中...' : '添加课程' }}
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
const showAddCourseDialog = ref(false)
const addStudentLoading = ref(false)
const addCourseLoading = ref(false)
const selectedClass = ref(null)
const selectedStudent = ref(null)

// 新增数据
const newStudent = ref({
  student_id: '',
  course_id: '',
  grade: 0
})

const newCourse = ref({
  course_id: '',
  grade: 0
})

// 可用课程列表
const availableCourses = ref([])
// 可用学生列表（本班学生）
const availableStudents = ref([])

// 学期选择器引用
const semesterSelector = ref(null)

// 筛选条件
const filters = ref({
  search: '',
  selectedClass: '',
  gradeRange: ''
})

// 获取本班所有学生 - 使用GET方法
const fetchClassStudents = async (classId) => {
  try {
    const token = localStorage.getItem('jwt_token')
    console.log('开始获取学生信息，班级ID:', classId)
    
    // 使用GET方法获取所有学生信息
    const response = await axios.get(`${apiConfig.BASE_URL}/admin/student_info`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    
    console.log('获取学生信息响应:', response.data)
    
    if (response.data.status === 'success') {
      // 从返回数据中筛选出指定班级的学生
      const allStudents = response.data.data.flatMap(classData => 
        classData.students || []
      )
      availableStudents.value = allStudents.filter(student => 
        student.class_id === classId
      )
      console.log(`班级 ${classId} 的学生:`, availableStudents.value)
    } else {
      errorMessage.value = response.data.error || '获取学生信息失败'
      availableStudents.value = []
    }
  } catch (error) {
    console.error('获取班级学生失败:', error)
    if (error.response) {
      console.error('错误详情:', error.response.data)
    }
    errorMessage.value = '获取学生信息失败，请检查网络连接'
    availableStudents.value = []
  }
}

// 获取所有课程 - 通过admin_check接口获取
const fetchCurrentSemesterCourses = async () => {
  try {
    const token = localStorage.getItem('jwt_token')
    
    // 通过admin_check接口获取教学数据来提取课程信息
    console.log('尝试通过admin_check获取课程信息...')
    const response = await axios.post(`${apiConfig.BASE_URL}/admin_check`, 
      {
        message_check: 'teaching',
        semester_id: currentSemesterId.value
      },
      {
        headers: { 'Authorization': `Bearer ${token}` }
      }
    )
    
    console.log('admin_check响应:', response.data)
    
    if (response.data.status === 'success') {
      // 从教学数据中提取课程信息
      const courses = new Map()
      response.data.data.forEach(teacher => {
        teacher.courses?.forEach(course => {
          if (course.course_id && !courses.has(course.course_id)) {
            courses.set(course.course_id, {
              course_id: course.course_id,
              course_name: course.course_name || `课程${course.course_id}`,
              course_type: course.course_type || '未知类型'
            })
          }
        })
      })
      
      availableCourses.value = Array.from(courses.values())
      console.log('提取的课程列表:', availableCourses.value)
      
      if (availableCourses.value.length === 0) {
        // 如果没有获取到课程，使用备用方案
        await fetchCoursesFallback()
      }
    } else {
      await fetchCoursesFallback()
    }
  } catch (error) {
    console.error('通过admin_check获取课程失败:', error)
    await fetchCoursesFallback()
  }
}

// 备用方案：从现有数据中提取课程或使用默认值
const fetchCoursesFallback = async () => {
  console.log('使用备用方案获取课程...')
  
  // 从当前班级数据中提取所有课程
  const courses = new Map()
  rawData.value.forEach(classItem => {
    classItem.students?.forEach(student => {
      student.courses?.forEach(course => {
        if (course.course_id && !courses.has(course.course_id)) {
          courses.set(course.course_id, {
            course_id: course.course_id,
            course_name: course.course_name || `课程${course.course_id}`,
            course_type: course.course_type || '未知类型'
          })
        }
      })
    })
  })
  
  if (courses.size > 0) {
    availableCourses.value = Array.from(courses.values())
    console.log('从现有数据提取的课程:', availableCourses.value)
  } else {
    // 最后使用默认课程列表
    availableCourses.value = [
      { course_id: 1, course_name: '数学', course_type: '必修' },
      { course_id: 2, course_name: '语文', course_type: '必修' },
      { course_id: 3, course_name: '英语', course_type: '必修' },
      { course_id: 4, course_name: '物理', course_type: '选修' },
      { course_id: 5, course_name: '化学', course_type: '选修' }
    ]
    console.log('使用默认课程列表:', availableCourses.value)
  }
}

// 打开添加学生成绩弹窗
const openAddStudentDialog = async (classItem) => {
  selectedClass.value = classItem
  console.log('打开弹窗，班级:', classItem)
  
  await fetchClassStudents(classItem.class_id)
  await fetchCurrentSemesterCourses()
  
  console.log('可用学生:', availableStudents.value)
  console.log('可用课程:', availableCourses.value)
  
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
  selectedClass.value = null
  availableStudents.value = []
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

// 打开添加课程弹窗
const openAddCourseDialog = (student) => {
  selectedStudent.value = student
  newCourse.value = {
    course_id: '',
    grade: 0
  }
  showAddCourseDialog.value = true
}

// 关闭添加课程弹窗
const closeAddCourseDialog = () => {
  showAddCourseDialog.value = false
  selectedStudent.value = null
}

// 提交添加课程 - 使用批量导入接口，支持添加新记录
const submitAddCourse = async () => {
  if (!newCourse.value.course_id) {
    errorMessage.value = '请选择课程'
    return
  }

  addCourseLoading.value = true

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
        student_id: selectedStudent.value.student_id,
        course_id: parseInt(newCourse.value.course_id),
        score: parseFloat(newCourse.value.grade),
        semester_name: semesterName
      }],
      {
        headers: { 'Authorization': `Bearer ${token}` }
      }
    )

    console.log('添加课程响应:', response.data)

    if (response.data.status === 'success') {
      successMessage.value = '课程添加成功'
      closeAddCourseDialog()
      await handleQuery() // 刷新数据
    } else {
      errorMessage.value = response.data.error || '添加失败'
    }
  } catch (error) {
    console.error('添加课程失败:', error)
    if (error.response) {
      console.error('错误响应:', error.response.data)
      errorMessage.value = error.response.data.error || '添加课程失败'
    } else {
      errorMessage.value = '网络错误，请检查连接'
    }
  } finally {
    addCourseLoading.value = false
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
  
  // 获取本学期课程
  await fetchCurrentSemesterCourses()
  
  // 如果有学期ID，自动查询
  if (semesterId) {
    // 短暂延迟确保DOM更新完成
    await nextTick()
    await handleQuery()
  }
}

// 检查课程是否有教师信息
const hasTeacherInfo = (course) => {
  return course.teacher_name && course.teacher_id && 
         course.teacher_name.trim() !== '' && 
         course.teacher_id.toString().trim() !== ''
}

// 获取教师显示信息
const getTeacherDisplay = (teacherName, teacherId) => {
  if (teacherName && teacherName.trim() !== '' && 
      teacherName !== '未分配' && teacherName !== '未知' &&
      teacherName !== '未知教师' && teacherName !== 'N/A') {
    return teacherName
  }
  
  if (teacherId && teacherId.toString().trim() !== '' && teacherId !== 'N/A') {
    return `教师ID: ${teacherId}`
  }
  
  return '未分配教师'
}

// 计算属性 - 处理班级数据
const classData = computed(() => {
  if (!rawData.value.length) return []
  
  return rawData.value.map(classItem => {
    // 计算班级平均分
    let totalGrade = 0
    let totalCourses = 0
    
    classItem.students.forEach(student => {
      // 确保每个课程都有教师信息
      student.courses.forEach(course => {
        if (!hasTeacherInfo(course)) {
          course.teacher_name = '未分配'
          course.teacher_id = 'N/A'
        }
      })
      
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

// 筛选后的班级数据
const filteredClassData = computed(() => {
  if (!classData.value.length) return []
  
  return classData.value
    .filter(classItem => {
      // 班级筛选
      if (filters.value.selectedClass && classItem.class_id !== filters.value.selectedClass) {
        return false
      }
      
      // 搜索筛选
      if (filters.value.search) {
        const searchLower = filters.value.search.toLowerCase()
        const classNameMatch = classItem.class_name?.toLowerCase().includes(searchLower)
        const teacherNameMatch = classItem.teacher_name?.toLowerCase().includes(searchLower)
        const studentMatch = classItem.students.some(student => 
          student.student_name?.toLowerCase().includes(searchLower) ||
          student.student_id?.toString().includes(searchLower)
        )
        
        if (!classNameMatch && !teacherNameMatch && !studentMatch) return false
      }
      
      return true
    })
    .map(classItem => {
      // 筛选学生
      const filteredStudents = classItem.students.filter(student => {
        // 搜索筛选
        if (filters.value.search) {
          const searchLower = filters.value.search.toLowerCase()
          const nameMatch = student.student_name?.toLowerCase().includes(searchLower)
          const idMatch = student.student_id?.toString().includes(searchLower)
          if (!nameMatch && !idMatch) return false
        }
        
        return true
      })
      
      return {
        ...classItem,
        students: filteredStudents
      }
    })
    .filter(classItem => classItem.students.length > 0)
})

// 可用班级列表（用于筛选）
const availableClasses = computed(() => {
  if (!classData.value.length) return []
  
  return classData.value.map(classItem => ({
    class_id: classItem.class_id,
    class_name: classItem.class_name
  }))
})

// 筛选后的数据总数
const filteredDataCount = computed(() => {
  return filteredClassData.value.reduce((total, classItem) => total + classItem.students.length, 0)
})

// 总数据量
const totalDataCount = computed(() => {
  return classData.value.reduce((total, classItem) => total + classItem.students.length, 0)
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
        message_check: 'class',
        semester_id: currentSemesterId.value
      },
      {
        headers: { 'Authorization': `Bearer ${token}` }
      }
    )
    
    console.log('API响应:', response.data)
    
    if (response.data.status === 'success') {
      console.log('返回的班级数据:', response.data.data)
      
      // 增强数据格式处理
      const processedData = processClassData(response.data.data)
      rawData.value = processedData.map(classItem => {
        return {
          ...classItem,
          isExpanded: false,
          students: (classItem.students || []).map(student => ({
            ...student,
            isExpanded: false,
            // 确保每个学生都有courses数组
            courses: student.courses || []
          }))
        }
      })
      
      successMessage.value = '班级成绩查询成功'
      
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
const processClassData = (data) => {
  if (!data || !Array.isArray(data)) return []
  
  return data.map(classItem => {
    // 确保班级数据完整性
    const processedClass = {
      class_id: classItem.class_id || 0,
      class_name: classItem.class_name || '未知班级',
      student_count: classItem.student_count || 0,
      teacher_name: classItem.teacher_name || '未分配',
      teacher_id: classItem.teacher_id || null,
      students: []
    }
    
    // 处理学生数据
    if (Array.isArray(classItem.students)) {
      processedClass.students = classItem.students.map(student => ({
        student_id: student.student_id || 0,
        student_name: student.student_name || '未知学生',
        class_id: student.class_id || processedClass.class_id,
        courses: student.courses || [],
        average_grade: student.average_grade || 0
      }))
    }
    
    return processedClass
  })
}

// 重置筛选条件
const resetFilters = () => {
  filters.value = {
    search: '',
    selectedClass: '',
    gradeRange: ''
  }
}

// 展开所有
const expandAll = () => {
  expandState.value = 'all'
  filteredClassData.value.forEach(classItem => {
    classItem.isExpanded = true
    classItem.students.forEach(student => {
      student.isExpanded = true
    })
  })
}

// 收起所有
const collapseAll = () => {
  expandState.value = 'none'
  filteredClassData.value.forEach(classItem => {
    classItem.isExpanded = false
    classItem.students.forEach(student => {
      student.isExpanded = false
    })
  })
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
}

// 清除成功信息
const clearSuccess = () => {
  successMessage.value = ''
}

// 删除学生 - 使用DELETE方法
const deleteStudent = async (student) => {
  if (!confirm(`确定要删除学生 "${student.student_name}" 吗？此操作不可撤销！`)) {
    return
  }

  try {
    const token = localStorage.getItem('jwt_token')
    // 使用DELETE方法，符合后端API定义
    const response = await axios.delete(`${apiConfig.BASE_URL}/admin/student_info`, {
      headers: { 'Authorization': `Bearer ${token}` },
      data: { student_id: student.student_id }  // DELETE方法使用data传参
    })

    console.log('删除学生响应:', response.data)

    if (response.data.status === 'success') {
      successMessage.value = '学生删除成功'
      await handleQuery()
    } else {
      errorMessage.value = response.data.error || '删除失败'
    }
  } catch (error) {
    console.error('删除学生失败:', error)
    if (error.response) {
      console.error('错误详情:', error.response.data)
      errorMessage.value = error.response.data.error || '删除失败'
    }
    handleApiError(error)
  }
}

// 编辑成绩
const editGrade = (student, course) => {
  const newGrade = prompt(`请输入 ${student.student_name} 的 ${course.course_name} 新成绩:`, course.grade)
  
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
const removeStudentCourse = async (student, course) => {
  if (!confirm(`确定要删除 ${student.student_name} 的 ${course.course_name} 课程吗？`)) {
    return
  }

  try {
    const token = localStorage.getItem('jwt_token')
    // 这里需要调用删除课程成绩的API
    // 假设有删除课程成绩的API，使用DELETE方法
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
    await fetchCurrentSemesterCourses()
    await handleQuery()
  }
})
</script>
<style scoped>
/* 原有的样式保持不变，只添加弹窗相关样式 */

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

/* 添加按钮样式 */
.add-btn:hover {
  background: rgba(76, 175, 80, 0.2);
  border-color: rgba(76, 175, 80, 0.4);
}

/* 原有的其他样式保持不变 */
/* ... */
/* 样式与之前保持一致，只做必要修改 */
.query-container {
  width: 100%;
  margin-top: 0;
  position: relative;
  z-index: 1;
  min-height: 500px;
}

.combined-controls {
  margin-bottom: 25px;
  padding: 25px;
  background: rgba(30, 30, 46, 0.8);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.3);
  border: 1px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
}

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

/* 操作按钮区域样式 */
.actions-bar {
  display: flex;
  justify-content: flex-start;
  align-items: center;
  margin-bottom: 20px;
  gap: 12px;
  flex-wrap: wrap;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.primary-btn {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

.primary-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
}

.secondary-btn {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: rgba(255, 255, 255, 0.9);
}

.secondary-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.15);
  transform: translateY(-1px);
}

.action-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

/* 操作按钮样式 */
.class-actions, .student-actions {
  display: flex;
  gap: 6px;
  margin-right: 12px;
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

.edit-btn:hover {
  background: rgba(76, 175, 80, 0.2);
  border-color: rgba(76, 175, 80, 0.4);
}

.delete-btn:hover {
  background: rgba(244, 67, 54, 0.2);
  border-color: rgba(244, 67, 54, 0.4);
}

.course-btn:hover {
  background: rgba(33, 150, 243, 0.2);
  border-color: rgba(33, 150, 243, 0.4);
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

.courses-table tr:hover .grade-edit-btn {
  opacity: 1;
}

/* 其他样式保持不变... */
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

.custom-semester-selector {
  width: 100%;
}

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

.class-results-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.class-card {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0,0,0,0.2);
  transition: all 0.3s ease;
}

.class-card:hover {
  border-color: rgba(255, 255, 255, 0.2);
  box-shadow: 0 6px 25px rgba(0,0,0,0.3);
  transform: translateY(-2px);
}

.class-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
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
  font-weight: 700;
}

.class-details {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}

.detail-item {
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
  font-weight: 500;
}

.class-status-container {
  display: flex;
  align-items: center;
  gap: 12px;
}

.class-status {
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

.students-container {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.student-card {
  background: rgba(255, 255, 255, 0.03);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.05);
  overflow: hidden;
  transition: all 0.3s ease;
}

.student-card:hover {
  border-color: rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.05);
}

.student-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
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
  margin-bottom: 6px;
  font-weight: 600;
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
  padding: 4px 8px;
  border-radius: 12px;
  font-weight: 600;
  font-size: 11px;
  min-width: 60px;
  text-align: center;
}

.courses-table-container {
  width: 100%;
  overflow-x: auto;
  border-radius: 0 0 8px 8px;
}

.courses-table {
  width: 100%;
  border-collapse: collapse;
  background: rgba(255, 255, 255, 0.02);
}

.courses-table th {
  background: rgba(255, 255, 255, 0.08);
  color: rgba(255, 255, 255, 0.95);
  padding: 12px 16px;
  text-align: left;
  font-weight: 600;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  font-size: 14px;
}

.courses-table td {
  padding: 10px 16px;
  color: rgba(255, 255, 255, 0.8);
  border-bottom: 1px solid rgba(255, 255, 255, 0.03);
  font-size: 14px;
}

.courses-table tr:last-child td {
  border-bottom: none;
}

.courses-table tr:hover {
  background: rgba(255, 255, 255, 0.03);
}

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

.no-teacher-info {
  color: #FF9800 !important;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 6px;
}

.no-teacher-info .warning-icon {
  font-size: 14px;
}

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
  
  .actions-bar {
    flex-direction: column;
    align-items: stretch;
  }
  
  .action-group {
    width: 100%;
    justify-content: space-between;
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
  
  .class-header, .student-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .class-details, .student-details {
    flex-direction: column;
    gap: 5px;
  }
  
  .class-actions, .student-actions {
    margin-right: 8px;
    gap: 4px;
  }
  
  .action-icon-btn {
    width: 28px;
    height: 28px;
    font-size: 12px;
  }
  
  .courses-table {
    font-size: 12px;
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