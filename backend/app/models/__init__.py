"""
导入所有模型，确保 Flask-Migrate 能识别
"""
from app.models.user import User
from app.models.company import Company
from app.models.order import Order, OrderItem
from app.models.logistics import Logistics
from app.models.meal_standard import MealStandard
from app.models.weekly_menu import WeeklyMenu, WeeklyMenuItem
from app.models.sub_menu import SubMenu, SubMenuItem
from app.models.inventory import Ingredient, Inventory, StockIn, StockOut
from app.models.purchase_order import PurchaseOrder, PurchaseOrderItem

__all__ = [
    "User", "Company", "Order", "OrderItem", "Logistics", "MealStandard",
    "WeeklyMenu", "WeeklyMenuItem", "SubMenu", "SubMenuItem",
    "Ingredient", "Inventory", "StockIn", "StockOut",
    "PurchaseOrder", "PurchaseOrderItem"
]
