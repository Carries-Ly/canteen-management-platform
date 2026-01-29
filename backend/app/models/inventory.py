from datetime import date
from app.extensions import db


class Ingredient(db.Model):
    __tablename__ = "ingredients"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True, nullable=False)
    category = db.Column(db.String(64))  # 蔬菜/肉类/调料/主食等
    unit = db.Column(db.String(32), nullable=False)  # kg/斤/包/箱等
    safety_stock = db.Column(db.Float, default=0)  # 安全库存
    shelf_life_days = db.Column(db.Integer)  # 保质期天数（可选）

    inventory = db.relationship("Inventory", uselist=False, back_populates="ingredient", cascade="all, delete-orphan")
    stock_ins = db.relationship("StockIn", back_populates="ingredient", lazy="dynamic")
    stock_outs = db.relationship("StockOut", back_populates="ingredient", lazy="dynamic")
    purchase_order_items = db.relationship("PurchaseOrderItem", back_populates="ingredient", lazy="dynamic")


class Inventory(db.Model):
    __tablename__ = "inventories"

    id = db.Column(db.Integer, primary_key=True)
    ingredient_id = db.Column(db.Integer, db.ForeignKey("ingredients.id"), unique=True, nullable=False)
    quantity = db.Column(db.Float, default=0, nullable=False)  # 当前库存数量
    last_in_date = db.Column(db.Date)  # 最后入库日期
    last_out_date = db.Column(db.Date)  # 最后出库日期
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    ingredient = db.relationship("Ingredient", back_populates="inventory")


class StockIn(db.Model):
    __tablename__ = "stock_ins"

    id = db.Column(db.Integer, primary_key=True)
    ingredient_id = db.Column(db.Integer, db.ForeignKey("ingredients.id"), nullable=False)
    quantity = db.Column(db.Float, nullable=False)  # 入库数量
    in_date = db.Column(db.Date, nullable=False, default=date.today)
    expiry_date = db.Column(db.Date)  # 保质期到期日期（可选）
    operator_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    scale_weight = db.Column(db.Float)  # 电子秤称重值（用于核对）
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    ingredient = db.relationship("Ingredient", back_populates="stock_ins")
    operator = db.relationship("User")


class StockOut(db.Model):
    __tablename__ = "stock_outs"

    id = db.Column(db.Integer, primary_key=True)
    ingredient_id = db.Column(db.Integer, db.ForeignKey("ingredients.id"), nullable=False)
    quantity = db.Column(db.Float, nullable=False)  # 出库数量
    out_date = db.Column(db.Date, nullable=False, default=date.today)
    purchase_order_id = db.Column(db.Integer, db.ForeignKey("purchase_orders.id"), nullable=True)  # 关联的采购单ID（可选）
    purpose = db.Column(db.String(128))  # 出库用途（如：生产使用/损耗/退货等）
    operator_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    scale_weight = db.Column(db.Float)  # 电子秤称重值（用于核对）
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    ingredient = db.relationship("Ingredient", back_populates="stock_outs")
    operator = db.relationship("User")
    purchase_order = db.relationship("PurchaseOrder", back_populates="stock_outs")

