from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt
from sqlalchemy import and_
import threading

from app.extensions import db
from app.models.weekly_menu import WeeklyMenu, WeeklyMenuItem
from app.models.user import User
from .utils import roles_required
from app.utils.processMenu import get_result


weekly_menu_bp = Blueprint("weekly_menu", __name__)


def generate_weekly_menu_data(week_year: int, week_number: int):
    """
    生成一周总菜单（模拟方法）
    返回格式：
    result = [
        [  # 大荤
            [  # 周一
                ["家常鸡块", "香菇百叶包", "酱鸭胸"],  # 午餐：大荤一、大荤二、大荤三
                ["家常鸭块", "毛豆萝卜炖小排"]  # 晚餐：大荤一、大荤二
            ],
            [  # 周二
                ["蚝油牛肉", "香菇山药炖蹄膀", "玉米虾仁"],  # 午餐
                ["玉米炖肋排", "白斩鸡"]  # 晚餐
            ],
            ...  # 周三到周日
        ],
        [  # 小荤
            [  # 周一
                ["西红柿炒蛋", "青豆玉米方腿丁"],  # 午餐：小荤一、小荤二
                ["香干茭白肉丁", "茄子肉丝"]  # 晚餐：小荤一、小荤二
            ],
            ...  # 周二到周日
        ],
        [  # 素菜
            [  # 周一
                ["干丝白菜", "葱油萝卜丝"],  # 午餐：素菜一、素菜二
                ["面筋青菜", "木耳冬瓜"]  # 晚餐：素菜一、素菜二
            ],
            ...  # 周二到周日
        ],
        [  # 例汤
            [  # 周一
                ["雪菜豆腐汤"],  # 午餐：例汤
                ["油豆腐粉丝汤"]  # 晚餐：例汤
            ],
            ...  # 周二到周日
        ],
    ]
    数据结构说明：
    - 第一层：4个元素，分别代表大荤、小荤、素菜、例汤
    - 第二层：7个元素，分别代表周一到周日
    - 第三层：2个元素，分别代表午餐和晚餐
    - 第四层：根据菜品类型和用餐时间不同，数量不同
      * 大荤午餐：3个元素（大荤一、大荤二、大荤三）
      * 大荤晚餐：2个元素（大荤一、大荤二）
      * 小荤午餐/晚餐：2个元素（小荤一、小荤二）
      * 素菜午餐/晚餐：2个元素（素菜一、素菜二）
      * 例汤午餐/晚餐：1个元素（例汤）
    """
    # 这里是模拟数据，实际应该调用已有的菜单生成算法
    # result = [
    #     [  # 大荤
    #         [["家常鸡块", "香菇百叶包", "酱鸭胸"], ["家常鸭块", "毛豆萝卜炖小排"]],
    #         [["蚝油牛肉", "香菇山药炖蹄膀", "玉米虾仁"], ["玉米炖肋排", "白斩鸡"]],
    #         [["面拖大排", "家常鸭翅根", "家常鲳鱼"], ["如意蛋卷", "油爆基围虾"]],
    #         [["香菇鸡片", "马蹄肉圆", "红烧鸭腿"], ["水煮牛柳", "枸杞鲜笋炖蹄膀"]],
    #         [["剁椒鱼块", "花生肉丁", "家常翅根"], ["芋艿烧肉", "咖喱鸡翅"]],
    #         [["盐水鸭翅", "香菇咸肉煮百叶", "黄豆猪手"], ["酱汁大排", "全家福"]],
    #         [["干烧鸡腿", "水笋烤肉", "梅菜烧肉"], ["酸菜回锅肉", "烤鸭"]],
    #     ],
    #     [  # 小荤
    #         [["西红柿炒蛋", "青豆玉米方腿丁"], ["香干茭白肉丁", "茄子肉丝"]],
    #         [["南瓜毛豆咸肉丁", "西芹方腿"], ["咸鱼炖蛋", "莴笋炒腊肉"]],
    #         [["肉糜粉丝", "鸡丝云丝"], ["三色云丝", "大蒜炒腊肉"]],
    #         [["西葫芦炒蛋", "黄瓜方腿丁"], ["开洋炖蛋", "芹菜香干肉丝"]],
    #         [["毛豆南瓜肉片", "豇豆鸡丝"], ["莴笋香干鸡丝", "家常素鸡"]],
    #         [["青椒银芽鸡丝", "木耳咸肉冬瓜片"], ["红椒莴笋鸡片", "榨菜毛豆肉丝"]],
    #         [["香莴笋炒蛋", "咸肉香菇煮百叶"], ["花菜木耳鸡片", "莲藕咸肉丁"]],
    #     ],
    #     [  # 素菜
    #         [["干丝白菜", "葱油萝卜丝"], ["面筋青菜", "木耳冬瓜"]],
    #         [["葱油海带丝", "姜汁菠菜"], ["清炒空心菜", "芹菜海带丝"]],
    #         [["炒青菜", "蒜叶萝卜"], ["葱油佛手瓜", "香菇青菜"]],
    #         [["青菜豆腐", "香干银芽"], ["麻油生菜", "雪菜百叶丝"]],
    #         [["青椒藕片", "面筋白菜"], ["青菜油豆腐", "青椒土豆丝"]],
    #         [["木耳花菜", "油豆腐白菜"], ["青菜百叶丝", "芹菜银芽"]],
    #         [["韭菜银芽", "番茄卷心菜"], ["红烧慈菇", "青菜腐竹"]],
    #     ],
    #     [  # 例汤
    #         [["雪菜豆腐汤"], ["油豆腐粉丝汤"]],
    #         [["萝卜鸡块汤"], ["土豆牛肉羹"]],
    #         [["蘑菇肉丝蛋汤"], ["西红柿蛋汤"]],
    #         [["酸辣汤"], ["紫菜冬瓜汤"]],
    #         [["扁尖冬瓜汤"], ["番茄蛋汤"]],
    #         [["紫菜蛋汤"], ["咸肉冬瓜汤"]],
    #         [["香菇肉丝冬瓜汤"], ["香菇肉丝豆腐羹"]],
    #     ],
    # ]
    # 尝试调用实际算法
    try:
        res = get_result()
        if res is not None:
            return res
    except Exception as e:
        print(f"菜单生成算法调用失败: {e}")
    
    # return result

