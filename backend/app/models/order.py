from datetime import date

from app.extensions import db


class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False)
    order_date = db.Column(db.Date, default=date.today, nullable=False)
    status = db.Column(db.String(20), default="submitted")  # submitted/closed
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    company = db.relationship("Company", back_populates="orders")
    items = db.relationship("OrderItem", back_populates="order", lazy="dynamic", cascade="all, delete-orphan")
    logistics = db.relationship("Logistics", uselist=False, back_populates="order")


class OrderItem(db.Model):
    __tablename__ = "order_items"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    meal_standard_id = db.Column(db.Integer, db.ForeignKey("meal_standards.id"))
    meal_name = db.Column(db.String(128), nullable=False)
    meal_type = db.Column(db.String(32), nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    order = db.relationship("Order", back_populates="items")
    meal_standard = db.relationship("MealStandard")
