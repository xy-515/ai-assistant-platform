import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import App from './App.vue'
import router from './router'

// Global styles
import 'element-plus/dist/index.css'
import './styles/global.scss'
import './styles/auth.scss'
import './styles/micro-interactions.css'
import './styles/theme.css'

const app = createApp(App)
app.use(ElementPlus)
app.use(createPinia())
app.use(router)
app.mount('#app')
