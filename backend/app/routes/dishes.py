from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from .utils import roles_required

dishes_bp = Blueprint("dishes", __name__)


@dishes_bp.get("/search")
@jwt_required()
@roles_required("user", "admin", "superadmin")
def search_dishes():
    """
    菜品库模糊搜索（占位接口）

    你后续可以把这里替换为你现有的“模糊查询菜品并返回列表”的实现。

    建议接口：
    - GET /api/dishes/search?q=关键词
    返回：
    - { items: [{ id: string|number, name: string }] }
    """
    q = (request.args.get("q") or "").strip()

    # TODO: 在这里接入你现有的菜品库模糊查询方法
    # 下面仅提供一个占位返回，保证前端联调不报错
    if not q:
        return jsonify({"items": []})

    # 简单占位：回显输入关键词
    return jsonify(
        {
            "items": [
                {"id": f"mock-{q}-1", "name": f"{q}（占位结果1）"},
                {"id": f"mock-{q}-2", "name": f"{q}（占位结果2）"},
            ]
        }
    )

