<script setup>
import { ref, computed } from 'vue'
import { marked } from 'marked'
import { useStreaming } from '../composables/useStreaming'

const content = ref('')
const func = ref('polish')
const polishMode = ref('academic')
const loading = ref(false)
const error = ref('')
const fileName = ref('')
const isDragging = ref(false)
const fileInput = ref(null)

const { result, streamPost } = useStreaming()

const functions = [
  { value: 'polish',  label: '润色优化', icon: '✨' },
  { value: 'outline', label: '大纲生成', icon: '📋' },
  { value: 'review',  label: '论文点评', icon: '🔍' },
]

const modes = [
  { value: 'academic', label: '学术风格', desc: '正式学术用语' },
  { value: 'concise',  label: '简洁化',   desc: '去除冗余表达' },
  { value: 'deweight', label: '降重改写', desc: '降低重复率' },
]

const ACCEPT = '.txt,.md,.doc,.docx'

const acceptLabel = computed(() => {
  if (func.value === 'outline') return '支持 .txt .md（题目/大纲草稿）'
  return '支持 .txt .md .doc .docx（论文正文）'
})

// ── 文件处理 ──────────────────────────────────────────
function triggerFile() { fileInput.value?.click() }
function handleFile(e) {
  const file = e.target.files?.[0]
  if (!file) return
  readFile(file)
  e.target.value = ''
}
function readFile(file) {
  const reader = new FileReader()
  reader.onload = () => { content.value = reader.result; fileName.value = file.name }
  reader.onerror = () => { error.value = '文件读取失败' }
  reader.readAsText(file)
}
function clearFile() { fileName.value = ''; content.value = ''; if (fileInput.value) fileInput.value.value = '' }
function onDragOver(e) { e.preventDefault(); isDragging.value = true }
function onDragLeave() { isDragging.value = false }
function onDrop(e) { e.preventDefault(); isDragging.value = false; const file = e.dataTransfer?.files?.[0]; if (file) readFile(file) }

// ── 提交（流式）───────────────────────────────────────
async function submit() {
  if (!content.value.trim()) return
  error.value = ''
  loading.value = true
  try {
    const endpoints = {
      outline: { url: '/paper/stream/outline', body: { title: content.value } },
      polish:  { url: '/paper/stream/polish',  body: { text: content.value, mode: polishMode.value } },
      review:  { url: '/paper/stream/feedback', body: { fragment: content.value } },
    }
    const ep = endpoints[func.value]
    await streamPost(ep.url, ep.body)
  } catch (e) {
    error.value = e.message || '请求失败'
  } finally {
    loading.value = false
  }
}

// ── 导出 ──────────────────────────────────────────────
const copied = ref(false)
async function copyResult() {
  await navigator.clipboard.writeText(result.value)
  copied.value = true
  setTimeout(() => copied.value = false, 2000)
}

