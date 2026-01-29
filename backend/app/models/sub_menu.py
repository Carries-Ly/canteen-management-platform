from app.extensions import db


class SubMenu(db.Model):
    __tablename__ = "sub_menus"

    id = db.Column(db.Integer, primary_key=True)
    weekly_menu_id = db.Column(db.Integer, db.ForeignKey("weekly_menus.id"), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False)
    name = db.Column(db.String(128))  # 可选，如"公司A-第1周菜单"
    status = db.Column(db.String(20), default="draft")  # draft/confirmed
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    weekly_menu = db.relationship("WeeklyMenu", back_populates="sub_menus")
    company = db.relationship("Company")
    items = db.relationship("SubMenuItem", back_populates="sub_menu", lazy="dynamic", cascade="all, delete-orphan")


class SubMenuItem(db.Model):
    __tablename__ = "sub_menu_items"

    id = db.Column(db.Integer, primary_key=True)
    sub_menu_id = db.Column(db.Integer, db.ForeignKey("sub_menus.id"), nullable=False)
    weekly_menu_item_id = db.Column(db.Integer, db.ForeignKey("weekly_menu_items.id"), nullable=True)  # 关联总菜单明细
    day_of_week = db.Column(db.Integer, nullable=False)  # 1-7
    meal_type = db.Column(db.String(32), nullable=False)  # 早餐/午餐/晚餐/夜宵
    dish_name = db.Column(db.String(128), nullable=False)  # 快照
    dish_category = db.Column(db.String(64))  # 快照

    sub_menu = db.relationship("SubMenu", back_populates="items")
    weekly_menu_item = db.relationship("WeeklyMenuItem")

