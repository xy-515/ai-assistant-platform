<script setup>
import { ref } from 'vue'
import { useAuthStore } from '../stores/auth'
import HistoryList from '../components/HistoryList.vue'

const auth = useAuthStore()
const historyTab = ref('paper')
</script>

<template>
  <div class="profile">
    <div class="user-card">
      <div class="avatar">👤</div>
      <div class="user-info">
        <h2>{{ auth.user?.username }}</h2>
        <p>{{ auth.user?.email }}</p>
      </div>
    </div>

    <div class="history-section">
      <h3>历史记录</h3>
      <div class="tabs">
        <button
          :class="['tab', { active: historyTab === 'paper' }]"
          @click="historyTab = 'paper'"
        >
          📝 论文记录
        </button>
        <button
          :class="['tab', { active: historyTab === 'code' }]"
          @click="historyTab = 'code'"
        >
          💻 代码记录
        </button>
      </div>
      <div class="tab-content">
        <HistoryList :type="historyTab" :key="historyTab" />
      </div>
    </div>
  </div>
</template>

<style scoped>
.profile { max-width: 1000px; margin: 0 auto; }
.user-card {
  display: flex;
  align-items: center;
  gap: 20px;
  background: white;
  padding: 32px;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.06);
  margin-bottom: 24px;
}
.avatar { font-size: 48px; }
.user-info h2 { font-size: 20px; margin-bottom: 4px; }
.user-info p { color: #888; font-size: 14px; }
.history-section { background: white; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); overflow: hidden; }
.history-section h3 { padding: 20px 24px 0; font-size: 18px; }
.tabs { display: flex; border-bottom: 1px solid #e5e7eb; margin-top: 16px; }
.tab {
  flex: 1;
  padding: 14px;
  border: none;
  background: transparent;
  font-size: 15px;
  cursor: pointer;
  color: #666;
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
}
.tab:hover { color: #333; }
.tab.active { color: #2563eb; border-bottom-color: #2563eb; }
.tab-content { padding: 24px; }
</style>
