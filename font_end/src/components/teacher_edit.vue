<template>
  <div class="admin-teacher-container">
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
      <p>正在加载老师数据...</p>
    </div>
    
    <!-- 控制区域 - 重点优化 -->
    <div class="controls-container">
      <div class="header-section">
        <h2 class="section-title">
          <span class="title-icon">👨‍🏫</span>
          老师信息管理
        </h2>
        <div class="header-stats">
          <div class="stat-item">
            <span class="stat-number">{{ filteredTeacherData.length }}</span>
            <span class="stat-label">筛选结果</span>
          </div>
          <div class="stat-item">
            <span class="stat-number">{{ totalTeachers }}</span>
            <span class="stat-label">总老师数</span>
          </div>
        </div>
      </div>
      
      <!-- 筛选控制区域 -->
      <div class="filter-controls">
        <div class="filter-group">
          <!-- 姓名/工号搜索 -->
          <div class="filter-item">
            <label class="filter-label">搜索:</label>
            <input 
              type="text" 
              v-model="filters.search" 
              placeholder="输入姓名或工号" 
              class="filter-input"
            >
          </div>
          
          <!-- 职称筛选 -->
          <div class="filter-item">
            <label class="filter-label">职称:</label>
            <select v-model="filters.title" class="filter-select">
              <option value="">全部职称</option>
              <option 
                v-for="title in availableTitles" 
                :key="title" 
                :value="title"
              >
                {{ title }}
              </option>
            </select>
          </div>
          
          <!-- 政治面貌筛选 -->
          <div class="filter-item">
            <label class="filter-label">政治面貌:</label>
            <select v-model="filters.politicalStatus" class="filter-select">
              <option value="">全部</option>
              <option 
                v-for="status in availablePoliticalStatus" 
                :key="status" 
                :value="status"
              >
                {{ status }}
              </option>
            </select>
          </div>
          
          <!-- 民族筛选 -->
          <div class="filter-item">
            <label class="filter-label">民族:</label>
            <select v-model="filters.ethnicity" class="filter-select">
              <option value="">全部民族</option>
              <option 
                v-for="ethnic in availableEthnicities" 
                :key="ethnic" 
                :value="ethnic"
              >
                {{ ethnic }}
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
        <!-- 优化的添加老师按钮 -->
        <button 
          @click="openAddTeacherDialog"
          class="action-btn primary-btn add-teacher-btn"
        >
          <span class="btn-icon">➕</span>
          添加老师
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

          <button 
            @click="toggleViewMode"
            class="action-btn secondary-btn"
          >
            <span class="btn-icon">{{ viewMode === 'simple' ? '📋' : '👁️' }}</span>
            {{ viewMode === 'simple' ? '详细视图' : '简化视图' }}
          </button>
          
          <!-- 导出按钮 -->
          <button 
            @click="exportData"
            class="action-btn secondary-btn"
            :disabled="filteredTeacherData.length === 0"
          >
            <span class="btn-icon">📤</span>
            导出数据
          </button>
        </div>
      </div>
    </div>
    
    <!-- 数据展示区域 -->
    <div v-if="filteredTeacherData.length > 0 && !loading" class="data-container">
      <div class="results-header">
        <h3 class="results-title">
          老师信息总览
          <span class="results-count">(共 {{ filteredTeacherData.length }} 名老师)</span>
        </h3>
        <div class="view-controls">
          <span class="view-label">视图模式:</span>
          <div class="view-toggle">
            <button 
              :class="['view-option', { active: viewMode === 'simple' }]"
              @click="viewMode = 'simple'"
            >
              简化
            </button>
            <button 
              :class="['view-option', { active: viewMode === 'detail' }]"
              @click="viewMode = 'detail'"
            >
              详细
            </button>
          </div>
        </div>
      </div>
      
      <div class="table-container">
        <table class="teachers-table">
          <thead>
            <tr>
              <th>工号</th>
              <th>姓名</th>
              <th>职称</th>
              <th v-if="viewMode === 'detail'">出生日期</th>
              <th v-if="viewMode === 'detail'">民族</th>
              <th>联系电话</th>
              <th>邮箱</th>
              <th v-if="viewMode === 'detail'">政治面貌</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="teacher in filteredTeacherData" :key="teacher.teacher_id">
              <td>{{ teacher.teacher_id }}</td>
              <td>
                <span v-if="!isEditing(teacher.teacher_id)" class="teacher-name">
                  {{ teacher.teacher_name }}
                </span>
                <input 
                  v-else
                  type="text"
                  v-model="editingTeacher.teacher_name"
                  class="edit-input"
                >
              </td>
              <td>
                <span v-if="!isEditing(teacher.teacher_id)">{{ teacher.teacher_title || '未设置' }}</span>
                <input 
                  v-else
                  type="text"
                  v-model="editingTeacher.teacher_title"
                  class="edit-input"
                >
              </td>
              <td v-if="viewMode === 'detail'">
                <span v-if="!isEditing(teacher.teacher_id)">{{ formatDate(teacher.birth_date) || '未设置' }}</span>
                <input 
                  v-else
                  type="date"
                  v-model="editingTeacher.birth_date"
                  class="edit-input"
                >
              </td>
              <td v-if="viewMode === 'detail'">
                <span v-if="!isEditing(teacher.teacher_id)">{{ teacher.ethnicity || '未设置' }}</span>
                <input 
                  v-else
                  type="text"
                  v-model="editingTeacher.ethnicity"
                  class="edit-input"
                >
              </td>
              <td>
                <span v-if="!isEditing(teacher.teacher_id)">{{ teacher.phone_number || '未设置' }}</span>
                <input 
                  v-else
                  type="text"
                  v-model="editingTeacher.phone_number"
                  class="edit-input"
                >
              </td>
              <td>
                <span v-if="!isEditing(teacher.teacher_id)">{{ teacher.email || '未设置' }}</span>
                <input 
                  v-else
                  type="email"
                  v-model="editingTeacher.email"
                  class="edit-input"
                >
              </td>
              <td v-if="viewMode === 'detail'">
                <span v-if="!isEditing(teacher.teacher_id)">{{ teacher.political_status || '未设置' }}</span>
                <input 
                  v-else
                  type="text"
                  v-model="editingTeacher.political_status"
                  class="edit-input"
                >
              </td>
              <td>
                <div class="action-buttons">
                  <button 
                    v-if="!isEditing(teacher.teacher_id)"
                    @click="startEdit(teacher)"
                    class="icon-btn edit-btn"
                    title="编辑老师信息"
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
                    v-if="!isEditing(teacher.teacher_id)"
                    @click="showDetailDialog(teacher)"
                    class="icon-btn view-btn"
                    title="查看详情"
                  >
                    👁️
                  </button>
                  <button 
                    v-if="!isEditing(teacher.teacher_id)"
                    @click="deleteTeacher(teacher)"
                    class="icon-btn delete-btn"
                    title="删除老师"
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
    
    <!-- 无数据提示 - 优化为空状态 -->
    <div v-if="filteredTeacherData.length === 0 && !loading" class="no-data-container">
      <div class="no-data-content">
        <div class="no-data-icon">👨‍🏫</div>
        <h3 v-if="teacherData.length === 0">暂无老师数据</h3>
        <h3 v-else>没有找到匹配的老师</h3>
        <p v-if="teacherData.length === 0">还没有添加任何老师信息，点击下方按钮开始添加</p>
        <p v-else>当前筛选条件下没有找到匹配的老师，请尝试调整筛选条件</p>
        <div class="no-data-actions">
          <button 
            @click="openAddTeacherDialog"
            class="no-data-action-btn"
          >
            <span class="btn-icon">➕</span>
            添加老师
          </button>
          <button 
            v-if="teacherData.length > 0"
            @click="resetFilters"
            class="no-data-action-btn secondary"
          >
            <span class="btn-icon">🔄</span>
            重置筛选
          </button>
        </div>
      </div>
    </div>
    
    <!-- 添加老师对话框 -->
    <div v-if="showTeacherDialog" class="modal-overlay" @click.self="closeTeacherDialog">
      <div class="modal-dialog large-dialog teacher-form-dialog">
        <div class="modal-header">
          <h3>
            <span class="dialog-icon">{{ isEditingTeacher ? '✏️' : '➕' }}</span>
            {{ isEditingTeacher ? '编辑老师信息' : '添加新老师' }}
          </h3>
          <button @click="closeTeacherDialog" class="modal-close">×</button>
        </div>
        
        <div class="modal-body">
          <form @submit.prevent="isEditingTeacher ? saveEdit() : addNewTeacher()" class="teacher-form">
            <div class="form-sections">
              <!-- 基本信息 -->
              <div class="form-section">
                <h4 class="section-title">
                  <span class="section-icon">📋</span>
                  基本信息
                </h4>
                <div class="form-columns">
                  <div class="form-column">
                    <div class="form-group">
                      <label class="required">姓名</label>
                      <input 
                        type="text" 
                        v-model="currentTeacher.teacher_name" 
                        required 
                        class="form-input"
                        placeholder="请输入老师姓名"
                      >
                    </div>
                    
                    <div class="form-group">
                      <label class="required">职称</label>
                      <input 
                        type="text" 
                        v-model="currentTeacher.teacher_title" 
                        required 
                        class="form-input"
                        placeholder="请输入职称"
                      >
                    </div>
                    
                    <div class="form-group">
                      <label>出生日期</label>
                      <input 
                        type="date" 
                        v-model="currentTeacher.birth_date" 
                        class="form-input"
                      >
                    </div>
                    
                    <div class="form-group">
                      <label>民族</label>
                      <input 
                        type="text" 
                        v-model="currentTeacher.ethnicity" 
                        class="form-input"
                        placeholder="请输入民族"
                      >
                    </div>
                  </div>
                  
                  <div class="form-column">
                    <div class="form-group">
                      <label>证件号</label>
                      <input 
                        type="text" 
                        v-model="currentTeacher.id_number" 
                        class="form-input"
                        placeholder="请输入证件号"
                      >
                    </div>
                    
                    <div class="form-group">
                      <label>籍贯</label>
                      <input 
                        type="text" 
                        v-model="currentTeacher.native_place" 
                        class="form-input"
                        placeholder="请输入籍贯"
                      >
                    </div>
                    
                    <div class="form-group">
                      <label>出生地</label>
                      <input 
                        type="text" 
                        v-model="currentTeacher.birthplace" 
                        class="form-input"
                        placeholder="请输入出生地"
                      >
                    </div>
                    
                    <div class="form-group">
                      <label>政治面貌</label>
                      <input 
                        type="text" 
                        v-model="currentTeacher.political_status" 
                        class="form-input"
                        placeholder="请输入政治面貌"
                      >
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- 联系信息 -->
              <div class="form-section">
                <h4 class="section-title">
                  <span class="section-icon">📞</span>
                  联系信息
                </h4>
                <div class="form-columns">
                  <div class="form-column">
                    <div class="form-group">
                      <label>家庭住址</label>
                      <textarea 
                        v-model="currentTeacher.home_address" 
                        class="form-input"
                        placeholder="请输入家庭住址"
                        rows="3"
                      ></textarea>
                    </div>
                    
                    <div class="form-group">
                      <label>现居住地</label>
                      <textarea 
                        v-model="currentTeacher.current_residence" 
                        class="form-input"
                        placeholder="请输入现居住地"
                        rows="3"
                      ></textarea>
                    </div>
                  </div>
                  
                  <div class="form-column">
                    <div class="form-group">
                      <label>联系电话</label>
                      <input 
                        type="text" 
                        v-model="currentTeacher.phone_number" 
                        class="form-input"
                        placeholder="请输入联系电话"
                      >
                    </div>
                    
                    <div class="form-group">
                      <label>邮箱</label>
                      <input 
                        type="email" 
                        v-model="currentTeacher.email" 
                        class="form-input"
                        placeholder="请输入邮箱地址"
                      >
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- 其他信息 -->
              <div class="form-section">
                <h4 class="section-title">
                  <span class="section-icon">ℹ️</span>
                  其他信息
                </h4>
                <div class="form-columns">
                  <div class="form-column">
                    <div class="form-group">
                      <label>血型</label>
                      <select v-model="currentTeacher.blood_type" class="form-select">
                        <option value="">请选择血型</option>
                        <option value="A">A型</option>
                        <option value="B">B型</option>
                        <option value="AB">AB型</option>
                        <option value="O">O型</option>
                        <option value="其他">其他</option>
                      </select>
                    </div>
                    
                    <div class="form-group">
                      <label>体重（kg）</label>
                      <input 
                        type="number" 
                        v-model="currentTeacher.weight" 
                        class="form-input"
                        placeholder="请输入体重"
                        step="0.1"
                        min="0"
                      >
                    </div>
                    
                    <div class="form-group">
                      <label>身高（cm）</label>
                      <input 
                        type="number" 
                        v-model="currentTeacher.height" 
                        class="form-input"
                        placeholder="请输入身高"
                        step="0.1"
                        min="0"
                      >
                    </div>
                  </div>
                  
                  <div class="form-column">
                    <div class="form-group full-width">
                      <label>特长</label>
                      <textarea 
                        v-model="currentTeacher.specialty" 
                        class="form-input"
                        placeholder="请输入特长"
                        rows="3"
                      ></textarea>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <div class="form-actions">
              <button type="button" @click="closeTeacherDialog" class="btn cancel-btn">
                取消
              </button>
              <button type="submit" class="btn primary-btn submit-btn" :disabled="savingTeacher">
                <span v-if="savingTeacher" class="loading-spinner-small"></span>
                {{ savingTeacher ? '保存中...' : (isEditingTeacher ? '更新老师' : '添加老师') }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- 老师详情对话框 -->
    <div v-if="showDetailDialogFlag" class="modal-overlay" @click.self="closeDetailDialog">
      <div class="modal-dialog">
        <div class="modal-header">
          <h3>
            <span class="dialog-icon">👁️</span>
            老师详细信息
          </h3>
          <button @click="closeDetailDialog" class="modal-close">×</button>
        </div>
        
        <div class="modal-body">
          <div class="teacher-detail">
            <div class="detail-section">
              <h4>基本信息</h4>
              <div class="detail-grid">
                <div class="detail-item">
                  <label>工号：</label>
                  <span>{{ currentTeacher.teacher_id }}</span>
                </div>
                <div class="detail-item">
                  <label>姓名：</label>
                  <span>{{ currentTeacher.teacher_name }}</span>
                </div>
                <div class="detail-item">
                  <label>职称：</label>
                  <span>{{ currentTeacher.teacher_title }}</span>
                </div>
                <div class="detail-item">
                  <label>出生日期：</label>
                  <span>{{ formatDate(currentTeacher.birth_date) || '未设置' }}</span>
                </div>
                <div class="detail-item">
                  <label>民族：</label>
                  <span>{{ currentTeacher.ethnicity || '未设置' }}</span>
                </div>
                <div class="detail-item">
                  <label>证件号：</label>
                  <span>{{ currentTeacher.id_number || '未设置' }}</span>
                </div>
              </div>
            </div>
            
            <div class="detail-section">
              <h4>联系信息</h4>
              <div class="detail-grid">
                <div class="detail-item">
                  <label>联系电话：</label>
                  <span>{{ currentTeacher.phone_number || '未设置' }}</span>
                </div>
                <div class="detail-item">
                  <label>邮箱：</label>
                  <span>{{ currentTeacher.email || '未设置' }}</span>
                </div>
                <div class="detail-item full-width">
                  <label>家庭住址：</label>
                  <span>{{ currentTeacher.home_address || '未设置' }}</span>
                </div>
                <div class="detail-item full-width">
                  <label>现居住地：</label>
                  <span>{{ currentTeacher.current_residence || '未设置' }}</span>
                </div>
              </div>
            </div>
            
            <div class="detail-section">
              <h4>其他信息</h4>
              <div class="detail-grid">
                <div class="detail-item">
                  <label>政治面貌：</label>
                  <span>{{ currentTeacher.political_status || '未设置' }}</span>
                </div>
                <div class="detail-item">
                  <label>血型：</label>
                  <span>{{ currentTeacher.blood_type || '未设置' }}</span>
                </div>
                <div class="detail-item">
                  <label>体重：</label>
                  <span>{{ currentTeacher.weight ? currentTeacher.weight + ' kg' : '未设置' }}</span>
                </div>
                <div class="detail-item">
                  <label>身高：</label>
                  <span>{{ currentTeacher.height ? currentTeacher.height + ' cm' : '未设置' }}</span>
                </div>
                <div class="detail-item full-width">
                  <label>特长：</label>
                  <span>{{ currentTeacher.specialty || '未设置' }}</span>
                </div>
              </div>
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
const teacherData = ref([])
const loading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const viewMode = ref('simple') // 'simple' 或 'detail'

// 筛选条件
const filters = ref({
  search: '',
  title: '',
  politicalStatus: '',
  ethnicity: ''
})

// 对话框状态
const showTeacherDialog = ref(false)
const showDetailDialogFlag = ref(false)
const isEditingTeacher = ref(false)
const savingTeacher = ref(false)

// 当前操作的老师
const currentTeacher = ref(createEmptyTeacher())

// 编辑状态
const editingTeacherId = ref(null)
const editingTeacher = ref({})

// 计算属性
const totalTeachers = computed(() => {
  return teacherData.value.length
})

// 筛选后的老师数据
const filteredTeacherData = computed(() => {
  if (!teacherData.value.length) return []
  
  return teacherData.value.filter(teacher => {
    // 搜索筛选（姓名或工号）
    if (filters.value.search) {
      const searchLower = filters.value.search.toLowerCase()
      const nameMatch = teacher.teacher_name?.toLowerCase().includes(searchLower)
      const idMatch = teacher.teacher_id?.toString().includes(searchLower)
      if (!nameMatch && !idMatch) return false
    }
    
    // 职称筛选
    if (filters.value.title && teacher.teacher_title !== filters.value.title) {
      return false
    }
    
    // 政治面貌筛选
    if (filters.value.politicalStatus && teacher.political_status !== filters.value.politicalStatus) {
      return false
    }
    
    // 民族筛选
    if (filters.value.ethnicity && teacher.ethnicity !== filters.value.ethnicity) {
      return false
    }
    
    return true
  })
})

// 可用职称列表
const availableTitles = computed(() => {
  const titles = new Set()
  teacherData.value.forEach(teacher => {
    if (teacher.teacher_title) {
      titles.add(teacher.teacher_title)
    }
  })
  return Array.from(titles).sort()
})

// 可用政治面貌列表
const availablePoliticalStatus = computed(() => {
  const statuses = new Set()
  teacherData.value.forEach(teacher => {
    if (teacher.political_status) {
      statuses.add(teacher.political_status)
    }
  })
  return Array.from(statuses).sort()
})

// 可用民族列表
const availableEthnicities = computed(() => {
  const ethnicities = new Set()
  teacherData.value.forEach(teacher => {
    if (teacher.ethnicity) {
      ethnicities.add(teacher.ethnicity)
    }
  })
  return Array.from(ethnicities).sort()
})

// 创建空老师对象
function createEmptyTeacher() {
  return {
    teacher_name: '',
    teacher_title: '',
    birth_date: '',
    ethnicity: '',
    id_number: '',
    native_place: '',
    birthplace: '',
    home_address: '',
    political_status: '',
    blood_type: '',
    weight: null,
    height: null,
    specialty: '',
    phone_number: '',
    email: '',
    current_residence: ''
  }
}

// 格式化日期
function formatDate(dateString) {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toISOString().split('T')[0]
}

// 重置筛选条件
const resetFilters = () => {
  filters.value = {
    search: '',
    title: '',
    politicalStatus: '',
    ethnicity: ''
  }
}

// 导出数据
const exportData = () => {
  const dataStr = JSON.stringify(filteredTeacherData.value, null, 2)
  const dataBlob = new Blob([dataStr], { type: 'application/json' })
  const url = URL.createObjectURL(dataBlob)
  const link = document.createElement('a')
  link.href = url
  link.download = `老师数据_${new Date().toISOString().split('T')[0]}.json`
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
  fetchTeacherData()
})

