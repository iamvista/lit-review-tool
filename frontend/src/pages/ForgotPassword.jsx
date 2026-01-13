import { useState } from 'react'
import { Link } from 'react-router-dom'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5001'

export default function ForgotPassword() {
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)
  const [resetUrl, setResetUrl] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setSuccess(false)
    setLoading(true)

    try {
      const response = await axios.post(`${API_URL}/api/auth/forgot-password`, {
        email: email.trim()
      })

      if (response.data.success) {
        setSuccess(true)
        // 在開發環境顯示重置連結
        if (response.data.reset_url) {
          setResetUrl(response.data.reset_url)
        }
      }
    } catch (err) {
      setError(err.response?.data?.error || '請求失敗，請稍後再試')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center px-4">
      <div className="max-w-md w-full">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">LitReview Tool</h1>
          <p className="text-gray-600">博碩士生文獻管理工具</p>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-8">
          <div className="mb-6">
            <h2 className="text-2xl font-semibold text-gray-800">忘記密碼</h2>
            <p className="text-sm text-gray-600 mt-2">
              輸入您的註冊郵箱，我們將發送重置密碼的連結給您
            </p>
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
              {error}
            </div>
          )}

          {success && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-4">
              <div className="flex items-start gap-3">
                <svg className="w-5 h-5 text-green-600 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <div className="flex-1">
                  <p className="text-green-800 font-medium mb-1">重置連結已生成！</p>
                  <p className="text-sm text-green-700 mb-3">
                    重置連結有效期為 1 小時。
                  </p>

                  {resetUrl && (
                    <div className="bg-white border border-green-300 rounded p-3">
                      <p className="text-xs text-gray-600 mb-2">開發環境重置連結：</p>
                      <div className="flex items-center gap-2">
                        <input
                          type="text"
                          value={resetUrl}
                          readOnly
                          className="flex-1 text-xs px-2 py-1 bg-gray-50 border border-gray-300 rounded font-mono"
                        />
                        <button
                          onClick={() => {
                            navigator.clipboard.writeText(resetUrl)
                            alert('已複製到剪貼簿')
                          }}
                          className="px-3 py-1 bg-green-600 text-white text-xs rounded hover:bg-green-700 transition"
                        >
                          複製
                        </button>
                      </div>
                      <a
                        href={resetUrl}
                        className="inline-block mt-2 text-sm text-green-700 hover:text-green-800 font-medium"
                      >
                        → 直接前往重置頁面
                      </a>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {!success && (
            <form onSubmit={handleSubmit}>
              <div className="mb-6">
                <label className="block text-gray-700 text-sm font-semibold mb-2">
                  電子郵件
                </label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-indigo-500"
                  placeholder="your@email.com"
                  required
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-indigo-600 text-white py-2 px-4 rounded-lg hover:bg-indigo-700 transition duration-200 disabled:opacity-50"
              >
                {loading ? '發送中...' : '發送重置連結'}
              </button>
            </form>
          )}

          <div className="mt-6 text-center space-y-2">
            <Link to="/login" className="block text-indigo-600 hover:text-indigo-700 text-sm font-medium">
              ← 返回登入
            </Link>
            <p className="text-gray-600 text-sm">
              還沒有帳戶？{' '}
              <Link to="/register" className="text-indigo-600 hover:text-indigo-700 font-semibold">
                立即註冊
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
