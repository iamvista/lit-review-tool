"""
數據模型
Database models using Flask-SQLAlchemy
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# 導入所有模型
from .user import User
from .project import Project
from .paper import Paper
from .author import Author, PaperAuthor, Collaboration
from .gap_analysis import GapAnalysis
