from datetime import date
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt

from app.extensions import db
from app.models.inventory import Ingredient, Inventory, StockIn, StockOut
from .utils import roles_required


inventory_bp = Blueprint("inventory", __name__)


@inventory_bp.get("")
@jwt_required()
@roles_required("user", "admin", "superadmin")
def list_inventory():
    """获取库存列表"""
    keyword = request.args.get("keyword", "").strip()
    category = request.args.get("category", "").strip()
    
    q = Ingredient.query
    
    if keyword:
        q = q.filter(Ingredient.name.like(f"%{keyword}%"))
    if category:
        q = q.filter(Ingredient.category == category)
    
    ingredients = q.all()
    
    data = []
    for ing in ingredients:
        inv = ing.inventory
        data.append({
            "ingredient_id": ing.id,
            "ingredient_name": ing.name,
            "category": ing.category,
            "unit": ing.unit,
            "safety_stock": ing.safety_stock,
            "current_quantity": inv.quantity if inv else 0,
            "last_in_date": inv.last_in_date.isoformat() if inv and inv.last_in_date else None,
            "last_out_date": inv.last_out_date.isoformat() if inv and inv.last_out_date else None,
        })
    
    return jsonify(data)


@inventory_bp.post("/stock-in")
@jwt_required()
@roles_required("user", "admin", "superadmin")
def stock_in():
    """食材入库"""
    data = request.json or {}
    ingredient_id = data.get("ingredient_id")
    quantity = data.get("quantity")
    in_date = data.get("in_date")
    expiry_date = data.get("expiry_date")
    scale_weight = data.get("scale_weight")
    
    if not ingredient_id or not quantity:
        return jsonify({"msg": "食材ID和数量必填"}), 400
    
    ingredient = Ingredient.query.get_or_404(ingredient_id)
    jwt_data = get_jwt()
    operator_id = jwt_data.get("sub")
    
    # 创建入库记录
    stock_in = StockIn(
        ingredient_id=ingredient_id,
        quantity=float(quantity),
        in_date=date.fromisoformat(in_date) if in_date else date.today(),
        expiry_date=date.fromisoformat(expiry_date) if expiry_date else None,
        operator_id=int(operator_id) if operator_id else None,
        scale_weight=float(scale_weight) if scale_weight else None,
    )
    db.session.add(stock_in)
    
    # 更新或创建库存记录
    inv = ingredient.inventory
    if not inv:
        inv = Inventory(ingredient_id=ingredient_id, quantity=0)
        db.session.add(inv)
    
    inv.quantity += float(quantity)
    inv.last_in_date = stock_in.in_date
    db.session.flush()
    
    db.session.commit()
    
    return jsonify({"msg": "入库成功", "id": stock_in.id}), 201


@inventory_bp.post("/stock-out")
@jwt_required()
@roles_required("user", "admin", "superadmin")
def stock_out():
    """食材出库"""
    data = request.json or {}
    ingredient_id = data.get("ingredient_id")
    quantity = data.get("quantity")
    out_date = data.get("out_date")
    purchase_order_id = data.get("purchase_order_id")
    purpose = data.get("purpose")
    scale_weight = data.get("scale_weight")
    
    if not ingredient_id or not quantity:
        return jsonify({"msg": "食材ID和数量必填"}), 400
    
    ingredient = Ingredient.query.get_or_404(ingredient_id)
    inv = ingredient.inventory
    
    if not inv or inv.quantity < float(quantity):
        return jsonify({"msg": "库存不足"}), 400
    
    jwt_data = get_jwt()
    operator_id = jwt_data.get("sub")
    
    # 创建出库记录
    stock_out = StockOut(
        ingredient_id=ingredient_id,
        quantity=float(quantity),
        out_date=date.fromisoformat(out_date) if out_date else date.today(),
        purchase_order_id=purchase_order_id,
        purpose=purpose,
        operator_id=int(operator_id) if operator_id else None,
        scale_weight=float(scale_weight) if scale_weight else None,
    )
    db.session.add(stock_out)
    
    # 更新库存
    inv.quantity -= float(quantity)
    inv.last_out_date = stock_out.out_date
    db.session.flush()
    
    db.session.commit()
    
    return jsonify({"msg": "出库成功", "id": stock_out.id}), 201

