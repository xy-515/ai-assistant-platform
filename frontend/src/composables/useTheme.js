import { ref, watchEffect } from 'vue'

const THEME_KEY = 'ai-platform-theme'
const theme = ref(localStorage.getItem(THEME_KEY) || 'light')

function applyTheme(name) {
  document.body.classList.remove('theme-light', 'theme-dark')
  document.body.classList.add(`theme-${name}`)
}

// 初始应用
applyTheme(theme.value)

// 监听变化 → 写 localStorage + 更新 body class
watchEffect(() => {
  localStorage.setItem(THEME_KEY, theme.value)
  applyTheme(theme.value)
})

export function useTheme() {
  const isDark = () => theme.value === 'dark'

  function toggle() {
    theme.value = theme.value === 'dark' ? 'light' : 'dark'
  }

  function setTheme(name) {
    theme.value = name
  }

  return { theme, isDark, toggle, setTheme }
}
