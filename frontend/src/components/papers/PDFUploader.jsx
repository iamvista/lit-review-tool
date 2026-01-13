/**
 * PDF 上傳與預覽組件
 * PDF Uploader Component - 支援拖放上傳和資訊預覽
 */

import { useState, useRef } from 'react'
import api from '../../services/api'

export default function PDFUploader({ projectId, onSuccess, onCancel }) {
  const [files, setFiles] = useState([])
  const [uploading, setUploading] = useState(false)
  const [results, setResults] = useState([])
  const [currentStep, setCurrentStep] = useState('upload') // 'upload' | 'preview' | 'editing'
  const [dragActive, setDragActive] = useState(false)
  const fileInputRef = useRef(null)

  // 處理拖放
  const handleDrag = (e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    const droppedFiles = Array.from(e.dataTransfer.files).filter(file =>
      file.type === 'application/pdf'
    )

    if (droppedFiles.length > 0) {
      setFiles(droppedFiles)
      setCurrentStep('preview')
    } else {
      alert('請上傳 PDF 文件')
    }
  }

  // 處理文件選擇
  const handleFileSelect = (e) => {
    const selectedFiles = Array.from(e.target.files).filter(file =>
      file.type === 'application/pdf'
    )

    if (selectedFiles.length > 0) {
      setFiles(selectedFiles)
      setCurrentStep('preview')
    }
  }

  // 上傳並處理 PDF
  const handleUpload = async () => {
    setUploading(true)
    const newResults = []

    for (let i = 0; i < files.length; i++) {
      const file = files[i]

      try {
        const formData = new FormData()
        formData.append('file', file)
        formData.append('project_id', projectId)

        const response = await api.post('/api/papers/upload-pdf', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })

        if (response.data.success) {
          newResults.push({
            id: i,
            filename: file.name,
            status: 'success',
            ...response.data.data
          })
        } else {
          newResults.push({
            id: i,
            filename: file.name,
            status: 'error',
            error: response.data.error
          })
        }
      } catch (error) {
        newResults.push({
          id: i,
          filename: file.name,
          status: 'error',
          error: error.response?.data?.error || error.message
        })
      }
    }

    setResults(newResults)
    setUploading(false)
    setCurrentStep('editing')
  }

  // 更新單個結果
  const updateResult = (id, field, value) => {
    setResults(prev => prev.map(r =>
      r.id === id ? { ...r, metadata: { ...r.metadata, [field]: value } } : r
    ))
  }

  // 確認導入
  const handleConfirm = async () => {
    try {
      setUploading(true)

      for (const result of results) {
        if (result.status === 'success') {
          await api.post('/api/papers/confirm-pdf', {
            project_id: projectId,
            title: result.metadata.title,
            authors: result.metadata.authors || [],
            year: result.metadata.year,
            journal: result.metadata.journal || '',
            doi: result.metadata.doi || '',
            url: result.metadata.url || '',
            abstract: result.sections?.abstract || '',
            introduction: result.sections?.introduction || '',
            conclusion: result.sections?.conclusion || '',
            temp_path: result.temp_path,
            filename: result.filename
          })
        }
      }

      alert(`成功導入 ${results.filter(r => r.status === 'success').length} 篇論文！`)
      onSuccess()
    } catch (error) {
      alert('導入失敗：' + (error.response?.data?.error || error.message))
    } finally {
      setUploading(false)
    }
  }

  // 渲染上傳區域
  if (currentStep === 'upload') {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
        <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-gray-900">上傳 PDF 論文</h2>
            <button onClick={onCancel} className="text-gray-500 hover:text-gray-700">
              <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* 拖放區域 */}
          <div
            className={`border-2 border-dashed rounded-lg p-12 text-center transition-colors ${
              dragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'
            }`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            <svg
              className="mx-auto h-12 w-12 text-gray-400 mb-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
              />
            </svg>
            <p className="text-lg font-medium text-gray-900 mb-2">
              拖放 PDF 文件到這裡
            </p>
            <p className="text-sm text-gray-500 mb-4">
              或點擊下方按鈕選擇文件
            </p>
            <button
              onClick={() => fileInputRef.current?.click()}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              選擇文件
            </button>
            <input
              ref={fileInputRef}
              type="file"
              multiple
              accept=".pdf"
              onChange={handleFileSelect}
              className="hidden"
            />
            <p className="text-xs text-gray-400 mt-4">
              支援批次上傳，一次可選擇多個 PDF 文件
            </p>
          </div>
        </div>
      </div>
    )
  }

  // 渲染文件預覽和處理
  if (currentStep === 'preview') {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
        <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
          <div className="sticky top-0 bg-white border-b p-6 z-10">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold text-gray-900">
                已選擇 {files.length} 個文件
              </h2>
              <button onClick={onCancel} className="text-gray-500 hover:text-gray-700">
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>

          <div className="p-6">
            <div className="space-y-3 mb-6">
              {files.map((file, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-4 bg-gray-50 rounded-lg"
                >
                  <div className="flex items-center space-x-3">
                    <svg className="w-8 h-8 text-red-500" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clipRule="evenodd" />
                    </svg>
                    <div>
                      <p className="font-medium text-gray-900">{file.name}</p>
                      <p className="text-sm text-gray-500">
                        {(file.size / 1024 / 1024).toFixed(2)} MB
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            <div className="flex justify-end space-x-3">
              <button
                onClick={() => {
                  setFiles([])
                  setCurrentStep('upload')
                }}
                className="px-6 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                重新選擇
              </button>
              <button
                onClick={handleUpload}
                disabled={uploading}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {uploading ? '處理中...' : '開始處理'}
              </button>
            </div>
          </div>
        </div>
      </div>
    )
  }

  // 渲染提取結果編輯
  if (currentStep === 'editing') {
    const successCount = results.filter(r => r.status === 'success').length
    const errorCount = results.filter(r => r.status === 'error').length

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
        <div className="bg-white rounded-lg shadow-xl max-w-6xl w-full max-h-[90vh] overflow-hidden flex flex-col">
          <div className="p-6 border-b">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold text-gray-900">處理結果</h2>
                <p className="text-sm text-gray-600 mt-1">
                  成功 {successCount} 個，失敗 {errorCount} 個
                </p>
              </div>
              <button onClick={onCancel} className="text-gray-500 hover:text-gray-700">
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>

          <div className="flex-1 overflow-y-auto p-6">
            <div className="space-y-6">
              {results.map((result) => (
                <PaperPreviewCard
                  key={result.id}
                  result={result}
                  onUpdate={(field, value) => updateResult(result.id, field, value)}
                />
              ))}
            </div>
          </div>

          <div className="p-6 border-t bg-gray-50">
            <div className="flex justify-end space-x-3">
              <button
                onClick={onCancel}
                className="px-6 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-white"
              >
                取消
              </button>
              <button
                onClick={handleConfirm}
                disabled={uploading || successCount === 0}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {uploading ? '導入中...' : `確認導入 ${successCount} 篇論文`}
              </button>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return null
}

// 論文預覽卡片組件
function PaperPreviewCard({ result, onUpdate }) {
  const [expanded, setExpanded] = useState(false)
  const [editing, setEditing] = useState(false)

  if (result.status === 'error') {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <div className="flex items-start">
          <svg className="w-6 h-6 text-red-500 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div>
            <p className="font-medium text-red-900">{result.filename}</p>
            <p className="text-sm text-red-700 mt-1">{result.error}</p>
          </div>
        </div>
      </div>
    )
  }

  const metadata = result.metadata || {}
  const sections = result.sections || {}

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <div className="flex items-center space-x-2 mb-2">
            <svg className="w-5 h-5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
            <span className="text-xs font-medium text-green-700 bg-green-100 px-2 py-1 rounded">
              {result.extraction_method === 'doi' ? '透過 DOI 識別' : '文字解析'}
            </span>
          </div>

          {editing ? (
            <input
              type="text"
              value={metadata.title}
              onChange={(e) => onUpdate('title', e.target.value)}
              className="text-xl font-semibold text-gray-900 w-full border border-gray-300 rounded px-2 py-1 mb-2"
            />
          ) : (
            <h3 className="text-xl font-semibold text-gray-900 mb-2">{metadata.title || '未識別標題'}</h3>
          )}

          <div className="grid grid-cols-2 gap-3 text-sm">
            <div>
              <span className="text-gray-500">作者：</span>
              <span className="text-gray-900">
                {metadata.authors?.slice(0, 3).join(', ') || '未識別'}
                {metadata.authors?.length > 3 && ` 等 ${metadata.authors.length} 人`}
              </span>
            </div>
            <div>
              <span className="text-gray-500">年份：</span>
              <span className="text-gray-900">{metadata.year || '未識別'}</span>
            </div>
            <div className="col-span-2">
              <span className="text-gray-500">期刊：</span>
              <span className="text-gray-900">{metadata.journal || '未識別'}</span>
            </div>
            {metadata.doi && (
              <div className="col-span-2">
                <span className="text-gray-500">DOI：</span>
                <span className="text-gray-900 text-xs">{metadata.doi}</span>
              </div>
            )}
          </div>
        </div>

        <button
          onClick={() => setEditing(!editing)}
          className="ml-4 px-3 py-1 text-sm text-blue-600 hover:text-blue-700 border border-blue-300 rounded hover:bg-blue-50"
        >
          {editing ? '完成' : '編輯'}
        </button>
      </div>

      {/* 摘要預覽 */}
      {sections.abstract && (
        <div className="mt-4 pt-4 border-t">
          <button
            onClick={() => setExpanded(!expanded)}
            className="flex items-center text-sm font-medium text-gray-700 hover:text-gray-900"
          >
            <svg
              className={`w-4 h-4 mr-1 transition-transform ${expanded ? 'rotate-90' : ''}`}
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
            </svg>
            {expanded ? '收合' : '查看'}摘要
          </button>
          {expanded && (
            <p className="mt-2 text-sm text-gray-600 leading-relaxed">{sections.abstract}</p>
          )}
        </div>
      )}
    </div>
  )
}
