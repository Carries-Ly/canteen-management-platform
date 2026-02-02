from datetime import date
from app.extensions import db


class WeeklyMenu(db.Model):
    __tablename__ = "weekly_menus"

    id = db.Column(db.Integer, primary_key=True)
    week_year = db.Column(db.Integer, nullable=False)
    week_number = db.Column(db.Integer, nullable=False)  # 1-53
    week_start_date = db.Column(db.Date, nullable=False)  # 周一
    week_end_date = db.Column(db.Date, nullable=False)  # 周日
    status = db.Column(db.String(20), default="draft")  # draft/published
    generating_status = db.Column(db.String(20), default="idle")  # idle/generating/completed/failed
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    items = db.relationship("WeeklyMenuItem", back_populates="weekly_menu", lazy="dynamic", cascade="all, delete-orphan")
    sub_menus = db.relationship("SubMenu", back_populates="weekly_menu", lazy="dynamic")


class WeeklyMenuItem(db.Model):
    __tablename__ = "weekly_menu_items"

    id = db.Column(db.Integer, primary_key=True)
    weekly_menu_id = db.Column(db.Integer, db.ForeignKey("weekly_menus.id"), nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False)  # 1-7, 1=周一
    meal_type = db.Column(db.String(32), nullable=False)  # 早餐/午餐/晚餐/夜宵
    dish_name = db.Column(db.String(128), nullable=False)
    dish_category = db.Column(db.String(64))  # 可选：大荤一/大荤二/小荤一/小荤二/素菜一/素菜二/例汤
    sort_order = db.Column(db.Integer, default=0)  # 同一餐别内的排序

    weekly_menu = db.relationship("WeeklyMenu", back_populates="items")

