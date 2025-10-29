import apiConfig from '@/config/apiConfig';

export default {
  install: (app) => {
    // 将API配置添加到全局属性
    app.config.globalProperties.$api = apiConfig;
    
    // 提供API配置给所有组件
    app.provide('apiConfig', apiConfig);
  }
};