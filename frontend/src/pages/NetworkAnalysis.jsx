/**
 * 網絡分析頁面
 * Network Analysis Page - 作者網絡圖和關鍵人物列表
 */

import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../services/api';
import NetworkGraph from '../components/NetworkGraph';

export default function NetworkAnalysis() {
  const { projectId } = useParams();
  const navigate = useNavigate();

  const [project, setProject] = useState(null);
  const [networkData, setNetworkData] = useState(null);
  const [keyPeople, setKeyPeople] = useState([]);
  const [statistics, setStatistics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [selectedAuthor, setSelectedAuthor] = useState(null);

  // 獲取專案資訊
  useEffect(() => {
    fetchProject();
    fetchNetworkData();
    fetchKeyPeople();
    fetchStatistics();
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

  const fetchNetworkData = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/api/network/projects/${projectId}/network`);
      if (response.data.success) {
        setNetworkData(response.data.network);
      }
    } catch (error) {
      console.error('獲取網絡數據失敗:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchKeyPeople = async () => {
    try {
      const response = await api.get(`/api/network/projects/${projectId}/key-people`);
      if (response.data.success) {
        setKeyPeople(response.data.key_people);
      }
    } catch (error) {
      console.error('獲取關鍵人物失敗:', error);
    }
  };

  const fetchStatistics = async () => {
    try {
      const response = await api.get(`/api/network/projects/${projectId}/statistics`);
      if (response.data.success) {
        setStatistics(response.data.statistics);
      }
    } catch (error) {
      console.error('獲取統計資訊失敗:', error);
    }
  };

  const handleAnalyze = async () => {
    try {
      setAnalyzing(true);
      const response = await api.post(`/api/network/projects/${projectId}/analyze`);

      if (response.data.success) {
        alert(`網絡分析完成！\n共分析 ${response.data.total_authors} 位作者\n識別出 ${response.data.key_people_count} 位關鍵人物`);

        // 重新獲取數據
        await fetchNetworkData();
        await fetchKeyPeople();
        await fetchStatistics();
      }
    } catch (error) {
      console.error('網絡分析失敗:', error);
      alert('網絡分析失敗：' + (error.response?.data?.error || error.message));
    } finally {
      setAnalyzing(false);
    }
  };

  const handleNodeClick = async (authorId) => {
    try {
      const response = await api.get(`/api/network/authors/${authorId}`);
      if (response.data.success) {
        setSelectedAuthor(response.data.author);
      }
    } catch (error) {
      console.error('獲取作者資訊失敗:', error);
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
                  作者網絡分析
                </h1>
                {project && (
                  <p className="text-sm text-gray-500 mt-1">{project.name}</p>
                )}
              </div>
            </div>
            <button
              onClick={handleAnalyze}
              disabled={analyzing}
              className={`px-6 py-2 rounded-lg font-medium transition-colors ${
                analyzing
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  : 'bg-blue-600 text-white hover:bg-blue-700'
              }`}
            >
              {analyzing ? '分析中...' : '重新分析網絡'}
            </button>
          </div>
        </div>
      </div>

      {/* 統計卡片 */}
      {statistics && (
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-white rounded-lg shadow p-4">
              <div className="text-sm text-gray-500">總作者數</div>
              <div className="text-2xl font-bold text-gray-900 mt-1">
                {statistics.total_authors}
              </div>
            </div>
            <div className="bg-white rounded-lg shadow p-4">
              <div className="text-sm text-gray-500">合作關係</div>
              <div className="text-2xl font-bold text-gray-900 mt-1">
                {statistics.total_collaborations}
              </div>
            </div>
            <div className="bg-white rounded-lg shadow p-4">
              <div className="text-sm text-gray-500">關鍵人物</div>
              <div className="text-2xl font-bold text-blue-600 mt-1">
                {statistics.key_people_count}
              </div>
            </div>
            <div className="bg-white rounded-lg shadow p-4">
              <div className="text-sm text-gray-500">最活躍作者</div>
              <div className="text-sm font-medium text-gray-900 mt-1 truncate">
                {statistics.most_active_author?.name || 'N/A'}
              </div>
              <div className="text-xs text-gray-500">
                {statistics.most_active_author?.paper_count} 篇論文
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 主要內容區 */}
      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* 網絡圖 */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow">
              <div className="p-4 border-b">
                <h2 className="text-lg font-semibold text-gray-900">
                  作者合作網絡
                </h2>
                <p className="text-sm text-gray-500 mt-1">
                  點擊節點查看作者詳情，節點大小代表論文數量
                </p>
              </div>
              <div className="p-4">
                {loading ? (
                  <div className="flex items-center justify-center h-96">
                    <div className="text-center">
                      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
                      <p className="mt-4 text-gray-500">載入網絡數據中...</p>
                    </div>
                  </div>
                ) : networkData ? (
                  <NetworkGraph
                    data={networkData}
                    onNodeClick={handleNodeClick}
                  />
                ) : (
                  <div className="flex items-center justify-center h-96">
                    <div className="text-center">
                      <p className="text-gray-500">尚無網絡數據</p>
                      <button
                        onClick={handleAnalyze}
                        className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                      >
                        開始分析
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* 關鍵人物列表 */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow">
              <div className="p-4 border-b">
                <h2 className="text-lg font-semibold text-gray-900">
                  關鍵人物
                </h2>
                <p className="text-sm text-gray-500 mt-1">
                  按影響力排序
                </p>
              </div>
              <div className="divide-y max-h-[600px] overflow-y-auto">
                {keyPeople.length > 0 ? (
                  keyPeople.map((author, index) => (
                    <div
                      key={author.id}
                      className="p-4 hover:bg-gray-50 cursor-pointer transition-colors"
                      onClick={() => handleNodeClick(author.id)}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-2">
                            <span className="text-xs font-semibold text-gray-400">
                              #{index + 1}
                            </span>
                            <h3 className="font-medium text-gray-900">
                              {author.name}
                            </h3>
                            {author.is_key_person && (
                              <span className="px-2 py-0.5 text-xs font-medium bg-yellow-100 text-yellow-800 rounded">
                                核心
                              </span>
                            )}
                          </div>
                          {author.institution && (
                            <p className="text-xs text-gray-500 mt-1">
                              {author.institution}
                            </p>
                          )}
                          <div className="flex items-center space-x-4 mt-2 text-xs text-gray-600">
                            <span>{author.papers_in_project} 篇論文</span>
                            {author.total_citations > 0 && (
                              <span>{author.total_citations} 引用</span>
                            )}
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-sm font-semibold text-blue-600">
                            {author.influence_score?.toFixed(1) || 'N/A'}
                          </div>
                          <div className="text-xs text-gray-500">影響力</div>
                        </div>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="p-8 text-center text-gray-500">
                    暫無關鍵人物數據
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 作者詳情模態框 */}
      {selectedAuthor && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
          onClick={() => setSelectedAuthor(null)}
        >
          <div
            className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[80vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="p-6 border-b">
              <div className="flex items-start justify-between">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900">
                    {selectedAuthor.name}
                  </h2>
                  {selectedAuthor.institution && (
                    <p className="text-gray-600 mt-1">{selectedAuthor.institution}</p>
                  )}
                </div>
                <button
                  onClick={() => setSelectedAuthor(null)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>

            <div className="p-6">
              {/* 統計指標 */}
              <div className="grid grid-cols-3 gap-4 mb-6">
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <div className="text-2xl font-bold text-gray-900">
                    {selectedAuthor.total_papers || 0}
                  </div>
                  <div className="text-sm text-gray-500 mt-1">總論文數</div>
                </div>
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <div className="text-2xl font-bold text-gray-900">
                    {selectedAuthor.total_citations || 0}
                  </div>
                  <div className="text-sm text-gray-500 mt-1">總引用數</div>
                </div>
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <div className="text-2xl font-bold text-blue-600">
                    {selectedAuthor.influence_score?.toFixed(1) || 'N/A'}
                  </div>
                  <div className="text-sm text-gray-500 mt-1">影響力分數</div>
                </div>
              </div>

              {/* 中心性指標 */}
              {selectedAuthor.degree_centrality !== undefined && (
                <div className="mb-6">
                  <h3 className="text-sm font-semibold text-gray-700 mb-3">
                    網絡中心性指標
                  </h3>
                  <div className="space-y-2">
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span className="text-gray-600">度中心性</span>
                        <span className="font-medium">
                          {(selectedAuthor.degree_centrality * 100).toFixed(1)}%
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-blue-600 h-2 rounded-full"
                          style={{ width: `${selectedAuthor.degree_centrality * 100}%` }}
                        ></div>
                      </div>
                    </div>
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span className="text-gray-600">介數中心性</span>
                        <span className="font-medium">
                          {(selectedAuthor.betweenness_centrality * 100).toFixed(1)}%
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-green-600 h-2 rounded-full"
                          style={{ width: `${selectedAuthor.betweenness_centrality * 100}%` }}
                        ></div>
                      </div>
                    </div>
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span className="text-gray-600">接近中心性</span>
                        <span className="font-medium">
                          {(selectedAuthor.closeness_centrality * 100).toFixed(1)}%
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-purple-600 h-2 rounded-full"
                          style={{ width: `${selectedAuthor.closeness_centrality * 100}%` }}
                        ></div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
