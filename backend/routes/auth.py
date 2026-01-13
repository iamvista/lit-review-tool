"""
認證 API
Authentication Routes
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import db, User

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    註冊新用戶
    POST /api/auth/register
    Body: { "email": "...", "username": "...", "password": "..." }
    """
    data = request.get_json()

    # 驗證必填欄位
    if not data or not all(k in data for k in ['email', 'username', 'password']):
        return jsonify({'error': '缺少必要欄位'}), 400

    email = data['email'].strip().lower()
    username = data['username'].strip()
    password = data['password']

    # 檢查郵箱是否已存在
    if User.query.filter_by(email=email).first():
        return jsonify({'error': '此郵箱已被註冊'}), 400

    # 檢查用戶名是否已存在
    if User.query.filter_by(username=username).first():
        return jsonify({'error': '此用戶名已被使用'}), 400

    # 創建新用戶
    try:
        user = User(
            email=email,
            username=username,
            full_name=data.get('full_name', ''),
            institution=data.get('institution', ''),
            field_of_study=data.get('field_of_study', '')
        )
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        # 生成 JWT token
        access_token = create_access_token(identity=str(user.id))

        return jsonify({
            'success': True,
            'message': '註冊成功',
            'user': user.to_dict(),
            'access_token': access_token
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'註冊失敗: {str(e)}'}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    用戶登入
    POST /api/auth/login
    Body: { "email": "...", "password": "..." }
    """
    data = request.get_json()

    if not data or not all(k in data for k in ['email', 'password']):
        return jsonify({'error': '缺少必要欄位'}), 400

    email = data['email'].strip().lower()
    password = data['password']

    # 查找用戶
    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return jsonify({'error': '郵箱或密碼錯誤'}), 401

    if not user.is_active:
        return jsonify({'error': '帳戶已被停用'}), 403

    # 生成 JWT token
    access_token = create_access_token(identity=str(user.id))

    return jsonify({
        'success': True,
        'message': '登入成功',
        'user': user.to_dict(),
        'access_token': access_token
    }), 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """
    獲取當前登入用戶資訊
    GET /api/auth/me
    Header: Authorization: Bearer <token>
    """
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if not user:
        return jsonify({'error': '用戶不存在'}), 404

    return jsonify({
        'success': True,
        'user': user.to_dict()
    }), 200


@auth_bp.route('/update-profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """
    更新用戶資料
    PUT /api/auth/update-profile
    Body: { "full_name": "...", "institution": "...", "field_of_study": "..." }
    """
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if not user:
        return jsonify({'error': '用戶不存在'}), 404

    data = request.get_json()

    try:
        # 更新允許的欄位
        updatable_fields = ['full_name', 'institution', 'field_of_study']
        for field in updatable_fields:
            if field in data:
                setattr(user, field, data[field])

        db.session.commit()

        return jsonify({
            'success': True,
            'message': '資料更新成功',
            'user': user.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'更新失敗: {str(e)}'}), 500


@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """
    忘記密碼 - 生成重置令牌
    POST /api/auth/forgot-password
    Body: { "email": "..." }
    """
    data = request.get_json()

    if not data or 'email' not in data:
        return jsonify({'error': '請提供電子郵件'}), 400

    email = data['email'].strip().lower()

    # 查找用戶
    user = User.query.filter_by(email=email).first()

    # 無論用戶是否存在，都返回相同訊息（安全考量，避免洩露用戶信息）
    if not user:
        return jsonify({
            'success': True,
            'message': '如果該郵箱已註冊，您將收到重置密碼的連結'
        }), 200

    if not user.is_active:
        return jsonify({
            'success': True,
            'message': '如果該郵箱已註冊，您將收到重置密碼的連結'
        }), 200

    try:
        # 生成重置令牌
        reset_token = user.generate_reset_token()
        db.session.commit()

        # 在開發環境中，直接返回重置令牌（生產環境應該發送郵件）
        reset_url = f"http://localhost:5173/reset-password?token={reset_token}"

        return jsonify({
            'success': True,
            'message': '重置連結已生成',
            'reset_url': reset_url,  # 生產環境應該移除這個
            'token': reset_token,     # 生產環境應該移除這個
            'expires_in': '1 小時'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'生成重置令牌失敗: {str(e)}'}), 500


@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """
    重置密碼
    POST /api/auth/reset-password
    Body: { "token": "...", "new_password": "..." }
    """
    data = request.get_json()

    if not data or not all(k in data for k in ['token', 'new_password']):
        return jsonify({'error': '缺少必要欄位'}), 400

    token = data['token']
    new_password = data['new_password']

    # 驗證密碼長度
    if len(new_password) < 6:
        return jsonify({'error': '密碼長度至少需要 6 個字符'}), 400

    # 查找擁有此令牌的用戶
    user = User.query.filter_by(reset_token=token).first()

    if not user:
        return jsonify({'error': '無效的重置令牌'}), 400

    # 驗證令牌是否有效
    if not user.verify_reset_token(token):
        return jsonify({'error': '重置令牌已過期或無效'}), 400

    try:
        # 重置密碼
        user.set_password(new_password)
        user.clear_reset_token()
        db.session.commit()

        return jsonify({
            'success': True,
            'message': '密碼重置成功，請使用新密碼登入'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'重置密碼失敗: {str(e)}'}), 500
