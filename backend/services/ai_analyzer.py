"""
AI 分析器 - 兼容現有路由的包裝類
AI Analyzer - Wrapper class compatible with existing routes
"""

from .ai_analysis import AIAnalysisService
from typing import List, Dict


class AIAnalyzer:
    """AI 分析器（兼容層）"""

    def __init__(self, api_key: str):
        """初始化 AI 分析器"""
        self.service = AIAnalysisService(api_key=api_key)

    def analyze_with_context(self, papers: List, domain_name: str, analysis_type: str = 'comprehensive') -> Dict:
        """
        執行帶上下文的分析

        Args:
            papers: Paper 模型列表
            domain_name: 研究領域名稱
            analysis_type: 分析類型

        Returns:
            分析結果字典
        """

        # 將 Paper 模型轉換為字典
        papers_data = []
        for paper in papers:
            # 處理作者列表
            authors_list = []
            if hasattr(paper, 'authors'):
                for author in paper.authors:
                    if hasattr(author, 'name'):
                        authors_list.append(author.name)
                    else:
                        authors_list.append(str(author))

            paper_dict = {
                'id': paper.id,
                'title': paper.title,
                'year': paper.year,
                'authors': authors_list,
                'journal': paper.journal,
                'abstract': paper.abstract or '',
                'doi': paper.doi,
                'url': paper.url
            }
            papers_data.append(paper_dict)

        # 準備專案資訊
        project_info = {
            'name': domain_name,
            'description': '',
            'domain': domain_name
        }

        # 執行分析
        result = self.service.analyze_research_gap(papers_data, project_info)

        if not result.get('success'):
            raise ValueError(result.get('error', '分析失敗'))

        # 轉換為兼容格式
        analysis = result.get('analysis', {})

        return {
            'model': result.get('model_used', 'claude-3-5-sonnet-20241022'),
            'full_text': analysis.get('full_text', ''),
            'content': analysis.get('full_text', ''),
            'development_history': analysis.get('development_history', ''),
            'core_problems': analysis.get('core_problems', ''),
            'method_evolution': analysis.get('method_evolution', ''),
            'research_gaps': analysis.get('research_gaps', ''),
            'recommendations': analysis.get('recommendations', ''),
            'papers_analyzed': result.get('papers_analyzed', 0)
        }
