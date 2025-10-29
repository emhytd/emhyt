import {createRouter, createWebHistory} from 'vue-router'
import useAuth from '@/composables/useAuth' 

const routes = [
  {
    path: '/',
    component: () => import('@/views/index.vue'),
    meta: { requiresAuth: false } // 首页不需要认证
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/login.vue'),
    meta: { requiresAuth: false } // 登录页不需要认证
  },
  {
    path: '/teacher',
    component: () => import('@/views/teacher.vue'),
    meta: { requiresAuth: true }, // 教师路由需要认证
    children: [
      {
        path: 'deadline',
        component: () => import('@/views/teacher/deadline.vue'),
        meta: { requiresAuth: true } // 子路由也需要认证
      },
      {
        path: '',
        component: () => import('@/views/teacher/grade_input.vue'),
        meta: { requiresAuth: true } // 默认子路由也需要认证
      },
      {
        path: 'bulk_import',
        component: () => import('@/views/teacher/bulk_import.vue'),
        meta: { requiresAuth: true } // 子路由也需要认证
      },
       {
        path: 'classquery_teacher',

        component: () => import('@/views/teacher/classquery_teacher.vue'),

        meta: { requiresAuth: true } // 子路由也需要认证
      },
      
    ]  
  },
  {
    path: '/student',
    component: () => import('@/views/student.vue'),
    meta: { requiresAuth: true } // 学生路由需要认证
  },
  {
    path: '/info_student',
    component: () => import('@/views/info_student.vue'),
    meta: { requiresAuth: true } // 学生信息路由需要认证
  },
  {
    path: '/test',
    component: () => import('@/views/test.vue'),
    meta: { requiresAuth: true } // 测试路由需要认证
  },
  {
    path: '/',
    redirect: '/login',
    meta: { requiresAuth: false } // 重定向不需要认证
  },
     { path: '/admin',
    component: () => import('@/views/admin/admin.vue'),
    meta: { requiresAuth: true }, // admin
   children:[
    {path: 'bulk_import',
        component: () => import('@/views/admin/bulk_import.vue'),
        meta: { requiresAuth: true }
      },
       {path: '',
        component: () => import('@/views/admin/default.vue'),
        meta: { requiresAuth: true }
      },
        {path: 'deadline',
        component: () => import('@/views/teacher/deadline.vue'),
        meta: { requiresAuth: true }
      },
      {path: 'grade_input_admin',
        component: () => import('@/views/admin/grade_input_admin.vue'),
        meta: { requiresAuth: true }
      },
        {path: 'student_edit',
        component: () => import('@/views/admin/student_edit.vue'),
        meta: { requiresAuth: true }
      },
      {path: 'teacher_edit',
        component: () => import('@/views/admin/teacher_edit.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: 'class_query',

        component: () => import('@/views/admin/classquery.vue'),

        meta: { requiresAuth: true } // 子路由也需要认证
      },
       {
        path: 'teacher_query',

        component: () => import('@/views/admin/teacherquery.vue'),
        meta: { requiresAuth: true } // 子路由也需要认证
      },

      {
        path: 'class_edit',

        component: () => import('@/views/admin/class_edit.vue'),
        meta: { requiresAuth: true } // 子路由也需要认证
      },
      
      {
        path: 'course_edit',

        component: () => import('@/views/admin/Course_edit.vue'),
        meta: { requiresAuth: true } // 子路由也需要认证
      },

   ]  
  
  
  
   }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const { user, checkLoginStatus } = useAuth()
  
  // 检查目标路由是否需要认证
  if (to.matched.some(record => record.meta.requiresAuth)) {
    // 如果需要认证，检查登录状态
    if (!user.value) {
      await checkLoginStatus()
    }

    // 如果没有登录，则跳转到登录页
    if (!user.value) {
      next({ path: '/login' })
    } else {
      next() // 已登录，允许访问
    }
  } else {
    next() // 不需要认证的页面直接通过
  }
})

export default router