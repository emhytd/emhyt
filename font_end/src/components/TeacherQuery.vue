<template>
  <div class="teacher-query-container">
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
    <div class="controls-container">
      <div class="header-section">
        <h2 class="section-title">
          <span class="title-icon">📚</span>
          授课课程查询
        </h2>
        <div class="header-stats">
          <div class="stat-item">
            <span class="stat-number">{{ 
              currentQueryType === 'class' ? filteredClassData.length : 
              currentQueryType === 'teaching' ? filteredTeachingData.length : 0 
            }}</span>
            <span class="stat-label">查询结果</span>
          </div>
          <div class="stat-item">
            <span class="stat-number">{{ 
              currentQueryType === 'class' ? classData.length : 
              currentQueryType === 'teaching' ? teachingData.length : 0 
            }}</span>
            <span class="stat-label">总数据量</span>
          </div>
        </div>
      </div>
      
      <!-- 查询按钮 -->
      <div class="query-controls">
        <button 
          @click="handleQuery('teaching')" 
          class="action-btn primary-btn query-btn"
          :disabled="loading"
          :class="{ active: currentQueryType === 'teaching' }"
        >
          <span class="btn-icon">🔍</span>
          查询授课数据
        </button>
        
        <!-- 批量导入按钮 -->
        <button 
          @click="showBulkImport = true" 
          class="action-btn secondary-btn bulk-import-btn"
        >
          <span class="btn-icon">📤</span>
          批量导入成绩
        </button>
      </div>
      
      <!-- 筛选控制区域 -->
      <div v-if="(currentQueryType === 'teaching' && teachingData.length > 0)" class="filter-controls">
        <h3 class="filter-title">筛选条件</h3>
        
        <div class="filter-group">
          <!-- 课程筛选 -->
          <div class="filter-item">
            <label class="filter-label">课程筛选:</label>
            <select v-model="filters.selectedCourse" class="filter-select">
              <option value="">全部课程</option>
              <option 
                v-for="course in availableCoursesForFilter" 
                :key="course.course_id" 
                :value="course.course_id"
              >
                {{ course.course_name }}
              </option>
            </select>
          </div>
          
          <!-- 学生搜索 -->
          <div class="filter-item">
            <label class="filter-label">学生搜索:</label>
            <input 
              type="text" 
              v-model="filters.studentSearch" 
              placeholder="输入学生姓名或学号" 
              class="filter-input"
            >
          </div>
          
          <!-- 成绩范围筛选 -->
          <div class="filter-item">
            <label class="filter-label">成绩范围:</label>
            <select v-model="filters.gradeRange" class="filter-select">
              <option value="">全部成绩</option>
              <option value="90-100">90-100 (优秀)</option>
              <option value="80-89">80-89 (良好)</option>
              <option value="60-79">60-79 (及格)</option>
              <option value="0-59">0-59 (不及格)</option>
            </select>
          </div>
          
          <!-- 重置筛选按钮 -->
          <button @click="resetFilters" class="filter-reset-btn action-btn secondary-btn">
            重置筛选
          </button>
        </div>
      </div>
    </div>
    
    <!-- 授课模式数据展示 -->
    <div v-if="currentQueryType === 'teaching' && filteredTeachingData.length > 0 && !loading" class="data-container">
      <div class="results-header">
        <h3 class="results-title">
          授课课程信息
          <span class="results-count">(共 {{ filteredTeachingData.length }} 门课程)</span>
        </h3>
      </div>
      
      <div class="teaching-results-container">
        <div v-for="course in filteredTeachingData" :key="course.course_id" class="course-card">
          <div class="course-header" @click="toggleCourseExpansion(course.course_id)">
            <div class="course-info">
              <h4 class="course-name">{{ course.course_name }}</h4>
              <div class="course-details">
                <span class="detail-item">课程ID: {{ course.course_id }}</span>
                <span class="detail-item">课程类型: {{ course.course_type }}</span>
                <span class="detail-item">授课教师: {{ course.course_teacher?.teacher_name || '未设置' }}</span>
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
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="student in course.students" :key="student.student_id">
                  <td>{{ student.student_id }}</td>
                  <td>{{ student.student_name }}</td>
                  <td>{{ student.class_name }}</td>
                  <td 
                    @dblclick="startEditGrade(student.student_id, course.course_id, student.grade)"
                    :class="getGradeClass(student.grade)"
                  >
                    <span v-if="!isEditing(student.student_id, course.course_id)">{{ student.grade }}</span>
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
                    <button 
                      @click="deleteGrade(student.student_id, course.course_id)"
                      class="action-btn delete-btn"
                      title="删除成绩"
                    >
                      🗑️
                    </button>
                  </td>
                </tr>
                <!-- 新增成绩行 -->
                <tr class="add-grade-row">
                  <td>
                    <select v-model="newGrade.student_id" class="student-select">
                      <option value="">选择学生</option>
                      <option 
                        v-for="student in availableStudents" 
                        :key="student.student_id" 
                        :value="student.student_id"
                      >
                        {{ student.student_name }} ({{ student.student_id }})
                      </option>
                    </select>
                  </td>
                  <td>
                    <span v-if="newGrade.student_id">
                      {{ getStudentName(newGrade.student_id) }}
                    </span>
                  </td>
                  <td>
                    <span v-if="newGrade.student_id">
                      {{ getStudentClass(newGrade.student_id) }}
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
                      @click="addNewGrade(course.course_id)"
                      class="action-btn add-btn"
                      :disabled="!canAddGrade(course.course_id)"
                      title="添加成绩"
                    >
                      ➕
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 无数据提示 -->
    <div v-if="((currentQueryType === 'teaching' && filteredTeachingData.length === 0)) && 
                !loading && currentQueryType" class="no-data-container">
      <div class="no-data-content">
        <span class="no-data-icon">📊</span>
        <h3>暂无查询数据</h3>
        <p>当前查询条件下没有找到相关数据</p>
        <button @click="resetFilters" class="no-data-action-btn secondary">重置筛选条件</button>
      </div>
    </div>
    
    <!-- 提交按钮 -->
    <div v-if="hasChanges" class="submit-container">
      <button @click="submitChanges" class="action-btn primary-btn submit-btn">
        <span class="btn-icon">💾</span>
        提交所有更改
      </button>
      <span class="changes-count">有 {{ changesCount }} 处更改待提交</span>
    </div>

    <!-- 批量导入模态框 -->
    <div v-if="showBulkImport" class="modal-overlay" @click="showBulkImport = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>批量导入成绩</h3>
          <button @click="closeBulkImport" class="modal-close">×</button>
        </div>
        
        <!-- 批量导入界面内容 -->
        <div class="bulk-import-content">
          <!-- 错误信息提示 -->
          <div v-if="bulkErrorMessage" class="error-message">
            <div class="error-content">
              <span class="error-icon">⚠️</span>
              <span class="error-text">{{ bulkErrorMessage }}</span>
              <button @click="clearBulkError" class="error-close">×</button>
            </div>
          </div>

          <!-- 成功信息提示 -->
          <div v-if="bulkSuccessMessage" class="success-message">
            <div class="success-content">
              <span class="success-icon">✅</span>
              <span class="success-text">{{ bulkSuccessMessage }}</span>
              <button @click="clearBulkSuccess" class="success-close">×</button>
            </div>
          </div>

          <!-- 加载状态 -->
          <div v-if="bulkLoading" class="loading-container">
            <div class="loading-spinner"></div>
            <p>{{ bulkLoadingText }}</p>
          </div>

          <!-- 操作区域 -->
          <div class="operation-section">
            <div class="operation-card">
              <div class="operation-grid">
                <!-- 模板下载 -->
                <div class="operation-item">
                  <h3 class="card-title">下载模板</h3>
                  <p class="operation-desc">下载Excel或CSV模板文件，按照格式填写数据</p>
                  <div class="template-buttons">
                    <button @click="downloadTemplate('excel')" class="download-btn">
                      📥 Excel模板
                    </button>
                    <button @click="downloadTemplate('csv')" class="download-btn csv-btn">
                      📥 CSV模板
                    </button>
                  </div>
                </div>

                <!-- 文件上传 -->
                <div class="operation-item">
                  <h3 class="card-title">上传文件</h3>
                  <p class="operation-desc">上传填写好的Excel或CSV文件</p>
                  <div class="upload-area" 
                       @click="triggerFileInput"
                       @drop="handleDrop"
                       @dragover.prevent="handleDragOver"
                       @dragleave.prevent="handleDragLeave"
                       :class="{ 'drag-over': isDragOver }">
                    <div class="upload-content">
                      <span class="upload-icon">📄</span>
                      <p class="upload-text">点击或拖拽文件到此处</p>
                      <p class="upload-hint">支持 .xlsx, .xls, .csv 格式</p>
                    </div>
                    <input 
                      type="file" 
                      ref="fileInput"
                      @change="handleFileSelect"
                      accept=".xlsx,.xls,.csv"
                      class="file-input"
                      @click.stop
                    />
                  </div>
                  <div v-if="selectedFile" class="file-info">
                    <span class="file-name">{{ selectedFile.name }}</span>
                    <span class="file-type">({{ getFileType(selectedFile.name) }})</span>
                    <span class="file-size">({{ formatFileSize(selectedFile.size) }})</span>
                    <button @click="removeFile" class="remove-file">×</button>
                  </div>
                </div>
              </div>

              <!-- 解析按钮 -->
              <div class="action-buttons">
                <button 
                  @click="parseFile" 
                  :disabled="!selectedFile || bulkParsing"
                  class="parse-btn"
                  :class="{ 'disabled': !selectedFile || bulkParsing }"
                >
                  {{ bulkParsing ? '解析中...' : '解析文件' }}
                </button>
              </div>
            </div>
          </div>

          <!-- 数据预览 -->
          <div v-if="parsedData.length > 0" class="preview-section">
            <div class="preview-card">
              <h3 class="card-title">数据预览</h3>
              <p class="preview-desc">共 {{ parsedData.length }} 条记录，其中有效数据 {{ validDataCount }} 条</p>
              
              <!-- 错误信息展示 -->
              <div v-if="importErrors.length > 0" class="import-errors">
                <div class="error-summary">
                  <span class="error-icon">⚠️</span>
                  <span class="error-text">发现 {{ importErrors.length }} 个错误（这些数据将不会被导入）</span>
                </div>
                
                <div class="error-details">
                  <div class="error-item" v-for="(error, index) in importErrors" :key="index">
                    <span class="error-row">第 {{ error.row }} 行:</span>
                    <span class="error-course">课程 {{ error.course_name }} (ID: {{ error.course_id }})</span>
                    <span class="error-message">{{ error.error }}</span>
                  </div>
                </div>
              </div>
              
              <div class="table-container">
                <table class="data-table">
                  <thead>
                    <tr>
                      <th>行号</th>
                      <th>学号</th>
                      <th>姓名</th>
                      <th>课程ID</th>
                      <th>课程名称</th>
                      <th>成绩</th>
                      <th>学期</th>
                      <th>操作类型</th>
                      <th>状态</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(item, index) in parsedData" :key="index" 
                        :class="getOperationTypeClass(item.operationType)">
                      <td>{{ index + 1 }}</td>
                      <td>{{ item.student_id }}</td>
                      <td>{{ item.student_name }}</td>
                      <td>{{ item.course_id }}</td>
                      <td>{{ item.course_name }}</td>
                      <td :class="getGradeClass(item.score)">{{ item.score }}</td>
                      <td>{{ item.semester_name }}</td>
                      <td>
                        <span class="operation-badge" :class="item.operationType">
                          {{ item.operationType === 'update' ? '更新' : '新增' }}
                        </span>
                      </td>
                      <td>
                        <span v-if="hasError(item.row)" class="error-badge">错误</span>
                        <span v-else class="valid-badge">有效</span>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <!-- 提交按钮 -->
              <div class="action-buttons">
                <button 
                  @click="submitBulkData" 
                  :disabled="bulkSubmitting || validDataCount === 0"
                  class="submit-btn"
                  :class="{ 
                    'disabled': bulkSubmitting || validDataCount === 0,
                  }"
                  :title="validDataCount === 0 ? '没有有效数据可提交' : ''"
                >
                  {{ bulkSubmitting ? '提交中...' : '提交有效数据' }}
                </button>
              </div>
            </div>
          </div>

          <!-- 导入结果 -->
          <div v-if="importResult" class="result-section">
            <div class="result-card">
              <h3 class="card-title">导入结果</h3>
              
              <div class="result-summary">
                <div class="summary-item success">
                  <span class="summary-label">成功导入</span>
                  <span class="summary-value">{{ importResult.successCount }}/{{ validDataCount }} 条</span>
                </div>
                <div class="summary-item error">
                  <span class="summary-label">导入失败</span>
                  <span class="summary-value">{{ importResult.errors.length }}/{{ validDataCount }} 条</span>
                </div>
                <div class="summary-item skipped">
                  <span class="summary-label">跳过无效数据</span>
                  <span class="summary-value">{{ importErrors.length }} 条</span>
                </div>
              </div>

              <!-- 错误详情 -->
              <div v-if="importResult.errors.length > 0" class="error-details">
                <h4 class="error-title">导入失败详情</h4>
                <div class="table-container">
                  <table class="data-table">
                    <thead>
                      <tr>
                        <th>行号</th>
                        <th>学号</th>
                        <th>课程ID</th>
                        <th>学期</th>
                        <th>错误信息</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="(error, index) in importResult.errors" :key="index">
                        <td>{{ error.row }}</td>
                        <td>{{ error.student_id }}</td>
                        <td>{{ error.course_id }}</td>
                        <td>{{ error.semester_name }}</td>
                        <td class="error-message-cell">{{ error.error }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
              
              <!-- 成功详情 -->
              <div v-if="importResult.successCount > 0" class="success-details">
                <h4 class="success-title">成功导入 {{ importResult.successCount }} 条记录</h4>
                <p class="success-hint">数据已成功更新到系统</p>
              </div>
              
              <div class="action-buttons">
                <button @click="closeBulkImport" class="close-btn">
                  关闭
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
import { ref, computed, watch, nextTick, onMounted } from 'vue'
import axios from 'axios'
import * as XLSX from 'xlsx'
import apiConfig from '@/config/apiConfig'

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
const emit = defineEmits(['update:errorMessage', 'clear-error'])

// 响应式数据
const rawData = ref([])
const loading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const currentQueryType = ref('teaching') // 默认显示授课查询

// 筛选条件
const filters = ref({
  selectedClass: '',
  selectedCourse: '',
  studentSearch: '',
  gradeRange: ''
})

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

// 批量导入相关状态
const showBulkImport = ref(false)
const selectedFile = ref(null)
const parsedData = ref([])
const importResult = ref(null)
const bulkLoading = ref(false)
const bulkParsing = ref(false)
const bulkSubmitting = ref(false)
const isDragOver = ref(false)
const bulkErrorMessage = ref('')
const bulkSuccessMessage = ref('')
const bulkLoadingText = ref('正在加载...')
const fileInput = ref(null)
const importErrors = ref([]) // 存储导入错误信息
const skipInvalidRows = ref(false) // 是否跳过无效行

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
      student.average_grade = studentTotalGrade / student.courses.length
      
      // 累加班级总分和课程数
      totalGrade += studentTotalGrade
      totalCourses += student.courses.length
    })
    
    // 计算班级平均分
    classItem.average_grade = totalCourses > 0 ? totalGrade / totalCourses : 0
    
    return classItem
  })
})

