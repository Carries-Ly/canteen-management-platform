# -*- coding: utf-8 -*-
import pandas as pd
import random
from itertools import chain


def big_is_qualify(
    target,
    price,
    meal_main1,
    meal_main2,
    meal_main3,
    meal_main4,
    meal_target,
    meal_price,
    used_big_main,
):
    qualified = 0
    if (
        meal_main1 in used_big_main
        or meal_main2 in used_big_main
        or meal_main3 in used_big_main
        or meal_main4 in used_big_main
    ):
        return qualified, meal_target, meal_price

    if meal_target == 0 and meal_price == 0:
        if target == "全部":
            meal_target = 1
            qualified = 1
        if price == "适中":
            meal_price = 1
            qualified = 1
        return qualified, meal_target, meal_price
    if meal_target == 1 and meal_price == 0:
        if price == "适中":
            meal_price = 1
            qualified = 1
            return qualified, meal_target, meal_price
        else:
            return qualified, meal_target, meal_price
    if meal_target == 0 and meal_price == 1:
        if target == "全部":
            meal_target = 1
            qualified = 1
            return qualified, meal_target, meal_price
        else:
            return qualified, meal_target, meal_price
    if meal_target == 1 and meal_price == 1:
        if target == "全部" or price == "适中":
            qualified = 1
            return qualified, meal_target, meal_price
        else:
            return qualified, meal_target, meal_price


# 引用时参数使用  has_braise举例             has_bean        used_main
#              has_braise[day][noon]     has_bean[day]   used_main[day][noon]
def meal_qualify(
    meal_main1,
    meal_main2,
    meal_main3,
    meal_main4,
    meal_bean,
    meal_braise,
    meal_flavor,
    used_main,
    has_bean,
    has_braise,
    has_special,
):
    try:
        qualify = 1
        if meal_bean == "含豆制品" and has_bean == 1:
            qualify = 0
        if meal_flavor != "家常" and has_special == 1:
            qualify = 0
        if meal_braise == "蒸" and has_braise == 1:
            qualify = 0
        if (
            meal_main1 in used_main
            or meal_main2 in used_main
            or meal_main3 in used_main
            or meal_main4 in used_main
        ):
            qualify = 0
        if qualify == 1:
            used_main.append(meal_main1)
            if pd.notna(meal_main2):
                used_main.append(meal_main2)
            if pd.notna(meal_main3):
                used_main.append(meal_main3)
            if pd.notna(meal_main4):
                used_main.append(meal_main4)

            if meal_bean == "含豆制品":
                has_bean = 1
            if meal_flavor != "家常":
                has_special = 1
            if meal_braise == "蒸":
                has_braise = 1
        return qualify, used_main, has_bean, has_braise, has_special
    except Exception as e:
        print("meal_quality error")


def small_qualify(
    small_selected,
    meal_xiafan,
    xiafan,
    meal_main1,
    meal_main2,
    meal_main3,
    meal_main4,
    meal_bean,
    meal_braise,
    meal_flavor,
    used_main,
    has_bean,
    has_braise,
    has_special,
):
    not_qualify = 0
    if small_selected == 0:
        if meal_xiafan == "是":
            xiafan = 1
            meal_quality, used_main, has_bean, has_braise, has_special = meal_qualify(
                meal_main1,
                meal_main2,
                meal_main3,
                meal_main4,
                meal_bean,
                meal_braise,
                meal_flavor,
                used_main,
                has_bean,
                has_braise,
                has_special,
            )
            return meal_quality, xiafan, used_main, has_bean, has_braise, has_special
        if meal_xiafan == "否":
            meal_quality, used_main, has_bean, has_braise, has_special = meal_qualify(
                meal_main1,
                meal_main2,
                meal_main3,
                meal_main4,
                meal_bean,
                meal_braise,
                meal_flavor,
                used_main,
                has_bean,
                has_braise,
                has_special,
            )
            return meal_quality, xiafan, used_main, has_bean, has_braise, has_special
    if small_selected == 1:
        if meal_xiafan == "是":
            xiafan = 1
            meal_quality, used_main, has_bean, has_braise, has_special = meal_qualify(
                meal_main1,
                meal_main2,
                meal_main3,
                meal_main4,
                meal_bean,
                meal_braise,
                meal_flavor,
                used_main,
                has_bean,
                has_braise,
                has_special,
            )
            return meal_quality, xiafan, used_main, has_bean, has_braise, has_special
        else:
            if xiafan == 0:
                return not_qualify, xiafan, used_main, has_bean, has_braise, has_special
            else:
                meal_quality, used_main, has_bean, has_braise, has_special = (
                    meal_qualify(
                        meal_main1,
                        meal_main2,
                        meal_main3,
                        meal_main4,
                        meal_bean,
                        meal_braise,
                        meal_flavor,
                        used_main,
                        has_bean,
                        has_braise,
                        has_special,
                    )
                )
                return (
                    meal_quality,
                    xiafan,
                    used_main,
                    has_bean,
                    has_braise,
                    has_special,
                )


