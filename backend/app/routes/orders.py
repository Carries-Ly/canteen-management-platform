from datetime import datetime
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

from app.extensions import db
from app.models.company import Company
from app.models.meal_standard import MealStandard
from app.models.order import Order, OrderItem
from app.models.logistics import Logistics

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


orders_bp = Blueprint("orders", __name__)


@orders_bp.get("")
@jwt_required()
def list_orders():
    # 从 additional_claims 中获取用户信息
    jwt_data = get_jwt()
    role = jwt_data.get("role")
    company_id = jwt_data.get("company_id")
    # #region agent log
    log_debug('backend/app/routes/orders.py:list_orders', 'list_orders entry', {'role': role, 'company_id': company_id}, 'H3')
    # #endregion

    q = Order.query.join(Company)

    # 客户公司只能看自己的订单
    if role == "customer" and company_id:
        q = q.filter(Order.company_id == company_id)

    order_date = request.args.get("order_date")
    if order_date:
        q = q.filter(Order.order_date == order_date)

    # 搜索公司名称
    company_keyword = request.args.get("company_keyword", "").strip()
    if company_keyword:
        q = q.filter(Company.name.like(f"%{company_keyword}%"))

    status = request.args.get("status")
    if status:
        q = q.filter(Order.status == status)

    rows = q.order_by(Order.order_date.desc(), Order.id.desc()).all()
    data = []
    for o in rows:
        # 获取订单的所有明细项（现在一个订单只有一个餐别）
        items = []
        meal_types = set()
        for item in o.items.all():
            items.append({
                "id": item.id,
                "meal_name": item.meal_name,
                "meal_type": item.meal_type,
                "unit_price": item.unit_price,
                "quantity": item.quantity,
            })
            meal_types.add(item.meal_type)
        
        # 获取主要餐别（用于显示，现在应该只有一个）
        primary_meal_type = list(meal_types)[0] if meal_types else None
        
        # 获取物流状态
        logistics = o.logistics
        current_stage = None
        if logistics:
            if logistics.stage_recycled:
                current_stage = "recycled"
            elif logistics.stage_arrived:
                current_stage = "arrived"
            elif logistics.stage_shipping:
                current_stage = "shipping"
            elif logistics.stage_prepare_loaded:
                current_stage = "prepare_loaded"
        
        # 计算总份数和总金额
        total_quantity = sum(item.quantity for item in o.items.all())
        total_amount = sum(item.unit_price * item.quantity for item in o.items.all())
        
        data.append(
            {
                "id": o.id,
                "company_id": o.company_id,
                "company_name": o.company.name if o.company else None,
                "order_date": o.order_date.isoformat(),
                "status": o.status,
                "items": items,
                "meal_type": primary_meal_type,  # 添加主要餐别字段
                "total_quantity": total_quantity,
                "total_amount": total_amount,
                "current_stage": current_stage,
                "created_at": o.created_at.isoformat() if o.created_at else None,
            }
        )
    return jsonify(data)


@orders_bp.post("")
@jwt_required()
def create_order():
    # 从 additional_claims 中获取用户信息
    jwt_data = get_jwt()
    role = jwt_data.get("role")
    company_id = jwt_data.get("company_id")

    if role != "customer" or not company_id:
        return jsonify({"msg": "仅客户公司可创建订单"}), 403

    data = request.json or {}
    order_date = data.get("order_date")
    items = data.get("items", [])

    if not order_date or not items:
        return jsonify({"msg": "订单日期和明细必填"}), 400

    # 按餐别分组，每个餐别创建一个独立的订单
    orders_by_meal_type = {}
    created_order_ids = []
    
    for row in items:
        ms_id = row.get("meal_standard_id")
        qty = row.get("quantity")
        meal_type = row.get("meal_type")  # 必须传入餐别
        if not ms_id or not qty or not meal_type:
            continue
        ms = MealStandard.query.get(ms_id)
        if not ms or ms.status != "enabled":
            continue
        
        # 按餐别分组
        if meal_type not in orders_by_meal_type:
            # 为每个餐别创建新订单
            order = Order(company_id=company_id, order_date=order_date, status="已提交，等待确认")
            db.session.add(order)
            db.session.flush()
            orders_by_meal_type[meal_type] = {
                "order": order,
                "items": []
            }
            created_order_ids.append(order.id)
            # 初始化物流记录
            lg = Logistics(order_id=order.id)
            db.session.add(lg)
        
        # 添加明细项到对应餐别的订单
        item = OrderItem(
            order_id=orders_by_meal_type[meal_type]["order"].id,
            meal_standard_id=ms.id,
            meal_name=ms.name,
            meal_type=meal_type,
            unit_price=row.get("unit_price", ms.price),
            quantity=qty,
        )
        db.session.add(item)
        orders_by_meal_type[meal_type]["items"].append(item)

    if not created_order_ids:
        return jsonify({"msg": "没有有效的订单明细"}), 400

    db.session.commit()
    return jsonify({"ids": created_order_ids, "count": len(created_order_ids)}), 201


