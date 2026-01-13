"""
路由模組
API Routes
"""

# 導入所有藍圖
from .auth import auth_bp
from .projects import projects_bp
from .papers import papers_bp
from .network import network_bp
from .analysis import analysis_bp
from .search import search_bp
from .settings import settings_bp

__all__ = ['auth_bp', 'projects_bp', 'papers_bp', 'network_bp', 'analysis_bp', 'search_bp', 'settings_bp']
