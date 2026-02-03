from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
import re
import pandas as pd
from .utils import roles_required
from app.utils.processMenu import read_menu_excel
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

    filepath = "app/data/new_meal_list.xls"  # 替换为您的Excel文件路径
    # 读取并处理Excel文件（返回的是 DataFrame，列名为 MultiIndex 如 ("菜名", "")）
    meal_list = read_menu_excel(filepath)

    matched_dishes = search_meal(q, meal_list)
    if matched_dishes is None:
        return jsonify({"items": []})
    return jsonify({"items": matched_dishes})


def search_meal(query, meal_df):
    """
    在菜品 DataFrame 的「菜名」列中模糊搜索，返回 [{ "id", "name" }]。
    meal_df 是 read_menu_excel 返回的 DataFrame，列名为 MultiIndex。
    """
    if meal_df is None or meal_df.empty:
        return []
    # 菜名列为 ("菜名", "")
    name_col = ("菜名", "")
    if name_col not in meal_df.columns:
        return []
    regex = re.compile(re.escape(query), re.IGNORECASE)
    items = []
    for idx, row in meal_df.iterrows():
        name = row.get(name_col)
        if pd.isna(name):
            continue
        name_str = str(name).strip()
        if not name_str or not regex.search(name_str):
            continue
        items.append({"id": int(idx) if isinstance(idx, (int, float)) else str(idx), "name": name_str})
    return items