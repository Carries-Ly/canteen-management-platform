import uuid
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt

from app.extensions import db
from app.models.purchase_order import PurchaseOrder, PurchaseOrderItem
from app.models.inventory import Ingredient, Inventory
from .utils import roles_required


purchase_order_bp = Blueprint("purchase_order", __name__)


@purchase_order_bp.get("")
@jwt_required()
@roles_required("user", "admin", "superadmin")
def list_purchase_orders():
    """获取采购单列表"""
    status = request.args.get("status", "").strip()
    
    q = PurchaseOrder.query
    
    if status:
        q = q.filter(PurchaseOrder.status == status)
    
    orders = q.order_by(PurchaseOrder.created_at.desc()).all()
    
    data = []
    for order in orders:
        data.append({
            "id": order.id,
            "order_number": order.order_number,
            "sub_menu_id": order.sub_menu_id,
            "total_amount": order.total_amount,
            "status": order.status,
            "created_by": order.created_by,
            "created_at": order.created_at.isoformat() if order.created_at else None,
        })
    
    return jsonify(data)


@purchase_order_bp.post("")
@jwt_required()
@roles_required("user", "admin", "superadmin")
def create_purchase_order():
    """创建采购单"""
    data = request.json or {}
    items = data.get("items", [])
    sub_menu_id = data.get("sub_menu_id")
    
    if not items:
        return jsonify({"msg": "采购明细不能为空"}), 400
    
    jwt_data = get_jwt()
    user_id = jwt_data.get("sub")
    
    # 生成采购单号
    order_number = f"PO-{uuid.uuid4().hex[:8].upper()}"
    
    purchase_order = PurchaseOrder(
        order_number=order_number,
        sub_menu_id=sub_menu_id,
        status="draft",
        created_by=int(user_id) if user_id else None,
    )
    db.session.add(purchase_order)
    db.session.flush()
    
    total_amount = 0
    
    for item_data in items:
        ingredient_id = item_data.get("ingredient_id")
        purchase_quantity = item_data.get("purchase_quantity", 0)
        unit_price = item_data.get("unit_price", 0)
        
        if not ingredient_id:
            continue
        
        ingredient = Ingredient.query.get(ingredient_id)
        if not ingredient:
            continue
        
        # 获取当前库存（快照）
        inv = ingredient.inventory
        stock_quantity = inv.quantity if inv else 0
        
        subtotal = float(purchase_quantity) * float(unit_price)
        total_amount += subtotal
        
        order_item = PurchaseOrderItem(
            purchase_order_id=purchase_order.id,
            ingredient_id=ingredient_id,
            required_quantity=float(item_data.get("required_quantity", 0)),
            stock_quantity=stock_quantity,
            use_stock=bool(item_data.get("use_stock", False)),
            purchase_quantity=float(purchase_quantity),
            unit_price=float(unit_price),
            subtotal=subtotal,
        )
        db.session.add(order_item)
    
    purchase_order.total_amount = total_amount
    db.session.commit()
    
    return jsonify({
        "id": purchase_order.id,
        "order_number": purchase_order.order_number,
        "msg": "采购单创建成功",
    }), 201

