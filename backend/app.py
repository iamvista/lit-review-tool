"""
LitReview Tool - Flask 主應用
Literature Review Tool for Graduate Students
基於「上帝視角文獻回顧法」
"""

from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_migrate import Migrate
import os
from datetime import datetime

from config import config
from models import db
# 路由導入
from routes import auth_bp, projects_bp, papers_bp, network_bp, analysis_bp, search_bp, settings_bp


def create_app(config_name=None):
    """應用工廠函數"""

    app = Flask(__name__)
    app.url_map.strict_slashes = False  # 禁用嚴格斜線

    # 載入配置
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app.config.from_object(config[config_name])

    # 生產環境檢查
    if config_name == 'production':
        config[config_name].init_app(app)

    # 初始化擴展
    db.init_app(app)
    jwt = JWTManager(app)

    # 配置 CORS
    CORS(app,
         origins=app.config['CORS_ORIGINS'],
         supports_credentials=True,
         allow_headers=['Content-Type', 'Authorization'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
         expose_headers=['Content-Type', 'Authorization', 'Content-Disposition', 'Content-Length'],
         max_age=3600)

    migrate = Migrate(app, db)

    # 註冊藍圖
    app.register_blueprint(auth_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(papers_bp)
    app.register_blueprint(network_bp)
    app.register_blueprint(analysis_bp)
    app.register_blueprint(search_bp)
    app.register_blueprint(settings_bp)

    # 健康檢查端點
    @app.route('/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'service': 'litreview-tool',
            'version': '1.0.0',
            'timestamp': datetime.utcnow().isoformat()
        }), 200

    # 根路徑
    @app.route('/')
    def index():
        return jsonify({
            'message': 'LitReview Tool API',
            'description': '博碩士生文獻管理工具 - 基於上帝視角文獻回顧法',
            'version': '1.0.0',
            'endpoints': {
                'auth': '/api/auth',
                'projects': '/api/projects',
                'papers': '/api/papers',
                'network': '/api/network',
                'analysis': '/api/analysis'
            },
            'features': [
                '文獻導入和時間軸排序',
                '橫向串讀視圖',
                '關鍵人物網絡分析',
                'AI 輔助研究缺口識別'
            ]
        }), 200

    # JWT 錯誤處理
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'error': 'Token 已過期',
            'message': '請重新登入'
        }), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({
            'error': 'Token 無效',
            'message': f'請提供有效的 Token: {str(error)}'
        }), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({
            'error': '缺少 Token',
            'message': '請先登入'
        }), 401

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        """當 JWT token 有效時，加載用戶資料"""
        from models import User
        user_id = int(jwt_data["sub"])
        return User.query.filter_by(id=user_id).first()

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'error': 'Token 已被撤銷',
            'message': '請重新登入'
        }), 401

    # 創建資料庫表
    @app.before_request
    def ensure_tables():
        """在第一次請求時創建資料庫表"""
        if not hasattr(app, '_tables_created'):
            try:
                db.create_all()
                app._tables_created = True
            except Exception as e:
                app.logger.warning(f"無法創建資料庫表：{e}")

    return app


# 用於開發環境直接運行
if __name__ == '__main__':
    app = create_app('development')
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
