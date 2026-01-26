# Postman API 测试指南

## 前置准备

1. **启动后端服务**
   ```bash
   cd backend
   python wsgi.py
   ```
   服务将在 `http://127.0.0.1:5000` 启动

2. **测试账号**（来自 `init_db.py`）
   - 超级管理员: `superadmin` / `admin123`
   - 管理员: `admin` / `admin123`
   - 普通员工: `staff1` / `user123`
   - 客户1: `customer1` / `customer123` (关联公司A)
   - 客户2: `customer2` / `customer123` (关联公司B)

---

## 步骤 1：登录获取 Token

### 请求配置

- **Method**: `POST`
- **URL**: `http://127.0.0.1:5000/api/auth/login`
- **Headers**: 
  ```
  Content-Type: application/json
  ```
- **Body** (raw JSON):
  ```json
  {
    "username": "superadmin",
    "password": "admin123"
  }
  ```

### 响应示例

```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "username": "superadmin",
    "role": "superadmin",
    "company_id": null
  }
}
```

### 保存 Token

1. 复制响应中的 `access_token` 值
2. 在 Postman 中，点击右上角的 **Environment** 图标（或使用快捷键 `Ctrl+E` / `Cmd+E`）
3. 创建新环境或使用现有环境
4. 添加变量：
   - **Variable**: `token`
   - **Initial Value**: 粘贴刚才复制的 token
   - **Current Value**: 同样粘贴 token

---

## 步骤 2：设置 Authorization Header

### 方法一：使用 Environment Variable（推荐）

1. 在 Postman 请求的 **Authorization** 标签页
2. **Type**: 选择 `Bearer Token`
3. **Token**: 输入 `{{token}}`（使用环境变量）

### 方法二：手动设置 Header

1. 在请求的 **Headers** 标签页
2. 添加 Header：
   - **Key**: `Authorization`
   - **Value**: `Bearer {{token}}` 或直接粘贴完整的 token

### 方法三：使用 Pre-request Script（自动获取）

在 Postman Collection 的 **Pre-request Script** 中添加：

```javascript
// 自动登录并获取 token（如果 token 不存在或过期）
if (!pm.environment.get("token")) {
    pm.sendRequest({
        url: 'http://127.0.0.1:5000/api/auth/login',
        method: 'POST',
        header: {
            'Content-Type': 'application/json'
        },
        body: {
            mode: 'raw',
            raw: JSON.stringify({
                username: 'superadmin',
                password: 'admin123'
            })
        }
    }, function (err, res) {
        if (res.json().access_token) {
            pm.environment.set("token", res.json().access_token);
        }
    });
}
```

---

## 步骤 3：测试不同角色的接口

### 3.1 客户管理接口（需要 admin/superadmin）

#### 获取客户列表
- **Method**: `GET`
- **URL**: `http://127.0.0.1:5000/api/companies`
- **Authorization**: `Bearer {{token}}`
- **Query Params** (可选):
  - `keyword`: 搜索关键词

#### 创建客户（仅 admin/superadmin）
- **Method**: `POST`
- **URL**: `http://127.0.0.1:5000/api/companies`
- **Authorization**: `Bearer {{token}}`
- **Body** (raw JSON):
  ```json
  {
    "name": "测试公司",
    "address": "测试地址",
    "contact_person": "联系人",
    "contact_phone": "13800138000"
  }
  ```

#### 更新客户（仅 admin/superadmin）
- **Method**: `PUT`
- **URL**: `http://127.0.0.1:5000/api/companies/1`
- **Authorization**: `Bearer {{token}}`
- **Body** (raw JSON):
  ```json
  {
    "contact_person": "新联系人",
    "contact_phone": "13900139000"
  }
  ```

#### 删除客户（仅 admin/superadmin）
- **Method**: `DELETE`
- **URL**: `http://127.0.0.1:5000/api/companies/1`
- **Authorization**: `Bearer {{token}}`

