from datetime import datetime
from collections import defaultdict

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt
from sqlalchemy import func, and_

from app.extensions import db
from app.models.logistics import Logistics
from app.models.order import Order, OrderItem
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


logistics_bp = Blueprint("logistics", __name__)


@logistics_bp.get("")
@jwt_required()
def list_logistics():
    # #region agent log
    jwt_data = get_jwt()
    log_debug('backend/app/routes/logistics.py:list_logistics', 'list_logistics entry', {'role': jwt_data.get('role'), 'company_id': jwt_data.get('company_id')}, 'H3')
    # #endregion
    role = jwt_data.get("role")
    company_id = jwt_data.get("company_id")
    order_date = request.args.get("order_date")
    meal_type = request.args.get("meal_type")
    
    # 构建查询
    q = Logistics.query.join(Order).join(Company)
    
    # customer 角色只能查看本企业的物流信息
    if role == "customer" and company_id:
        q = q.filter(Order.company_id == company_id)
    
    if order_date:
        q = q.filter(Order.order_date == order_date)
    
    rows = q.all()
    
    # 如果需要按meal_type筛选，需要检查订单明细
    if meal_type:
        filtered_order_ids = set()
        for lg in rows:
            order = lg.order
            # 检查订单中是否有指定meal_type的明细
            has_meal_type = OrderItem.query.filter_by(
                order_id=order.id,
                meal_type=meal_type
            ).first() is not None
            if has_meal_type:
                filtered_order_ids.add(order.id)
        rows = [lg for lg in rows if lg.order_id in filtered_order_ids]
    
    data = []
    for lg in rows:
        o = lg.order
        # 获取订单的所有餐别（用于显示）
        meal_types = [item.meal_type for item in o.items.all()]
        data.append(
            {
                "order_id": o.id,
                "company_id": o.company_id,
                "company_name": o.company.name if o.company else None,
                "order_date": o.order_date.isoformat(),
                "meal_types": list(set(meal_types)),  # 去重
                "stage_prepare_loaded": lg.stage_prepare_loaded or False,
                "time_prepare_loaded": lg.time_prepare_loaded.isoformat() if lg.time_prepare_loaded else None,
                "stage_shipping": lg.stage_shipping or False,
                "time_shipping": lg.time_shipping.isoformat() if lg.time_shipping else None,
                "stage_arrived": lg.stage_arrived or False,
                "time_arrived": lg.time_arrived.isoformat() if lg.time_arrived else None,
                "stage_recycled": lg.stage_recycled or False,
                "time_recycled": lg.time_recycled.isoformat() if lg.time_recycled else None,
            }
        )
    return jsonify(data)


@logistics_bp.get("/statistics")
@jwt_required()
def get_statistics():
    """获取物流统计（某天某餐的四种状态的订单完成数量）"""
    # #region agent log
    jwt_data = get_jwt()
    log_debug('backend/app/routes/logistics.py:get_statistics', 'get_statistics entry', {'role': jwt_data.get('role')}, 'H1')
    # #endregion
    role = jwt_data.get("role")
    company_id = jwt_data.get("company_id")
    order_date = request.args.get("order_date")
    meal_type = request.args.get("meal_type")

    if not order_date or not meal_type:
        return jsonify({"msg": "日期和餐别参数必填"}), 400
    
    # 构建查询：找到指定日期和餐别的所有订单
    orders_query = Order.query.join(OrderItem).filter(
        Order.order_date == order_date,
        OrderItem.meal_type == meal_type
    )
    
    # customer 角色只能查看本企业
    if role == "customer" and company_id:
        orders_query = orders_query.filter(Order.company_id == company_id)
    
    orders = orders_query.all()
    order_ids = [o.id for o in orders]
    
    # 统计各阶段的完成数量（统计当前处于该状态的订单，而不是经过该状态的订单）
    # 逻辑：每个订单只统计在它当前最高阶段，不会重复统计
    logistics_list = Logistics.query.filter(Logistics.order_id.in_(order_ids)).all() if order_ids else []
    
    stats = {
        "prepare_loaded": 0,
        "shipping": 0,
        "arrived": 0,
        "recycled": 0,
    }
    
    for lg in logistics_list:
        # 按优先级统计：一个订单只会在它当前的最高阶段被统计一次
        # 例如：如果订单已完成recycled，只统计在recycled，不会统计在arrived/shipping/prepare_loaded
        if lg.stage_recycled:
            stats["recycled"] += 1
        elif lg.stage_arrived:
            stats["arrived"] += 1
        elif lg.stage_shipping:
            stats["shipping"] += 1
        elif lg.stage_prepare_loaded:
            stats["prepare_loaded"] += 1
    
    # #region agent log
    log_debug('backend/app/routes/logistics.py:get_statistics', 'get_statistics success', {'stats': stats, 'total_orders': len(order_ids)})
    # #endregion
    return jsonify(stats)


