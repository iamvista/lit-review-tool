"""
專案模型
Project Model - 代表一個研究主題的文獻集合
"""

from . import db
from datetime import datetime


class Project(db.Model):
    """專案資料表"""

    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)

    # 基本資訊
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    domain = db.Column(db.String(100))  # 研究領域

    # 專案設定
    target_paper_count = db.Column(db.Integer, default=30)  # 目標論文數量（建議30篇，最多100篇）
    is_public = db.Column(db.Boolean, default=False)  # 是否公開分享
    share_token = db.Column(db.String(64), unique=True, index=True)  # 分享連結 token

    # 時間戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 關聯
    papers = db.relationship('Paper', backref='project', lazy='dynamic', cascade='all, delete-orphan')
    # gap_analyses = db.relationship('GapAnalysis', backref='project', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self, include_papers=False):
        """轉換為字典"""
        result = {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'description': self.description,
            'domain': self.domain,
            'target_paper_count': self.target_paper_count,
            'is_public': self.is_public,
            'paper_count': self.papers.count(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

        if include_papers:
            result['papers'] = [paper.to_dict() for paper in self.papers.order_by(Paper.year.asc())]

        return result

    def __repr__(self):
        return f'<Project {self.id}: {self.name}>'
