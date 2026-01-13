"""
作者網絡分析服務
使用 NetworkX 分析作者合作網絡，識別關鍵人物
"""

import networkx as nx
from typing import Dict, List, Tuple, Optional
from collections import defaultdict


class AuthorNetworkAnalyzer:
    """作者網絡分析器"""

    def __init__(self):
        self.graph = nx.Graph()
        self.authors = {}  # author_id -> author_data
        self.papers = {}  # paper_id -> paper_data

    def add_paper(self, paper_id: int, paper_data: Dict, authors: List[Dict]):
        """
        添加論文和作者到網絡

        Args:
            paper_id: 論文 ID
            paper_data: 論文數據（包含年份、引用數等）
            authors: 作者列表，每個作者包含 id, name, position 等
        """
        self.papers[paper_id] = paper_data

        # 添加作者節點
        for author in authors:
            author_id = author['id']
            if author_id not in self.authors:
                self.authors[author_id] = {
                    'id': author_id,
                    'name': author['name'],
                    'papers': [],
                    'citations': 0,
                    'first_author_count': 0,
                    'corresponding_count': 0,
                    'collaborators': set()
                }
                self.graph.add_node(author_id, **self.authors[author_id])

            # 更新作者統計
            self.authors[author_id]['papers'].append(paper_id)
            self.authors[author_id]['citations'] += paper_data.get('citation_count', 0)

            if author.get('position') == 1:
                self.authors[author_id]['first_author_count'] += 1
            if author.get('is_corresponding'):
                self.authors[author_id]['corresponding_count'] += 1

        # 建立合作關係（邊）
        if len(authors) > 1:
            for i in range(len(authors)):
                for j in range(i + 1, len(authors)):
                    author1_id = authors[i]['id']
                    author2_id = authors[j]['id']

                    # 添加合作關係
                    self.authors[author1_id]['collaborators'].add(author2_id)
                    self.authors[author2_id]['collaborators'].add(author1_id)

                    # 添加或更新邊
                    if self.graph.has_edge(author1_id, author2_id):
                        self.graph[author1_id][author2_id]['weight'] += 1
                        self.graph[author1_id][author2_id]['papers'].append(paper_id)
                    else:
                        self.graph.add_edge(
                            author1_id,
                            author2_id,
                            weight=1,
                            papers=[paper_id]
                        )

    def calculate_centrality_metrics(self) -> Dict[int, Dict]:
        """
        計算所有中心性指標

        Returns:
            字典，key 為 author_id，value 為包含各種中心性指標的字典
        """
        if len(self.graph.nodes()) == 0:
            return {}

        metrics = {}

        # 度中心性（Degree Centrality）
        degree_centrality = nx.degree_centrality(self.graph)

        # 介數中心性（Betweenness Centrality）
        betweenness_centrality = nx.betweenness_centrality(self.graph, weight='weight')

        # 接近中心性（Closeness Centrality）
        # 只計算連通的節點
        try:
            closeness_centrality = nx.closeness_centrality(self.graph)
        except:
            closeness_centrality = {node: 0 for node in self.graph.nodes()}

        # PageRank（影響力評分）
        try:
            pagerank = nx.pagerank(self.graph, weight='weight')
        except:
            pagerank = {node: 0 for node in self.graph.nodes()}

        # 整合所有指標
        for author_id in self.graph.nodes():
            metrics[author_id] = {
                'degree_centrality': degree_centrality.get(author_id, 0),
                'betweenness_centrality': betweenness_centrality.get(author_id, 0),
                'closeness_centrality': closeness_centrality.get(author_id, 0),
                'pagerank': pagerank.get(author_id, 0),
                'degree': self.graph.degree(author_id),  # 實際合作者數量
                'influence_score': self._calculate_influence_score(author_id)
            }

        return metrics

    def _calculate_influence_score(self, author_id: int) -> float:
        """
        計算作者的影響力分數
        綜合考慮：論文數量、引用數、合作者數量、第一作者比例等

        Args:
            author_id: 作者 ID

        Returns:
            影響力分數（0-100）
        """
        author = self.authors.get(author_id, {})

        # 基礎分數
        paper_count = len(author.get('papers', []))
        citations = author.get('citations', 0)
        collaborators = len(author.get('collaborators', set()))
        first_author_ratio = author.get('first_author_count', 0) / max(paper_count, 1)

        # 加權計算
        score = (
            paper_count * 2 +  # 論文數量
            min(citations / 100, 50) +  # 引用數（上限50分）
            collaborators * 1.5 +  # 合作者數量
            first_author_ratio * 10  # 第一作者比例
        )

        return min(score, 100)  # 限制在 0-100 之間

    def identify_key_people(self, top_n: int = 10) -> List[Tuple[int, Dict]]:
        """
        識別關鍵人物

        Args:
            top_n: 返回前 N 位關鍵人物

        Returns:
            [(author_id, metrics)] 列表，按影響力排序
        """
        metrics = self.calculate_centrality_metrics()

        # 按影響力分數排序
        ranked_authors = sorted(
            metrics.items(),
            key=lambda x: x[1]['influence_score'],
            reverse=True
        )

        return ranked_authors[:top_n]

    def detect_communities(self) -> Dict[int, int]:
        """
        檢測研究社群（學術陣營）

        Returns:
            字典，key 為 author_id，value 為社群 ID
        """
        if len(self.graph.nodes()) < 2:
            return {}

        try:
            # 使用 Louvain 社群檢測算法（需要 python-louvain 庫）
            # 這裡使用 NetworkX 內建的 greedy modularity 算法
            communities = nx.community.greedy_modularity_communities(self.graph, weight='weight')

            # 轉換為 author_id -> community_id 的字典
            community_map = {}
            for community_id, community in enumerate(communities):
                for author_id in community:
                    community_map[author_id] = community_id

            return community_map
        except:
            return {}

    def get_author_collaborations(self, author_id: int) -> List[Dict]:
        """
        獲取作者的所有合作關係

        Args:
            author_id: 作者 ID

        Returns:
            合作關係列表
        """
        if author_id not in self.graph:
            return []

        collaborations = []
        for neighbor in self.graph.neighbors(author_id):
            edge_data = self.graph[author_id][neighbor]
            collaborations.append({
                'collaborator_id': neighbor,
                'collaborator_name': self.authors[neighbor]['name'],
                'collaboration_count': edge_data['weight'],
                'shared_papers': edge_data['papers']
            })

        # 按合作次數排序
        collaborations.sort(key=lambda x: x['collaboration_count'], reverse=True)
        return collaborations

    def get_network_statistics(self) -> Dict:
        """
        獲取網絡整體統計資訊

        Returns:
            網絡統計數據
        """
        if len(self.graph.nodes()) == 0:
            return {
                'total_authors': 0,
                'total_collaborations': 0,
                'avg_collaborators': 0,
                'network_density': 0,
                'largest_component_size': 0
            }

        # 基本統計
        total_authors = self.graph.number_of_nodes()
        total_edges = self.graph.number_of_edges()
        degrees = [d for n, d in self.graph.degree()]
        avg_degree = sum(degrees) / len(degrees) if degrees else 0

        # 網絡密度
        density = nx.density(self.graph)

        # 最大連通分量
        if nx.is_connected(self.graph):
            largest_component_size = total_authors
        else:
            largest_component = max(nx.connected_components(self.graph), key=len)
            largest_component_size = len(largest_component)

        return {
            'total_authors': total_authors,
            'total_collaborations': total_edges,
            'avg_collaborators': round(avg_degree, 2),
            'network_density': round(density, 4),
            'largest_component_size': largest_component_size,
            'is_connected': nx.is_connected(self.graph)
        }

    def export_network_data(self) -> Dict:
        """
        導出網絡數據，用於前端可視化

        Returns:
            包含 nodes 和 links 的字典
        """
        nodes = []
        for author_id in self.graph.nodes():
            author = self.authors[author_id]
            nodes.append({
                'id': author_id,
                'name': author['name'],
                'papers_count': len(author['papers']),
                'citations': author['citations'],
                'first_author_count': author['first_author_count'],
                'degree': self.graph.degree(author_id)
            })

        links = []
        for author1, author2, edge_data in self.graph.edges(data=True):
            links.append({
                'source': author1,
                'target': author2,
                'weight': edge_data['weight'],
                'papers': edge_data['papers']
            })

        return {
            'nodes': nodes,
            'links': links
        }