@logistics_bp.post("/<int:order_id>/update_stage")
@jwt_required()
def update_stage(order_id):
    # #region agent log
    jwt_data = get_jwt()
    log_debug('backend/app/routes/logistics.py:update_stage', 'update_stage entry', {'order_id': order_id, 'role': jwt_data.get('role')}, 'H3')
    # #endregion
    data = request.json or {}
    stage = data.get("stage")
    role = jwt_data.get("role")
    user_company_id = jwt_data.get("company_id")

    order = Order.query.get_or_404(order_id)
    
    # customer 角色不能操作物流阶段
    if role == "customer":
        return jsonify({"msg": "无权限"}), 403
    
    logistics = order.logistics
    if not logistics:
        logistics = Logistics(order_id=order.id)
        db.session.add(logistics)
        db.session.flush()

    now = datetime.now()
    
    # 检查阶段顺序（必须按顺序，不能跳过）
    can_update = False
    error_msg = ""
    
    if stage == "prepare_loaded":
        # 备餐装车是第一阶段，可以直接更新
        if logistics.stage_prepare_loaded:
            return jsonify({"msg": "该阶段已完成，无法再次更新"}), 400
        can_update = True
    elif stage == "shipping":
        # 运输中需要备餐装车已完成
        if logistics.stage_shipping:
            return jsonify({"msg": "该阶段已完成，无法再次更新"}), 400
        if logistics.stage_prepare_loaded:
            can_update = True
        else:
            error_msg = "备餐装车未完成，无法更新到运输中"
    elif stage == "arrived":
        # 已到达需要运输中已完成
        if logistics.stage_arrived:
            return jsonify({"msg": "该阶段已完成，无法再次更新"}), 400
        if logistics.stage_shipping:
            can_update = True
        else:
            error_msg = "运输中未完成，无法更新到已到达"
    elif stage == "recycled":
        # 已回收需要已到达已完成
        if logistics.stage_recycled:
            return jsonify({"msg": "该阶段已完成，无法再次更新"}), 400
        if logistics.stage_arrived:
            can_update = True
        else:
            error_msg = "已到达未完成，无法更新到已回收"
    else:
        return jsonify({"msg": "未知阶段"}), 400
    
    if not can_update:
        return jsonify({"msg": error_msg or "不能跳过阶段，请按顺序确认"}), 400

    # 更新阶段
    if stage == "prepare_loaded":
        if role not in ["admin", "superadmin"]:
            return jsonify({"msg": "无权限"}), 403
        if not logistics.stage_prepare_loaded:
            logistics.stage_prepare_loaded = True
            logistics.time_prepare_loaded = now
    elif stage == "shipping":
        if role not in ["admin", "superadmin"]:
            return jsonify({"msg": "无权限"}), 403
        if not logistics.stage_shipping:
            logistics.stage_shipping = True
            logistics.time_shipping = now
    elif stage == "arrived":
        if role not in ["admin", "superadmin", "user"]:
            return jsonify({"msg": "无权限"}), 403
        if not logistics.stage_arrived:
            logistics.stage_arrived = True
            logistics.time_arrived = now
    elif stage == "recycled":
        if role not in ["admin", "superadmin", "user"]:
            return jsonify({"msg": "无权限"}), 403
        if not logistics.stage_recycled:
            logistics.stage_recycled = True
            logistics.time_recycled = now

    db.session.commit()
    # #region agent log
    log_debug('backend/app/routes/logistics.py:update_stage', 'update_stage success', {'order_id': order_id, 'stage': stage})
    # #endregion
    return jsonify({"msg": "ok"})