// 获取老师数据
const fetchTeacherData = async () => {
  loading.value = true
  errorMessage.value = ''
  
  try {
    const token = localStorage.getItem('jwt_token')
    const response = await axios.get(apiConfig.ADMIN_API.TEACHER_INFO, {
      headers: { 'Authorization': `Bearer ${token}` }
    })

    if (response.data.status === 'success') {
      teacherData.value = response.data.data
    } else {
      errorMessage.value = response.data.error || '获取数据失败'
    }
  } catch (error) {
    handleApiError(error)
  } finally {
    loading.value = false
  }
}

// 刷新数据
const refreshData = () => {
  fetchTeacherData()
}

// 切换视图模式
const toggleViewMode = () => {
  viewMode.value = viewMode.value === 'simple' ? 'detail' : 'simple'
}

// 打开添加老师对话框
const openAddTeacherDialog = () => {
  isEditingTeacher.value = false
  currentTeacher.value = createEmptyTeacher()
  showTeacherDialog.value = true
}

// 开始编辑老师
const startEdit = (teacher) => {
  isEditingTeacher.value = true
  editingTeacherId.value = teacher.teacher_id
  editingTeacher.value = { ...teacher }
  currentTeacher.value = { ...teacher }
  showTeacherDialog.value = true
}

// 从详情开始编辑
const startEditFromDetail = () => {
  showDetailDialogFlag.value = false
  isEditingTeacher.value = true
  editingTeacherId.value = currentTeacher.value.teacher_id
  editingTeacher.value = { ...currentTeacher.value }
  showTeacherDialog.value = true
}

