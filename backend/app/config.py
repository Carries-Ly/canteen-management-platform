import os
from datetime import timedelta


class Config:
    # MySQL 数据库配置
    DB_HOST = os.getenv("DB_HOST", "121.199.16.11")
    DB_PORT = os.getenv("DB_PORT", "3306")
    DB_USER = os.getenv("DB_USER", "bqlmenu")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "root")
    DB_NAME = os.getenv("DB_NAME", "canteen")

    # 构建数据库连接 URI
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        f"?charset=utf8mb4"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT 配置
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "594188lxc")
    # JWT Token 过期时间（默认24小时，可根据需要修改）
    # 示例：
    #   timedelta(hours=24)      - 24小时
    #   timedelta(days=7)        - 7天
    #   timedelta(hours=1)       - 1小时
    #   timedelta(minutes=30)    - 30分钟
    #   也可以从环境变量读取：os.getenv("JWT_ACCESS_TOKEN_EXPIRES", "24")  # 小时数
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