@orders_bp.get("/<int:order_id>")
@jwt_required()
def order_detail(order_id):
    # 从 additional_claims 中获取用户信息
    jwt_data = get_jwt()
    role = jwt_data.get("role")
    user_company_id = jwt_data.get("company_id")

    o = Order.query.get_or_404(order_id)
    if role == "customer" and user_company_id and o.company_id != user_company_id:
        return jsonify({"msg": "无权限"}), 403

    items = [
        {
            "id": it.id,
            "meal_name": it.meal_name,
            "meal_type": it.meal_type,
            "unit_price": it.unit_price,
            "quantity": it.quantity,
        }
        for it in o.items
    ]
    lg = o.logistics
    logistics = None
    if lg:
        logistics = {
            "stage_prepare_loaded": lg.stage_prepare_loaded,
            "time_prepare_loaded": lg.time_prepare_loaded.isoformat() if lg.time_prepare_loaded else None,
            "stage_shipping": lg.stage_shipping,
            "time_shipping": lg.time_shipping.isoformat() if lg.time_shipping else None,
            "stage_arrived": lg.stage_arrived,
            "time_arrived": lg.time_arrived.isoformat() if lg.time_arrived else None,
            "stage_recycled": lg.stage_recycled,
            "time_recycled": lg.time_recycled.isoformat() if lg.time_recycled else None,
        }

    total_quantity = sum(item.quantity for item in o.items)
    total_amount = sum(item.unit_price * item.quantity for item in o.items)

    return jsonify(
        {
            "id": o.id,
            "company_id": o.company_id,
            "company_name": o.company.name if o.company else None,
            "order_date": o.order_date.isoformat(),
            "status": o.status,
            "items": items,
            "total_quantity": total_quantity,
            "total_amount": total_amount,
            "logistics": logistics,
        }
    )


@orders_bp.put("/<int:order_id>")
@jwt_required()
def update_order(order_id):
    """更新订单（仅 admin/superadmin）"""
    from .utils import roles_required
    # #region agent log
    jwt_data = get_jwt()
    log_debug('backend/app/routes/orders.py:update_order', 'update_order entry', {'order_id': order_id, 'role': jwt_data.get('role')}, 'H1')
    # #endregion
    
    # 检查权限
    try:
        from flask_jwt_extended import verify_jwt_in_request
        verify_jwt_in_request()
        role = jwt_data.get("role")
        if role not in ["admin", "superadmin"]:
            return jsonify({"msg": "无权限"}), 403
    except:
        return jsonify({"msg": "无权限"}), 403

    o = Order.query.get_or_404(order_id)
    data = request.json or {}

    # 更新状态
    if "status" in data:
        o.status = data["status"]

    # 更新明细项（如果提供）
    if "items" in data:
        # 删除旧明细
        for item in o.items.all():
            db.session.delete(item)
        
        # 添加新明细
        for row in data["items"]:
            ms_id = row.get("meal_standard_id")
            qty = row.get("quantity")
            meal_type = row.get("meal_type")
            if not ms_id or not qty:
                continue
            ms = MealStandard.query.get(ms_id)
            if not ms:
                continue
            item_meal_type = meal_type if meal_type else ms.meal_type
            item = OrderItem(
                order_id=o.id,
                meal_standard_id=ms.id,
                meal_name=ms.name,
                meal_type=item_meal_type,
                unit_price=row.get("unit_price", ms.price),
                quantity=qty,
            )
            db.session.add(item)

    db.session.commit()
    # #region agent log
    log_debug('backend/app/routes/orders.py:update_order', 'update_order success', {'order_id': order_id})
    # #endregion
    return jsonify({"msg": "更新成功"})


