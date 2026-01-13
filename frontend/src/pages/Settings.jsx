/**
 * 設定頁面
 * Settings Page - User preferences and API keys management
 */

import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../services/api'

export default function Settings() {
  const navigate = useNavigate()

  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)

  // API Key 管理
  const [anthropicApiKey, setAnthropicApiKey] = useState('')
  const [showApiKey, setShowApiKey] = useState(false)
  const [hasApiKey, setHasApiKey] = useState(false)
  const [apiKeyMessage, setApiKeyMessage] = useState('')

  // 個人資料
  const [fullName, setFullName] = useState('')
  const [institution, setInstitution] = useState('')
  const [fieldOfStudy, setFieldOfStudy] = useState('')

  useEffect(() => {
    loadSettings()
  }, [])

  const loadSettings = async () => {
    try {
      setLoading(true)

      // 載入用戶資料
      const profileResponse = await api.get('/api/settings/profile')
      if (profileResponse.data.success) {
        const userData = profileResponse.data.user
        setUser(userData)
        setFullName(userData.full_name || '')
        setInstitution(userData.institution || '')
        setFieldOfStudy(userData.field_of_study || '')
        setHasApiKey(userData.has_anthropic_api_key || false)
      }

    } catch (error) {
      console.error('載入設定失敗:', error)
      alert('載入設定失敗')
    } finally {
      setLoading(false)
    }
  }

  const handleSaveProfile = async () => {
    try {
      setSaving(true)

      const response = await api.put('/api/settings/profile', {
        full_name: fullName,
        institution: institution,
        field_of_study: fieldOfStudy
      })

      if (response.data.success) {
        alert('個人資料更新成功！')
        setUser(response.data.user)
      }

    } catch (error) {
      console.error('更新個人資料失敗:', error)
      alert('更新失敗：' + (error.response?.data?.error || error.message))
    } finally {
      setSaving(false)
    }
  }

  const handleSaveApiKey = async () => {
    if (!anthropicApiKey.trim()) {
      setApiKeyMessage('請輸入 API Key')
      return
    }

    if (!anthropicApiKey.startsWith('sk-ant-')) {
      setApiKeyMessage('API Key 格式不正確，應以 sk-ant- 開頭')
      return
    }

    try {
      setSaving(true)
      setApiKeyMessage('')

      const response = await api.post('/api/settings/api-keys/anthropic', {
        api_key: anthropicApiKey
      })

      if (response.data.success) {
        setApiKeyMessage('✅ API Key 設定成功！')
        setHasApiKey(true)
        setAnthropicApiKey('')
        setShowApiKey(false)

        setTimeout(() => {
          setApiKeyMessage('')
        }, 3000)
      }

    } catch (error) {
      console.error('設定 API Key 失敗:', error)
      setApiKeyMessage('❌ ' + (error.response?.data?.error || error.message))
    } finally {
      setSaving(false)
    }
  }

  const handleDeleteApiKey = async () => {
    if (!confirm('確定要刪除 Anthropic API Key 嗎？刪除後將無法使用 AI 分析功能。')) {
      return
    }

    try {
      setSaving(true)

      const response = await api.delete('/api/settings/api-keys/anthropic')

      if (response.data.success) {
        setApiKeyMessage('✅ API Key 已刪除')
        setHasApiKey(false)
        setAnthropicApiKey('')

        setTimeout(() => {
          setApiKeyMessage('')
        }, 3000)
      }

    } catch (error) {
      console.error('刪除 API Key 失敗:', error)
      setApiKeyMessage('❌ ' + (error.response?.data?.error || error.message))
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                onClick={() => navigate('/projects')}
                className="text-gray-600 hover:text-gray-800"
              >
                ← 返回
              </button>
              <h1 className="text-2xl font-bold text-gray-800">設定</h1>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-6">

          {/* API Keys 設定 */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">🤖 AI API Keys</h2>

            <div className="space-y-4">
              {/* Anthropic API Key */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="block text-sm font-medium text-gray-700">
                    Anthropic Claude API Key
                  </label>
                  {hasApiKey && (
                    <span className="text-sm text-green-600">✓ 已設定</span>
                  )}
                </div>

                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-3">
                  <p className="text-sm text-blue-800 mb-2">
                    <strong>BYOK (Bring Your Own Key)</strong> - 每位用戶使用自己的 API Key，費用由您承擔
                  </p>
                  <ul className="text-xs text-blue-700 space-y-1">
                    <li>• 單次分析約 $0.02-0.05 USD（新台幣 ~0.6-1.5元）</li>
                    <li>• 使用模型：Claude 3 Haiku（快速且經濟）</li>
                    <li>• 如何取得：前往 <a href="https://console.anthropic.com/" target="_blank" rel="noopener noreferrer" className="underline">console.anthropic.com</a></li>
                    <li>• 最低儲值：$5 USD（約可進行 100-250 次完整分析）</li>
                  </ul>
                </div>

                <div className="flex gap-2">
                  <input
                    type={showApiKey ? 'text' : 'password'}
                    value={anthropicApiKey}
                    onChange={(e) => setAnthropicApiKey(e.target.value)}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-indigo-500"
                    placeholder="sk-ant-api03-..."
                  />
                  <button
                    onClick={() => setShowApiKey(!showApiKey)}
                    className="px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                  >
                    {showApiKey ? '🙈' : '👁️'}
                  </button>
                  <button
                    onClick={handleSaveApiKey}
                    disabled={saving}
                    className="bg-indigo-600 text-white px-6 py-2 rounded-lg hover:bg-indigo-700 disabled:opacity-50"
                  >
                    {saving ? '儲存中...' : '儲存'}
                  </button>
                </div>

                {hasApiKey && (
                  <button
                    onClick={handleDeleteApiKey}
                    disabled={saving}
                    className="mt-2 text-sm text-red-600 hover:text-red-800 disabled:opacity-50"
                  >
                    刪除 API Key
                  </button>
                )}

                {apiKeyMessage && (
                  <div className={`mt-3 p-3 rounded-lg text-sm ${
                    apiKeyMessage.includes('✅')
                      ? 'bg-green-50 text-green-700 border border-green-200'
                      : 'bg-red-50 text-red-700 border border-red-200'
                  }`}>
                    {apiKeyMessage}
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* 個人資料 */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">👤 個人資料</h2>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  使用者名稱
                </label>
                <input
                  type="text"
                  value={user?.username || ''}
                  disabled
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-50"
                />
                <p className="text-xs text-gray-500 mt-1">使用者名稱無法修改</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Email
                </label>
                <input
                  type="email"
                  value={user?.email || ''}
                  disabled
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-50"
                />
                <p className="text-xs text-gray-500 mt-1">Email 無法修改</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  全名
                </label>
                <input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-indigo-500"
                  placeholder="請輸入您的全名"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  機構/學校
                </label>
                <input
                  type="text"
                  value={institution}
                  onChange={(e) => setInstitution(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-indigo-500"
                  placeholder="例如：台灣大學"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  研究領域
                </label>
                <input
                  type="text"
                  value={fieldOfStudy}
                  onChange={(e) => setFieldOfStudy(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-indigo-500"
                  placeholder="例如：計算機科學、生物醫學"
                />
              </div>

              <button
                onClick={handleSaveProfile}
                disabled={saving}
                className="w-full bg-indigo-600 text-white px-6 py-3 rounded-lg hover:bg-indigo-700 disabled:opacity-50"
              >
                {saving ? '儲存中...' : '儲存個人資料'}
              </button>
            </div>
          </div>

          {/* 帳戶資訊 */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">📊 帳戶資訊</h2>

            <div className="space-y-2 text-sm text-gray-600">
              <div className="flex justify-between">
                <span>註冊時間：</span>
                <span>{user?.created_at ? new Date(user.created_at).toLocaleDateString('zh-TW') : 'N/A'}</span>
              </div>
              <div className="flex justify-between">
                <span>帳戶狀態：</span>
                <span className="text-green-600">● 正常</span>
              </div>
            </div>
          </div>

        </div>
      </main>
    </div>
  )
}
