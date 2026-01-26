from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
import secrets
import string

from app.extensions import db
from app.models.user import User
from .utils import roles_required

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

staff_bp = Blueprint("staff", __name__)


def generate_random_password(length=8):
    """生成随机密码"""
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))


@staff_bp.get("")
@jwt_required()
@roles_required("superadmin")
def list_staff():
    """获取员工列表（仅 admin 和 user 角色）"""
    # #region agent log
    jwt_data = get_jwt()
    log_debug('backend/app/routes/staff.py:list_staff', 'list_staff entry', {'role': jwt_data.get('role')}, 'H1')
    # #endregion
    keyword = request.args.get("keyword", "").strip()
    role_filter = request.args.get("role")
    
    # 只查询 admin 和 user 角色的员工
    query = User.query.filter(User.role.in_(["admin", "user"]))
    
    if keyword:
        query = query.filter(User.username.like(f"%{keyword}%"))
    if role_filter and role_filter in ["admin", "user"]:
        query = query.filter(User.role == role_filter)
    
    staff_list = query.order_by(User.id.desc()).all()
    # #region agent log
    log_debug('backend/app/routes/staff.py:list_staff', 'list_staff success', {'count': len(staff_list)})
    # #endregion
    return jsonify(
        [
            {
                "id": s.id,
                "username": s.username,
                "role": s.role,
                "company_id": s.company_id,  # 应该为 None
            }
            for s in staff_list
        ]
    )


@staff_bp.get("/<int:staff_id>")
@jwt_required()
@roles_required("superadmin")
def get_staff(staff_id):
    """获取单个员工详情"""
    staff = User.query.get_or_404(staff_id)
    
    # 只能查看 admin 或 user 角色的员工
    if staff.role not in ["admin", "user"]:
        return jsonify({"msg": "只能查看员工账号"}), 403
    
    return jsonify(
        {
            "id": staff.id,
            "username": staff.username,
            "role": staff.role,
            "company_id": staff.company_id,
        }
    )


@staff_bp.post("")
@jwt_required()
@roles_required("superadmin")
def create_staff():
    """创建新员工（仅 superadmin）"""
    # #region agent log
    jwt_data = get_jwt()
    log_debug('backend/app/routes/staff.py:create_staff', 'create_staff entry', {'role': jwt_data.get('role')}, 'H1')
    # #endregion
    data = request.json or {}
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()
    role = data.get("role", "").strip()

    if not username or not password or not role:
        return jsonify({"msg": "用户名、密码和角色必填"}), 400

    # 只能创建 admin 或 user 角色
    if role not in ["admin", "user"]:
        return jsonify({"msg": "员工角色只能是 admin 或 user"}), 400

    # 检查用户名是否已存在
    if User.query.filter_by(username=username).first():
        return jsonify({"msg": "用户名已存在"}), 400

    staff = User(
        username=username,
        role=role,
        company_id=None,  # 员工不绑定客户企业
    )
    staff.set_password(password)
    db.session.add(staff)
    db.session.commit()

    # #region agent log
    log_debug('backend/app/routes/staff.py:create_staff', 'create_staff success', {'staff_id': staff.id, 'username': staff.username})
    # #endregion
    return jsonify(
        {
            "id": staff.id,
            "username": staff.username,
            "role": staff.role,
            "company_id": staff.company_id,
        }
    ), 201


