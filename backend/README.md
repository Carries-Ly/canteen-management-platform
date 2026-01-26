# 中央厨房管理平台 - 后端

## 技术栈

- Flask 3.0.0
- Flask-SQLAlchemy (ORM)
- Flask-Migrate (数据库迁移)
- Flask-JWT-Extended (JWT 认证)
- SQLite (默认，可切换为 MySQL/PostgreSQL)

## 快速开始

### 1. 安装依赖

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. 初始化数据库

```bash
python init_db.py
```

这会创建所有数据表，并插入测试账号和示例数据。

**测试账号：**
- 超级管理员: `superadmin` / `admin123`
- 管理员: `admin` / `admin123`
- 普通员工: `user` / `user123`
- 客户1: `customer1` / `customer123` (关联公司A)
- 客户2: `customer2` / `customer123` (关联公司B)

### 3. 启动服务

```bash
python wsgi.py
```

服务将在 `http://127.0.0.1:5000` 启动。

## API 接口

### 认证
- `POST /api/auth/login` - 用户登录

### 客户管理（仅 superadmin/admin）
- `GET /api/companies` - 获取客户列表（支持 keyword 搜索）
- `GET /api/companies/<id>` - 获取客户详情
- `POST /api/companies` - 创建新客户
- `PUT /api/companies/<id>` - 更新客户信息
- `DELETE /api/companies/<id>` - 删除客户

### 餐标管理
- `GET /api/meal-standards` - 获取餐标列表（所有角色可查看）
- `POST /api/meal-standards` - 创建餐标（仅 superadmin/admin）
- `PUT /api/meal-standards/<id>` - 更新餐标（仅 superadmin/admin）

### 订单管理
- `GET /api/orders` - 获取订单列表
- `POST /api/orders` - 创建订单（仅 customer）
- `GET /api/orders/<id>` - 获取订单详情

### 物流管理
- `GET /api/logistics` - 获取物流列表
- `POST /api/logistics/<order_id>/update_stage` - 更新物流阶段

## 数据库配置

### MySQL 配置（已配置为远程 MySQL 服务器）

项目已配置为连接 MySQL 数据库（服务器：121.199.16.11:3306）。

**方式一：使用环境变量（推荐）**

创建 `.env` 文件（在 `backend` 目录下）：

```bash
# 数据库配置
DB_HOST=121.199.16.11
DB_PORT=3306
DB_USER=your_username
DB_PASSWORD=your_password
DB_NAME=canteen

# JWT 密钥（生产环境请使用强随机字符串）
JWT_SECRET_KEY=your-secret-key-here
```

**方式二：直接设置环境变量**

```bash
export DB_HOST=121.199.16.11
export DB_PORT=3306
export DB_USER=your_username
export DB_PASSWORD=your_password
export DB_NAME=canteen
export JWT_SECRET_KEY=your-secret-key-here
```

**注意：**
- 请确保 MySQL 服务器已创建数据库（如 `canteen`）
- 确保数据库用户有足够的权限（CREATE、ALTER、INSERT、SELECT、UPDATE、DELETE）
- 如果使用 `.env` 文件，需要安装 `python-dotenv`（已在 requirements.txt 中）

### 初始化数据库

配置好环境变量后，运行：

```bash
python init_db.py
```

这会自动创建所有数据表。

## 使用 Flask-Migrate（可选）

如果需要使用迁移工具管理数据库变更：

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```
