import { useState, useEffect } from 'react'
import api from '../services/api'

export default function GapAnalysis({ projectId, paperCount }) {
  const [analyzing, setAnalyzing] = useState(false)
  const [analyses, setAnalyses] = useState([])
  const [currentAnalysis, setCurrentAnalysis] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    loadAnalyses()
  }, [projectId])

  const loadAnalyses = async () => {
    try {
      const response = await api.get(`/api/analysis/projects/${projectId}/analyses`)
      if (response.data.success) {
        setAnalyses(response.data.analyses)
        if (response.data.analyses.length > 0) {
          setCurrentAnalysis(response.data.analyses[0])
        }
      }
    } catch (err) {
      console.error('載入分析失敗:', err)
    }
  }

  const handleAnalyze = async () => {
    if (paperCount < 3) {
      setError('至少需要 3 篇論文才能進行分析')
      return
    }

    setAnalyzing(true)
    setError('')

    try {
      const title = `AI 分析報告`
      const response = await api.post(`/api/analysis/projects/${projectId}/analyze`, {
        analysis_type: 'comprehensive',
        title
      })

      if (response.data.success) {
        setCurrentAnalysis(response.data.analysis)
        loadAnalyses()
        alert('AI 分析完成！')
      }
    } catch (err) {
      setError(err.response?.data?.error || err.response?.data?.message || '分析失敗')
    } finally {
      setAnalyzing(false)
    }
  }

  const handleDelete = async (analysisId) => {
    if (!confirm('確定要刪除此分析報告嗎？')) return

    try {
      await api.delete(`/api/analysis/analyses/${analysisId}`)
      setAnalyses(analyses.filter(a => a.id !== analysisId))
      if (currentAnalysis?.id === analysisId) {
        setCurrentAnalysis(null)
      }
    } catch (err) {
      alert('刪除失敗')
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">AI 研究缺口識別</h2>
          <p className="text-sm text-gray-600 mt-1">使用 AI 分析論文集，識別研究缺口</p>
        </div>
        <button
          onClick={handleAnalyze}
          disabled={analyzing || paperCount < 3}
          className="bg-purple-600 text-white px-6 py-3 rounded-lg hover:bg-purple-700 transition disabled:opacity-50"
        >
          {analyzing ? '分析中...' : '🤖 開始 AI 分析'}
        </button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      {paperCount < 3 && (
        <div className="bg-yellow-50 border border-yellow-200 text-yellow-800 px-4 py-3 rounded-lg">
          目前只有 {paperCount} 篇論文，建議至少 3 篇才能進行分析
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <div className="lg:col-span-1">
          <h3 className="font-semibold text-gray-900 mb-3">分析歷史</h3>
          <div className="space-y-2">
            {analyses.length === 0 ? (
              <p className="text-sm text-gray-500">尚無分析報告</p>
            ) : (
              analyses.map(analysis => (
                <div
                  key={analysis.id}
                  onClick={() => setCurrentAnalysis(analysis)}
                  className={`p-3 border rounded-lg cursor-pointer transition ${
                    currentAnalysis?.id === analysis.id
                      ? 'border-purple-600 bg-purple-50'
                      : 'border-gray-200 hover:bg-gray-50'
                  }`}
                >
                  <div className="text-sm font-medium line-clamp-2">{analysis.title}</div>
                  <div className="text-xs text-gray-500 mt-1">
                    {new Date(analysis.generated_at).toLocaleDateString('zh-TW')}
                  </div>
                  <div className="text-xs text-gray-500">{analysis.papers_analyzed} 篇論文</div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      handleDelete(analysis.id)
                    }}
                    className="text-xs text-red-600 hover:text-red-800 mt-2"
                  >
                    刪除
                  </button>
                </div>
              ))
            )}
          </div>
        </div>

        <div className="lg:col-span-3">
          {currentAnalysis ? (
            <div className="bg-white border border-gray-200 rounded-lg p-6">
              <h3 className="text-xl font-bold mb-4">{currentAnalysis.title}</h3>
              <div className="text-sm text-gray-600 mb-4">
                {new Date(currentAnalysis.generated_at).toLocaleString('zh-TW')} · {currentAnalysis.papers_analyzed} 篇論文
              </div>
              <div className="prose max-w-none whitespace-pre-wrap">
                {currentAnalysis.full_text || currentAnalysis.summary || '載入中...'}
              </div>
            </div>
          ) : (
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-12 text-center">
              <p className="text-gray-600">尚未進行 AI 分析</p>
              <p className="text-sm text-gray-500 mt-2">點擊「開始 AI 分析」按鈕來分析您的論文集</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
