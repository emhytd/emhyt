<template>



<DeadlineManager  @semester-change="handleSemesterChange"/>


</template>

<script setup >

import DeadlineManager from "@/components/DeadlineManager.vue"

const handleSemesterChange = (semesterId) => {
  console.log('父组件接收到学期ID:', semesterId)
  // 在这里可以根据学期ID获取对应的成绩数据
  // 例如：fetchScoresBySemester(semesterId)

}


</script>

<style scoped>



</style>