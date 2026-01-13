"""
網絡分析 API
Network Analysis Routes - 作者網絡分析和關鍵人物識別
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Project, Paper, Author, PaperAuthor, Collaboration
from services.network_analyzer import AuthorNetworkAnalyzer
from sqlalchemy import func

network_bp = Blueprint('network', __name__, url_prefix='/api/network')


@network_bp.route('/projects/<int:project_id>/analyze', methods=['POST'])
@jwt_required()
def analyze_project_network(project_id):
    """
    分析專案的作者網絡
    POST /api/network/projects/:id/analyze

    這會：
    1. 分析專案中所有論文的作者關係
    2. 計算中心性指標
    3. 識別關鍵人物
    4. 更新資料庫中的統計資訊
    """
    user_id = int(get_jwt_identity())

    # 驗證專案所有權
    project = Project.query.filter_by(id=project_id, user_id=user_id).first()
    if not project:
        return jsonify({'error': '專案不存在或無權限'}), 404

    try:
        # 獲取專案的所有論文
        papers = Paper.query.filter_by(project_id=project_id).all()

        if not papers:
            return jsonify({'error': '專案中沒有論文'}), 400

        # 創建網絡分析器
        analyzer = AuthorNetworkAnalyzer()

        # 添加論文和作者到網絡
        for paper in papers:
            # 獲取論文的作者
            paper_authors = PaperAuthor.query.filter_by(paper_id=paper.id).all()

            authors_data = []
            for pa in paper_authors:
                authors_data.append({
                    'id': pa.author_id,
                    'name': pa.author.name,
                    'position': pa.author_position,
                    'is_corresponding': pa.is_corresponding
                })

            # 添加到網絡分析器
            analyzer.add_paper(
                paper.id,
                {
                    'year': paper.year,
                    'citation_count': paper.citation_count or 0,
                    'title': paper.title
                },
                authors_data
            )

        # 計算中心性指標
        metrics = analyzer.calculate_centrality_metrics()

        # 更新作者的網絡指標
        for author_id, author_metrics in metrics.items():
            author = Author.query.get(author_id)
            if author:
                author.degree_centrality = author_metrics['degree_centrality']
                author.betweenness_centrality = author_metrics['betweenness_centrality']
                author.closeness_centrality = author_metrics['closeness_centrality']
                author.influence_score = author_metrics['influence_score']
                author.is_key_person = author_metrics['influence_score'] > 20  # 閾值可調整

        # 識別關鍵人物
        key_people = analyzer.identify_key_people(top_n=10)

        # 更新或創建合作關係
        for author1_id, author2_id, edge_data in analyzer.graph.edges(data=True):
            # 確保 author1_id < author2_id
            if author1_id > author2_id:
                author1_id, author2_id = author2_id, author1_id

            collaboration = Collaboration.query.filter_by(
                author1_id=author1_id,
                author2_id=author2_id,
                project_id=project_id
            ).first()

            if collaboration:
                collaboration.collaboration_count = edge_data['weight']
            else:
                # 獲取論文年份
                paper_ids = edge_data['papers']
                years = [Paper.query.get(pid).year for pid in paper_ids if Paper.query.get(pid) and Paper.query.get(pid).year]

                collaboration = Collaboration(
                    author1_id=author1_id,
                    author2_id=author2_id,
                    project_id=project_id,
                    collaboration_count=edge_data['weight'],
                    first_collaboration_year=min(years) if years else None,
                    last_collaboration_year=max(years) if years else None,
                    collaboration_strength=edge_data['weight']
                )
                db.session.add(collaboration)

        db.session.commit()

        # 獲取網絡統計
        stats = analyzer.get_network_statistics()

        return jsonify({
            'success': True,
            'message': '網絡分析完成',
            'statistics': stats,
            'key_people_count': len(key_people),
            'total_authors': len(metrics)
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'分析失敗: {str(e)}'}), 500


@network_bp.route('/projects/<int:project_id>/network', methods=['GET'])
@jwt_required()
def get_network_data(project_id):
    """
    獲取專案的網絡數據（用於可視化）
    GET /api/network/projects/:id/network
    """
    user_id = int(get_jwt_identity())

    # 驗證專案所有權
    project = Project.query.filter_by(id=project_id, user_id=user_id).first()
    if not project:
        return jsonify({'error': '專案不存在或無權限'}), 404

    try:
        # 重新構建網絡（用於可視化）
        analyzer = AuthorNetworkAnalyzer()

        papers = Paper.query.filter_by(project_id=project_id).all()
        for paper in papers:
            paper_authors = PaperAuthor.query.filter_by(paper_id=paper.id).all()

            authors_data = []
            for pa in paper_authors:
                authors_data.append({
                    'id': pa.author_id,
                    'name': pa.author.name,
                    'position': pa.author_position,
                    'is_corresponding': pa.is_corresponding
                })

            analyzer.add_paper(
                paper.id,
                {'year': paper.year, 'citation_count': paper.citation_count or 0},
                authors_data
            )

        # 導出網絡數據
        network_data = analyzer.export_network_data()

        # 添加作者的詳細資訊
        for node in network_data['nodes']:
            author = Author.query.get(node['id'])
            if author:
                node['institution'] = author.institution
                node['is_key_person'] = author.is_key_person
                node['influence_score'] = author.influence_score

        return jsonify({
            'success': True,
            'network': network_data
        }), 200

    except Exception as e:
        return jsonify({'error': f'獲取網絡數據失敗: {str(e)}'}), 500


@network_bp.route('/projects/<int:project_id>/key-people', methods=['GET'])
@jwt_required()
def get_key_people(project_id):
    """
    獲取專案的關鍵人物列表
    GET /api/network/projects/:id/key-people
    """
    user_id = int(get_jwt_identity())

    # 驗證專案所有權
    project = Project.query.filter_by(id=project_id, user_id=user_id).first()
    if not project:
        return jsonify({'error': '專案不存在或無權限'}), 404

    try:
        # 獲取專案相關的所有作者
        author_ids = db.session.query(PaperAuthor.author_id).join(Paper).filter(
            Paper.project_id == project_id
        ).distinct().all()

        author_ids = [aid[0] for aid in author_ids]

        # 獲取作者詳細資訊並排序
        authors = Author.query.filter(Author.id.in_(author_ids)).all()

        # 按影響力分數排序
        authors_sorted = sorted(authors, key=lambda a: a.influence_score or 0, reverse=True)

        # 計算每個作者在該專案中的論文數
        author_paper_counts = {}
        for author in authors:
            count = PaperAuthor.query.join(Paper).filter(
                PaperAuthor.author_id == author.id,
                Paper.project_id == project_id
            ).count()
            author_paper_counts[author.id] = count

        # 轉換為字典
        key_people = []
        for author in authors_sorted[:20]:  # 返回前 20 位
            author_dict = author.to_dict()
            author_dict['papers_in_project'] = author_paper_counts.get(author.id, 0)
            key_people.append(author_dict)

        return jsonify({
            'success': True,
            'key_people': key_people,
            'total_authors': len(authors)
        }), 200

    except Exception as e:
        return jsonify({'error': f'獲取關鍵人物失敗: {str(e)}'}), 500


@network_bp.route('/authors/<int:author_id>', methods=['GET'])
@jwt_required()
def get_author_details(author_id):
    """
    獲取作者詳細資訊
    GET /api/network/authors/:id
    """
    try:
        author = Author.query.get(author_id)
        if not author:
            return jsonify({'error': '作者不存在'}), 404

        # 獲取作者的論文列表
        paper_authors = PaperAuthor.query.filter_by(author_id=author_id).all()
        papers = []
        for pa in paper_authors:
            paper = pa.paper
            papers.append({
                'id': paper.id,
                'title': paper.title,
                'year': paper.year,
                'journal': paper.journal,
                'citation_count': paper.citation_count,
                'position': pa.author_position,
                'is_corresponding': pa.is_corresponding
            })

        # 按年份排序
        papers.sort(key=lambda p: p['year'] or 0)

        # 獲取合作者
        collaborations = Collaboration.query.filter(
            (Collaboration.author1_id == author_id) | (Collaboration.author2_id == author_id)
        ).all()

        collaborators = []
        for collab in collaborations:
            collaborator_id = collab.author2_id if collab.author1_id == author_id else collab.author1_id
            collaborator = Author.query.get(collaborator_id)
            if collaborator:
                collaborators.append({
                    'id': collaborator.id,
                    'name': collaborator.name,
                    'institution': collaborator.institution,
                    'collaboration_count': collab.collaboration_count,
                    'first_year': collab.first_collaboration_year,
                    'last_year': collab.last_collaboration_year
                })

        # 按合作次數排序
        collaborators.sort(key=lambda c: c['collaboration_count'], reverse=True)

        return jsonify({
            'success': True,
            'author': author.to_dict(),
            'papers': papers,
            'collaborators': collaborators[:10]  # 前 10 位合作者
        }), 200

    except Exception as e:
        return jsonify({'error': f'獲取作者資訊失敗: {str(e)}'}), 500


@network_bp.route('/projects/<int:project_id>/statistics', methods=['GET'])
@jwt_required()
def get_network_statistics(project_id):
    """
    獲取專案的網絡統計資訊
    GET /api/network/projects/:id/statistics
    """
    user_id = int(get_jwt_identity())

    # 驗證專案所有權
    project = Project.query.filter_by(id=project_id, user_id=user_id).first()
    if not project:
        return jsonify({'error': '專案不存在或無權限'}), 404

    try:
        # 統計資訊
        total_authors = db.session.query(func.count(func.distinct(PaperAuthor.author_id))).join(Paper).filter(
            Paper.project_id == project_id
        ).scalar()

        total_collaborations = Collaboration.query.filter_by(project_id=project_id).count()

        key_people_count = db.session.query(func.count(Author.id)).join(PaperAuthor).join(Paper).filter(
            Paper.project_id == project_id,
            Author.is_key_person == True
        ).distinct().scalar()

        # 最活躍的作者
        top_author = db.session.query(
            Author.id,
            Author.name,
            func.count(PaperAuthor.paper_id).label('paper_count')
        ).join(PaperAuthor).join(Paper).filter(
            Paper.project_id == project_id
        ).group_by(Author.id, Author.name).order_by(
            func.count(PaperAuthor.paper_id).desc()
        ).first()

        return jsonify({
            'success': True,
            'statistics': {
                'total_authors': total_authors,
                'total_collaborations': total_collaborations,
                'key_people_count': key_people_count,
                'most_active_author': {
                    'id': top_author[0],
                    'name': top_author[1],
                    'paper_count': top_author[2]
                } if top_author else None
            }
        }), 200

    except Exception as e:
        return jsonify({'error': f'獲取統計資訊失敗: {str(e)}'}), 500
