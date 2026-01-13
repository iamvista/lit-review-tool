import { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { projectsService } from '../services/projects'
import { papersService } from '../services/papers'
import SmartPaperSearch from '../components/SmartPaperSearch'
import PDFUploader from '../components/papers/PDFUploader'
import api from '../services/api'

export default function ProjectDetail() {
  const { projectId } = useParams()
  const navigate = useNavigate()
  const [project, setProject] = useState(null)
  const [papers, setPapers] = useState([])
  const [loading, setLoading] = useState(true)
  const [showImportModal, setShowImportModal] = useState(false)
  const [showShareModal, setShowShareModal] = useState(false)
  const [showPDFUploader, setShowPDFUploader] = useState(false)
  const [shareUrl, setShareUrl] = useState('')

  useEffect(() => {
    loadProjectData()
  }, [projectId])

  const loadProjectData = async () => {
    try {
      const [projectData, papersData] = await Promise.all([
        projectsService.getProject(projectId),
        projectsService.getProjectPapers(projectId, 'year', 'asc')
      ])
      setProject(projectData.project)
      setPapers(papersData.papers || [])
    } catch (err) {
      console.error('載入專案失敗:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleExport = async (format) => {
    console.log('=== 匯出功能被觸發 ===')
    console.log('格式:', format)
    console.log('專案 ID:', projectId)
    console.log('專案:', project?.name)

    if (!project) {
      alert('專案資料載入中，請稍後再試')
      return
    }

    try {
      const token = localStorage.getItem('access_token')
      if (!token) {
        alert('請先登入')
        return
      }

      console.log('開始請求匯出...')
      const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:5001'
      const url = `${baseUrl}/api/projects/${projectId}/export/${format}`
      console.log('請求 URL:', url)

      // 使用原生 fetch 代替 axios，解決 blob 下載問題
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      console.log('✓ 收到響應')
      console.log('響應狀態:', response.status, response.statusText)

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      // 獲取 blob 數據
      const blob = await response.blob()
      console.log('✓ 獲取 Blob，大小:', blob.size, 'bytes')

      if (blob.size === 0) {
        throw new Error('下載的文件為空')
      }

      // 創建下載連結
      const downloadUrl = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = downloadUrl

      // 設置檔案名稱
      const extension = format === 'bibtex' ? 'bib' : 'md'
      const filename = `${project.name || 'project'}_${format}.${extension}`
      link.download = filename

      console.log('✓ 設置檔案名稱:', filename)

      // 觸發下載
      document.body.appendChild(link)
      link.click()
      console.log('✓ 已觸發下載')

      // 清理
      setTimeout(() => {
        document.body.removeChild(link)
        window.URL.revokeObjectURL(downloadUrl)
        console.log('✓ 清理完成')
      }, 100)

      console.log(`✅ 匯出成功: ${filename}`)
    } catch (err) {
      console.error('❌ 匯出失敗:', err)
      alert(`匯出失敗: ${err.message}`)
    }
  }

  const handleShare = async () => {
    try {
      const token = localStorage.getItem('access_token')
      const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:5001'
      const url = `${baseUrl}/api/projects/${projectId}/share`

      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })

      const data = await response.json()

      if (response.ok) {
        const fullShareUrl = `${window.location.origin}/share/${data.share_token}`
        setShareUrl(fullShareUrl)
        setShowShareModal(true)
      } else {
        alert(data.error || '生成分享連結失敗')
      }
    } catch (err) {
      console.error('生成分享連結失敗:', err)
      alert('生成分享連結失敗，請稍後再試')
    }
  }

  const copyShareUrl = () => {
    navigator.clipboard.writeText(shareUrl)
    alert('分享連結已複製到剪貼簿！')
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    )
  }

  if (!project) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600 mb-4">專案不存在</p>
          <Link to="/projects" className="text-indigo-600 hover:text-indigo-700">
            返回專案列表
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                onClick={() => navigate('/projects')}
                className="text-gray-600 hover:text-gray-800"
              >
                ← 返回
              </button>
              <div>
                <h1 className="text-2xl font-bold text-gray-800">{project.name}</h1>
                <p className="text-sm text-gray-600">{project.description}</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats */}
        <div className="grid md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm text-gray-600 mb-1">論文數量</div>
            <div className="text-3xl font-bold text-indigo-600">
              {papers.length} / {project.target_paper_count}
            </div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm text-gray-600 mb-1">年份範圍</div>
            <div className="text-2xl font-semibold text-gray-800">
              {papers.length > 0
                ? `${Math.min(...papers.filter(p => p.year).map(p => p.year))} - ${Math.max(...papers.filter(p => p.year).map(p => p.year))}`
                : 'N/A'}
            </div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm text-gray-600 mb-1">已閱讀</div>
            <div className="text-2xl font-semibold text-gray-800">
              {papers.filter(p => p.read_status !== 'unread').length} / {papers.length}
            </div>
          </div>
        </div>

        {/* Papers List */}
        <div className="bg-white rounded-lg shadow">
          <div className="p-6 border-b border-gray-200 flex justify-between items-center">
            <h2 className="text-xl font-semibold text-gray-800">論文列表</h2>
            <div className="flex gap-2">
              {papers.length > 0 && (
                <>
                  <button
                    onClick={() => navigate(`/projects/${projectId}/reading`)}
                    className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition"
                  >
                    📖 進入閱讀模式
                  </button>
                  <button
                    onClick={() => navigate(`/projects/${projectId}/network`)}
                    className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition"
                  >
                    🔗 網絡分析
                  </button>
                  <button
                    onClick={() => navigate(`/projects/${projectId}/ai-analysis`)}
                    className="bg-pink-600 text-white px-4 py-2 rounded-lg hover:bg-pink-700 transition"
                  >
                    🤖 AI 分析
                  </button>
                </>
              )}
              <button
                onClick={handleShare}
                className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition"
                title="分享專案"
              >
                🔗 分享
              </button>
              <button
                onClick={() => handleExport('bibtex')}
                className="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700 transition"
                title="匯出 BibTeX 格式"
              >
                📄 BibTeX
              </button>
              <button
                onClick={() => handleExport('markdown')}
                className="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700 transition"
                title="匯出 Markdown 報告"
              >
                📝 Markdown
              </button>
              <button
                onClick={() => setShowPDFUploader(true)}
                className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition"
              >
                📄 上傳 PDF
              </button>
              <button
                onClick={() => setShowImportModal(true)}
                className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition"
              >
                + 導入論文
              </button>
            </div>
          </div>

          <div className="divide-y divide-gray-200">
            {papers.length === 0 ? (
              <div className="p-12 text-center text-gray-600">
                <p className="mb-4">還沒有論文</p>
                <button
                  onClick={() => setShowImportModal(true)}
                  className="text-indigo-600 hover:text-indigo-700 font-semibold"
                >
                  導入第一篇論文
                </button>
              </div>
            ) : (
              papers.map((paper) => (
                <PaperItem key={paper.id} paper={paper} />
              ))
            )}
          </div>
        </div>

        {showImportModal && (
          <ImportPapersModal
            projectId={projectId}
            onClose={() => setShowImportModal(false)}
            onSuccess={() => {
              setShowImportModal(false)
              loadProjectData()
            }}
          />
        )}

        {showShareModal && (
          <ShareModal
            shareUrl={shareUrl}
            onClose={() => setShowShareModal(false)}
            onCopy={copyShareUrl}
          />
        )}

        {showPDFUploader && (
          <PDFUploader
            projectId={parseInt(projectId)}
            onSuccess={() => {
              setShowPDFUploader(false)
              loadProjectData()
            }}
            onCancel={() => setShowPDFUploader(false)}
          />
        )}
      </main>
    </div>
  )
}

