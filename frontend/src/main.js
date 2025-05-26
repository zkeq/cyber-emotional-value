import { createApp } from 'vue'
import { inject } from '@vercel/analytics'
import App from './App.vue'
import router from './router'
import './assets/tailwind.css'
import './assets/main.css'

// 注入 Vercel Analytics
inject()

createApp(App).use(router).mount('#app')
