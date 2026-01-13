"""
研究缺口分析模型
Gap Analysis Models - AI 生成的研究缺口分析報告
"""

from . import db
from datetime import datetime


class GapAnalysis(db.Model):
    """研究缺口分析報告"""
    __tablename__ = 'gap_analyses'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    title = db.Column(db.String(500), nullable=False)

    # 分析類型
    analysis_type = db.Column(db.String(50), default='comprehensive')
    # comprehensive: 綜合分析
    # domain_history: 領域發展史
    # core_problems: 核心問題
    # method_evolution: 方法演進
    # research_gaps: 研究缺口
    # controversies: 學術爭議
    # research_directions: 研究方向建議

    # AI 生成內容
    full_text = db.Column(db.Text)  # 完整分析文本

    # 結構化內容（JSON 格式）
    summary = db.Column(db.Text)  # 領域發展史摘要
    core_problems = db.Column(db.JSON)  # 核心問題列表
    method_evolution = db.Column(db.JSON)  # 方法演進分析
    controversies = db.Column(db.JSON)  # 爭議點
    research_gaps = db.Column(db.JSON)  # 研究缺口
    recommendations = db.Column(db.JSON)  # 研究方向建議

    # 元數據
    model_used = db.Column(db.String(100))  # 使用的 AI 模型
    papers_analyzed = db.Column(db.Integer, default=0)  # 分析的論文數量
    confidence_score = db.Column(db.Float)  # 分析可信度（可選）

    # 時間戳
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 關聯
    project = db.relationship('Project', backref=db.backref('gap_analyses', lazy='dynamic'))

    def to_dict(self):
        """轉換為字典"""
        return {
            'id': self.id,
            'project_id': self.project_id,
            'title': self.title,
            'analysis_type': self.analysis_type,
            'full_text': self.full_text,
            'summary': self.summary,
            'core_problems': self.core_problems,
            'method_evolution': self.method_evolution,
            'controversies': self.controversies,
            'research_gaps': self.research_gaps,
            'recommendations': self.recommendations,
            'model_used': self.model_used,
            'papers_analyzed': self.papers_analyzed,
            'confidence_score': self.confidence_score,
            'generated_at': self.generated_at.isoformat() if self.generated_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<GapAnalysis {self.id}: {self.title}>'
