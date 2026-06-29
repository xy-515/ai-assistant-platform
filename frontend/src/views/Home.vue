<script setup>
import { ref } from 'vue'
import PaperAssistant from '../components/PaperAssistant.vue'
import CodeAssistant from '../components/CodeAssistant.vue'

const activeTab = ref('paper')
</script>

<template>
  <div class="home">
    <div class="tabs-card page-card-enter">
      <!-- Tab Bar -->
      <el-tabs v-model="activeTab" class="main-tabs">
        <el-tab-pane label="论文助手" name="paper">
          <template #label>
            <span class="tab-label">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
              <span>论文助手</span>
            </span>
          </template>
          <PaperAssistant />
        </el-tab-pane>

        <el-tab-pane label="代码助手" name="code">
          <template #label>
            <span class="tab-label">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>
              <span>代码助手</span>
            </span>
          </template>
          <CodeAssistant />
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<style scoped>
/* ── Page Layout ────────────────────────────────────── */
.home {
  max-width: 1100px;
  margin: 0 auto;
  padding: 24px;

  @media (max-width: 768px) {
    padding: 12px;
  }
}

/* ── Card Shell ─────────────────────────────────────── */
.tabs-card {
  background: #FFF;
  border-radius: 16px;
  box-shadow: 0 2px 16px rgba(0, 0, 0, 0.06);
  overflow: hidden;
}

/* ── Tabs — Element Plus Override ───────────────────── */
.main-tabs {
  :deep(.el-tabs__header) {
    margin: 0;
    padding: 0 20px;
    background: #FAFBFC;
    border-bottom: 1px solid #EBEEF5;
  }

  :deep(.el-tabs__nav-wrap::after) {
    display: none;
  }

  :deep(.el-tabs__item) {
    height: 52px;
    line-height: 52px;
    padding: 0 24px;
    font-size: 15px;
    font-weight: 600;
    color: #909399;
    transition: color 0.25s, background 0.25s;

    &:hover {
      color: #555;
    }

    &.is-active {
      color: #2D6AFF;
    }
  }

  :deep(.el-tabs__active-bar) {
    height: 3px;
    border-radius: 3px 3px 0 0;
    background: linear-gradient(90deg, #667eea, #764ba2);
  }

  :deep(.el-tabs__content) {
    padding: 0;
  }
}

/* Tab label: icon + text */
.tab-label {
  display: inline-flex;
  align-items: center;
  gap: 8px;

  svg {
    transition: transform 0.2s;
  }
}

.el-tabs__item.is-active .tab-label svg {
  color: #2D6AFF;
}

/* ── Content Area (inside each tab-pane) ─────────────── */
:deep(.el-tab-pane) {
  padding: 24px;

  @media (max-width: 768px) {
    padding: 16px;
  }
}

/* ── Textarea (shared by both assistants) ───────────── */
:deep(.el-textarea__inner) {
  min-height: 160px !important;
  font-size: 14px;
  font-family: 'Fira Code', 'Consolas', 'Courier New', monospace;
  line-height: 1.7;
  color: #1A1A2E;
  background: #F8F9FB;
  border: 1px solid #E4E7ED;
  border-radius: 8px;
  padding: 14px 16px;
  resize: vertical;
  transition: border-color 0.2s, box-shadow 0.2s;

  &:focus {
    border-color: #2D6AFF;
    box-shadow: 0 0 0 3px rgba(45, 106, 255, 0.08);
    background: #FFF;
  }

  &::placeholder {
    color: #BBB;
  }
}

/* Error textarea variant */
:deep(.el-textarea.error-input .el-textarea__inner) {
  background: #FFF5F5;
  border-color: #FBC4C4;
  min-height: 80px !important;

  &:focus {
    border-color: #F56C6C;
    box-shadow: 0 0 0 3px rgba(245, 108, 108, 0.08);
  }
}

/* ── Select + Button Row ────────────────────────────── */
.control-row {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;

  @media (max-width: 600px) {
    flex-direction: column;
    align-items: stretch;
  }
}

:deep(.el-select) {
  width: 180px;

  @media (max-width: 600px) {
    width: 100%;
  }

  .el-input__wrapper {
    border-radius: 8px;
    box-shadow: none !important;
    border: 1px solid #E4E7ED;
    transition: border-color 0.2s;

    &:hover {
      border-color: #C0C4CC;
    }
  }

  &.is-focus .el-input__wrapper {
    border-color: #2D6AFF;
    box-shadow: 0 0 0 3px rgba(45, 106, 255, 0.08) !important;
  }
}

/* Submit button */
:deep(.el-button--primary) {
  border-radius: 8px;
  font-weight: 500;
  padding: 10px 28px;
  transition: all 0.25s;

  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 14px rgba(45, 106, 255, 0.3);
  }
}

/* ── Result Area ────────────────────────────────────── */
.result-block {
  margin-top: 24px;
  background: #F8F9FB;
  border: 1px solid #EBEEF5;
  border-radius: 8px;
  padding: 20px;
  line-height: 1.8;
  font-size: 15px;
  color: #333;

  /* Markdown content */
  :deep(h1), :deep(h2), :deep(h3), :deep(h4) {
    margin: 20px 0 10px;
    color: #1A1A2E;
    font-weight: 600;
  }

  :deep(h1) { font-size: 20px; }
  :deep(h2) { font-size: 18px; border-bottom: 1px solid #EBEEF5; padding-bottom: 6px; }
  :deep(h3) { font-size: 16px; }

  :deep(p) {
    margin: 8px 0;
    line-height: 1.8;
  }

  /* Inline code */
  :deep(code) {
    font-family: 'Fira Code', 'Consolas', monospace;
    font-size: 13px;
    background: #E8ECF1;
    color: #D63384;
    padding: 2px 8px;
    border-radius: 4px;
  }

  /* Code block — dark theme */
  :deep(pre) {
    background: #1E1E2E;
    color: #CDD6F4;
    padding: 16px 20px;
    border-radius: 8px;
    overflow-x: auto;
    margin: 12px 0;
    font-size: 13px;
    line-height: 1.7;
    tab-size: 4;

    code {
      background: transparent;
      color: inherit;
      padding: 0;
    }
  }

  /* Python syntax highlight hints */
  :deep(pre code .keyword) { color: #CBA6F7; }
  :deep(pre code .string)  { color: #A6E3A1; }
  :deep(pre code .comment) { color: #6C7086; }
  :deep(pre code .number)  { color: #FAB387; }

  :deep(ul), :deep(ol) {
    padding-left: 24px;
    margin: 8px 0;
  }

  :deep(li) {
    margin: 4px 0;
  }

  :deep(blockquote) {
    border-left: 3px solid #2D6AFF;
    padding: 8px 16px;
    margin: 12px 0;
    background: rgba(45, 106, 255, 0.04);
    border-radius: 0 6px 6px 0;
    color: #555;
  }

  :deep(table) {
    border-collapse: collapse;
    margin: 12px 0;
    width: 100%;

    th, td {
      padding: 8px 14px;
      border: 1px solid #E4E7ED;
      text-align: left;
    }

    th {
      background: #F0F2F5;
      font-weight: 600;
    }
  }

  :deep(strong) {
    color: #1A1A2E;
  }

  :deep(hr) {
    border: none;
    border-top: 1px solid #E4E7ED;
    margin: 20px 0;
  }
}
</style>
