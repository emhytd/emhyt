<template>
  <div class="admin-class-container">
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
      <p>正在加载班级数据...</p>
    </div>
    
    <!-- 控制区域 -->
    <div class="controls-container">
      <div class="header-section">
        <h2 class="section-title">
          <span class="title-icon">🏫</span>
          班级信息管理
        </h2>
        <div class="header-stats">
          <div class="stat-item">
            <span class="stat-number">{{ filteredClassData.length }}</span>
            <span class="stat-label">筛选结果</span>
          </div>
          <div class="stat-item">
            <span class="stat-number">{{ totalClasses }}</span>
            <span class="stat-label">总班级数</span>
          </div>
          <div class="stat-item">
            <span class="stat-number">{{ totalStudents }}</span>
            <span class="stat-label">总学生数</span>
          </div>
        </div>
      </div>
      
      <!-- 筛选控制区域 -->
      <div class="filter-controls">
        <div class="filter-group">
          <!-- 班级名称搜索 -->
          <div class="filter-item">
            <label class="filter-label">搜索:</label>
            <input 
              type="text" 
              v-model="filters.search" 
              placeholder="输入班级名称" 
              class="filter-input"
            >
          </div>
          
          <!-- 班主任筛选 -->
          <div class="filter-item">
            <label class="filter-label">班主任:</label>
            <select v-model="filters.teacher" class="filter-select">
              <option value="">全部班主任</option>
              <option 
                v-for="teacher in availableTeachers" 
                :key="teacher.teacher_id" 
                :value="teacher.teacher_id"
              >
                {{ teacher.teacher_name }} ({{ teacher.teacher_title }})
              </option>
            </select>
          </div>
          
          <!-- 学期筛选 -->
          <div class="filter-item">
            <label class="filter-label">学期:</label>
            <select v-model="filters.semester" class="filter-select">
              <option value="">全部学期</option>
              <option 
                v-for="semester in availableSemesters" 
                :key="semester.semester_id" 
                :value="semester.semester_id"
              >
                {{ semester.semester_name }}
              </option>
            </select>
          </div>
          
          <!-- 重置筛选按钮 -->
          <button @click="resetFilters" class="filter-reset-btn">
            重置筛选
          </button>
        </div>
      </div>
      
      <div class="actions-bar">
        <!-- 添加班级按钮 -->
        <button 
          @click="openAddClassDialog"
          class="action-btn primary-btn add-class-btn"
        >
          <span class="btn-icon">➕</span>
          添加班级
          <span class="btn-badge">NEW</span>
        </button>
        
        <div class="action-group">
          <button 
            @click="refreshData"
            class="action-btn secondary-btn"
            :disabled="loading"
          >
            <span class="btn-icon">🔄</span>
            刷新数据
          </button>
          
          <!-- 导出按钮 -->
          <button 
            @click="exportData"
            class="action-btn secondary-btn"
            :disabled="filteredClassData.length === 0"
          >
            <span class="btn-icon">📤</span>
            导出数据
          </button>
        </div>
      </div>
    </div>
    
    <!-- 数据展示区域 -->
    <div v-if="filteredClassData.length > 0 && !loading" class="data-container">
      <div class="results-header">
        <h3 class="results-title">
          班级信息总览
          <span class="results-count">(共 {{ filteredClassData.length }} 个班级)</span>
        </h3>
      </div>
      
      <div class="table-container">
        <table class="teachers-table">
          <thead>
            <tr>
              <th>班级ID</th>
              <th>班级名称</th>
              <th>学生人数</th>
              <th>班主任</th>
              <th>学期</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="classItem in filteredClassData" :key="classItem.class_id">
              <td>{{ classItem.class_id }}</td>
              <td>
                <span v-if="!isEditing(classItem.class_id)" class="teacher-name">
                  {{ classItem.class_name }}
                </span>
                <input 
                  v-else
                  type="text"
                  v-model="editingClass.class_name"
                  class="edit-input"
                >
              </td>
              <td>
                <span v-if="!isEditing(classItem.class_id)">{{ classItem.student_count }}</span>
                <input 
                  v-else
                  type="number"
                  v-model="editingClass.student_count"
                  class="edit-input"
                  min="0"
                >
              </td>
              <td>
                <span v-if="!isEditing(classItem.class_id)">
                  {{ classItem.teacher_name || '未分配' }}
                </span>
                <select 
                  v-else
                  v-model="editingClass.teacher_id"
                  class="edit-select"
                >
                  <option value="">未分配</option>
                  <option 
                    v-for="teacher in availableTeachers" 
                    :key="teacher.teacher_id" 
                    :value="teacher.teacher_id"
                  >
                    {{ teacher.teacher_name }} ({{ teacher.teacher_title }})
                  </option>
                </select>
              </td>
              <td>
                <span v-if="!isEditing(classItem.class_id)">
                  {{ getSemesterName(classItem.semester_id) }}
                </span>
                <select 
                  v-else
                  v-model="editingClass.semester_id"
                  class="edit-select"
                >
                  <option 
                    v-for="semester in availableSemesters" 
                    :key="semester.semester_id" 
                    :value="semester.semester_id"
                  >
                    {{ semester.semester_name }}
                  </option>
                </select>
              </td>
              <td>
                <div class="action-buttons">
                  <button 
                    v-if="!isEditing(classItem.class_id)"
                    @click="startEdit(classItem)"
                    class="icon-btn edit-btn"
                    title="编辑班级信息"
                  >
                    ✏️
                  </button>
                  <button 
                    v-else
                    @click="saveEdit"
                    class="icon-btn save-btn"
                    title="保存修改"
                  >
                    💾
                  </button>
                  <button 
                    v-if="!isEditing(classItem.class_id)"
                    @click="showDetailDialog(classItem)"
                    class="icon-btn view-btn"
                    title="查看详情"
                  >
                    👁️
                  </button>
                  <button 
                    v-if="!isEditing(classItem.class_id)"
                    @click="deleteClass(classItem)"
                    class="icon-btn delete-btn"
                    title="删除班级"
                  >
                    🗑️
                  </button>
                  <button 
                    v-else
                    @click="cancelEdit"
                    class="icon-btn cancel-btn"
                    title="取消编辑"
                  >
                    ❌
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    
    <!-- 无数据提示 -->
    <div v-if="filteredClassData.length === 0 && !loading" class="no-data-container">
      <div class="no-data-content">
        <div class="no-data-icon">🏫</div>
        <h3 v-if="classData.length === 0">暂无班级数据</h3>
        <h3 v-else>没有找到匹配的班级</h3>
        <p v-if="classData.length === 0">还没有添加任何班级信息，点击下方按钮开始添加</p>
        <p v-else>当前筛选条件下没有找到匹配的班级，请尝试调整筛选条件</p>
        <div class="no-data-actions">
          <button 
            @click="openAddClassDialog"
            class="no-data-action-btn"
          >
            <span class="btn-icon">➕</span>
            添加班级
          </button>
          <button 
            v-if="classData.length > 0"
            @click="resetFilters"
            class="no-data-action-btn secondary"
          >
            <span class="btn-icon">🔄</span>
            重置筛选
          </button>
        </div>
      </div>
    </div>
    
    <!-- 添加班级对话框 -->
    <div v-if="showClassDialog" class="modal-overlay" @click.self="closeClassDialog">
     <div class="modal-dialog large-dialog teacher-form-dialog">
        <div class="modal-header">
          <h3>
            <span class="dialog-icon">{{ isEditingClass ? '✏️' : '➕' }}</span>
            {{ isEditingClass ? '编辑班级信息' : '添加新班级' }}
          </h3>
          <button @click="closeClassDialog" class="modal-close">×</button>
        </div>
        
        <div class="modal-body">
          <form @submit.prevent="isEditingClass ? saveEdit() : addNewClass()" class="teacher-form">
            <div class="form-sections">
              <div class="form-section">
                <h4 class="section-title">
                  <span class="section-icon">📋</span>
                  基本信息
                </h4>
                <div class="form-columns">
                  <div class="form-column">
                    <div class="form-group">
                      <label class="required">班级名称</label>
                      <input 
                        type="text" 
                        v-model="currentClass.class_name" 
                        required 
                        class="form-input"
                        placeholder="请输入班级名称"
                      >
                    </div>
                    
                    <div class="form-group">
                      <label class="required">学生人数</label>
                      <input 
                        type="number" 
                        v-model="currentClass.student_count" 
                        required 
                        class="form-input"
                        placeholder="请输入学生人数"
                        min="0"
                      >
                    </div>
                  </div>
                  
                  <div class="form-column">
                    <div class="form-group">
                      <label>班主任</label>
                      <select v-model="currentClass.teacher_id" class="form-select">
                        <option value="">请选择班主任</option>
                        <option 
                          v-for="teacher in availableTeachers" 
                          :key="teacher.teacher_id" 
                          :value="teacher.teacher_id"
                        >
                          {{ teacher.teacher_name }} ({{ teacher.teacher_title }})
                        </option>
                      </select>
                    </div>
                    
                    <div class="form-group">
                      <label class="required">学期</label>
                      <select v-model="currentClass.semester_id" class="form-select" required>
                        <option value="">请选择学期</option>
                        <option 
                          v-for="semester in availableSemesters" 
                          :key="semester.semester_id" 
                          :value="semester.semester_id"
                        >
                          {{ semester.semester_name }}
                        </option>
                      </select>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <div class="form-actions">
              <button type="button" @click="closeClassDialog" class="btn cancel-btn">
                取消
              </button>
              <button type="submit" class="btn primary-btn submit-btn" :disabled="savingClass">
                <span v-if="savingClass" class="loading-spinner-small"></span>
                {{ savingClass ? '保存中...' : (isEditingClass ? '更新班级' : '添加班级') }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- 班级详情对话框 -->
    <div v-if="showDetailDialogFlag" class="modal-overlay" @click.self="closeDetailDialog">
      <div class="modal-dialog large-dialog">
        <div class="modal-header">
          <h3>
            <span class="dialog-icon">👁️</span>
            班级详细信息
          </h3>
          <button @click="closeDetailDialog" class="modal-close">×</button>
        </div>
        
        <div class="modal-body">
          <div class="teacher-detail">
            <div class="detail-section">
              <h4>基本信息</h4>
              <div class="detail-grid">
                <div class="detail-item">
                  <label>班级ID：</label>
                  <span>{{ currentClass.class_id }}</span>
                </div>
                <div class="detail-item">
                  <label>班级名称：</label>
                  <span>{{ currentClass.class_name }}</span>
                </div>
                <div class="detail-item">
                  <label>学生人数：</label>
                  <span>{{ currentClass.student_count }}</span>
                </div>
                <div class="detail-item">
                  <label>班主任：</label>
                  <span>{{ currentClass.teacher_name || '未分配' }}</span>
                </div>
                <div class="detail-item">
                  <label>学期：</label>
                  <span>{{ getSemesterName(currentClass.semester_id) }}</span>
                </div>
              </div>
            </div>
            
            <!-- 学生列表 -->
            <div class="detail-section" v-if="currentClass.students && currentClass.students.length > 0">
              <h4>学生列表 ({{ currentClass.students.length }} 人)</h4>
              <div class="table-container">
                <table class="teachers-table">
                  <thead>
                    <tr>
                      <th>学号</th>
                      <th>姓名</th>
                      <th>性别</th>
                      <th>平均成绩</th>
                      <th>课程数量</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="student in currentClass.students" :key="student.student_id">
                      <td>{{ student.student_id }}</td>
                      <td>{{ student.student_name }}</td>
                      <td>{{ student.student_gender }}</td>
                      <td>{{ student.average_grade || '无' }}</td>
                      <td>{{ student.course_count || 0 }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
            
            <div class="detail-section" v-else>
              <h4>学生列表</h4>
              <p class="no-data-text">暂无学生数据</p>
            </div>
          </div>
          
          <div class="detail-actions">
            <button @click="startEditFromDetail" class="btn primary-btn">
              ✏️ 编辑信息
            </button>
            <button @click="closeDetailDialog" class="btn cancel-btn">
              关闭
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

// 响应式数据
const classData = ref([])
const teacherData = ref([])
const semesterData = ref([])
const loading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

// 筛选条件
const filters = ref({
  search: '',
  teacher: '',
  semester: ''
})

// 对话框状态
const showClassDialog = ref(false)
const showDetailDialogFlag = ref(false)
const isEditingClass = ref(false)
const savingClass = ref(false)

// 当前操作的班级
const currentClass = ref(createEmptyClass())

// 编辑状态
const editingClassId = ref(null)
const editingClass = ref({})

// 计算属性
const totalClasses = computed(() => {
  return classData.value.length
})

const totalStudents = computed(() => {
  return classData.value.reduce((total, classItem) => total + classItem.student_count, 0)
})

// 筛选后的班级数据
const filteredClassData = computed(() => {
  if (!classData.value.length) return []
  
  return classData.value.filter(classItem => {
    // 搜索筛选（班级名称）
    if (filters.value.search) {
      const searchLower = filters.value.search.toLowerCase()
      const nameMatch = classItem.class_name?.toLowerCase().includes(searchLower)
      if (!nameMatch) return false
    }
    
    // 班主任筛选
    if (filters.value.teacher && classItem.teacher_id !== parseInt(filters.value.teacher)) {
      return false
    }
    
    // 学期筛选
    if (filters.value.semester && classItem.semester_id !== parseInt(filters.value.semester)) {
      return false
    }
    
    return true
  })
})

// 可用班主任列表
const availableTeachers = computed(() => {
  return teacherData.value
})

// 可用学期列表
const availableSemesters = computed(() => {
  return semesterData.value
})

// 创建空班级对象
function createEmptyClass() {
  return {
    class_name: '',
    student_count: 0,
    teacher_id: null,
    semester_id: null
  }
}

// 获取学期名称
function getSemesterName(semesterId) {
  const semester = semesterData.value.find(s => s.semester_id === semesterId)
  return semester ? semester.semester_name : '未知学期'
}

// 重置筛选条件
const resetFilters = () => {
  filters.value = {
    search: '',
    teacher: '',
    semester: ''
  }
}

// 导出数据
const exportData = () => {
  const dataStr = JSON.stringify(filteredClassData.value, null, 2)
  const dataBlob = new Blob([dataStr], { type: 'application/json' })
  const url = URL.createObjectURL(dataBlob)
  const link = document.createElement('a')
  link.href = url
  link.download = `班级数据_${new Date().toISOString().split('T')[0]}.json`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
  
  successMessage.value = '数据导出成功'
  setTimeout(() => {
    successMessage.value = ''
  }, 3000)
}

// 生命周期
onMounted(() => {
  fetchClassData()
  fetchTeacherData()
  fetchSemesterData()
})

// 获取班级数据
const fetchClassData = async () => {
  loading.value = true
  errorMessage.value = ''
  
  try {
    const token = localStorage.getItem('jwt_token')
    const response = await axios.get(apiConfig.ADMIN_API.CLASS_INFO, {
      headers: { 'Authorization': `Bearer ${token}` }
    })

    if (response.data.status === 'success') {
      classData.value = response.data.data
    } else {
      errorMessage.value = response.data.error || '获取数据失败'
    }
  } catch (error) {
    handleApiError(error)
  } finally {
    loading.value = false
  }
}

// 获取老师数据
const fetchTeacherData = async () => {
  try {
    const token = localStorage.getItem('jwt_token')
    const response = await axios.get(apiConfig.ADMIN_API.TEACHER_INFO, {
      headers: { 'Authorization': `Bearer ${token}` }
    })

    if (response.data.status === 'success') {
      teacherData.value = response.data.data
    }
  } catch (error) {
    console.error('获取老师数据失败:', error)
  }
}

// 获取学期数据
const fetchSemesterData = async () => {
  try {
    const token = localStorage.getItem('jwt_token')
    const response = await axios.get(apiConfig.ADMIN_API.SEMESTER_INFO, {
      headers: { 'Authorization': `Bearer ${token}` }
    })

    if (response.data.status === 'success') {
      semesterData.value = response.data.data
    }
  } catch (error) {
    console.error('获取学期数据失败:', error)
  }
}

// 刷新数据
const refreshData = () => {
  fetchClassData()
  fetchTeacherData()
  fetchSemesterData()
}

// 打开添加班级对话框
const openAddClassDialog = () => {
  isEditingClass.value = false
  currentClass.value = createEmptyClass()
  showClassDialog.value = true
}

// 开始编辑班级
const startEdit = (classItem) => {
  isEditingClass.value = true
  editingClassId.value = classItem.class_id
  editingClass.value = { ...classItem }
  currentClass.value = { ...classItem }
  showClassDialog.value = true
}

// 从详情开始编辑
const startEditFromDetail = () => {
  showDetailDialogFlag.value = false
  isEditingClass.value = true
  editingClassId.value = currentClass.value.class_id
  editingClass.value = { ...currentClass.value }
  showClassDialog.value = true
}

// 取消编辑
const cancelEdit = () => {
  editingClassId.value = null
  editingClass.value = {}
}

// 检查是否正在编辑
const isEditing = (classId) => {
  return editingClassId.value === classId
}

// 保存编辑
const saveEdit = async () => {
  if (!currentClass.value.class_name.trim()) {
    errorMessage.value = '班级名称不能为空'
    return
  }

  if (!currentClass.value.semester_id) {
    errorMessage.value = '请选择学期'
    return
  }

  savingClass.value = true

  try {
    const token = localStorage.getItem('jwt_token')
    const response = await axios.put(apiConfig.ADMIN_API.CLASS_INFO, 
      currentClass.value,
      {
        headers: { 'Authorization': `Bearer ${token}` }
      }
    )

    if (response.data.status === 'success') {
      successMessage.value = '班级信息更新成功'
      closeClassDialog()
      fetchClassData()
      
      setTimeout(() => {
        successMessage.value = ''
      }, 3000)
    } else {
      errorMessage.value = response.data.error || '更新失败'
    }
  } catch (error) {
    handleApiError(error)
  } finally {
    savingClass.value = false
  }
}

// 显示班级详情
const showDetailDialog = async (classItem) => {
  currentClass.value = { ...classItem }
  
  // 获取班级的学生详情
  try {
    const token = localStorage.getItem('jwt_token')
    const response = await axios.get(`${apiConfig.ADMIN_API.CLASS_INFO}?class_id=${classItem.class_id}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })

    if (response.data.status === 'success' && response.data.data.students) {
      currentClass.value.students = response.data.data.students
    }
  } catch (error) {
    console.error('获取班级详情失败:', error)
  }
  
  showDetailDialogFlag.value = true
}

// 关闭详情对话框
const closeDetailDialog = () => {
  showDetailDialogFlag.value = false
  currentClass.value = createEmptyClass()
}

// 删除班级
const deleteClass = async (classItem) => {
  if (!confirm(`确定要删除班级 "${classItem.class_name}" 吗？此操作不可撤销！`)) {
    return
  }

  try {
    const token = localStorage.getItem('jwt_token')
    const response = await axios.delete(apiConfig.ADMIN_API.CLASS_INFO, {
      headers: { 'Authorization': `Bearer ${token}` },
      data: { class_id: classItem.class_id }
    })

    if (response.data.status === 'success') {
      successMessage.value = '班级删除成功'
      
      // 从本地数据中移除
      classData.value = classData.value.filter(c => c.class_id !== classItem.class_id)
      
      setTimeout(() => {
        successMessage.value = ''
      }, 3000)
    } else {
      errorMessage.value = response.data.error || '删除失败'
    }
  } catch (error) {
    handleApiError(error)
  }
}

// 添加新班级
const addNewClass = async () => {
  if (!currentClass.value.class_name.trim()) {
    errorMessage.value = '班级名称不能为空'
    return
  }

  if (!currentClass.value.semester_id) {
    errorMessage.value = '请选择学期'
    return
  }

  savingClass.value = true
  
  try {
    const token = localStorage.getItem('jwt_token')
    const response = await axios.post(apiConfig.ADMIN_API.CLASS_INFO, 
      currentClass.value,
      {
        headers: { 'Authorization': `Bearer ${token}` }
      }
    )

    if (response.data.status === 'success') {
      successMessage.value = '班级添加成功'
      closeClassDialog()
      fetchClassData()
      
      setTimeout(() => {
        successMessage.value = ''
      }, 3000)
    } else {
      errorMessage.value = response.data.error || '添加失败'
    }
  } catch (error) {
    handleApiError(error)
  } finally {
    savingClass.value = false
  }
}

// 关闭班级对话框
const closeClassDialog = () => {
  showClassDialog.value = false
  isEditingClass.value = false
  savingClass.value = false
  currentClass.value = createEmptyClass()
  cancelEdit()
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

// 清除错误信息
const clearError = () => {
  errorMessage.value = ''
}

// 清除成功信息
const clearSuccess = () => {
  successMessage.value = ''
}

import apiConfig from '@/config/apiConfig';
</script>

<style scoped>
/* 完全复用老师管理页面的所有样式 */
.admin-class-container {
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
  flex-shrink:0 ;
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

.loading-spinner-small {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  display: inline-block;
  margin-right: 8px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-container p {
  color: rgba(255, 255, 255, 0.7);
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

/* 筛选控制区域 */
.filter-controls {
  margin-bottom: 20px;
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

.actions-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 15px;
}

.action-group {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

/* 优化的添加班级按钮 */
.add-class-btn {
  position: relative;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-weight: 700;
  padding: 14px 28px;
  border: none;
  border-radius: 12px;
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 16px;
  z-index: 10;
  animation: pulse 2s infinite;
}

.add-class-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6);
}

.add-class-btn:active {
  transform: translateY(-1px);
}

.btn-badge {
  background: rgba(255, 255, 255, 0.9);
  color: #667eea;
  font-size: 10px;
  font-weight: 800;
  padding: 2px 6px;
  border-radius: 8px;
  margin-left: 4px;
  animation: bounce 2s infinite;
}

@keyframes pulse {
  0% {
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
  }
  50% {
    box-shadow: 0 6px 25px rgba(102, 126, 234, 0.7);
  }
  100% {
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
  }
}

@keyframes bounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-2px);
  }
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  border: none;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.primary-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.secondary-btn {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: rgba(255, 255, 255, 0.9);
}

.action-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.btn-icon {
  font-size: 18px;
}

/* 数据展示区域 */
.data-container {
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
  margin: 0;
}

.results-count {
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
  font-weight: normal;
}

.table-container {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

/* 老师表格样式 */
.teachers-table {
  width: 100%;
  border-collapse: collapse;
}

.teachers-table th {
  background: rgba(255, 255, 255, 0.08);
  color: rgba(255, 255, 255, 0.95);
  padding: 15px;
  text-align: left;
  font-weight: 600;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.teachers-table td {
  padding: 15px;
  color: rgba(255, 255, 255, 0.8);
  border-bottom: 1px solid rgba(255, 255, 255, 0.03);
}

.teachers-table tr:last-child td {
  border-bottom: none;
}

.teachers-table tr:hover {
  background: rgba(255, 255, 255, 0.02);
}

.teacher-name {
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
}

.action-buttons {
  display: flex;
  gap: 8px;
}

/* 编辑输入框样式 */
.edit-input, .edit-select {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 6px;
  color: white;
  padding: 8px 12px;
  width: 100%;
  font-size: 14px;
}

.edit-input:focus, .edit-select:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.3);
}

.edit-select {
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%23ffffff' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 8px center;
  background-size: 12px;
}

/* 模态对话框样式 */
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

.modal-dialog {
  background: rgba(30, 30, 46, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
}

.large-dialog {
  max-width: 900px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 25px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.modal-header h3 {
  color: rgba(255, 255, 255, 0.95);
  margin: 0;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 20px;
}

.dialog-icon {
  font-size: 24px;
}

.modal-close {
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.7);
  font-size: 24px;
  cursor: pointer;
  padding: 0;
  width: 30px;
  height: 30px;
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

.modal-body {
  padding: 25px;
}

/* 表单样式 */
.teacher-form {
  max-height: 70vh;
  overflow-y: auto;
}

.form-sections {
  display: flex;
  flex-direction: column;
  gap: 25px;
}

.form-section {
  padding: 25px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.form-section .section-title {
  color: rgba(255, 255, 255, 0.9);
  font-size: 18px;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  text-align: left;
  display: flex;
  align-items: center;
  gap: 8px;
}

.section-icon {
  font-size: 20px;
}

.form-columns {
  display: flex;
  gap: 25px;
}

.form-column {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  color: rgba(255, 255, 255, 0.9);
  font-weight: 500;
  font-size: 14px;
}

.form-group label.required::after {
  content: " *";
  color: #ff4757;
}

.form-input {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  color: white;
  padding: 12px 15px;
  font-size: 15px;
  transition: all 0.3s ease;
}

.form-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.3);
}

.form-input::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

/* 下拉菜单样式 */
.form-select {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  color: white;
  padding: 12px 15px;
  font-size: 15px;
  transition: all 0.3s ease;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%23ffffff' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 15px center;
  background-size: 12px;
}

.form-select:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.3);
}

/* 为下拉选项添加深色背景 - 全局样式 */
:deep(select.form-select option) {
  background: rgba(30, 30, 46, 0.95);
  color: rgba(255, 255, 255, 0.9);
  padding: 8px 12px;
}

:deep(select.form-select optgroup) {
  background: rgba(30, 30, 46, 0.95);
  color: rgba(255, 255, 255, 0.7);
  font-weight: bold;
}

.form-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.cancel-btn {
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.9);
}

.cancel-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

.submit-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  min-width: 120px;
  justify-content: center;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

/* 老师详情样式 */
.teacher-detail {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.detail-section {
  padding: 20px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.detail-section h4 {
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  font-size: 18px;
}

.detail-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.detail-item.full-width {
  grid-column: 1 / -1;
}

.detail-item label {
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
  font-weight: 500;
}

.detail-item span {
  color: rgba(255, 255, 255, 0.9);
  font-size: 16px;
  word-break: break-word;
}

.detail-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 25px;
  padding-top: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
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

.no-data-action-btn.secondary {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.no-data-action-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.5);
}

.no-data-action-btn.secondary:hover {
  box-shadow: 0 8px 25px rgba(255, 255, 255, 0.2);
}

.no-data-text {
  color: rgba(255, 255, 255, 0.6);
  text-align: center;
  padding: 20px;
  font-style: italic;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header-section {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .actions-bar {
    flex-direction: column;
    align-items: stretch;
    gap: 15px;
  }
  
  .action-group {
    justify-content: space-between;
  }
  
  .action-btn {
    width: 100%;
    justify-content: center;
  }
  
  .add-class-btn {
    order: -1;
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
  
  .teachers-table {
    font-size: 14px;
  }
  
  .teachers-table th,
  .teachers-table td {
    padding: 10px 8px;
  }
  
  .modal-dialog {
    margin: 10px;
    width: calc(100% - 20px);
  }
  
  .form-actions {
    flex-direction: column;
  }
  
  .btn {
    width: 100%;
    justify-content: center;
  }
  
  .form-columns {
    flex-direction: column;
    gap: 15px;
  }
  
  .detail-grid {
    grid-template-columns: 1fr;
  }
  
  .large-dialog {
    margin: 10px;
    width: calc(100% - 20px);
  }
  
  .detail-actions {
    flex-direction: column;
  }
  
  .no-data-actions {
    flex-direction: column;
    align-items: center;
  }
  
  .no-data-action-btn {
    width: 100%;
    max-width: 250px;
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .controls-container, .data-container {
    padding: 15px;
  }
  
  .section-title {
    font-size: 24px;
  }
  
  .title-icon {
    font-size: 28px;
  }
  
  .results-title {
    font-size: 18px;
  }
  
  .teachers-table {
    font-size: 12px;
  }
  
  .teachers-table th,
  .teachers-table td {
    padding: 8px 6px;
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
  
  .edit-input, .edit-select {
    padding: 6px 8px;
    font-size: 12px;
  }
  
  .icon-btn {
    width: 28px;
    height: 28px;
    font-size: 14px;
  }
  
  .form-section {
    padding: 15px;
  }
  
  .detail-section {
    padding: 15px;
  }
  
  .modal-header {
    padding: 20px;
  }
  
  .modal-body {
    padding: 20px;
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