def calculate_week_dates(week_year: int, week_number: int):
    """计算指定周的开始日期（周一）和结束日期（周日）"""
    # 使用ISO周数计算
    from datetime import datetime, timedelta
    
    # 找到该年的第一个周四（ISO周从包含1月4日的周开始）
    jan4 = datetime(week_year, 1, 4)
    # 周四是一周的第4天（ISO周从周一开始，周四是第4天）
    first_thursday = jan4 - timedelta(days=(jan4.weekday() - 3) % 7)
    # 计算第一周的周一
    first_monday = first_thursday - timedelta(days=3)
    # 计算目标周的周一
    week_start = first_monday + timedelta(weeks=week_number - 1)
    week_end = week_start + timedelta(days=6)
    return week_start.date(), week_end.date()


@weekly_menu_bp.get("")
@jwt_required()
def list_weekly_menus():
    """获取总菜单列表"""
    jwt_data = get_jwt()
    role = jwt_data.get("role")
    
    # customer 角色不能查看总菜单
    if role == "customer":
        return jsonify({"msg": "无权限"}), 403
    
    week_year = request.args.get("week_year", type=int)
    week_number = request.args.get("week_number", type=int)
    
    q = WeeklyMenu.query
    
    if week_year:
        q = q.filter(WeeklyMenu.week_year == week_year)
    if week_number:
        q = q.filter(WeeklyMenu.week_number == week_number)
    
    menus = q.order_by(WeeklyMenu.week_year.desc(), WeeklyMenu.week_number.desc()).all()
    
    data = []
    for menu in menus:
        data.append({
            "id": menu.id,
            "week_year": menu.week_year,
            "week_number": menu.week_number,
            "week_start_date": menu.week_start_date.isoformat(),
            "week_end_date": menu.week_end_date.isoformat(),
            "status": menu.status,
            "generating_status": menu.generating_status or "idle",
            "created_by": menu.created_by,
            "created_at": menu.created_at.isoformat() if menu.created_at else None,
            "updated_at": menu.updated_at.isoformat() if menu.updated_at else None,
        })
    
    return jsonify(data)


