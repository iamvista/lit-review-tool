"""
學術搜尋 API
Academic Search Routes
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from services.academic_search import AcademicSearchService

search_bp = Blueprint('search', __name__, url_prefix='/api/search')
search_service = AcademicSearchService()


@search_bp.route('/google-scholar', methods=['GET'])
@jwt_required()
def search_google_scholar():
    """
    Google Scholar 搜尋
    GET /api/search/google-scholar?q=deep learning&limit=10
    """
    query = request.args.get('q', '').strip()
    limit = request.args.get('limit', 10, type=int)

    if not query:
        return jsonify({'error': '請提供搜尋關鍵詞'}), 400

    if limit > 20:
        limit = 20  # 限制最大結果數

    try:
        results = search_service.search_google_scholar(query, max_results=limit)

        return jsonify({
            'success': True,
            'query': query,
            'count': len(results),
            'results': results
        }), 200

    except Exception as e:
        return jsonify({'error': f'搜尋失敗: {str(e)}'}), 500


@search_bp.route('/doi', methods=['GET'])
@jwt_required()
def search_by_doi():
    """
    DOI 查詢
    GET /api/search/doi?doi=10.1038/nature12345
    """
    doi = request.args.get('doi', '').strip()

    if not doi:
        return jsonify({'error': '請提供 DOI'}), 400

    try:
        result = search_service.search_by_doi(doi)

        if not result:
            return jsonify({'error': '找不到該 DOI 對應的論文'}), 404

        return jsonify({
            'success': True,
            'paper': result
        }), 200

    except Exception as e:
        return jsonify({'error': f'查詢失敗: {str(e)}'}), 500


@search_bp.route('/arxiv', methods=['GET'])
@jwt_required()
def search_arxiv():
    """
    arXiv 搜尋
    GET /api/search/arxiv?q=neural networks&limit=10
    """
    query = request.args.get('q', '').strip()
    limit = request.args.get('limit', 10, type=int)

    if not query:
        return jsonify({'error': '請提供搜尋關鍵詞或 arXiv ID'}), 400

    if limit > 20:
        limit = 20

    try:
        results = search_service.search_arxiv(query, max_results=limit)

        return jsonify({
            'success': True,
            'query': query,
            'count': len(results),
            'results': results
        }), 200

    except Exception as e:
        return jsonify({'error': f'搜尋失敗: {str(e)}'}), 500


@search_bp.route('/url', methods=['POST'])
@jwt_required()
def search_by_url():
    """
    URL 智能解析
    POST /api/search/url
    Body: { "url": "https://..." }
    """
    data = request.get_json()
    url = data.get('url', '').strip() if data else ''

    if not url:
        return jsonify({'error': '請提供 URL'}), 400

    try:
        result = search_service.search_by_url(url)

        if not result:
            return jsonify({'error': '無法解析該 URL 或找不到論文'}), 404

        return jsonify({
            'success': True,
            'paper': result
        }), 200

    except Exception as e:
        return jsonify({'error': f'解析失敗: {str(e)}'}), 500


@search_bp.route('/title', methods=['GET'])
@jwt_required()
def search_by_title():
    """
    標題搜尋
    GET /api/search/title?title=Deep Learning for Computer Vision
    """
    title = request.args.get('title', '').strip()

    if not title:
        return jsonify({'error': '請提供論文標題'}), 400

    try:
        result = search_service.search_by_title(title)

        if not result:
            return jsonify({'error': '找不到該論文'}), 404

        return jsonify({
            'success': True,
            'paper': result
        }), 200

    except Exception as e:
        return jsonify({'error': f'搜尋失敗: {str(e)}'}), 500


@search_bp.route('/smart', methods=['POST'])
@jwt_required()
def smart_search():
    """
    智能搜尋 - 自動判斷輸入類型
    POST /api/search/smart
    Body: { "input": "..." }

    支援：
    - 論文標題
    - DOI
    - URL（各種學術網站）
    - arXiv ID
    """
    data = request.get_json()
    input_text = data.get('input', '').strip() if data else ''

    if not input_text:
        return jsonify({'error': '請提供搜尋內容'}), 400

    try:
        result = None

        # 判斷輸入類型
        # 1. 檢查是否是 URL
        if input_text.startswith('http://') or input_text.startswith('https://'):
            result = search_service.search_by_url(input_text)

        # 2. 檢查是否是 DOI（10.xxxx/xxxxx 格式）
        elif input_text.startswith('10.') and '/' in input_text:
            result = search_service.search_by_doi(input_text)

        # 3. 檢查是否是 arXiv ID（YYMM.NNNNN 格式）
        elif search_service._is_arxiv_id(input_text):
            results = search_service.search_arxiv(input_text, max_results=1)
            result = results[0] if results else None

        # 4. 否則當作標題搜尋
        else:
            result = search_service.search_by_title(input_text)

        if not result:
            return jsonify({'error': '找不到相關論文，請嘗試更換搜尋方式'}), 404

        # 生成 BibTeX
        bibtex = search_service.generate_bibtex_from_paper(result)
        result['bibtex'] = bibtex

        return jsonify({
            'success': True,
            'input_type': 'auto-detected',
            'paper': result
        }), 200

    except Exception as e:
        return jsonify({'error': f'搜尋失敗: {str(e)}'}), 500
