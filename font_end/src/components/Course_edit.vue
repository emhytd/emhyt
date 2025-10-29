<template>
  <div class="admin-course-selection-container">
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
      <p>正在加载选课数据...</p>
    </div>
    
    <!-- 选项卡切换 -->
    <div class="tab-container">
      <div class="tab-buttons">
        <button 
          :class="['tab-button', { active: activeTab === 'selections' }]"
          @click="activeTab = 'selections'"
        >
          <span class="tab-icon">📚</span>
          选课管理
        </button>
        <button 
          :class="['tab-button', { active: activeTab === 'teachings' }]"
          @click="activeTab = 'teachings'"
        >
          <span class="tab-icon">👨‍🏫</span>
          老师授课管理
        </button>
      </div>
    </div>
    
    <!-- 选课管理标签页 -->
    <div v-if="activeTab === 'selections'" class="tab-content">
      <!-- 控制区域 -->
      <div class="controls-container">
        <div class="header-section">
          <h2 class="section-title">
            <span class="title-icon">📚</span>
            选课信息管理
          </h2>
          <div class="header-stats">
            <div class="stat-item">
              <span class="stat-number">{{ filteredSelectionData.length }}</span>
              <span class="stat-label">筛选结果</span>
            </div>
            <div class="stat-item">
              <span class="stat-number">{{ totalSelections }}</span>
              <span class="stat-label">总选课数</span>
            </div>
            <div class="stat-item">
              <span class="stat-number">{{ uniqueStudents }}</span>
              <span class="stat-label">涉及学生</span>
            </div>
          </div>
        </div>
        
        <!-- 筛选控制区域 -->
        <div class="filter-controls">
          <div class="filter-group">
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
            
            <!-- 课程筛选 -->
            <div class="filter-item">
              <label class="filter-label">课程:</label>
              <select v-model="filters.course" class="filter-select">
                <option value="">全部课程</option>
                <option 
                  v-for="course in availableCourses" 
                  :key="course.course_id" 
                  :value="course.course_id"
                >
                  {{ course.course_name }}
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
            
            <!-- 班级筛选 -->
            <div class="filter-item">
              <label class="filter-label">班级:</label>
              <select v-model="filters.class" class="filter-select">
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
        
        <div class="actions-bar">
          <!-- 添加选课按钮 -->
          <button 
            @click="openAddSelectionDialog"
            class="action-btn primary-btn add-selection-btn"
          >
            <span class="btn-icon">➕</span>
            添加选课
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
              @click="exportData"
              class="action-btn secondary-btn"
              :disabled="filteredSelectionData.length === 0"
            >
              <span class="btn-icon">📤</span>
              导出数据
            </button>

            <!-- 批量操作下拉菜单 -->
            <div class="dropdown">
              <button class="action-btn secondary-btn dropdown-toggle">
                <span class="btn-icon">⚙️</span>
                批量操作
              </button>
              <div class="dropdown-menu">
                <button @click="openBulkImportDialog" class="dropdown-item">
                  <span class="dropdown-icon">📥</span>
                  批量导入
                </button>
                <button @click="batchDeleteSelected" class="dropdown-item">
                  <span class="dropdown-icon">🗑️</span>
                  批量删除
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 数据展示区域 - 表格视图 -->
      <div v-if="filteredSelectionData.length > 0 && !loading" class="data-container">
        <div class="results-header">
          <h3 class="results-title">
            选课信息总览
            <span class="results-count">(共 {{ filteredSelectionData.length }} 条选课记录)</span>
          </h3>
          <div class="view-controls">
            <span class="view-label">成绩状态:</span>
            <div class="view-toggle">
              <button 
                :class="['view-option', { active: gradeFilter === 'all' }]"
                @click="gradeFilter = 'all'"
              >
                全部
              </button>
              <button 
                :class="['view-option', { active: gradeFilter === 'graded' }]"
                @click="gradeFilter = 'graded'"
              >
                已评分
              </button>
              <button 
                :class="['view-option', { active: gradeFilter === 'ungraded' }]"
                @click="gradeFilter = 'ungraded'"
              >
                未评分
              </button>
            </div>
            
            <!-- 批量选择 -->
            <div class="batch-controls" v-if="selectedSelections.length > 0">
              <span class="batch-count">已选择 {{ selectedSelections.length }} 项</span>
              <button @click="clearSelection" class="batch-clear-btn">清除选择</button>
            </div>
          </div>
        </div>
        
        <div class="table-container">
          <table class="selections-table">
            <thead>
              <tr>
                <th width="40">
                  <input 
                    type="checkbox" 
                    v-model="selectAll"
                    @change="toggleSelectAll"
                    class="selection-checkbox"
                  >
                </th>
                <th>选课ID</th>
                <th>学生信息</th>
                <th>课程信息</th>
                <th>学期</th>
                <th>授课教师</th>
                <th>成绩</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="selection in finalFilteredData" :key="selection.selection_id" 
                  :class="{ 'selected': isSelected(selection.selection_id) }">
                <td>
                  <input 
                    type="checkbox" 
                    :value="selection.selection_id"
                    v-model="selectedSelections"
                    class="selection-checkbox"
                  >
                </td>
                <td>{{ selection.selection_id }}</td>
                <td>
                  <div class="student-info">
                    <div class="student-name">{{ selection.student_name }}</div>
                    <div class="student-details">
                      <span class="student-id">学号: {{ selection.student_id }}</span>
                      <span class="class-name">班级: {{ selection.class_name }}</span>
                    </div>
                  </div>
                </td>
                <td>
                  <div class="course-info">
                    <div class="course-name">{{ selection.course_name }}</div>
                    <div class="course-type">{{ selection.course_type }}</div>
                  </div>
                </td>
                <td>{{ selection.semester_name }}</td>
                <td>{{ selection.teacher_name }}</td>
                <td>
                  <span v-if="!isEditing(selection.selection_id)" 
                        :class="['grade-display', { 
                          'excellent': selection.grade >= 90, 
                          'good': selection.grade >= 80 && selection.grade < 90,
                          'average': selection.grade >= 70 && selection.grade < 80,
                          'pass': selection.grade >= 60 && selection.grade < 70,
                          'fail': selection.grade < 60 && selection.grade !== null,
                          'no-grade': selection.grade === null 
                        }]">
                    {{ selection.grade !== null ? selection.grade : '未评分' }}
                  </span>
                  <div v-else class="edit-grade-container">
                    <input 
                      type="number"
                      v-model="editingSelection.grade"
                      class="edit-input grade-input"
                      placeholder="请输入成绩"
                      min="0"
                      max="100"
                      step="0.1"
                    >
                    <span class="grade-hint">(0-100)</span>
                  </div>
                </td>
                <td>
                  <div class="action-buttons">
                    <button 
                      v-if="!isEditing(selection.selection_id)"
                      @click="startEdit(selection)"
                      class="icon-btn edit-btn"
                      title="编辑成绩"
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
                      v-if="!isEditing(selection.selection_id)"
                      @click="showDetailDialog(selection)"
                      class="icon-btn view-btn"
                      title="查看详情"
                    >
                      👁️
                    </button>
                    <button 
                      v-if="!isEditing(selection.selection_id)"
                      @click="deleteSelection(selection)"
                      class="icon-btn delete-btn"
                      title="删除选课"
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
      <div v-if="filteredSelectionData.length === 0 && !loading" class="no-data-container">
        <div class="no-data-content">
          <div class="no-data-icon">📚</div>
          <h3 v-if="selectionData.length === 0">暂无选课数据</h3>
          <h3 v-else>没有找到匹配的选课记录</h3>
          <p v-if="selectionData.length === 0">还没有添加任何选课记录，点击下方按钮开始添加</p>
          <p v-else>当前筛选条件下没有找到匹配的选课记录，请尝试调整筛选条件</p>
          <div class="no-data-actions">
            <button 
              @click="openAddSelectionDialog"
              class="no-data-action-btn"
            >
              <span class="btn-icon">➕</span>
              添加选课
            </button>
            <button 
              v-if="selectionData.length > 0"
              @click="resetFilters"
              class="no-data-action-btn secondary"
            >
              <span class="btn-icon">🔄</span>
              重置筛选
            </button>
          </div>
        </div>
      </div>

      <!-- 添加/编辑选课对话框 -->
      <div v-if="showSelectionDialog" class="modal-overlay" @click.self="closeSelectionDialog">
        <div class="modal-dialog large-dialog selection-form-dialog">
          <div class="modal-header">
            <h3>
              <span class="dialog-icon">{{ isEditingSelection ? '✏️' : '➕' }}</span>
              {{ isEditingSelection ? '编辑选课记录' : '添加选课记录' }}
            </h3>
            <button @click="closeSelectionDialog" class="modal-close">×</button>
          </div>
          
          <div class="modal-body">
            <form @submit.prevent="isEditingSelection ? updateSelection() : addNewSelection()" class="selection-form">
              <div class="form-sections">
                <!-- 基本信息 -->
                <div class="form-section">
                  <h4 class="section-title">
                    <span class="section-icon">📋</span>
                    选课信息
                  </h4>
                  <div class="form-columns">
                    <div class="form-column">
                      <div class="form-group">
                        <label class="required">学生</label>
                        <select 
                          v-model="currentSelection.student_id" 
                          required 
                          class="form-select"
                          :disabled="isEditingSelection"
                        >
                          <option value="">请选择学生</option>
                          <option 
                            v-for="student in baseData.students" 
                            :key="student.student_id" 
                            :value="student.student_id"
                          >
                            {{ student.student_name }} ({{ student.student_id }}) - {{ student.class_name }}
                          </option>
                        </select>
                      </div>
                      
                      <div class="form-group">
                        <label class="required">课程</label>
                        <select 
                          v-model="currentSelection.course_id" 
                          required 
                          class="form-select"
                          :disabled="isEditingSelection"
                        >
                          <option value="">请选择课程</option>
                          <option 
                            v-for="course in baseData.courses" 
                            :key="course.course_id" 
                            :value="course.course_id"
                          >
                            {{ course.course_name }} ({{ course.course_type }})
                          </option>
                        </select>
                      </div>
                    </div>
                    
                    <div class="form-column">
                      <div class="form-group">
                        <label class="required">学期</label>
                        <select 
                          v-model="currentSelection.semester_id" 
                          required 
                          class="form-select"
                          :disabled="isEditingSelection"
                        >
                          <option value="">请选择学期</option>
                          <option 
                            v-for="semester in baseData.semesters" 
                            :key="semester.semester_id" 
                            :value="semester.semester_id"
                          >
                            {{ semester.semester_name }}
                          </option>
                        </select>
                      </div>
                      
                      <div class="form-group">
                        <label>成绩</label>
                        <input 
                          type="number" 
                          v-model="currentSelection.grade" 
                          class="form-input"
                          placeholder="请输入成绩（可选）"
                          min="0"
                          max="100"
                          step="0.1"
                        >
                        <div class="input-hint">成绩范围：0-100，留空表示未评分</div>
                      </div>
                    </div>
                  </div>
                </div>
                
                <!-- 预览信息 -->
                <div v-if="showPreview" class="form-section">
                  <h4 class="section-title">
                    <span class="section-icon">👁️</span>
                    信息预览
                  </h4>
                  <div class="preview-info">
                    <div class="preview-item">
                      <label>学生:</label>
                      <span>{{ getStudentName(currentSelection.student_id) }}</span>
                    </div>
                    <div class="preview-item">
                      <label>课程:</label>
                      <span>{{ getCourseName(currentSelection.course_id) }}</span>
                    </div>
                    <div class="preview-item">
                      <label>学期:</label>
                      <span>{{ getSemesterName(currentSelection.semester_id) }}</span>
                    </div>
                    <div class="preview-item">
                      <label>成绩:</label>
                      <span>{{ currentSelection.grade || '未设置' }}</span>
                    </div>
                  </div>
                </div>
              </div>
              
              <div class="form-actions">
                <button type="button" @click="closeSelectionDialog" class="btn cancel-btn">
                  取消
                </button>
                <button type="submit" class="btn primary-btn submit-btn" :disabled="savingSelection">
                  <span v-if="savingSelection" class="loading-spinner-small"></span>
                  {{ savingSelection ? '保存中...' : (isEditingSelection ? '更新选课' : '添加选课') }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>

      <!-- 选课详情对话框 -->
      <div v-if="showDetailDialogFlag" class="modal-overlay" @click.self="closeDetailDialog">
        <div class="modal-dialog">
          <div class="modal-header">
            <h3>
              <span class="dialog-icon">👁️</span>
              选课详细信息
            </h3>
            <button @click="closeDetailDialog" class="modal-close">×</button>
          </div>
          
          <div class="modal-body">
            <div class="selection-detail">
              <div class="detail-section">
                <h4>学生信息</h4>
                <div class="detail-grid">
                  <div class="detail-item">
                    <label>学号：</label>
                    <span>{{ currentSelection.student_id }}</span>
                  </div>
                  <div class="detail-item">
                    <label>姓名：</label>
                    <span>{{ currentSelection.student_name }}</span>
                  </div>
                  <div class="detail-item">
                    <label>班级：</label>
                    <span>{{ currentSelection.class_name }}</span>
                  </div>
                </div>
              </div>
              
              <div class="detail-section">
                <h4>课程信息</h4>
                <div class="detail-grid">
                  <div class="detail-item">
                    <label>课程ID：</label>
                    <span>{{ currentSelection.course_id }}</span>
                  </div>
                  <div class="detail-item">
                    <label>课程名称：</label>
                    <span>{{ currentSelection.course_name }}</span>
                  </div>
                  <div class="detail-item">
                    <label>课程类型：</label>
                    <span>{{ currentSelection.course_type }}</span>
                  </div>
                </div>
              </div>
              
              <div class="detail-section">
                <h4>其他信息</h4>
                <div class="detail-grid">
                  <div class="detail-item">
                    <label>学期：</label>
                    <span>{{ currentSelection.semester_name }}</span>
                  </div>
                  <div class="detail-item">
                    <label>授课教师：</label>
                    <span>{{ currentSelection.teacher_name }}</span>
                  </div>
                  <div class="detail-item">
                    <label>成绩：</label>
                    <span :class="['grade-detail', { 
                      'excellent': currentSelection.grade >= 90, 
                      'good': currentSelection.grade >= 80 && currentSelection.grade < 90,
                      'average': currentSelection.grade >= 70 && currentSelection.grade < 80,
                      'pass': currentSelection.grade >= 60 && currentSelection.grade < 70,
                      'fail': currentSelection.grade < 60 && currentSelection.grade !== null,
                      'no-grade': currentSelection.grade === null 
                    }]">
                      {{ currentSelection.grade !== null ? currentSelection.grade : '未评分' }}
                    </span>
                  </div>
                  <div class="detail-item" v-if="currentSelection.created_at">
                    <label>创建时间：</label>
                    <span>{{ formatDateTime(currentSelection.created_at) }}</span>
                  </div>
                </div>
              </div>
            </div>
            
            <div class="detail-actions">
              <button @click="startEditFromDetail" class="btn primary-btn">
                ✏️ 编辑成绩
              </button>
              <button @click="deleteSelection(currentSelection)" class="btn danger-btn">
                🗑️ 删除选课
              </button>
              <button @click="closeDetailDialog" class="btn cancel-btn">
                关闭
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 批量导入对话框 -->
      <div v-if="showBulkImportDialog" class="modal-overlay" @click.self="closeBulkImportDialog">
        <div class="modal-dialog large-dialog">
          <div class="modal-header">
            <h3>
              <span class="dialog-icon">📥</span>
              批量导入选课记录
            </h3>
            <button @click="closeBulkImportDialog" class="modal-close">×</button>
          </div>
          
          <div class="modal-body">
            <div class="bulk-import-content">
              <div class="import-instructions">
                <h4>导入说明</h4>
                <p>请按照以下格式准备数据：</p>
                <ul>
                  <li>支持 JSON 格式数据</li>
                  <li>每条记录包含：student_id, course_id, semester_id, grade（可选）</li>
                  <li>grade 为数值类型，范围 0-100</li>
                </ul>
                <div class="import-template">
                  <h5>数据模板：</h5>
                  <pre>{{ bulkImportTemplate }}</pre>
                  <button @click="copyTemplate" class="btn secondary-btn">
                    📋 复制模板
                  </button>
                </div>
              </div>
              
              <div class="import-data">
                <label class="required">导入数据</label>
                <textarea 
                  v-model="bulkImportData"
                  class="import-textarea"
                  placeholder="请粘贴或输入JSON格式的选课数据..."
                  rows="10"
                ></textarea>
              </div>
              
              <div v-if="importResults" class="import-results">
                <h4>导入结果</h4>
                <div class="result-stats">
                  <span class="result-success">成功: {{ importResults.success }}</span>
                  <span class="result-failed">失败: {{ importResults.failed }}</span>
                  <span class="result-total">总计: {{ importResults.total }}</span>
                </div>
                <div v-if="importResults.errors && importResults.errors.length > 0" class="result-errors">
                  <h5>错误详情：</h5>
                  <div v-for="error in importResults.errors" :key="error.index" class="error-item">
                    第{{ error.index + 1 }}行: {{ error.error }}
                  </div>
                </div>
              </div>
            </div>
            
            <div class="form-actions">
              <button type="button" @click="closeBulkImportDialog" class="btn cancel-btn">
                取消
              </button>
              <button @click="validateImportData" class="btn secondary-btn">
                验证数据
              </button>
              <button @click="executeBulkImport" class="btn primary-btn" :disabled="!bulkImportData.trim()">
                执行导入
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 老师授课管理标签页 -->
    <div v-if="activeTab === 'teachings'" class="tab-content">
      <!-- 控制区域 -->
      <div class="controls-container">
        <div class="header-section">
          <h2 class="section-title">
            <span class="title-icon">👨‍🏫</span>
            老师授课信息管理
          </h2>
          <div class="header-stats">
            <div class="stat-item">
              <span class="stat-number">{{ filteredTeachingData.length }}</span>
              <span class="stat-label">筛选结果</span>
            </div>
            <div class="stat-item">
              <span class="stat-number">{{ totalTeachings }}</span>
              <span class="stat-label">总授课数</span>
            </div>
            <div class="stat-item">
              <span class="stat-number">{{ uniqueTeachers }}</span>
              <span class="stat-label">涉及老师</span>
            </div>
          </div>
        </div>
        
        <!-- 筛选控制区域 -->
        <div class="filter-controls">
          <div class="filter-group">
            <!-- 老师搜索 -->
            <div class="filter-item">
              <label class="filter-label">老师搜索:</label>
              <input 
                type="text" 
                v-model="teachingFilters.teacherSearch" 
                placeholder="输入老师姓名" 
                class="filter-input"
              >
            </div>
            
            <!-- 课程筛选 -->
            <div class="filter-item">
              <label class="filter-label">课程:</label>
              <select v-model="teachingFilters.course" class="filter-select">
                <option value="">全部课程</option>
                <option 
                  v-for="course in availableTeachingCourses" 
                  :key="course.course_id" 
                  :value="course.course_id"
                >
                  {{ course.course_name }}
                </option>
              </select>
            </div>
            
            <!-- 学期筛选 -->
            <div class="filter-item">
              <label class="filter-label">学期:</label>
              <select v-model="teachingFilters.semester" class="filter-select">
                <option value="">全部学期</option>
                <option 
                  v-for="semester in availableTeachingSemesters" 
                  :key="semester.semester_id" 
                  :value="semester.semester_id"
                >
                  {{ semester.semester_name }}
                </option>
              </select>
            </div>
            
            <!-- 重置筛选按钮 -->
            <button @click="resetTeachingFilters" class="filter-reset-btn">
              重置筛选
            </button>
          </div>
        </div>
        
        <div class="actions-bar">
          <!-- 添加授课按钮 -->
          <button 
            @click="openAddTeachingDialog"
            class="action-btn primary-btn add-teaching-btn"
          >
            <span class="btn-icon">➕</span>
            添加授课
            <span class="btn-badge">NEW</span>
          </button>
          
          <div class="action-group">
            <button 
              @click="refreshTeachingData"
              class="action-btn secondary-btn"
              :disabled="loading"
            >
              <span class="btn-icon">🔄</span>
              刷新数据
            </button>

            <button 
              @click="exportTeachingData"
              class="action-btn secondary-btn"
              :disabled="filteredTeachingData.length === 0"
            >
              <span class="btn-icon">📤</span>
              导出数据
            </button>
          </div>
        </div>
      </div>
      
      <!-- 数据展示区域 - 可折叠表格 -->
      <div v-if="filteredTeachingData.length > 0 && !loading" class="data-container">
        <div class="results-header">
          <h3 class="results-title">
            授课信息总览
            <span class="results-count">(共 {{ filteredTeachingData.length }} 条授课记录)</span>
          </h3>
          <div class="view-controls">
            <button 
              @click="toggleAllTeachers"
              class="action-btn secondary-btn"
            >
              <span class="btn-icon">{{ allTeachersExpanded ? '📂' : '📁' }}</span>
              {{ allTeachersExpanded ? '全部折叠' : '全部展开' }}
            </button>
          </div>
        </div>
        
        <div class="table-container">
          <!-- 按老师分组的可折叠表格 -->
          <div v-for="teacher in groupedTeachingData" :key="teacher.teacher_id" class="teacher-group">
            <div class="teacher-header" @click="toggleTeacher(teacher.teacher_id)">
              <div class="teacher-info">
                  <span class="toggle-icon">{{ expandedTeachers[teacher.teacher_id] ? '📂' : '📁' }}</span>
                  <span class="teacher-id">ID: {{ teacher.teacher_id }}</span>
                  <span class="teacher-name">{{ teacher.teacher_name }}</span>
                  <span class="teacher-title">{{ teacher.teacher_title }}</span>
                  <span class="teaching-count">({{ teacher.teachings.length }} 门课程)</span>
              </div>
              <div class="teacher-actions">
                <button 
                  @click.stop="openAddTeachingDialog(teacher.teacher_id)"
                  class="icon-btn add-btn"
                  title="为此老师添加授课"
                >
                  ➕
                </button>
              </div>
            </div>
            
            <div v-if="expandedTeachers[teacher.teacher_id]" class="teaching-list">
              <table class="teachings-table">
                <thead>
                  <tr>
                    <th>课程名称</th>
                    <th>课程类型</th>
                    <th>学期</th>
                    <th>学生人数</th>
                    <th>操作</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="teaching in teacher.teachings" :key="teaching.teaching_id">
                    <td>
                      <div class="course-info">
                        <div class="course-name">{{ teaching.course_name }}</div>
                      </div>
                    </td>
                    <td>{{ teaching.course_type }}</td>
                    <td>{{ teaching.semester_name }}</td>
                    <td>
                      <span class="student-count">{{ teaching.student_count }} 人</span>
                    </td>
                    <td>
                      <div class="action-buttons">
                        <button 
                          @click="editTeaching(teaching)"
                          class="icon-btn edit-btn"
                          title="编辑授课"
                        >
                          ✏️
                        </button>
                        <button 
                          @click="deleteTeaching(teaching)"
                          class="icon-btn delete-btn"
                          title="删除授课"
                        >
                          🗑️
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
      <div v-if="filteredTeachingData.length === 0 && !loading" class="no-data-container">
        <div class="no-data-content">
          <div class="no-data-icon">👨‍🏫</div>
          <h3 v-if="teachingData.length === 0">暂无授课数据</h3>
          <h3 v-else>没有找到匹配的授课记录</h3>
          <p v-if="teachingData.length === 0">还没有添加任何授课记录，点击下方按钮开始添加</p>
          <p v-else>当前筛选条件下没有找到匹配的授课记录，请尝试调整筛选条件</p>
          <div class="no-data-actions">
            <button 
              @click="openAddTeachingDialog"
              class="no-data-action-btn"
            >
              <span class="btn-icon">➕</span>
              添加授课
            </button>
            <button 
              v-if="teachingData.length > 0"
              @click="resetTeachingFilters"
              class="no-data-action-btn secondary"
            >
              <span class="btn-icon">🔄</span>
              重置筛选
            </button>
          </div>
        </div>
      </div>

      <!-- 添加/编辑授课对话框 -->
      <div v-if="showTeachingDialog" class="modal-overlay" @click.self="closeTeachingDialog">
        <div class="modal-dialog large-dialog teaching-form-dialog">
          <div class="modal-header">
            <h3>
              <span class="dialog-icon">{{ isEditingTeaching ? '✏️' : '➕' }}</span>
              {{ isEditingTeaching ? '编辑授课记录' : '添加授课记录' }}
            </h3>
            <button @click="closeTeachingDialog" class="modal-close">×</button>
          </div>
          
          <div class="modal-body">
            <form @submit.prevent="isEditingTeaching ? updateTeaching() : addNewTeaching()" class="teaching-form">
              <div class="form-sections">
                <!-- 基本信息 -->
                <div class="form-section">
                  <h4 class="section-title">
                    <span class="section-icon">📋</span>
                    授课信息
                  </h4>
                  <div class="form-columns">
                    <div class="form-column">
                      <div class="form-group">
                        <label class="required">老师</label>
                        <select 
                          v-model="currentTeaching.teacher_id" 
                          required 
                          class="form-select"
                          :disabled="isEditingTeaching"
                        >
                          <option value="">请选择老师</option>
                         <option 
                            v-for="teacher in baseData.teachers" 
                            :key="teacher.teacher_id" 
                            :value="teacher.teacher_id"
                          >
                            {{ getTeacherInfo(teacher.teacher_id) }}
                          </option>
                        </select>
                      </div>
                      
                      <div class="form-group">
                        <label class="required">课程</label>
                        <select 
                          v-model="currentTeaching.course_id" 
                          required 
                          class="form-select"
                          :disabled="isEditingTeaching"
                        >
                          <option value="">请选择课程</option>
                          <option 
                            v-for="course in baseData.courses" 
                            :key="course.course_id" 
                            :value="course.course_id"
                          >
                            {{ course.course_name }} ({{ course.course_type }})
                          </option>
                        </select>
                      </div>
                    </div>
                    
                    <div class="form-column">
                      <div class="form-group">
                        <label class="required">学期</label>
                        <select 
                          v-model="currentTeaching.semester_id" 
                          required 
                          class="form-select"
                          :disabled="isEditingTeaching"
                        >
                          <option value="">请选择学期</option>
                          <option 
                            v-for="semester in baseData.semesters" 
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
                
                <!-- 预览信息 -->
                <div v-if="showTeachingPreview" class="form-section">
                  <h4 class="section-title">
                    <span class="section-icon">👁️</span>
                    信息预览
                  </h4>
                  <div class="preview-info">
                    <div class="preview-item">
                      <label>老师:</label>
                      <span>{{ getTeacherName(currentTeaching.teacher_id) }}</span>
                    </div>
                    <div class="preview-item">
                      <label>课程:</label>
                      <span>{{ getCourseName(currentTeaching.course_id) }}</span>
                    </div>
                    <div class="preview-item">
                      <label>学期:</label>
                      <span>{{ getSemesterName(currentTeaching.semester_id) }}</span>
                    </div>
                  </div>
                </div>
              </div>
              
              <div class="form-actions">
                <button type="button" @click="closeTeachingDialog" class="btn cancel-btn">
                  取消
                </button>
                <button type="submit" class="btn primary-btn submit-btn" :disabled="savingTeaching">
                  <span v-if="savingTeaching" class="loading-spinner-small"></span>
                  {{ savingTeaching ? '保存中...' : (isEditingTeaching ? '更新授课' : '添加授课') }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { ADMIN_API } from '@/config/apiConfig'

// 响应式数据
const activeTab = ref('selections') // 'selections' 或 'teachings'

// 选课管理相关数据
const selectionData = ref([])
const baseData = ref({
  students: [],
  courses: [],
  semesters: [],
  classes: [],
  teachers: []
})
const loading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const gradeFilter = ref('all') // 'all', 'graded', 'ungraded'

// 筛选条件
const filters = ref({
  studentSearch: '',
  course: '',
  semester: '',
  class: ''
})

// 对话框状态
const showSelectionDialog = ref(false)
const showDetailDialogFlag = ref(false)
const showBulkImportDialog = ref(false)
const isEditingSelection = ref(false)
const savingSelection = ref(false)

// 当前操作的选课记录
const currentSelection = ref(createEmptySelection())

// 编辑状态
const editingSelectionId = ref(null)
const editingSelection = ref({})

// 批量操作
const selectedSelections = ref([])
const selectAll = ref(false)

// 批量导入
const bulkImportData = ref('')
const importResults = ref(null)
const bulkImportTemplate = `[
  {
    "student_id": 1001,
    "course_id": 1,
    "semester_id": 1,
    "grade": 85.5
  },
  {
    "student_id": 1002,
    "course_id": 2,
    "semester_id": 1,
    "grade": 92.0
  }
]`

// 老师授课管理相关数据
const teachingData = ref([])
const teachingFilters = ref({
  teacherSearch: '',
  course: '',
  semester: ''
})
const showTeachingDialog = ref(false)
const isEditingTeaching = ref(false)
const savingTeaching = ref(false)
const currentTeaching = ref(createEmptyTeaching())
const expandedTeachers = ref({})
const allTeachersExpanded = ref(false)

// 计算属性 - 选课管理
const totalSelections = computed(() => {
  return selectionData.value.length
})

const uniqueStudents = computed(() => {
  const studentIds = new Set(selectionData.value.map(item => item.student_id))
  return studentIds.size
})

// 筛选后的选课数据
const filteredSelectionData = computed(() => {
  if (!selectionData.value.length) return []
  
  return selectionData.value.filter(selection => {
    // 学生搜索筛选（姓名或学号）
    if (filters.value.studentSearch) {
      const searchLower = filters.value.studentSearch.toLowerCase()
      const nameMatch = selection.student_name?.toLowerCase().includes(searchLower)
      const idMatch = selection.student_id?.toString().includes(searchLower)
      if (!nameMatch && !idMatch) return false
    }
    
    // 课程筛选
    if (filters.value.course && selection.course_id !== parseInt(filters.value.course)) {
      return false
    }
    
    // 学期筛选
    if (filters.value.semester && selection.semester_id !== parseInt(filters.value.semester)) {
      return false
    }
    
    // 班级筛选
    if (filters.value.class && selection.class_id !== parseInt(filters.value.class)) {
      return false
    }
    
    return true
  })
})

// 最终过滤数据（包含成绩状态过滤）
const finalFilteredData = computed(() => {
  let data = filteredSelectionData.value
  
  if (gradeFilter.value === 'graded') {
    data = data.filter(selection => selection.grade !== null)
  } else if (gradeFilter.value === 'ungraded') {
    data = data.filter(selection => selection.grade === null)
  }
  
  return data
})

// 预览信息显示
const showPreview = computed(() => {
  return currentSelection.value.student_id && currentSelection.value.course_id && currentSelection.value.semester_id
})

// 检查是否选中
const isSelected = (selectionId) => {
  return selectedSelections.value.includes(selectionId)
}

// 计算属性 - 老师授课管理
const totalTeachings = computed(() => {
  return teachingData.value.length
})

const uniqueTeachers = computed(() => {
  const teacherIds = new Set(teachingData.value.map(item => item.teacher_id))
  return teacherIds.size
})

// 筛选后的授课数据
const filteredTeachingData = computed(() => {
  if (!teachingData.value.length) return []
  
  return teachingData.value.filter(teaching => {
    // 老师搜索筛选（姓名或ID）
    if (teachingFilters.value.teacherSearch) {
      const searchLower = teachingFilters.value.teacherSearch.toLowerCase()
      const nameMatch = teaching.teacher_name?.toLowerCase().includes(searchLower)
      const idMatch = teaching.teacher_id?.toString().includes(searchLower)
      if (!nameMatch && !idMatch) return false
    }
    
    // 课程筛选
    if (teachingFilters.value.course && teaching.course_id !== parseInt(teachingFilters.value.course)) {
      return false
    }
    
    // 学期筛选
    if (teachingFilters.value.semester && teaching.semester_id !== parseInt(teachingFilters.value.semester)) {
      return false
    }
    
    return true
  })
})

// 按老师分组的授课数据
const groupedTeachingData = computed(() => {
  const teacherMap = new Map()
  
  filteredTeachingData.value.forEach(teaching => {
    if (!teacherMap.has(teaching.teacher_id)) {
      teacherMap.set(teaching.teacher_id, {
        teacher_id: teaching.teacher_id,
        teacher_name: teaching.teacher_name,
        teacher_title: teaching.teacher_title,
        teachings: []
      })
    }
    teacherMap.get(teaching.teacher_id).teachings.push(teaching)
  })
  
  return Array.from(teacherMap.values()).sort((a, b) => a.teacher_name.localeCompare(b.teacher_name))
})

// 授课预览信息显示
const showTeachingPreview = computed(() => {
  return currentTeaching.value.teacher_id && currentTeaching.value.course_id && currentTeaching.value.semester_id
})

// 可用课程列表 - 选课管理
const availableCourses = computed(() => {
  const courses = new Map()
  selectionData.value.forEach(selection => {
    if (!courses.has(selection.course_id)) {
      courses.set(selection.course_id, {
        course_id: selection.course_id,
        course_name: selection.course_name
      })
    }
  })
  return Array.from(courses.values()).sort((a, b) => a.course_name.localeCompare(b.course_name))
})

// 可用学期列表 - 选课管理
const availableSemesters = computed(() => {
  const semesters = new Map()
  selectionData.value.forEach(selection => {
    if (!semesters.has(selection.semester_id)) {
      semesters.set(selection.semester_id, {
        semester_id: selection.semester_id,
        semester_name: selection.semester_name
      })
    }
  })
  return Array.from(semesters.values()).sort((a, b) => b.semester_id - a.semester_id)
})

// 可用班级列表 - 选课管理
const availableClasses = computed(() => {
  const classes = new Map()
  selectionData.value.forEach(selection => {
    if (!classes.has(selection.class_id)) {
      classes.set(selection.class_id, {
        class_id: selection.class_id,
        class_name: selection.class_name
      })
    }
  })
  return Array.from(classes.values()).sort((a, b) => a.class_name.localeCompare(b.class_name))
})

// 可用课程列表 - 老师授课管理
const availableTeachingCourses = computed(() => {
  const courses = new Map()
  teachingData.value.forEach(teaching => {
    if (!courses.has(teaching.course_id)) {
      courses.set(teaching.course_id, {
        course_id: teaching.course_id,
        course_name: teaching.course_name
      })
    }
  })
  return Array.from(courses.values()).sort((a, b) => a.course_name.localeCompare(b.course_name))
})

// 可用学期列表 - 老师授课管理
const availableTeachingSemesters = computed(() => {
  const semesters = new Map()
  teachingData.value.forEach(teaching => {
    if (!semesters.has(teaching.semester_id)) {
      semesters.set(teaching.semester_id, {
        semester_id: teaching.semester_id,
        semester_name: teaching.semester_name
      })
    }
  })
  return Array.from(semesters.values()).sort((a, b) => b.semester_id - a.semester_id)
})

// 创建空选课记录对象
function createEmptySelection() {
  return {
    selection_id: null,
    student_id: '',
    course_id: '',
    semester_id: '',
    grade: null
  }
}

// 创建空授课记录对象
function createEmptyTeaching() {
  return {
    teacher_id: '',
    course_id: '',
    semester_id: '',
    original_teacher_id: '',
    original_course_id: '',
    original_semester_id: ''
  }
}

// 获取学生姓名
function getStudentName(studentId) {
  const student = baseData.value.students.find(s => s.student_id === studentId)
  return student ? `${student.student_name} (${student.student_id}) - ${student.class_name}` : '未知学生'
}

// 获取课程名称
function getCourseName(courseId) {
  const course = baseData.value.courses.find(c => c.course_id === courseId)
  return course ? `${course.course_name} (${course.course_type})` : '未知课程'
}

// 获取学期名称
function getSemesterName(semesterId) {
  const semester = baseData.value.semesters.find(s => s.semester_id === semesterId)
  return semester ? semester.semester_name : '未知学期'
}

// 获取老师信息（包含ID和姓名）
function getTeacherInfo(teacherId) {
  const teacher = baseData.value.teachers.find(t => t.teacher_id === teacherId)
  return teacher ? `${teacher.teacher_name} (ID: ${teacher.teacher_id}) - ${teacher.teacher_title}` : '未知老师'
}

// 获取老师姓名
function getTeacherName(teacherId) {
  const teacher = baseData.value.teachers.find(t => t.teacher_id === teacherId)
  return teacher ? teacher.teacher_name : '未知老师'
}

// 格式化日期时间
function formatDateTime(dateTimeString) {
  if (!dateTimeString) return ''
  const date = new Date(dateTimeString)
  return date.toLocaleString('zh-CN')
}

// 重置筛选条件 - 选课管理
const resetFilters = () => {
  filters.value = {
    studentSearch: '',
    course: '',
    semester: '',
    class: ''
  }
  gradeFilter.value = 'all'
}

// 重置筛选条件 - 老师授课管理
const resetTeachingFilters = () => {
  teachingFilters.value = {
    teacherSearch: '',
    course: '',
    semester: ''
  }
}

// 导出数据 - 选课管理
const exportData = () => {
  const dataStr = JSON.stringify(finalFilteredData.value, null, 2)
  const dataBlob = new Blob([dataStr], { type: 'application/json' })
  const url = URL.createObjectURL(dataBlob)
  const link = document.createElement('a')
  link.href = url
  link.download = `选课数据_${new Date().toISOString().split('T')[0]}.json`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
  
  successMessage.value = '数据导出成功'
  setTimeout(() => {
    successMessage.value = ''
  }, 3000)
}

// 导出数据 - 老师授课管理
const exportTeachingData = () => {
  const dataStr = JSON.stringify(filteredTeachingData.value, null, 2)
  const dataBlob = new Blob([dataStr], { type: 'application/json' })
  const url = URL.createObjectURL(dataBlob)
  const link = document.createElement('a')
  link.href = url
  link.download = `授课数据_${new Date().toISOString().split('T')[0]}.json`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
  
  successMessage.value = '授课数据导出成功'
  setTimeout(() => {
    successMessage.value = ''
  }, 3000)
}

// 全选/取消全选
const toggleSelectAll = () => {
  if (selectAll.value) {
    selectedSelections.value = finalFilteredData.value.map(item => item.selection_id)
  } else {
    selectedSelections.value = []
  }
}

// 清除选择
const clearSelection = () => {
  selectedSelections.value = []
  selectAll.value = false
}

// 批量删除选中的记录
const batchDeleteSelected = async () => {
  if (selectedSelections.value.length === 0) {
    errorMessage.value = '请先选择要删除的选课记录'
    return
  }

  if (!confirm(`确定要删除选中的 ${selectedSelections.value.length} 条选课记录吗？此操作不可撤销！`)) {
    return
  }

  try {
    const token = localStorage.getItem('jwt_token')
    let successCount = 0
    let errorCount = 0

    for (const selectionId of selectedSelections.value) {
      try {
        const response = await axios.delete(ADMIN_API.COURSE_SELECTION_MANAGEMENT, {
          headers: { 'Authorization': `Bearer ${token}` },
          data: { selection_id: selectionId }
        })

        if (response.data.status === 'success') {
          successCount++
          // 从本地数据中移除
          selectionData.value = selectionData.value.filter(s => s.selection_id !== selectionId)
        } else {
          errorCount++
        }
      } catch (error) {
        errorCount++
      }
    }

    clearSelection()
    
    if (errorCount === 0) {
      successMessage.value = `成功删除 ${successCount} 条选课记录`
    } else {
      successMessage.value = `删除完成：成功 ${successCount} 条，失败 ${errorCount} 条`
    }
    
    setTimeout(() => {
      successMessage.value = ''
    }, 3000)
  } catch (error) {
    errorMessage.value = '批量删除过程中发生错误'
  }
}

// 打开批量导入对话框
const openBulkImportDialog = () => {
  showBulkImportDialog.value = true
  importResults.value = null
  bulkImportData.value = ''
}

// 关闭批量导入对话框
const closeBulkImportDialog = () => {
  showBulkImportDialog.value = false
  importResults.value = null
  bulkImportData.value = ''
}

// 复制模板
const copyTemplate = () => {
  navigator.clipboard.writeText(bulkImportTemplate).then(() => {
    successMessage.value = '模板已复制到剪贴板'
    setTimeout(() => {
      successMessage.value = ''
    }, 2000)
  })
}

// 验证导入数据
const validateImportData = () => {
  if (!bulkImportData.value.trim()) {
    errorMessage.value = '请输入要导入的数据'
    return
  }

  try {
    const data = JSON.parse(bulkImportData.value)
    if (!Array.isArray(data)) {
      throw new Error('数据必须是数组格式')
    }

    let validCount = 0
    const errors = []

    data.forEach((item, index) => {
      if (!item.student_id || !item.course_id || !item.semester_id) {
        errors.push({
          index,
          error: '缺少必要字段: student_id, course_id, semester_id'
        })
        return
      }

      if (item.grade !== undefined && item.grade !== null) {
        const grade = parseFloat(item.grade)
        if (isNaN(grade) || grade < 0 || grade > 100) {
          errors.push({
            index,
            error: '成绩必须在0-100之间'
          })
          return
        }
      }

      validCount++
    })

    if (errors.length === 0) {
      successMessage.value = `数据验证通过：${validCount} 条记录格式正确`
    } else {
      errorMessage.value = `数据验证失败：${errors.length} 条记录有错误`
      importResults.value = {
        total: data.length,
        success: 0,
        failed: errors.length,
        errors: errors
      }
    }
  } catch (error) {
    errorMessage.value = `JSON格式错误: ${error.message}`
  }
}

// 执行批量导入
const executeBulkImport = async () => {
  if (!bulkImportData.value.trim()) {
    errorMessage.value = '请输入要导入的数据'
    return
  }

  try {
    const data = JSON.parse(bulkImportData.value)
    const token = localStorage.getItem('jwt_token')

    const response = await axios.post(ADMIN_API.COURSE_SELECTION_BULK_IMPORT, {
      selections: data
    }, {
      headers: { 'Authorization': `Bearer ${token}` }
    })

    if (response.data.status === 'success') {
      importResults.value = response.data.results
      successMessage.value = response.data.message
      
      // 刷新数据
      if (importResults.value.success > 0) {
        fetchSelectionData()
      }
    } else {
      errorMessage.value = response.data.error || '导入失败'
    }
  } catch (error) {
    handleApiError(error)
  }
}

// 老师授课管理 - 切换老师展开状态
const toggleTeacher = (teacherId) => {
  expandedTeachers.value[teacherId] = !expandedTeachers.value[teacherId]
}

// 老师授课管理 - 切换所有老师展开状态
const toggleAllTeachers = () => {
  allTeachersExpanded.value = !allTeachersExpanded.value
  groupedTeachingData.value.forEach(teacher => {
    expandedTeachers.value[teacher.teacher_id] = allTeachersExpanded.value
  })
}

// 老师授课管理 - 打开添加授课对话框
const openAddTeachingDialog = (teacherId = null) => {
  isEditingTeaching.value = false
  currentTeaching.value = createEmptyTeaching()
  if (teacherId) {
    currentTeaching.value.teacher_id = teacherId
  }
  showTeachingDialog.value = true
}

// 老师授课管理 - 编辑授课
const editTeaching = (teaching) => {
  isEditingTeaching.value = true
  currentTeaching.value = {
    teacher_id: teaching.teacher_id,
    course_id: teaching.course_id,
    semester_id: teaching.semester_id,
    original_teacher_id: teaching.teacher_id,
    original_course_id: teaching.course_id,
    original_semester_id: teaching.semester_id
  }
  showTeachingDialog.value = true
}

// 老师授课管理 - 删除授课
const deleteTeaching = async (teaching) => {
  if (!confirm(`确定要删除 ${teaching.teacher_name} (ID: ${teaching.teacher_id}) 教授的《${teaching.course_name}》授课记录吗？此操作不可撤销！`)) {
    return
  }

  try {
    const token = localStorage.getItem('jwt_token')
    const response = await axios.delete(ADMIN_API.TEACHING_MANAGEMENT, {
      headers: { 'Authorization': `Bearer ${token}` },
      data: {
        teacher_id: teaching.teacher_id,
        course_id: teaching.course_id,
        semester_id: teaching.semester_id
      }
    })

    if (response.data.status === 'success') {
      successMessage.value = '授课记录删除成功'
      
      // 从本地数据中移除
      teachingData.value = teachingData.value.filter(t => 
        !(t.teacher_id === teaching.teacher_id && 
          t.course_id === teaching.course_id && 
          t.semester_id === teaching.semester_id)
      )
      
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

// 老师授课管理 - 添加新授课记录
const addNewTeaching = async () => {
  if (!currentTeaching.value.teacher_id) {
    errorMessage.value = '请选择老师'
    return
  }

  if (!currentTeaching.value.course_id) {
    errorMessage.value = '请选择课程'
    return
  }

  if (!currentTeaching.value.semester_id) {
    errorMessage.value = '请选择学期'
    return
  }

  savingTeaching.value = true
  
  try {
    const token = localStorage.getItem('jwt_token')
    const response = await axios.post(ADMIN_API.TEACHING_MANAGEMENT, 
      {
        teacher_id: currentTeaching.value.teacher_id,
        course_id: currentTeaching.value.course_id,
        semester_id: currentTeaching.value.semester_id
      },
      {
        headers: { 'Authorization': `Bearer ${token}` }
      }
    )

    if (response.data.status === 'success') {
      successMessage.value = '授课记录添加成功'
      closeTeachingDialog()
      fetchTeachingData()
      
      setTimeout(() => {
        successMessage.value = ''
      }, 3000)
    } else {
      errorMessage.value = response.data.error || '添加失败'
    }
  } catch (error) {
    handleApiError(error)
  } finally {
    savingTeaching.value = false
  }
}

// 老师授课管理 - 更新授课记录
const updateTeaching = async () => {
  savingTeaching.value = true

  try {
    const token = localStorage.getItem('jwt_token')
    const response = await axios.put(ADMIN_API.TEACHING_MANAGEMENT, 
      {
        teacher_id: currentTeaching.value.original_teacher_id,
        course_id: currentTeaching.value.original_course_id,
        semester_id: currentTeaching.value.original_semester_id,
        new_teacher_id: currentTeaching.value.teacher_id,
        new_course_id: currentTeaching.value.course_id,
        new_semester_id: currentTeaching.value.semester_id
      },
      {
        headers: { 'Authorization': `Bearer ${token}` }
      }
    )

    if (response.data.status === 'success') {
      successMessage.value = '授课记录更新成功'
      closeTeachingDialog()
      fetchTeachingData()
      
      setTimeout(() => {
        successMessage.value = ''
      }, 3000)
    } else {
      errorMessage.value = response.data.error || '更新失败'
    }
  } catch (error) {
    handleApiError(error)
  } finally {
    savingTeaching.value = false
  }
}

// 老师授课管理 - 关闭授课对话框
const closeTeachingDialog = () => {
  showTeachingDialog.value = false
  isEditingTeaching.value = false
  savingTeaching.value = false
  currentTeaching.value = createEmptyTeaching()
}

// 老师授课管理 - 刷新数据
const refreshTeachingData = () => {
  fetchTeachingData()
}

// 生命周期
onMounted(() => {
  console.log('组件挂载，开始获取数据...')
  fetchSelectionData()
  fetchBaseData()
  fetchTeachingData()
})

// 获取选课数据
const fetchSelectionData = async () => {
  loading.value = true
  errorMessage.value = ''
  
  try {
    const token = localStorage.getItem('jwt_token')
    const response = await axios.get(ADMIN_API.COURSE_SELECTION_MANAGEMENT, {
      headers: { 'Authorization': `Bearer ${token}` }
    })

    console.log('选课数据响应:', response.data)

    if (response.data.status === 'success') {
      selectionData.value = response.data.data
      console.log('选课数据加载成功，数量:', selectionData.value.length)
    } else {
      errorMessage.value = response.data.error || '获取数据失败'
      console.error('获取选课数据失败:', response.data.error)
    }
  } catch (error) {
    console.error('获取选课数据异常:', error)
    handleApiError(error)
  } finally {
    loading.value = false
  }
}

// 获取基础数据
const fetchBaseData = async () => {
  try {
    const token = localStorage.getItem('jwt_token')
    const response = await axios.get(ADMIN_API.COURSE_SELECTION_BASE_DATA, {
      headers: { 'Authorization': `Bearer ${token}` }
    })

    console.log('基础数据响应:', response.data)

    if (response.data.status === 'success') {
      baseData.value = response.data.data
      console.log('基础数据加载成功')
    } else {
      console.error('获取基础数据失败:', response.data.error)
    }
  } catch (error) {
    console.error('获取基础数据异常:', error)
  }
}

// 获取授课数据
const fetchTeachingData = async () => {
  try {
    const token = localStorage.getItem('jwt_token')
    const response = await axios.get(ADMIN_API.TEACHING_MANAGEMENT, {
      headers: { 'Authorization': `Bearer ${token}` }
    })

    console.log('授课数据响应:', response.data)

    if (response.data.status === 'success') {
      teachingData.value = response.data.data
      
      // 初始化展开状态
      const teacherIds = new Set(teachingData.value.map(item => item.teacher_id))
      teacherIds.forEach(id => {
        if (expandedTeachers.value[id] === undefined) {
          expandedTeachers.value[id] = false
        }
      })
      
      console.log('授课数据加载成功，数量:', teachingData.value.length)
    } else {
      console.error('获取授课数据失败:', response.data.error)
      errorMessage.value = response.data.error || '获取授课数据失败'
    }
  } catch (error) {
    console.error('获取授课数据失败:', error)
    if (error.response) {
      console.error('错误状态:', error.response.status)
      console.error('错误数据:', error.response.data)
      errorMessage.value = `获取授课数据失败: ${error.response.data.error || error.response.statusText}`
    } else {
      errorMessage.value = '网络错误，无法获取授课数据'
    }
  }
}

// 刷新数据
const refreshData = () => {
  fetchSelectionData()
  fetchBaseData()
  clearSelection()
}

// 打开添加选课对话框
const openAddSelectionDialog = () => {
  isEditingSelection.value = false
  currentSelection.value = createEmptySelection()
  showSelectionDialog.value = true
}

// 开始编辑选课记录
const startEdit = (selection) => {
  editingSelectionId.value = selection.selection_id
  editingSelection.value = { ...selection }
}

// 从详情开始编辑
const startEditFromDetail = () => {
  showDetailDialogFlag.value = false
  isEditingSelection.value = true
  editingSelectionId.value = currentSelection.value.selection_id
  editingSelection.value = { ...currentSelection.value }
  currentSelection.value = { ...currentSelection.value }
  showSelectionDialog.value = true
}

// 取消编辑
const cancelEdit = () => {
  editingSelectionId.value = null
  editingSelection.value = {}
}

// 检查是否正在编辑
const isEditing = (selectionId) => {
  return editingSelectionId.value === selectionId
}

// 保存编辑（成绩）
const saveEdit = async () => {
  if (editingSelection.value.grade !== null && editingSelection.value.grade !== '') {
    const grade = parseFloat(editingSelection.value.grade)
    if (isNaN(grade) || grade < 0 || grade > 100) {
      errorMessage.value = '成绩必须在0-100之间'
      return
    }
  }

  try {
    const token = localStorage.getItem('jwt_token')
    const response = await axios.put(ADMIN_API.COURSE_SELECTION_MANAGEMENT, 
      {
        selection_id: editingSelectionId.value,
        grade: editingSelection.value.grade === '' ? null : editingSelection.value.grade
      },
      {
        headers: { 'Authorization': `Bearer ${token}` }
      }
    )

    if (response.data.status === 'success') {
      successMessage.value = '成绩更新成功'
      cancelEdit()
      fetchSelectionData()
      
      setTimeout(() => {
        successMessage.value = ''
      }, 3000)
    } else {
      errorMessage.value = response.data.error || '更新失败'
    }
  } catch (error) {
    handleApiError(error)
  }
}

// 显示选课详情
const showDetailDialog = (selection) => {
  currentSelection.value = { ...selection }
  showDetailDialogFlag.value = true
}

// 关闭详情对话框
const closeDetailDialog = () => {
  showDetailDialogFlag.value = false
  currentSelection.value = createEmptySelection()
}

// 删除选课记录
const deleteSelection = async (selection) => {
  if (!confirm(`确定要删除 ${selection.student_name} 的《${selection.course_name}》选课记录吗？此操作不可撤销！`)) {
    return
  }

  try {
    const token = localStorage.getItem('jwt_token')
    const response = await axios.delete(ADMIN_API.COURSE_SELECTION_MANAGEMENT, {
      headers: { 'Authorization': `Bearer ${token}` },
      data: { selection_id: selection.selection_id }
    })

    if (response.data.status === 'success') {
      successMessage.value = '选课记录删除成功'
      
      // 从本地数据中移除
      selectionData.value = selectionData.value.filter(s => s.selection_id !== selection.selection_id)
      // 从选中列表中移除
      selectedSelections.value = selectedSelections.value.filter(id => id !== selection.selection_id)
      
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

// 添加新选课记录
const addNewSelection = async () => {
  if (!currentSelection.value.student_id) {
    errorMessage.value = '请选择学生'
    return
  }

  if (!currentSelection.value.course_id) {
    errorMessage.value = '请选择课程'
    return
  }

  if (!currentSelection.value.semester_id) {
    errorMessage.value = '请选择学期'
    return
  }

  // 验证成绩
  if (currentSelection.value.grade !== null && currentSelection.value.grade !== '') {
    const grade = parseFloat(currentSelection.value.grade)
    if (isNaN(grade) || grade < 0 || grade > 100) {
      errorMessage.value = '成绩必须在0-100之间'
      return
    }
  }

  savingSelection.value = true
  
  try {
    const token = localStorage.getItem('jwt_token')
    const response = await axios.post(ADMIN_API.COURSE_SELECTION_MANAGEMENT, 
      {
        student_id: currentSelection.value.student_id,
        course_id: currentSelection.value.course_id,
        semester_id: currentSelection.value.semester_id,
        grade: currentSelection.value.grade === '' ? null : currentSelection.value.grade
      },
      {
        headers: { 'Authorization': `Bearer ${token}` }
      }
    )

    if (response.data.status === 'success') {
      successMessage.value = '选课记录添加成功'
      closeSelectionDialog()
      fetchSelectionData()
      
      setTimeout(() => {
        successMessage.value = ''
      }, 3000)
    } else {
      errorMessage.value = response.data.error || '添加失败'
    }
  } catch (error) {
    handleApiError(error)
  } finally {
    savingSelection.value = false
  }
}

// 更新选课记录
const updateSelection = async () => {
  if (currentSelection.value.grade !== null && currentSelection.value.grade !== '') {
    const grade = parseFloat(currentSelection.value.grade)
    if (isNaN(grade) || grade < 0 || grade > 100) {
      errorMessage.value = '成绩必须在0-100之间'
      return
    }
  }

  savingSelection.value = true

  try {
    const token = localStorage.getItem('jwt_token')
    const response = await axios.put(ADMIN_API.COURSE_SELECTION_MANAGEMENT, 
      {
        selection_id: currentSelection.value.selection_id,
        grade: currentSelection.value.grade === '' ? null : currentSelection.value.grade
      },
      {
        headers: { 'Authorization': `Bearer ${token}` }
      }
    )

    if (response.data.status === 'success') {
      successMessage.value = '选课记录更新成功'
      closeSelectionDialog()
      fetchSelectionData()
      
      setTimeout(() => {
        successMessage.value = ''
      }, 3000)
    } else {
      errorMessage.value = response.data.error || '更新失败'
    }
  } catch (error) {
    handleApiError(error)
  } finally {
    savingSelection.value = false
  }
}

// 关闭选课对话框
const closeSelectionDialog = () => {
  showSelectionDialog.value = false
  isEditingSelection.value = false
  savingSelection.value = false
  currentSelection.value = createEmptySelection()
  cancelEdit()
}

// 处理API错误
const handleApiError = (error) => {
  console.error('API错误详情:', error)
  
  if (error.response) {
    const status = error.response.status
    const data = error.response.data
    
    console.error('错误状态码:', status)
    console.error('错误响应数据:', data)
    
    if (data.status === 'failed' && data.error) {
      errorMessage.value = data.error
      return
    }
    
    switch (status) {
      case 400:
        errorMessage.value = '参数错误: ' + (data.error || '请求格式不正确')
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
        errorMessage.value = '无权限访问，仅限管理员用户: ' + (data.error || '')
        break
      case 500:
        errorMessage.value = '服务器错误，请稍后重试: ' + (data.error || '')
        break
      default:
        errorMessage.value = `请求失败 (${status}): ${data.error || '未知错误'}`
    }
  } else if (error.request) {
    console.error('网络请求失败:', error.request)
    errorMessage.value = '网络连接错误，请检查网络连接'
  } else {
    console.error('请求配置错误:', error.message)
    errorMessage.value = '请求发送失败: ' + error.message
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
/* 使用与学生管理页面完全一致的样式系统 */
.admin-course-selection-container {
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

/* 优化的添加按钮 */
.add-selection-btn, .add-teaching-btn {
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

.add-selection-btn:hover, .add-teaching-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6);
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

/* 表格容器 */
.table-container {
  width: 100%;
  overflow-x: auto;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.selections-table, .teachings-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 800px;
}

.selections-table th, .teachings-table th {
  background: rgba(255, 255, 255, 0.08);
  color: rgba(255, 255, 255, 0.95);
  padding: 12px 15px;
  text-align: left;
  font-weight: 600;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.selections-table td, .teachings-table td {
  padding: 12px 15px;
  color: rgba(255, 255, 255, 0.8);
  border-bottom: 1px solid rgba(255, 255, 255, 0.03);
}

.selections-table tr:last-child td, .teachings-table tr:last-child td {
  border-bottom: none;
}

.selections-table tr:hover, .teachings-table tr:hover {
  background: rgba(255, 255, 255, 0.02);
}

/* 学生信息样式 */
.student-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.student-name {
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
}

.student-details {
  display: flex;
  flex-direction: column;
  gap: 2px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
}

/* 课程信息样式 */
.course-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.course-name {
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
}

.course-type {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
}

/* 成绩显示样式 */
.grade-display {
  padding: 4px 8px;
  border-radius: 12px;
  font-weight: 600;
  font-size: 14px;
}

.grade-display.excellent {
  background: rgba(76, 175, 80, 0.2);
  color: #4CAF50;
  border: 1px solid rgba(76, 175, 80, 0.4);
}

.grade-display.good {
  background: rgba(33, 150, 243, 0.2);
  color: #2196F3;
  border: 1px solid rgba(33, 150, 243, 0.4);
}

.grade-display.average {
  background: rgba(255, 193, 7, 0.2);
  color: #FFC107;
  border: 1px solid rgba(255, 193, 7, 0.4);
}

.grade-display.pass {
  background: rgba(255, 152, 0, 0.2);
  color: #FF9800;
  border: 1px solid rgba(255, 152, 0, 0.4);
}

.grade-display.fail {
  background: rgba(244, 67, 54, 0.2);
  color: #F44336;
  border: 1px solid rgba(244, 67, 54, 0.4);
}

.grade-display.no-grade {
  background: rgba(158, 158, 158, 0.2);
  color: #9E9E9E;
  border: 1px solid rgba(158, 158, 158, 0.4);
}

/* 操作按钮样式 */
.action-buttons {
  display: flex;
  gap: 5px;
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

.selection-form-dialog, .teaching-form-dialog {
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
.selection-form, .teaching-form {
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

/* 预览信息样式 */
.preview-info {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
  padding: 15px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.preview-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.preview-item:last-child {
  border-bottom: none;
}

.preview-item label {
  color: rgba(255, 255, 255, 0.7);
  font-weight: 500;
}

.preview-item span {
  color: rgba(255, 255, 255, 0.9);
  font-weight: 600;
}

/* 详情样式 */
.selection-detail {
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

/* 成绩详情样式 */
.grade-detail {
  padding: 6px 12px;
  border-radius: 12px;
  font-weight: 600;
  font-size: 16px;
}

.grade-detail.excellent {
  background: rgba(76, 175, 80, 0.2);
  color: #4CAF50;
  border: 1px solid rgba(76, 175, 80, 0.4);
}

.grade-detail.good {
  background: rgba(33, 150, 243, 0.2);
  color: #2196F3;
  border: 1px solid rgba(33, 150, 243, 0.4);
}

.grade-detail.average {
  background: rgba(255, 193, 7, 0.2);
  color: #FFC107;
  border: 1px solid rgba(255, 193, 7, 0.4);
}

.grade-detail.pass {
  background: rgba(255, 152, 0, 0.2);
  color: #FF9800;
  border: 1px solid rgba(255, 152, 0, 0.4);
}

.grade-detail.fail {
  background: rgba(244, 67, 54, 0.2);
  color: #F44336;
  border: 1px solid rgba(244, 67, 54, 0.4);
}

.grade-detail.no-grade {
  background: rgba(158, 158, 158, 0.2);
  color: #9E9E9E;
  border: 1px solid rgba(158, 158, 158, 0.4);
}

/* 输入提示 */
.input-hint {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
  margin-top: 4px;
}

/* 危险按钮样式 */
.danger-btn {
  background: rgba(244, 67, 54, 0.8);
  color: white;
}

.danger-btn:hover {
  background: rgba(244, 67, 54, 1);
}

/* 选项卡样式 */
.tab-container {
  margin-bottom: 25px;
}

.tab-buttons {
  display: flex;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.tab-button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  background: transparent;
  border: none;
  color: rgba(255, 255, 255, 0.7);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 16px;
  font-weight: 500;
  flex: 1;
  justify-content: center;
}

.tab-button.active {
  background: rgba(102, 126, 234, 0.3);
  color: white;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.tab-button:hover:not(.active) {
  background: rgba(255, 255, 255, 0.05);
  color: rgba(255, 255, 255, 0.9);
}

.tab-icon {
  font-size: 20px;
}

.tab-content {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* 复选框样式 */
.selection-checkbox {
  width: 16px;
  height: 16px;
  cursor: pointer;
}

/* 选中行样式 */
tr.selected {
  background: rgba(102, 126, 234, 0.1) !important;
}

/* 批量控制样式 */
.batch-controls {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-left: auto;
}

.batch-count {
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
}

.batch-clear-btn {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: rgba(255, 255, 255, 0.8);
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.batch-clear-btn:hover {
  background: rgba(255, 255, 255, 0.15);
}

/* 编辑成绩容器 */
.edit-grade-container {
  display: flex;
  align-items: center;
  gap: 8px;
}

.grade-input {
  width: 80px;
  text-align: center;
}

.grade-hint {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
}

/* 下拉菜单样式 */
.dropdown {
  position: relative;
  display: inline-block;
}

.dropdown-toggle {
  display: flex;
  align-items: center;
  gap: 8px;
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  background: rgba(30, 30, 46, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  padding: 8px;
  min-width: 160px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
  z-index: 100;
  display: none;
}

.dropdown:hover .dropdown-menu {
  display: block;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  padding: 10px 12px;
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.9);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
}

.dropdown-item:hover {
  background: rgba(255, 255, 255, 0.1);
}

.dropdown-icon {
  font-size: 16px;
}

/* 批量导入样式 */
.bulk-import-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.import-instructions {
  padding: 15px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.import-instructions h4 {
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 10px;
}

.import-instructions p {
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 10px;
}

.import-instructions ul {
  color: rgba(255, 255, 255, 0.8);
  margin-left: 20px;
  margin-bottom: 15px;
}

.import-template {
  margin-top: 15px;
}

.import-template h5 {
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 8px;
}

.import-template pre {
  background: rgba(0, 0, 0, 0.3);
  padding: 10px;
  border-radius: 6px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 10px;
  overflow-x: auto;
}

.import-data {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.import-textarea {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  color: white;
  padding: 12px;
  font-family: 'Courier New', monospace;
  font-size: 14px;
  resize: vertical;
  min-height: 200px;
}

.import-textarea:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.3);
}

.import-results {
  padding: 15px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.import-results h4 {
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 10px;
}

.result-stats {
  display: flex;
  gap: 15px;
  margin-bottom: 10px;
}

.result-success {
  color: #4caf50;
  font-weight: 600;
}

.result-failed {
  color: #f44336;
  font-weight: 600;
}

.result-total {
  color: rgba(255, 255, 255, 0.8);
  font-weight: 600;
}

.result-errors {
  margin-top: 10px;
}

.result-errors h5 {
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 8px;
}

.error-item {
  color: #f44336;
  font-size: 14px;
  padding: 4px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.error-item:last-child {
  border-bottom: none;
}

/* 老师授课管理样式 */
.teacher-group {
  margin-bottom: 15px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  overflow: hidden;
}

.teacher-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  background: rgba(255, 255, 255, 0.08);
  cursor: pointer;
  transition: all 0.3s ease;
}

.teacher-header:hover {
  background: rgba(255, 255, 255, 0.12);
}

.teacher-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.toggle-icon {
  font-size: 18px;
  width: 24px;
  text-align: center;
}

.teacher-name {
  font-weight: 600;
  color: rgba(255, 255, 255, 0.95);
  font-size: 18px;
}

.teacher-title {
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
}

.teaching-count {
  color: rgba(255, 255, 255, 0.6);
  font-size: 14px;
}

.teacher-actions {
  display: flex;
  gap: 8px;
}

.teaching-list {
  background: rgba(255, 255, 255, 0.05);
}

.student-count {
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
}

/* 编辑输入框样式 */
.edit-input {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  color: white;
  padding: 5px 8px;
  width: 100%;
  font-size: 14px;
}

.edit-input:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.3);
}

/* 错误信息、成功信息、加载状态样式 */
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

.loading-container {
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

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(255, 255, 255, 0.1);
  border-left: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

.loading-spinner-small {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-left: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-right: 8px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

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
  
  .add-selection-btn, .add-teaching-btn {
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
  
  .tab-buttons {
    flex-direction: column;
  }
  
  .batch-controls {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .edit-grade-container {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }
  
  .grade-input {
    width: 100%;
  }
  
  .teacher-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .teacher-info {
    flex-wrap: wrap;
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
  
  .selections-table, .teachings-table {
    font-size: 12px;
  }
  
  .selections-table th, .selections-table td,
  .teachings-table th, .teachings-table td {
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
  
  .edit-input {
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
  
  .tab-button {
    padding: 10px 15px;
    font-size: 14px;
  }
  
  .tab-icon {
    font-size: 16px;
  }
  
  .teacher-name {
    font-size: 16px;
  }
}
</style>