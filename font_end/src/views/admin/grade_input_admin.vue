<template>
  <div class="parent-container">
    <semester-selector 
      @semester-change="handleSemesterChange"
      :initial-semester-id="defaultSemesterId"
    />
    <AdminQuery :semester-id="selectedSemesterId" />
  </div>
</template>

<script setup>
import SemesterSelector from '@/components/SemesterSelector.vue';
import AdminQuery from '@/components/AdminQuery.vue';
import { ref, onMounted } from 'vue'

// 设置默认学期ID为1
const defaultSemesterId = ref('1')

// 当前选中的学期ID
const selectedSemesterId = ref(defaultSemesterId.value)

// 处理学期变化
const handleSemesterChange = (semesterId) => {
  selectedSemesterId.value = semesterId
  console.log('当前选中的学期ID:', selectedSemesterId.value);
}

// 组件挂载时初始化
onMounted(() => {
  console.log('默认学期ID:', defaultSemesterId.value);
  console.log('初始选中的学期ID:', selectedSemesterId.value);
})
</script>

<style scoped>
.parent-container {
  padding: 20px;
}

.semester-selector {
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.semester-selector label {
  color: rgba(255, 255, 255, 0.9);
  font-weight: 500;
}

.semester-selector select {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 6px;
  padding: 8px 12px;
  color: rgba(255, 255, 255, 0.9);
  min-width: 200px;
}
</style>