// 计算属性 - 处理授课数据
const teachingData = computed(() => {
  if (currentQueryType.value !== 'teaching' || !rawData.value.length) return []
  
  return rawData.value.map(course => {
    // 计算课程平均分
    const totalGrade = course.students.reduce((sum, student) => sum + student.grade, 0)
    course.average_grade = course.students.length > 0 ? totalGrade / course.students.length : 0
    
    return course
  })
})

// 计算属性 - 筛选后的班级数据
const filteredClassData = computed(() => {
  if (!classData.value.length) return []
  
  return classData.value
    .filter(classItem => {
      // 班级筛选
      if (filters.value.selectedClass && classItem.class_id !== filters.value.selectedClass) {
        return false
      }
      
      // 学生搜索筛选
      if (filters.value.studentSearch) {
        const searchLower = filters.value.studentSearch.toLowerCase()
        const hasMatchingStudent = classItem.students.some(student => 
          student.student_name.toLowerCase().includes(searchLower) ||
          student.student_id.toString().includes(searchLower)
        )
        
        if (!hasMatchingStudent) return false
      }
      
      // 成绩范围筛选
      if (filters.value.gradeRange) {
        const [min, max] = filters.value.gradeRange.split('-').map(Number)
        if (classItem.average_grade < min || classItem.average_grade > max) {
          return false
        }
      }
      
      return true
    })
    .map(classItem => {
      // 筛选学生
      const filteredStudents = classItem.students.filter(student => {
        // 学生搜索筛选
        if (filters.value.studentSearch) {
          const searchLower = filters.value.studentSearch.toLowerCase()
          const nameMatch = student.student_name.toLowerCase().includes(searchLower)
          const idMatch = student.student_id.toString().includes(searchLower)
          if (!nameMatch && !idMatch) return false
        }
        
        // 成绩范围筛选
        if (filters.value.gradeRange) {
          const [min, max] = filters.value.gradeRange.split('-').map(Number)
          if (student.average_grade < min || student.average_grade > max) {
            return false
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

// 计算属性 - 筛选后的授课数据
const filteredTeachingData = computed(() => {
  if (!teachingData.value.length) return []
  
  return teachingData.value
    .filter(course => {
      // 课程筛选
      if (filters.value.selectedCourse && course.course_id !== filters.value.selectedCourse) {
        return false
      }
      
      // 学生搜索筛选
      if (filters.value.studentSearch) {
        const searchLower = filters.value.studentSearch.toLowerCase()
        const hasMatchingStudent = course.students.some(student => 
          student.student_name.toLowerCase().includes(searchLower) ||
          student.student_id.toString().includes(searchLower)
        )
        
        if (!hasMatchingStudent) return false
      }
      
      // 成绩范围筛选
      if (filters.value.gradeRange) {
        const [min, max] = filters.value.gradeRange.split('-').map(Number)
        if (course.average_grade < min || course.average_grade > max) {
          return false
        }
      }
      
      return true
    })
    .map(course => {
      // 筛选学生
      const filteredStudents = course.students.filter(student => {
        // 学生搜索筛选
        if (filters.value.studentSearch) {
          const searchLower = filters.value.studentSearch.toLowerCase()
          const nameMatch = student.student_name.toLowerCase().includes(searchLower)
          const idMatch = student.student_id.toString().includes(searchLower)
          if (!nameMatch && !idMatch) return false
        }
        
        // 成绩范围筛选
        if (filters.value.gradeRange) {
          const [min, max] = filters.value.gradeRange.split('-').map(Number)
          if (student.grade < min || student.grade > max) {
            return false
          }
        }
        
        return true
      })
      
      return {
        ...course,
        students: filteredStudents
      }
    })
    .filter(course => course.students.length > 0) // 移除没有学生的课程
})

// 计算属性 - 可用班级列表（用于筛选）
const availableClasses = computed(() => {
  if (currentQueryType.value !== 'class' || !rawData.value.length) return []
  
  return rawData.value.map(classItem => ({
    class_id: classItem.class_id,
    class_name: classItem.class_name
  }))
})

// 计算属性 - 可用课程列表（用于筛选）
const availableCoursesForFilter = computed(() => {
  if (currentQueryType.value !== 'teaching' || !rawData.value.length) return []
  
  return rawData.value.map(course => ({
    course_id: course.course_id,
    course_name: course.course_name
  }))
})

// 计算属性 - 可用课程列表（用于新增成绩）
const availableCourses = computed(() => {
  if (currentQueryType.value !== 'class' || !rawData.value.length) return []
  
  // 获取老师本学期所教的所有课程（去重）
  const teacherCourses = new Map()
  
  // 遍历所有班级数据，收集所有课程
  rawData.value.forEach(classItem => {
    classItem.students.forEach(student => {
      student.courses.forEach(course => {
        if (!teacherCourses.has(course.course_id)) {
          teacherCourses.set(course.course_id, {
            course_id: course.course_id,
            course_name: course.course_name,
            course_type: course.course_type,
            course_teacher: course.course_teacher // 确保包含授课教师信息
          })
        }
      })
    })
  })
  
  return Array.from(teacherCourses.values())
})

// 计算属性 - 可用学生列表（用于新增成绩）
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

// 计算属性 - 有效数据数量
const validDataCount = computed(() => {
  if (!parsedData.value.length) return 0
  return parsedData.value.filter(item => !hasError(item.row)).length
})

// 检查数据行是否有错误
const hasError = (row) => {
  return importErrors.value.some(error => error.row === row)
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
  resetChanges()
  resetFilters()
  
  try {
    const token = localStorage.getItem('jwt_token')
    const response = await axios.post(apiConfig.TEACHER_API.CHECK, 
      {
        message_check: queryType,
        semester_id: props.semesterId
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
              isExpanded: false
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

// 重置筛选条件
const resetFilters = () => {
  filters.value = {
    selectedClass: '',
    selectedCourse: '',
    studentSearch: '',
    gradeRange: ''
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

// 切换课程展开状态
const toggleCourseExpansion = (courseId) => {
  const course = rawData.value.find(c => c.course_id === courseId)
  if (course) {
    course.isExpanded = !course.isExpanded
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
      semester_id: props.semesterId,
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
              course.grade = new极Value
            }
          })
        }
      })
    })
  } else {
    rawData.value.forEach(course => {
      if (course.course_id === courseId) {
        course.students.forEach(student => {
          if (student.student_id === studentId) {
            student.grade = newGradeValue
          }
        })
      }
    })
  }
  
  resetEditing()
}

// 删除成绩
const deleteGrade = async (studentId, courseId) => {
  if (!confirm('确定要删除这条成绩记录吗？')) return
  
  try {
    const token = localStorage.getItem('jwt_token')
    
    // 立即发送删除请求
    const response = await axios.post(apiConfig.TEACHER_API.UPDATE_GRADES, 
      {
        updates: [],
        deletions: [{
          student_id: studentId,
          course_id: courseId,
          semester_id: props.semesterId
        }],
        additions: []
      },
      {
        headers: { 'Authorization': `Bearer ${token}` }
      }
    )
    
    if (response.data.status === 'success') {
      // 删除成功，更新本地数据
      if (currentQueryType.value === 'class') {
        rawData.value.forEach(classItem => {
          classItem.students.forEach(student => {
            if (student.student_id === studentId) {
              student.courses = student.courses.filter(course => course.course_id !== courseId)
            }
          })
        })
      } else {
        rawData.value.forEach(course => {
          if (course.course_id === courseId) {
            course.students = course.students.filter(student => student.student_id !== studentId)
          }
        })
      }
      
      successMessage.value = '删除成功'
      setTimeout(() => { successMessage.value = '' }, 3000)
      
      // 同时从更改记录中移除相关的删除记录（如果存在）
      const deletionIndex = gradeDeletions.value.findIndex(deletion => 
        deletion.student_id === studentId && 
        deletion.course_id === courseId
      )
      if (deletionIndex !== -1) {
        gradeDeletions.value.splice(deletionIndex, 1)
      }
    } else {
      errorMessage.value = response.data.error || '删除失败'
    }
  } catch (error) {
    handleApiError(error)
  }
}

// 添加新成绩
const addNewGrade = (contextId) => {
  if (!canAddGrade(contextId)) return
  
  const newRecord = {
    student_id: currentQueryType.value === 'class' ? contextId : newGrade.value.student_id,
    course_id: currentQueryType.value === 'class' ? newGrade.value.course_id : contextId,
    semester_id: props.semesterId,
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
        if (student.student_id === contextId) {
          student.courses.push({
            course_id: newRecord.course_id,
            course_name: getCourseName(newRecord.course_id),
            course_type: getCourseType(newRecord.course_id),
            grade: newRecord.grade
          })
        }
      })
    })
  } else {
    rawData.value.forEach(course => {
      if (course.course_id === contextId) {
        course.students.push({
          student_id: newRecord.student_id,
          student_name: getStudentName(newRecord.student_id),
          class_id: getStudentClassId(newRecord.student_id),
          class_name: getStudentClass(newRecord.student_id),
          grade: newRecord.grade
        })
      }
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
const canAddGrade = (contextId) => {
  if (currentQueryType.value === 'class') {
    return newGrade.value.course_id && newGrade.value.grade !== null
  } else {
    return newGrade.value.student_id && newGrade.value.grade !== null
  }
}

// 获取课程名称
const getCourseName = (courseId) => {
  const course = availableCourses.value.find(c => c.course_id === courseId)
  return course ? course.course_name : '未知课程'
}

// 获取课程类型
const getCourseType = (courseId) => {
  const course = availableCourses.value.find(c => c.course_id === courseId)
  return course ? course.course_type : '未知类型'
}

// 获取学生姓名
const getStudentName = (studentId) => {
  const student = availableStudents.value.find(s => s.student_id === studentId)
  return student ? student.student_name : '未知学生'
}

// 获取学生班级
const getStudentClass = (studentId) => {
  const student = availableStudents.value.find(s => s.student_id === studentId)
  return student ? student.class_name : '未知班级'
}

// 获取学生班级ID
const getStudentClassId = (studentId) => {
  // 在实际应用中，这里应该从学生数据中获取班级ID
  return 1 // 简化处理
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
        headers: { 'Authorization': `Bearer ${极}` }
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

// 组件挂载时自动查询数据
onMounted(() => {
  if (props.semesterId) {
    handleQuery('teaching')
  }
})

// 监听学期ID变化
watch(() => props.semesterId, (newVal) => {
  if (newVal) {
    handleQuery(currentQueryType.value || 'teaching')
  } else {
    // 学期ID为空时清空数据
    rawData.value = []
    currentQueryType.value = 'teaching'
    resetChanges()
    resetFilters()
  }
}, { immediate: true })

// ==================== 批量导入功能 ====================

// 获取文件类型
const getFileType = (fileName) => {
  const extension = fileName.split('.').pop().toLowerCase()
  if (['xlsx', 'xls'].includes(extension)) {
    return 'Excel文件'
  } else if (extension === 'csv') {
    return 'CSV文件'
  } else {
    return '未知文件'
  }
}

// 触发文件选择
const triggerFileInput = () => {
  if (fileInput.value) {
    fileInput.value.click()
  }
}

// 处理文件选择
const handleFileSelect = (event) => {
  const file = event.target.files[0]
  if (file) {
    const fileExtension = file.name.split('.').pop().toLowerCase()
    if (['xlsx', 'xls', 'csv'].includes(fileExtension)) {
      selectedFile.value = file
      parsedData.value = []
      importResult.value = null
      bulkErrorMessage.value = ''
      bulkSuccessMessage.value = ''
      importErrors.value = [] // 清空错误列表
    } else {
      showBulkError('请上传Excel或CSV文件（.xlsx, .xls, .csv 格式）')
    }
  }
  
  // 重置input值，允许重复选择同一文件
  event.target.value = ''
}

// 移除文件
const removeFile = () => {
  selectedFile.value = null
  parsedData.value = []
  importResult.value = null
  importErrors.value = [] // 清空错误列表
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

// 处理拖拽
const handleDragOver = (event) => {
  event.preventDefault()
  isDragOver.value = true
}

const handleDragLeave = (event) => {
  event.preventDefault()
  isDragOver.value = false
}

const handleDrop = (event) => {
  event.preventDefault()
  isDragOver.value = false
  
  const files = event.dataTransfer.files
  if (files.length > 0) {
    const file = files[0]
    const fileExtension = file.name.split('.').pop().toLowerCase()
    if (['xlsx', 'xls', 'csv'].includes(fileExtension)) {
      selectedFile.value = file
      parsedData.value = []
      importResult.value = null
      bulkErrorMessage.value = ''
      bulkSuccessMessage.value = ''
      importErrors.value = [] // 清空错误列表
    } else {
      showBulkError('请上传Excel或CSV文件（.xlsx, .xls, .csv 格式）')
    }
  }
}

// 格式化文件大小
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 下载模板 - 基于UPDATE_GRADES接口所需参数
const downloadTemplate = (type) => {
  // 基于UPDATE_GRADES接口参数创建模板
  const templateData = [
    {
      student_id: '1001',
      student_name: '张三',
      course_id: '3',
      course_name: '概率论与数理统计',
      score: '91',
      semester_name: props.semesterInfo?.semester_name || '2025-2026学年第二学期'
    },
    {
      student_id: '1002',
      student_name: '李四',
      course_id: '5',
      course_name: '高等数学',
      score: '85',
      semester_name: props.semesterInfo?.semester_name || '2025-2026学年第二学期'
    }
  ]

  if (type === 'excel') {
    const worksheet = XLSX.utils.json_to_sheet(templateData)
    const workbook = XLSX.utils.book_new()
    XLSX.utils.book_append_sheet(workbook, worksheet, '成绩模板')
    XLSX.writeFile(workbook, '成绩导入模板.xlsx')
  } else if (type === 'csv') {
    // 创建CSV内容
    const headers = ['student_id', 'student_name', 'course_id', 'course_name', 'score', 'semester_name']
    const csvContent = [
      headers.join(','), // 表头
      ...templateData.map(row => headers.map(header => row[header]).join(','))
    ].join('\n')
    
    // 创建Blob并下载
    const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    const url = URL.createObjectURL(blob)
    link.setAttribute('href', url)
    link.setAttribute('download', '成绩导入模板.csv')
    link.style.visibility = 'hidden'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }
}

// 获取当前教师所授课程的ID列表
const getTeacherCourseIds = () => {
  if (!rawData.value || rawData.value.length === 0) {
    return []
  }
  
  const courseIds = rawData.value.map(course => String(course.course_id))
  console.log('当前教师所授课程ID列表:', courseIds)
  return courseIds
}

// 解析文件
const parseFile = async () => {
  if (!selectedFile.value) {
    showBulkError('请先选择文件')
    return
  }

  // 检查是否有查询数据
  if (!rawData.value || rawData.value.length === 0) {
    showBulkError('请先查询授课数据，确保有课程数据后再进行批量导入')
    return
  }

  bulkParsing.value = true
  bulkErrorMessage.value = ''
  importErrors.value = [] // 清空错误列表
  importResult.value = null // 清空导入结果
  
  try {
    const fileExtension = selectedFile.value.name.split('.').pop().toLowerCase()
    let data
    
    if (fileExtension === 'csv') {
      data = await readCSVFile(selectedFile.value)
    } else {
      data = await readExcelFile(selectedFile.value)
    }
    
    // 验证数据格式并收集错误
    const validatedData = validateAndTransformData(data)
    
    // 验证课程ID是否在教师所授课程中
    const teacherCourseIds = getTeacherCourseIds()
    
    // 检查课程是否在教师授课范围内
    validatedData.forEach((item, index) => {
      if (!teacherCourseIds.includes(String(item.course_id))) {
        importErrors.value.push({
          row: index + 2, // Excel行号从2开始（表头+1）
          student_id: item.student_id,
          student_name: item.student_name,
          course_id: item.course_id,
          course_name: item.course_name,
          error: `课程不在您的授课范围内`
        })
      }
    })
    
    // 为每条数据判断操作类型（更新或新增）
    const processedData = await determineOperationType(validatedData)
    
    // 为每条数据添加行号
    processedData.forEach((item, index) => {
      item.row = index + 2
    })
    
    parsedData.value = processedData
    
    bulkSuccessMessage.value = `成功解析 ${data.length} 条记录，发现 ${importErrors.value.length} 个错误`
  } catch (error) {
    console.error('解析文件失败:', error)
    showBulkError(`解析文件失败: ${error.message}`)
  } finally {
    bulkParsing.value = false
  }
}

// 读取Excel文件
const readExcelFile = (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    
    reader.onload = (e) => {
      try {
        const data = new Uint8Array(e.target.result)
        const workbook = XLSX.read(data, { type: 'array' })
        const firstSheetName = workbook.SheetNames[0]
        const worksheet = workbook.Sheets[firstSheetName]
        const jsonData = XLSX.utils.sheet_to_json(worksheet)
        
        // 验证数据格式
        const validatedData = validateAndTransformData(jsonData)
        resolve(validatedData)
      } catch (error) {
        reject(error)
      }
    }
    
    reader.onerror = () => reject(new Error('文件读取失败'))
    reader.readAsArrayBuffer(file)
  })
}

// 读取CSV文件
const readCSVFile = (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    
    reader.onload = (e) => {
      try {
        const csvData = e.target.result
        const workbook = XLSX.read(csvData, { 
          type: 'string',
          codepage: 65001 // UTF-8
        })
        const firstSheetName = workbook.SheetNames[0]
        const worksheet = workbook.Sheets[firstSheetName]
        const jsonData = XLSX.utils.sheet_to_json(worksheet)
        
        // 验证数据格式
        const validatedData = validateAndTransformData(jsonData)
        resolve(validatedData)
      } catch (error) {
        reject(error)
      }
    }
    
    reader.onerror = () => reject(new Error('CSV文件读取失败'))
    reader.readAsText(file, 'UTF-8')
  })
}

// 验证和转换数据
const validateAndTransformData = (jsonData) => {
  return jsonData.map((item, index) => {
    const requiredFields = ['student_id', 'student_name', 'course_id', 'course_name', 'score', 'semester_name']
    const missingFields = requiredFields.filter(field => !item[field] && item[field] !== 0)
    
    if (missingFields.length > 0) {
      // 收集错误而不是抛出异常
      importErrors.value.push({
        row: index + 2,
        student_id: item.student_id || '',
        student_name: item.student_name || '',
        course_id: item.course_id || '',
        course_name: item.course_name || '',
        error: `缺少必要字段: ${missingFields.join(', ')}`
      })
    }
    
    // 验证成绩格式
    let score = null
    if (item.score !== undefined && item.score !== null) {
      score = parseFloat(item.score)
      if (isNaN(score) || score < 0 || score > 100) {
        importErrors.value.push({
          row: index + 2,
          student_id: item.student_id || '',
          student_name: item.student_name || '',
          course_id: item.course_id || '',
          course_name: item.course_name || '',
          error: `成绩格式错误: 必须在0-100之间`
        })
      }
    }
    
    return {
      student_id: String(item.student_id || ''),
      student_name: String(item.student_name || ''),
      course_id: String(item.course_id || ''),
      course_name: String(item.course_name || ''),
      score: score,
      semester_name: String(item.semester_name || ''),
      semester_id: props.semesterId // 添加学期ID
    }
  })
}

// 判断操作类型（更新或新增）- 使用前端已有数据进行比较
const determineOperationType = async (data) => {
  // 使用前端已有的rawData进行判断，避免重复请求
  const currentGrades = getCurrentGradesFromRawData()
  
  return data.map(item => {
    // 检查该学生在该课程下是否已有成绩记录（不考虑成绩值）
    // 使用学生ID、课程ID和学期ID三个字段来判断
    const existingRecord = currentGrades.find(grade => 
      String(grade.student_id) === String(item.student_id) && 
      String(grade.course_id) === String(item.course_id) &&
      Number(grade.semester_id) === Number(props.semesterId)
    )
    
    console.log('判断操作类型:', {
      学生ID: item.student_id,
      课程ID: item.course_id,
      学期ID: props.semesterId,
      是否存在: !!existingRecord,
      操作类型: existingRecord ? 'update' : 'add'
    })
    
    return {
      ...item,
      operationType: existingRecord ? 'update' : 'add'
    }
  })
}

// 从rawData中获取当前成绩数据
const getCurrentGradesFromRawData = () => {
  const grades = []
  
  if (rawData.value && rawData.value.length > 0) {
    console.log('从rawData获取成绩数据，课程数量:', rawData.value.length)
    
    // 遍历所有课程数据
    rawData.value.forEach(course => {
      console.log(`课程 ${course.course_id} (${course.course_name}) 有 ${course.students.length} 名学生`)
      
      // 遍历每个课程的学生成绩
      course.students.forEach(student => {
        grades.push({
          student_id: String(student.student_id),
          course_id: String(course.course_id),
          semester_id: Number(props.semesterId),
          grade: student.grade
        })
        
        console.log(`学生 ${student.student_id} 在课程 ${course.course_id} 的成绩: ${student.grade}`)
      })
    })
  } else {
    console.log('rawData为空或没有数据')
  }
  
  console.log('获取到的成绩记录总数:', grades.length)
  return grades
}

// 获取操作类型样式
const getOperationTypeClass = (operationType) => {
  return operationType === 'update' ? 'update-row' : 'add-row'
}

// 提交批量数据
const submitBulkData = async () => {
  if (validDataCount.value === 0) return

  bulkSubmitting.value = true
  bulkLoading.value = true
  bulkLoadingText.value = '正在提交数据...'
  bulkErrorMessage.value = ''
  bulkSuccessMessage.value = ''

  try {
    const token = localStorage.getItem('jwt_token')
    if (!token) {
      throw new Error('未找到认证令牌，请重新登录')
    }

    // 过滤掉有错误的数据
    const validData = parsedData.value.filter(item => !hasError(item.row))
    
    // 分离更新和新增的数据 - 基于UPDATE_GRADES接口参数
    const updates = validData
      .filter(item => item.operationType === 'update' && item.score !== null)
      .map(item => ({
        student_id: String(item.student_id),
        course_id: String(item.course_id),
        semester_id: Number(props.semesterId),
        grade: Number(item.score)
      }))

    const additions = validData
      .filter(item => item.operationType === 'add' && item.score !== null)
      .map(item => ({
        student_id: String(item.student_id),
        course_id: String(item.course_id),
        semester_id: Number(props.semesterId),
        grade: Number(item.score)
      }))

    console.log('批量导入数据统计:', {
      更新记录数: updates.length,
      更新记录: updates,
      新增记录数: additions.length,
      新增记录: additions,
      总记录数: validData.length
    })

    // 使用现有的更新成绩接口
    const response = await axios.post(apiConfig.TEACHER_API.UPDATE_GRADES, 
      {
        updates: updates,
        deletions: [],
        additions: additions
      },
      {
        headers: { 
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      }
    )

    console.log('批量导入响应:', response.data)

    if (response.data.status === 'success') {
      // 处理导入结果
      const successCount = updates.length + additions.length
      const errors = response.data.errors || []
      
      importResult.value = {
        successCount: successCount - errors.length,
        errors: errors.map(error => ({
          row: error.row || 0,
          student_id: error.student_id || '',
          course_id: error.course_id || '',
          semester_name: props.semesterInfo?.semester_name || '',
          error: error.error || '未知错误'
        }))
      }
      
      if (errors.length === 0) {
        bulkSuccessMessage.value = `全部导入成功！成功导入 ${successCount} 条记录`
        // 成功后刷新数据
        handleQuery('teaching')
      } else if (successCount - errors.length > 0) {
        bulkSuccessMessage.value = `部分导入成功！成功导入 ${successCount - errors.length}/${successCount} 条记录`
        // 部分成功后刷新数据
        handleQuery('teaching')
      } else {
        showBulkError(`导入失败！所有 ${successCount} 条记录均未成功导入`)
      }
    } else {
      throw new Error(response.data.error || '导入失败')
    }
  } catch (error) {
    console.error('提交数据失败:', error)
    handleBulkApiError(error)
  } finally {
    bulkSubmitting.value = false
    bulkLoading.value = false
  }
}

// 批量导入的API错误处理
const handleBulkApiError = (error) => {
  if (error.response) {
    const status = error.response.status
    const data = error.response.data
    
    switch (status) {
      case 401:
        if (data.error === '未提供token') {
          showBulkError('认证失败：未提供访问令牌')
        } else if (data.error === 'Token已过期') {
          showBulkError('认证失败：令牌已过期，请重新登录')
        } else if (data.error === '无效的Token') {
          showBulkError('认证失败：无效的令牌')
        } else if (data.error === 'Token解析错误') {
          showBulkError('认证失败：令牌解析错误')
        } else {
          showBulkError('认证失败：请重新登录')
        }
        break
      case 403:
        showBulkError('权限不足：仅限教师用户进行批量导入')
        break
      case 400:
        showBulkError(`请求错误：${data.error || '数据格式不正确'}`)
        break
      case 404:
        showBulkError('接口不存在：请检查后端服务是否正常运行')
        break
      case 500:
        showBulkError('服务器错误：批量导入失败，请稍后重试')
        break
      default:
        showBulkError(`导入失败: ${status} ${data?.error || error.message}`)
    }
  } else if (error.code === 'NETWORK_ERROR' || error.message.includes('Network Error')) {
    showBulkError('网络错误：无法连接到后端服务，请检查：\n1. 后端服务是否启动\n2. 端口号是否正确\n3. 网络连接是否正常')
  } else if (error.request) {
    showBulkError('网络错误：无法连接到服务器，请检查后端服务是否运行')
  } else {
    showBulkError(`导入失败: ${error.message}`)
  }
}

// 关闭批量导入模态框
const closeBulkImport = () => {
  showBulkImport.value = false
  // 重置批量导入状态
  selectedFile.value = null
  parsedData.value = []
  importResult.value = null
  bulkErrorMessage.value = ''
  bulkSuccessMessage.value = ''
  importErrors.value = [] // 清空错误列表
}

// 显示批量导入错误信息
const showBulkError = (message) => {
  bulkErrorMessage.value = message
  setTimeout(() => {
    if (bulkErrorMessage.value === message) {
      bulkErrorMessage.value = ''
    }
  }, 5000)
}

// 清除批量导入错误信息
const clearBulkError = () => {
  bulkErrorMessage.value = ''
}

// 清除批量导入成功信息
const clearBulkSuccess = () => {
  bulkSuccessMessage.value = ''
}
</script>

<style scoped>
/* 添加一些新样式 */
.error-badge {
  background-color: #ffebee;
  color: #c62828;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
}

.valid-badge {
  background-color: #e8f5e9;
  color: #2e7d32;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
}

.summary-item.skipped {
  background-color: #fff3e0;
  border-left: 4px solid #ff9800;
}

.summary-item.skipped .summary-label {
  color: #ff9800;
}

.success-details {
  margin-top: 20px;
  padding: 15px;
  background-color: #e8f5e9;
  border-radius: 8px;
}

.success-title {
  color: #2e7d32;
  margin-bottom: 10px;
}

.success-hint {
  color: #4caf50;
  font-size: 14px;
}

.close-btn {
  background-color: #f5f5f5;
  color: #333;
  border: 1px solid #ddd;
  padding: 8px 20px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
}

.close-btn:hover {
  background-color: #e0e0e0;
}

.import-errors {
  background-color: #fff8f8;
  border: 1px solid #ffcccc;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 20px;
}

.error-summary {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
  font-weight: bold;
  color: #e53935;
}

.error-icon {
  margin-right: 8px;
  font-size: 18px;
}

.error-details {
  border-top: 1px solid #ffcccc;
  padding-top: 10px;
}

.error-item {
  display: flex;
  margin-bottom: 8px;
  font-size: 14px;
}

.error-row {
  font-weight: bold;
  margin-right: 10px;
  min-width: 60px;
}

.error-course {
  margin-right: 10px;
  min-width: 200px;
}

.error-message {
  color: #e53935;
}

/* 主界面样式 */
.teacher-query-container {
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

/* 加载状态样式 */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(20px);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  margin-bottom: 20px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(255, 255, 255, 0.1);
  border-left: 4px solid rgba(255, 255, 255, 0.8);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 15px;
}

.loading-container p {
  color: rgba(255, 255, 255, 0.8);
  font-size: 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
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

/* 操作区域样式 */
.operation-section {
  margin-bottom: 30px;
}

.operation-card {
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(20px);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  padding: 25px;
}

.section-title {
  color: rgba(255, 255, 255, 0.95);
  margin-bottom: 20px;
  font-size: 24px;
  text-align: center;
}

.operation-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 30px;
  margin-bottom: 25px;
}

.operation-item {
  text-align: center;
}

.card-title {
  color: rgba(255, 255, 255, 0.95);
  margin-bottom: 10px;
  font-size: 18px;
}

.operation-desc {
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 15px;
  font-size: 14px;
}

.template-buttons {
  display: flex;
  gap: 10px;
  justify-content: center;
  flex-wrap: wrap;
}

.download-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 12px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
  flex: 1;
  min-width: 120px;
}

.download-btn.csv-btn {
  background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
}

.download-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
}

.download-btn.csv-btn:hover {
  box-shadow: 0 5px 15px rgba(76, 175, 80, 0.4);
}

/* 上传区域样式 */
.upload-area {
  border: 2px dashed rgba(255, 255, 255, 0.3);
  border-radius: 12px;
  padding: 40px 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
}

.upload-area:hover,
.upload-area.drag-over {
  border-color: rgba(102, 126, 234, 0.8);
  background: rgba(102, 126, 234, 0.1);
}

.upload-content {
  pointer-events: none;
}

.upload-icon {
  font-size: 48px;
  margin-bottom: 10px;
  display: block;
}

.upload-text {
  color: rgba(255, 255, 255, 0.9);
  font-size: 16px;
  font-weight: 500;
  margin-bottom: 5px;
}

.upload-hint {
  color: rgba(255, 255, 255, 0.6);
  font-size: 12px;
}

.file-input {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  opacity: 0;
  cursor: pointer;
}

.file-info {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 15px;
  padding: 10px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  gap: 8px;
  flex-wrap: wrap;
}

.file-name {
  color: rgba(255, 255, 255, 0.9);
  font-size: 14px;
  font-weight: 500;
}

.file-type {
  color: rgba(102, 126, 234, 0.9);
  font-size: 12px;
  font-weight: 500;
}

.file-size {
  color: rgba(255, 255, 255, 0.7);
  font-size: 12px;
}

.remove-file {
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.7);
  font-size: 18px;
  cursor: pointer;
  padding: 0;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: all 0.3s ease;
}

.remove-file:hover {
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.9);
}

/* 按钮样式 */
.action-buttons {
  text-align: center;
}

.parse-btn,
.submit-btn {
  background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
  color: white;
  border: none;
  padding: 12px 30px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 500;
  transition: all 0.3s ease;
  min-width: 140px;
}

.parse-btn:hover:not(.disabled),
.submit-btn:hover:not(.disabled) {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(76, 175, 80, 0.4);
}

.parse-btn.disabled,
.submit-btn.disabled {
  background: rgba(255, 255, 255, 0.2);
  color: rgba(255, 255, 255, 0.5);
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

/* 预览区域样式 */
.preview-section,
.result-section {
  margin-bottom: 30px;
}

.preview-card,
.result-card {
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(20px);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  padding: 25px;
}

.preview-desc {
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 20px;
  text-align: center;
  font-size: 14px;
}

/* 表格样式 */
.table-container {
  overflow-x: auto;
  margin-bottom: 20px;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  background: rgba(255, 255, 255, 0.05);
}

.data-table th {
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.9);
  padding: 12px 15px;
  text-align: left;
  font-weight: 600;
  font-size: 14px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.data-table td {
  padding: 12px 15px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
}

.data-table tr:hover {
  background: rgba(255, 255, 255, 0.05);
}

.error-message-cell {
  color: #ff6b6b;
  max-width: 300px;
  word-break: break-word;
}

/* 结果汇总样式 */
.result-summary {
  display: flex;
  justify-content: center;
  gap: 30px;
  margin-bottom: 25px;
}

.summary-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
  border-radius: 12px;
  min-width: 120px;
}

.summary-item.success {
  background: rgba(76, 175, 80, 0.15);
  border: 1px solid rgba(76, 175, 80, 0.3);
}

.summary-item.error {
  background: rgba(244, 67, 54, 0.15);
  border: 1px solid rgba(244, 67, 54, 0.3);
}

.summary-label {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 8px;
}

.summary-value {
  font-size: 24px;
  font-weight: bold;
}

.summary-item.success .summary-value {
  color: #4CAF50;
}

.summary-item.error .summary-value {
  color: #f44336;
}

.error-title {
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 15px;
  font-size: 18px;
  text-align: center;
}

/* 批量导入按钮样式 */
.bulk-import-btn {
  background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%);
}

