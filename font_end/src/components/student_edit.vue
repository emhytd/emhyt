<template>
  <div class="admin-student-container">
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
      <p>正在加载学生数据...</p>
    </div>
    
    <!-- 控制区域 -->
    <div class="controls-container">
      <div class="header-section">
        <h2 class="section-title">
          <span class="title-icon">👨‍🎓</span>
          学生信息管理
        </h2>
        <div class="header-stats">
          <div class="stat-item">
            <span class="stat-number">{{ filteredStudentCount }}</span>
            <span class="stat-label">筛选结果</span>
          </div>
          <div class="stat-item">
            <span class="stat-number">{{ totalStudents }}</span>
            <span class="stat-label">总学生数</span>
          </div>
          <div class="stat-item">
            <span class="stat-number">{{ studentData.length }}</span>
            <span class="stat-label">班级数量</span>
          </div>
        </div>
      </div>
      
      <!-- 筛选控制区域 -->
      <div class="filter-controls">
        <div class="filter-group">
          <!-- 姓名/学号搜索 -->
          <div class="filter-item">
            <label class="filter-label">搜索:</label>
            <input 
              type="text" 
              v-model="filters.search" 
              placeholder="输入姓名或学号" 
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
          
          <!-- 性别筛选 -->
          <div class="filter-item">
            <label class="filter-label">性别:</label>
            <select v-model="filters.gender" class="filter-select">
              <option value="">全部性别</option>
              <option value="男">男</option>
              <option value="女">女</option>
            </select>
          </div>
          
          <!-- 重置筛选按钮 -->
          <button @click="resetFilters" class="filter-reset-btn">
            重置筛选
          </button>
        </div>
      </div>
      
      <div class="actions-bar">
        <!-- 优化的添加学生按钮 -->
        <button 
          @click="openAddStudentDialog"
          class="action-btn primary-btn add-student-btn"
        >
          <span class="btn-icon">➕</span>
          添加学生
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
            :disabled="filteredStudentCount === 0"
          >
            <span class="btn-icon">📤</span>
            导出数据
          </button>
        </div>
      </div>
    </div>
    
    <!-- 数据展示区域 -->
    <div v-if="filteredStudentData.length > 0 && !loading" class="data-container">
      <div class="results-header">
        <h3 class="results-title">
          学生信息总览
          <span class="results-count">(共 {{ filteredStudentCount }} 名学生)</span>
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
      
      <div class="classes-container">
        <div v-for="classItem in filteredStudentData" :key="classItem.class_id" class="class-card">
          <div class="class-header" @click="toggleClassExpansion(classItem.class_id)">
            <div class="class-info">
              <h4 class="class-name">{{ classItem.class_name }}</h4>
              <div class="class-details">
                <span class="detail-item">班级ID: {{ classItem.class_id }}</span>
                <span class="detail-item">学生人数: {{ classItem.students.length }}</span>
                <!-- 修改班主任信息访问方式 -->
                <span class="detail-item">班主任: {{ classItem.class_teacher?.teacher_name || '未分配' }}</span>
                <span v-if="classItem.class_teacher?.teacher_title" class="detail-item">
                  职称: {{ classItem.class_teacher.teacher_title }}
                </span>
              </div>
            </div>
            <div class="class-status-container">
              <div class="class-status">
                {{ classItem.students.length }} 名学生
              </div>
              <div class="class-actions">
                <button 
                  @click.stop="addStudentToClass(classItem)"
                  class="icon-btn add-btn"
                  title="添加学生到此班级"
                >
                  ➕
                </button>
                <div class="collapse-icon">
                  {{ classItem.isExpanded ? '▼' : '►' }}
                </div>
              </div>
            </div>
          </div>
          
          <div v-show="classItem.isExpanded" class="students-container">
            <table class="students-table">
              <thead>
                <tr>
                  <th>学号</th>
                  <th>姓名</th>
                  <th>性别</th>
                  <th v-if="viewMode === 'detail'">出生日期</th>
                  <th v-if="viewMode === 'detail'">民族</th>
                  <th v-if="viewMode === 'detail'">证件号</th>
                  <th>联系电话</th>
                  <th>邮箱</th>
                  <th v-if="viewMode === 'detail'">政治面貌</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="student in classItem.students" :key="student.student_id">
                  <td>{{ student.student_id }}</td>
                  <td>
                    <span v-if="!isEditing(student.student_id)" class="student-name">
                      {{ student.student_name }}
                    </span>
                    <input 
                      v-else
                      type="text"
                      v-model="editingStudent.student_name"
                      class="edit-input"
                    >
                  </td>
                  <td>
                    <span v-if="!isEditing(student.student_id)">{{ student.student_gender || '未设置' }}</span>
                    <select v-else v-model="editingStudent.student_gender" class="edit-select">
                      <option value="男">男</option>
                      <option value="女">女</option>
                    </select>
                  </td>
                  <td v-if="viewMode === 'detail'">
                    <span v-if="!isEditing(student.student_id)">{{ formatDate(student.birth_date) || '未设置' }}</span>
                    <input 
                      v-else
                      type="date"
                      v-model="editingStudent.birth_date"
                      class="edit-input"
                    >
                  </td>
                  <td v-if="viewMode === 'detail'">
                    <span v-if="!isEditing(student.student_id)">{{ student.ethnicity || '未设置' }}</span>
                    <input 
                      v-else
                      type="text"
                      v-model="editingStudent.ethnicity"
                      class="edit-input"
                    >
                  </td>
                  <td v-if="viewMode === 'detail'">
                    <span v-if="!isEditing(student.student_id)">{{ student.id_number || '未设置' }}</span>
                    <input 
                      v-else
                      type="text"
                      v-model="editingStudent.id_number"
                      class="edit-input"
                    >
                  </td>
                  <td>
                    <span v-if="!isEditing(student.student_id)">{{ student.phone_number || '未设置' }}</span>
                    <input 
                      v-else
                      type="text"
                      v-model="editingStudent.phone_number"
                      class="edit-input"
                    >
                  </td>
                  <td>
                    <span v-if="!isEditing(student.student_id)">{{ student.email || '未设置' }}</span>
                    <input 
                      v-else
                      type="email"
                      v-model="editingStudent.email"
                      class="edit-input"
                    >
                  </td>
                  <td v-if="viewMode === 'detail'">
                    <span v-if="!isEditing(student.student_id)">{{ student.political_status || '未设置' }}</span>
                    <input 
                      v-else
                      type="text"
                      v-model="editingStudent.political_status"
                      class="edit-input"
                    >
                  </td>
                  <td>
                    <div class="action-buttons">
                      <button 
                        v-if="!isEditing(student.student_id)"
                        @click="startEdit(student)"
                        class="icon-btn edit-btn"
                        title="编辑学生信息"
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
                        v-if="!isEditing(student.student_id)"
                        @click="showDetailDialog(student)"
                        class="icon-btn view-btn"
                        title="查看详情"
                      >
                        👁️
                      </button>
                      <button 
                        v-if="!isEditing(student.student_id)"
                        @click="deleteStudent(student)"
                        class="icon-btn delete-btn"
                        title="删除学生"
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
      </div>
    </div>
    
    <!-- 无数据提示 -->
    <div v-if="filteredStudentData.length === 0 && !loading" class="no-data-container">
      <div class="no-data-content">
        <div class="no-data-icon">👨‍🎓</div>
        <h3 v-if="studentData.length === 0">暂无学生数据</h3>
        <h3 v-else>没有找到匹配的学生</h3>
        <p v-if="studentData.length === 0">还没有添加任何学生信息，点击下方按钮开始添加</p>
        <p v-else>当前筛选条件下没有找到匹配的学生，请尝试调整筛选条件</p>
        <div class="no-data-actions">
          <button 
            @click="openAddStudentDialog"
            class="no-data-action-btn"
          >
            <span class="btn-icon">➕</span>
            添加学生
          </button>
          <button 
            v-if="studentData.length > 0"
            @click="resetFilters"
            class="no-data-action-btn secondary"
          >
            <span class="btn-icon">🔄</span>
            重置筛选
          </button>
        </div>
      </div>
    </div>
    
    <!-- 添加/编辑学生对话框 -->
    <div v-if="showStudentDialog" class="modal-overlay" @click.self="closeStudentDialog">
      <div class="modal-dialog large-dialog student-form-dialog">
        <div class="modal-header">
          <h3>
            <span class="dialog-icon">{{ isEditingStudent ? '✏️' : '➕' }}</span>
            {{ isEditingStudent ? '编辑学生信息' : '添加新学生' }}
          </h3>
          <button @click="closeStudentDialog" class="modal-close">×</button>
        </div>
        
        <div class="modal-body">
          <form @submit.prevent="isEditingStudent ? saveEdit() : addNewStudent()" class="student-form">
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
                      <label class="required">班级：</label>
                      <select v-model="currentStudent.class_id" required class="form-select">
                        <option value="">请选择班级</option>
                        <option 
                          v-for="classItem in studentData" 
                          :key="classItem.class_id" 
                          :value="classItem.class_id"
                        >
                          {{ classItem.class_name }} ({{ classItem.class_id }})
                        </option>
                      </select>
                    </div>
                    
                    <div class="form-group">
                      <label class="required">姓名：</label>
                      <input 
                        type="text" 
                        v-model="currentStudent.student_name" 
                        required 
                        class="form-input"
                        placeholder="请输入学生姓名"
                      >
                    </div>
                    
                    <div class="form-group">
                      <label class="required">性别：</label>
                      <select v-model="currentStudent.student_gender" required class="form-select">
                        <option value="男">男</option>
                        <option value="女">女</option>
                      </select>
                    </div>
                    
                    <div class="form-group">
                      <label>出生日期：</label>
                      <input 
                        type="date" 
                        v-model="currentStudent.birth_date" 
                        class="form-input"
                      >
                    </div>
                    
                    <div class="form-group">
                      <label>民族：</label>
                      <input 
                        type="text" 
                        v-model="currentStudent.ethnicity" 
                        class="form-input"
                        placeholder="请输入民族"
                      >
                    </div>
                  </div>
                  
                  <div class="form-column">
                    <div class="form-group">
                      <label>证件号：</label>
                      <input 
                        type="text" 
                        v-model="currentStudent.id_number" 
                        class="form-input"
                        placeholder="请输入证件号"
                      >
                    </div>
                    
                    <div class="form-group">
                      <label>籍贯：</label>
                      <input 
                        type="text" 
                        v-model="currentStudent.native_place" 
                        class="form-input"
                        placeholder="请输入籍贯"
                      >
                    </div>
                    
                    <div class="form-group">
                      <label>出生地：</label>
                      <input 
                        type="text" 
                        v-model="currentStudent.birthplace" 
                        class="form-input"
                        placeholder="请输入出生地"
                      >
                    </div>
                    
                    <div class="form-group">
                      <label>政治面貌：</label>
                      <input 
                        type="text" 
                        v-model="currentStudent.political_status" 
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
                      <label>家庭住址：</label>
                      <textarea 
                        v-model="currentStudent.home_address" 
                        class="form-input"
                        placeholder="请输入家庭住址"
                        rows="3"
                      ></textarea>
                    </div>
                    
                    <div class="form-group">
                      <label>现居住地：</label>
                      <textarea 
                        v-model="currentStudent.current_residence" 
                        class="form-input"
                        placeholder="请输入现居住地"
                        rows="3"
                      ></textarea>
                    </div>
                  </div>
                  
                  <div class="form-column">
                    <div class="form-group">
                      <label>联系电话：</label>
                      <input 
                        type="text" 
                        v-model="currentStudent.phone_number" 
                        class="form-input"
                        placeholder="请输入联系电话"
                      >
                    </div>
                    
                    <div class="form-group">
                      <label>邮箱：</label>
                      <input 
                        type="email" 
                        v-model="currentStudent.email" 
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
                      <label>血型：</label>
                      <select v-model="currentStudent.blood_type" class="form-select">
                        <option value="">请选择血型</option>
                        <option value="A">A型</option>
                        <option value="B">B型</option>
                        <option value="AB">AB型</option>
                        <option value="O">O型</option>
                        <option value="其他">其他</option>
                      </select>
                    </div>
                    
                    <div class="form-group">
                      <label>体重（kg）：</label>
                      <input 
                        type="number" 
                        v-model="currentStudent.weight" 
                        class="form-input"
                        placeholder="请输入体重"
                        step="0.1"
                        min="0"
                      >
                    </div>
                    
                    <div class="form-group">
                      <label>身高（cm）：</label>
                      <input 
                        type="number" 
                        v-model="currentStudent.height" 
                        class="form-input"
                        placeholder="请输入身高"
                        step="0.1"
                        min="0"
                      >
                    </div>
                  </div>
                  
                  <div class="form-column">
                    <div class="form-group full-width">
                      <label>特长：</label>
                      <textarea 
                        v-model="currentStudent.specialty" 
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
              <button type="button" @click="closeStudentDialog" class="btn cancel-btn">
                取消
              </button>
              <button type="submit" class="btn primary-btn submit-btn" :disabled="savingStudent">
                <span v-if="savingStudent" class="loading-spinner-small"></span>
                {{ savingStudent ? '保存中...' : (isEditingStudent ? '更新学生' : '添加学生') }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- 学生详情对话框 -->
    <div v-if="showDetailDialogFlag" class="modal-overlay" @click.self="closeDetailDialog">
      <div class="modal-dialog">
        <div class="modal-header">
          <h3>
            <span class="dialog-icon">👁️</span>
            学生详细信息
          </h3>
          <button @click="closeDetailDialog" class="modal-close">×</button>
        </div>
        
        <div class="modal-body">
          <div class="student-detail">
            <div class="detail-section">
              <h4>基本信息</h4>
              <div class="detail-grid">
                <div class="detail-item">
                  <label>学号：</label>
                  <span>{{ currentStudent.student_id }}</span>
                </div>
                <div class="detail-item">
                  <label>姓名：</label>
                  <span>{{ currentStudent.student_name }}</span>
                </div>
                <div class="detail-item">
                  <label>性别：</label>
                  <span>{{ currentStudent.student_gender }}</span>
                </div>
                <div class="detail-item">
                  <label>出生日期：</label>
                  <span>{{ formatDate(currentStudent.birth_date) || '未设置' }}</span>
                </div>
                <div class="detail-item">
                  <label>民族：</label>
                  <span>{{ currentStudent.ethnicity || '未设置' }}</span>
                </div>
                <div class="detail-item">
                  <label>证件号：</label>
                  <span>{{ currentStudent.id_number || '未设置' }}</span>
                </div>
                <!-- 添加新的字段 -->
                <div class="detail-item">
                  <label>籍贯：</label>
                  <span>{{ currentStudent.native_place || '未设置' }}</span>
                </div>
                <div class="detail-item">
                  <label>出生地：</label>
                  <span>{{ currentStudent.birthplace || '未设置' }}</span>
                </div>
              </div>
            </div>
            
            <div class="detail-section">
              <h4>联系信息</h4>
              <div class="detail-grid">
                <div class="detail-item">
                  <label>联系电话：</label>
                  <span>{{ currentStudent.phone_number || '未设置' }}</span>
                </div>
                <div class="detail-item">
                  <label>邮箱：</label>
                  <span>{{ currentStudent.email || '未设置' }}</span>
                </div>
                <div class="detail-item full-width">
                  <label>家庭住址：</label>
                  <span>{{ currentStudent.home_address || '未设置' }}</span>
                </div>
                <div class="detail-item full-width">
                  <label>现居住地：</label>
                  <span>{{ currentStudent.current_residence || '未设置' }}</span>
                </div>
              </div>
            </div>
            
            <div class="detail-section">
              <h4>其他信息</h4>
              <div class="detail-grid">
                <div class="detail-item">
                  <label>政治面貌：</label>
                  <span>{{ currentStudent.political_status || '未设置' }}</span>
                </div>
                <div class="detail-item">
                  <label>血型：</label>
                  <span>{{ currentStudent.blood_type || '未设置' }}</span>
                </div>
                <div class="detail-item">
                  <label>体重：</label>
                  <span>{{ currentStudent.weight ? currentStudent.weight + ' kg' : '未设置' }}</span>
                </div>
                <div class="detail-item">
                  <label>身高：</label>
                  <span>{{ currentStudent.height ? currentStudent.height + ' cm' : '未设置' }}</span>
                </div>
                <div class="detail-item full-width">
                  <label>特长：</label>
                  <span>{{ currentStudent.specialty || '未设置' }}</span>
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
import apiConfig from '@/config/apiConfig'

// 响应式数据
const studentData = ref([])
const loading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const viewMode = ref('simple') // 'simple' 或 'detail'

// 筛选条件
const filters = ref({
  search: '',
  selectedClass: '',
  gender: ''
})

// 对话框状态
const showStudentDialog = ref(false)
const showDetailDialogFlag = ref(false)
const isEditingStudent = ref(false)
const savingStudent = ref(false)

// 当前操作的学生
const currentStudent = ref(createEmptyStudent())

// 编辑状态
const editingStudentId = ref(null)
const editingStudent = ref({})

// 计算属性
const totalStudents = computed(() => {
  return studentData.value.reduce((total, classItem) => total + classItem.students.length, 0)
})

// 筛选后的学生数据
const filteredStudentData = computed(() => {
  if (!studentData.value.length) return []
  
  return studentData.value
    .filter(classItem => {
      // 班级筛选
      if (filters.value.selectedClass && classItem.class_id !== filters.value.selectedClass) {
        return false
      }
      
      // 学生搜索筛选
      if (filters.value.search) {
        const hasMatchingStudent = classItem.students.some(student => 
          student.student_name?.toLowerCase().includes(filters.value.search.toLowerCase()) ||
          student.student_id?.toString().includes(filters.value.search)
        )
        
        if (!hasMatchingStudent) return false
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
        
        // 性别筛选
        if (filters.value.gender && student.student_gender !== filters.value.gender) {
          return false
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

// 筛选后的学生总数
const filteredStudentCount = computed(() => {
  return filteredStudentData.value.reduce((total, classItem) => total + classItem.students.length, 0)
})

// 可用班级列表（用于筛选）
const availableClasses = computed(() => {
  if (!studentData.value.length) return []
  
  return studentData.value.map(classItem => ({
    class_id: classItem.class_id,
    class_name: classItem.class_name
  }))
})

// 创建空学生对象 - 更新字段以匹配新数据结构
function createEmptyStudent() {
  return {
    class_id: '',
    student_name: '',
    student_gender: '男',
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
    selectedClass: '',
    gender: ''
  }
}

// 导出数据
const exportData = () => {
  const allStudents = filteredStudentData.value.flatMap(classItem => 
    classItem.students.map(student => ({
      ...student,
      class_name: classItem.class_name,
      teacher_name: classItem.class_teacher?.teacher_name || '未分配'
    }))
  )
  
  const dataStr = JSON.stringify(allStudents, null, 2)
  const dataBlob = new Blob([dataStr], { type: 'application/json' })
  const url = URL.createObjectURL(dataBlob)
  const link = document.createElement('a')
  link.href = url
  link.download = `学生数据_${new Date().toISOString().split('T')[0]}.json`
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
  fetchStudentData()
})

// 获取学生数据
const fetchStudentData = async () => {
  loading.value = true
  errorMessage.value = ''
  
  try {
    const token = localStorage.getItem('jwt_token')
    const response = await axios.get(apiConfig.ADMIN_API.STUDENT_INFO, {
      headers: { 'Authorization': `Bearer ${token}` }
    })

    if (response.data.status === 'success') {
      studentData.value = response.data.data.map(classItem => ({
        ...classItem,
        isExpanded: false
      }))
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
  fetchStudentData()
}

// 切换视图模式
const toggleViewMode = () => {
  viewMode.value = viewMode.value === 'simple' ? 'detail' : 'simple'
}

// 切换班级展开状态
const toggleClassExpansion = (classId) => {
  const classItem = studentData.value.find(c => c.class_id === classId)
  if (classItem) {
    classItem.isExpanded = !classItem.isExpanded
  }
}

// 打开添加学生对话框
const openAddStudentDialog = () => {
  isEditingStudent.value = false
  currentStudent.value = createEmptyStudent()
  showStudentDialog.value = true
}

// 开始编辑学生
const startEdit = (student) => {
  isEditingStudent.value = true
  editingStudentId.value = student.student_id
  editingStudent.value = { ...student }
  currentStudent.value = { ...student }
  showStudentDialog.value = true
}

// 从详情开始编辑
const startEditFromDetail = () => {
  showDetailDialogFlag.value = false
  isEditingStudent.value = true
  editingStudentId.value = currentStudent.value.student_id
  editingStudent.value = { ...currentStudent.value }
  showStudentDialog.value = true
}

// 取消编辑
const cancelEdit = () => {
  editingStudentId.value = null
  editingStudent.value = {}
}

// 检查是否正在编辑
const isEditing = (studentId) => {
  return editingStudentId.value === studentId
}

// 保存编辑
const saveEdit = async () => {
  if (!currentStudent.value.student_name.trim()) {
    errorMessage.value = '学生姓名不能为空'
    return
  }

  savingStudent.value = true

  try {
    const token = localStorage.getItem('jwt_token')
    const response = await axios.put(apiConfig.ADMIN_API.STUDENT_INFO, 
      currentStudent.value,
      {
        headers: { 'Authorization': `Bearer ${token}` }
      }
    )

    if (response.data.status === 'success') {
      successMessage.value = '学生信息更新成功'
      closeStudentDialog()
      fetchStudentData()
      
      setTimeout(() => {
        successMessage.value = ''
      }, 3000)
    } else {
      errorMessage.value = response.data.error || '更新失败'
    }
  } catch (error) {
    handleApiError(error)
  } finally {
    savingStudent.value = false
  }
}

// 显示学生详情
const showDetailDialog = (student) => {
  currentStudent.value = { ...student }
  showDetailDialogFlag.value = true
}

// 关闭详情对话框
const closeDetailDialog = () => {
  showDetailDialogFlag.value = false
  currentStudent.value = createEmptyStudent()
}

// 删除学生
const deleteStudent = async (student) => {
  if (!confirm(`确定要删除学生 ${student.student_name} (${student.student_id}) 吗？此操作不可撤销！`)) {
    return
  }

  try {
    const token = localStorage.getItem('jwt_token')
    const response = await axios.delete(apiConfig.ADMIN_API.STUDENT_INFO, {
      headers: { 'Authorization': `Bearer ${token}` },
      data: { student_id: student.student_id }
    })

    if (response.data.status === 'success') {
      successMessage.value = '学生删除成功'
      
      // 从本地数据中移除
      studentData.value.forEach(classItem => {
        classItem.students = classItem.students.filter(s => s.student_id !== student.student_id)
      })
      
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

// 添加学生到指定班级
const addStudentToClass = (classItem) => {
  isEditingStudent.value = false
  currentStudent.value = createEmptyStudent()
  currentStudent.value.class_id = classItem.class_id
  showStudentDialog.value = true
}

// 添加新学生
const addNewStudent = async () => {
  if (!currentStudent.value.student_name.trim()) {
    errorMessage.value = '学生姓名不能为空'
    return
  }

  if (!currentStudent.value.class_id) {
    errorMessage.value = '请选择班级'
    return
  }

  savingStudent.value = true
  
  try {
    const token = localStorage.getItem('jwt_token')
    const response = await axios.post(apiConfig.ADMIN_API.STUDENT_INFO, 
      currentStudent.value,
      {
        headers: { 'Authorization': `Bearer ${token}` }
      }
    )

    if (response.data.status === 'success') {
      successMessage.value = '学生添加成功'
      closeStudentDialog()
      fetchStudentData()
      
      setTimeout(() => {
        successMessage.value = ''
      }, 3000)
    } else {
      errorMessage.value = response.data.error || '添加失败'
    }
  } catch (error) {
    handleApiError(error)
  } finally {
    savingStudent.value = false
  }
}

// 关闭学生对话框
const closeStudentDialog = () => {
  showStudentDialog.value = false
  isEditingStudent.value = false
  savingStudent.value = false
  currentStudent.value = createEmptyStudent()
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
/* 这里添加与老师管理组件完全一致的样式 */
/* 由于样式代码太长，这里只展示关键样式部分，完整样式请参考老师管理组件 */

.admin-student-container {
  width: 100%;
  margin-top: 0;
  position: relative;
  z-index: 1;
  min-height: 500px;
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

/* 优化的添加学生按钮 */
.add-student-btn {
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

.add-student-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6);
}

.add-student-btn:active {
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

/* 班级卡片样式 */
.classes-container {
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
  background: rgba(102, 126, 234, 0.2);
  color: #667eea;
  border-radius: 20px;
  font-weight: 600;
  font-size: 14px;
  border: 1px solid rgba(102, 126, 234, 0.4);
}

.class-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.icon-btn {
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

.icon-btn:hover {
  background: rgba(255, 255, 255, 0.1);
}

.add-btn:hover {
  color: #4CAF50;
}

.edit-btn:hover {
  color: #2196F3;
}

.delete-btn:hover {
  color: #F44336;
}

.save-btn:hover {
  color: #4CAF50;
}

.cancel-btn:hover {
  color: #FF9800;
}

.view-btn:hover {
  color: #2196F3;
}

.collapse-icon {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.7);
  transition: transform 0.3s ease;
}

/* 学生表格样式 */
.students-container {
  padding: 15px;
  width: 100%;
  overflow-x: auto;
}

.students-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 800px;
}

.students-table th {
  background: rgba(255, 255, 255, 0.08);
  color: rgba(255, 255, 255, 0.95);
  padding: 12px 15px;
  text-align: left;
  font-weight: 600;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.students-table td {
  padding: 12px 15px;
  color: rgba(255, 255, 255, 0.8);
  border-bottom: 1px solid rgba(255, 255, 255, 0.03);
}

.students-table tr:last-child td {
  border-bottom: none;
}

.students-table tr:hover {
  background: rgba(255, 255, 255, 0.02);
}

.student-name {
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
}

.action-buttons {
  display: flex;
  gap: 5px;
}

/* 编辑输入框样式 */
.edit-input, .edit-select {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  color: white;
  padding: 5px 8px;
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

/* 模态对话框样式 - 与老师管理组件一致 */
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

.student-form-dialog {
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

/* 表单样式 - 与老师管理组件一致 */
.student-form {
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

/* 学生详情样式 */
.student-detail {
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

/* 错误信息、成功信息、加载状态等样式与老师管理组件完全一致 */
/* 这里省略重复的样式代码，请参考老师管理组件的完整样式 */

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
  
  .add-student-btn {
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
  
  .class-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .class-details {
    flex-direction: column;
    gap: 5px;
  }
  
  .class-status-container {
    align-self: flex-end;
  }
  
  .students-table {
    font-size: 14px;
  }
  
  .students-table th,
  .students-table td {
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
  
  .students-table {
    font-size: 12px;
  }
  
  .students-table th,
  .students-table td {
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
.error-message {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 2000;
  background: linear-gradient(to right, #ff4d4d, #ff0000);
  color: white;
  padding: 15px 0;
  text-align: center;
  box-shadow: 0 4px 12px rgba(255, 0, 0, 0.3);
  animation: slideInDown 0.5s ease-out;
}

.error-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}

.error-icon {
  font-size: 24px;
  margin-right: 10px;
  flex-shrink: 0;
  animation: pulse 1.5s infinite;
}

.error-text {
  flex: 1;
  color: rgba(255, 255, 255, 0.95);
  font-weight: 600;
  font-size: 16px;
  text-shadow: 0 1px 2px rgba(0,0,0,0.2);
}

.error-close {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  flex-shrink: 0;
  margin-left: 10px;
}

.error-close:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.1);
}

/* 成功信息样式 - 增强视觉冲击力 */
.success-message {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 2000;
  background: linear-gradient(to right, #00c853, #00e676);
  color: white;
  padding: 15px 0;
  text-align: center;
  box-shadow: 0 4px 12px rgba(0, 200, 83, 0.3);
  animation: slideInDown 0.5s ease-out;
}

.success-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}

.success-icon {
  font-size: 24px;
  margin-right: 10px;
  flex-shrink: 0;
  animation: bounce 1.5s infinite;
}

.success-text {
  flex: 1;
  color: rgba(255, 255, 255, 0.95);
  font-weight: 600;
  font-size: 16px;
  text-shadow: 0 1px 2px rgba(0,0,0,0.2);
}

.success-close {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  flex-shrink: 0;
  margin-left: 10px;
}

.success-close:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.1);
}

/* 动画效果 */
@keyframes slideInDown {
  from {
    transform: translateY(-100%);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

@keyframes pulse {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
  100% {
    transform: scale(1);
  }
}

@keyframes bounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-5px);
  }
}
</style>