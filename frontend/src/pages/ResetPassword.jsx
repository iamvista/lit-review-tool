import { useState, useEffect } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5001'

export default function ResetPassword() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const [token, setToken] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)

  useEffect(() => {
    // 從 URL 參數獲取 token
    const tokenFromUrl = searchParams.get('token')
    if (tokenFromUrl) {
      setToken(tokenFromUrl)
    } else {
      setError('缺少重置令牌，請從郵件中點擊連結訪問')
    }
  }, [searchParams])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setSuccess(false)

    // 驗證密碼
    if (newPassword.length < 6) {
      setError('密碼長度至少需要 6 個字符')
      return
    }

    if (newPassword !== confirmPassword) {
      setError('兩次輸入的密碼不一致')
      return
    }

    setLoading(true)

    try {
      const response = await axios.post(`${API_URL}/api/auth/reset-password`, {
        token,
        new_password: newPassword
      })

      if (response.data.success) {
        setSuccess(true)
        // 3 秒後跳轉到登入頁
        setTimeout(() => {
          navigate('/login')
        }, 3000)
      }
    } catch (err) {
      setError(err.response?.data?.error || '重置失敗，請稍後再試')
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
            <h2 className="text-2xl font-semibold text-gray-800">重置密碼</h2>
            <p className="text-sm text-gray-600 mt-2">
              請輸入您的新密碼
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
                <div>
                  <p className="text-green-800 font-medium">密碼重置成功！</p>
                  <p className="text-sm text-green-700 mt-1">
                    正在跳轉到登入頁面...
                  </p>
                </div>
              </div>
            </div>
          )}

          {!success && (
            <form onSubmit={handleSubmit}>
              {/* 隱藏的 token 字段（用於調試） */}
              {token && (
                <div className="mb-4 p-2 bg-gray-50 rounded">
                  <p className="text-xs text-gray-500">令牌已載入 ✓</p>
                </div>
              )}

              <div className="mb-4">
                <label className="block text-gray-700 text-sm font-semibold mb-2">
                  新密碼
                </label>
                <input
                  type="password"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-indigo-500"
                  placeholder="至少 6 個字符"
                  required
                  disabled={!token}
                />
              </div>

              <div className="mb-6">
                <label className="block text-gray-700 text-sm font-semibold mb-2">
                  確認新密碼
                </label>
                <input
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-indigo-500"
                  placeholder="再次輸入密碼"
                  required
                  disabled={!token}
                />
              </div>

              <button
                type="submit"
                disabled={loading || !token}
                className="w-full bg-indigo-600 text-white py-2 px-4 rounded-lg hover:bg-indigo-700 transition duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? '重置中...' : '重置密碼'}
              </button>
            </form>
          )}

          <div className="mt-6 text-center">
            <Link to="/login" className="text-indigo-600 hover:text-indigo-700 text-sm font-medium">
              ← 返回登入
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}
