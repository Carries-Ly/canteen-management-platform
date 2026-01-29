from app.extensions import db


class PurchaseOrder(db.Model):
    __tablename__ = "purchase_orders"

    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(64), unique=True, nullable=False)  # 采购单号（自动生成）
    sub_menu_id = db.Column(db.Integer, db.ForeignKey("sub_menus.id"), nullable=True)  # 关联的子菜单ID（可选）
    total_amount = db.Column(db.Float, default=0)  # 预估总金额
    status = db.Column(db.String(20), default="draft")  # draft/confirmed/purchased
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    items = db.relationship("PurchaseOrderItem", back_populates="purchase_order", lazy="dynamic", cascade="all, delete-orphan")
    stock_outs = db.relationship("StockOut", back_populates="purchase_order", lazy="dynamic")
    sub_menu = db.relationship("SubMenu")


class PurchaseOrderItem(db.Model):
    __tablename__ = "purchase_order_items"

    id = db.Column(db.Integer, primary_key=True)
    purchase_order_id = db.Column(db.Integer, db.ForeignKey("purchase_orders.id"), nullable=False)
    ingredient_id = db.Column(db.Integer, db.ForeignKey("ingredients.id"), nullable=False)
    required_quantity = db.Column(db.Float, nullable=False)  # 所需数量（根据菜单计算）
    stock_quantity = db.Column(db.Float, default=0)  # 当前库存数量（快照）
    use_stock = db.Column(db.Boolean, default=False)  # 是否使用库存（布尔）
    purchase_quantity = db.Column(db.Float, nullable=False)  # 实际采购数量
    unit_price = db.Column(db.Float, nullable=False)  # 单价（快照）
    subtotal = db.Column(db.Float, default=0)  # 小计金额

    purchase_order = db.relationship("PurchaseOrder", back_populates="items")
    ingredient = db.relationship("Ingredient", back_populates="purchase_order_items")