# has_bean 每天一道豆制品 [1x7] 0:今天还没有 1:今天已经有豆制品
# has_braise 每餐只能出现一次蒸菜
# has_special 每餐只能排一次特殊味道
# used_main  每餐用过的主料
def select_meal(meal, category, has_bean, has_braise, has_special, used_main):
    try:
        if category == "小荤":
            # 一周安排5次蛋类
            # 西红柿炒鸡蛋必须有  上午
            # 炖蛋必须有  不能再同一天
            egg_selected = 0
            require_egg = ["西红柿炒蛋", "开洋炖蛋"]
            egg = meal.loc[meal[("类别", "")] == "蛋类"]
            egg_indexes = list(egg.index)
            # egg_length = len(egg) - 1
            # print('本周蛋类菜品数量：5')
            numbers = range(7)
            # 从numbers中随机选择3个不同的数

            lunch_egg_day = random.sample(numbers, 3)
            tomato_day = random.sample(lunch_egg_day, 1)  # 西红柿炒鸡蛋在中午中选一天
            supper_egg_day = random.sample(numbers, 2)
            if_egg_day = random.randint(0, 1)
            if if_egg_day == 0:
                egg_day = random.sample(
                    [item for item in lunch_egg_day if item not in tomato_day], 1
                )
            else:
                egg_day = random.sample(
                    [item for item in supper_egg_day if item not in tomato_day], 1
                )
            # print(egg_day)
        if category == "大荤":  # 一周吃两次牛肉 且不在周末
            beef_selected = 0
            numbers = range(1, 5)
            lunch_beef_day = random.sample(numbers, 1)[0]
            supper_beef_day = (lunch_beef_day + 2) % 4

        index_list = list(meal.index)
        beef_list = list(meal.loc[meal[("类别", "")] == "牛肉类"].index)
        meal_week = []
        fish = 0
        shrimp = 0
        used_categories = [None, None]  # 记录前一天   已经使用的大荤类别
        used_big_main = [[], []]  # 记录 前一天 的大荤配料，第二天不重复
        for day in range(7):
            meal_day = []
            # yesterday_big_main 用来记录昨天已经使用过的主配料
            # used_big_mian 用来记录当天已经使用过的主配料
            yesterday_big_main = used_big_main
            used_big_main = [[], []]
            for noon in range(2):
                meal_noon = []
                has_whole = 0
                has_medium = 0
                counter = 0
                # 表示品种搭配并且与上午下午不一样，与前一天时间错开
                if category == "大荤":
                    # 鱼类一周只安排 两次
                    meat_selected = 0
                    other_selected = 0
                    while not (meat_selected and other_selected):
                        # 限定最大迭代数量
                        counter += 1
                        if counter == 500:
                            return None
                        # 处理牛肉类
                        if beef_selected == 0 and (
                            (day == lunch_beef_day and noon == 0)
                            or (day == supper_beef_day and noon == 1)
                        ):
                            index = random.sample(beef_list, 1)[0]
                            while meal.loc[index, ("check", "")] == 1:
                                index = random.sample(beef_list, 1)[0]
                            meal_category = meal.loc[index, ("类别", "")]
                            meal_name = meal.loc[index, ("菜名", "")]
                            meal_target = meal.loc[index, ("适用人群", "")]
                            meal_price = meal.loc[index, ("成本", "")]
                            meal_bean = meal.loc[index, ("是否含豆制品", "")]
                            meal_braise = meal.loc[index, ("烹饪方式", "")]
                            meal_flavor = meal.loc[index, ("味型", "")]
                            meal_main1 = meal.loc[index, ("原料1", "半成品名称")]
                            meal_main2 = meal.loc[index, ("原料2", "半成品名称")]
                            meal_main3 = meal.loc[index, ("原料3", "半成品名称")]
                            meal_main4 = meal.loc[index, ("原料4", "半成品名称")]
                            qualified, has_whole, has_medium = big_is_qualify(
                                meal_target,
                                meal_price,
                                meal_main1,
                                meal_main2,
                                meal_main3,
                                meal_main4,
                                has_whole,
                                has_medium,
                                chain.from_iterable(yesterday_big_main + used_big_main),
                            )
                            if qualified == 1:
                                (
                                    qualify,
                                    used_main[day][noon],
                                    has_bean[day],
                                    has_braise[day][noon],
                                    has_special[day][noon],
                                ) = meal_qualify(
                                    meal_main1,
                                    meal_main2,
                                    meal_main3,
                                    meal_main4,
                                    meal_bean,
                                    meal_braise,
                                    meal_flavor,
                                    used_main[day][noon],
                                    has_bean[day],
                                    has_braise[day][noon],
                                    has_special[day][noon],
                                )
                            if qualified and qualify == 1:
                                beef_selected = 1
                                meal.loc[index, ("check", "")] = 1
                                meal_noon.append(meal_name)
                                used_big_main[noon].append(meal_main1)
                                if pd.notna(meal_main2):
                                    used_big_main[noon].append(meal_main2)
                                if pd.notna(meal_main3):
                                    used_big_main[noon].append(meal_main3)
                                if pd.notna(meal_main4):
                                    used_big_main[noon].append(meal_main4)
                                continue
                            else:
                                continue
                        # 除了牛肉类
                        index = random.sample(index_list, 1)[0]
                        # 表示这一周没有用过
                        while (
                            meal.loc[index, ("check", "")] == 1
                            or meal.loc[index, ("类别", "")] in used_categories
                            or meal.loc[index, ("类别", "")] == "牛肉类"
                        ):
                            index = random.sample(index_list, 1)[0]

                        meal_category = meal.loc[index, ("类别", "")]
                        meal_name = meal.loc[index, ("菜名", "")]
                        meal_target = meal.loc[index, ("适用人群", "")]
                        meal_price = meal.loc[index, ("成本", "")]
                        meal_bean = meal.loc[index, ("是否含豆制品", "")]
                        meal_braise = meal.loc[index, ("烹饪方式", "")]
                        meal_flavor = meal.loc[index, ("味型", "")]
                        meal_main1 = meal.loc[index, ("原料1", "半成品名称")]
                        meal_main2 = meal.loc[index, ("原料2", "半成品名称")]
                        meal_main3 = meal.loc[index, ("原料3", "半成品名称")]
                        meal_main4 = meal.loc[index, ("原料4", "半成品名称")]

                        if meal_category in ["猪肉类"] and meat_selected == 0:
                            qualified, has_whole, has_medium = big_is_qualify(
                                meal_target,
                                meal_price,
                                meal_main1,
                                meal_main2,
                                meal_main3,
                                meal_main4,
                                has_whole,
                                has_medium,
                                chain.from_iterable(yesterday_big_main + used_big_main),
                            )
                            if qualified == 1:
                                (
                                    qualify,
                                    used_main[day][noon],
                                    has_bean[day],
                                    has_braise[day][noon],
                                    has_special[day][noon],
                                ) = meal_qualify(
                                    meal_main1,
                                    meal_main2,
                                    meal_main3,
                                    meal_main4,
                                    meal_bean,
                                    meal_braise,
                                    meal_flavor,
                                    used_main[day][noon],
                                    has_bean[day],
                                    has_braise[day][noon],
                                    has_special[day][noon],
                                )
                            if qualified and qualify == 1:
                                meat_selected = 1
                                meal.loc[index, ("check", "")] = 1
                                meal_noon.append(meal_name)
                                used_big_main[noon].append(meal_main1)
                                if pd.notna(meal_main2):
                                    used_big_main[noon].append(meal_main2)
                                if pd.notna(meal_main3):
                                    used_big_main[noon].append(meal_main3)
                                if pd.notna(meal_main4):
                                    used_big_main[noon].append(meal_main4)
                            else:
                                continue
                        # 检查是否满足鸡鸭鹅鱼类别的要求
                        if (
                            meal_category in ["鸡类", "鸭类", "混合类", "鱼类", "虾类"]
                            and other_selected != 1
                        ):
                            if meal_category == "鱼类" and fish == 2:
                                continue
                            if meal_category == "虾类" and shrimp == 2:
                                continue
                            else:
                                if noon == 0:
                                    if meal_category not in used_categories:
                                        qualified, has_whole, has_medium = (
                                            big_is_qualify(
                                                meal_target,
                                                meal_price,
                                                meal_main1,
                                                meal_main2,
                                                meal_main3,
                                                meal_main4,
                                                has_whole,
                                                has_medium,
                                                chain.from_iterable(
                                                    yesterday_big_main + used_big_main
                                                ),
                                            )
                                        )
                                        if qualified == 1:
                                            (
                                                qualify,
                                                used_main[day][noon],
                                                has_bean[day],
                                                has_braise[day][noon],
                                                has_special[day][noon],
                                            ) = meal_qualify(
                                                meal_main1,
                                                meal_main2,
                                                meal_main3,
                                                meal_main4,
                                                meal_bean,
                                                meal_braise,
                                                meal_flavor,
                                                used_main[day][noon],
                                                has_bean[day],
                                                has_braise[day][noon],
                                                has_special[day][noon],
                                            )
                                        if qualified == 1 and qualify == 1:
                                            other_selected = 1
                                            meal.loc[index, ("check", "")] = 1
                                            meal_noon.append(meal_name)
                                            used_big_main[noon].append(meal_main1)
                                            if pd.notna(meal_main2):
                                                used_big_main[noon].append(meal_main2)
                                            if pd.notna(meal_main3):
                                                used_big_main[noon].append(meal_main3)
                                            if pd.notna(meal_main4):
                                                used_big_main[noon].append(meal_main4)
                                            used_categories[0] = meal_category
                                            if meal_category == "鱼类":
                                                fish += 1
                                            if meal_category == "虾类":
                                                shrimp += 1
                                        else:
                                            continue
                                else:
                                    if (day == lunch_beef_day and noon == 0) or (
                                        day == supper_beef_day and noon == 1
                                    ):
                                        other_selected = 1
                                        continue
                                    if meal_category not in used_categories:
                                        qualified, has_whole, has_medium = (
                                            big_is_qualify(
                                                meal_target,
                                                meal_price,
                                                meal_main1,
                                                meal_main2,
                                                meal_main3,
                                                meal_main4,
                                                has_whole,
                                                has_medium,
                                                chain.from_iterable(
                                                    yesterday_big_main + used_big_main
                                                ),
                                            )
                                        )
                                        if qualified == 1:
                                            (
                                                qualify,
                                                used_main[day][noon],
                                                has_bean[day],
                                                has_braise[day][noon],
                                                has_special[day][noon],
                                            ) = meal_qualify(
                                                meal_main1,
                                                meal_main2,
                                                meal_main3,
                                                meal_main4,
                                                meal_bean,
                                                meal_braise,
                                                meal_flavor,
                                                used_main[day][noon],
                                                has_bean[day],
                                                has_braise[day][noon],
                                                has_special[day][noon],
                                            )
                                        if qualified == 1 and qualify == 1:
                                            other_selected = 1
                                            meal.loc[index, ("check", "")] = 1
                                            meal_noon.append(meal_name)
                                            used_big_main[noon].append(meal_main1)
                                            if pd.notna(meal_main2):
                                                used_big_main[noon].append(meal_main2)
                                            if pd.notna(meal_main3):
                                                used_big_main[noon].append(meal_main3)
                                            if pd.notna(meal_main4):
                                                used_big_main[noon].append(meal_main4)
                                            used_categories[1] = meal_category
                                            if meal_category == "鱼类":
                                                fish += 1
                                            if meal_category == "虾类":
                                                shrimp += 1
                                        else:
                                            continue
                    # 如果牛肉在下午那么就会导致有三个菜了
                    if (
                        (day == lunch_beef_day and noon == 0)
                        or (day == supper_beef_day and noon == 1)
                    ) or (noon == 1):
                        third = 1
                    else:
                        third = 0
                    while third < 1:
                        # 再添加一个大荤，主料不重复并且不是牛肉 烹饪方式要求不同！
                        index = random.sample(index_list, 1)[0]
                        # 表示这一周没有用过
                        while (
                            meal.loc[index, ("check", "")] == 1
                            or meal.loc[index, ("类别", "")] in used_categories
                            or meal.loc[index, ("类别", "")] == "牛肉类"
                        ):
                            index = random.sample(index_list, 1)[0]

                        meal_category = meal.loc[index, ("类别", "")]
                        if meal_category == "鱼类" and fish == 2:
                            continue
                        if meal_category == "虾类" and shrimp == 1:
                            continue

                        meal_name = meal.loc[index, ("菜名", "")]
                        meal_target = meal.loc[index, ("适用人群", "")]
                        meal_price = meal.loc[index, ("成本", "")]
                        meal_bean = meal.loc[index, ("是否含豆制品", "")]
                        meal_braise = meal.loc[index, ("烹饪方式", "")]
                        meal_flavor = meal.loc[index, ("味型", "")]
                        meal_main1 = meal.loc[index, ("原料1", "半成品名称")]
                        meal_main2 = meal.loc[index, ("原料2", "半成品名称")]
                        meal_main3 = meal.loc[index, ("原料3", "半成品名称")]
                        meal_main4 = meal.loc[index, ("原料4", "半成品名称")]
                        qualified, has_whole, has_medium = big_is_qualify(
                            meal_target,
                            meal_price,
                            meal_main1,
                            meal_main2,
                            meal_main3,
                            meal_main4,
                            has_whole,
                            has_medium,
                            chain.from_iterable(yesterday_big_main + used_big_main),
                        )
                        if qualified == 1:
                            (
                                qualify,
                                used_main[day][noon],
                                has_bean[day],
                                has_braise[day][noon],
                                has_special[day][noon],
                            ) = meal_qualify(
                                meal_main1,
                                meal_main2,
                                meal_main3,
                                meal_main4,
                                meal_bean,
                                meal_braise,
                                meal_flavor,
                                used_main[day][noon],
                                has_bean[day],
                                has_braise[day][noon],
                                has_special[day][noon],
                            )
                        if qualified and qualify == 1:
                            third = 1
                            meal.loc[index, ("check", "")] = 1
                            meal_noon.append(meal_name)
                            used_big_main[noon].append(meal_main1)
                            if pd.notna(meal_main2):
                                used_big_main[noon].append(meal_main2)
                            if pd.notna(meal_main3):
                                used_big_main[noon].append(meal_main3)
                            if pd.notna(meal_main4):
                                used_big_main[noon].append(meal_main4)
                            if meal_category == "鱼类":
                                fish += 1
                            if meal_category == "虾类":
                                shrimp += 1
                        else:
                            continue

                    beef_selected = 0

                if category == "小荤":
                    xiafan = 0
                    small_selected = 0
                    used_small = []
                    while small_selected < 2:
                        # 限定最大迭代数量
                        counter += 1
                        if counter == 500:
                            return None
                        if (
                            day in lunch_egg_day and noon == 0 and egg_selected == 0
                        ):  # 今天中午需要一个蛋类
                            if day in tomato_day:
                                meal.loc[
                                    meal[("菜名", "")] == "西红柿炒蛋", "check"
                                ] = 1
                                meal_noon.append("西红柿炒蛋")  #:红黄
                                egg_selected = 1
                                xiafan += 1
                                small_selected += 1
                                used_main[day][noon].append("鸡蛋")
                                used_main[day][noon].append("西红柿")
                                continue

                            if if_egg_day == 0 and day in egg_day:
                                # 炖蛋是 蒸 的！！！！！！！！！！！需要注意
                                meal.loc[meal[("菜名", "")] == "开洋炖蛋", "check"] = 1
                                has_braise[day][noon] = 1
                                meal_noon.append("开洋炖蛋")  #:黄色
                                used_main[day][noon].append("鸡蛋")
                                egg_selected = 1
                                small_selected += 1
                                continue

                            index = random.sample(egg_indexes, 1)[0]
                            egg_name = egg.loc[index, ("菜名", "")]
                            while (
                                meal.loc[index, ("check", "")] == 1
                            ).any() or egg_name in require_egg:
                                index = random.sample(egg_indexes, 1)[0]
                                egg_name = meal.loc[index, ("菜名", "")]

                            meal_bean = meal.loc[index, ("是否含豆制品", "")]
                            meal_braise = meal.loc[index, ("烹饪方式", "")]
                            meal_flavor = meal.loc[index, ("味型", "")]
                            meal_xiafan = meal.loc[index, ("下饭菜", "")]
                            meal_color = meal.loc[index, ("色", "")]
                            meal_main1 = meal.loc[index, ("原料1", "半成品名称")]
                            meal_main2 = meal.loc[index, ("原料2", "半成品名称")]
                            meal_main3 = meal.loc[index, ("原料3", "半成品名称")]
                            meal_main4 = meal.loc[index, ("原料4", "半成品名称")]
                            (
                                qualify,
                                xiafan,
                                used_main[day][noon],
                                has_bean[day],
                                has_braise[day][noon],
                                has_special[day][noon],
                            ) = small_qualify(
                                small_selected,
                                meal_xiafan,
                                xiafan,
                                meal_main1,
                                meal_main2,
                                meal_main3,
                                meal_main4,
                                meal_bean,
                                meal_braise,
                                meal_flavor,
                                used_main[day][noon],
                                has_bean[day],
                                has_braise[day][noon],
                                has_special[day][noon],
                            )
                            if qualify == 1:
                                meal.loc[index, ("check", "")] = 1
                                meal_noon.append(egg_name)  # +':'+meal_color
                                egg_selected = 1
                                small_selected += 1
                                continue
                            else:
                                continue

                        if (
                            day in supper_egg_day and noon == 1 and egg_selected == 0
                        ):  # 今天晚上需要一个蛋类
                            if if_egg_day == 1 and day in egg_day:
                                meal.loc[meal[("菜名", "")] == "开洋炖蛋", "check"] = 1
                                has_braise[day][noon] = 1
                                meal_noon.append("开洋炖蛋")
                                egg_selected = 1
                                small_selected += 1
                                continue

                            index = random.sample(egg_indexes, 1)[0]
                            egg_name = egg.loc[index, ("菜名", "")]
                            while (
                                meal.loc[index, ("check", "")] == 1
                            ).any() or egg_name in require_egg:
                                index = random.sample(egg_indexes, 1)[0]
                                egg_name = meal.loc[index, ("菜名", "")]

                            meal_bean = meal.loc[index, ("是否含豆制品", "")]
                            meal_braise = meal.loc[index, ("烹饪方式", "")]
                            meal_flavor = meal.loc[index, ("味型", "")]
                            meal_xiafan = meal.loc[index, ("下饭菜", "")]
                            meal_color = meal.loc[index, ("色", "")]
                            meal_main1 = meal.loc[index, ("原料1", "半成品名称")]
                            meal_main2 = meal.loc[index, ("原料2", "半成品名称")]
                            meal_main3 = meal.loc[index, ("原料3", "半成品名称")]
                            meal_main4 = meal.loc[index, ("原料4", "半成品名称")]
                            (
                                qualify,
                                xiafan,
                                used_main[day][noon],
                                has_bean[day],
                                has_braise[day][noon],
                                has_special[day][noon],
                            ) = small_qualify(
                                small_selected,
                                meal_xiafan,
                                xiafan,
                                meal_main1,
                                meal_main2,
                                meal_main3,
                                meal_main4,
                                meal_bean,
                                meal_braise,
                                meal_flavor,
                                used_main[day][noon],
                                has_bean[day],
                                has_braise[day][noon],
                                has_special[day][noon],
                            )
                            if qualify == 1:
                                meal.loc[index, ("check", "")] = 1
                                meal_noon.append(egg_name)  # +':'+meal_color
                                egg_selected = 1
                                small_selected += 1
                                continue
                            else:
                                continue

                        # 非蛋类:
                        index = random.sample(index_list, 1)[0]

                        # 表示这一周没有用过
                        while (
                            meal.loc[index, ("check", "")] == 1
                            or meal.loc[index, ("类别", "")] == "蛋类"
                        ):
                            index = random.sample(index_list, 1)[0]

                        meal_category = meal.loc[index, ("类别", "")]
                        meal_name = meal.loc[index, ("菜名", "")]
                        meal_target = meal.loc[index, ("适用人群", "")]
                        meal_price = meal.loc[index, ("成本", "")]
                        meal_xiafan = meal.loc[index, ("下饭菜", "")]
                        meal_bean = meal.loc[index, ("是否含豆制品", "")]
                        meal_braise = meal.loc[index, ("烹饪方式", "")]
                        meal_flavor = meal.loc[index, ("味型", "")]
                        meal_main1 = meal.loc[index, ("原料1", "半成品名称")]
                        meal_main2 = meal.loc[index, ("原料2", "半成品名称")]
                        meal_main3 = meal.loc[index, ("原料3", "半成品名称")]
                        meal_main4 = meal.loc[index, ("原料4", "半成品名称")]

                        (
                            qualify,
                            xiafan,
                            used_main[day][noon],
                            has_bean[day],
                            has_braise[day][noon],
                            has_special[day][noon],
                        ) = small_qualify(
                            small_selected,
                            meal_xiafan,
                            xiafan,
                            meal_main1,
                            meal_main2,
                            meal_main3,
                            meal_main4,
                            meal_bean,
                            meal_braise,
                            meal_flavor,
                            used_main[day][noon],
                            has_bean[day],
                            has_braise[day][noon],
                            has_special[day][noon],
                        )
                        if qualify == 1:
                            if (
                                small_selected == 0
                            ):  # TODO 现在的小荤里不一定按照这个格式！
                                if meal_main1 in [
                                    "肉片",
                                    "肉丝",
                                    "肉丁",
                                    "鸡丁",
                                    "鸡片",
                                    "鸡丝",
                                ]:
                                    used_small.append(meal_main1)
                            else:
                                if meal_main1 in [
                                    "肉片",
                                    "肉丝",
                                    "肉丁",
                                    "鸡丁",
                                    "鸡片",
                                    "鸡丝",
                                ]:
                                    pig = "猪肉" + meal_main1[-1]
                                    # print("pig:{}".format(pig))
                                    chicken = "鸡" + meal_main1[-1]
                                    # print("chicken:{}".format(chicken))
                                    if pig in used_small or chicken in used_small:
                                        # print("day:{}noon:{}不要".format(day,noon))
                                        continue
                            meal_noon.append(meal_name)  # +':'+meal_color
                            meal.loc[index, ("check", "")] = 1
                            small_selected += 1
                        else:
                            continue

                        egg_selected = 0

                if category == "素菜":
                    small_selected = 0
                    leaf_selected = 0
                    other_selected = 0
                    xiafan = 0
                    while not (leaf_selected and other_selected):
                        # 限定最大迭代数量
                        counter += 1
                        if counter == 500:
                            return None

                        index = random.sample(index_list, 1)[0]
                        # 表示这一周没有用过
                        while meal.loc[index, ("check", "")] == 1:
                            index = random.sample(index_list, 1)[0]

                        meal_category = meal.loc[index, ("类别", "")]
                        meal_name = meal.loc[index, ("菜名", "")]
                        meal_target = meal.loc[index, ("适用人群", "")]
                        meal_price = meal.loc[index, ("成本", "")]
                        meal_xiafan = meal.loc[index, ("下饭菜", "")]
                        meal_bean = meal.loc[index, ("是否含豆制品", "")]
                        meal_braise = meal.loc[index, ("烹饪方式", "")]
                        meal_flavor = meal.loc[index, ("味型", "")]
                        meal_main1 = meal.loc[index, ("原料1", "半成品名称")]
                        meal_main2 = meal.loc[index, ("原料2", "半成品名称")]
                        meal_main3 = meal.loc[index, ("原料3", "半成品名称")]
                        meal_main4 = meal.loc[index, ("原料4", "半成品名称")]
                        (
                            qualify,
                            xiafan,
                            used_main[day][noon],
                            has_bean[day],
                            has_braise[day][noon],
                            has_special[day][noon],
                        ) = small_qualify(
                            small_selected,
                            meal_xiafan,
                            xiafan,
                            meal_main1,
                            meal_main2,
                            meal_main3,
                            meal_main4,
                            meal_bean,
                            meal_braise,
                            meal_flavor,
                            used_main[day][noon],
                            has_bean[day],
                            has_braise[day][noon],
                            has_special[day][noon],
                        )
                        if qualify == 1:
                            if meal_category == "叶类" and leaf_selected == 0:
                                leaf_selected = 1
                                small_selected += 1
                                meal_noon.append(meal_name)
                                meal.loc[index, ("check", "")] = 1
                            if meal_category != "叶类" and other_selected == 0:
                                other_selected = 1
                                small_selected += 1
                                meal_noon.append(meal_name)
                                meal.loc[index, ("check", "")] = 1
                        else:
                            continue

                if category == "例汤":
                    soap_selected = 0
                    while soap_selected == 0:
                        # 限定最大迭代数量
                        counter += 1
                        if counter == 500:
                            return None

                        index = random.sample(index_list, 1)[0]
                        # 表示这一周没有用过
                        while meal.loc[index, ("check", "")] == 1:
                            index = random.sample(index_list, 1)[0]
                        meal_category = meal.loc[index, ("类别", "")]
                        meal_name = meal.loc[index, ("菜名", "")]
                        meal_target = meal.loc[index, ("适用人群", "")]
                        meal_price = meal.loc[index, ("成本", "")]
                        meal_bean = meal.loc[index, ("是否含豆制品", "")]
                        meal_braise = meal.loc[index, ("烹饪方式", "")]
                        meal_flavor = meal.loc[index, ("味型", "")]
                        meal_main1 = meal.loc[index, ("原料1", "半成品名称")]
                        meal_main2 = meal.loc[index, ("原料2", "半成品名称")]
                        meal_main3 = meal.loc[index, ("原料3", "半成品名称")]
                        meal_main4 = meal.loc[index, ("原料4", "半成品名称")]
                        (
                            qualify,
                            used_main[day][noon],
                            has_bean[day],
                            has_braise[day][noon],
                            has_special[day][noon],
                        ) = meal_qualify(
                            meal_main1,
                            meal_main2,
                            meal_main3,
                            meal_main4,
                            meal_bean,
                            meal_braise,
                            meal_flavor,
                            used_main[day][noon],
                            has_bean[day],
                            has_braise[day][noon],
                            has_special[day][noon],
                        )
                        if qualify == 1:
                            meal_noon.append(meal_name)
                            meal.loc[index, ("check", "")] = 1
                            soap_selected = 1
                        else:
                            continue
                meal_day.append(meal_noon)
            meal_week.append(meal_day)
        meal.loc[:, ("check", "")] = 0
        return meal_week, has_bean, has_braise, has_special, used_main, used_big_main
    except Exception as e:
        print(e)


