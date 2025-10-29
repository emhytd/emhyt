<template>
  <div class="admin-query-container">
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
      <div class="header-section">
        <h2 class="section-title">
          <span class="title-icon">📊</span>
          管理员查询
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
      
      <!-- 查询类型选择 -->
      <div class="query-type-section">
        <div class="button-group">
          <button 
            @click="handleQuery('class')" 
            class="query-btn"
            :disabled="loading || !semesterId"
            :class="{ active: currentQueryType === 'class' }"
          >
            <span class="btn-icon">👨‍🏫</span>
            班级成绩总览
          </button>
          
          <button 
            @click="handleQuery('teaching')" 
            class="query-btn"
            :disabled="loading || !semesterId"
            :class="{ active: currentQueryType === 'teaching' }"
          >
            <span class="btn-icon">📚</span>
            教师教学总览
          </button>
        </div>
        
        <div v-if="!semesterId" class="semester-warning">
          <span class="warning-icon">ℹ️</span>
          请先选择学期
        </div>
      </div>
      
      <!-- 筛选控制区域 -->
      <div v-if="currentQueryType && semesterId" class="filter-controls">
        <div class="filter-group">
          <!-- 搜索框 -->
          <div class="filter-item">
            <label class="filter-label">搜索:</label>
            <input 
              type="text" 
              v-model="filters.search" 
              :placeholder="getSearchPlaceholder()"
              class="filter-input"
            >
          </div>
          
          <!-- 班级模式筛选 -->
          <div v-if="currentQueryType === 'class'" class="filter-item">
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
          
          <!-- 教师模式筛选 -->
          <div v-if="currentQueryType === 'teaching'" class="filter-item">
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
    
    <!-- 班级模式数据展示 -->
    <div v-if="currentQueryType === 'class' && filteredClassData.length > 0 && !loading" class="query-results">
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
          <div class="class-header" @click="toggleClassExpansion(classItem.class_id)">
            <div class="class-info">
              <h4 class="class-name">{{ classItem.class_name }}</h4>
              <div class="class-details">
                <span class="detail-item">班级ID: {{ classItem.class_id }}</span>
                <span class="detail-item">学生人数: {{ classItem.students.length }}</span>
                <!-- 直接使用班级数据中的班主任信息 -->
                <span class="detail-item">班主任: {{ getTeacherDisplay(classItem.teacher_name, classItem.teacher_id) }}</span>
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
                      <th>授课教师</th>
                      <th>得分</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="course in student.courses" :key="course.course_id">
                      <td>{{ course.course_id }}</td>
                      <td>{{ course.course_name }}</td>
                      <td>{{ course.course_type }}</td>
                      <td>
                        <!-- 直接使用课程数据中的授课教师信息 -->
                        <span v-if="hasTeacherInfo(course)">
                          {{ getTeacherDisplay(course.teacher_name, course.teacher_id) }}
                        </span>
                        <span v-else class="no-teacher-info">
                          <span class="warning-icon">⚠️</span>
                          教师未分配
                        </span>
                      </td>
                      <td :class="getGradeClass(course.grade)">
                        {{ course.grade }}
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
    
    <!-- 授课模式数据展示 -->
    <div v-if="currentQueryType === 'teaching' && filteredTeachingData.length > 0 && !loading" class="query-results">
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
              </div>
            </div>
            <div class="collapse-icon">
              {{ teacher.isExpanded ? '▼' : '►' }}
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
                    <span class="detail-item">平均分: {{ course.average_grade.toFixed(1) }}</span>
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
                        {{ student.grade }}
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
    <div v-if="((currentQueryType === 'class' && filteredClassData.length === 0) || 
                (currentQueryType === 'teaching' && filteredTeachingData.length === 0)) && 
                !loading && currentQueryType && semesterId" class="no-data-container">
      <div class="no-data-content">
        <div class="no-data-icon">📊</div>
        <h3>暂无查询数据</h3>
        <p>当前查询条件下没有找到相关数据，请尝试调整筛选条件</p>
        <div class="no-data-actions">
          <button 
            @click="resetFilters"
            class="no-data-action-btn"
          >
            <span class="btn-icon">🔄</span>
            重置筛选条件
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import apiConfig from '@/config/apiConfig';
import { ref, computed, watch, onMounted } from 'vue'
import axios from 'axios'

