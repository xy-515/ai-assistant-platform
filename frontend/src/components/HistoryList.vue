<script setup>
import { ref, watch, onMounted } from 'vue'
import { marked } from 'marked'
import api from '../api/axios'

const props = defineProps({
  type: { type: String, required: true }, // "paper" or "code"
})

const items = ref([])
const page = ref(1)
const total = ref(0)
const pageSize = 10
const loading = ref(false)
const expandedId = ref(null)       // 当前展开的卡片 ID
const detailLoading = ref(false)   // 详情加载中
const detail = ref(null)           // 详情完整数据

// ── 加载列表 ──────────────────────────────────────────
async function load() {
  loading.value = true
  try {
    const { data } = await api.get(`/history/${props.type}/`, {
      params: { page: page.value, page_size: pageSize },
    })
    items.value = data.results
    total.value = data.count
  } catch (e) {
    console.error('Failed to load history:', e)
  } finally {
    loading.value = false
  }
}

// ── 删除 ──────────────────────────────────────────────
async function remove(id) {
  if (!confirm('确定删除这条记录？')) return
  try {
    await api.delete(`/history/${props.type}/${id}/`)
    if (expandedId.value === id) {
      expandedId.value = null
      detail.value = null
    }
    load()
  } catch (e) {
    console.error('Failed to delete:', e)
  }
}

// ── 展开/折叠详情 ─────────────────────────────────────
async function toggle(id) {
  if (expandedId.value === id) {
    expandedId.value = null
    detail.value = null
  } else {
    expandedId.value = id
    detailLoading.value = true
    detail.value = null
    try {
      const { data } = await api.get(`/history/${props.type}/${id}/`)
      detail.value = data
    } catch (e) {
      console.error('Failed to load detail:', e)
    } finally {
      detailLoading.value = false
    }
  }
}

// ── 分页变化 ──────────────────────────────────────────
function onPageChange(p) {
  page.value = p
  expandedId.value = null
  detail.value = null
  load()
}

// ── 工具函数 ──────────────────────────────────────────
function formatDate(iso) {
  return new Date(iso).toLocaleString('zh-CN', {
    month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit',
  })
}

const funcLabels = {
  polish: '✨ 润色优化',
  outline: '📋 大纲生成',
  review: '🔍 论文点评',
  generate_test: '🧪 生成测试',
  fix: '🔧 修复 Bug',
}

const funcColors = {
  polish: '#8B5CF6', outline: '#3B82F6', review: '#EC4899',
  generate_test: '#10B981', fix: '#F59E0B',
}

// ── 切换类型时重置 ──────────────────────────────────
watch(() => props.type, () => {
  page.value = 1
  expandedId.value = null
  detail.value = null
  load()
})

onMounted(load)
</script>