@weekly_menu_bp.get("/<int:menu_id>")
@jwt_required()
def get_weekly_menu(menu_id):
    """获取总菜单详情"""
    jwt_data = get_jwt()
    role = jwt_data.get("role")
    
    if role == "customer":
        return jsonify({"msg": "无权限"}), 403
    
    menu = WeeklyMenu.query.get_or_404(menu_id)
    
    # 获取所有明细项（直接查询，避免lazy loading的N+1问题）
    items = db.session.query(WeeklyMenuItem).filter(
        WeeklyMenuItem.weekly_menu_id == menu_id
    ).order_by(
        WeeklyMenuItem.day_of_week,
        WeeklyMenuItem.meal_type,
        WeeklyMenuItem.sort_order
    ).all()
    
    items_data = []
    for item in items:
        items_data.append({
            "id": item.id,
            "day_of_week": item.day_of_week,
            "meal_type": item.meal_type,
            "dish_name": item.dish_name,
            "dish_category": item.dish_category,
            "sort_order": item.sort_order,
        })
    
    return jsonify({
        "id": menu.id,
        "week_year": menu.week_year,
        "week_number": menu.week_number,
        "week_start_date": menu.week_start_date.isoformat(),
        "week_end_date": menu.week_end_date.isoformat(),
        "status": menu.status,
        "generating_status": menu.generating_status or "idle",
        "created_by": menu.created_by,
        "created_at": menu.created_at.isoformat() if menu.created_at else None,
        "updated_at": menu.updated_at.isoformat() if menu.updated_at else None,
        "items": items_data,
    })


def save_menu_items(menu_id: int, menu_data: list):
    """保存菜单明细项到数据库（在独立会话中）"""
    from app import create_app
    app = create_app()
    with app.app_context():
        # 创建新的数据库会话
        from app.extensions import db
        menu = WeeklyMenu.query.get(menu_id)
        if not menu:
            return
        
        dish_types = ["大荤", "小荤", "素菜", "例汤"]
        meal_types = ["午餐", "晚餐"]
        
        try:
            # 保存菜单明细
            item_count = 0
            for dish_type_idx, dish_type_data in enumerate(menu_data):
                dish_type = dish_types[dish_type_idx]
                
                for day_idx, day_data in enumerate(dish_type_data):
                    day_of_week = day_idx + 1
                    
                    for meal_idx, meal_dishes in enumerate(day_data):
                        meal_type = meal_types[meal_idx]
                        
                        if dish_type == "大荤":
                            if meal_type == "午餐":
                                categories = ["大荤一", "大荤二", "大荤三"]
                            else:
                                categories = ["大荤一", "大荤二"]
                        elif dish_type == "小荤":
                            categories = ["小荤一", "小荤二"]
                        elif dish_type == "素菜":
                            categories = ["素菜一", "素菜二"]
                        else:
                            categories = ["例汤"]
                        
                        for sort_order, dish_name in enumerate(meal_dishes):
                            dish_category = categories[sort_order] if sort_order < len(categories) else categories[-1]
                            item = WeeklyMenuItem(
                                weekly_menu_id=menu_id,
                                day_of_week=day_of_week,
                                meal_type=meal_type,
                                dish_name=dish_name,
                                dish_category=dish_category,
                                sort_order=sort_order,
                            )
                            db.session.add(item)
                            item_count += 1
            
            # 更新状态为完成
            menu.generating_status = "completed"
            menu.status = "draft"
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            menu = WeeklyMenu.query.get(menu_id)
            if menu:
                menu.generating_status = "failed"
                db.session.commit()
            raise


