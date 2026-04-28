import { useState, useEffect, useRef } from 'react'
import { Input, Button, List, Spin, message } from 'antd'
import { SendOutlined, PlusOutlined, LogoutOutlined } from '@ant-design/icons'
import { sendMessageStream, getHistory, getSessions } from './api'
import Login from './Login'
import './App.css'

// 消息类型
interface ChatMsg {
  id: number
  role: string      // USER 或 ASSISTANT
  content: string
  created_at: string
}

function App() {
  const [token, setToken] = useState<string>(localStorage.getItem('token') || '')
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
      const data = await getSessions()
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
    // 先加用户消息，再加一个空的助手消息占位
    const assistantMsgId = Date.now() + 1
    const emptyAssistantMsg: ChatMsg = {
      id: assistantMsgId,
      role: 'ASSISTANT',
      content: '',
      created_at: new Date().toISOString(),
    }
    setMessages(prev => [...prev, tempUserMsg, emptyAssistantMsg])
    setInput('')

    try {
      let finalSessionId = activeSession
      await sendMessageStream(
        text,
        activeSession || undefined,
        (chunk) => {
          // 流式接收每个chunk，追加到助手消息
          setMessages(prev => prev.map(msg => {
            if (msg.id === assistantMsgId) {
              return { ...msg, content: msg.content + chunk }
            }
            return msg
          }))
        },
        (sessionId) => {
          finalSessionId = sessionId
          if (!activeSession) {
            setActiveSession(sessionId)
            loadSessions()
          }
        },
        (error) => {
          message.error(error)
        }
      )
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

  if (!token) {
    return <Login onLogin={(t: string) => setToken(t)} />
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
        <div className="chat-header">
            企业员工助手
            <Button
              size="small"
              icon={<LogoutOutlined />}
              style={{ float: 'right', marginTop: 4 }}
              onClick={() => {
                localStorage.removeItem('token')
                setToken('')
                setSessions([])
                setActiveSession('')
                setMessages([])
              }}
            >
              退出
            </Button>
          </div>

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
                {/* 如果是正在生成的空消息，显示loading */}
                {loading && msg.role === 'ASSISTANT' && msg.content === '' && (
                  <Spin size="small" />
                )}
              </div>
            </div>
          ))}
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
