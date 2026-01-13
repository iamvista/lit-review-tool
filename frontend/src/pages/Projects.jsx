import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { projectsService } from '../services/projects'
import { authService } from '../services/auth'

export default function Projects() {
  const navigate = useNavigate()
  const [projects, setProjects] = useState([])
  const [loading, setLoading] = useState(true)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [user, setUser] = useState(null)

  useEffect(() => {
    const userData = authService.getUser()
    setUser(userData)
    loadProjects()
  }, [])

  const loadProjects = async () => {
    try {
      const data = await projectsService.getProjects()
      setProjects(data.projects || [])
    } catch (err) {
      console.error('載入專案失敗:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = () => {
    authService.logout()
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold text-gray-800">LitReview Tool</h1>
              <p className="text-sm text-gray-600">歡迎回來，{user?.full_name || user?.username}</p>
            </div>
            <div className="flex items-center gap-3">
              <button
                onClick={() => navigate('/settings')}
                className="text-gray-600 hover:text-gray-800 flex items-center gap-1"
              >
                ⚙️ 設定
              </button>
              <button
                onClick={handleLogout}
                className="text-gray-600 hover:text-gray-800"
              >
                登出
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-semibold text-gray-800">我的專案</h2>
          <button
            onClick={() => setShowCreateModal(true)}
            className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition"
          >
            + 新建專案
          </button>
        </div>

        {loading ? (
          <div className="flex justify-center items-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
          </div>
        ) : projects.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-12 text-center">
            <p className="text-gray-600 mb-4">還沒有專案</p>
            <button
              onClick={() => setShowCreateModal(true)}
              className="bg-indigo-600 text-white px-6 py-2 rounded-lg hover:bg-indigo-700 transition"
            >
              創建第一個專案
            </button>
          </div>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {projects.map((project) => (
              <ProjectCard key={project.id} project={project} />
            ))}
          </div>
        )}

        {showCreateModal && (
          <CreateProjectModal
            onClose={() => setShowCreateModal(false)}
            onSuccess={() => {
              setShowCreateModal(false)
              loadProjects()
            }}
          />
        )}
      </main>
    </div>
  )
}

function ProjectCard({ project }) {
  const navigate = useNavigate()

  return (
    <div
      onClick={() => navigate(`/projects/${project.id}`)}
      className="bg-white rounded-lg shadow hover:shadow-lg transition cursor-pointer p-6"
    >
      <h3 className="text-lg font-semibold text-gray-800 mb-2">{project.name}</h3>
      <p className="text-gray-600 text-sm mb-4 line-clamp-2">
        {project.description || '暫無描述'}
      </p>

      <div className="flex items-center justify-between text-sm text-gray-500">
        <span>{project.paper_count || 0} 篇論文</span>
        <span className="text-indigo-600">{project.domain || '未分類'}</span>
      </div>

      <div className="mt-4 pt-4 border-t border-gray-200">
        <div className="text-xs text-gray-500">
          最後更新：{new Date(project.updated_at).toLocaleDateString('zh-TW')}
        </div>
      </div>
    </div>
  )
}

function CreateProjectModal({ onClose, onSuccess }) {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    domain: '',
    target_paper_count: 30
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      await projectsService.createProject(formData)
      onSuccess()
    } catch (err) {
      setError(err.response?.data?.error || '創建失敗')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg max-w-md w-full p-6">
        <h3 className="text-xl font-semibold mb-4">新建專案</h3>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-semibold mb-2">
              專案名稱 *
            </label>
            <input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-indigo-500"
              placeholder="例如：深度學習在醫學影像的應用"
              required
            />
          </div>

          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-semibold mb-2">
              描述
            </label>
            <textarea
              name="description"
              value={formData.description}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-indigo-500"
              rows="3"
              placeholder="簡要描述研究主題..."
            />
          </div>

          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-semibold mb-2">
              研究領域
            </label>
            <input
              type="text"
              name="domain"
              value={formData.domain}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-indigo-500"
              placeholder="例如：醫學影像、自然語言處理"
            />
          </div>

          <div className="mb-6">
            <label className="block text-gray-700 text-sm font-semibold mb-2">
              目標論文數量
            </label>
            <input
              type="number"
              name="target_paper_count"
              value={formData.target_paper_count}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-indigo-500"
              min="5"
              max="100"
            />
            <p className="text-xs text-gray-500 mt-1">建議 20-50 篇高品質論文，最多 100 篇</p>
          </div>

          <div className="flex gap-3">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition"
            >
              取消
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition disabled:opacity-50"
            >
              {loading ? '創建中...' : '創建'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
