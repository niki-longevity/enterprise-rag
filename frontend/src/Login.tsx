import { useState } from 'react'
import { Input, Button, Tabs, message } from 'antd'
import { UserOutlined, LockOutlined } from '@ant-design/icons'

interface Props {
  onLogin: (token: string) => void
}

function Login({ onLogin }: Props) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [tab, setTab] = useState('login')

  async function handleSubmit() {
    if (!username.trim() || !password.trim()) {
      message.warning('请输入用户名和密码')
      return
    }
    setLoading(true)
    try {
      const endpoint = tab === 'login' ? '/api/login' : '/api/register'
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: username.trim(), password }),
      })
      const data = await res.json()
      if (!res.ok) {
        message.error(data.detail || '请求失败')
        return
      }
      localStorage.setItem('token', data.token)
      onLogin(data.token)
    } catch {
      message.error('网络错误，请重试')
    } finally {
      setLoading(false)
    }
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === 'Enter') handleSubmit()
  }

  return (
    <div className="login-page">
      <div className="login-bg-decor" />
      <div className="login-card">
        <div className="login-accent-bar" />
        <div className="login-content">
          <div className="login-brand">
            <div className="login-icon">
              <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
                <rect width="32" height="32" rx="8" fill="var(--accent)"/>
                <path d="M16 8c-3.3 0-6 2.7-6 6 0 1.7.7 3.3 1.9 4.4l-.5 5.6 4.6-2.5 4.6 2.5-.5-5.6c1.2-1.1 1.9-2.7 1.9-4.4 0-3.3-2.7-6-6-6zm-2 7c-.6 0-1-.4-1-1s.4-1 1-1 1 .4 1 1-.4 1-1 1zm4 0c-.6 0-1-.4-1-1s.4-1 1-1 1 .4 1 1-.4 1-1 1z" fill="#fff"/>
              </svg>
            </div>
            <h1>企业员工助手</h1>
            <p>公司政策、规定问询，随时为您解答</p>
          </div>

          <Tabs
            activeKey={tab}
            onChange={setTab}
            centered
            className="login-tabs"
            items={[
              { key: 'login', label: '登录' },
              { key: 'register', label: '注册' },
            ]}
          />

          <div className="login-form">
            <Input
              prefix={<UserOutlined style={{color:'var(--text-muted)'}}/>}
              placeholder="用户名"
              value={username}
              onChange={e => setUsername(e.target.value)}
              onKeyDown={handleKeyDown}
              maxLength={20}
            />
            <Input.Password
              prefix={<LockOutlined style={{color:'var(--text-muted)'}}/>}
              placeholder="密码"
              value={password}
              onChange={e => setPassword(e.target.value)}
              onKeyDown={handleKeyDown}
              maxLength={50}
            />
            <Button
              type="primary"
              block
              loading={loading}
              onClick={handleSubmit}
              className="login-btn"
            >
              {tab === 'login' ? '登录' : '注册'}
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Login