<template>
  <div class="history-panel">
    <!-- ═══════════ 空状态 ═══════════ -->
    <div v-if="!loading && !items.length" class="empty-state">
      <div class="empty-illustration">
        <svg width="120" height="100" viewBox="0 0 120 100" fill="none" xmlns="http://www.w3.org/2000/svg">
          <rect x="20" y="30" width="80" height="55" rx="8" stroke="#D0D5DD" stroke-width="2.5" stroke-dasharray="5 3" fill="#F9FAFB"/>
          <rect x="34" y="45" width="52" height="4" rx="2" fill="#E5E7EB"/>
          <rect x="34" y="55" width="38" height="4" rx="2" fill="#E5E7EB"/>
          <rect x="34" y="65" width="44" height="4" rx="2" fill="#E5E7EB"/>
          <path d="M47 20 L47 32 M47 20 L55 20 L55 32" stroke="#D0D5DD" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M65 20 L65 32 M65 20 L73 20 L73 32" stroke="#D0D5DD" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
          <circle cx="47" cy="14" r="6" stroke="#D0D5DD" stroke-width="2" fill="#F9FAFB"/>
          <circle cx="73" cy="14" r="6" stroke="#D0D5DD" stroke-width="2" fill="#F9FAFB"/>
        </svg>
      </div>
      <p class="empty-title">暂无{{ props.type === 'paper' ? '论文' : '代码' }}记录</p>
      <p class="empty-hint">开始使用{{ props.type === 'paper' ? '论文' : '代码' }}助手，记录将显示在这里</p>
    </div>

    <!-- ═══════════ 加载中 ═══════════ -->
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>加载中...</p>
    </div>

    <!-- ═══════════ 卡片列表 ═══════════ -->
    <div v-if="!loading && items.length" class="card-list">
      <div
        v-for="item in items"
        :key="item.id"
        class="history-card"
        :class="{ expanded: expandedId === item.id }"
      >
        <!-- ── 卡片主体 ────────────────────────────── -->
        <div class="card-main" @click="toggle(item.id)">
          <!-- 左侧图标 -->
          <div class="card-icon" :style="{ background: (funcColors[item.function_type] || '#6B7280') + '15' }">
            <span class="icon-emoji">{{ props.type === 'paper' ? '📄' : '💻' }}</span>
          </div>

          <!-- 中间内容 -->
          <div class="card-body">
            <div class="card-title">{{ item.title || '未命名记录' }}</div>
            <div class="card-meta">
              <span class="func-tag" :style="{ background: (funcColors[item.function_type] || '#6B7280') + '18', color: funcColors[item.function_type] || '#6B7280' }">
                {{ funcLabels[item.function_type] || item.function_display || item.function_type }}
              </span>
              <span v-if="item.token_used" class="token-info">🪙 {{ item.token_used }} tokens</span>
            </div>
          </div>

          <!-- 右侧时间 + 删除 -->
          <div class="card-right">
            <span class="card-time">{{ formatDate(item.created_at) }}</span>
            <button class="btn-delete" @click.stop="remove(item.id)" title="删除">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/><line x1="10" y1="11" x2="10" y2="17"/><line x1="14" y1="11" x2="14" y2="17"/>
              </svg>
            </button>
            <!-- 展开箭头 -->
            <svg
              class="expand-arrow"
              :class="{ rotated: expandedId === item.id }"
              width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#909399" stroke-width="2.5" stroke-linecap="round"
            >
              <polyline points="6 9 12 15 18 9"/>
            </svg>
          </div>
        </div>

        <!-- ── 折叠详情区 ──────────────────────────── -->
        <div v-if="expandedId === item.id" class="card-detail">
          <div v-if="detailLoading" class="detail-loading">
            <div class="loading-spinner small"></div>
            <span>加载详情...</span>
          </div>
          <template v-else-if="detail">
            <div class="detail-section">
              <h4 class="detail-label">📥 输入内容</h4>
              <pre class="detail-content">{{ detail.input_content || detail.code_content || '（无）' }}</pre>
            </div>
            <div v-if="detail.error_info" class="detail-section">
              <h4 class="detail-label">⚠️ 报错信息</h4>
              <pre class="detail-content error-content">{{ detail.error_info }}</pre>
            </div>
            <div class="detail-section">
              <h4 class="detail-label">📤 AI 输出</h4>
              <div class="detail-content markdown-body" v-html="marked(detail.output_content || '（无）', { breaks: true })"></div>
            </div>
          </template>
        </div>
      </div>
    </div>

    <!-- ═══════════ 分页 ═══════════ -->
    <div v-if="total > pageSize" class="pagination-wrap">
      <el-pagination
        background
        layout="prev, pager, next"
        :total="total"
        :page-size="pageSize"
        :current-page="page"
        @current-change="onPageChange"
      />
    </div>
  </div>
</template>

<style scoped>
/* ── 容器 ──────────────────────────────────────────── */
.history-panel {
  min-height: 280px;
}

/* ── 空状态 ──────────────────────────────────────── */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
}

.empty-illustration {
  margin-bottom: 20px;
  opacity: 0.7;
}

.empty-title {
  font-size: 16px;
  font-weight: 600;
  color: #6B7280;
  margin-bottom: 6px;
}

.empty-hint {
  font-size: 13px;
  color: #9CA3AF;
}

/* ── 加载状态 ────────────────────────────────────── */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #9CA3AF;
  font-size: 14px;
  gap: 12px;
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #E5E7EB;
  border-top-color: #3B82F6;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

.loading-spinner.small {
  width: 20px;
  height: 20px;
  border-width: 2px;
}

@keyframes spin { to { transform: rotate(360deg); } }

/* ── 卡片列表 ────────────────────────────────────── */
.card-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

/* ── 单个卡片 ────────────────────────────────────── */
.history-card {
  border: 1px solid #EBEEF5;
  border-radius: 10px;
  background: #FFF;
  transition: all 0.2s ease;
  overflow: hidden;
}

.history-card:hover {
  border-color: #D0D5DD;
}

.history-card.expanded {
  border-color: #3B82F6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.08);
}

/* ── 卡片主体行 ──────────────────────────────────── */
.card-main {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px 16px;
  cursor: pointer;
  transition: background 0.15s;
  user-select: none;
}

.card-main:hover {
  background: #F8F9FA;
}

