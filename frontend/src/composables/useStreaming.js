import { ref } from 'vue'
import { useAuthStore } from '../stores/auth'

/**
 * 流式请求 composable
 *
 * Usage:
 *   const { result, loading, error, streamPost } = useStreaming()
 *   await streamPost('/paper/stream/outline', { title: '...' })
 *
 * result 会逐字增长，模板中直接绑定即可看到打字机效果
 */
export function useStreaming() {
  const result = ref('')
  const loading = ref(false)
  const error = ref('')
  const meta = ref(null)  // 保存 id, created_at 等元数据

  async function streamPost(url, body) {
    result.value = ''
    error.value = ''
    meta.value = null
    loading.value = true

    const auth = useAuthStore()
    const BASE = '/api'

    try {
      const response = await fetch(`${BASE}${url}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(auth.token ? { Authorization: `Bearer ${auth.token}` } : {}),
        },
        body: JSON.stringify(body),
      })

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}))
        throw new Error(errData.detail || `请求失败 (${response.status})`)
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })

        // 解析 SSE 事件
        const lines = buffer.split('\n')
        buffer = lines.pop()  // 最后一行可能不完整，保留到下次

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6)
            if (data === '[DONE]') continue

            try {
              const parsed = JSON.parse(data)
              if (parsed.type === 'chunk') {
                result.value += parsed.content
              } else if (parsed.type === 'meta') {
                meta.value = parsed
              } else if (parsed.type === 'error') {
                throw new Error(parsed.message)
              }
            } catch (e) {
              if (e.message && !e.message.includes('JSON')) throw e
              // JSON parse error on partial chunk, ignore
            }
          } else if (line.startsWith('event: error')) {
            // handle error event
          }
        }
      }
    } catch (e) {
      error.value = e.message || '流式请求失败'
    } finally {
      loading.value = false
    }

    return { result, meta }
  }

  return { result, loading, error, meta, streamPost }
}
