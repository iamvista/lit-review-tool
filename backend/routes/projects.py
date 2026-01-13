"""
專案管理 API
Projects Management Routes
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Project, Paper
from sqlalchemy import desc
import secrets
from urllib.parse import quote

projects_bp = Blueprint('projects', __name__, url_prefix='/api/projects')


@projects_bp.route('/', methods=['GET'])
@jwt_required()
def get_projects():
    """
    獲取用戶的所有專案
    GET /api/projects
    """
    user_id = int(get_jwt_identity())

    # 查詢用戶的所有專案，按更新時間排序
    projects = Project.query.filter_by(user_id=user_id).order_by(desc(Project.updated_at)).all()

    return jsonify({
        'success': True,
        'count': len(projects),
        'projects': [project.to_dict() for project in projects]
    }), 200


@projects_bp.route('/', methods=['POST'])
@jwt_required()
def create_project():
    """
    創建新專案
    POST /api/projects
    Body: {
        "name": "專案名稱",
        "description": "描述",
        "domain": "研究領域",
        "target_paper_count": 30
    }
    """
    user_id = int(get_jwt_identity())
    data = request.get_json()

    if not data or 'name' not in data:
        return jsonify({'error': '缺少專案名稱'}), 400

    try:
        project = Project(
            user_id=user_id,
            name=data['name'].strip(),
            description=data.get('description', ''),
            domain=data.get('domain', ''),
            target_paper_count=data.get('target_paper_count', 30),
            is_public=data.get('is_public', False)
        )

        db.session.add(project)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': '專案創建成功',
            'project': project.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'創建失敗: {str(e)}'}), 500


@projects_bp.route('/<int:project_id>', methods=['GET'])
@jwt_required()
def get_project(project_id):
    """
    獲取專案詳情
    GET /api/projects/:id?include_papers=true
    """
    user_id = int(get_jwt_identity())
    include_papers = request.args.get('include_papers', 'false').lower() == 'true'

    project = Project.query.filter_by(id=project_id, user_id=user_id).first()

    if not project:
        return jsonify({'error': '專案不存在'}), 404

    return jsonify({
        'success': True,
        'project': project.to_dict(include_papers=include_papers)
    }), 200


@projects_bp.route('/<int:project_id>', methods=['PUT'])
@jwt_required()
def update_project(project_id):
    """
    更新專案資訊
    PUT /api/projects/:id
    Body: { "name": "...", "description": "...", ... }
    """
    user_id = int(get_jwt_identity())
    data = request.get_json()

    project = Project.query.filter_by(id=project_id, user_id=user_id).first()

    if not project:
        return jsonify({'error': '專案不存在'}), 404

    try:
        # 更新允許的欄位
        updatable_fields = ['name', 'description', 'domain', 'target_paper_count', 'is_public']
        for field in updatable_fields:
            if field in data:
                setattr(project, field, data[field])

        db.session.commit()

        return jsonify({
            'success': True,
            'message': '專案更新成功',
            'project': project.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'更新失敗: {str(e)}'}), 500


@projects_bp.route('/<int:project_id>', methods=['DELETE'])
@jwt_required()
def delete_project(project_id):
    """
    刪除專案（連同所有論文）
    DELETE /api/projects/:id
    """
    user_id = int(get_jwt_identity())

    project = Project.query.filter_by(id=project_id, user_id=user_id).first()

    if not project:
        return jsonify({'error': '專案不存在'}), 404

    try:
        db.session.delete(project)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': '專案已刪除'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'刪除失敗: {str(e)}'}), 500


@projects_bp.route('/<int:project_id>/papers', methods=['GET'])
@jwt_required()
def get_project_papers(project_id):
    """
    獲取專案的所有論文（按年份排序，支援分頁）
    GET /api/projects/:id/papers?sort=year&order=asc&page=1&per_page=20
    """
    user_id = int(get_jwt_identity())

    # 驗證專案所有權
    project = Project.query.filter_by(id=project_id, user_id=user_id).first()
    if not project:
        return jsonify({'error': '專案不存在'}), 404

    # 獲取排序參數
    sort_by = request.args.get('sort', 'year')
    order = request.args.get('order', 'asc')

    # 獲取分頁參數
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 100, type=int)  # 預設 100，論文集通常不會太大

    # 是否包含完整文本
    include_full_text = request.args.get('include_full_text', 'false').lower() == 'true'

    # 構建查詢
    query = Paper.query.filter_by(project_id=project_id)

    # 排序
    if sort_by == 'year':
        sort_column = Paper.year
    elif sort_by == 'title':
        sort_column = Paper.title
    elif sort_by == 'citation_count':
        sort_column = Paper.citation_count
    else:
        sort_column = Paper.created_at

    if order == 'desc':
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(sort_column.asc())

    # 分頁（但如果 per_page=-1 則返回全部）
    if per_page == -1:
        papers = query.all()
        total = len(papers)
        has_next = False
        has_prev = False
    else:
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        papers = pagination.items
        total = pagination.total
        has_next = pagination.has_next
        has_prev = pagination.has_prev

    return jsonify({
        'success': True,
        'project_id': project_id,
        'count': len(papers),
        'total': total,
        'page': page,
        'per_page': per_page,
        'has_next': has_next,
        'has_prev': has_prev,
        'papers': [paper.to_dict(include_full_text=include_full_text) for paper in papers]
    }), 200


@projects_bp.route('/<int:project_id>/stats', methods=['GET'])
@jwt_required()
def get_project_stats(project_id):
    """
    獲取專案統計資訊
    GET /api/projects/:id/stats
    """
    user_id = int(get_jwt_identity())

    project = Project.query.filter_by(id=project_id, user_id=user_id).first()
    if not project:
        return jsonify({'error': '專案不存在'}), 404

    papers = Paper.query.filter_by(project_id=project_id).all()

    # 統計資訊
    stats = {
        'total_papers': len(papers),
        'target_count': project.target_paper_count,
        'progress_percentage': (len(papers) / project.target_paper_count * 100) if project.target_paper_count > 0 else 0,
        'read_count': sum(1 for p in papers if p.read_status != 'unread'),
        'unread_count': sum(1 for p in papers if p.read_status == 'unread'),
        'year_range': {
            'min': min([p.year for p in papers if p.year]) if papers and any(p.year for p in papers) else None,
            'max': max([p.year for p in papers if p.year]) if papers and any(p.year for p in papers) else None
        },
        'total_citations': sum(p.citation_count or 0 for p in papers),
        'venue_distribution': {}
    }

    # 期刊分佈
    for paper in papers:
        venue = paper.venue_type or 'other'
        stats['venue_distribution'][venue] = stats['venue_distribution'].get(venue, 0) + 1

    return jsonify({
        'success': True,
        'stats': stats
    }), 200


@projects_bp.route('/<int:project_id>/export/bibtex', methods=['GET'])
@jwt_required()
def export_bibtex(project_id):
    """
    匯出專案的所有論文為 BibTeX 格式
    GET /api/projects/:id/export/bibtex
    """
    user_id = int(get_jwt_identity())

    # 驗證專案所有權
    project = Project.query.filter_by(id=project_id, user_id=user_id).first()
    if not project:
        return jsonify({'error': '專案不存在'}), 404

    # 獲取所有論文，按年份排序
    papers = Paper.query.filter_by(project_id=project_id).order_by(Paper.year.asc()).all()

    if not papers:
        return jsonify({'error': '專案中沒有論文'}), 404

    # 組合所有 BibTeX
    bibtex_entries = []
    for paper in papers:
        if paper.bibtex:
            bibtex_entries.append(paper.bibtex)
        else:
            # 如果沒有儲存的 BibTeX，生成簡單的條目
            bibtex_entry = generate_bibtex_entry(paper)
            bibtex_entries.append(bibtex_entry)

    bibtex_content = '\n\n'.join(bibtex_entries)

    # 添加標題註釋
    header = f"% BibTeX entries for project: {project.name}\n"
    header += f"% Generated from LitReview Tool\n"
    header += f"% Total papers: {len(papers)}\n\n"

    full_content = header + bibtex_content

    from flask import make_response
    response = make_response(full_content)
    response.headers['Content-Type'] = 'text/plain; charset=utf-8'

    # 使用 RFC 5987 編碼支持中文檔案名稱
    filename = f"{project.name}_bibliography.bib"
    encoded_filename = quote(filename)
    response.headers['Content-Disposition'] = f"attachment; filename*=UTF-8''{encoded_filename}"

    return response


@projects_bp.route('/<int:project_id>/export/markdown', methods=['GET'])
@jwt_required()
def export_markdown(project_id):
    """
    匯出專案分析報告為 Markdown 格式
    GET /api/projects/:id/export/markdown
    """
    user_id = int(get_jwt_identity())

    # 驗證專案所有權
    project = Project.query.filter_by(id=project_id, user_id=user_id).first()
    if not project:
        return jsonify({'error': '專案不存在'}), 404

    # 獲取所有論文，按年份排序
    papers = Paper.query.filter_by(project_id=project_id).order_by(Paper.year.asc()).all()

    if not papers:
        return jsonify({'error': '專案中沒有論文'}), 404

    # 生成 Markdown 報告
    markdown_content = generate_markdown_report(project, papers)

    from flask import make_response
    response = make_response(markdown_content)
    response.headers['Content-Type'] = 'text/markdown; charset=utf-8'

    # 使用 RFC 5987 編碼支持中文檔案名稱
    filename = f"{project.name}_report.md"
    encoded_filename = quote(filename)
    response.headers['Content-Disposition'] = f"attachment; filename*=UTF-8''{encoded_filename}"

    return response


def generate_bibtex_entry(paper):
    """為論文生成 BibTeX 條目"""
    # 生成簡單的 cite key
    if paper.year and paper.title:
        first_word = paper.title.split()[0].lower() if paper.title.split() else 'paper'
        cite_key = f"{first_word}{paper.year}"
    else:
        cite_key = f"paper{paper.id}"

    entry = f"@article{{{cite_key},\n"
    entry += f"  title = {{{paper.title}}},\n"

    if paper.year:
        entry += f"  year = {{{paper.year}}},\n"

    if paper.journal:
        entry += f"  journal = {{{paper.journal}}},\n"

    if paper.doi:
        entry += f"  doi = {{{paper.doi}}},\n"

    if paper.url:
        entry += f"  url = {{{paper.url}}},\n"

    entry += "}\n"

    return entry


def generate_markdown_report(project, papers):
    """生成 Markdown 格式的專案報告"""
    md = f"# {project.name}\n\n"

    if project.description:
        md += f"## 專案描述\n\n{project.description}\n\n"

    if project.domain:
        md += f"**研究領域**: {project.domain}\n\n"

    md += f"**論文數量**: {len(papers)} 篇\n\n"

    # 年份範圍
    years = [p.year for p in papers if p.year]
    if years:
        md += f"**年份範圍**: {min(years)} - {max(years)}\n\n"

    md += "---\n\n"
    md += "## 論文列表（按年份排序）\n\n"

    # 按年份分組
    papers_by_year = {}
    for paper in papers:
        year = paper.year or '未知年份'
        if year not in papers_by_year:
            papers_by_year[year] = []
        papers_by_year[year].append(paper)

    # 按年份排序輸出
    for year in sorted(papers_by_year.keys(), reverse=True):
        md += f"### {year}\n\n"
        for paper in papers_by_year[year]:
            md += f"**{paper.title}**\n\n"

            if paper.journal:
                md += f"*{paper.journal}*\n\n"

            if paper.abstract:
                md += f"> {paper.abstract}\n\n"

            if paper.doi:
                md += f"DOI: {paper.doi}\n\n"

            if paper.tags:
                tags_list = paper.tags.split(',')
                md += f"標籤: {', '.join(f'`{tag.strip()}`' for tag in tags_list)}\n\n"

            if paper.notes:
                md += f"**筆記**:\n\n{paper.notes}\n\n"

            md += "---\n\n"

    # 添加生成資訊
    md += "\n\n*由 LitReview Tool 生成*\n"

    return md


@projects_bp.route('/<int:project_id>/share', methods=['POST'])
@jwt_required()
def create_share_link(project_id):
    """
    生成專案分享連結
    POST /api/projects/:id/share
    """
    user_id = int(get_jwt_identity())

    project = Project.query.filter_by(id=project_id, user_id=user_id).first()
    if not project:
        return jsonify({'error': '專案不存在'}), 404

    try:
        # 生成唯一的分享 token（如果還沒有）
        if not project.share_token:
            project.share_token = secrets.token_urlsafe(32)

        # 設置為公開
        project.is_public = True

        db.session.commit()

        share_url = f"/share/{project.share_token}"

        return jsonify({
            'success': True,
            'share_url': share_url,
            'share_token': project.share_token,
            'message': '分享連結已生成'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'生成分享連結失敗: {str(e)}'}), 500


@projects_bp.route('/<int:project_id>/share', methods=['DELETE'])
@jwt_required()
def revoke_share_link(project_id):
    """
    撤銷專案分享連結
    DELETE /api/projects/:id/share
    """
    user_id = int(get_jwt_identity())

    project = Project.query.filter_by(id=project_id, user_id=user_id).first()
    if not project:
        return jsonify({'error': '專案不存在'}), 404

    try:
        # 設置為私有
        project.is_public = False
        # 可選：清除 token（或保留以便重新啟用分享）
        # project.share_token = None

        db.session.commit()

        return jsonify({
            'success': True,
            'message': '分享連結已撤銷'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'撤銷失敗: {str(e)}'}), 500


@projects_bp.route('/shared/<share_token>', methods=['GET'])
def get_shared_project(share_token):
    """
    通過分享連結獲取公開專案（無需登入）
    GET /api/projects/shared/:token?include_papers=true
    """
    include_papers = request.args.get('include_papers', 'false').lower() == 'true'

    project = Project.query.filter_by(share_token=share_token, is_public=True).first()

    if not project:
        return jsonify({'error': '分享連結無效或已過期'}), 404

    return jsonify({
        'success': True,
        'project': project.to_dict(include_papers=include_papers),
        'is_shared': True
    }), 200