// 取消编辑
const cancelEdit = () => {
  editingTeacherId.value = null
  editingTeacher.value = {}
}

// 检查是否正在编辑
const isEditing = (teacherId) => {
  return editingTeacherId.value === teacherId
}

// 保存编辑
const saveEdit = async () => {
  if (!currentTeacher.value.teacher_name.trim()) {
    errorMessage.value = '老师姓名不能为空'
    return
  }

  savingTeacher.value = true

  try {
    const token = localStorage.getItem('jwt_token')
    const response = await axios.put(apiConfig.ADMIN_API.TEACHER_INFO, 
      currentTeacher.value,
      {
        headers: { 'Authorization': `Bearer ${token}` }
      }
    )

    if (response.data.status === 'success') {
      successMessage.value = '老师信息更新成功'
      closeTeacherDialog()
      fetchTeacherData()
      
      setTimeout(() => {
        successMessage.value = ''
      }, 3000)
    } else {
      errorMessage.value = response.data.error || '更新失败'
    }
  } catch (error) {
    handleApiError(error)
  } finally {
    savingTeacher.value = false
  }
}

// 显示老师详情
const showDetailDialog = (teacher) => {
  currentTeacher.value = { ...teacher }
  showDetailDialogFlag.value = true
}

// 关闭详情对话框
const closeDetailDialog = () => {
  showDetailDialogFlag.value = false
  currentTeacher.value = createEmptyTeacher()
}