/* ── 左侧图标 ────────────────────────────────────── */
.card-icon {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.icon-emoji {
  font-size: 22px;
  line-height: 1;
}

/* ── 中间内容区 ──────────────────────────────────── */
.card-body {
  flex: 1;
  min-width: 0;
}

.card-title {
  font-size: 14px;
  font-weight: 500;
  color: #1F2937;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-bottom: 6px;
}

.card-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.func-tag {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
}

.token-info {
  font-size: 11px;
  color: #9CA3AF;
}

/* ── 右侧区域 ────────────────────────────────────── */
.card-right {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}

.card-time {
  font-size: 12px;
  color: #9CA3AF;
  white-space: nowrap;
}

.btn-delete {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: 1px solid transparent;
  border-radius: 6px;
  background: transparent;
  color: #D1D5DB;
  cursor: pointer;
  transition: all 0.15s;
  flex-shrink: 0;
}

.btn-delete:hover {
  color: #EF4444;
  background: #FEF2F2;
  border-color: #FECACA;
}

.expand-arrow {
  flex-shrink: 0;
  transition: transform 0.25s ease;
}

.expand-arrow.rotated {
  transform: rotate(180deg);
}

/* ── 折叠详情区 ──────────────────────────────────── */
.card-detail {
  border-top: 1px solid #EBEEF5;
  background: #F9FAFB;
  padding: 20px 24px;
  animation: slideDown 0.25s ease;
}

@keyframes slideDown {
  from { opacity: 0; max-height: 0; }
  to   { opacity: 1; max-height: 2000px; }
}

.detail-loading {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #9CA3AF;
  font-size: 13px;
  padding: 20px 0;
}

.detail-section {
  margin-bottom: 18px;
}

.detail-section:last-child {
  margin-bottom: 0;
}

.detail-label {
  font-size: 13px;
  font-weight: 600;
  color: #6B7280;
  margin-bottom: 8px;
}

.detail-content {
  background: #FFF;
  border: 1px solid #E5E7EB;
  border-radius: 8px;
  padding: 14px 16px;
  font-size: 13px;
  line-height: 1.7;
  color: #374151;
  overflow-x: auto;
  white-space: pre-wrap;
  word-break: break-word;
  font-family: 'Fira Code', 'Consolas', 'Courier New', monospace;
}

.detail-content.error-content {
  background: #FFF5F5;
  border-color: #FECACA;
  color: #991B1B;
}

/* ── Markdown 内容 ────────────────────────────────── */
.markdown-body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', sans-serif;
  white-space: normal;
}

.markdown-body :deep(h1),
.markdown-body :deep(h2),
.markdown-body :deep(h3),
.markdown-body :deep(h4) {
  margin: 16px 0 8px;
  color: #1F2937;
  font-weight: 600;
}

.markdown-body :deep(h1) { font-size: 18px; }
.markdown-body :deep(h2) { font-size: 16px; border-bottom: 1px solid #E5E7EB; padding-bottom: 6px; }
.markdown-body :deep(h3) { font-size: 14px; }

.markdown-body :deep(p) { margin: 8px 0; line-height: 1.8; }

.markdown-body :deep(code) {
  background: #F0F2F5;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-family: 'Fira Code', 'Consolas', monospace;
  color: #D63384;
}

.markdown-body :deep(pre) {
  background: #1E1E2E;
  color: #CDD6F4;
  padding: 16px 20px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 10px 0;
  font-size: 13px;
  line-height: 1.7;
  tab-size: 4;
}

.markdown-body :deep(pre code) {
  background: transparent;
  color: inherit;
  padding: 0;
  font-size: inherit;
}

.markdown-body :deep(ul),
.markdown-body :deep(ol) {
  padding-left: 22px;
  margin: 8px 0;
}

.markdown-body :deep(li) { margin: 4px 0; }

.markdown-body :deep(blockquote) {
  border-left: 3px solid #3B82F6;
  padding: 8px 16px;
  margin: 10px 0;
  background: rgba(59, 130, 246, 0.04);
  border-radius: 0 6px 6px 0;
  color: #6B7280;
}

.markdown-body :deep(table) {
  border-collapse: collapse;
  margin: 10px 0;
  width: 100%;
}

.markdown-body :deep(th),
.markdown-body :deep(td) {
  padding: 8px 12px;
  border: 1px solid #E5E7EB;
  text-align: left;
  font-size: 13px;
}

.markdown-body :deep(th) {
  background: #F9FAFB;
  font-weight: 600;
}

.markdown-body :deep(strong) { color: #1F2937; }

/* ── 分页 ────────────────────────────────────────── */
.pagination-wrap {
  display: flex;
  justify-content: center;
  margin-top: 24px;
}

/* Element Plus 分页主题色覆盖 */
.pagination-wrap :deep(.el-pagination.is-background .el-pager li:not(.is-disabled).is-active) {
  background-color: #3B82F6;
}

.pagination-wrap :deep(.el-pagination.is-background .el-pager li:not(.is-disabled):hover) {
  color: #3B82F6;
}

.pagination-wrap :deep(.el-pagination .btn-prev:hover),
.pagination-wrap :deep(.el-pagination .btn-next:hover) {
  color: #3B82F6;
}

.pagination-wrap :deep(.el-pagination.is-background .btn-prev),
.pagination-wrap :deep(.el-pagination.is-background .btn-next) {
  background: #FFF;
  border: 1px solid #E5E7EB;
  border-radius: 8px;
}

.pagination-wrap :deep(.el-pagination.is-background .el-pager li) {
  border-radius: 8px;
  margin: 0 2px;
}
</style>
