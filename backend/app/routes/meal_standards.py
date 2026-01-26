from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt

from app.extensions import db
from app.models.meal_standard import MealStandard
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

meal_standards_bp = Blueprint("meal_standards", __name__)


@meal_standards_bp.get("")
@jwt_required()
def list_standards():
    # #region agent log
    try:
        jwt_data = get_jwt()
        log_debug('backend/app/routes/meal_standards.py:list_standards', 'list_standards entry', {'role': jwt_data.get('role'), 'jwt_keys': list(jwt_data.keys())}, 'H3')
    except Exception as e:
        log_debug('backend/app/routes/meal_standards.py:list_standards', 'get_jwt failed', {'error': str(e), 'error_type': type(e).__name__}, 'H3')
        raise
    # #endregion
    status = request.args.get("status")
    query = MealStandard.query
    if status:
        query = query.filter_by(status=status)
    items = query.order_by(MealStandard.id.desc()).all()
    return jsonify(
        [
            {
                "id": m.id,
                "name": m.name,
                "meal_type": m.meal_type,
                "price": m.price,
                "status": m.status,
                "description": m.description,
            }
            for m in items
        ]
    )


@meal_standards_bp.post("")
@jwt_required()
@roles_required("superadmin", "admin")
def create_standard():
    # #region agent log
    jwt_data = get_jwt()
    log_debug('backend/app/routes/meal_standards.py:create_standard', 'create_standard entry', {'role': jwt_data.get('role')}, 'H3')
    # #endregion
    data = request.json or {}
    m = MealStandard(
        name=data["name"],
        meal_type=data["meal_type"],
        price=data["price"],
        description=data.get("description"),
        status=data.get("status", "enabled"),
    )
    db.session.add(m)
    db.session.commit()
    return jsonify({"id": m.id}), 201


@meal_standards_bp.put("/<int:standard_id>")
@jwt_required()
@roles_required("superadmin", "admin")
def update_standard(standard_id):
    # #region agent log
    jwt_data = get_jwt()
    log_debug('backend/app/routes/meal_standards.py:update_standard', 'update_standard entry', {'standard_id': standard_id, 'role': jwt_data.get('role')}, 'H3')
    # #endregion
    data = request.json or {}
    m = MealStandard.query.get_or_404(standard_id)
    m.name = data.get("name", m.name)
    m.meal_type = data.get("meal_type", m.meal_type)
    m.price = data.get("price", m.price)
    m.description = data.get("description", m.description)
    m.status = data.get("status", m.status)
    db.session.commit()
    return jsonify({"msg": "ok"})
