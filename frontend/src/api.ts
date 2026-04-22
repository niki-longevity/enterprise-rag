// 后端API封装
// 后端地址通过vite proxy代理，前端直接请求 /api/xxx

const API_BASE = '/api'

// 发送聊天消息（流式）
export async function sendMessageStream(
  userId: string,
  message: string,
  sessionId: string | undefined,
  onChunk: (chunk: string) => void,
  onEnd: (sessionId: string) => void,
  onError: (error: string) => void
) {
  const res = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ userId, message, sessionId: sessionId || null }),
  })

  if (!res.ok) {
    onError(`请求失败: ${res.status}`)
    return
  }

  const reader = res.body!.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  try {
    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6))
            if (data.type === 'content') {
              onChunk(data.content)
            } else if (data.type === 'end') {
              onEnd(data.session_id)
            } else if (data.type === 'error') {
              onError(data.content)
            }
          } catch {
            // 忽略解析错误
          }
        }
      }
    }
  } catch (e) {
    onError(e instanceof Error ? e.message : '未知错误')
  }
}

// 获取会话历史消息
export async function getHistory(sessionId: string) {
  const res = await fetch(`${API_BASE}/history?session_id=${encodeURIComponent(sessionId)}`)
  if (!res.ok) throw new Error(`请求失败: ${res.status}`)
  return res.json()
}

// 获取用户的会话列表
export async function getSessions(userId: string) {
  const res = await fetch(`${API_BASE}/sessions?user_id=${encodeURIComponent(userId)}`)
  if (!res.ok) throw new Error(`请求失败: ${res.status}`)
  return res.json()
}
