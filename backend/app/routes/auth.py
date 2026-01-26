from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token

from app.extensions import db
from app.models.user import User

# #region agent log
import json
import os
log_path = '/Users/c4rries/Desktop/贝晟/.cursor/debug.log'
def log_debug(location, message, data, hypothesis_id='ALL'):
    try:
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps({
                'sessionId': 'debug-session',
                'runId': 'post-fix',
                'hypothesisId': hypothesis_id,
                'location': location,
                'message': message,
                'data': data,
                'timestamp': int(__import__('time').time() * 1000)
            }, ensure_ascii=False) + '\n')
    except:
        pass
# #endregion

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/login")
def login():
    # #region agent log
    log_debug('backend/app/routes/auth.py:login', 'login entry', {}, 'H3')
    # #endregion
    data = request.json or {}
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return jsonify({"msg": "用户名和密码必填"}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        # #region agent log
        log_debug('backend/app/routes/auth.py:login', 'login failed', {'username': username}, 'H3')
        # #endregion
        return jsonify({"msg": "用户名或密码错误"}), 401

    # 使用 identity 和 additional_claims 方式
    # Flask-JWT-Extended 4.6.0 使用 identity 参数（必须是字符串）而不是 subject
    access_token = create_access_token(
        identity=str(user.id),  # identity字段仅存用户ID（字符串），避免复杂格式
        additional_claims={    # 存放额外信息
            "role": user.role,
            "company_id": user.company_id
        }
    )
    # #region agent log
    log_debug('backend/app/routes/auth.py:login', 'login success', {'user_id': user.id, 'role': user.role}, 'H3')
    # #endregion
    return jsonify(
        {
            "access_token": access_token,
            "user": {
                "id": user.id,
                "username": user.username,
                "role": user.role,
                "company_id": user.company_id,
            },
        }
    )
