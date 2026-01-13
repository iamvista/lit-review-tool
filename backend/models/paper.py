"""
論文模型
Paper Model - 核心模型，儲存論文資訊
"""

from . import db
from datetime import datetime


class Paper(db.Model):
    """論文資料表"""

    __tablename__ = 'papers'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False, index=True)

    # 基本資訊
    title = db.Column(db.Text, nullable=False)
    year = db.Column(db.Integer, index=True)  # 用於時間軸排序
    journal = db.Column(db.String(500))
    doi = db.Column(db.String(255), index=True)
    url = db.Column(db.Text)
    citation_count = db.Column(db.Integer, default=0)
    venue_type = db.Column(db.String(50))  # nature, science, cell, high_cited, q1, other

    # 橫向串讀的核心內容
    abstract = db.Column(db.Text)  # 摘要
    introduction = db.Column(db.Text)  # 引言（前幾段）
    conclusion = db.Column(db.Text)  # 結論/討論（後幾段）
    full_text = db.Column(db.Text)  # 完整文本（可選）

    # 元數據
    pdf_path = db.Column(db.String(500))  # PDF 文件路徑
    bibtex = db.Column(db.Text)  # BibTeX 格式
    original_source = db.Column(db.String(100))  # 導入來源

    # 用戶標註
    tags = db.Column(db.Text)  # 逗號分隔的標籤
    notes = db.Column(db.Text)  # 個人筆記
    highlights = db.Column(db.JSON)  # 高亮內容

    # 閱讀狀態
    read_status = db.Column(db.String(20), default='unread')  # unread, abstract_only, full_read
    read_time_seconds = db.Column(db.Integer, default=0)  # 閱讀時長
    reading_order = db.Column(db.Integer)  # 在專案中的閱讀順序

    # 時間戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 關聯（稍後添加 Author 多對多關係）
    # authors = db.relationship('Author', secondary='paper_authors', back_populates='papers')

    def to_dict(self, include_full_text=False):
        """轉換為字典"""
        result = {
            'id': self.id,
            'project_id': self.project_id,
            'title': self.title,
            'year': self.year,
            'journal': self.journal,
            'doi': self.doi,
            'url': self.url,
            'citation_count': self.citation_count,
            'venue_type': self.venue_type,
            'abstract': self.abstract,
            'introduction': self.introduction,
            'conclusion': self.conclusion,
            'pdf_path': self.pdf_path,
            'bibtex': self.bibtex,
            'tags': self.tags.split(',') if self.tags else [],
            'notes': self.notes,
            'highlights': self.highlights or [],
            'read_status': self.read_status,
            'read_time_seconds': self.read_time_seconds,
            'reading_order': self.reading_order,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

        if include_full_text and self.full_text:
            result['full_text'] = self.full_text

        return result

    def __repr__(self):
        return f'<Paper {self.id}: {self.title[:50]}>'
