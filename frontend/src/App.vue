<script setup>
import { useAuthStore } from './stores/auth'
import { useRouter } from 'vue-router'
import ThemeToggle from './components/ThemeToggle.vue'
import { useTheme } from './composables/useTheme'

const auth = useAuthStore()
const router = useRouter()

// 初始化主题
useTheme()

function logout() {
  auth.logout()
  router.push('/login')
}
</script>

<template>
  <div id="app-container">
    <nav v-if="auth.isLoggedIn" class="navbar">
      <div class="nav-left">
        <router-link to="/" class="logo">🎓 AI 智能助手</router-link>
      </div>
      <div class="nav-right">
        <router-link to="/" class="nav-link">工作台</router-link>
        <router-link to="/profile" class="nav-link">
          👤 {{ auth.user?.username }}
        </router-link>
        <ThemeToggle />
        <button @click="logout" class="btn-logout">退出</button>
      </div>
    </nav>
    <main class="card-enter-stage">
      <router-view />
    </main>
  </div>
</template>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 32px;
  height: 56px;
  background: linear-gradient(135deg, #1a1a2e, #16213e);
  color: white;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}

.nav-left .logo {
  color: white;
  text-decoration: none;
  font-size: 18px;
  font-weight: 600;
}

.nav-right {
  display: flex;
  align-items: center;
  gap: 14px;
}

.nav-link {
  color: #c0c0d0;
  text-decoration: none;
  font-size: 14px;
  transition: color 0.2s;
}

.nav-link:hover, .nav-link.router-link-exact-active {
  color: white;
}

.btn-logout {
  background: rgba(255,255,255,0.1);
  color: #c0c0d0;
  border: 1px solid rgba(255,255,255,0.2);
  padding: 6px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s;
}

.btn-logout:hover {
  background: rgba(255,255,255,0.2);
  color: white;
}

main {
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px;
}
</style>
