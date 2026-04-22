import { useState, useEffect, useRef } from 'react'
import { Input, Button, List, Spin, message } from 'antd'
import { SendOutlined, PlusOutlined } from '@ant-design/icons'
import { sendMessage, getHistory, getSessions } from './api'
import './App.css'

// 消息类型
interface ChatMsg {
  id: number
  role: string      // USER 或 ASSISTANT
  content: string
  created_at: string
}

// 暂时写死用户ID，不做认证
const USER_ID = 'user001'

function App() {
  const [sessions, setSessions] = useState<string[]>([])        // 会话ID列表
  const [activeSession, setActiveSession] = useState<string>('') // 当前会话ID
  const [messages, setMessages] = useState<ChatMsg[]>([])        // 当前会话的消息
  const [input, setInput] = useState('')                        // 输入框内容
  const [loading, setLoading] = useState(false)                 // 发送中loading
  const msgEndRef = useRef<HTMLDivElement>(null)                // 用于自动滚到底部

  // 页面加载时获取会话列表
  useEffect(() => {
    loadSessions()
  }, [])

  // 切换会话时加载历史消息
  useEffect(() => {
    if (activeSession) {
      loadHistory(activeSession)
    } else {
      setMessages([])
    }
  }, [activeSession])

  // 消息更新时自动滚到底部
  useEffect(() => {
    msgEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // 加载会话列表
  async function loadSessions() {
    try {
      const data = await getSessions(USER_ID)
      setSessions(data)
      // 如果有会话，默认选中第一个
      if (data.length > 0 && !activeSession) {
        setActiveSession(data[0])
      }
    } catch {
      message.error('加载会话列表失败')
    }
  }

  // 加载会话历史
  async function loadHistory(sessionId: string) {
    try {
      const data = await getHistory(sessionId)
      setMessages(data)
    } catch {
      message.error('加载历史消息失败')
    }
  }

  // 新建会话
  function newSession() {
    setActiveSession('')
    setMessages([])
  }

  // 发送消息
  async function handleSend() {
    const text = input.trim()
    if (!text || loading) return

    setLoading(true)
    // 先在界面上显示用户消息（乐观更新）
    const tempUserMsg: ChatMsg = {
      id: Date.now(),
      role: 'USER',
      content: text,
      created_at: new Date().toISOString(),
    }
    setMessages(prev => [...prev, tempUserMsg])
    setInput('')

    try {
      // 调后端接口
      const data = await sendMessage(USER_ID, text, activeSession || undefined)
      // 如果是新会话，后端会返回session_id，切换过去
      if (!activeSession) {
        setActiveSession(data.session_id)
        loadSessions()
      }
      // 追加助手回复到消息列表
      const assistantMsg: ChatMsg = {
        id: Date.now() + 1,
        role: 'ASSISTANT',
        content: data.reply,
        created_at: new Date().toISOString(),
      }
      setMessages(prev => [...prev, assistantMsg])
    } catch {
      message.error('发送失败，请重试')
    } finally {
      setLoading(false)
    }
  }

  // Enter发送，Shift+Enter换行
  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="app-container">
      {/* 左侧会话列表 */}
      <div className="sidebar">
        <div className="sidebar-header">
          <Button icon={<PlusOutlined />} block onClick={newSession}>
            新建会话
          </Button>
        </div>
        <List
          className="session-list"
          dataSource={sessions}
          renderItem={(sid) => (
            <List.Item
              className={`session-item ${sid === activeSession ? 'active' : ''}`}
              onClick={() => setActiveSession(sid)}
            >
              <span className="session-text">{sid}</span>
            </List.Item>
          )}
        />
      </div>

      {/* 右侧聊天区 */}
      <div className="chat-area">
        {/* 标题栏 */}
        <div className="chat-header">企业员工助手</div>

        {/* 消息区域 */}
        <div className="chat-messages">
          {messages.length === 0 && (
            <div className="empty-tip">输入问题开始对话，如：婚假能请几天？</div>
          )}
          {messages.map((msg) => (
            <div key={msg.id} className={`msg-row ${msg.role === 'USER' ? 'user' : 'assistant'}`}>
              <div className={`msg-bubble ${msg.role === 'USER' ? 'user' : 'assistant'}`}>
                {msg.content.split('\n').map((line, i) => (
                  <span key={i}>
                    {line}
                    {i < msg.content.split('\n').length - 1 && <br />}
                  </span>
                ))}
              </div>
            </div>
          ))}
          {/* 发送中显示loading气泡 */}
          {loading && (
            <div className="msg-row assistant">
              <div className="msg-bubble assistant loading-bubble">
                <Spin size="small" /> 思考中...
              </div>
            </div>
          )}
          <div ref={msgEndRef} />
        </div>

        {/* 输入区域 */}
        <div className="chat-input">
          <Input.TextArea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="输入您的问题... (Enter发送，Shift+Enter换行)"
            autoSize={{ minRows: 1, maxRows: 4 }}
            disabled={loading}
          />
          <Button
            type="primary"
            icon={<SendOutlined />}
            onClick={handleSend}
            loading={loading}
            disabled={!input.trim()}
          >
            发送
          </Button>
        </div>
      </div>
    </div>
  )
}

export default App
