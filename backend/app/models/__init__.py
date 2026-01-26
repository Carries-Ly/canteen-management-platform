"""
导入所有模型，确保 Flask-Migrate 能识别
"""
from app.models.user import User
from app.models.company import Company
from app.models.order import Order, OrderItem
from app.models.logistics import Logistics
from app.models.meal_standard import MealStandard

__all__ = ["User", "Company", "Order", "OrderItem", "Logistics", "MealStandard"]