export default {
  props: {
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
  },
  
  emits: ['update:errorMessage', 'clear-error'],
  
  setup(props, { emit }) {
    // 响应式数据
    const rawData = ref([])
    const loading = ref(false)
    const errorMessage = ref('')
    const successMessage = ref('')
    const currentQueryType = ref('') // 'class' 或 'teaching'
    const expandState = ref('none') // 'all', 'none'

    // 筛选条件
    const filters = ref({
      search: '',
      selectedClass: '',
      selectedTeacher: '',
      gradeRange: ''
    })

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
      if (currentQueryType.value !== 'class' || !rawData.value.length) return []
      
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

    // 计算属性 - 处理教师数据
    const teachingData = computed(() => {
      if (currentQueryType.value !== 'teaching' || !rawData.value.length) return []
      
      return rawData.value.map(teacher => {
        // 计算每位教师的平均分
        let totalCourses = 0
        let totalGrade = 0
        
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
          
          // 累加教师总分和课程数
          totalGrade += courseTotalGrade
          totalCourses += course.students.length
        })
        
        return teacher
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
            
            // 成绩筛选
            if (filters.value.gradeRange) {
              const avgGrade = student.average_grade
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
            ...classItem,
            students: filteredStudents
          }
        })
        .filter(classItem => classItem.students.length > 0) // 移除没有学生的班级
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

    // 可用班级列表（用于筛选）
    const availableClasses = computed(() => {
      if (!classData.value.length) return []
      
      return classData.value.map(classItem => ({
        class_id: classItem.class_id,
        class_name: classItem.class_name
      }))
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
      if (currentQueryType.value === 'class') {
        return filteredClassData.value.reduce((total, classItem) => total + classItem.students.length, 0)
      } else if (currentQueryType.value === 'teaching') {
        return filteredTeachingData.value.reduce((total, teacher) => 
          total + teacher.courses.reduce((courseTotal, course) => courseTotal + course.students.length, 0), 0)
      }
      return 0
    })

    // 总数据量
    const totalDataCount = computed(() => {
      if (currentQueryType.value === 'class') {
        return classData.value.reduce((total, classItem) => total + classItem.students.length, 0)
      } else if (currentQueryType.value === 'teaching') {
        return teachingData.value.reduce((total, teacher) => 
          total + teacher.courses.reduce((courseTotal, course) => courseTotal + course.students.length, 0), 0)
      }
      return 0
    })

    // 获取搜索框占位符文本
    const getSearchPlaceholder = () => {
      if (currentQueryType.value === 'class') {
        return '搜索班级、教师、学生姓名或学号...'
      } else if (currentQueryType.value === 'teaching') {
        return '搜索教师、课程、学生姓名或学号...'
      }
      return '搜索...'
    }
  
    // 处理查询
    const handleQuery = async (queryType) => {
      if (!props.semesterId) {
        errorMessage.value = '请先选择学期'
        return
      }
      
      currentQueryType.value = queryType
      loading.value = true
      errorMessage.value = ''
      successMessage.value = ''
      rawData.value = []
      
      try {
        const token = localStorage.getItem('jwt_token')
        const response = await axios.post(apiConfig.ADMIN_API.CHECK, 
          {
            message_check: queryType,
            semester_id: props.semesterId
          },
          {
            headers: { 'Authorization': `Bearer ${token}` }
          }
        )
        
        if (response.data.status === 'success') {
          // 为每个班级/教师添加折叠状态
          if (queryType === 'class') {
            rawData.value = response.data.data.map(classItem => {
              return {
                ...classItem,
                isExpanded: false,
                students: classItem.students.map(student => ({
                  ...student,
                  isExpanded: false
                }))
              }
            })
          } else {
            rawData.value = response.data.data.map(teacher => ({
              ...teacher,
              isExpanded: false,
              courses: teacher.courses.map(course => ({
                ...course,
                isExpanded: false
              }))
            }))
          }
          
          successMessage.value = queryType === 'class' ? '班级成绩查询成功' : '教师教学查询成功'
          
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

    // 重置筛选条件
    const resetFilters = () => {
      filters.value = {
        search: '',
        selectedClass: '',
        selectedTeacher: '',
        gradeRange: ''
      }
    }

    // 展开所有
    const expandAll = () => {
      expandState.value = 'all'
      if (currentQueryType.value === 'class') {
        filteredClassData.value.forEach(classItem => {
          classItem.isExpanded = true
          classItem.students.forEach(student => {
            student.isExpanded = true
          })
        })
      } else if (currentQueryType.value === 'teaching') {
        filteredTeachingData.value.forEach(teacher => {
          teacher.isExpanded = true
          teacher.courses.forEach(course => {
            course.isExpanded = true
          })
        })
      }
    }

    // 收起所有
    const collapseAll = () => {
      expandState.value = 'none'
      if (currentQueryType.value === 'class') {
        filteredClassData.value.forEach(classItem => {
          classItem.isExpanded = false
          classItem.students.forEach(student => {
            student.isExpanded = false
          })
        })
      } else if (currentQueryType.value === 'teaching') {
        filteredTeachingData.value.forEach(teacher => {
          teacher.isExpanded = false
          teacher.courses.forEach(course => {
            course.isExpanded = false
          })
        })
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
      emit('clear-error')
    }

    // 清除成功信息
    const clearSuccess = () => {
      successMessage.value = ''
    }

    // 监听学期ID变化
    watch(() => props.semesterId, (newVal) => {
      if (newVal && currentQueryType.value) {
        handleQuery(currentQueryType.value)
      } else {
        // 学期ID为空时清空数据
        rawData.value = []
        currentQueryType.value = ''
        resetFilters()
      }
    })

    // 组件挂载时初始化查询
    onMounted(() => {
      if (props.semesterId) {
        handleQuery('class')
      }
    })

    return {
      rawData,
      loading,
      errorMessage,
      successMessage,
      currentQueryType,
      expandState,
      filters,
      classData,
      teachingData,
      filteredClassData,
      filteredTeachingData,
      availableClasses,
      availableTeachers,
      filteredDataCount,
      totalDataCount,
      handleQuery,
      resetFilters,
      expandAll,
      collapseAll,
      toggleClassExpansion,
      toggleStudentExpansion,
      toggleTeacherExpansion,
      toggleCourseExpansion,
      getTotalStudents,
      getSearchPlaceholder,
      getTeacherDisplay,
      hasTeacherInfo,
      getGradeClass,
      getClassStatusClass,
      getClassStatusText,
      getStudentStatusClass,
      getStudentStatusText,
      getCourseStatusClass,
      getCourseStatusText,
      clearError,
      clearSuccess
    }
  }
}
</script>

<!-- 样式部分保持不变 -->
<style scoped>
/* 样式保持不变，与之前的代码相同 */
.admin-query-container {
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
  padding: 25px;
  background: rgba(30, 30, 46, 0.9);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.3);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

/* 头部区域样式 */
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

/* 查询类型区域 */
.query-type-section {
  margin-bottom: 20px;
}

.button-group {
  display: flex;
  gap: 15px;
  justify-content: center;
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

/* 筛选控制区域 */
.filter-controls {
  margin: 20px 0;
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
  font-weight: 500;
}

.filter-select {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 6px;
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
}

.filter-select:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.3);
}

.filter-input {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 6px;
  color: rgba(255, 255, 255, 0.9);
  padding: 10px 12px;
  font-size: 14px;
  transition: all 0.3s ease;
}

.filter-input:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.3);
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

/* 视图控制 */
.view-controls {
  display: flex;
  align-items: center;
  gap: 10px;
}

.view-label {
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
}

.view-toggle {
  display: flex;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 4px;
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
}

.view-option.active {
  background: rgba(102, 126, 234, 0.3);
  color: white;
}

.view-option:hover:not(.active) {
  background: rgba(255, 255, 255, 0.05);
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
}

.courses-table tr:last-child td {
  border-bottom: none;
}

.courses-table tr:hover {
  background: rgba(255, 255, 255, 0.02);
}

/* 教师查询结果样式 */
.teaching-results-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.teacher-card {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  overflow: hidden;
}

.teacher-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
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
}

.teacher-details {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}

.courses-container {
  padding: 15px;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.course-card {
  background: rgba(255, 255, 255, 0.03);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.05);
  overflow: hidden;
}

.course-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 15px;
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
  margin-bottom: 5px;
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
  padding: 6px 12px;
  border-radius: 20px;
  font-weight: 600;
  font-size: 14px;
}

