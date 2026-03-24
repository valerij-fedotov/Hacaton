import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { loadAllData } from './stores/appData'   

const app = createApp(App)

app.use(router)

// Загружаем данные перед монтированием
loadAllData()
  .then(() => {
    app.mount('#app')
  })
  .catch((err: any) => {
    console.error('Failed to load initial data:', err)
    app.mount('#app')
  })