function downloadMD() {
  const blob = new Blob([result.value], { type: 'text/markdown' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `paper-${func.value}-${Date.now()}.md`
  a.click()
  URL.revokeObjectURL(url)
}

// 切换功能时清空结果
function onFuncChange() { result.value = ''; error.value = '' }
</script>

<template>
  <div class="assistant">
    <!-- Controls Row -->
    <div class="control-row">
      <el-select v-model="func" class="func-select" @change="onFuncChange">
        <el-option v-for="f in functions" :key="f.value" :label="f.label" :value="f.value">
          <span>{{ f.icon }} {{ f.label }}</span>
        </el-option>
      </el-select>

      <!-- 润色模式选择器 -->
      <div v-if="func === 'polish'" class="mode-selector">
        <button
          v-for="m in modes" :key="m.value"
          class="mode-btn"
          :class="{ active: polishMode === m.value }"
          @click="polishMode = m.value"
          :title="m.desc"
        >
          {{ m.label }}
        </button>
      </div>

      <el-button type="primary" :loading="loading" :disabled="!content.trim()" @click="submit">
        <span v-if="!loading">{{ functions.find(f => f.value === func)?.icon }}</span>
        {{ loading ? '生成中...' : '提交' }}
      </el-button>
    </div>

    <!-- File Upload Drop Zone -->
    <div class="drop-zone" :class="{ dragging: isDragging, 'has-file': !!fileName }"
      @click="triggerFile" @dragover="onDragOver" @dragleave="onDragLeave" @drop="onDrop">
      <input ref="fileInput" type="file" :accept="ACCEPT" class="file-input-hidden" @change="handleFile" />
      <template v-if="fileName">
        <div class="file-chip">
          <span class="file-icon">📄</span><span class="file-name">{{ fileName }}</span>
          <button class="file-remove" @click.stop="clearFile" title="移除文件">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
          </button>
        </div>
        <span class="file-hint">已加载 {{ content.length }} 字符</span>
      </template>
      <template v-else>
        <div class="drop-icon">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#909399" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
        </div>
        <p class="drop-text">点击选择桌面文件，或拖拽到此处</p>
        <p class="drop-hint">{{ acceptLabel }}</p>
      </template>
    </div>

    <!-- Input Textarea -->
    <el-input v-model="content" type="textarea"
      :placeholder="fileName ? '文件内容已加载，可直接编辑...' : '在此粘贴或输入论文内容...'"
      :rows="10" class="main-input" />

    <p v-if="error" class="error-msg">{{ error }}</p>

    <!-- Streaming cursor -->
    <div v-if="loading" class="streaming-hint">
      <span class="cursor-blink">▌</span> 正在生成...
    </div>

    <!-- Result -->
    <div v-if="result" class="result-block">
      <div class="result-toolbar">
        <span class="result-label">{{ functions.find(f => f.value === func)?.icon }} 生成结果</span>
        <div class="result-actions">
          <button class="action-btn" @click="copyResult">
            {{ copied ? '✅ 已复制' : '📋 复制' }}
          </button>
          <button class="action-btn" @click="downloadMD">💾 下载 .md</button>
        </div>
      </div>
      <div class="result-content" v-html="marked(result, { breaks: true })"></div>
    </div>
  </div>
</template>

<style scoped>
.assistant { display: flex; flex-direction: column; gap: 14px; }
.control-row { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.func-select { width: 150px; }

/* ── Polish Mode Selector ──────────────────────────── */
.mode-selector { display: flex; gap: 4px; background: #F0F2F5; border-radius: 8px; padding: 3px; }
.mode-btn {
  padding: 6px 14px; border: none; border-radius: 6px;
  font-size: 12px; font-weight: 500; cursor: pointer;
  background: transparent; color: #606266;
  transition: all 0.2s; white-space: nowrap;
}
.mode-btn:hover { color: #3B82F6; }
.mode-btn.active { background: #FFF; color: #3B82F6; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }

/* ── Drop Zone ──────────────────────────────────────── */
.drop-zone {
  display: flex; align-items: center; justify-content: center; gap: 12px;
  padding: 14px 20px; border: 2px dashed #D0D5DD; border-radius: 10px;
  background: #FAFBFC; cursor: pointer; transition: all 0.2s; user-select: none; min-height: 56px;
}
.drop-zone:hover { border-color: #667eea; background: #F0F2FF; }
.drop-zone.dragging { border-color: #667eea; background: #EBEEFF; box-shadow: 0 0 0 4px rgba(102,126,234,0.10); }
.drop-zone.has-file { border-style: solid; border-color: #67C23A; background: #F6FEF6; padding: 8px 14px; }
.file-input-hidden { display: none; }
.drop-icon { flex-shrink: 0; display: flex; }
.drop-text { font-size: 14px; color: #606266; margin: 0; }
.drop-hint { font-size: 12px; color: #909399; margin: 0; }
.file-chip {
  display: inline-flex; align-items: center; gap: 8px; padding: 5px 12px;
  background: #FFF; border: 1px solid #B7E4B7; border-radius: 8px; font-size: 13px;
}
.file-icon { font-size: 16px; }
.file-name { color: #1F2937; font-weight: 500; max-width: 220px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.file-remove {
  display: flex; align-items: center; justify-content: center;
  width: 22px; height: 22px; border: none; border-radius: 50%;
  background: #FEE2E2; color: #EF4444; cursor: pointer; transition: all 0.15s; flex-shrink: 0;
}
.file-remove:hover { background: #FECACA; }
.file-hint { font-size: 12px; color: #67C23A; }

.main-input :deep(.el-textarea__inner) { min-height: 200px !important; }
.error-msg { color: #F56C6C; font-size: 13px; }

/* ── Streaming ─────────────────────────────────────── */
.streaming-hint { font-size: 14px; color: #3B82F6; padding: 8px 0; }
.cursor-blink { animation: blink 0.8s infinite; }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0} }

/* ── Result ────────────────────────────────────────── */
.result-block {
  border: 1px solid #EBEEF5; border-radius: 10px; overflow: hidden;
  animation: card-rise-in 0.35s ease both;
}
.result-toolbar {
  display: flex; justify-content: space-between; align-items: center;
  padding: 10px 16px; background: #F8F9FB; border-bottom: 1px solid #EBEEF5;
}
.result-label { font-size: 13px; font-weight: 600; color: #606266; }
.result-actions { display: flex; gap: 8px; }
.action-btn {
  padding: 5px 14px; border: 1px solid #D0D5DD; border-radius: 6px;
  background: #FFF; font-size: 12px; color: #606266;
  cursor: pointer; transition: all 0.15s;
}
.action-btn:hover { border-color: #3B82F6; color: #3B82F6; background: #EEF3FF; }
.result-content { padding: 20px; line-height: 1.8; font-size: 15px; color: #333; }
.result-content :deep(h1),.result-content :deep(h2),.result-content :deep(h3) { margin: 18px 0 10px; color: #1F2937; font-weight: 600; }
.result-content :deep(h1) { font-size: 20px; }
.result-content :deep(h2) { font-size: 18px; border-bottom: 1px solid #EBEEF5; padding-bottom: 6px; }
.result-content :deep(h3) { font-size: 16px; }
.result-content :deep(p) { margin: 8px 0; }
.result-content :deep(code) { background: #F0F2F5; padding: 2px 8px; border-radius: 4px; font-size: 13px; color: #D63384; font-family: 'Fira Code', monospace; }
.result-content :deep(pre) { background: #1E1E2E; color: #CDD6F4; padding: 16px 20px; border-radius: 8px; overflow-x: auto; margin: 12px 0; font-size: 13px; line-height: 1.7; }
.result-content :deep(pre code) { background: transparent; color: inherit; padding: 0; }
.result-content :deep(ul),.result-content :deep(ol) { padding-left: 24px; margin: 8px 0; }
.result-content :deep(blockquote) { border-left: 3px solid #3B82F6; padding: 8px 16px; margin: 12px 0; background: rgba(59,130,246,0.04); border-radius: 0 6px 6px 0; color: #6B7280; }
.result-content :deep(table) { border-collapse: collapse; width: 100%; margin: 12px 0; }
.result-content :deep(th),.result-content :deep(td) { padding: 8px 14px; border: 1px solid #E4E7ED; }
.result-content :deep(th) { background: #F0F2F5; font-weight: 600; }
.result-content :deep(strong) { color: #1F2937; }

@keyframes card-rise-in { from { opacity: 0; transform: translateY(12px); } to { opacity: 1; transform: translateY(0); } }
</style>
