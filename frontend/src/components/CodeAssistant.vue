<script setup>
import { ref, computed } from 'vue'
import { marked } from 'marked'
import { useStreaming } from '../composables/useStreaming'
import MonacoEditor from './MonacoEditor.vue'

const code = ref('')
const errorInput = ref('')
const func = ref('review')
const loading = ref(false)
const submitError = ref('')
const fileName = ref('')
const isDragging = ref(false)
const detectedLang = ref('python')
const fileInput = ref(null)

const { result, streamPost } = useStreaming()

const functions = [
  { value: 'review',        label: '代码审查',   icon: '🔍' },
  { value: 'generate_test', label: '生成测试',   icon: '🧪' },
  { value: 'fix',           label: '修复 Bug',   icon: '🔧' },
]

const EXT_MAP = {
  py: 'python', js: 'javascript', ts: 'typescript',
  java: 'java', cpp: 'cpp', cc: 'cpp', cxx: 'cpp', c: 'cpp',
  go: 'go', rs: 'rust', swift: 'swift', kt: 'kotlin',
  html: 'html', css: 'css', scss: 'scss', json: 'json',
  yaml: 'yaml', yml: 'yaml', xml: 'xml', sql: 'sql',
  sh: 'bash', bat: 'batch', vue: 'vue', jsx: 'jsx', tsx: 'tsx',
}

const LANG_LABELS = {
  python: 'Python', javascript: 'JavaScript', typescript: 'TypeScript',
  java: 'Java', cpp: 'C++', go: 'Go', rust: 'Rust',
}

const ACCEPT = '.py,.js,.ts,.jsx,.tsx,.java,.cpp,.c,.cc,.go,.rs,.swift,.kt,.html,.css,.scss,.json,.yaml,.yml,.xml,.sql,.sh,.bat,.vue,.txt'

const acceptLabel = computed(() => {
  if (func.value === 'fix') return '支持 .py .js .java .cpp .go 等代码文件'
  if (func.value === 'generate_test') return '输入需求描述，也可上传 .txt'
  return '支持 .py .js .ts .java .cpp .go 等主流语言'
})

// ── 文件处理 ──────────────────────────────────────────
function triggerFile() { fileInput.value?.click() }
function handleFile(e) {
  const file = e.target.files?.[0]
  if (!file) return
  const ext = file.name.split('.').pop()?.toLowerCase()
  if (ext && EXT_MAP[ext]) detectedLang.value = EXT_MAP[ext]
  readFile(file)
  e.target.value = ''
}
function readFile(file) {
  const reader = new FileReader()
  reader.onload = () => { code.value = reader.result; fileName.value = file.name }
  reader.onerror = () => { submitError.value = '文件读取失败' }
  reader.readAsText(file)
}
function clearFile() { fileName.value = ''; code.value = ''; if (fileInput.value) fileInput.value.value = '' }
function onDragOver(e) { e.preventDefault(); isDragging.value = true }
function onDragLeave() { isDragging.value = false }
function onDrop(e) { e.preventDefault(); isDragging.value = false; const file = e.dataTransfer?.files?.[0]; if (file) readFile(file) }

