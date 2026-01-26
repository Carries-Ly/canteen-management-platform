from functools import wraps

from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt

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


def roles_required(*roles):
    def wrapper(fn):
        @wraps(fn)
        def decorated(*args, **kwargs):
            # #region agent log
            log_debug('backend/app/routes/utils.py:roles_required', 'roles_required check start', {'required_roles': list(roles)}, 'H1')
            # #endregion
            try:
                verify_jwt_in_request()
                # 从 additional_claims 中获取角色信息
                jwt_data = get_jwt()
                user_role = jwt_data.get("role")
                # #region agent log
                log_debug('backend/app/routes/utils.py:roles_required', 'roles_required check', {'user_role': user_role, 'required_roles': list(roles), 'jwt_keys': list(jwt_data.keys())}, 'H1')
                # #endregion
                if user_role not in roles:
                    # #region agent log
                    log_debug('backend/app/routes/utils.py:roles_required', 'roles_required denied', {'user_role': user_role, 'required_roles': list(roles)}, 'H1')
                    # #endregion
                    return jsonify({"msg": "无权限"}), 403
                return fn(*args, **kwargs)
            except Exception as e:
                # #region agent log
                log_debug('backend/app/routes/utils.py:roles_required', 'roles_required exception', {'error': str(e), 'error_type': type(e).__name__}, 'H3')
                # #endregion
                # 如果是 "Subject must be a string" 错误，提示用户重新登录
                error_msg = str(e)
                if "Subject must be a string" in error_msg:
                    return jsonify({"msg": "Token格式错误，请清除浏览器缓存并重新登录"}), 401
                return jsonify({"msg": f"JWT验证失败: {error_msg}"}), 401

        return decorated

    return wrapper