def read_menu_excel(filepath: str) -> pd.DataFrame:
    """
    读取带有多级表头的Excel文件，并将其转换为带有MultiIndex列的DataFrame。

    :param filepath: Excel文件路径
    :return: 处理后的DataFrame
    """
    # 确定使用的引擎
    if filepath.endswith(".xls"):
        engine = "xlrd"
    elif filepath.endswith(".xlsx"):
        engine = "openpyxl"
    else:
        raise ValueError("Unsupported file format. Please use .xls or .xlsx files.")

    # 读取前两行作为表头
    df_header = pd.read_excel(
        filepath, sheet_name=0, nrows=2, header=None, engine=engine
    )

    # 填充主类名称（第一行），向下填充NaN值
    main_headers = df_header.iloc[0].ffill().astype(str)
    # print(main_headers)
    # 获取子类名称（第二行），填充NaN为空字符串
    sub_headers = df_header.iloc[1].fillna("").astype(str)

    # 合并主类和子类名称，形成MultiIndex
    combined_headers = []
    for main, sub in zip(main_headers, sub_headers):
        if sub:
            combined_name = (main, sub)
        else:
            combined_name = (main, "")
        combined_headers.append(combined_name)

    # 创建MultiIndex
    multi_index = pd.MultiIndex.from_tuples(combined_headers)
    # 读取数据，跳过前两行
    df_data = pd.read_excel(
        filepath, sheet_name=0, skiprows=2, header=None, engine=engine
    )

    # 分配MultiIndex列名
    df_data.columns = multi_index

    # 转换特定列的数据类型为数值类型
    numeric_keywords = ["切后克重", "出成率", "单价", "成本", "损耗", "调料"]
    # 根据子字段匹配
    numeric_columns = [
        col
        for col in df_data.columns
        if any(keyword in col[1] for keyword in numeric_keywords)
    ]
    for col in numeric_columns:
        df_data[col] = pd.to_numeric(df_data[col], errors="coerce")

    return df_data


