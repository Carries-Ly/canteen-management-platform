from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt

from app.extensions import db
from app.models.company import Company
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

companies_bp = Blueprint("companies", __name__)


@companies_bp.get("")
@jwt_required()
def list_companies():
    """获取客户公司列表（所有角色可查看）"""
    # #region agent log
    jwt_data = get_jwt()
    log_debug('backend/app/routes/companies.py:list_companies', 'list_companies entry', {'role': jwt_data.get('role'), 'company_id': jwt_data.get('company_id')}, 'H3')
    # #endregion
    keyword = request.args.get("keyword", "").strip()
    query = Company.query

    if keyword:
        query = query.filter(
            Company.name.like(f"%{keyword}%")
            | Company.contact_person.like(f"%{keyword}%")
            | Company.contact_phone.like(f"%{keyword}%")
        )

    companies = query.order_by(Company.created_at.desc()).all()
    # #region agent log
    log_debug('backend/app/routes/companies.py:list_companies', 'list_companies success', {'count': len(companies)}, 'H1')
    # #endregion
    return jsonify(
        [
            {
                "id": c.id,
                "name": c.name,
                "contact_person": c.contact_person,
                "contact_phone": c.contact_phone,
                "address": c.address,
                "created_at": c.created_at.isoformat() if c.created_at else None,
            }
            for c in companies
        ]
    )


@companies_bp.get("/<int:company_id>")
@jwt_required()
def get_company(company_id):
    """获取单个客户公司详情"""
    company = Company.query.get_or_404(company_id)
    return jsonify(
        {
            "id": company.id,
            "name": company.name,
            "contact_person": company.contact_person,
            "contact_phone": company.contact_phone,
            "address": company.address,
            "created_at": company.created_at.isoformat() if company.created_at else None,
        }
    )


@companies_bp.post("")
@jwt_required()
@roles_required("superadmin", "admin")
def create_company():
    """创建新客户公司（仅 superadmin/admin）"""
    # #region agent log
    jwt_data = get_jwt()
    log_debug('backend/app/routes/companies.py:create_company', 'create_company entry', {'role': jwt_data.get('role')}, 'H3')
    # #endregion
    data = request.json or {}
    name = data.get("name", "").strip()
    if not name:
        return jsonify({"msg": "公司名称必填"}), 400

    # 检查名称是否已存在
    if Company.query.filter_by(name=name).first():
        return jsonify({"msg": "公司名称已存在"}), 400

    company = Company(
        name=name,
        contact_person=data.get("contact_person", "").strip() or None,
        contact_phone=data.get("contact_phone", "").strip() or None,
        address=data.get("address", "").strip() or None,
    )
    db.session.add(company)
    db.session.commit()

    return jsonify(
        {
            "id": company.id,
            "name": company.name,
            "contact_person": company.contact_person,
            "contact_phone": company.contact_phone,
            "address": company.address,
            "created_at": company.created_at.isoformat() if company.created_at else None,
        }
    ), 201


@companies_bp.put("/<int:company_id>")
@jwt_required()
@roles_required("superadmin", "admin")
def update_company(company_id):
    """更新客户公司信息（仅 superadmin/admin）"""
    # #region agent log
    jwt_data = get_jwt()
    log_debug('backend/app/routes/companies.py:update_company', 'update_company entry', {'company_id': company_id, 'role': jwt_data.get('role')}, 'H3')
    # #endregion
    company = Company.query.get_or_404(company_id)
    data = request.json or {}

    name = data.get("name", "").strip()
    if name and name != company.name:
        # 检查新名称是否已被其他公司使用
        if Company.query.filter(Company.name == name, Company.id != company_id).first():
            return jsonify({"msg": "公司名称已存在"}), 400
        company.name = name

    if "contact_person" in data:
        company.contact_person = data.get("contact_person", "").strip() or None
    if "contact_phone" in data:
        company.contact_phone = data.get("contact_phone", "").strip() or None
    if "address" in data:
        company.address = data.get("address", "").strip() or None

    db.session.commit()

    return jsonify(
        {
            "id": company.id,
            "name": company.name,
            "contact_person": company.contact_person,
            "contact_phone": company.contact_phone,
            "address": company.address,
            "created_at": company.created_at.isoformat() if company.created_at else None,
        }
    )


@companies_bp.delete("/<int:company_id>")
@jwt_required()
@roles_required("superadmin", "admin")
def delete_company(company_id):
    """删除客户公司（仅 superadmin/admin）"""
    # #region agent log
    jwt_data = get_jwt()
    log_debug('backend/app/routes/companies.py:delete_company', 'delete_company entry', {'company_id': company_id, 'role': jwt_data.get('role')}, 'H3')
    # #endregion
    company = Company.query.get_or_404(company_id)

    # 检查是否有关联的用户（customer 角色的用户）或订单
    from app.models.user import User
    customer_count = User.query.filter_by(company_id=company_id, role='customer').count()
    orders_count = company.orders.count()
    
    error_messages = []
    if customer_count > 0:
        error_messages.append(f"该客户公司下还有 {customer_count} 个客户账号")
    if orders_count > 0:
        error_messages.append(f"该客户公司下还有 {orders_count} 个订单")
    
    if error_messages:
        return jsonify({"msg": "无法删除：" + "，".join(error_messages)}), 400

    db.session.delete(company)
    db.session.commit()

    return jsonify({"msg": "删除成功"})