.bulk-import-btn:hover {
  background: linear-gradient(135deg, #f57c00 0%, #ef6c00 100%);
  box-shadow: 0 5px 15px rgba(245, 124, 0, 0.4);
}

/* 模态框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(5px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal-content {
  background: rgba(30, 30, 40, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  width: 100%;
  max-width: 1200px;
  max-height: 90vh;
  overflow-y: auto;
  position: relative;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 25px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.modal-header h3 {
  color: rgba(255, 255, 255, 0.95);
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

.modal-close {
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.7);
  font-size: 24px;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.modal-close:hover {
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.9);
}

/* 批量导入内容区域 */
.bulk-import-content {
  padding: 20px 25px;
  max-height: calc(90vh - 80px);
  overflow-y: auto;
}

/* 操作类型标识 */
.operation-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.operation-badge.update {
  background: rgba(255, 152, 0, 0.2);
  color: #ff9800;
  border: 1px solid rgba(255, 152, 0, 0.3);
}

.operation-badge.add {
  background: rgba(76, 175, 80, 0.2);
  color: #4CAF50;
  border: 1px solid rgba(76, 175, 80, 0.3);
}

/* 表格行样式 */
.update-row {
  background: rgba(255, 152, 0, 0.05);
}

.add-row {
  background: rgba(76, 175, 80, 0.05);
}

.update-row:hover,
.add-row:hover {
  background: rgba(255, 255, 255, 0.08);
}

/* 成绩样式 */
.grade-excellent {
  color: #4CAF50;
  font-weight: 600;
}

.grade-good {
  color: #2196F3;
  font-weight: 500;
}

.grade-pass {
  color: #FF9800;
}

.grade-fail {
  color: #f44336;
  font-weight: 500;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .modal-content {
    margin: 10px;
    max-height: 95vh;
  }
  
  .bulk-import-content {
    padding: 15px;
  }
  
  .modal-header {
    padding: 15px 20px;
  }
  
  .operation-grid {
    grid-template-columns: 1fr;
    gap: 20px;
  }
  
  .template-buttons {
    flex-direction: column;
  }
  
  .result-summary {
    flex-direction: column;
    gap: 15px;
    align-items: center;
  }
  
  .summary-item {
    width: 100%;
    max-width: 200px;
  }
  
  .data-table th,
  .data-table td {
    padding: 8px 10px;
    font-size: 12px;
  }
  
  .operation-card,
  .preview-card,
  .result-card {
    padding: 15px;
  }
}

/* 主界面特有样式（简化版） */
.controls-container {
  margin-bottom: 30px;
}

.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-stats {
  display: flex;
  gap: 20px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-number {
  font-size: 24px;
  font-weight: bold;
  color: rgba(255, 255, 255, 0.95);
}

.stat-label {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
  margin-top: 5px;
}

.query-controls {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.action-btn {
  padding: 12px 20px;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.primary-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.secondary-btn {
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
}

.filter-controls {
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(20px);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  padding: 20px;
  margin-bottom: 20px;
}

.filter-title {
  color: rgba(255, 255, 255, 0.95);
  margin-bottom: 15px;
  font-size: 16px;
}

.filter-group {
  display: flex;
  gap: 15px;
  align-items: center;
  flex-wrap: wrap;
}

.filter-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.filter-label {
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
  white-space: nowrap;
}

.filter-select,
.filter-input {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 6px;
  padding: 8px 12px;
  color: rgba(255, 255, 255, 0.9);
  font-size: 14px;
  min-width: 120px;
}

.filter-input {
  min-width: 180px;
}

.filter-reset-btn {
  margin-left: auto;
}

/* 数据展示样式 */
.data-container {
  margin-bottom: 30px;
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.results-title {
  color: rgba(255, 255, 255, 0.95);
  font-size: 20px;
  margin: 0;
}

.results-count {
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
  font-weight: normal;
}

.teaching-results-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.course-card {
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(20px);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  overflow: hidden;
}

.course-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.course-header:hover {
  background: rgba(255, 255, 255, 0.05);
}

.course-info {
  flex: 1;
}

.course-name {
  color: rgba(255, 255, 255, 0.95);
  margin: 0 0 10px 0;
  font-size: 18px;
}

.course-details {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}

.detail-item {
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
}

.course-status-container {
  display: flex;
  align-items: center;
  gap: 15px;
}

.course-status {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.status-excellent {
  background: rgba(76, 175, 80, 0.2);
  color: #4CAF50;
  border: 1px solid rgba(76, 175, 80, 0.3);
}

.status-good {
  background: rgba(33, 150, 243, 0.2);
  color: #2196F3;
  border: 1px solid rgba(33, 150, 243, 0.3);
}

.status-pass {
  background: rgba(255, 152, 0, 0.2);
  color: #FF9800;
  border: 1px solid rgba(255, 152, 0, 0.3);
}

.status-fail {
  background: rgba(244, 67, 54, 0.2);
  color: #f44336;
  border: 1px solid rgba(244, 67, 54, 0.3);
}

.collapse-icon {
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
}

.students-table-container {
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  padding: 0;
}

.students-table {
  width: 100%;
  border-collapse: collapse;
}

.students-table th {
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.9);
  padding: 12px 15px;
  text-align: left;
  font-weight: 600;
  font-size: 14px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.students-table td {
  padding: 12px 15px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
}

.students-table tr:hover {
  background: rgba(255, 255, 255, 0.05);
}

.grade-input {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  padding: 4px 8px;
  color: rgba(255, 255, 255, 0.9);
  width: 60px;
  text-align: center;
}

.student-select {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  padding: 4px 8px;
  color: rgba(255, 255, 255, 0.9);
  width: 100%;
}

.add-grade-row {
  background: rgba(76, 175, 80, 0.05);
}

.add-grade-row:hover {
  background: rgba(76, 175, 80, 0.1);
}

.delete-btn {
  background: rgba(244, 67, 54, 0.2);
  color: #f44336;
  border: 1px solid rgba(244, 67, 54, 0.3);
  padding: 6px 10px;
  border-radius: 4px;
  cursor: pointer;
}

.delete-btn:hover {
  background: rgba(244, 67, 54, 0.3);
}

.add-btn {
  background: rgba(76, 175, 80, 0.2);
  color: #4CAF50;
  border: 1px solid rgba(76, 175, 80, 0.3);
  padding: 6px 10px;
  border-radius: 4px;
  cursor: pointer;
}

.add-btn:hover:not(:disabled) {
  background: rgba(76, 175, 80, 0.3);
}

.add-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 无数据提示 */
.no-data-container {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 60px 20px;
}

.no-data-content {
  text-align: center;
  max-width: 400px;
}

.no-data-icon {
  font-size: 64px;
  margin-bottom: 20px;
  display: block;
}

.no-data-content h3 {
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 10px;
  font-size: 20px;
}

.no-data-content p {
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 20px;
  font-size: 14px;
}

.no-data-action-btn {
  padding: 10px 20px;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.2);
  cursor: pointer;
  font-size: 14px;
}

.no-data-action-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

/* 提交容器 */
.submit-container {
  position: sticky;
  bottom: 20px;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 15px;
  padding: 15px;
  background: rgba(30, 30, 40, 0.9);
  backdrop-filter: blur(20px);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  margin-top: 20px;
}

.submit-btn {
  background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
  color: white;
  border: none;
  padding: 12px 30px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.submit-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(76, 175, 80, 0.4);
}

.changes-count {
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header-section {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .header-stats {
    width: 100%;
    justify-content: space-around;
  }
  
  .query-controls {
    flex-direction: column;
  }
  
  .filter-group {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .filter-item {
    width: 100%;
    justify-content: space-between;
  }
  
  .filter-select,
  .filter-input {
    min-width: auto;
    flex: 1;
  }
  
  .filter-reset-btn {
    margin-left: 0;
    width: 100%;
  }
  
  .course-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .course-status-container {
    width: 100%;
    justify-content: space-between;
  }
  
  .course-details {
    flex-direction: column;
    gap: 8px;
  }
  
  .students-table {
    font-size: 12px;
  }
  
  .students-table th,
  .students-table td {
    padding: 8px 10px;
  }
  
  .submit-container {
    flex-direction: column;
    text-align: center;
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
  background: rgba(102, 126, 234, 0.5) !important;}
</style>