@staff_bp.put("/<int:staff_id>")
@jwt_required()
@roles_required("superadmin")
def update_staff(staff_id):
    """更新员工信息（仅 superadmin）"""
    # #region agent log
    jwt_data = get_jwt()
    log_debug('backend/app/routes/staff.py:update_staff', 'update_staff entry', {'staff_id': staff_id, 'role': jwt_data.get('role')}, 'H1')
    # #endregion
    staff = User.query.get_or_404(staff_id)
    
    # 不能修改 superadmin 账号
    if staff.role == "superadmin":
        return jsonify({"msg": "不能修改 superadmin 账号"}), 403
    
    # 只能修改 admin 或 user 角色的员工
    if staff.role not in ["admin", "user"]:
        return jsonify({"msg": "只能修改员工账号"}), 403
    
    data = request.json or {}

    # 更新用户名
    if "username" in data:
        new_username = data.get("username", "").strip()
        if new_username and new_username != staff.username:
            # 检查新用户名是否已被使用
            if User.query.filter(User.username == new_username, User.id != staff_id).first():
                return jsonify({"msg": "用户名已存在"}), 400
            staff.username = new_username

    # 更新角色
    if "role" in data:
        new_role = data.get("role", "").strip()
        # 只能修改为 admin 或 user 角色
        if new_role not in ["admin", "user"]:
            return jsonify({"msg": "员工角色只能是 admin 或 user"}), 400
        staff.role = new_role

    db.session.commit()

    # #region agent log
    log_debug('backend/app/routes/staff.py:update_staff', 'update_staff success', {'staff_id': staff.id})
    # #endregion
    return jsonify(
        {
            "id": staff.id,
            "username": staff.username,
            "role": staff.role,
            "company_id": staff.company_id,
        }
    )


@staff_bp.post("/<int:staff_id>/reset-password")
@jwt_required()
@roles_required("superadmin")
def reset_password(staff_id):
    """重置员工密码（仅 superadmin）"""
    # #region agent log
    jwt_data = get_jwt()
    log_debug('backend/app/routes/staff.py:reset_password', 'reset_password entry', {'staff_id': staff_id}, 'H1')
    # #endregion
    staff = User.query.get_or_404(staff_id)
    
    # 不能修改 superadmin 账号
    if staff.role == "superadmin":
        return jsonify({"msg": "不能重置 superadmin 账号密码"}), 403
    
    # 只能重置 admin 或 user 角色的员工密码
    if staff.role not in ["admin", "user"]:
        return jsonify({"msg": "只能重置员工账号密码"}), 403
    
    data = request.json or {}
    new_password = data.get("new_password")
    
    # 如果没有提供新密码，生成随机密码
    if not new_password:
        new_password = generate_random_password()
    else:
        new_password = new_password.strip()
        if not new_password:
            return jsonify({"msg": "新密码不能为空"}), 400
    
    staff.set_password(new_password)
    db.session.commit()

    # #region agent log
    log_debug('backend/app/routes/staff.py:reset_password', 'reset_password success', {'staff_id': staff.id})
    # #endregion
    # 返回新密码（明文，仅首次返回）
    return jsonify(
        {
            "msg": "密码重置成功",
            "new_password": new_password,  # 注意：生产环境应该通过其他安全方式传递密码
        }
    )


@staff_bp.delete("/<int:staff_id>")
@jwt_required()
@roles_required("superadmin")
def delete_staff(staff_id):
    """删除员工（仅 superadmin）"""
    # #region agent log
    jwt_data = get_jwt()
    log_debug('backend/app/routes/staff.py:delete_staff', 'delete_staff entry', {'staff_id': staff_id}, 'H1')
    # #endregion
    staff = User.query.get_or_404(staff_id)
    
    # 不能删除 superadmin 账号
    if staff.role == "superadmin":
        return jsonify({"msg": "不能删除 superadmin 账号"}), 403
    
    # 只能删除 admin 或 user 角色的员工
    if staff.role not in ["admin", "user"]:
        return jsonify({"msg": "只能删除员工账号"}), 403
    
    # 不能删除自己
    current_user_id = get_jwt_identity()
    if current_user_id and str(current_user_id) == str(staff.id):
        return jsonify({"msg": "不能删除自己"}), 400

    db.session.delete(staff)
    db.session.commit()

    # #region agent log
    log_debug('backend/app/routes/staff.py:delete_staff', 'delete_staff success', {'staff_id': staff_id})
    # #endregion
    return jsonify({"msg": "删除成功"})

