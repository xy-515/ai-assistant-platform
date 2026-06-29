<script setup>
import { ref, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import loader from '@monaco-editor/loader'

const props = defineProps({
  modelValue: { type: String, default: '' },
  language: { type: String, default: 'python' },
  readOnly: { type: Boolean, default: false },
  height: { type: String, default: '400px' },
})

const emit = defineEmits(['update:modelValue'])

const container = ref(null)
let editor = null
let monaco = null

onMounted(async () => {
  monaco = await loader.init()

  editor = monaco.editor.create(container.value, {
    value: props.modelValue,
    language: props.language,
    readOnly: props.readOnly,
    theme: 'vs-dark',
    fontSize: 14,
    fontFamily: "'Fira Code', 'Cascadia Code', 'Consolas', 'Courier New', monospace",
    lineNumbers: 'on',
    minimap: { enabled: false },
    scrollBeyondLastLine: false,
    automaticLayout: true,
    tabSize: 4,
    renderWhitespace: 'selection',
    bracketPairColorization: { enabled: true },
    padding: { top: 16, bottom: 16 },
    suggest: { showWords: true },
    wordBasedSuggestions: 'currentDocument',
  })

  editor.onDidChangeModelContent(() => {
    emit('update:modelValue', editor.getValue())
  })
})

watch(() => props.language, (lang) => {
  if (editor && monaco) {
    monaco.editor.setModelLanguage(editor.getModel(), lang)
  }
})

watch(() => props.modelValue, (val) => {
  if (editor && val !== editor.getValue()) {
    editor.setValue(val)
  }
})

onBeforeUnmount(() => {
  editor?.dispose()
})
</script>

<template>
  <div
    ref="container"
    class="monaco-wrapper"
    :style="{ height }"
  ></div>
</template>

<style scoped>
.monaco-wrapper {
  width: 100%;
  border-radius: 10px;
  overflow: hidden;
  border: 1px solid #DDD;
}
</style>
