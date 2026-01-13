/**
 * 智能論文搜尋組件
 * Smart Paper Search - 統一的論文搜尋和導入介面
 */

import { useState } from 'react'
import api from '../services/api'

export default function SmartPaperSearch({ projectId, onPaperAdded }) {
  const [searchType, setSearchType] = useState('smart') // smart, google-scholar, arxiv
  const [searchInput, setSearchInput] = useState('')
  const [searching, setSearching] = useState(false)
  const [results, setResults] = useState([])
  const [selectedPapers, setSelectedPapers] = useState(new Set())
  const [error, setError] = useState('')

  const handleSmartSearch = async () => {
    if (!searchInput.trim()) {
      setError('請輸入搜尋內容')
      return
    }

    setSearching(true)
    setError('')
    setResults([])

    try {
      const response = await api.post('/api/search/smart', {
        input: searchInput
      })

      if (response.data.success) {
        // 智能搜尋只返回一個結果
        setResults([response.data.paper])
      }
    } catch (err) {
      setError(err.response?.data?.error || '搜尋失敗')
    } finally {
      setSearching(false)
    }
  }

  const handleGoogleScholarSearch = async () => {
    if (!searchInput.trim()) {
      setError('請輸入搜尋關鍵詞')
      return
    }

    setSearching(true)
    setError('')
    setResults([])

    try {
      const response = await api.get('/api/search/google-scholar', {
        params: {
          q: searchInput,
          limit: 10
        }
      })

      if (response.data.success) {
        setResults(response.data.results)
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Google Scholar 搜尋失敗')
    } finally {
      setSearching(false)
    }
  }

  const handleArXivSearch = async () => {
    if (!searchInput.trim()) {
      setError('請輸入搜尋關鍵詞或 arXiv ID')
      return
    }

    setSearching(true)
    setError('')
    setResults([])

    try {
      const response = await api.get('/api/search/arxiv', {
        params: {
          q: searchInput,
          limit: 10
        }
      })

      if (response.data.success) {
        setResults(response.data.results)
      }
    } catch (err) {
      setError(err.response?.data?.error || 'arXiv 搜尋失敗')
    } finally {
      setSearching(false)
    }
  }

  const handleSearch = () => {
    setSelectedPapers(new Set())

    if (searchType === 'smart') {
      handleSmartSearch()
    } else if (searchType === 'google-scholar') {
      handleGoogleScholarSearch()
    } else if (searchType === 'arxiv') {
      handleArXivSearch()
    }
  }

  const togglePaperSelection = (index) => {
    const newSelected = new Set(selectedPapers)
    if (newSelected.has(index)) {
      newSelected.delete(index)
    } else {
      newSelected.add(index)
    }
    setSelectedPapers(newSelected)
  }

  const handleAddSelected = async () => {
    if (selectedPapers.size === 0) {
      setError('請選擇要添加的論文')
      return
    }

    const papersToAdd = Array.from(selectedPapers).map(idx => results[idx])

    try {
      setSearching(true)

      // 逐個添加論文
      for (const paper of papersToAdd) {
        await api.post(`/api/papers/projects/${projectId}/from-metadata`, {
          title: paper.title,
          authors: paper.authors || [],
          year: paper.year,
          journal: paper.journal,
          doi: paper.doi,
          url: paper.url,
          abstract: paper.abstract,
          bibtex: paper.bibtex || ''
        })
      }

      // 成功後通知父組件
      if (onPaperAdded) {
        onPaperAdded()
      }

      // 清空選擇和結果
      setResults([])
      setSelectedPapers(new Set())
      setSearchInput('')
      alert(`成功添加 ${papersToAdd.length} 篇論文！`)

    } catch (err) {
      setError(err.response?.data?.error || '添加論文失敗')
    } finally {
      setSearching(false)
    }
  }

  return (
    <div className="space-y-4">
      {/* 搜尋類型選擇 */}
      <div className="flex gap-2">
        <button
          onClick={() => setSearchType('smart')}
          className={`flex-1 py-2 px-4 rounded-lg border-2 transition ${
            searchType === 'smart'
              ? 'border-indigo-600 bg-indigo-50 text-indigo-700'
              : 'border-gray-200 hover:border-gray-300'
          }`}
        >
          🎯 智能搜尋
        </button>
        <button
          onClick={() => setSearchType('google-scholar')}
          className={`flex-1 py-2 px-4 rounded-lg border-2 transition ${
            searchType === 'google-scholar'
              ? 'border-indigo-600 bg-indigo-50 text-indigo-700'
              : 'border-gray-200 hover:border-gray-300'
          }`}
        >
          🔍 Google Scholar
        </button>
        <button
          onClick={() => setSearchType('arxiv')}
          className={`flex-1 py-2 px-4 rounded-lg border-2 transition ${
            searchType === 'arxiv'
              ? 'border-indigo-600 bg-indigo-50 text-indigo-700'
              : 'border-gray-200 hover:border-gray-300'
          }`}
        >
          📄 arXiv
        </button>
      </div>

      {/* 搜尋提示 */}
      <div className="text-sm text-gray-600 bg-blue-50 p-3 rounded-lg">
        {searchType === 'smart' && (
          <div>
            <strong>智能搜尋支援：</strong>
            <ul className="mt-1 list-disc list-inside">
              <li>論文標題（如：Deep Learning for Computer Vision）</li>
              <li>DOI（如：10.1038/nature12345）</li>
              <li>URL（支援 arXiv、PubMed、IEEE、ACM 等）</li>
              <li>arXiv ID（如：2012.12345）</li>
            </ul>
          </div>
        )}
        {searchType === 'google-scholar' && (
          <div>
            <strong>Google Scholar 搜尋：</strong>輸入關鍵詞搜尋學術論文（最多顯示 10 筆）
          </div>
        )}
        {searchType === 'arxiv' && (
          <div>
            <strong>arXiv 搜尋：</strong>輸入關鍵詞或 arXiv ID（如：2012.12345）
          </div>
        )}
      </div>

      {/* 搜尋輸入 */}
      <div className="flex gap-2">
        <input
          type="text"
          value={searchInput}
          onChange={(e) => setSearchInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
          placeholder={
            searchType === 'smart'
              ? '輸入標題、DOI、URL 或 arXiv ID...'
              : '輸入搜尋關鍵詞...'
          }
          className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-indigo-500"
          disabled={searching}
        />
        <button
          onClick={handleSearch}
          disabled={searching || !searchInput.trim()}
          className="bg-indigo-600 text-white px-6 py-2 rounded-lg hover:bg-indigo-700 transition disabled:opacity-50"
        >
          {searching ? '搜尋中...' : '搜尋'}
        </button>
      </div>

      {/* 錯誤提示 */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      {/* 搜尋結果 */}
      {results.length > 0 && (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold text-gray-900">
              搜尋結果（{results.length} 筆）
            </h3>
            {selectedPapers.size > 0 && (
              <button
                onClick={handleAddSelected}
                disabled={searching}
                className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition disabled:opacity-50"
              >
                添加選中的論文 ({selectedPapers.size})
              </button>
            )}
          </div>

          <div className="max-h-96 overflow-y-auto space-y-2">
            {results.map((paper, index) => (
              <PaperResultCard
                key={index}
                paper={paper}
                selected={selectedPapers.has(index)}
                onToggle={() => togglePaperSelection(index)}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

function PaperResultCard({ paper, selected, onToggle }) {
  return (
    <div
      className={`p-4 border-2 rounded-lg cursor-pointer transition ${
        selected
          ? 'border-indigo-600 bg-indigo-50'
          : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
      }`}
      onClick={onToggle}
    >
      <div className="flex items-start gap-3">
        <input
          type="checkbox"
          checked={selected}
          onChange={onToggle}
          className="mt-1"
        />
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            {paper.year && (
              <span className="text-sm font-semibold text-indigo-600">
                {paper.year}
              </span>
            )}
            {paper.source && (
              <span className="text-xs bg-gray-200 text-gray-700 px-2 py-0.5 rounded">
                {paper.source}
              </span>
            )}
            {paper.citation_count > 0 && (
              <span className="text-xs text-gray-500">
                引用: {paper.citation_count}
              </span>
            )}
          </div>

          <h4 className="font-semibold text-gray-900 mb-1">
            {paper.title}
          </h4>

          {paper.authors && paper.authors.length > 0 && (
            <p className="text-sm text-gray-600 mb-1">
              作者: {paper.authors.slice(0, 3).join(', ')}
              {paper.authors.length > 3 && ` 等 ${paper.authors.length} 人`}
            </p>
          )}

          {paper.journal && (
            <p className="text-sm text-gray-600 mb-1">
              期刊: {paper.journal}
            </p>
          )}

          {paper.abstract && (
            <p className="text-sm text-gray-600 line-clamp-2 mt-2">
              {paper.abstract}
            </p>
          )}

          {paper.doi && (
            <p className="text-xs text-gray-500 mt-2">
              DOI: {paper.doi}
            </p>
          )}
        </div>
      </div>
    </div>
  )
}