def generate_menu_async(menu_id: int, week_year: int, week_number: int):
    """异步生成菜单的后台任务"""
    try:
        # 更新状态为生成中
        from app import create_app
        app = create_app()
        with app.app_context():
            from app.extensions import db
            menu = WeeklyMenu.query.get(menu_id)
            if not menu:
                return
            
            menu.generating_status = "generating"
            db.session.commit()
        
        # 调用菜单生成算法
        menu_data = generate_weekly_menu_data(week_year, week_number)
        
        # 保存菜单明细（在独立会话中）
        save_menu_items(menu_id, menu_data)
    except Exception as e:
        # 更新状态为失败
        from app import create_app
        app = create_app()
        with app.app_context():
            from app.extensions import db
            menu = WeeklyMenu.query.get(menu_id)
            if menu:
                menu.generating_status = "failed"
                db.session.commit()


@weekly_menu_bp.post("/generate")
@jwt_required()
@roles_required("user", "admin", "superadmin")
def generate_menu():
    """生成一周总菜单（异步）"""
    data = request.json or {}
    week_year = data.get("week_year")
    week_number = data.get("week_number")
    
    if not week_year or not week_number:
        return jsonify({"msg": "年份和周数必填"}), 400
    
    # 检查是否已存在（如果需要覆盖，会在前端确认后传递 force=true）
    force = data.get("force", False)
    existing = WeeklyMenu.query.filter_by(
        week_year=week_year,
        week_number=week_number
    ).first()
    if existing:
        if not force:
            # 返回菜单状态，让前端决定是否覆盖
            return jsonify({
                "id": existing.id,
                "generating_status": existing.generating_status or "idle",
                "status": existing.status,
                "msg": "该周菜单已存在",
                "exists": True,
            }), 409  # 409 Conflict
        else:
            # 删除已存在的菜单及其明细
            WeeklyMenuItem.query.filter_by(weekly_menu_id=existing.id).delete()
            db.session.delete(existing)
            db.session.commit()
    
    # 计算周的开始和结束日期
    week_start, week_end = calculate_week_dates(week_year, week_number)
    
    # 创建总菜单记录（初始状态为生成中）
    jwt_data = get_jwt()
    user_id = jwt_data.get("sub")
    
    weekly_menu = WeeklyMenu(
        week_year=week_year,
        week_number=week_number,
        week_start_date=week_start,
        week_end_date=week_end,
        status="draft",
        generating_status="generating",
        created_by=int(user_id) if user_id else None,
    )
    db.session.add(weekly_menu)
    db.session.flush()
    menu_id = weekly_menu.id
    db.session.commit()
    
    # 启动后台线程生成菜单
    thread = threading.Thread(
        target=generate_menu_async,
        args=(menu_id, week_year, week_number),
        daemon=True
    )
    thread.start()
    
    return jsonify({
        "id": menu_id,
        "generating_status": "generating",
        "msg": "菜单生成已启动，正在后台处理",
    }), 202


@weekly_menu_bp.post("")
@jwt_required()
@roles_required("user", "admin", "superadmin")
def create_weekly_menu():
    """手动创建总菜单"""
    data = request.json or {}
    week_year = data.get("week_year")
    week_number = data.get("week_number")
    items = data.get("items", [])
    
    if not week_year or not week_number:
        return jsonify({"msg": "年份和周数必填"}), 400
    
    # 检查是否已存在
    existing = WeeklyMenu.query.filter_by(
        week_year=week_year,
        week_number=week_number
    ).first()
    if existing:
        return jsonify({"msg": "该周菜单已存在"}), 400
    
    # 计算周的开始和结束日期
    week_start, week_end = calculate_week_dates(week_year, week_number)
    
    jwt_data = get_jwt()
    user_id = jwt_data.get("sub")
    
    weekly_menu = WeeklyMenu(
        week_year=week_year,
        week_number=week_number,
        week_start_date=week_start,
        week_end_date=week_end,
        status=data.get("status", "draft"),
        created_by=int(user_id) if user_id else None,
    )
    db.session.add(weekly_menu)
    db.session.flush()
    
    # 保存明细项
    for item_data in items:
        item = WeeklyMenuItem(
            weekly_menu_id=weekly_menu.id,
            day_of_week=item_data.get("day_of_week"),
            meal_type=item_data.get("meal_type"),
            dish_name=item_data.get("dish_name"),
            dish_category=item_data.get("dish_category"),
            sort_order=item_data.get("sort_order", 0),
        )
        db.session.add(item)
    
    db.session.commit()
    
    return jsonify({
        "id": weekly_menu.id,
        "msg": "创建成功",
    }), 201


