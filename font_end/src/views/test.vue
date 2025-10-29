<template>
    <div>

    </div>
</template>

<script setup>


// import axios from 'axios';
// async function student_info() {
//   const token = localStorage.getItem('jwt_token') 
//   const res = await axios.get('http://127.0.0.1:5000/student_info',
//      {
//         headers: { 'Authorization': `Bearer ${token}` }}
//   );
// console.log(res);

// }
// student_info()


// import axios from 'axios';
// async function check_deadline() {
//   const token = localStorage.getItem('jwt_token')
//   const res = await axios.get('http://127.0.0.1:5000/check_deadline',
//      {
//         headers: { 'Authorization': `Bearer ${token}` }}
//   );
//   console.log(res);
  
// }
// check_deadline()

// import {ref} from "vue"
// const data_time=ref("2028-12-31")
// async function set_deadline() {
//   const token = localStorage.getItem('jwt_token')
//   const res = await axios.post('http://127.0.0.1:5000/set_deadline',
//   {"deadline": data_time.value},
//      {
//         headers: { 'Authorization': `Bearer ${token}` }}
//   );
//   console.log(res);
  
// }
// set_deadline()



// import { VueElement } from 'vue';
// import axios from 'axios';
// async function teacher_check(){

// const token = localStorage.getItem('jwt_token')


//   const res = await axios.post('http://127.0.0.1:5000/teacher_check',
//  {


//     "message_check": "class",
//     "semester_id": 2


// },
//      {
//         headers: { 'Authorization': `Bearer ${token}` }}
//   );


// console.log(res);


// }


// teacher_check()




// import axios from 'axios';
// async function bulk_import() {
//   const token = localStorage.getItem('jwt_token')


//   const res = await axios.post('http://127.0.0.1:5000/bulkimport',
//  [
//     {
//         "student_id": "1001",
//         "student_name": "lry",
//         "course_id": "3",
//         "course_name": "概率论与数理统计",
//         "score": "91",
//         "semester_name": "2025-2026学年第二学期"
//     }
    
//     ],
//      {
//         headers: { 'Authorization': `Bearer ${token}` }}
//   );


// console.log(res);


  
// }






// bulk_import()

import axios from 'axios';
async function admin_student_info() {
  const token = localStorage.getItem('jwt_token')


  const res = await axios.get('http://127.0.0.1:5000/admin/student_info',

     {
        headers: { 'Authorization': `Bearer ${token}` }}
  );


console.log(res);


  
}
admin_student_info()

</script>





<style scoped>

</style>