---

### 3.2 餐标配置接口

#### 获取餐标列表（所有角色）
- **Method**: `GET`
- **URL**: `http://127.0.0.1:5000/api/meal-standards`
- **Authorization**: `Bearer {{token}}`
- **Query Params** (可选):
  - `status`: `enabled` 或 `disabled`

#### 创建餐标（仅 admin/superadmin）
- **Method**: `POST`
- **URL**: `http://127.0.0.1:5000/api/meal-standards`
- **Authorization**: `Bearer {{token}}`
- **Body** (raw JSON):
  ```json
  {
    "name": "测试餐标",
    "meal_type": "lunch",
    "price": 25.0,
    "status": "enabled",
    "description": "测试描述"
  }
  ```

#### 更新餐标（仅 admin/superadmin）
- **Method**: `PUT`
- **URL**: `http://127.0.0.1:5000/api/meal-standards/1`
- **Authorization**: `Bearer {{token}}`
- **Body** (raw JSON):
  ```json
  {
    "price": 30.0,
    "status": "disabled"
  }
  ```

---

### 3.3 订单管理接口

#### 获取订单列表
- **Method**: `GET`
- **URL**: `http://127.0.0.1:5000/api/orders`
- **Authorization**: `Bearer {{token}}`
- **Query Params** (可选):
  - `order_date`: `2024-01-15`
  - `company_id`: `1`
  - `status`: `submitted` 或 `closed`
- **注意**: customer 角色只能看到自己公司的订单

#### 创建订单（仅 customer）
- **Method**: `POST`
- **URL**: `http://127.0.0.1:5000/api/orders`
- **Authorization**: `Bearer {{token}}` (使用 customer1 或 customer2 的 token)
- **Body** (raw JSON):
  ```json
  {
    "order_date": "2024-01-16",
    "items": [
      {
        "meal_standard_id": 1,
        "quantity": 100,
        "unit_price": 25.0
      }
    ]
  }
  ```

#### 获取订单详情
- **Method**: `GET`
- **URL**: `http://127.0.0.1:5000/api/orders/1`
- **Authorization**: `Bearer {{token}}`

#### 修改订单（仅 admin/superadmin）
- **Method**: `PUT`
- **URL**: `http://127.0.0.1:5000/api/orders/1`
- **Authorization**: `Bearer {{token}}`
- **Body** (raw JSON):
  ```json
  {
    "status": "closed",
    "items": [
      {
        "meal_standard_id": 1,
        "quantity": 150,
        "unit_price": 25.0
      }
    ]
  }
  ```

---

### 3.4 物流管理接口

#### 获取物流列表
- **Method**: `GET`
- **URL**: `http://127.0.0.1:5000/api/logistics`
- **Authorization**: `Bearer {{token}}`
- **Query Params** (可选):
  - `order_date`: `2024-01-15`
- **注意**: customer 角色只能看到自己公司的物流

#### 更新物流阶段
- **Method**: `POST`
- **URL**: `http://127.0.0.1:5000/api/logistics/1/update_stage`
- **Authorization**: `Bearer {{token}}`
- **Body** (raw JSON):
  ```json
  {
    "stage": "prepare_loaded"
  }
  ```
- **阶段说明**:
  - `prepare_loaded`: 备餐装车（仅 admin/superadmin）
  - `shipping`: 运输中（仅 admin/superadmin）
  - `arrived`: 已到达（admin/superadmin/user）
  - `recycled`: 已回收（admin/superadmin/user）

---

### 3.5 用户管理接口（仅 superadmin）

#### 获取用户列表（仅 admin/superadmin）
- **Method**: `GET`
- **URL**: `http://127.0.0.1:5000/api/users`
- **Authorization**: `Bearer {{token}}`
- **Query Params** (可选):
  - `keyword`: 搜索关键词
  - `role`: 角色筛选
  - `company_id`: 公司筛选

