import { useState, useEffect, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { projectsService } from '../services/projects'
import { papersService } from '../services/papers'

export default function ReadingView() {
  const { projectId } = useParams()
  const navigate = useNavigate()

  const [project, setProject] = useState(null)
  const [papers, setPapers] = useState([])
  const [currentPaperIndex, setCurrentPaperIndex] = useState(0)
  const [currentTab, setCurrentTab] = useState('abstract') // abstract, introduction, conclusion
  const [loading, setLoading] = useState(true)
  const [notes, setNotes] = useState('')
  const [tags, setTags] = useState([])
  const [isSaving, setIsSaving] = useState(false)

  // 載入数据
  useEffect(() => {
    loadData()
  }, [projectId])

  const loadData = async () => {
    try {
      const [projectData, papersData] = await Promise.all([
        projectsService.getProject(projectId),
        projectsService.getProjectPapers(projectId, 'year', 'asc')
      ])

      setProject(projectData.project)
      setPapers(papersData.papers || [])

      // 如果有論文，載入第一篇的筆記和標籤
      if (papersData.papers && papersData.papers.length > 0) {
        const firstPaper = papersData.papers[0]
        setNotes(firstPaper.notes || '')
        setTags(firstPaper.tags ? firstPaper.tags.split(',').filter(t => t) : [])
      }
    } catch (err) {
      console.error('載入失敗:', err)
    } finally {
      setLoading(false)
    }
  }

  // 當前論文
  const currentPaper = papers[currentPaperIndex]

  // 切換論文
  const goToPaper = useCallback((index) => {
    if (index >= 0 && index < papers.length) {
      setCurrentPaperIndex(index)
      const paper = papers[index]
      setNotes(paper.notes || '')
      setTags(paper.tags ? paper.tags.split(',').filter(t => t) : [])
      setCurrentTab('abstract') // 切換論文时默认显示摘要
    }
  }, [papers])

  // 键盘导航
  useEffect(() => {
    const handleKeyPress = (e) => {
      // 如果在輸入框中，不响应快捷鍵
      if (e.target.tagName === 'TEXTAREA' || e.target.tagName === 'INPUT') {
        return
      }

      switch (e.key) {
        case 'ArrowUp':
        case 'k':
          e.preventDefault()
          goToPaper(currentPaperIndex - 1)
          break
        case 'ArrowDown':
        case 'j':
          e.preventDefault()
          goToPaper(currentPaperIndex + 1)
          break
        case '1':
          setCurrentTab('abstract')
          break
        case '2':
          setCurrentTab('introduction')
          break
        case '3':
          setCurrentTab('conclusion')
          break
        default:
          break
      }
    }

    window.addEventListener('keydown', handleKeyPress)
    return () => window.removeEventListener('keydown', handleKeyPress)
  }, [currentPaperIndex, goToPaper])

  // 儲存筆記
  const handleSaveNotes = async () => {
    if (!currentPaper) return

    setIsSaving(true)
    try {
      await papersService.updateNotes(currentPaper.id, notes)
      // 更新本地狀態
      const updatedPapers = [...papers]
      updatedPapers[currentPaperIndex].notes = notes
      setPapers(updatedPapers)
    } catch (err) {
      console.error('儲存筆記失敗:', err)
      alert('儲存失敗')
    } finally {
      setIsSaving(false)
    }
  }

  // 更新閱讀狀態
  const handleUpdateReadStatus = async (status) => {
    if (!currentPaper) return

    try {
      await papersService.updateReadStatus(currentPaper.id, status)
      // 更新本地狀態
      const updatedPapers = [...papers]
      updatedPapers[currentPaperIndex].read_status = status
      setPapers(updatedPapers)
    } catch (err) {
      console.error('更新閱讀狀態失敗:', err)
    }
  }

  // 添加標籤
  const handleAddTag = async (tag) => {
    if (!currentPaper || !tag.trim()) return

    const newTags = [...tags, tag.trim()]
    try {
      await papersService.updateTags(currentPaper.id, newTags)
      setTags(newTags)

      // 更新本地狀態
      const updatedPapers = [...papers]
      updatedPapers[currentPaperIndex].tags = newTags.join(',')
      setPapers(updatedPapers)
    } catch (err) {
      console.error('添加標籤失敗:', err)
    }
  }

  // 移除標籤
  const handleRemoveTag = async (tagToRemove) => {
    if (!currentPaper) return

    const newTags = tags.filter(t => t !== tagToRemove)
    try {
      await papersService.updateTags(currentPaper.id, newTags)
      setTags(newTags)

      // 更新本地狀態
      const updatedPapers = [...papers]
      updatedPapers[currentPaperIndex].tags = newTags.join(',')
      setPapers(updatedPapers)
    } catch (err) {
      console.error('移除標籤失敗:', err)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    )
  }

  if (!project || papers.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600 mb-4">暫無論文可供閱讀</p>
          <button
            onClick={() => navigate(`/projects/${projectId}`)}
            className="text-indigo-600 hover:text-indigo-700"
          >
            返回專案
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate(`/projects/${projectId}`)}
              className="text-gray-600 hover:text-gray-800"
            >
              ← 返回
            </button>
            <div>
              <h1 className="text-lg font-semibold text-gray-800">{project.name}</h1>
              <p className="text-xs text-gray-500">
                橫向串讀模式 ({currentPaperIndex + 1} / {papers.length})
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2 text-xs text-gray-500">
            <span>快捷鍵：↑↓ 切換論文</span>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left: Timeline Navigation */}
        <aside className="w-80 bg-white border-r border-gray-200 overflow-y-auto">
          <div className="p-4">
            <h2 className="text-sm font-semibold text-gray-700 mb-3">論文時間軸</h2>
            <div className="space-y-2">
              {papers.map((paper, index) => (
                <PaperTimelineItem
                  key={paper.id}
                  paper={paper}
                  isActive={index === currentPaperIndex}
                  onClick={() => goToPaper(index)}
                />
              ))}
            </div>
          </div>
        </aside>

        {/* Right: Reading View */}
        <main className="flex-1 overflow-y-auto">
          {currentPaper && (
            <div className="max-w-4xl mx-auto p-8">
              {/* Paper Header */}
              <div className="mb-6">
                <div className="flex items-center gap-3 mb-2">
                  <span className="text-indigo-600 font-semibold">{currentPaper.year}</span>
                  <ReadStatusBadge
                    status={currentPaper.read_status}
                    onChange={handleUpdateReadStatus}
                  />
                </div>
                <h2 className="text-2xl font-bold text-gray-800 mb-2">
                  {currentPaper.title}
                </h2>
                <p className="text-gray-600">{currentPaper.journal}</p>

                {/* Tags */}
                <div className="mt-3">
                  <TagManager
                    tags={tags}
                    onAddTag={handleAddTag}
                    onRemoveTag={handleRemoveTag}
                  />
                </div>
              </div>

              {/* Content Tabs */}
              <div className="bg-white rounded-lg shadow-lg border border-gray-200 overflow-hidden">
                <div className="border-b border-gray-200 bg-gray-50">
                  <nav className="flex -mb-px">
                    <TabButton
                      active={currentTab === 'abstract'}
                      onClick={() => setCurrentTab('abstract')}
                      label="摘要"
                      hasContent={!!currentPaper.abstract}
                    />
                    <TabButton
                      active={currentTab === 'introduction'}
                      onClick={() => setCurrentTab('introduction')}
                      label="引言"
                      hasContent={!!currentPaper.introduction}
                    />
                    <TabButton
                      active={currentTab === 'conclusion'}
                      onClick={() => setCurrentTab('conclusion')}
                      label="結論"
                      hasContent={!!currentPaper.conclusion}
                    />
                  </nav>
                </div>

                <div className="p-8 bg-gradient-to-b from-white to-gray-50">
                  <ContentSection
                    content={
                      currentTab === 'abstract'
                        ? currentPaper.abstract
                        : currentTab === 'introduction'
                        ? currentPaper.introduction
                        : currentPaper.conclusion
                    }
                    section={currentTab}
                  />
                </div>
              </div>

              {/* Notes Section */}
              <div className="mt-8 bg-white rounded-lg shadow-lg border border-gray-200 overflow-hidden">
                <div className="bg-gradient-to-r from-amber-50 to-yellow-50 border-b border-amber-200 px-6 py-4">
                  <div className="flex items-center gap-2">
                    <svg className="w-5 h-5 text-amber-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                    <h3 className="text-lg font-bold text-amber-900">筆記</h3>
                  </div>
                </div>
                <div className="p-6">
                  <textarea
                    value={notes}
                    onChange={(e) => setNotes(e.target.value)}
                    onBlur={handleSaveNotes}
                    className="w-full h-40 px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-amber-500 focus:ring-2 focus:ring-amber-200 resize-none transition font-serif text-gray-800 leading-relaxed"
                    placeholder="在此添加筆記、想法或重要觀察..."
                  />
                  {isSaving && (
                    <div className="flex items-center gap-2 mt-3 text-sm text-amber-600">
                      <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      <span>儲存中...</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  )
}

// 時間軸論文條目
function PaperTimelineItem({ paper, isActive, onClick }) {
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

  return (
    <div
      onClick={onClick}
      className={`p-3 rounded-lg cursor-pointer transition ${
        isActive
          ? 'bg-indigo-50 border-2 border-indigo-500'
          : 'bg-gray-50 border-2 border-transparent hover:bg-gray-100'
      }`}
    >
      <div className="flex items-center gap-2 mb-1">
        <span className="text-xs font-semibold text-indigo-600">{paper.year}</span>
        <span className={`text-xs px-2 py-0.5 rounded ${getStatusColor(paper.read_status)}`}>
          {paper.read_status === 'full_read' ? '已讀' : paper.read_status === 'abstract_only' ? '摘要' : '未讀'}
        </span>
      </div>
      <h4 className="text-sm font-medium text-gray-800 line-clamp-2">{paper.title}</h4>
    </div>
  )
}

// 閱讀狀態徽章
function ReadStatusBadge({ status, onChange }) {
  const statuses = [
    { value: 'unread', label: '未讀', color: 'bg-gray-100 text-gray-800' },
    { value: 'abstract_only', label: '已讀摘要', color: 'bg-yellow-100 text-yellow-800' },
    { value: 'full_read', label: '完整閱讀', color: 'bg-green-100 text-green-800' },
  ]

  const currentStatus = statuses.find(s => s.value === status) || statuses[0]

  return (
    <div className="relative group">
      <button className={`text-xs px-3 py-1 rounded ${currentStatus.color}`}>
        {currentStatus.label} ▼
      </button>
      <div className="absolute left-0 mt-1 w-32 bg-white border border-gray-200 rounded-lg shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition z-10">
        {statuses.map((s) => (
          <button
            key={s.value}
            onClick={() => onChange(s.value)}
            className="block w-full text-left px-3 py-2 text-sm hover:bg-gray-50 first:rounded-t-lg last:rounded-b-lg"
          >
            {s.label}
          </button>
        ))}
      </div>
    </div>
  )
}

// 標籤管理
function TagManager({ tags, onAddTag, onRemoveTag }) {
  const [isAdding, setIsAdding] = useState(false)
  const [newTag, setNewTag] = useState('')

  const predefinedTags = ['關鍵起點', '技術突破', '臨床應用', '仍有爭議', '方法演進']

  const handleAdd = () => {
    if (newTag.trim()) {
      onAddTag(newTag.trim())
      setNewTag('')
      setIsAdding(false)
    }
  }

  return (
    <div className="flex flex-wrap items-center gap-2">
      {tags.map((tag, index) => (
        <span
          key={index}
          className="inline-flex items-center gap-1 bg-blue-50 text-blue-700 text-xs px-2 py-1 rounded"
        >
          {tag}
          <button
            onClick={() => onRemoveTag(tag)}
            className="hover:text-blue-900"
          >
            ×
          </button>
        </span>
      ))}

      {isAdding ? (
        <div className="inline-flex items-center gap-1">
          <input
            type="text"
            value={newTag}
            onChange={(e) => setNewTag(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleAdd()}
            onBlur={handleAdd}
            className="w-24 text-xs px-2 py-1 border border-gray-300 rounded"
            placeholder="標籤名稱"
            autoFocus
          />
        </div>
      ) : (
        <button
          onClick={() => setIsAdding(true)}
          className="text-xs text-indigo-600 hover:text-indigo-700 px-2 py-1"
        >
          + 添加標籤
        </button>
      )}

      {isAdding && (
        <div className="w-full mt-2 flex flex-wrap gap-1">
          <span className="text-xs text-gray-500">快速添加：</span>
          {predefinedTags.map((tag) => (
            <button
              key={tag}
              onClick={() => {
                onAddTag(tag)
                setIsAdding(false)
              }}
              className="text-xs bg-gray-100 text-gray-700 px-2 py-0.5 rounded hover:bg-gray-200"
            >
              {tag}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}

// 標籤页按鈕
function TabButton({ active, onClick, label, hasContent }) {
  return (
    <button
      onClick={onClick}
      className={`px-6 py-3 text-sm font-medium border-b-2 transition ${
        active
          ? 'border-indigo-500 text-indigo-600'
          : 'border-transparent text-gray-600 hover:text-gray-800'
      } ${!hasContent && 'opacity-50'}`}
    >
      {label}
      {!hasContent && <span className="ml-1 text-xs">(無內容)</span>}
    </button>
  )
}

// 內容區域
function ContentSection({ content, section }) {
  if (!content) {
    return (
      <div className="text-center py-12 text-gray-500 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
        <svg className="mx-auto h-12 w-12 text-gray-400 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <p className="mb-2 font-medium">此部分暫無內容</p>
        <p className="text-sm">可以透過上傳 PDF 或手動輸入來添加內容</p>
      </div>
    )
  }

  const getSectionLabel = () => {
    switch (section) {
      case 'abstract':
        return '摘要'
      case 'introduction':
        return '引言'
      case 'conclusion':
        return '結論'
      default:
        return ''
    }
  }

  return (
    <div className="bg-gradient-to-br from-white to-gray-50 rounded-lg">
      {/* Section header with visual accent */}
      <div className="border-l-4 border-indigo-500 bg-indigo-50 px-6 py-3 mb-6 rounded-r-lg">
        <h3 className="text-lg font-bold text-indigo-900">{getSectionLabel()}</h3>
      </div>

      {/* Content area with enhanced typography */}
      <div className="px-6 pb-6">
        <div className="prose prose-slate prose-lg max-w-none
          prose-p:text-gray-800 prose-p:leading-loose prose-p:mb-6 prose-p:text-justify
          prose-headings:text-gray-900 prose-headings:font-bold
          prose-h1:text-2xl prose-h1:mb-4 prose-h1:mt-6
          prose-h2:text-xl prose-h2:mb-3 prose-h2:mt-5
          prose-h3:text-lg prose-h3:mb-2 prose-h3:mt-4
          prose-strong:text-gray-900 prose-strong:font-semibold prose-strong:bg-yellow-100 prose-strong:px-1 prose-strong:rounded
          prose-em:text-indigo-700 prose-em:italic
          prose-ul:my-4 prose-ul:space-y-2
          prose-ol:my-4 prose-ol:space-y-2
          prose-li:text-gray-800 prose-li:leading-relaxed
          prose-blockquote:border-l-4 prose-blockquote:border-indigo-400 prose-blockquote:pl-4 prose-blockquote:py-2 prose-blockquote:my-4 prose-blockquote:bg-indigo-50 prose-blockquote:italic prose-blockquote:text-gray-700
          prose-code:bg-gray-100 prose-code:text-pink-600 prose-code:px-2 prose-code:py-1 prose-code:rounded prose-code:text-sm prose-code:font-mono
          prose-pre:bg-gray-800 prose-pre:text-gray-100 prose-pre:p-4 prose-pre:rounded-lg prose-pre:my-4 prose-pre:overflow-x-auto
          prose-a:text-indigo-600 prose-a:no-underline hover:prose-a:underline prose-a:font-medium
          prose-img:rounded-lg prose-img:shadow-md prose-img:my-6">
          <div className="text-gray-800 leading-loose whitespace-pre-wrap font-serif">
            {content}
          </div>
        </div>
      </div>
    </div>
  )
}