.students-table-container {
  width: 100%;
  overflow-x: auto;
}

.students-table {
  width: 100%;
  border-collapse: collapse;
}

.students-table th {
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.95);
  padding: 12px 15px;
  text-align: left;
  font-weight: 600;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

.students-table td {
  padding: 12px 15px;
  color: rgba(255, 255, 255, 0.8);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  position: relative;
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

/* 教师未分配和班级信息缺失样式 */
.no-teacher-info,
.no-class-info {
  color: #FF9800 !important;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 5px;
}

.no-teacher-info .warning-icon,
.no-class-info .warning-icon {
  font-size: 14px;
}

/* 无数据提示样式 - 优化 */
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
  
  .button-group {
    flex-direction: column;
  }
  
  .query-btn {
    justify-content: center;
  }
  
  .class-header, .teacher-header, .student-header, .course-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .class-details, .teacher-details, .student-details, .course-details {
    flex-direction: column;
    gap: 5px;
  }
  
  .courses-table, .students-table {
    font-size: 14px;
  }
  
  .courses-table th,
  .courses-table td,
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
  .query-controls, .query-results {
    padding: 15px;
  }
  
  .section-title {
    font-size: 20px;
  }
  
  .title-icon {
    font-size: 28px;
  }
  
  .results-title {
    font-size: 18px;
  }
  
  .courses-table-container, .students-table-container {
    font-size: 12px;
  }
  
  .courses-table th,
  .courses-table td,
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
  
  .no-data-icon {
    font-size: 60px;
  }
  
  .no-data-container h3 {
    font-size: 24px;
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