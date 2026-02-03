from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt
from sqlalchemy import and_

from app.extensions import db
from app.models.sub_menu import SubMenu, SubMenuItem
from app.models.weekly_menu import WeeklyMenu, WeeklyMenuItem
from app.models.company import Company
from .utils import roles_required


sub_menu_bp = Blueprint("sub_menu", __name__)


@sub_menu_bp.get("")
@jwt_required()
def list_sub_menus():
    """获取子菜单列表"""
    jwt_data = get_jwt()
    role = jwt_data.get("role")
    company_id = jwt_data.get("company_id")
    
    weekly_menu_id = request.args.get("weekly_menu_id", type=int)
    company_id_filter = request.args.get("company_id", type=int)
    
    q = SubMenu.query
    
    if weekly_menu_id:
        q = q.filter(SubMenu.weekly_menu_id == weekly_menu_id)
    
    # customer 只能查看本企业的子菜单
    if role == "customer":
        if company_id:
            q = q.filter(SubMenu.company_id == company_id)
        else:
            return jsonify([])
    elif company_id_filter:
        q = q.filter(SubMenu.company_id == company_id_filter)
    
    sub_menus = q.order_by(SubMenu.created_at.desc()).all()
    
    data = []
    for sub_menu in sub_menus:
        data.append({
            "id": sub_menu.id,
            "weekly_menu_id": sub_menu.weekly_menu_id,
            "company_id": sub_menu.company_id,
            "company_name": sub_menu.company.name if sub_menu.company else None,
            "name": sub_menu.name,
            "status": sub_menu.status,
            "created_by": sub_menu.created_by,
            "created_at": sub_menu.created_at.isoformat() if sub_menu.created_at else None,
        })
    
    return jsonify(data)


@sub_menu_bp.get("/<int:sub_menu_id>")
@jwt_required()
def get_sub_menu(sub_menu_id):
    """获取子菜单详情"""
    jwt_data = get_jwt()
    role = jwt_data.get("role")
    company_id = jwt_data.get("company_id")
    
    sub_menu = SubMenu.query.get_or_404(sub_menu_id)
    
    # customer 只能查看本企业的子菜单
    if role == "customer" and sub_menu.company_id != company_id:
        return jsonify({"msg": "无权限"}), 403
    
    items = sub_menu.items.order_by(
        SubMenuItem.day_of_week,
        SubMenuItem.meal_type
    ).all()
    
    items_data = []
    for item in items:
        items_data.append({
            "id": item.id,
            "day_of_week": item.day_of_week,
            "meal_type": item.meal_type,
            "dish_name": item.dish_name,
            "dish_category": item.dish_category,
        })
    
    return jsonify({
        "id": sub_menu.id,
        "weekly_menu_id": sub_menu.weekly_menu_id,
        "company_id": sub_menu.company_id,
        "company_name": sub_menu.company.name if sub_menu.company else None,
        "name": sub_menu.name,
        "status": sub_menu.status,
        "created_by": sub_menu.created_by,
        "created_at": sub_menu.created_at.isoformat() if sub_menu.created_at else None,
        "items": items_data,
    })


@sub_menu_bp.post("/select")
@jwt_required()
@roles_required("admin", "superadmin")
def select_sub_menu():
    """从总菜单中选择子菜单，关联到客户企业"""
    data = request.json or {}
    weekly_menu_id = data.get("weekly_menu_id")
    company_ids = data.get("company_ids", [])
    selected_items = data.get("selected_items", [])
    
    if not weekly_menu_id or not company_ids:
        return jsonify({"msg": "总菜单ID和客户企业ID必填"}), 400
    
    weekly_menu = WeeklyMenu.query.get_or_404(weekly_menu_id)
    jwt_data = get_jwt()
    user_id = jwt_data.get("sub")
    
    created_sub_menus = []
    
    for company_id in company_ids:
        # 检查公司是否存在
        company = Company.query.get(company_id)
        if not company:
            continue
        
        # 创建子菜单
        sub_menu = SubMenu(
            weekly_menu_id=weekly_menu_id,
            company_id=company_id,
            name=data.get("name") or f"{company.name}-第{weekly_menu.week_number}周菜单",
            status="confirmed",
            created_by=int(user_id) if user_id else None,
        )
        db.session.add(sub_menu)
        db.session.flush()
        
        # 保存子菜单明细
        for item_data in selected_items:
            # 如果提供了weekly_menu_item_id，使用它；否则直接使用提供的数据
            if "weekly_menu_item_id" in item_data:
                weekly_item = WeeklyMenuItem.query.get(item_data["weekly_menu_item_id"])
                if weekly_item:
                    sub_item = SubMenuItem(
                        sub_menu_id=sub_menu.id,
                        weekly_menu_item_id=weekly_item.id,
                        day_of_week=weekly_item.day_of_week,
                        meal_type=weekly_item.meal_type,
                        dish_name=weekly_item.dish_name,
                        dish_category=weekly_item.dish_category,
                    )
                else:
                    continue
            else:
                sub_item = SubMenuItem(
                    sub_menu_id=sub_menu.id,
                    day_of_week=item_data.get("day_of_week"),
                    meal_type=item_data.get("meal_type"),
                    dish_name=item_data.get("dish_name"),
                    dish_category=item_data.get("dish_category"),
                )
            db.session.add(sub_item)
        
        created_sub_menus.append(sub_menu.id)
    
    db.session.commit()
    
    return jsonify({
        "ids": created_sub_menus,
        "count": len(created_sub_menus),
        "msg": "子菜单创建成功",
    }), 201


@sub_menu_bp.get("/history")
@jwt_required()
def get_sub_menu_history():
    """获取历史子菜单"""
    jwt_data = get_jwt()
    role = jwt_data.get("role")
    company_id = jwt_data.get("company_id")
    
    company_id_filter = request.args.get("company_id", type=int)
    week_year = request.args.get("week_year", type=int)
    week_number = request.args.get("week_number", type=int)
    
    q = SubMenu.query.join(WeeklyMenu)
    
    # customer 只能查看本企业的历史
    if role == "customer":
        if company_id:
            q = q.filter(SubMenu.company_id == company_id)
        else:
            return jsonify([])
    elif company_id_filter:
        q = q.filter(SubMenu.company_id == company_id_filter)
    
    if week_year:
        q = q.filter(WeeklyMenu.week_year == week_year)
    
    if week_number:
        q = q.filter(WeeklyMenu.week_number == week_number)
    
    sub_menus = q.order_by(WeeklyMenu.week_year.desc(), WeeklyMenu.week_number.desc()).all()
    
    data = []
    for sub_menu in sub_menus:
        weekly_menu = sub_menu.weekly_menu
        data.append({
            "id": sub_menu.id,
            "weekly_menu_id": sub_menu.weekly_menu_id,
            "week_year": weekly_menu.week_year if weekly_menu else None,
            "week_number": weekly_menu.week_number if weekly_menu else None,
            "company_id": sub_menu.company_id,
            "company_name": sub_menu.company.name if sub_menu.company else None,
            "name": sub_menu.name,
            "status": sub_menu.status,
            "created_at": sub_menu.created_at.isoformat() if sub_menu.created_at else None,
        })
    
    return jsonify(data)

