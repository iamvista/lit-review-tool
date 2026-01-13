"""
作者服務
Author Service - 處理作者創建和更新
"""

from models import db, Author, PaperAuthor
from typing import List, Dict


def create_or_get_author(author_data: Dict) -> Author:
    """
    創建或獲取作者
    如果作者已存在（根據名字），則返回現有作者
    否則創建新作者

    Args:
        author_data: 作者數據字典，包含 first_name, last_name, full_name

    Returns:
        Author 對象
    """
    full_name = author_data.get('full_name', '').strip()
    first_name = author_data.get('first_name', '').strip()
    last_name = author_data.get('last_name', '').strip()

    if not full_name and not (first_name and last_name):
        return None

    # 嘗試查找現有作者（根據完整名字）
    author = Author.query.filter_by(name=full_name).first()

    if not author:
        # 創建新作者
        author = Author(
            name=full_name,
            first_name=first_name if first_name else None,
            last_name=last_name if last_name else None
        )
        db.session.add(author)
        db.session.flush()  # 獲取 ID 但不提交

    return author


def link_paper_authors(paper_id: int, authors_data: List[Dict]):
    """
    連結論文和作者

    Args:
        paper_id: 論文 ID
        authors_data: 作者數據列表，每個元素是字典包含 first_name, last_name, full_name
    """
    for position, author_data in enumerate(authors_data, start=1):
        author = create_or_get_author(author_data)

        if author:
            # 創建論文-作者關聯
            paper_author = PaperAuthor(
                paper_id=paper_id,
                author_id=author.id,
                author_position=position,
                is_corresponding=False  # 預設為 False，之後可以手動更新
            )
            db.session.add(paper_author)


def update_author_statistics(author_id: int):
    """
    更新作者的統計資訊

    Args:
        author_id: 作者 ID
    """
    author = Author.query.get(author_id)
    if not author:
        return

    # 計算論文數量
    paper_authors = PaperAuthor.query.filter_by(author_id=author_id).all()
    author.total_papers = len(paper_authors)

    # 計算第一作者論文數
    author.first_author_count = sum(1 for pa in paper_authors if pa.author_position == 1)

    # 計算通訊作者論文數
    author.corresponding_author_count = sum(1 for pa in paper_authors if pa.is_corresponding)

    # 計算總引用數
    total_citations = 0
    years = []
    for pa in paper_authors:
        if pa.paper:
            total_citations += pa.paper.citation_count or 0
            if pa.paper.year:
                years.append(pa.paper.year)

    author.total_citations = total_citations

    # 更新研究時期
    if years:
        author.first_publication_year = min(years)
        author.last_publication_year = max(years)

    db.session.flush()
