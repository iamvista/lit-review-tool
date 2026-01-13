"""
配置文件
Configuration settings for different environments
"""

import os
from datetime import timedelta


class Config:
    """基礎配置"""

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-me'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-change-me'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)

    # 資料庫配置
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://litreview:password@localhost:5432/litreview_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # CORS 配置
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:5173').split(',')

    # Anthropic API
    ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')

    # 上傳配置
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'pdf', 'bib', 'txt'}

    @staticmethod
    def init_app(app):
        """初始化應用配置"""
        pass


class DevelopmentConfig(Config):
    """開發環境配置"""
    DEBUG = True
    TESTING = False

    # 開發環境使用 SQLite（絕對路徑）
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:////Users/vista/lit-review-tool/backend/instance/litreview.db'


class ProductionConfig(Config):
    """生產環境配置"""
    DEBUG = False
    TESTING = False

    @classmethod
    def init_app(cls, app):
        """生產環境初始化"""
        Config.init_app(app)

        # 生產環境檢查
        if not os.environ.get('SECRET_KEY'):
            raise ValueError('SECRET_KEY 環境變數未設置！')
        if not os.environ.get('JWT_SECRET_KEY'):
            raise ValueError('JWT_SECRET_KEY 環境變數未設置！')
        if not os.environ.get('DATABASE_URL'):
            raise ValueError('DATABASE_URL 環境變數未設置！')


class TestingConfig(Config):
    """測試環境配置"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