function PaperItem({ paper }) {
  const getStatusColor = (status) => {
    switch (status) {
      case 'full_read':
        return 'bg-green-100 text-green-800'
      case 'abstract_only':
        return 'bg-yellow-100 text-yellow-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatusText = (status) => {
    switch (status) {
      case 'full_read':
        return '已完整閱讀'
      case 'abstract_only':
        return '已讀摘要'
      default:
        return '未讀'
    }
  }

  return (
    <div className="p-6 hover:bg-gray-50 transition">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            {paper.year && (
              <span className="text-sm font-semibold text-indigo-600">
                {paper.year}
              </span>
            )}
            <span className={`text-xs px-2 py-1 rounded ${getStatusColor(paper.read_status)}`}>
              {getStatusText(paper.read_status)}
            </span>
          </div>

          <h3 className="text-lg font-semibold text-gray-800 mb-2">
            {paper.title}
          </h3>

          {paper.journal && (
            <p className="text-sm text-gray-600 mb-1">
              {paper.journal}
            </p>
          )}

          {paper.abstract && (
            <p className="text-sm text-gray-600 line-clamp-2 mt-2">
              {paper.abstract}
            </p>
          )}

          {paper.tags && paper.tags.length > 0 && (
            <div className="flex flex-wrap gap-2 mt-3">
              {paper.tags.map((tag, idx) => (
                <span
                  key={idx}
                  className="text-xs bg-blue-50 text-blue-600 px-2 py-1 rounded"
                >
                  {tag}
                </span>
              ))}
            </div>
          )}
        </div>

        {paper.citation_count > 0 && (
          <div className="text-sm text-gray-500 ml-4">
            引用: {paper.citation_count}
          </div>
        )}
      </div>
    </div>
  )
}

function ImportPapersModal({ projectId, onClose, onSuccess }) {
  const [importType, setImportType] = useState('search') // 'search', 'bibtex' or 'doi'
  const [bibtexContent, setBibtexContent] = useState('')
  const [doi, setDoi] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  const handleBibtexImport = async () => {
    setError('')
    setSuccess('')
    setLoading(true)

    try {
      const result = await papersService.importBibTeX(projectId, bibtexContent)
      setSuccess(`成功導入 ${result.count} 篇論文！`)
      setTimeout(() => {
        onSuccess()
      }, 1500)
    } catch (err) {
      setError(err.response?.data?.error || '導入失敗')
    } finally {
      setLoading(false)
    }
  }

  const handleDoiImport = async () => {
    setError('')
    setSuccess('')
    setLoading(true)

    try {
      await papersService.importDOI(projectId, doi)
      setSuccess('論文導入成功！')
      setTimeout(() => {
        onSuccess()
      }, 1500)
    } catch (err) {
      setError(err.response?.data?.error || 'DOI 解析失敗')
    } finally {
      setLoading(false)
    }
  }

  const handleFileUpload = (e) => {
    const file = e.target.files[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = (event) => {
        setBibtexContent(event.target.result)
      }
      reader.readAsText(file)
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg max-w-2xl w-full p-6 max-h-[90vh] overflow-y-auto">
        <h3 className="text-xl font-semibold mb-4">導入論文</h3>

        {/* Import Type Selector */}
        <div className="flex gap-2 mb-6">
          <button
            onClick={() => setImportType('search')}
            className={`flex-1 py-2 px-4 rounded-lg border-2 transition ${
              importType === 'search'
                ? 'border-indigo-600 bg-indigo-50 text-indigo-700'
                : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            🔍 智能搜尋
          </button>
          <button
            onClick={() => setImportType('bibtex')}
            className={`flex-1 py-2 px-4 rounded-lg border-2 transition ${
              importType === 'bibtex'
                ? 'border-indigo-600 bg-indigo-50 text-indigo-700'
                : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            📄 BibTeX
          </button>
          <button
            onClick={() => setImportType('doi')}
            className={`flex-1 py-2 px-4 rounded-lg border-2 transition ${
              importType === 'doi'
                ? 'border-indigo-600 bg-indigo-50 text-indigo-700'
                : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            🔗 DOI
          </button>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        {success && (
          <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded mb-4">
            {success}
          </div>
        )}

        {importType === 'search' ? (
          <div>
            <SmartPaperSearch
              projectId={projectId}
              onPaperAdded={() => {
                onSuccess()
              }}
            />
            <div className="flex justify-end mt-4">
              <button
                onClick={onClose}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition"
              >
                關閉
              </button>
            </div>
          </div>
        ) : importType === 'bibtex' ? (
          <div>
            <div className="mb-4">
              <label className="block text-gray-700 text-sm font-semibold mb-2">
                上傳 BibTeX 文件
              </label>
              <input
                type="file"
                accept=".bib,.txt"
                onChange={handleFileUpload}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              />
            </div>

            <div className="mb-6">
              <label className="block text-gray-700 text-sm font-semibold mb-2">
                或直接貼上 BibTeX 內容
              </label>
              <textarea
                value={bibtexContent}
                onChange={(e) => setBibtexContent(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-indigo-500 font-mono text-sm"
                rows="10"
                placeholder="@article{example2020,
  title={Example Paper Title},
  author={Author, First and Author, Second},
  journal={Journal Name},
  year={2020}
}"
              />
            </div>

            <div className="flex gap-3">
              <button
                onClick={onClose}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition"
              >
                取消
              </button>
              <button
                onClick={handleBibtexImport}
                disabled={loading || !bibtexContent.trim()}
                className="flex-1 bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition disabled:opacity-50"
              >
                {loading ? '導入中...' : '導入'}
              </button>
            </div>
          </div>
        ) : (
          <div>
            <div className="mb-6">
              <label className="block text-gray-700 text-sm font-semibold mb-2">
                輸入 DOI
              </label>
              <input
                type="text"
                value={doi}
                onChange={(e) => setDoi(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-indigo-500"
                placeholder="10.1234/example.doi"
              />
              <p className="text-xs text-gray-500 mt-1">
                例如：10.1038/nature12345
              </p>
            </div>

            <div className="flex gap-3">
              <button
                onClick={onClose}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition"
              >
                取消
              </button>
              <button
                onClick={handleDoiImport}
                disabled={loading || !doi.trim()}
                className="flex-1 bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition disabled:opacity-50"
              >
                {loading ? '導入中...' : '導入'}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

function ShareModal({ shareUrl, onClose, onCopy }) {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg max-w-md w-full p-6">
        <h3 className="text-xl font-semibold mb-4">分享專案</h3>

        <p className="text-gray-600 mb-4">
          任何擁有此連結的人都可以查看您的專案和論文列表。
        </p>

        <div className="bg-gray-50 p-3 rounded-lg mb-4 border border-gray-200">
          <div className="flex items-center justify-between">
            <code className="text-sm text-gray-700 break-all flex-1 mr-3">
              {shareUrl}
            </code>
            <button
              onClick={onCopy}
              className="flex-shrink-0 bg-indigo-600 text-white px-3 py-1 rounded hover:bg-indigo-700 transition text-sm"
            >
              複製
            </button>
          </div>
        </div>

        <div className="flex items-start gap-2 mb-6 text-sm text-gray-600">
          <svg className="h-5 w-5 text-yellow-600 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span>
            分享連結將保持有效，直到您撤銷分享權限為止。
          </span>
        </div>

        <div className="flex gap-3">
          <button
            onClick={onClose}
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition"
          >
            關閉
          </button>
        </div>
      </div>
    </div>
  )
}
