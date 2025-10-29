<template>
  <div class="bulk-import-container">
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
      <p>{{ loadingText }}</p>
    </div>

    <!-- 操作区域 -->
    <div class="operation-section">
      <div class="operation-card">
        <h2 class="section-title">批量导入成绩</h2>
        
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
            :disabled="!selectedFile || parsing"
            class="parse-btn"
            :class="{ 'disabled': !selectedFile || parsing }"
          >
            {{ parsing ? '解析中...' : '解析文件' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 数据预览 -->
    <div v-if="parsedData.length > 0" class="preview-section">
      <div class="preview-card">
        <h3 class="card-title">数据预览</h3>
        <p class="preview-desc">共 {{ parsedData.length }} 条记录，请确认数据无误后提交</p>
        
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
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, index) in parsedData" :key="index">
                <td>{{ index + 1 }}</td>
                <td>{{ item.student_id }}</td>
                <td>{{ item.student_name }}</td>
                <td>{{ item.course_id }}</td>
                <td>{{ item.course_name }}</td>
                <td>{{ item.score }}</td>
                <td>{{ item.semester_name }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- 提交按钮 -->
        <div class="action-buttons">
          <button 
            @click="submitData" 
            :disabled="submitting"
            class="submit-btn"
            :class="{ 'disabled': submitting }"
          >
            {{ submitting ? '提交中...' : '提交数据' }}
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
            <span class="summary-label">成功</span>
            <span class="summary-value">{{ importResult.details.success }}/{{ importResult.details.total }}</span>
          </div>
          <div class="summary-item error">
            <span class="summary-label">失败</span>
            <span class="summary-value">{{ importResult.details.errors.length }}/{{ importResult.details.total }}</span>
          </div>
        </div>

        <!-- 错误详情 -->
        <div v-if="importResult.details.errors.length > 0" class="error-details">
          <h4 class="error-title">错误详情</h4>
          <div class="error-table-container">
            <table class="error-table">
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
                <tr v-for="(error, index) in importResult.details.errors" :key="index">
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
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import * as XLSX from 'xlsx'

// 配置后端基础URL

import apiConfig from '@/config/apiConfig';
// 响应式数据
const selectedFile = ref(null)
const parsedData = ref([])
const importResult = ref(null)
const loading = ref(false)
const parsing = ref(false)
const submitting = ref(false)
const isDragOver = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const loadingText = ref('正在加载...')

const fileInput = ref(null)

// 确保组件挂载后能正确引用fileInput
onMounted(() => {
  console.log('组件已挂载，fileInput:', fileInput.value)
})

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

// 触发文件选择 - 修复重复触发问题
const triggerFileInput = () => {
  console.log('触发文件选择')
  
  // 确保fileInput存在再调用
  if (fileInput.value) {
    fileInput.value.click()
  } else {
    console.error('fileInput 引用为空')
  }
}

// 处理文件选择
const handleFileSelect = (event) => {
  console.log('文件选择事件触发', event.target.files)
  
  const file = event.target.files[0]
  if (file) {
    const fileExtension = file.name.split('.').pop().toLowerCase()
    if (['xlsx', 'xls', 'csv'].includes(fileExtension)) {
      selectedFile.value = file
      console.log('已选择文件:', file.name)
    } else {
      showError('请上传Excel或CSV文件（.xlsx, .xls, .csv 格式）')
    }
  } else {
    console.log('未选择文件')
  }
  
  // 重置input值，允许重复选择同一文件
  event.target.value = ''
}

// 移除文件
const removeFile = () => {
  console.log('移除文件')
  selectedFile.value = null
  parsedData.value = []
  importResult.value = null
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
  console.log('拖拽文件:', files)
  
  if (files.length > 0) {
    const file = files[0]
    const fileExtension = file.name.split('.').pop().toLowerCase()
    if (['xlsx', 'xls', 'csv'].includes(fileExtension)) {
      selectedFile.value = file
      console.log('通过拖拽选择文件:', file.name)
    } else {
      showError('请上传Excel或CSV文件（.xlsx, .xls, .csv 格式）')
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

// 下载模板
const downloadTemplate = (type) => {
  const templateData = [
    {
      student_id: '1001',
      student_name: '张三',
      course_id: '3',
      course_name: '概率论与数理统计',
      score: '91',
      semester_name: '2025-2026学年第二学期'
    },
    {
      student_id: '1002',
      student_name: '李四',
      course_id: '5',
      course_name: '高等数学',
      score: '85',
      semester_name: '2025-2026学年第二学期'
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

// 解析文件
const parseFile = async () => {
  if (!selectedFile.value) {
    showError('请先选择文件')
    return
  }

  parsing.value = true
  errorMessage.value = ''
  
  try {
    const fileExtension = selectedFile.value.name.split('.').pop().toLowerCase()
    let data
    
    if (fileExtension === 'csv') {
      data = await readCSVFile(selectedFile.value)
    } else {
      data = await readExcelFile(selectedFile.value)
    }
    
    parsedData.value = data
    successMessage.value = `成功解析 ${data.length} 条记录`
  } catch (error) {
    console.error('解析文件失败:', error)
    showError(`解析文件失败: ${error.message}`)
  } finally {
    parsing.value = false
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
      throw new Error(`第${index + 2}行缺少必要字段: ${missingFields.join(', ')}`)
    }
    
    return {
      student_id: String(item.student_id),
      student_name: String(item.student_name),
      course_id: String(item.course_id),
      course_name: String(item.course_name),
      score: String(item.score),
      semester_name: String(item.semester_name)
    }
  })
}

// 提交数据
const submitData = async () => {
  if (parsedData.value.length === 0) return

  submitting.value = true
  loading.value = true
  loadingText.value = '正在提交数据...'
  errorMessage.value = ''
  successMessage.value = ''

  try {
    const token = localStorage.getItem('jwt_token')
    if (!token) {
      throw new Error('未找到认证令牌，请重新登录')
    }

    // 使用正确的后端URL
    const res = await axios.post(apiConfig.TEACHER_API.BULK_IMPORT, parsedData.value, {
      headers: { 
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    })

    console.log('导入结果:', res)

    if (res.status === 200) {
      importResult.value = res.data
      
      if (res.data.details.success === res.data.details.total) {
        successMessage.value = `全部导入成功！成功导入 ${res.data.details.success} 条记录`
      } else if (res.data.details.success > 0) {
        successMessage.value = `部分导入成功！成功导入 ${res.data.details.success}/${res.data.details.total} 条记录`
      } else {
        errorMessage.value = `导入失败！所有 ${res.data.details.total} 条记录均未成功导入`
      }
    } else {
      throw new Error(`导入失败: ${res.status} ${res.statusText}`)
    }
  } catch (error) {
    console.error('提交数据失败:', error)
    handleApiError(error)
  } finally {
    submitting.value = false
    loading.value = false
  }
}

// 统一的API错误处理
const handleApiError = (error) => {
  if (error.response) {
    const status = error.response.status
    const data = error.response.data
    
    switch (status) {
      case 401:
        if (data.error === '未提供token') {
          showError('认证失败：未提供访问令牌')
        } else if (data.error === 'Token已过期') {
          showError('认证失败：令牌已过期，请重新登录')
        } else if (data.error === '无效的Token') {
          showError('认证失败：无效的令牌')
        } else if (data.error === 'Token解析错误') {
          showError('认证失败：令牌解析错误')
        } else {
          showError('认证失败：请重新登录')
        }
        break
      case 403:
        showError('权限不足：仅限教师用户进行批量导入')
        break
      case 400:
        showError(`请求错误：${data.error || '数据格式不正确'}`)
        break
      case 404:
        showError('接口不存在：请检查后端服务是否正常运行')
        break
      case 500:
        showError('服务器错误：批量导入失败，请稍后重试')
        break
      default:
        showError(`导入失败: ${status} ${data?.error || error.message}`)
    }
  } else if (error.code === 'NETWORK_ERROR' || error.message.includes('Network Error')) {
    showError('网络错误：无法连接到后端服务，请检查：\n1. 后端服务是否启动\n2. 端口号是否正确\n3. 网络连接是否正常')
  } else if (error.request) {
    showError('网络错误：无法连接到服务器，请检查后端服务是否运行')
  } else {
    showError(`导入失败: ${error.message}`)
  }
}

// 显示错误信息
const showError = (message) => {
  errorMessage.value = message
  // 5秒后自动清除错误信息
  setTimeout(() => {
    if (errorMessage.value === message) {
      errorMessage.value = ''
    }
  }, 5000)
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
.bulk-import-container {
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

/* 修复文件输入框样式 */
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
.table-container,
.error-table-container {
  overflow-x: auto;
  margin-bottom: 20px;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.data-table,
.error-table {
  width: 100%;
  border-collapse: collapse;
  background: rgba(255, 255, 255, 0.05);
}

.data-table th,
.error-table th {
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.9);
  padding: 12px 15px;
  text-align: left;
  font-weight: 600;
  font-size: 14px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.data-table td,
.error-table td {
  padding: 12px 15px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
}

.data-table tr:hover,
.error-table tr:hover {
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

/* 响应式设计 */
@media (max-width: 768px) {
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
  .data-table td,
  .error-table th,
  .error-table td {
    padding: 8px 10px;
    font-size: 12px;
  }
  
  .operation-card,
  .preview-card,
  .result-card {
    padding: 15px;
  }
}

@media (max-width: 480px) {
  .section-title {
    font-size: 20px;
  }
  
  .card-title {
    font-size: 16px;
  }
  
  .upload-area {
    padding: 30px 15px;
  }
  
  .upload-icon {
    font-size: 36px;
  }
  
  .upload-text {
    font-size: 14px;
  }
  
  .parse-btn,
  .submit-btn {
    padding: 10px 20px;
    font-size: 14px;
    min-width: 120px;
  }
  
  .file-info {
    flex-direction: column;
    gap: 5px;
  }
}
</style>