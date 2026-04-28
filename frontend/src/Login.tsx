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
    <div style={{
      display: 'flex', justifyContent: 'center', alignItems: 'center',
      height: '100vh', background: '#f0f2f5'
    }}>
      <div style={{
        width: 360, padding: 32, background: '#fff',
        borderRadius: 8, boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
      }}>
        <h2 style={{ textAlign: 'center', marginBottom: 24 }}>企业员工助手</h2>
        <Tabs
          activeKey={tab}
          onChange={setTab}
          centered
          items={[
            { key: 'login', label: '登录' },
            { key: 'register', label: '注册' },
          ]}
        />
        <Input
          prefix={<UserOutlined />}
          placeholder="用户名"
          value={username}
          onChange={e => setUsername(e.target.value)}
          onKeyDown={handleKeyDown}
          style={{ marginBottom: 12 }}
          maxLength={20}
        />
        <Input.Password
          prefix={<LockOutlined />}
          placeholder="密码"
          value={password}
          onChange={e => setPassword(e.target.value)}
          onKeyDown={handleKeyDown}
          style={{ marginBottom: 24 }}
          maxLength={50}
        />
        <Button
          type="primary"
          block
          loading={loading}
          onClick={handleSubmit}
        >
          {tab === 'login' ? '登录' : '注册'}
        </Button>
      </div>
    </div>
  )
}

export default Login
