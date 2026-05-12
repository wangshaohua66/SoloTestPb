import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import Recognize from './views/Recognize.vue'
import FontLibrary from './views/FontLibrary.vue'
import History from './views/History.vue'
import './assets/style.css'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'Recognize', component: Recognize },
    { path: '/library', name: 'FontLibrary', component: FontLibrary },
    { path: '/history', name: 'History', component: History }
  ]
})

const app = createApp(App)
app.use(router)
app.mount('#app')