// ── 提交（流式）───────────────────────────────────────
async function submit() {
  if (!code.value.trim()) return
  submitError.value = ''
  loading.value = true
  try {
    const endpoints = {
      review:        { url: '/code/stream/review',   body: { code: code.value, language: detectedLang.value } },
      generate_test: { url: '/code/stream/generate', body: { requirement: code.value, language: detectedLang.value } },
      fix:           { url: '/code/stream/debug',    body: { code: code.value, error: errorInput.value, language: detectedLang.value } },
    }
    const ep = endpoints[func.value]
    await streamPost(ep.url, ep.body)
  } catch (e) {
    submitError.value = e.message || '请求失败'
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
  a.download = `code-${func.value}-${Date.now()}.md`
  a.click()
  URL.revokeObjectURL(url)
}

// ── Diff 提取（从修复结果中分离原始代码和修复代码）─────
const diffView = ref(false)
const fixedCode = computed(() => {
  if (func.value !== 'fix' || !result.value) return ''
  // 尝试提取 ``` 代码块
  const matches = result.value.match(/```[\w]*\n([\s\S]*?)```/g)
  if (!matches || matches.length < 2) return ''
  // 取最后一个代码块作为修复后的代码
  const last = matches[matches.length - 1]
  return last.replace(/```[\w]*\n/, '').replace(/```$/, '').trim()
})

function onFuncChange() { result.value = ''; submitError.value = ''; diffView.value = false }
</script>

<template>
  <div class="assistant">
    <!-- Controls -->
    <div class="control-row">
      <el-select v-model="func" class="func-select" @change="onFuncChange">
        <el-option v-for="f in functions" :key="f.value" :label="f.label" :value="f.value">
          <span>{{ f.icon }} {{ f.label }}</span>
        </el-option>
      </el-select>
      <el-button type="primary" :loading="loading" :disabled="!code.trim()" @click="submit">
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
          <span class="file-icon">💻</span><span class="file-name">{{ fileName }}</span>
          <span v-if="detectedLang" class="lang-tag">{{ LANG_LABELS[detectedLang] || detectedLang }}</span>
          <button class="file-remove" @click.stop="clearFile" title="移除文件">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
          </button>
        </div>
        <span class="file-hint">已加载 {{ code.length }} 字符</span>
      </template>
      <template v-else>
        <div class="drop-icon">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#909399" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
        </div>
        <p class="drop-text">点击选择桌面代码文件，或拖拽到此处</p>
        <p class="drop-hint">{{ acceptLabel }}</p>
      </template>
    </div>

    <!-- Monaco Editor -->
    <MonacoEditor v-model="code" :language="detectedLang" height="380px" />

    <!-- Error Input (fix mode only) -->
    <div v-if="func === 'fix'" class="error-section">
      <div class="error-label">⚠️ 报错信息（可选）</div>
      <textarea v-model="errorInput" class="error-textarea" placeholder="粘贴报错日志或异常信息..." rows="3"></textarea>
    </div>

    <p v-if="submitError" class="error-msg">{{ submitError }}</p>

    <!-- Streaming cursor -->
    <div v-if="loading" class="streaming-hint">
      <span class="cursor-blink">▌</span> 正在生成...
    </div>

    <!-- Result -->
    <div v-if="result" class="result-area">
      <div class="result-toolbar">
        <span class="result-label">{{ functions.find(f => f.value === func)?.icon }} 生成结果</span>
        <div class="result-actions">
          <button v-if="func === 'fix' && fixedCode" class="action-btn" @click="diffView = !diffView">
            {{ diffView ? '📝 隐藏 Diff' : '🔍 查看 Diff' }}
          </button>
          <button class="action-btn" @click="copyResult">{{ copied ? '✅ 已复制' : '📋 复制' }}</button>
          <button class="action-btn" @click="downloadMD">💾 下载 .md</button>
        </div>
      </div>

      <!-- Diff 对比视图 -->
      <div v-if="diffView && func === 'fix' && fixedCode" class="diff-container">
        <div class="diff-panel">
          <div class="diff-panel-header">❌ 原始代码</div>
          <pre class="diff-code original">{{ code }}</pre>
        </div>
        <div class="diff-panel">
          <div class="diff-panel-header fixed">✅ 修复后代码</div>
          <pre class="diff-code fixed">{{ fixedCode }}</pre>
        </div>
      </div>

      <!-- Markdown 结果 -->
      <div class="result-content" v-html="marked(result, { breaks: true })"></div>
    </div>
  </div>
</template>

<style scoped>
.assistant { display: flex; flex-direction: column; gap: 14px; }
.control-row { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.func-select { width: 150px; }

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
.file-name { color: #1F2937; font-weight: 500; max-width: 200px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.lang-tag { padding: 1px 8px; background: #E0F2FE; color: #0369A1; border-radius: 10px; font-size: 11px; font-weight: 600; }
.file-remove {
  display: flex; align-items: center; justify-content: center;
  width: 22px; height: 22px; border: none; border-radius: 50%;
  background: #FEE2E2; color: #EF4444; cursor: pointer; transition: all 0.15s; flex-shrink: 0;
}
.file-remove:hover { background: #FECACA; }
.file-hint { font-size: 12px; color: #67C23A; }

/* ── Error Section ──────────────────────────────────── */
.error-section { display: flex; flex-direction: column; gap: 6px; }
.error-label { font-size: 13px; font-weight: 500; color: #F56C6C; display: flex; align-items: center; gap: 4px; }
.error-textarea {
  width: 100%; min-height: 64px; padding: 10px 14px;
  border: 1px solid #FBC4C4; border-radius: 8px; outline: none; resize: vertical;
  font-family: 'Fira Code', monospace; font-size: 13px; line-height: 1.5;
  color: #1A1A2E; background: #FFF5F5; transition: border-color 0.2s, box-shadow 0.2s;
}
.error-textarea:focus { border-color: #F56C6C; box-shadow: 0 0 0 3px rgba(245,108,108,0.12); }
.error-textarea::placeholder { color: #DBB0B0; }
.error-msg { color: #F56C6C; font-size: 13px; }

/* ── Streaming ─────────────────────────────────────── */
.streaming-hint { font-size: 14px; color: #3B82F6; padding: 8px 0; }
.cursor-blink { animation: blink 0.8s infinite; }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0} }

/* ── Result Area ───────────────────────────────────── */
.result-area {
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

/* ── Diff Container ────────────────────────────────── */
.diff-container {
  display: grid; grid-template-columns: 1fr 1fr; gap: 1px;
  background: #EBEEF5; border-bottom: 1px solid #EBEEF5;
}
.diff-panel { background: #FFF; overflow: hidden; }
.diff-panel-header {
  padding: 8px 14px; font-size: 12px; font-weight: 600; color: #606266;
  background: #F8F9FB; border-bottom: 1px solid #EBEEF5;
}
.diff-panel-header.fixed { color: #16A34A; }
.diff-code {
  padding: 14px; margin: 0; font-family: 'Fira Code', monospace;
  font-size: 12px; line-height: 1.65; white-space: pre-wrap; word-break: break-all;
  overflow-x: auto; max-height: 400px; overflow-y: auto;
  color: #374151; border: none; border-radius: 0; background: transparent;
}
.diff-code.fixed { background: #F6FEF6; }

/* ── Result Content ────────────────────────────────── */
.result-content { padding: 20px; line-height: 1.8; font-size: 15px; color: #333; }
.result-content :deep(h1),.result-content :deep(h2),.result-content :deep(h3) { margin: 18px 0 10px; color: #1F2937; font-weight: 600; }
.result-content :deep(h2) { font-size: 18px; border-bottom: 1px solid #EBEEF5; padding-bottom: 6px; }
.result-content :deep(h3) { font-size: 16px; }
.result-content :deep(p) { margin: 8px 0; }
.result-content :deep(code) { background: #F0F2F5; padding: 2px 8px; border-radius: 4px; font-size: 13px; color: #D63384; font-family: 'Fira Code', monospace; }
.result-content :deep(pre) { background: #1E1E2E; color: #CDD6F4; padding: 16px 20px; border-radius: 8px; overflow-x: auto; margin: 12px 0; font-size: 13px; line-height: 1.7; }
.result-content :deep(pre code) { background: transparent; color: inherit; padding: 0; }
.result-content :deep(ul),.result-content :deep(ol) { padding-left: 24px; margin: 8px 0; }
.result-content :deep(table) { border-collapse: collapse; width: 100%; margin: 12px 0; }
.result-content :deep(th),.result-content :deep(td) { padding: 8px 14px; border: 1px solid #E4E7ED; }
.result-content :deep(th) { background: #F0F2F5; font-weight: 600; }

@keyframes card-rise-in { from { opacity: 0; transform: translateY(12px); } to { opacity: 1; transform: translateY(0); } }
</style>
