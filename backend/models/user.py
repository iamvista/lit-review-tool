"""
用戶模型
User Model
"""

from . import db
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from cryptography.fernet import Fernet
import base64
import os
import secrets


class User(db.Model):
    """用戶資料表"""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    username = db.Column(db.String(100), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)

    # 個人資訊
    full_name = db.Column(db.String(200))
    institution = db.Column(db.String(200))
    field_of_study = db.Column(db.String(200))

    # 帳戶狀態
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)

    # API Keys (加密儲存)
    anthropic_api_key_encrypted = db.Column(db.Text, nullable=True)

    # 密碼重置
    reset_token = db.Column(db.String(255), nullable=True, index=True)
    reset_token_expires = db.Column(db.DateTime, nullable=True)

    # 時間戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 關聯
    projects = db.relationship('Project', backref='owner', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password):
        """設置密碼（加密）"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """驗證密碼"""
        return check_password_hash(self.password_hash, password)

    def generate_reset_token(self):
        """生成密碼重置令牌（有效期 1 小時）"""
        self.reset_token = secrets.token_urlsafe(32)
        self.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
        return self.reset_token

    def verify_reset_token(self, token):
        """驗證重置令牌是否有效"""
        if not self.reset_token or not self.reset_token_expires:
            return False
        if self.reset_token != token:
            return False
        if datetime.utcnow() > self.reset_token_expires:
            return False
        return True

    def clear_reset_token(self):
        """清除重置令牌"""
        self.reset_token = None
        self.reset_token_expires = None

    @staticmethod
    def _get_cipher():
        """獲取加密器（使用 Flask SECRET_KEY）"""
        secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-me')
        # 將 SECRET_KEY 轉換為 32 bytes 的 key
        key = base64.urlsafe_b64encode(secret_key.ljust(32)[:32].encode())
        return Fernet(key)

    def set_anthropic_api_key(self, api_key):
        """設置 Anthropic API Key（加密儲存）"""
        if api_key:
            cipher = self._get_cipher()
            encrypted = cipher.encrypt(api_key.encode())
            self.anthropic_api_key_encrypted = encrypted.decode()
        else:
            self.anthropic_api_key_encrypted = None

    def get_anthropic_api_key(self):
        """獲取 Anthropic API Key（解密）"""
        if not self.anthropic_api_key_encrypted:
            return None
        try:
            cipher = self._get_cipher()
            decrypted = cipher.decrypt(self.anthropic_api_key_encrypted.encode())
            return decrypted.decode()
        except Exception:
            return None

    @property
    def has_anthropic_api_key(self):
        """檢查是否已設置 Anthropic API Key"""
        return bool(self.anthropic_api_key_encrypted)

    def to_dict(self):
        """轉換為字典"""
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'full_name': self.full_name,
            'institution': self.institution,
            'field_of_study': self.field_of_study,
            'is_active': self.is_active,
            'has_anthropic_api_key': self.has_anthropic_api_key,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<User {self.username}>'
