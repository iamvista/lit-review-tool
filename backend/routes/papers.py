"""
論文管理 API
Papers Management Routes
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Paper, Project
from services.parser import BibTeXParser, DOIResolver
from services.extractor import PDFExtractor
from services.author_service import link_paper_authors, update_author_statistics
from services.pdf_processor import PDFProcessor
from sqlalchemy import desc
from werkzeug.utils import secure_filename
import os
from datetime import datetime

papers_bp = Blueprint('papers', __name__, url_prefix='/api/papers')


@papers_bp.route('/import/bibtex', methods=['POST'])
@jwt_required()
def import_bibtex():
    """
    批量導入 BibTeX 文獻
    POST /api/papers/import/bibtex
    Body: {
        "project_id": 1,
        "bibtex_content": "BibTeX 文件內容"
    }
    """
    user_id = int(get_jwt_identity())
    data = request.get_json()

    if not data or 'project_id' not in data or 'bibtex_content' not in data:
        return jsonify({'error': '缺少必要參數'}), 400

    project_id = data['project_id']
    bibtex_content = data['bibtex_content']

    # 驗證專案所有權
    project = Project.query.filter_by(id=project_id, user_id=user_id).first()
    if not project:
        return jsonify({'error': '專案不存在或無權限'}), 404

    try:
        # 解析 BibTeX
        parsed_papers = BibTeXParser.parse_bibtex_file(bibtex_content)

        if not parsed_papers:
            return jsonify({'error': 'BibTeX 文件為空或格式錯誤'}), 400

        # 批量創建論文
        created_papers = []
        all_author_ids = set()  # 記錄所有作者 ID，用於最後更新統計

        for paper_data in parsed_papers:
            paper = Paper(
                project_id=project_id,
                title=paper_data.get('title', ''),
                year=paper_data.get('year'),
                journal=paper_data.get('journal', ''),
                doi=paper_data.get('doi', ''),
                url=paper_data.get('url', ''),
                abstract=paper_data.get('abstract', ''),
                bibtex=paper_data.get('bibtex', ''),
                venue_type=_classify_venue(paper_data.get('journal', '')),
                original_source='bibtex'
            )

            db.session.add(paper)
            db.session.flush()  # 獲取 paper.id

            # 關聯作者
            authors_data = paper_data.get('authors', [])
            if authors_data:
                link_paper_authors(paper.id, authors_data)
                # 收集作者 ID（需要再次 flush 來獲取新創建的作者 ID）
                db.session.flush()
                from models import PaperAuthor
                paper_authors = PaperAuthor.query.filter_by(paper_id=paper.id).all()
                for pa in paper_authors:
                    all_author_ids.add(pa.author_id)

            created_papers.append(paper)

        db.session.commit()

        # 更新所有作者的統計資訊
        for author_id in all_author_ids:
            update_author_statistics(author_id)

        return jsonify({
            'success': True,
            'message': f'成功導入 {len(created_papers)} 篇論文',
            'count': len(created_papers),
            'papers': [paper.to_dict() for paper in created_papers]
        }), 201

    except ValueError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'導入失敗: {str(e)}'}), 500


@papers_bp.route('/import/doi', methods=['POST'])
@jwt_required()
def import_doi():
    """
    通過 DOI 導入論文
    POST /api/papers/import/doi
    Body: {
        "project_id": 1,
        "doi": "10.1234/example"
    }
    """
    user_id = int(get_jwt_identity())
    data = request.get_json()

    if not data or 'project_id' not in data or 'doi' not in data:
        return jsonify({'error': '缺少必要參數'}), 400

    project_id = data['project_id']
    doi = data['doi']

    # 驗證專案所有權
    project = Project.query.filter_by(id=project_id, user_id=user_id).first()
    if not project:
        return jsonify({'error': '專案不存在或無權限'}), 404

    try:
        # 解析 DOI
        paper_data = DOIResolver.resolve_doi(doi)

        if not paper_data:
            return jsonify({'error': 'DOI 解析失敗或不存在'}), 404

        # 創建論文
        paper = Paper(
            project_id=project_id,
            title=paper_data.get('title', ''),
            year=paper_data.get('year'),
            journal=paper_data.get('journal', ''),
            doi=paper_data.get('doi', ''),
            url=paper_data.get('url', ''),
            abstract=paper_data.get('abstract', ''),
            citation_count=paper_data.get('citation_count', 0),
            venue_type=_classify_venue(paper_data.get('journal', '')),
            original_source='doi'
        )

        db.session.add(paper)
        db.session.flush()  # 獲取 paper.id

        # 關聯作者
        authors_data = paper_data.get('authors', [])
        if authors_data:
            link_paper_authors(paper.id, authors_data)
            db.session.flush()

            # 獲取作者 ID 並更新統計
            from models import PaperAuthor
            paper_authors = PaperAuthor.query.filter_by(paper_id=paper.id).all()
            for pa in paper_authors:
                update_author_statistics(pa.author_id)

        db.session.commit()

        return jsonify({
            'success': True,
            'message': '論文導入成功',
            'paper': paper.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'導入失敗: {str(e)}'}), 500


@papers_bp.route('/<int:paper_id>', methods=['GET'])
@jwt_required()
def get_paper(paper_id):
    """
    獲取論文詳情
    GET /api/papers/:id?include_full_text=true
    """
    user_id = int(get_jwt_identity())
    include_full_text = request.args.get('include_full_text', 'false').lower() == 'true'

    # 獲取論文
    paper = Paper.query.get(paper_id)
    if not paper:
        return jsonify({'error': '論文不存在'}), 404

    # 驗證專案所有權
    project = Project.query.filter_by(id=paper.project_id, user_id=user_id).first()
    if not project:
        return jsonify({'error': '無權限訪問此論文'}), 403

    return jsonify({
        'success': True,
        'paper': paper.to_dict(include_full_text=include_full_text)
    }), 200


@papers_bp.route('/<int:paper_id>', methods=['PUT'])
@jwt_required()
def update_paper(paper_id):
    """
    更新論文資訊
    PUT /api/papers/:id
    Body: { "notes": "...", "tags": "...", ... }
    """
    user_id = int(get_jwt_identity())
    data = request.get_json()

    paper = Paper.query.get(paper_id)
    if not paper:
        return jsonify({'error': '論文不存在'}), 404

    # 驗證專案所有權
    project = Project.query.filter_by(id=paper.project_id, user_id=user_id).first()
    if not project:
        return jsonify({'error': '無權限修改此論文'}), 403

    try:
        # 更新允許的欄位
        updatable_fields = [
            'title', 'year', 'journal', 'doi', 'url', 'abstract',
            'introduction', 'conclusion', 'notes', 'tags',
            'read_status', 'highlights'
        ]

        for field in updatable_fields:
            if field in data:
                # 特殊處理標籤（數組轉逗號分隔字符串）
                if field == 'tags' and isinstance(data[field], list):
                    setattr(paper, field, ','.join(data[field]))
                else:
                    setattr(paper, field, data[field])

        db.session.commit()

        return jsonify({
            'success': True,
            'message': '論文更新成功',
            'paper': paper.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'更新失敗: {str(e)}'}), 500


@papers_bp.route('/<int:paper_id>', methods=['DELETE'])
@jwt_required()
def delete_paper(paper_id):
    """
    刪除論文
    DELETE /api/papers/:id
    """
    user_id = int(get_jwt_identity())

    paper = Paper.query.get(paper_id)
    if not paper:
        return jsonify({'error': '論文不存在'}), 404

    # 驗證專案所有權
    project = Project.query.filter_by(id=paper.project_id, user_id=user_id).first()
    if not project:
        return jsonify({'error': '無權限刪除此論文'}), 403

    try:
        db.session.delete(paper)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': '論文已刪除'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'刪除失敗: {str(e)}'}), 500


@papers_bp.route('/<int:paper_id>/notes', methods=['PUT'])
@jwt_required()
def update_notes(paper_id):
    """
    更新論文筆記
    PUT /api/papers/:id/notes
    Body: { "notes": "筆記內容" }
    """
    user_id = int(get_jwt_identity())
    data = request.get_json()

    if not data or 'notes' not in data:
        return jsonify({'error': '缺少筆記內容'}), 400

    paper = Paper.query.get(paper_id)
    if not paper:
        return jsonify({'error': '論文不存在'}), 404

    # 驗證專案所有權
    project = Project.query.filter_by(id=paper.project_id, user_id=user_id).first()
    if not project:
        return jsonify({'error': '無權限修改此論文'}), 403

    try:
        paper.notes = data['notes']
        db.session.commit()

        return jsonify({
            'success': True,
            'message': '筆記已更新'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'更新失敗: {str(e)}'}), 500


@papers_bp.route('/<int:paper_id>/read-status', methods=['PUT'])
@jwt_required()
def update_read_status(paper_id):
    """
    更新閱讀狀態
    PUT /api/papers/:id/read-status
    Body: { "status": "abstract_only" | "full_read" }
    """
    user_id = int(get_jwt_identity())
    data = request.get_json()

    if not data or 'status' not in data:
        return jsonify({'error': '缺少狀態參數'}), 400

    valid_statuses = ['unread', 'abstract_only', 'full_read']
    if data['status'] not in valid_statuses:
        return jsonify({'error': f'無效的狀態值。允許值: {", ".join(valid_statuses)}'}), 400

    paper = Paper.query.get(paper_id)
    if not paper:
        return jsonify({'error': '論文不存在'}), 404

    # 驗證專案所有權
    project = Project.query.filter_by(id=paper.project_id, user_id=user_id).first()
    if not project:
        return jsonify({'error': '無權限修改此論文'}), 403

    try:
        paper.read_status = data['status']
        db.session.commit()

        return jsonify({
            'success': True,
            'message': '閱讀狀態已更新'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'更新失敗: {str(e)}'}), 500


def _classify_venue(journal_name: str) -> str:
    """
    分類期刊類型
    根據期刊名稱判斷是 nature, science, cell 還是其他
    """
    if not journal_name:
        return 'other'

    journal_lower = journal_name.lower()

    if 'nature' in journal_lower:
        return 'nature'
    elif 'science' in journal_lower:
        return 'science'
    elif 'cell' in journal_lower:
        return 'cell'
    else:
        return 'q1'  # 默認設為 Q1，實際可以通過 SJR 等數據庫查詢


@papers_bp.route('/<int:paper_id>/tags', methods=['PUT'])
@jwt_required()
def update_tags(paper_id):
    """
    更新論文標籤
    PUT /api/papers/:id/tags
    Body: { "tags": ["關鍵起點", "技術突破"] }
    """
    user_id = int(get_jwt_identity())
    data = request.get_json()

    if not data or 'tags' not in data:
        return jsonify({'error': '缺少標籤參數'}), 400

    if not isinstance(data['tags'], list):
        return jsonify({'error': '標籤必須是數組'}), 400

    paper = Paper.query.get(paper_id)
    if not paper:
        return jsonify({'error': '論文不存在'}), 404

    # 驗證專案所有權
    project = Project.query.filter_by(id=paper.project_id, user_id=user_id).first()
    if not project:
        return jsonify({'error': '無權限修改此論文'}), 403

    try:
        # 將標籤列表轉為逗號分隔的字符串
        paper.tags = ','.join(data['tags']) if data['tags'] else ''
        db.session.commit()

        return jsonify({
            'success': True,
            'message': '標籤已更新',
            'tags': data['tags']
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'更新失敗: {str(e)}'}), 500


@papers_bp.route('/<int:paper_id>/extract', methods=['POST'])
@jwt_required()
def extract_pdf_content(paper_id):
    """
    從 PDF 提取內容（Abstract, Introduction, Conclusion）
    POST /api/papers/:id/extract
    Body: { "pdf_content": "base64_encoded_pdf" } 或上傳 PDF 文件
    """
    user_id = int(get_jwt_identity())

    paper = Paper.query.get(paper_id)
    if not paper:
        return jsonify({'error': '論文不存在'}), 404

    # 驗證專案所有權
    project = Project.query.filter_by(id=paper.project_id, user_id=user_id).first()
    if not project:
        return jsonify({'error': '無權限修改此論文'}), 403

    try:
        # 檢查是否有上傳的文件
        if 'file' in request.files:
            pdf_file = request.files['file']
            pdf_bytes = pdf_file.read()
        else:
            # 從 JSON 獲取 base64 編碼的 PDF
            data = request.get_json()
            if not data or 'pdf_content' not in data:
                return jsonify({'error': '缺少 PDF 內容'}), 400

            import base64
            try:
                pdf_bytes = base64.b64decode(data['pdf_content'])
            except Exception:
                return jsonify({'error': 'PDF 內容格式錯誤'}), 400

        # 提取內容
        extracted = PDFExtractor.extract_from_bytes(pdf_bytes)

        if 'error' in extracted:
            return jsonify({'error': f'PDF 提取失敗: {extracted["error"]}'}), 500

        # 更新論文內容
        if extracted.get('abstract'):
            paper.abstract = extracted['abstract']
        if extracted.get('introduction'):
            paper.introduction = extracted['introduction']
        if extracted.get('conclusion'):
            paper.conclusion = extracted['conclusion']

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'PDF 內容提取成功',
            'extracted': {
                'abstract': extracted.get('abstract') is not None,
                'introduction': extracted.get('introduction') is not None,
                'conclusion': extracted.get('conclusion') is not None
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'提取失敗: {str(e)}'}), 500


@papers_bp.route('/<int:paper_id>/highlights', methods=['PUT'])
@jwt_required()
def update_highlights(paper_id):
    """
    更新論文高亮內容
    PUT /api/papers/:id/highlights
    Body: { "highlights": [{"section": "abstract", "text": "...", "color": "yellow"}] }
    """
    user_id = int(get_jwt_identity())
    data = request.get_json()

    if not data or 'highlights' not in data:
        return jsonify({'error': '缺少高亮參數'}), 400

    if not isinstance(data['highlights'], list):
        return jsonify({'error': '高亮必須是數組'}), 400

    paper = Paper.query.get(paper_id)
    if not paper:
        return jsonify({'error': '論文不存在'}), 404

    # 驗證專案所有權
    project = Project.query.filter_by(id=paper.project_id, user_id=user_id).first()
    if not project:
        return jsonify({'error': '無權限修改此論文'}), 403

    try:
        paper.highlights = data['highlights']
        db.session.commit()

        return jsonify({
            'success': True,
            'message': '高亮已更新'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'更新失敗: {str(e)}'}), 500


@papers_bp.route('/projects/<int:project_id>/from-metadata', methods=['POST'])
@jwt_required()
def add_paper_from_metadata(project_id):
    """
    從搜尋結果的 metadata 創建論文
    POST /api/papers/projects/:id/from-metadata
    Body: {
        "title": "...",
        "authors": ["Author1", "Author2"],
        "year": 2024,
        "journal": "...",
        "doi": "...",
        "url": "...",
        "abstract": "...",
        "bibtex": "..."
    }
    """
    user_id = int(get_jwt_identity())
    data = request.get_json()

    # 驗證專案所有權
    project = Project.query.filter_by(id=project_id, user_id=user_id).first()
    if not project:
        return jsonify({'error': '專案不存在或無權限'}), 404

    if not data or 'title' not in data:
        return jsonify({'error': '缺少論文標題'}), 400

    try:
        # 創建論文記錄
        paper = Paper(
            project_id=project_id,
            title=data.get('title', '').strip(),
            year=data.get('year'),
            journal=data.get('journal', ''),
            doi=data.get('doi', ''),
            url=data.get('url', ''),
            abstract=data.get('abstract', ''),
            bibtex=data.get('bibtex', ''),
            original_source='search'
        )

        db.session.add(paper)
        db.session.flush()  # 獲取 paper.id

        # 連結作者
        if 'authors' in data and data['authors']:
            authors_data = []
            for idx, author_name in enumerate(data['authors'], 1):
                if isinstance(author_name, str):
                    # 簡單的名字分割（姓和名）
                    parts = author_name.strip().split()
                    if len(parts) >= 2:
                        first_name = ' '.join(parts[:-1])
                        last_name = parts[-1]
                    else:
                        first_name = ''
                        last_name = author_name.strip()

                    authors_data.append({
                        'full_name': author_name.strip(),
                        'first_name': first_name,
                        'last_name': last_name,
                        'position': idx
                    })

            link_paper_authors(paper.id, authors_data)

        db.session.commit()

        # 更新作者統計
        update_author_statistics(project_id)

        return jsonify({
            'success': True,
            'message': '論文添加成功',
            'paper': paper.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'添加失敗: {str(e)}'}), 500


@papers_bp.route('/upload-pdf', methods=['POST'])
@jwt_required()
def upload_pdf():
    """
    上傳 PDF 並提取資訊
    POST /api/papers/upload-pdf
    """
    user_id = int(get_jwt_identity())

    # 檢查文件
    if 'file' not in request.files:
        return jsonify({'error': '未提供 PDF 文件'}), 400

    file = request.files['file']
    project_id = request.form.get('project_id')

    if not project_id:
        return jsonify({'error': '未提供專案 ID'}), 400

    project_id = int(project_id)

    # 驗證專案權限
    project = Project.query.get(project_id)
    if not project or project.user_id != user_id:
        return jsonify({'error': '無權限訪問此專案'}), 403

    if file.filename == '':
        return jsonify({'error': '未選擇文件'}), 400

    if not file.filename.lower().endswith('.pdf'):
        return jsonify({'error': '只支援 PDF 文件'}), 400

    try:
        # 保存文件到臨時目錄
        filename = secure_filename(file.filename)
        upload_folder = os.path.join(os.getcwd(), 'uploads', str(user_id))
        os.makedirs(upload_folder, exist_ok=True)

        temp_path = os.path.join(upload_folder, filename)
        file.save(temp_path)

        # 處理 PDF
        processor = PDFProcessor()
        result = processor.process_pdf(temp_path)

        if not result['success']:
            return jsonify({
                'success': False,
                'error': result.get('error', 'PDF 處理失敗')
            }), 400

        # 返回提取的資訊（不直接存入資料庫，等用戶確認）
        return jsonify({
            'success': True,
            'data': {
                'filename': filename,
                'temp_path': temp_path,
                'metadata': result['metadata'],
                'sections': result['sections'],
                'extraction_method': result['extraction_method']
            }
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'處理 PDF 失敗：{str(e)}'
        }), 500


@papers_bp.route('/confirm-pdf', methods=['POST'])
@jwt_required()
def confirm_pdf():
    """
    確認 PDF 提取的資訊並存入資料庫
    POST /api/papers/confirm-pdf
    """
    user_id = int(get_jwt_identity())
    data = request.get_json()

    project_id = data.get('project_id')
    if not project_id:
        return jsonify({'error': '未提供專案 ID'}), 400

    # 驗證專案權限
    project = Project.query.get(project_id)
    if not project or project.user_id != user_id:
        return jsonify({'error': '無權限訪問此專案'}), 403

    try:
        # 創建 Paper 記錄
        paper = Paper(
            project_id=project_id,
            title=data.get('title', '未命名論文'),
            year=data.get('year'),
            journal=data.get('journal', ''),
            doi=data.get('doi', ''),
            url=data.get('url', ''),
            abstract=data.get('abstract', ''),
            introduction=data.get('introduction', ''),
            conclusion=data.get('conclusion', ''),
            pdf_path=data.get('temp_path', ''),
            original_source='pdf_upload'
        )

        db.session.add(paper)
        db.session.commit()

        # 處理作者（如果有）
        authors = data.get('authors', [])
        if authors:
            link_paper_authors(paper.id, authors, project_id)

        # 更新作者統計
        update_author_statistics(project_id)

        return jsonify({
            'success': True,
            'message': '論文導入成功',
            'paper': paper.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'保存失敗：{str(e)}'}), 500
