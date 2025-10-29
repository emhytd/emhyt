// API基础URL
const BASE_URL = 'https://api.emhyt.top';

// 认证相关API
export const AUTH_API = {
  LOGIN: `${BASE_URL}/login`,
  LOGOUT: `${BASE_URL}/logout`,
  CHECK_LOGIN: `${BASE_URL}/check_login/`,
  GET_USER_NAME: `${BASE_URL}/get_user_name`,
};

// 学生相关API
export const STUDENT_API = {
  CHECK: `${BASE_URL}/student_check`,
  GET_SEMESTERS: `${BASE_URL}/semesters`,
  GET_INFO: `${BASE_URL}/student_info`,
};

// 教师相关API
export const TEACHER_API = {
  CHECK_DEADLINE: `${BASE_URL}/check_deadline`,
  SET_DEADLINE: `${BASE_URL}/set_deadline`,
  CHECK: `${BASE_URL}/teacher_check`,
  UPDATE_GRADES: `${BASE_URL}/update_grades`,
  BULK_IMPORT: `${BASE_URL}/bulkimport`,
};

// 管理员相关API
// apiConfig.js - 修正后的版本
export const ADMIN_API = {
  CHECK: `${BASE_URL}/admin_check`,
  STUDENT_INFO: `${BASE_URL}/admin/student_info`,
  TEACHER_INFO: `${BASE_URL}/admin/teacher_info`,
  CLASS_TEACHER_INFO: `${BASE_URL}/admin/class_teacher_info`,
  CLASS_INFO: `${BASE_URL}/admin/class_info`,
  SEMESTER_INFO: `${BASE_URL}/admin/semester_info`,
  COURSE_SELECTION_INFO: `${BASE_URL}/admin/course_selection_info`,
  COURSE_SELECTION_MANAGEMENT: `${BASE_URL}/admin/course_selection_management`,
  COURSE_SELECTION_BASE_DATA: `${BASE_URL}/admin/course_selection_base_data`,
  COURSE_SELECTION_BULK_IMPORT: `${BASE_URL}/admin/course_selection_bulk_import`,
  TEACHING_MANAGEMENT: `${BASE_URL}/admin/teaching_management`
};
// 通用API
export const COMMON_API = {
  CHECK_DEADLINE: `${BASE_URL}/check_deadline`,
};

export default {
  BASE_URL,
  AUTH_API,
  STUDENT_API,
  TEACHER_API,
  ADMIN_API,
  COMMON_API,
};