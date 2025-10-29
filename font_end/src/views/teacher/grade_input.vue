<template>
    <div class="parent-container">
<semester-selector @semester-change="handleSemesterChange"/>
 <TeacherQuery :semester-id="selectedSemesterId" />
    </div>
</template>

<script setup>
import SemesterSelector from '@/components/SemesterSelector.vue';
import TeacherQuery from '@/components/TeacherQuery.vue';

const handleSemesterChange = (semesterId) => {
//   console.log('父组件接收到学期ID:', semesterId)
  // 在这里可以根据学期ID获取对应的成绩数据
  // 例如：fetchScoresBySemester(semesterId)
 selectedSemesterId.value = semesterId
 console.log(selectedSemesterId.value);
 
}

import {ref} from 'vue'

const selectedSemesterId = ref('')

// console.log(selectedSemesterId.value);


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