def get_result():
    # result = [[[['烤麸烧肉', '家常鸭翅根', '山药鸡片'], ['香辣鸡翅', '白云猪手', '家常鲳鱼']], [['豉椒鱼块', '蒜苔炒腊肉', '红烧蹄膀'], ['家常牛肉', '酱汁大排', '家常鸭翅']], [['花生肉丁', '蒜香鸡块', '马蹄肉圆'], ['香芋烧肉', '盐水基围虾', '莴笋炖肋排']], [['水煮牛柳', '面拖大排', '家常鸭翅根'], ['枸杞鲜笋炖蹄膀', '椒盐鸡柳', '香菇百叶包']], [['马蹄肉圆', '香辣虾', '萝卜烧肉'], ['玉米炖肋排', '红烧鸭块', '双菇鸡片']], [['如意蛋卷', '干锅仔鸡', '干豇豆烧肉'], ['青椒回锅肉', '全家福', '红烧肉方']], [['芋艿烧肉', '麻辣鸭块', '金针菇滑鸡丝'], ['三鲜鸡丸', '芝香大排', '莲藕狮子头']]], [[['豇豆香干鸡丝', '地瓜咸肉片'], ['开洋炖蛋', '佛手瓜肉片']], [['西红柿炒蛋', '西葫芦木耳鸡片'], ['芹菜豆干肉丝', '大蒜炒腊肉']], [['虾仁蒸蛋', '素鸡白菜肉片'], ['开洋炖蛋', '鱼香素鸡']], [['毛豆南瓜肉片', '莴笋木耳鸡片'], ['香干黄瓜肉片', '蒜苔素肠肉片']], [['丝瓜炒蛋', '茄子肉丝'], ['酸豇豆百叶鸡丝', '双花肉片']], [['毛豆茭白肉丁', '素鸡南瓜肉片'], ['青豆玉米鸡丁', '雪菜百叶肉丝']], [['胡萝卜黄瓜肉丁', '莴笋方腿片'], ['豇豆肉片', '芹菜香干肉丝']]], [[['葱油海带丝', '青菜百叶丝'], ['芹菜银芽', '蒜泥杭白菜']], [['云丝银芽', '香菇青菜'], ['雪菜黄豆芽', '红椒菠菜']], [['芹菜土豆丝', '清炒鸡毛菜'], ['韭菜银芽', '油豆腐卷心菜']], [['醋溜白菜', '冬瓜毛豆'], ['青菜腐竹', '油焖茭白']], [['玉米南瓜', '番茄卷心菜'], ['香菜百叶黄豆芽', '麻油生菜']], [['炒青菜', '青椒茭白丝'], ['芹菜海带银芽丝', '面筋白菜']], [['雪菜花生', '清炒空心菜'], ['木耳地瓜片', '面筋青菜']]], [[['西红柿豆腐汤'], ['土豆牛肉羹']], [['荠菜肉丝豆腐羹'], ['油豆腐粉丝汤']], [['香菇肉丝冬瓜汤'], ['香菇咸肉冬瓜汤']], [['蘑菇肉丝蛋汤'], ['番茄蛋汤']], [['扁尖冬瓜汤'], ['虾皮冬瓜汤']], [['紫菜冬瓜汤'], ['萝卜鸡块汤']], [['榨菜肉丝蛋汤'], ['酸辣汤']]]]
    # return result
    # 指定Excel文件路径
    filepath = "app/data/new_meal_list.xls"  # 替换为您的Excel文件路径

    # 读取并处理Excel文件
    meal_list = read_menu_excel(filepath)

    # 要求：1.大荤配置：肉 + 鸡、鸭、鹅  鸡鸭鹅一天吃两种，第一天和第二天的时间要错开
    #      2.小荤  蛋 + 鸡丝 + 肉丝
    #      3.素菜 豆制品、绿叶菜、根茎、果实类
    #      4.一周菜品不重复
    meal_list[("check", "")] = 0
    meal_list[("是否含豆制品", "")] = 0
    meal_list[("成本", "")] = "适中"
    meal_list[("适用人群", "")] = "全部"
    meal_list[("下饭菜", "")] = "是"
    meal_list.loc[meal_list[("类别", "")] == "豆制品", ("是否含豆制品", "")] = 1
    meal_list.loc[meal_list[("类别", "")].isin(["牛肉类", "虾类"]), ("成本", "")] = "高"

    大荤 = meal_list[meal_list[("品种", "")] == "大荤"].reset_index(drop=True)

    小荤 = meal_list[meal_list[("品种", "")] == "小荤"].reset_index(drop=True)

    素菜 = meal_list[meal_list[("品种", "")] == "素菜"].reset_index(drop=True)

    例汤 = meal_list[meal_list[("品种", "")] == "汤"].reset_index(drop=True)
    has_bean = [0 for _ in range(7)]
    has_braise = [[0, 0] for _ in range(7)]
    has_special = [[0, 0] for _ in range(7)]
    used_main = [[[], []] for _ in range(7)]
    try:
        d = select_meal(例汤, "例汤", has_bean, has_braise, has_special, used_main)
        if d is None:
            return None
        else:
            print("d")
        b = select_meal(小荤, "小荤", d[1], d[2], d[3], d[4])
        if b is None:
            return None
        else:
            print("b")
        a = select_meal(大荤, "大荤", b[1], b[2], b[3], b[4])
        if a is None:
            return None
        else:
            print("a")
        c = select_meal(素菜, "素菜", a[1], a[2], a[3], a[4])
        if c is None:
            return None
        else:
            print("c")
        a_week_menu = [a[0], b[0], c[0], d[0]]
        return a_week_menu
    except Exception as e:
        print(e)


if __name__ == "__main__":
    while True:
        result = get_result()
        if result is not None:
            break
