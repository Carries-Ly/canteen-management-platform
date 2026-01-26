from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

from app.extensions import db
from app.models.user import User
from app.models.company import Company
from .utils import roles_required

# #region agent log
import json
import os
log_path = '/Users/c4rries/Desktop/贝晟/.cursor/debug.log'
def log_debug(location, message, data):
    try:
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps({
                'sessionId': 'debug-session',
                'runId': 'post-fix',
                'hypothesisId': 'H6',
                'location': location,
                'message': message,
                'data': data,
                'timestamp': int(__import__('time').time() * 1000)
            }, ensure_ascii=False) + '\n')
    except:
        pass
# #endregion

users_bp = Blueprint("users", __name__)

# #region agent log
log_debug('backend/app/routes/users.py:13', 'users_bp blueprint created', {'blueprint_name': 'users'})
# #endregion


@users_bp.get("")
@jwt_required()
@roles_required("superadmin", "admin")
def list_users():
    """获取用户列表（仅 superadmin/admin 可查看）"""
    # #region agent log
    log_debug('backend/app/routes/users.py:list_users', 'list_users called', {})
    # #endregion
    keyword = request.args.get("keyword", "").strip()
    role_filter = request.args.get("role")
    company_id_filter = request.args.get("company_id")
    query = User.query

    if keyword:
        query = query.filter(User.username.like(f"%{keyword}%"))
    if role_filter:
        query = query.filter(User.role == role_filter)
    if company_id_filter:
        try:
            query = query.filter(User.company_id == int(company_id_filter))
        except ValueError:
            pass

    users = query.order_by(User.id.desc()).all()
    # #region agent log
    log_debug('backend/app/routes/users.py:list_users', 'list_users success', {'count': len(users)})
    # #endregion
    return jsonify(
        [
            {
                "id": u.id,
                "username": u.username,
                "role": u.role,
                "company_id": u.company_id,
                "company_name": u.company.name if u.company else None,
            }
            for u in users
        ]
    )


@users_bp.get("/<int:user_id>")
@jwt_required()
def get_user(user_id):
    """获取单个用户详情"""
    # #region agent log
    log_debug('backend/app/routes/users.py:get_user', 'get_user called', {'user_id': user_id})
    # #endregion
    user = User.query.get_or_404(user_id)
    # #region agent log
    log_debug('backend/app/routes/users.py:get_user', 'get_user success', {'user_id': user.id, 'username': user.username})
    # #endregion
    return jsonify(
        {
            "id": user.id,
            "username": user.username,
            "role": user.role,
            "company_id": user.company_id,
            "company_name": user.company.name if user.company else None,
        }
    )


@users_bp.post("")
@jwt_required()
@roles_required("superadmin")
def create_user():
    """创建新用户（仅 superadmin）"""
    # #region agent log
    log_debug('backend/app/routes/users.py:create_user', 'create_user called', {})
    # #endregion
    data = request.json or {}
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()
    role = data.get("role", "").strip()
    company_id = data.get("company_id")

    if not username or not password or not role:
        return jsonify({"msg": "用户名、密码和角色必填"}), 400

    if role not in ["superadmin", "admin", "user", "customer"]:
        return jsonify({"msg": "无效的角色"}), 400

    # 检查用户名是否已存在
    if User.query.filter_by(username=username).first():
        return jsonify({"msg": "用户名已存在"}), 400

    # customer 角色必须绑定 company_id
    if role == "customer" and not company_id:
        return jsonify({"msg": "客户角色必须绑定公司"}), 400

    # 验证 company_id 是否存在
    if company_id:
        company = Company.query.get(company_id)
        if not company:
            return jsonify({"msg": "公司不存在"}), 400

    user = User(
        username=username,
        role=role,
        company_id=company_id if role == "customer" else None,
    )
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    # #region agent log
    log_debug('backend/app/routes/users.py:create_user', 'create_user success', {'userId': user.id, 'username': user.username})
    # #endregion
    return jsonify(
        {
            "id": user.id,
            "username": user.username,
            "role": user.role,
            "company_id": user.company_id,
            "company_name": user.company.name if user.company else None,
        }
    ), 201


@users_bp.put("/<int:user_id>")
@jwt_required()
@roles_required("superadmin")
def update_user(user_id):
    """更新用户信息（仅 superadmin）"""
    # #region agent log
    log_debug('backend/app/routes/users.py:update_user', 'update_user called', {'user_id': user_id})
    # #endregion
    user = User.query.get_or_404(user_id)
    data = request.json or {}

    # 更新密码
    if "password" in data and data["password"]:
        user.set_password(data["password"])

    # 更新角色
    if "role" in data:
        new_role = data["role"].strip()
        if new_role not in ["superadmin", "admin", "user", "customer"]:
            return jsonify({"msg": "无效的角色"}), 400
        user.role = new_role

    # 更新公司绑定
    if "company_id" in data:
        company_id = data["company_id"]
        if user.role == "customer" and not company_id:
            return jsonify({"msg": "客户角色必须绑定公司"}), 400
        if company_id:
            company = Company.query.get(company_id)
            if not company:
                return jsonify({"msg": "公司不存在"}), 400
        user.company_id = company_id if user.role == "customer" else None

    db.session.commit()

    # #region agent log
    log_debug('backend/app/routes/users.py:update_user', 'update_user success', {'user_id': user.id})
    # #endregion
    return jsonify(
        {
            "id": user.id,
            "username": user.username,
            "role": user.role,
            "company_id": user.company_id,
            "company_name": user.company.name if user.company else None,
        }
    )


@users_bp.delete("/<int:user_id>")
@jwt_required()
@roles_required("superadmin")
def delete_user(user_id):
    """删除用户（仅 superadmin）"""
    # #region agent log
    log_debug('backend/app/routes/users.py:delete_user', 'delete_user called', {'user_id': user_id})
    # #endregion
    user = User.query.get_or_404(user_id)

    # 不能删除自己
    # get_jwt_identity() 返回 subject（用户ID字符串）
    current_user_id = get_jwt_identity()
    if current_user_id and str(current_user_id) == str(user.id):
        return jsonify({"msg": "不能删除自己"}), 400

    db.session.delete(user)
    db.session.commit()

    # #region agent log
    log_debug('backend/app/routes/users.py:delete_user', 'delete_user success', {'user_id': user_id})
    # #endregion
    return jsonify({"msg": "删除成功"})