@weekly_menu_bp.put("/<int:menu_id>")
@jwt_required()
@roles_required("user", "admin", "superadmin")
def update_weekly_menu(menu_id):
    """更新总菜单"""
    menu = WeeklyMenu.query.get_or_404(menu_id)
    data = request.json or {}
    
    if "status" in data:
        menu.status = data["status"]
    
    if "items" in data:
        # 删除旧明细
        WeeklyMenuItem.query.filter_by(weekly_menu_id=menu.id).delete()
        
        # 添加新明细
        for item_data in data["items"]:
            item = WeeklyMenuItem(
                weekly_menu_id=menu.id,
                day_of_week=item_data.get("day_of_week"),
                meal_type=item_data.get("meal_type"),
                dish_name=item_data.get("dish_name"),
                dish_category=item_data.get("dish_category"),
                sort_order=item_data.get("sort_order", 0),
            )
            db.session.add(item)
    
    db.session.commit()
    
    return jsonify({"msg": "更新成功"})


@weekly_menu_bp.put("/<int:menu_id>/items/replace")
@jwt_required()
@roles_required("user", "admin", "superadmin")
def replace_weekly_menu_item(menu_id: int):
    """
    替换“一个单元格”的菜品（按 day_of_week + meal_type + dish_category 定位）

    入参：
    {
      "day_of_week": 1-7,
      "meal_type": "午餐" | "晚餐",
      "dish_category": "大荤一" | ... | "例汤",
      "new_dish_name": "新菜品名"
    }
    """
    data = request.json or {}
    day_of_week = data.get("day_of_week")
    meal_type = data.get("meal_type")
    dish_category = data.get("dish_category")
    new_dish_name = (data.get("new_dish_name") or "").strip()

    if not day_of_week or not meal_type or not dish_category or not new_dish_name:
        return jsonify({"msg": "day_of_week、meal_type、dish_category、new_dish_name 必填"}), 400

    menu = WeeklyMenu.query.get_or_404(menu_id)

    # 定位现有项
    item = WeeklyMenuItem.query.filter_by(
        weekly_menu_id=menu.id,
        day_of_week=day_of_week,
        meal_type=meal_type,
        dish_category=dish_category,
    ).first()

    if item:
        item.dish_name = new_dish_name
    else:
        # 如果该单元格原本为空：创建一个新项（sort_order 尽量按分类落位）
        def _sort_order_for_category(meal: str, category: str) -> int:
            if meal == "午餐":
                order = ["大荤一", "大荤二", "大荤三", "小荤一", "小荤二", "素菜一", "素菜二", "例汤"]
            else:
                order = ["大荤一", "大荤二", "小荤一", "小荤二", "素菜一", "素菜二", "例汤"]
            return order.index(category) if category in order else 0

        item = WeeklyMenuItem(
            weekly_menu_id=menu.id,
            day_of_week=day_of_week,
            meal_type=meal_type,
            dish_name=new_dish_name,
            dish_category=dish_category,
            sort_order=_sort_order_for_category(meal_type, dish_category),
        )
        db.session.add(item)

    db.session.commit()

    return jsonify(
        {
            "msg": "替换成功",
            "item": {
                "id": item.id,
                "day_of_week": item.day_of_week,
                "meal_type": item.meal_type,
                "dish_name": item.dish_name,
                "dish_category": item.dish_category,
                "sort_order": item.sort_order,
            },
        }
    )

