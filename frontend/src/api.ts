// 后端API封装
// 后端地址通过vite proxy代理，前端直接请求 /api/xxx

const API_BASE = '/api'

// 发送聊天消息
export async function sendMessage(userId: string, message: string, sessionId?: string) {
  const res = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ userId, message, sessionId: sessionId || null }),
  })
  if (!res.ok) throw new Error(`请求失败: ${res.status}`)
  return res.json()
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
