import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'
import ElementPlus from 'element-plus'
import apiPlugin from './plugins/apiPlugin';
import VueParticles from 'vue3-particles'
import useAuth from './composables/useAuth'
const app=createApp(App)
app.use(router)
app.use(ElementPlus)
app.use(VueParticles)
app.use(apiPlugin);
app.mount('#app')
import '@fortawesome/fontawesome-free/css/all.css'