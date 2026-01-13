/**
 * AI 分析頁面
 * AI Analysis Page - 研究缺口識別和領域分析
 */

import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../services/api';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

export default function AIAnalysis() {
  const { projectId } = useParams();
  const navigate = useNavigate();

  const [project, setProject] = useState(null);
  const [analyses, setAnalyses] = useState([]);
  const [currentAnalysis, setCurrentAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [apiKeyConfigured, setApiKeyConfigured] = useState(false);
  const [showAnalyzeModal, setShowAnalyzeModal] = useState(false);

  useEffect(() => {
    fetchProject();
    fetchAnalyses();
    checkApiKey();
  }, [projectId]);

  const fetchProject = async () => {
    try {
      const response = await api.get(`/api/projects/${projectId}`);
      if (response.data.success) {
        setProject(response.data.project);
      }
    } catch (error) {
      console.error('獲取專案失敗:', error);
    }
  };

  const fetchAnalyses = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/api/analysis/projects/${projectId}/analyses`);
      if (response.data.success) {
        setAnalyses(response.data.analyses);
        if (response.data.analyses.length > 0) {
          setCurrentAnalysis(response.data.analyses[0]);
        }
      }
    } catch (error) {
      console.error('獲取分析報告失敗:', error);
    } finally {
      setLoading(false);
    }
  };

  const checkApiKey = async () => {
    try {
      const response = await api.get('/api/analysis/check-api-key');
      setApiKeyConfigured(response.data.configured);
    } catch (error) {
      console.error('檢查 API 金鑰失敗:', error);
    }
  };

  const handleAnalyze = async (analysisType = 'comprehensive', title = '') => {
    try {
      setAnalyzing(true);
      setShowAnalyzeModal(false);

      const response = await api.post(`/api/analysis/projects/${projectId}/analyze`, {
        analysis_type: analysisType,
        title: title || `${project.name} - AI 分析報告`
      });

      if (response.data.success) {
        alert('AI 分析完成！');
        await fetchAnalyses();
        setCurrentAnalysis(response.data.analysis);
      }
    } catch (error) {
      console.error('AI 分析失敗:', error);
      const errorMsg = error.response?.data?.error || error.response?.data?.message || '分析失敗';
      alert('AI 分析失敗：' + errorMsg);
    } finally {
      setAnalyzing(false);
    }
  };

  const handleDeleteAnalysis = async (analysisId) => {
    if (!confirm('確定要刪除此分析報告嗎？')) return;

    try {
      await api.delete(`/api/analysis/analyses/${analysisId}`);
      await fetchAnalyses();
      if (currentAnalysis?.id === analysisId) {
        setCurrentAnalysis(null);
      }
      alert('分析報告已刪除');
    } catch (error) {
      console.error('刪除分析報告失敗:', error);
      alert('刪除失敗：' + (error.response?.data?.error || error.message));
    }
  };

  const handleExportMarkdown = () => {
    if (!currentAnalysis) return;

    const content = currentAnalysis.full_text || '';
    const blob = new Blob([content], { type: 'text/markdown;charset=utf-8' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${currentAnalysis.title || '分析報告'}.md`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  };

  const handleExportDocx = async () => {
    if (!currentAnalysis) return;

    try {
      const response = await api.post(`/api/analysis/analyses/${currentAnalysis.id}/export/docx`, {}, {
        responseType: 'blob'
      });

      const blob = new Blob([response.data], { type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${currentAnalysis.title || '分析報告'}.docx`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('匯出 DOCX 失敗:', error);
      alert('匯出失敗：' + (error.response?.data?.error || error.message));
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 頂部導航 */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate(`/projects/${projectId}`)}
                className="text-gray-600 hover:text-gray-900"
              >
                ← 返回專案
              </button>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  AI 研究缺口分析
                </h1>
                {project && (
                  <p className="text-sm text-gray-500 mt-1">{project.name}</p>
                )}
              </div>
            </div>
            <div className="flex items-center space-x-2">
              {!apiKeyConfigured && (
                <div className="flex items-center gap-2 text-sm text-orange-600 mr-4">
                  <span>⚠️ 未配置 AI API 金鑰</span>
                  <button
                    onClick={() => navigate('/settings')}
                    className="text-indigo-600 hover:text-indigo-800 underline"
                  >
                    前往設定
                  </button>
                </div>
              )}
              <button
                onClick={() => setShowAnalyzeModal(true)}
                disabled={analyzing || !apiKeyConfigured}
                className={`px-6 py-2 rounded-lg font-medium transition-colors ${
                  analyzing || !apiKeyConfigured
                    ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                    : 'bg-blue-600 text-white hover:bg-blue-700'
                }`}
              >
                {analyzing ? '分析中...' : '+ 新增分析'}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* 主要內容 */}
      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* 左側：分析報告列表 */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow">
              <div className="p-4 border-b">
                <h2 className="text-lg font-semibold text-gray-900">
                  分析報告
                </h2>
                <p className="text-sm text-gray-500 mt-1">
                  {analyses.length} 份報告
                </p>
              </div>
              <div className="divide-y max-h-[calc(100vh-300px)] overflow-y-auto">
                {loading ? (
                  <div className="p-8 text-center text-gray-500">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                    <p className="mt-2 text-sm">載入中...</p>
                  </div>
                ) : analyses.length > 0 ? (
                  analyses.map((analysis) => (
                    <div
                      key={analysis.id}
                      className={`p-4 cursor-pointer transition-colors ${
                        currentAnalysis?.id === analysis.id
                          ? 'bg-blue-50 border-l-4 border-blue-600'
                          : 'hover:bg-gray-50'
                      }`}
                      onClick={() => setCurrentAnalysis(analysis)}
                    >
                      <h3 className="font-medium text-gray-900 text-sm line-clamp-2">
                        {analysis.title}
                      </h3>
                      <div className="mt-2 flex items-center justify-between text-xs text-gray-500">
                        <span>{new Date(analysis.generated_at).toLocaleDateString('zh-TW')}</span>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleDeleteAnalysis(analysis.id);
                          }}
                          className="text-red-600 hover:text-red-800"
                        >
                          刪除
                        </button>
                      </div>
                      <div className="mt-1 text-xs text-gray-500">
                        分析 {analysis.papers_analyzed} 篇論文
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="p-8 text-center text-gray-500">
                    <p className="mb-2">尚無分析報告</p>
                    <button
                      onClick={() => setShowAnalyzeModal(true)}
                      disabled={!apiKeyConfigured}
                      className="text-blue-600 hover:text-blue-700 text-sm"
                    >
                      開始第一次分析
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* 右側：分析報告內容 */}
          <div className="lg:col-span-3">
            {currentAnalysis ? (
              <div className="bg-white rounded-lg shadow">
                <div className="p-6 border-b">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h2 className="text-2xl font-bold text-gray-900">
                        {currentAnalysis.title}
                      </h2>
                      <div className="mt-2 flex items-center space-x-4 text-sm text-gray-500">
                        <span>生成時間：{new Date(currentAnalysis.generated_at).toLocaleString('zh-TW')}</span>
                        <span>•</span>
                        <span>分析論文：{currentAnalysis.papers_analyzed} 篇</span>
                        <span>•</span>
                        <span>模型：{currentAnalysis.model_used || 'Claude'}</span>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2 ml-4">
                      <button
                        onClick={handleExportMarkdown}
                        className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                        title="匯出 Markdown"
                      >
                        📝 Markdown
                      </button>
                      <button
                        onClick={handleExportDocx}
                        className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-blue-600 rounded-lg hover:bg-blue-700 transition-colors"
                        title="匯出 Word 文件"
                      >
                        📄 Word
                      </button>
                    </div>
                  </div>
                </div>

                <div className="p-12 bg-gradient-to-b from-gray-50 to-white">
                  {currentAnalysis.full_text ? (
                    <div className="prose prose-slate max-w-4xl mx-auto
                      prose-headings:font-bold prose-headings:text-gray-800
                      prose-h1:text-4xl prose-h1:mb-10 prose-h1:pb-6 prose-h1:border-b-2 prose-h1:border-blue-300 prose-h1:mt-0
                      prose-h2:text-3xl prose-h2:mt-20 prose-h2:mb-8 prose-h2:pb-4 prose-h2:border-b-2 prose-h2:border-gray-300
                      prose-h3:text-2xl prose-h3:mt-12 prose-h3:mb-6 prose-h3:text-blue-700 prose-h3:font-bold
                      prose-h4:text-xl prose-h4:mt-10 prose-h4:mb-5 prose-h4:text-gray-800 prose-h4:font-semibold
                      prose-p:text-gray-700 prose-p:leading-loose prose-p:mb-8 prose-p:text-lg prose-p:tracking-wide
                      prose-ul:my-8 prose-ul:space-y-4
                      prose-li:my-4 prose-li:leading-loose prose-li:text-lg
                      prose-strong:text-gray-900 prose-strong:font-bold prose-strong:bg-yellow-100 prose-strong:px-2 prose-strong:py-0.5 prose-strong:rounded
                      prose-blockquote:border-l-4 prose-blockquote:border-blue-500 prose-blockquote:pl-8 prose-blockquote:py-4 prose-blockquote:my-10 prose-blockquote:bg-blue-50 prose-blockquote:rounded-r-lg prose-blockquote:shadow-sm
                      prose-code:bg-gray-100 prose-code:px-2 prose-code:py-1 prose-code:rounded prose-code:text-base prose-code:font-mono
                      prose-pre:bg-gray-800 prose-pre:text-gray-100 prose-pre:p-6 prose-pre:rounded-lg prose-pre:my-8 prose-pre:shadow-lg
                      prose-table:my-10 prose-th:bg-gray-100 prose-th:p-4 prose-td:p-4 prose-td:border-t prose-td:border-gray-200">
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>
                        {currentAnalysis.full_text}
                      </ReactMarkdown>
                    </div>
                  ) : (
                    <div className="text-center py-12 text-gray-500">
                      <p>報告內容不可用</p>
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <div className="bg-white rounded-lg shadow">
                <div className="p-12 text-center">
                  <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <h3 className="mt-2 text-sm font-medium text-gray-900">尚未選擇分析報告</h3>
                  <p className="mt-1 text-sm text-gray-500">
                    請從左側選擇一份報告查看，或創建新的分析
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* 分析類型選擇模態框 */}
      {showAnalyzeModal && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
          onClick={() => setShowAnalyzeModal(false)}
        >
          <div
            className="bg-white rounded-lg shadow-xl max-w-2xl w-full p-6"
            onClick={(e) => e.stopPropagation()}
          >
            <h3 className="text-xl font-bold text-gray-900 mb-4">
              選擇分析類型
            </h3>

            <div className="space-y-3">
              <AnalysisTypeOption
                title="綜合分析（推薦）"
                description="一次性完整分析：領域發展史、核心問題、方法演進、研究缺口、學術爭議、研究方向建議"
                onClick={() => handleAnalyze('comprehensive')}
              />
              <AnalysisTypeOption
                title="領域發展史"
                description="分析研究領域的起源、發展階段、重要突破和當前狀態"
                onClick={() => handleAnalyze('domain_history')}
              />
              <AnalysisTypeOption
                title="核心問題識別"
                description="識別反覆出現的研究問題及其演變過程"
                onClick={() => handleAnalyze('core_problems')}
              />
              <AnalysisTypeOption
                title="方法演進分析"
                description="分析研究方法隨時間的演變、改進和淘汰"
                onClick={() => handleAnalyze('method_evolution')}
              />
              <AnalysisTypeOption
                title="研究缺口識別"
                description="從方法論、應用、理論角度識別研究缺口"
                onClick={() => handleAnalyze('research_gaps')}
              />
              <AnalysisTypeOption
                title="學術爭議"
                description="識別領域內的爭議點和不同學派的觀點"
                onClick={() => handleAnalyze('controversies')}
              />
            </div>

            <div className="mt-6 flex justify-end">
              <button
                onClick={() => setShowAnalyzeModal(false)}
                className="px-4 py-2 text-gray-700 hover:text-gray-900"
              >
                取消
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function AnalysisTypeOption({ title, description, onClick }) {
  return (
    <button
      onClick={onClick}
      className="w-full text-left p-4 border border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors"
    >
      <h4 className="font-semibold text-gray-900">{title}</h4>
      <p className="text-sm text-gray-600 mt-1">{description}</p>
    </button>
  );
}
