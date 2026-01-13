"""
用戶設定 API
Settings Routes - User preferences and API keys
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User

settings_bp = Blueprint('settings', __name__, url_prefix='/api/settings')


@settings_bp.route('/api-keys', methods=['GET'])
@jwt_required()
def get_api_keys_status():
    """
    獲取用戶 API Keys 設定狀態
    GET /api/settings/api-keys

    Returns:
        {
            "has_anthropic_api_key": true/false
        }
    """
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if not user:
        return jsonify({'error': '用戶不存在'}), 404

    return jsonify({
        'success': True,
        'has_anthropic_api_key': user.has_anthropic_api_key
    }), 200


@settings_bp.route('/api-keys/anthropic', methods=['POST'])
@jwt_required()
def set_anthropic_api_key():
    """
    設定 Anthropic API Key
    POST /api/settings/api-keys/anthropic

    Body:
        {
            "api_key": "sk-ant-api03-..."
        }
    """
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if not user:
        return jsonify({'error': '用戶不存在'}), 404

    data = request.get_json()
    api_key = data.get('api_key', '').strip()

    if not api_key:
        return jsonify({'error': 'API Key 不能為空'}), 400

    # 驗證 API Key 格式
    if not api_key.startswith('sk-ant-'):
        return jsonify({'error': 'API Key 格式不正確，應以 sk-ant- 開頭'}), 400

    try:
        # 設定加密的 API Key
        user.set_anthropic_api_key(api_key)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Anthropic API Key 設定成功'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'設定失敗: {str(e)}'}), 500


@settings_bp.route('/api-keys/anthropic', methods=['DELETE'])
@jwt_required()
def delete_anthropic_api_key():
    """
    刪除 Anthropic API Key
    DELETE /api/settings/api-keys/anthropic
    """
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if not user:
        return jsonify({'error': '用戶不存在'}), 404

    try:
        user.set_anthropic_api_key(None)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Anthropic API Key 已刪除'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'刪除失敗: {str(e)}'}), 500


@settings_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """
    獲取用戶資料
    GET /api/settings/profile
    """
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if not user:
        return jsonify({'error': '用戶不存在'}), 404

    return jsonify({
        'success': True,
        'user': user.to_dict()
    }), 200


@settings_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """
    更新用戶資料
    PUT /api/settings/profile

    Body:
        {
            "full_name": "...",
            "institution": "...",
            "field_of_study": "..."
        }
    """
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if not user:
        return jsonify({'error': '用戶不存在'}), 404

    data = request.get_json()

    # 更新可編輯欄位
    if 'full_name' in data:
        user.full_name = data['full_name']
    if 'institution' in data:
        user.institution = data['institution']
    if 'field_of_study' in data:
        user.field_of_study = data['field_of_study']

    try:
        db.session.commit()
        return jsonify({
            'success': True,
            'message': '資料更新成功',
            'user': user.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'更新失敗: {str(e)}'}), 500
