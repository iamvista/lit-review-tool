"""
作者模型
Author Model - 儲存作者資訊和網絡分析數據
"""

from . import db
from datetime import datetime


class Author(db.Model):
    """作者資料表"""

    __tablename__ = 'authors'

    id = db.Column(db.Integer, primary_key=True)

    # 基本資訊
    name = db.Column(db.String(200), nullable=False, index=True)  # 完整姓名
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))

    # 機構資訊
    institution = db.Column(db.String(500))  # 所屬機構
    email = db.Column(db.String(255))

    # 學術ID
    google_scholar_id = db.Column(db.String(100))
    orcid = db.Column(db.String(100))
    scopus_id = db.Column(db.String(100))

    # 統計數據（從論文中計算）
    total_papers = db.Column(db.Integer, default=0)  # 論文總數
    total_citations = db.Column(db.Integer, default=0)  # 引用總數
    h_index = db.Column(db.Integer, default=0)
    first_author_count = db.Column(db.Integer, default=0)  # 第一作者論文數
    corresponding_author_count = db.Column(db.Integer, default=0)  # 通訊作者論文數

    # 網絡分析結果
    is_key_person = db.Column(db.Boolean, default=False)  # 是否為關鍵人物
    influence_score = db.Column(db.Float, default=0.0)  # 影響力分數（基於網絡分析）
    degree_centrality = db.Column(db.Float, default=0.0)  # 度中心性
    betweenness_centrality = db.Column(db.Float, default=0.0)  # 介數中心性
    closeness_centrality = db.Column(db.Float, default=0.0)  # 接近中心性

    # 研究時期
    first_publication_year = db.Column(db.Integer)  # 最早發表年份
    last_publication_year = db.Column(db.Integer)  # 最近發表年份

    # 時間戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 關聯
    paper_authors = db.relationship('PaperAuthor', back_populates='author', cascade='all, delete-orphan')

    def to_dict(self):
        """轉換為字典"""
        return {
            'id': self.id,
            'name': self.name,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'institution': self.institution,
            'email': self.email,
            'google_scholar_id': self.google_scholar_id,
            'orcid': self.orcid,
            'scopus_id': self.scopus_id,
            'total_papers': self.total_papers,
            'total_citations': self.total_citations,
            'h_index': self.h_index,
            'first_author_count': self.first_author_count,
            'corresponding_author_count': self.corresponding_author_count,
            'is_key_person': self.is_key_person,
            'influence_score': self.influence_score,
            'degree_centrality': self.degree_centrality,
            'betweenness_centrality': self.betweenness_centrality,
            'closeness_centrality': self.closeness_centrality,
            'first_publication_year': self.first_publication_year,
            'last_publication_year': self.last_publication_year,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class PaperAuthor(db.Model):
    """論文-作者關聯表（多對多關係）"""

    __tablename__ = 'paper_authors'

    id = db.Column(db.Integer, primary_key=True)
    paper_id = db.Column(db.Integer, db.ForeignKey('papers.id'), nullable=False, index=True)
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'), nullable=False, index=True)

    # 作者資訊
    author_position = db.Column(db.Integer, default=1)  # 作者順序（1=第一作者）
    is_corresponding = db.Column(db.Boolean, default=False)  # 是否為通訊作者
    affiliation = db.Column(db.String(500))  # 該論文中的單位
    contribution = db.Column(db.String(500))  # 貢獻描述

    # 時間戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 關聯
    paper = db.relationship('Paper', backref='paper_authors')
    author = db.relationship('Author', back_populates='paper_authors')

    def to_dict(self):
        """轉換為字典"""
        return {
            'id': self.id,
            'paper_id': self.paper_id,
            'author_id': self.author_id,
            'author_position': self.author_position,
            'is_corresponding': self.is_corresponding,
            'affiliation': self.affiliation,
            'contribution': self.contribution
        }


class Collaboration(db.Model):
    """作者合作關係表"""

    __tablename__ = 'collaborations'

    id = db.Column(db.Integer, primary_key=True)
    author1_id = db.Column(db.Integer, db.ForeignKey('authors.id'), nullable=False, index=True)
    author2_id = db.Column(db.Integer, db.ForeignKey('authors.id'), nullable=False, index=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False, index=True)

    # 合作統計
    collaboration_count = db.Column(db.Integer, default=1)  # 合作次數
    first_collaboration_year = db.Column(db.Integer)  # 首次合作年份
    last_collaboration_year = db.Column(db.Integer)  # 最近合作年份

    # 合作強度
    collaboration_strength = db.Column(db.Float, default=1.0)  # 合作強度（基於合作次數、時間等）

    # 時間戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 確保 author1_id < author2_id，避免重複
    __table_args__ = (
        db.UniqueConstraint('author1_id', 'author2_id', 'project_id', name='unique_collaboration'),
        db.CheckConstraint('author1_id < author2_id', name='author_order_check'),
    )

    def to_dict(self):
        """轉換為字典"""
        return {
            'id': self.id,
            'author1_id': self.author1_id,
            'author2_id': self.author2_id,
            'project_id': self.project_id,
            'collaboration_count': self.collaboration_count,
            'first_collaboration_year': self.first_collaboration_year,
            'last_collaboration_year': self.last_collaboration_year,
            'collaboration_strength': self.collaboration_strength
        }
