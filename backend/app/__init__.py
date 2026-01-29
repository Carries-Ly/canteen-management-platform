from flask import Flask,jsonify
from .extensions import db, migrate, jwt
from .config import Config

# 导入所有模型，确保 Flask-Migrate 能识别
from .models import (
    User, Company, Order, OrderItem, Logistics, MealStandard,
    WeeklyMenu, WeeklyMenuItem, SubMenu, SubMenuItem,
    Ingredient, Inventory, StockIn, StockOut,
    PurchaseOrder, PurchaseOrderItem
)

from .routes.auth import auth_bp
from .routes.orders import orders_bp
from .routes.logistics import logistics_bp
from .routes.meal_standards import meal_standards_bp
from .routes.companies import companies_bp
from .routes.staff import staff_bp
from .routes.weekly_menu import weekly_menu_bp
from .routes.sub_menu import sub_menu_bp
from .routes.inventory import inventory_bp
from .routes.purchase_order import purchase_order_bp
from .routes.dishes import dishes_bp
# #region agent log
import json
import os
log_path = '/Users/c4rries/Desktop/贝晟/.cursor/debug.log'
def log_debug(location, message, data, hypothesis_id='ALL'):
    try:
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps({
                'sessionId': 'debug-session',
                'runId': 'post-fix',
                'hypothesisId': hypothesis_id,
                'location': location,
                'message': message,
                'data': data,
                'timestamp': int(__import__('time').time() * 1000)
            }, ensure_ascii=False) + '\n')
    except:
        pass
log_debug('backend/app/__init__.py:8', 'importing blueprints start', {})
# #endregion
from .routes.users import users_bp
# #region agent log
log_debug('backend/app/__init__.py:13', 'importing users_bp success', {'blueprint_name': users_bp.name if users_bp else None})
# #endregion


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # #region agent log
    log_debug('backend/app/__init__.py:create_app', 'create_app called', {})
    # #endregion

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # JWT 错误处理
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        # #region agent log
        log_debug('backend/app/__init__.py:expired_token', 'token expired', {'jwt_payload': jwt_payload}, 'H3')
        # #endregion
        return jsonify({"msg": "Token已过期，请重新登录"}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        # #region agent log
        log_debug('backend/app/__init__.py:invalid_token', 'invalid token', {'error': str(error)}, 'H3')
        # #endregion
        return jsonify({"msg": "Token无效，请重新登录"}), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        # #region agent log
        log_debug('backend/app/__init__.py:missing_token', 'missing token', {'error': str(error)}, 'H3')
        # #endregion
        return jsonify({"msg": "缺少Token，请先登录"}), 401

    # #region agent log
    log_debug('backend/app/__init__.py:create_app', 'JWT configured', {})
    # #endregion

    # 添加CORS支持（允许前端跨域请求）
    from flask_cors import CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(orders_bp, url_prefix="/api/orders")
    app.register_blueprint(logistics_bp, url_prefix="/api/logistics")
    app.register_blueprint(meal_standards_bp, url_prefix="/api/meal-standards")
    app.register_blueprint(companies_bp, url_prefix="/api/companies")
    app.register_blueprint(users_bp, url_prefix="/api/users")
    app.register_blueprint(staff_bp, url_prefix="/api/staff")
    app.register_blueprint(weekly_menu_bp, url_prefix="/api/weekly-menus")
    app.register_blueprint(sub_menu_bp, url_prefix="/api/sub-menus")
    app.register_blueprint(inventory_bp, url_prefix="/api/inventory")
    app.register_blueprint(purchase_order_bp, url_prefix="/api/purchase-orders")
    app.register_blueprint(dishes_bp, url_prefix="/api/dishes")

    # 全局错误处理
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"msg": "资源不存在"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        # #region agent log
        log_debug('backend/app/__init__.py:internal_error', 'internal server error', {'error': str(error)}, 'H5')
        # #endregion
        return jsonify({"msg": "服务器内部错误"}), 500

    @app.errorhandler(Exception)
    def handle_exception(e):
        # #region agent log
        log_debug('backend/app/__init__.py:handle_exception', 'unhandled exception', {'error': str(e), 'type': type(e).__name__}, 'H5')
        # #endregion
        return jsonify({"msg": f"错误: {str(e)}"}), 500

    # #region agent log
    log_debug('backend/app/__init__.py:create_app', 'create_app completed', {})
    # #endregion

    return app