#### 创建用户（仅 superadmin）
- **Method**: `POST`
- **URL**: `http://127.0.0.1:5000/api/users`
- **Authorization**: `Bearer {{token}}` (必须是 superadmin)
- **Body** (raw JSON):
  ```json
  {
    "username": "newuser",
    "password": "password123",
    "role": "user",
    "company_id": null
  }
  ```
  或创建客户账号：
  ```json
  {
    "username": "newcustomer",
    "password": "password123",
    "role": "customer",
    "company_id": 1
  }
  ```

#### 更新用户（仅 superadmin）
- **Method**: `PUT`
- **URL**: `http://127.0.0.1:5000/api/users/1`
- **Authorization**: `Bearer {{token}}` (必须是 superadmin)
- **Body** (raw JSON):
  ```json
  {
    "password": "newpassword123",
    "role": "admin"
  }
  ```

#### 删除用户（仅 superadmin）
- **Method**: `DELETE`
- **URL**: `http://127.0.0.1:5000/api/users/1`
- **Authorization**: `Bearer {{token}}` (必须是 superadmin)
- **注意**: 不能删除自己

---

## 测试不同角色的权限

### 测试流程

1. **使用 superadmin 登录**，获取 token，测试所有接口
2. **使用 admin 登录**，获取 token，测试：
   - ✅ 客户管理（CRUD）
   - ✅ 餐标配置（CRUD）
   - ✅ 订单查看和修改
   - ✅ 物流管理（全部阶段）
   - ❌ 用户管理（应该返回 403）
3. **使用 user 登录**，获取 token，测试：
   - ✅ 订单查看
   - ✅ 物流查看
   - ✅ 物流阶段确认（仅 arrived/recycled）
   - ❌ 客户管理（应该返回 403）
   - ❌ 餐标配置（应该返回 403）
4. **使用 customer1 登录**，获取 token，测试：
   - ✅ 创建订单
   - ✅ 查看订单（仅自己公司的）
   - ✅ 查看物流（仅自己公司的）
   - ❌ 修改订单（应该返回 403）
   - ❌ 其他管理功能（应该返回 403）

---

## 常见错误处理

### 401 Unauthorized
- **原因**: Token 无效或已过期
- **解决**: 重新登录获取新的 token

### 403 Forbidden
- **原因**: 当前角色没有权限访问该接口
- **解决**: 使用具有相应权限的角色账号登录

### 400 Bad Request
- **原因**: 请求参数错误或缺失
- **解决**: 检查请求 Body 和 Query Params 是否符合 API 要求

---

## Postman Collection 导入

你可以创建一个 Postman Collection，包含所有接口的预配置请求。建议结构：

```
中央厨房管理平台 API
├── 认证
│   └── 登录
├── 客户管理
│   ├── 获取客户列表
│   ├── 创建客户
│   ├── 更新客户
│   └── 删除客户
├── 餐标配置
│   ├── 获取餐标列表
│   ├── 创建餐标
│   └── 更新餐标
├── 订单管理
│   ├── 获取订单列表
│   ├── 创建订单
│   ├── 获取订单详情
│   └── 修改订单
├── 物流管理
│   ├── 获取物流列表
│   └── 更新物流阶段
└── 用户管理
    ├── 获取用户列表
    ├── 创建用户
    ├── 更新用户
    └── 删除用户
```

---

## 快速测试脚本

在 Postman 的 **Tests** 标签页中添加以下脚本，自动保存 token：

```javascript
// 登录接口的 Tests 脚本
if (pm.response.code === 200) {
    var jsonData = pm.response.json();
    if (jsonData.access_token) {
        pm.environment.set("token", jsonData.access_token);
        pm.environment.set("user_role", jsonData.user.role);
        console.log("Token saved:", jsonData.access_token);
        console.log("User role:", jsonData.user.role);
    }
}
```

这样每次登录成功后，token 会自动保存到环境变量中。

