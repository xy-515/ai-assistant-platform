<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()
const username = ref('')
const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function handleRegister() {
  error.value = ''
  loading.value = true
  try {
    await auth.register(username.value, email.value, password.value)
    router.push('/')
  } catch (e) {
    error.value = e.response?.data?.detail || '注册失败，请重试'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="auth-bg">
    <div class="shape shape-1"></div>
    <div class="shape shape-2"></div>
    <div class="shape shape-3"></div>
    <div class="shape shape-4"></div>

    <div class="auth-card page-card-enter">
      <!-- Robot Icon -->
      <div class="robot-icon">
        <svg viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg">
          <rect x="10" y="25" width="60" height="40" rx="16" fill="white" stroke="url(#grad)" stroke-width="3"/>
          <circle cx="30" cy="40" r="6" fill="url(#grad)"/>
          <circle cx="50" cy="40" r="6" fill="url(#grad)"/>
          <circle cx="30" cy="40" r="2.5" fill="white"/>
          <circle cx="50" cy="40" r="2.5" fill="white"/>
          <rect x="24" y="50" width="32" height="4" rx="2" fill="url(#grad)"/>
          <circle cx="22" cy="32" r="3" fill="#F56C6C"/>
          <circle cx="58" cy="32" r="3" fill="#67C23A"/>
          <rect x="18" y="18" width="10" height="10" rx="4" fill="white" stroke="url(#grad)" stroke-width="2"/>
          <rect x="52" y="18" width="10" height="10" rx="4" fill="white" stroke="url(#grad)" stroke-width="2"/>
          <circle cx="40" cy="15" r="6" fill="url(#grad)"/>
          <defs>
            <linearGradient id="grad" x1="0" y1="0" x2="1" y2="1">
              <stop offset="0%" stop-color="#667eea"/>
              <stop offset="100%" stop-color="#764ba2"/>
            </linearGradient>
          </defs>
        </svg>
      </div>

      <h1>创建账号</h1>
      <p class="subtitle">加入毕业设计智能辅助平台</p>

      <form @submit.prevent="handleRegister">
        <div class="input-wrap">
          <span class="input-icon">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#909399" stroke-width="2" stroke-linecap="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
          </span>
          <input v-model="username" type="text" placeholder="用户名" required />
        </div>

        <div class="input-wrap">
          <span class="input-icon">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#909399" stroke-width="2" stroke-linecap="round"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="M2 6l10 7 10-7"/></svg>
          </span>
          <input v-model="email" type="email" placeholder="邮箱" required />
        </div>

        <div class="input-wrap">
          <span class="input-icon">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#909399" stroke-width="2" stroke-linecap="round"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
          </span>
          <input v-model="password" type="password" placeholder="密码（至少6位）" required minlength="6" />
        </div>

        <p v-if="error" class="error">{{ error }}</p>

        <button type="submit" :disabled="loading" class="btn-login">
          <span v-if="loading" class="spinner"></span>
          <span v-else>注 册</span>
        </button>
      </form>

      <p class="switch">
        已有账号？<router-link to="/login">立即登录</router-link>
      </p>
    </div>
  </div>
</template>

<style scoped>
.auth-card {
  position: relative;
  z-index: 1;
  width: 450px;
  max-width: 90vw;
  padding: 48px 40px 36px;
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border-radius: 24px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12), 0 2px 8px rgba(0, 0, 0, 0.06);
  animation: card-in 0.5s ease;
}

@keyframes card-in {
  from { opacity: 0; transform: translateY(20px) scale(0.97); }
  to   { opacity: 1; transform: translateY(0) scale(1); }
}

.robot-icon {
  display: flex;
  justify-content: center;
  margin-bottom: 8px;
}
.robot-icon svg {
  width: 72px;
  height: 72px;
  filter: drop-shadow(0 4px 8px rgba(102, 126, 234, 0.25));
  animation: robot-bounce 3s ease-in-out infinite;
}

@keyframes robot-bounce {
  0%, 100% { transform: translateY(0); }
  50%      { transform: translateY(-6px); }
}

h1 {
  text-align: center;
  font-size: 24px;
  font-weight: 700;
  color: #1A1A2E;
  margin-bottom: 4px;
}

.subtitle {
  text-align: center;
  font-size: 14px;
  color: #909399;
  margin-bottom: 32px;
}

.input-wrap {
  position: relative;
  margin-bottom: 18px;
}

.input-icon {
  position: absolute;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  align-items: center;
  z-index: 1;
}

input {
  width: 100%;
  padding: 14px 16px 14px 46px;
  font-size: 15px;
  color: #1A1A2E;
  background: #F5F7FA;
  border: 2px solid transparent;
  border-radius: 20px;
  outline: none;
  transition: all 0.25s ease;
}

input::placeholder { color: #BBB; }

input:focus {
  background: #FFF;
  border-color: #667eea;
  box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.12);
}

.error {
  color: #F56C6C;
  font-size: 13px;
  margin: -8px 0 12px;
  padding-left: 6px;
}

.btn-login {
  width: 100%;
  padding: 14px;
  font-size: 16px;
  font-weight: 600;
  color: #FFF;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border: none;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  letter-spacing: 4px;
}

.btn-login:hover:not(:disabled) {
  transform: scale(1.03);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.btn-login:active:not(:disabled) { transform: scale(0.98); }
.btn-login:disabled { opacity: 0.7; cursor: not-allowed; }

.spinner {
  display: inline-block;
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: #FFF;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

.switch {
  text-align: center;
  margin-top: 24px;
  font-size: 14px;
  color: #909399;
}

.switch a {
  color: #667eea;
  font-weight: 500;
  text-decoration: none;
  transition: color 0.2s;
}

.switch a:hover { color: #764ba2; }
</style>