@orders_bp.delete("/<int:order_id>")
@jwt_required()
def delete_order(order_id):
    """删除订单（仅 admin/superadmin）"""
    # #region agent log
    jwt_data = get_jwt()
    log_debug('backend/app/routes/orders.py:delete_order', 'delete_order entry', {'order_id': order_id, 'role': jwt_data.get('role')}, 'H1')
    # #endregion
    
    # 检查权限
    try:
        from flask_jwt_extended import verify_jwt_in_request
        verify_jwt_in_request()
        role = jwt_data.get("role")
        if role not in ["admin", "superadmin"]:
            return jsonify({"msg": "无权限"}), 403
    except:
        return jsonify({"msg": "无权限"}), 403

    o = Order.query.get_or_404(order_id)
    
    # 删除物流记录
    if o.logistics:
        db.session.delete(o.logistics)
    
    # 删除订单（明细会通过级联删除）
    db.session.delete(o)
    db.session.commit()
    
    # #region agent log
    log_debug('backend/app/routes/orders.py:delete_order', 'delete_order success', {'order_id': order_id})
    # #endregion
    return jsonify({"msg": "删除成功"})


@orders_bp.post("/<int:order_id>/confirm")
@jwt_required()
def confirm_order(order_id):
    """确认接收订单（将状态从"已提交，等待确认"改为"订餐已收到"，并自动创建物流记录为"备餐装车中"状态）"""
    # #region agent log
    jwt_data = get_jwt()
    log_debug('backend/app/routes/orders.py:confirm_order', 'confirm_order entry', {'order_id': order_id, 'role': jwt_data.get('role')}, 'H1')
    # #endregion
    
    role = jwt_data.get("role")
    # user/admin/superadmin 可以确认订单
    if role not in ["user", "admin", "superadmin"]:
        return jsonify({"msg": "无权限"}), 403

    o = Order.query.get_or_404(order_id)
    
    if o.status != "已提交，等待确认":
        return jsonify({"msg": "订单状态不正确，无法确认"}), 400
    
    # 更新订单状态
    o.status = "订餐已收到"
    
    # 创建或更新物流记录，设置为"备餐装车中"状态
    logistics = o.logistics
    if not logistics:
        # 如果物流记录不存在，创建新的
        logistics = Logistics(order_id=o.id)
        db.session.add(logistics)
        db.session.flush()
    
    # 设置备餐装车中状态（如果还没设置）
    if not logistics.stage_prepare_loaded:
        logistics.stage_prepare_loaded = True
        logistics.time_prepare_loaded = datetime.now()
    
    db.session.commit()
    
    # #region agent log
    log_debug('backend/app/routes/orders.py:confirm_order', 'confirm_order success', {'order_id': order_id, 'logistics_created': logistics.stage_prepare_loaded})
    # #endregion
    return jsonify({"msg": "确认成功"})


@orders_bp.post("/batch-confirm")
@jwt_required()
def batch_confirm_orders():
    """批量确认接收订单（自动创建物流记录为"备餐装车中"状态）"""
    # #region agent log
    jwt_data = get_jwt()
    log_debug('backend/app/routes/orders.py:batch_confirm_orders', 'batch_confirm_orders entry', {'role': jwt_data.get('role')}, 'H1')
    # #endregion
    
    role = jwt_data.get("role")
    # user/admin/superadmin 可以确认订单
    if role not in ["user", "admin", "superadmin"]:
        return jsonify({"msg": "无权限"}), 403

    data = request.json or {}
    order_ids = data.get("order_ids", [])
    
    if not order_ids:
        return jsonify({"msg": "请选择要确认的订单"}), 400

    success_count = 0
    errors = []
    
    for order_id in order_ids:
        try:
            o = Order.query.get(order_id)
            if not o:
                errors.append(f"订单 {order_id} 不存在")
                continue
            
            if o.status != "已提交，等待确认":
                errors.append(f"订单 {order_id} 状态不正确，无法确认")
                continue
            
            # 更新订单状态
            o.status = "订餐已收到"
            
            # 创建或更新物流记录，设置为"备餐装车中"状态
            logistics = o.logistics
            if not logistics:
                # 如果物流记录不存在，创建新的
                logistics = Logistics(order_id=o.id)
                db.session.add(logistics)
                db.session.flush()
            
            # 设置备餐装车中状态（如果还没设置）
            if not logistics.stage_prepare_loaded:
                logistics.stage_prepare_loaded = True
                logistics.time_prepare_loaded = datetime.now()
            
            success_count += 1
        except Exception as e:
            errors.append(f"订单 {order_id}: {str(e)}")
    
    db.session.commit()
    
    # #region agent log
    log_debug('backend/app/routes/orders.py:batch_confirm_orders', 'batch_confirm_orders success', {'success_count': success_count, 'errors_count': len(errors)})
    # #endregion
    
    return jsonify({
        "msg": f"成功确认 {success_count} 个订单",
        "success_count": success_count,
        "errors": errors
    })