@logistics_bp.post("/batch-update-stages")
@jwt_required()
def batch_update_stages():
    """批量更新物流阶段"""
    # #region agent log
    jwt_data = get_jwt()
    log_debug('backend/app/routes/logistics.py:batch_update_stages', 'batch_update_stages entry', {'role': jwt_data.get('role')}, 'H1')
    # #endregion
    role = jwt_data.get("role")
    data = request.json or {}
    updates = data.get("updates", [])  # [{order_id: 1, stage: "arrived"}, ...]
    
    if not updates:
        return jsonify({"msg": "没有要更新的记录"}), 400
    
    # customer 角色不能操作物流阶段
    if role == "customer":
        return jsonify({"msg": "无权限"}), 403
    
    now = datetime.now()
    stage_order = {
        "prepare_loaded": 1,
        "shipping": 2,
        "arrived": 3,
        "recycled": 4,
    }
    
    success_count = 0
    errors = []
    
    for item in updates:
        order_id = item.get("order_id")
        stage = item.get("stage")
        
        if not order_id or not stage:
            continue
        
        try:
            order = Order.query.get(order_id)
            if not order:
                errors.append(f"订单 {order_id} 不存在")
                continue
            
            logistics = order.logistics
            if not logistics:
                logistics = Logistics(order_id=order.id)
                db.session.add(logistics)
                db.session.flush()
            
            target_stage = stage_order.get(stage)
            if target_stage is None:
                errors.append(f"订单 {order_id}: 未知阶段 {stage}")
                continue
            
            # 检查权限
            if stage == "prepare_loaded" and role not in ["admin", "superadmin"]:
                errors.append(f"订单 {order_id}: 无权限操作该阶段")
                continue
            if stage == "shipping" and role not in ["admin", "superadmin"]:
                errors.append(f"订单 {order_id}: 无权限操作该阶段")
                continue
            if stage == "arrived" and role not in ["admin", "superadmin", "user"]:
                errors.append(f"订单 {order_id}: 无权限操作该阶段")
                continue
            if stage == "recycled" and role not in ["admin", "superadmin", "user"]:
                errors.append(f"订单 {order_id}: 无权限操作该阶段")
                continue
            
            # 检查阶段顺序（必须按顺序，不能跳过）
            # 检查前置阶段是否完成
            can_update = False
            
            # 如果阶段已完成，不能再次更新
            if stage == "prepare_loaded" and logistics.stage_prepare_loaded:
                continue  # 跳过，不添加到错误
            if stage == "shipping" and logistics.stage_shipping:
                continue
            if stage == "arrived" and logistics.stage_arrived:
                continue
            if stage == "recycled" and logistics.stage_recycled:
                continue
            
            if stage == "prepare_loaded":
                # 备餐装车是第一阶段，可以直接更新
                can_update = True
            elif stage == "shipping":
                # 运输中需要备餐装车已完成
                if logistics.stage_prepare_loaded:
                    can_update = True
                else:
                    errors.append(f"订单 {order_id}: 备餐装车未完成，无法更新到运输中")
            elif stage == "arrived":
                # 已到达需要运输中已完成
                if logistics.stage_shipping:
                    can_update = True
                else:
                    errors.append(f"订单 {order_id}: 运输中未完成，无法更新到已到达")
            elif stage == "recycled":
                # 已回收需要已到达已完成
                if logistics.stage_arrived:
                    can_update = True
                else:
                    errors.append(f"订单 {order_id}: 已到达未完成，无法更新到已回收")
            
            if not can_update:
                continue
            
            # 更新阶段（确保只更新一次）
            if stage == "prepare_loaded" and not logistics.stage_prepare_loaded and can_update:
                logistics.stage_prepare_loaded = True
                logistics.time_prepare_loaded = now
                success_count += 1
            elif stage == "shipping" and not logistics.stage_shipping and can_update:
                logistics.stage_shipping = True
                logistics.time_shipping = now
                success_count += 1
            elif stage == "arrived" and not logistics.stage_arrived and can_update:
                logistics.stage_arrived = True
                logistics.time_arrived = now
                success_count += 1
            elif stage == "recycled" and not logistics.stage_recycled and can_update:
                logistics.stage_recycled = True
                logistics.time_recycled = now
                success_count += 1
        except Exception as e:
            errors.append(f"订单 {order_id}: {str(e)}")
    
    db.session.commit()
    
    # #region agent log
    log_debug('backend/app/routes/logistics.py:batch_update_stages', 'batch_update_stages success', {'success_count': success_count, 'errors_count': len(errors)})
    # #endregion
    
    return jsonify({
        "msg": f"成功更新 {success_count} 条记录",
        "success_count": success_count,
        "errors": errors
    })
