"""
数据库初始化脚本
运行方式: python init_db.py
"""
from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.company import Company
from app.models.meal_standard import MealStandard


def init_database():
    app = create_app()
    with app.app_context():
        # 删除所有表（谨慎使用，仅用于开发环境）
        db.drop_all()
        # 创建所有表
        db.create_all()

        # 创建超级管理员账号
        superadmin = User(
            username="superadmin",
            role="superadmin",
        )
        superadmin.set_password("admin123")
        db.session.add(superadmin)

        # 创建管理员账号
        admin = User(
            username="admin",
            role="admin",
        )
        admin.set_password("admin123")
        db.session.add(admin)

        # 创建普通员工账号
        user = User(
            username="staff1",
            role="user",
        )
        user.set_password("user123")
        db.session.add(user)

        # 创建示例客户公司
        company1 = Company(
            name="示例客户公司A",
            contact_person="张三",
            contact_phone="13800138000",
            address="北京市朝阳区示例街道123号",
        )
        db.session.add(company1)

        company2 = Company(
            name="示例客户公司B",
            contact_person="李四",
            contact_phone="13900139000",
            address="上海市浦东新区示例路456号",
        )
        db.session.add(company2)

        # 创建客户账号（关联到公司）
        customer1 = User(
            username="customer1",
            role="customer",
            company_id=1,  # 关联到 company1
        )
        customer1.set_password("customer123")
        db.session.add(customer1)

        customer2 = User(
            username="customer2",
            role="customer",
            company_id=2,  # 关联到 company2
        )
        customer2.set_password("customer123")
        db.session.add(customer2)

        # 创建示例餐标
        meal1 = MealStandard(
            name="标准工作餐A",
            meal_type="lunch",
            price=25.0,
            status="enabled",
            description="一荤两素",
        )
        db.session.add(meal1)

        meal2 = MealStandard(
            name="标准工作餐B",
            meal_type="lunch",
            price=30.0,
            status="enabled",
            description="两荤一素",
        )
        db.session.add(meal2)

        meal3 = MealStandard(
            name="早餐套餐",
            meal_type="breakfast",
            price=15.0,
            status="enabled",
            description="包子+豆浆+鸡蛋",
        )
        db.session.add(meal3)

        db.session.commit()

        print("数据库初始化完成！")
        print("\n测试账号：")
        print("  超级管理员: superadmin / admin123")
        print("  管理员: admin / admin123")
        print("  普通员工: user / user123")
        print("  客户1: customer1 / customer123 (关联公司A)")
        print("  客户2: customer2 / customer123 (关联公司B)")


if __name__ == "__main__":
    init_database()
