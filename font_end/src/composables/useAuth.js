import { ref } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import apiConfig from '@/config/apiConfig';
const useAuth = () => {
  const router = useRouter()
  const user = ref(null)
  const loading = ref(false)
  const error = ref(null)

  // 检查是否已登录
  
  const checkLoginStatus = async () => {
    const token = localStorage.getItem('jwt_token') 
    // 从 localStorage 获取 JWT token
    console.log('Authorization Header:', `Bearer ${token}`);

    if (!token) {
      console.log('No token found')
      user.value = null
      return
    }

    loading.value = true // 开始加载
    error.value = null  // 清除之前的错误信息

    try {
      console.log('Sending check_login request...')
      const response = await axios.get(apiConfig.AUTH_API.CHECK_LOGIN, {
        headers: { 'Authorization': `Bearer ${token}` }, // 发送 token
      })
      console.log('Response received:', response.data)

      if (response.data.status === 'success') {
        user.value = response.data
        console.log('User is logged in:', user.value)
      }
    } catch (err) {
      console.error('检查登录状态失败:', err)
      console.error('Error response:', err.response?.data)
      error.value = err.response?.data?.error || '登录状态检查失败'
      user.value = null

      // 如果是 Token 无效或过期，跳转到登录页面
      if (err.response?.data?.error === '无效的Token' || err.response?.data?.error === 'Token已过期') {
        router.push('/login')
      }
    } finally {
      loading.value = false // 请求完成，停止加载
    }
  }

  // 注销功能
  const logout = async () => {
    try {
      localStorage.removeItem('jwt_token') // 清除本地存储的 token
      user.value = null
      router.push('/login') // 注销后跳转到登录页面
    } catch (err) {
      console.error('注销失败:', err)
    }
  }

  return { user, loading, error, checkLoginStatus, logout }
}

export default useAuth