// 删除老师
const deleteTeacher = async (teacher) => {
  if (!confirm(`确定要删除老师 ${teacher.teacher_name} (${teacher.teacher_id}) 吗？此操作不可撤销！`)) {
    return
  }

  try {
    const token = localStorage.getItem('jwt_token')
    const response = await axios.delete(apiConfig.ADMIN_API.TEACHER_INFO, {
      headers: { 'Authorization': `Bearer ${token}` },
      data: { teacher_id: teacher.teacher_id }
    })

    if (response.data.status === 'success') {
      successMessage.value = '老师删除成功'
      
      // 从本地数据中移除
      teacherData.value = teacherData.value.filter(t => t.teacher_id !== teacher.teacher_id)
      
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
import apiConfig from '@/config/apiConfig';
// 添加新老师
const addNewTeacher = async () => {
  if (!currentTeacher.value.teacher_name.trim()) {
    errorMessage.value = '老师姓名不能为空'
    return
  }

  if (!currentTeacher.value.teacher_title.trim()) {
    errorMessage.value = '老师职称不能为空'
    return
  }

  savingTeacher.value = true
  
  try {
    const token = localStorage.getItem('jwt_token')
    const response = await axios.post(apiConfig.ADMIN_API.TEACHER_INFO, 
      currentTeacher.value,
      {
        headers: { 'Authorization': `Bearer ${token}` }
      }
    )

    if (response.data.status === 'success') {
      successMessage.value = '老师添加成功'
      closeTeacherDialog()
      fetchTeacherData()
      
      setTimeout(() => {
        successMessage.value = ''
      }, 3000)
    } else {
      errorMessage.value = response.data.error || '添加失败'
    }
  } catch (error) {
    handleApiError(error)
  } finally {
    savingTeacher.value = false
  }
}

// 关闭老师对话框
const closeTeacherDialog = () => {
  showTeacherDialog.value = false
  isEditingTeacher.value = false
  savingTeacher.value = false
  currentTeacher.value = createEmptyTeacher()
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
</script>

<style scoped>
.admin-teacher-container {
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

/* 优化的添加老师按钮 */
.add-teacher-btn {
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

.add-teacher-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6);
}

.add-teacher-btn:active {
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

.teacher-form-dialog {
  max-width: 800px;
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

.form-group.full-width {
  grid-column: 1 / -1;
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
  
  .add-teacher-btn {
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
  
  .view-controls {
    width: 100%;
    justify-content: space-between;
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