# 中央厨房管理平台 - 功能设计计划书

## 1. 项目概述

**项目名称**：中央厨房食堂服务公司管理平台  
**业务背景**：一家送餐公司（内部员工：superadmin/admin/user）为多个客户企业（customer）提供每日订餐服务，需要管理订单、餐标、物流状态等。平台兼容生产环节管理，包括菜单生成、库存管理、采购清单等功能。  
**技术栈**：
- 后端：Python Flask + SQLAlchemy + JWT + MySQL
- 前端：Vue3 + Vite + Element Plus + Pinia + ECharts
- 数据库：MySQL（服务器：121.199.16.11:3306）
- 外部设备：电子秤（通过模拟接口集成，后续可对接真实设备）
- 文件处理：Excel（xlsx）菜单库文件解析

---

## 2. 角色与权限边界（核心约束）

### 2.1 角色定义

- **superadmin**：送餐公司最高管理员（系统配置、全部数据管理）
- **admin**：送餐公司管理员（业务数据管理：客户、餐标、订单、物流）
- **user**：送餐公司普通员工（业务查看 + 部分物流确认）
- **customer**：客户企业账号（仅本企业：下单 + 查看订单/物流）

### 2.2 权限矩阵

| 模块 | customer | user | admin | superadmin |
|------|----------|------|-------|------------|
| 登录/退出 | ✅ | ✅ | ✅ | ✅ |
| 客户管理（企业客户信息） | ❌ | 只读（可选） | ✅ CRUD | ✅ CRUD |
| 餐标配置（餐标+金额） | 只读（用于下单选择） | 只读 | ✅ CRUD | ✅ CRUD |
| 订单管理 | ✅ 创建/查看(仅本企业) | ✅ 查看(全部客户) | ✅ 查看/修改 | ✅ 查看/修改 |
| 物流管理（4阶段） | ✅ 查看(仅本企业) | ✅ 确认到达/回收 | ✅ 确认全阶段 | ✅ 确认全阶段 |
| 员工管理（admin/user） | ❌ | ❌ | ❌ | ✅ CRUD |
| 一周总菜单生成 | ❌ | ✅ 查看 | ✅ 生成/查看 | ✅ 生成/查看 |
| 子菜单选取与生成 | ❌ | ✅ 查看 | ✅ 选择/生成/查看 | ✅ 选择/生成/查看 |
| 库存管理 | ❌ | ✅ CRUD | ✅ CRUD | ✅ CRUD |
| 采购清单生成 | ❌ | ✅ 生成/查看 | ✅ 生成/查看 | ✅ 生成/查看 |
| 权限管理/账号管理 | 仅自账号（可选） | 仅自账号（可选） | 可创建 customer（可选） | ✅ 全部账号管理 |

> **说明**：是否允许 `admin` 创建客户企业账号/重置密码，可按实际运营流程决定。

---

## 3. 功能模块化设计（页面 + 业务能力）

### 3.1 登录与权限模块（Auth/RBAC）

**页面**：
- `登录页 /login`：用户名+密码，登录成功跳转主布局

**关键能力**：
- JWT 登录鉴权
- 前端路由守卫（基于 `role`）
- 菜单按角色动态显示

**字段解释（用户）**：
- `username`：登录名（唯一）
- `password_hash`：密码哈希
- `role`：角色（枚举：superadmin/admin/user/customer）
- `company_id`：仅 `customer` 绑定客户企业，用于数据隔离

---

### 3.2 客户管理模块（企业客户 Company）

**页面**：
- `客户列表`：支持搜索、分页（可选）、新增/编辑/删除（admin/superadmin）
- `客户详情`：展示企业信息、创建时间、关联订单/账号（可选）

**关键能力**：
- 管理客户企业基本资料（名称、地址、联系人、联系方式、添加时间）
- 删除前检查：是否存在关联订单/客户账号

**字段解释（客户企业）**：
- `id`：主键
- `name`：企业客户名称（唯一建议）
- `address`：配送地址/企业地址
- `contact_person`：联系人姓名
- `contact_phone`：联系方式（手机号/座机）
- `created_at`：添加时间（服务端自动生成）

---

### 3.3 餐标配置模块（MealStandard）

**业务背景**：餐标由送餐公司维护，客户企业下单时只能从“启用的餐标”选择；金额默认带出；订单层可允许 admin/superadmin 改价（不影响基础餐标价）。

**页面**：
- `餐标配置 /meal-standards`
  - 列表：餐标名称、餐别、单价、状态、备注
  - 新增/编辑弹窗（admin/superadmin）

**字段解释（餐标）**：
- `id`：主键
- `name`：餐标名称（如"标准工作餐A"）
- `meal_type`：餐别（中文：`早餐/午餐/晚餐/夜宵`）
- `price`：默认单价（元）
- `status`：`enabled/disabled`（决定是否可被 customer 下单选择）
- `description`：备注说明（可选）

---

### 3.4 订单管理模块（Order + OrderItem）

**业务流程**：
- `customer`：每天提交“**次日订单**”（选择餐标 + 数量）
- `user`：查看各企业订单情况（按日期/企业/状态）
- `admin/superadmin`：查看 + 修改订单（如改数量、改价、关闭订单）

**页面**：
- `订单列表 /orders`
  - **user/admin/superadmin 视图**：
    - 筛选：日期筛选框、公司名称搜索框
    - 列表：客户公司、订单日期、订单餐别、餐标名称、数量、单价、总价、状态、物流阶段、操作
    - 表格展示：同一公司同一天的订单，公司名称和订单日期单元格合并，按餐别分行展示
    - 操作：查看详情、确认接收订单（user/admin/superadmin）、编辑订单（admin/superadmin）、删除订单（admin/superadmin）
  - **customer 视图**：
    - 筛选：日期筛选框、状态筛选框（"已提交，等待确认"/"订餐已收到"）
    - 创建订单：填写日期、明细（选择餐别、选择餐标、显示单价、填写数量），支持同一天添加多个明细
    - 订单子board：展示本企业某日所有订单
- `订单详情 /orders/:id`
  - 订单基本信息 + 明细项列表
  - 物流步骤可视化（Steps + ECharts 状态图）

**字段解释（订单）**：
- `id`：主键
- `company_id`：客户企业 ID
- `order_date`：订餐日期（通常为明天）
- `status`：订单状态
  - `已提交，等待确认`：客户提交订单后的初始状态
  - `订餐已收到`：管理员确认接收后的状态
  - `closed`：已关闭（保留兼容）
- `created_at` / `updated_at`：创建/更新时间

**字段解释（订单明细 OrderItem）**：
- `id`：主键
- `order_id`：订单 ID
- `meal_standard_id`：关联餐标（用于追溯）
- `meal_name`：下单快照（防止餐标改名影响历史）
- `meal_type`：下单快照
- `unit_price`：下单快照单价（允许订单层改价）
- `quantity`：数量（份数）

---

### 3.5 运餐物流模块（Logistics，四阶段）

**阶段定义（固定四步）**：
1. `备餐装车中`（prepare_loaded）
2. `订餐运输中`（shipping）
3. `订餐已到达`（arrived）
4. `订餐已回收`（recycled）

**角色操作规则**：
- `customer`：只读查看本企业订单物流阶段 + 时间
- `user`：可确认 **已到达 / 已回收**
- `admin/superadmin`：可确认 **全部阶段**

**页面**：
- `物流总览 /logistics`
  - **user/admin/superadmin 视图**：
    - 筛选条件：餐别（meal_type）和日期（复合筛选）
    - 统计图表：展示某天某餐的四种状态的订单完成数量（ECharts 柱状图）
    - 企业客户子board：
      - 企业客户批量勾选（全选/取消全选）
      - 多个步骤图（el-steps）展示被勾选企业的运餐物流状态
      - 每个企业可单独确认物流状态（勾选框 + 确认按钮）
      - 批量确认功能：选择多个企业，统一确认选中状态
  - **customer 视图**：
    - 筛选条件：餐别（meal_type）和日期（复合筛选）
    - 企业物流状态子board：
      - 一个步骤图（el-steps）展示本企业的运餐物流状态
      - 只读查看，不能操作
- `订单详情内嵌物流视图`
  - `el-steps` 显示四步完成情况
  - ECharts 状态图/柱状统计用于直观展示

**字段解释（物流）**：
- `id`：主键
- `order_id`：一对一关联订单
- `stage_prepare_loaded` / `time_prepare_loaded`：备餐装车阶段/时间
- `stage_shipping` / `time_shipping`：运输阶段/时间
- `stage_arrived` / `time_arrived`：到达阶段/时间
- `stage_recycled` / `time_recycled`：回收阶段/时间

> **建议补充约束**：阶段按顺序推进（不允许跳步），并记录操作者 `operator_user_id`（可选）用于审计。

---

### 3.6 员工管理模块（Staff Management）

**业务背景**：送餐公司内部员工（admin 和 user）的账号管理，由 superadmin 统一管理，包括创建、编辑、删除、重置密码等操作。

**页面**：
- `员工管理 /staff`（仅 superadmin 可见）
  - 列表：用户名、角色（admin/user）、创建时间、最后登录时间（可选）
  - 筛选：按角色筛选（admin/user）
  - 操作：新增员工、编辑信息、重置密码、删除账号

**关键能力**：
- 创建 admin 和 user 角色的员工账号
- 编辑员工信息（用户名、角色）
- 重置员工密码（生成临时密码或由 superadmin 设置）
- 删除员工账号（需检查是否有关联操作记录，建议软删除或限制删除）

**字段解释（员工账号，复用 User 模型）**：
- `id`：主键
- `username`：登录名（唯一）
- `password_hash`：密码哈希
- `role`：角色（仅 `admin` 或 `user`，不包含 `customer` 和 `superadmin`）
- `company_id`：为空（内部员工不绑定客户企业）

**业务规则**：
- 只能管理 `role` 为 `admin` 或 `user` 的账号
- 不能删除或修改 `superadmin` 账号（系统保护）
- 不能将员工账号改为 `customer` 角色（customer 账号由客户管理模块创建）
- 删除前建议检查：是否有操作记录、是否正在使用等

---

### 3.7 一周总菜单生成模块（Weekly Menu Generation）

**业务背景**：系统已有菜单生成算法，需要适配到平台进行可视化展示和管理。总菜单是一周7天（周一到周日）的完整菜单，包含每天的早餐、午餐、晚餐、夜宵等餐别的菜品安排。

**页面**：
- `一周总菜单 /weekly-menu`（user/admin/superadmin）
  - **生成总菜单**：
    - 选择周次（年-周数，如 2024-W01）
    - 调用菜单生成算法生成一周菜单
    - 可视化展示：周一到周日的表格视图，每行代表一天，每列代表一个餐别
    - 支持手动调整菜品（拖拽替换、删除、添加）
    - 保存总菜单
  - **查看历史总菜单**：
    - 按周次筛选查看历史总菜单
    - 支持查看、导出（Excel/PDF）

**关键能力**：
- 调用已有菜单生成算法生成一周菜单
- 可视化展示一周菜单（表格/日历视图）
- 支持手动编辑和调整
- 保存和管理历史总菜单

**字段解释（总菜单 WeeklyMenu）**：
- `id`：主键
- `week_year`：年份（如 2024）
- `week_number`：周数（1-53）
- `week_start_date`：周开始日期（周一）
- `week_end_date`：周结束日期（周日）
- `status`：状态（`draft` 草稿 / `published` 已发布）
- `created_by`：创建人 ID
- `created_at` / `updated_at`：创建/更新时间

**字段解释（总菜单明细 WeeklyMenuItem）**：
- `id`：主键
- `weekly_menu_id`：总菜单 ID
- `day_of_week`：星期几（1-7，1=周一）
- `meal_type`：餐别（早餐/午餐/晚餐/夜宵）
- `dish_name`：菜品名称
- `dish_category`：菜品分类（可选，如：荤菜/素菜/汤/主食）
- `sort_order`：排序（同一餐别内的顺序）

---

### 3.8 子菜单选取与生成模块（Sub Menu Selection）

**业务背景**：在总菜单生成后，superadmin/admin 可以为不同的客户企业选择子菜单。子菜单是从总菜单中选取的某几天或某些菜品组合，适用于特定客户企业。

**页面**：
- `子菜单管理 /sub-menu`（user/admin/superadmin）
  - **选择子菜单**：
    - 选择已生成的总菜单（周次）
    - 打开子菜单选择窗口，展示总菜单（可视化表格）
    - 通过点击/拖拽方式选择子菜单：
      - 可以选择整天的菜单（周一全部、周二全部等）
      - 可以选择某天的某个餐别（周一午餐、周二晚餐等）
      - 可以选择具体菜品
    - 确认选择的子菜单后，选择适用的公司客户（可多选）
    - 保存子菜单关联
  - **历史菜单查看**：
    - 查看历史总菜单列表
    - 选择客户企业，查看该企业的历史子菜单
    - 支持按周次、客户企业筛选

**关键能力**：
- 从总菜单中灵活选择子菜单（支持多种选择方式）
- 将子菜单关联到客户企业
- 查看历史总菜单和子菜单
- customer 只能查看自己公司的历史子菜单

**字段解释（子菜单 SubMenu）**：
- `id`：主键
- `weekly_menu_id`：关联的总菜单 ID
- `company_id`：客户企业 ID
- `name`：子菜单名称（可选，如"公司A-第1周菜单"）
- `status`：状态（`draft` / `confirmed` 已确认）
- `created_by`：创建人 ID
- `created_at` / `updated_at`：创建/更新时间

**字段解释（子菜单明细 SubMenuItem）**：
- `id`：主键
- `sub_menu_id`：子菜单 ID
- `weekly_menu_item_id`：关联的总菜单明细 ID（用于追溯）
- `day_of_week`：星期几
- `meal_type`：餐别
- `dish_name`：菜品名称（快照）
- `dish_category`：菜品分类（快照）

**业务规则**：
- 一个客户企业可以有多份子菜单（不同周次）
- 同一周次可以为不同客户企业选择不同的子菜单
- customer 只能查看自己公司的子菜单，不能修改

---

### 3.9 库存管理模块（Inventory Management）

**业务背景**：管理中央厨房的食材库存，包括入库、出库、库存查询等功能。入库和出库都需要连接外部电子秤进行自动称重。

**页面**：
- `库存管理 /inventory`（user/admin/superadmin，customer 不可见）
  - **库存列表**：
    - 展示所有食材的当前库存数量、入库日期、保质期等
    - 支持按食材名称、分类筛选
    - 支持按库存数量、入库日期排序
  - **入库操作**：
    - 选择菜品/食材
    - 连接外部电子秤（模拟接口）
    - 上秤自动称量，显示重量
    - 确认后入库，记录入库日期、数量、操作人等
  - **出库操作**：
    - 选择出库类型：
      - **关联采购单出库**：选择采购单，自动关联出库
      - **手动出库**：填写出库单（选择食材、数量、用途等）
    - 连接外部电子秤（模拟接口）
    - 上秤自动称量，确认出库
    - 记录出库日期、数量、操作人、关联采购单（如有）

**关键能力**：
- 食材入库管理（电子秤自动称重）
- 食材出库管理（关联采购单或手动出库）
- 库存实时查询和统计
- 库存预警（低库存提醒、保质期提醒）

**字段解释（食材库 Ingredient）**：
- `id`：主键
- `name`：食材名称（唯一）
- `category`：食材分类（如：蔬菜/肉类/调料/主食等）
- `unit`：单位（如：kg/斤/包/箱）
- `safety_stock`：安全库存（最低库存量）
- `shelf_life_days`：保质期天数（可选）

**字段解释（库存记录 Inventory）**：
- `id`：主键
- `ingredient_id`：食材 ID
- `quantity`：当前库存数量
- `last_in_date`：最后入库日期
- `last_out_date`：最后出库日期
- `updated_at`：更新时间

**字段解释（入库记录 StockIn）**：
- `id`：主键
- `ingredient_id`：食材 ID
- `quantity`：入库数量
- `in_date`：入库日期
- `expiry_date`：保质期到期日期（可选）
- `operator_id`：操作人 ID
- `scale_weight`：电子秤称重值（用于核对）
- `created_at`：创建时间

**字段解释（出库记录 StockOut）**：
- `id`：主键
- `ingredient_id`：食材 ID
- `quantity`：出库数量
- `out_date`：出库日期
- `purchase_order_id`：关联的采购单 ID（可选）
- `purpose`：出库用途（如：生产使用/损耗/退货等）
- `operator_id`：操作人 ID
- `scale_weight`：电子秤称重值（用于核对）
- `created_at`：创建时间

**外部设备集成**：
- **电子秤接口**（模拟）：
  - `GET /api/scale/weight`：获取当前称重值
  - `POST /api/scale/tare`：去皮（清零）
  - 后续可对接真实电子秤设备（串口/USB/API）

---

### 3.10 采购清单生成模块（Purchase List Generation）

**业务背景**：根据生成的菜单和菜单库（xlsx 文件），自动计算所需食材的采购清单和金额。采购清单会展示每个品类的库存数量和入库日期，用户可以选择使用库存或加采购，最终生成采购单。

**页面**：
- `采购清单 /purchase-list`（user/admin/superadmin，customer 不可见）
  - **生成采购清单**：
    - 选择已生成的子菜单（或总菜单）
    - 上传或选择菜单库 xlsx 文件（包含菜品-食材映射关系）
    - 系统自动解析 xlsx，计算所需食材清单
    - 展示采购清单：
      - 食材名称、所需数量、当前库存数量、库存入库日期
      - 可选择：使用库存 / 加采购
      - 显示预估采购金额
    - 调整采购数量后，生成最终采购单
  - **采购单管理**：
    - 查看历史采购单
    - 采购单详情（食材清单、金额、关联菜单等）
    - 导出采购单（Excel/PDF）

**关键能力**：
- 解析菜单库 xlsx 文件（菜品-食材映射关系）
- 根据菜单自动计算食材需求
- 结合库存信息，生成采购清单
- 支持手动调整采购数量
- 生成最终采购单和预估金额

**字段解释（菜单库文件 MenuLibrary）**：
- 存储在服务器文件系统或数据库
- xlsx 格式，包含以下信息：
  - **菜品表**：菜品名称、餐别、分类等
  - **食材表**：食材名称、单位、单价等
  - **菜品-食材映射表**：菜品名称、食材名称、用量（如：100份菜品需要 5kg 食材）

**字段解释（采购单 PurchaseOrder）**：
- `id`：主键
- `order_number`：采购单号（自动生成）
- `sub_menu_id`：关联的子菜单 ID（可选）
- `total_amount`：预估总金额
- `status`：状态（`draft` 草稿 / `confirmed` 已确认 / `purchased` 已采购）
- `created_by`：创建人 ID
- `created_at` / `updated_at`：创建/更新时间

**字段解释（采购单明细 PurchaseOrderItem）**：
- `id`：主键
- `purchase_order_id`：采购单 ID
- `ingredient_id`：食材 ID
- `required_quantity`：所需数量（根据菜单计算）
- `stock_quantity`：当前库存数量（快照）
- `use_stock`：是否使用库存（布尔）
- `purchase_quantity`：实际采购数量
- `unit_price`：单价（快照）
- `subtotal`：小计金额

**业务规则**：
- 菜单库 xlsx 文件需要定期维护和更新
- 采购清单计算时，需要考虑菜单的份数（根据订单数量）
- 库存数量实时查询，采购单生成时记录快照
- 采购单确认后，可以关联到出库操作

---

## 4. 数据库设计（ER 关系）

```
Company (客户企业)
  ├── 1..N User (customer 角色账号)
  ├── 1..N Order (订单)
  │     ├── 1..N OrderItem (订单明细)
  │     │     └── N..1 MealStandard (餐标)
  │     └── 1..1 Logistics (物流)
  └── 1..N SubMenu (子菜单)
        ├── 1..N SubMenuItem (子菜单明细)
        │     └── N..1 WeeklyMenuItem (总菜单明细)
        └── N..1 WeeklyMenu (总菜单)

WeeklyMenu (一周总菜单)
  ├── 1..N WeeklyMenuItem (总菜单明细)
  └── 1..N SubMenu (子菜单)

Ingredient (食材库)
  ├── 1..1 Inventory (库存记录)
  ├── 1..N StockIn (入库记录)
  ├── 1..N StockOut (出库记录)
  └── 1..N PurchaseOrderItem (采购单明细)

PurchaseOrder (采购单)
  ├── 1..N PurchaseOrderItem (采购单明细)
  │     └── N..1 Ingredient (食材)
  └── N..1 SubMenu (子菜单，可选)
```

**关键关系**：
- `User` 中 `role=customer` 时必须绑定 `company_id`
- `superadmin/admin/user` 不绑定客户企业（`company_id` 为空）
- `SubMenu` 关联 `WeeklyMenu` 和 `Company`，实现子菜单与客户企业的绑定
- `StockOut` 可关联 `PurchaseOrder`，实现采购单关联出库
- `PurchaseOrder` 可关联 `SubMenu`，追溯采购单来源

---

## 5. 后端 API 设计（给代码生成 agent 的接口基准）

### 5.1 认证

- `POST /api/auth/login`
  - 入参：`{ username, password }`
  - 出参：`{ access_token, user:{ id, username, role, company_id } }`

### 5.2 客户管理（企业）

- `GET /api/companies?keyword=...`
  - 返回：客户列表（所有角色可查看）
- `GET /api/companies/{id}`
  - 返回：客户详情
- `POST /api/companies`（admin/superadmin）
  - 入参：`{ name, address, contact_person, contact_phone }`
- `PUT /api/companies/{id}`（admin/superadmin）
  - 入参：`{ name?, address?, contact_person?, contact_phone? }`
- `DELETE /api/companies/{id}`（admin/superadmin，需无关联账号/订单）

### 5.3 餐标配置

- `GET /api/meal-standards?status=enabled`
  - 返回：餐标列表（所有角色可查看）
- `POST /api/meal-standards`（admin/superadmin）
  - 入参：`{ name, meal_type, price, status, description? }`
- `PUT /api/meal-standards/{id}`（admin/superadmin）
  - 入参：`{ name?, meal_type?, price?, status?, description? }`

### 5.4 订单

- `GET /api/orders?order_date=YYYY-MM-DD&company_keyword=...&status=...`
  - 返回：订单列表（包含明细项、总份数、总金额、物流阶段）
  - customer：后端强制只返回本企业
  - 支持按日期、公司名称关键词、状态筛选
- `POST /api/orders`（customer）
  - 入参示例：
    - `order_date: "2024-01-15"`
    - `items: [{ meal_standard_id: 1, meal_type: "午餐", quantity: 100, unit_price?: 10.0 }]`
  - 状态默认为"已提交，等待确认"
- `GET /api/orders/{id}`
  - 返回：订单详情 + 明细 + 物流状态 + 总份数 + 总金额
- `PUT /api/orders/{id}`（admin/superadmin）
  - 入参：`{ status?: string, items?: [...] }`
  - 允许修改状态、订单明细（数量、单价等）
- `DELETE /api/orders/{id}`（admin/superadmin）
  - 删除订单（级联删除明细和物流记录）
- `POST /api/orders/{id}/confirm`（user/admin/superadmin）
  - 将订单状态从"已提交，等待确认"改为"订餐已收到"

### 5.5 物流

- `GET /api/logistics?order_date=YYYY-MM-DD&meal_type=breakfast|lunch|dinner|supper`
  - 返回：物流列表（包含订单信息、企业信息、各阶段状态和时间）
  - customer：后端强制只返回本企业
  - 支持按日期和餐别复合筛选
- `GET /api/logistics/statistics?order_date=YYYY-MM-DD&meal_type=breakfast|lunch|dinner|supper`
  - 返回：统计数据 `{ prepare_loaded: 数量, shipping: 数量, arrived: 数量, recycled: 数量 }`
  - 用于图表展示某天某餐的四种状态的订单完成数量
  - customer：后端强制只返回本企业数据
- `POST /api/logistics/{order_id}/update_stage`
  - 入参：`{ stage: 'prepare_loaded'|'shipping'|'arrived'|'recycled' }`
  - 后端按角色控制可操作阶段
  - 阶段按顺序推进，不允许跳步
- `POST /api/logistics/batch-update-stages`
  - 入参：`{ updates: [{ order_id: 1, stage: 'arrived' }, ...] }`
  - 批量更新多个订单的物流阶段
  - 返回：`{ msg: "成功更新 X 条记录", success_count: 数量, errors: [] }`
  - 仅 user/admin/superadmin 可用

### 5.6 员工管理（仅 superadmin）

- `GET /api/staff?role=admin|user&keyword=...`
  - 返回：员工列表（仅 admin 和 user 角色）
  - 筛选：按角色、关键词（用户名）
- `GET /api/staff/{id}`
  - 返回：员工详情
- `POST /api/staff`（仅 superadmin）
  - 入参：`{ username, password, role: 'admin'|'user' }`
  - 返回：创建成功后的员工信息
- `PUT /api/staff/{id}`（仅 superadmin）
  - 入参：`{ username?, role?: 'admin'|'user' }`
  - 注意：不能修改为 superadmin 或 customer 角色
- `POST /api/staff/{id}/reset-password`（仅 superadmin）
  - 入参：`{ new_password? }`（可选，不传则生成随机密码）
  - 返回：新密码（明文，仅首次返回，后续不再返回）
- `DELETE /api/staff/{id}`（仅 superadmin）
  - 删除前检查：不能删除 superadmin，建议检查操作记录
  - 返回：删除成功信息

### 5.7 一周总菜单管理

- `GET /api/weekly-menus?week_year=...&week_number=...`
  - 返回：总菜单列表
  - 支持按年份、周数筛选
- `GET /api/weekly-menus/{id}`
  - 返回：总菜单详情 + 明细项
- `POST /api/weekly-menus/generate`（user/admin/superadmin）
  - 入参：`{ week_year, week_number }`
  - 调用菜单生成算法，生成一周总菜单
  - 返回：生成的总菜单数据
- `POST /api/weekly-menus`（user/admin/superadmin）
  - 入参：`{ week_year, week_number, items: [{ day_of_week, meal_type, dish_name, ... }] }`
  - 保存总菜单
- `PUT /api/weekly-menus/{id}`（user/admin/superadmin）
  - 入参：`{ status?, items?: [...] }`
  - 更新总菜单（可修改状态、明细项）
- `GET /api/weekly-menus/{id}/export`（user/admin/superadmin）
  - 导出总菜单为 Excel/PDF

### 5.8 子菜单管理

- `GET /api/sub-menus?weekly_menu_id=...&company_id=...`
  - 返回：子菜单列表
  - 支持按总菜单、客户企业筛选
  - customer：后端强制只返回本企业
- `GET /api/sub-menus/{id}`
  - 返回：子菜单详情 + 明细项
- `POST /api/sub-menus/select`（admin/superadmin）
  - 入参：`{ weekly_menu_id, company_ids: [1, 2, ...], selected_items: [{ day_of_week, meal_type, dish_name, ... }] }`
  - 从总菜单中选择子菜单，关联到客户企业
- `POST /api/sub-menus`（admin/superadmin）
  - 入参：`{ weekly_menu_id, company_id, name?, items: [...] }`
  - 手动创建子菜单
- `PUT /api/sub-menus/{id}`（admin/superadmin）
  - 入参：`{ name?, status?, items?: [...] }`
  - 更新子菜单
- `GET /api/sub-menus/history?company_id=...&week_year=...`（所有角色）
  - 返回：历史子菜单列表
  - customer：后端强制只返回本企业

### 5.9 库存管理

- `GET /api/inventory?keyword=...&category=...`
  - 返回：库存列表（食材名称、当前库存、最后入库日期等）
  - user/admin/superadmin 可用
- `GET /api/inventory/{ingredient_id}`
  - 返回：食材库存详情 + 入库/出库历史
- `POST /api/inventory/stock-in`（user/admin/superadmin）
  - 入参：`{ ingredient_id, quantity, in_date, expiry_date?, scale_weight? }`
  - 食材入库（可传入电子秤称重值）
- `POST /api/inventory/stock-out`（user/admin/superadmin）
  - 入参：`{ ingredient_id, quantity, out_date, purchase_order_id?, purpose?, scale_weight? }`
  - 食材出库（可关联采购单）
- `GET /api/inventory/stock-in-history?ingredient_id=...`
  - 返回：入库历史记录
- `GET /api/inventory/stock-out-history?ingredient_id=...`
  - 返回：出库历史记录

### 5.10 电子秤接口（模拟）

- `GET /api/scale/weight`
  - 返回：`{ weight: 1.25, unit: "kg", stable: true }`
  - 获取当前称重值（模拟接口）
- `POST /api/scale/tare`
  - 去皮（清零）
  - 返回：`{ msg: "ok" }`

### 5.11 采购清单生成

- `POST /api/purchase-lists/generate`（user/admin/superadmin）
  - 入参：`{ sub_menu_id, menu_library_file_id? }`
  - 根据子菜单和菜单库，自动计算采购清单
  - 返回：采购清单（包含所需食材、库存信息、预估金额）
- `POST /api/purchase-lists/calculate`（user/admin/superadmin）
  - 入参：`{ sub_menu_id, items: [{ ingredient_id, required_quantity, use_stock, purchase_quantity }] }`
  - 计算采购清单（考虑库存使用情况）
  - 返回：最终采购清单和总金额
- `POST /api/purchase-orders`（user/admin/superadmin）
  - 入参：`{ sub_menu_id?, items: [{ ingredient_id, purchase_quantity, unit_price }] }`
  - 生成最终采购单
  - 返回：采购单信息
- `GET /api/purchase-orders?status=...`
  - 返回：采购单列表
- `GET /api/purchase-orders/{id}`
  - 返回：采购单详情 + 明细项
- `PUT /api/purchase-orders/{id}`（user/admin/superadmin）
  - 入参：`{ status? }`
  - 更新采购单状态
- `POST /api/menu-library/upload`（admin/superadmin）
  - 上传菜单库 xlsx 文件
  - 返回：文件 ID 和解析结果

---

## 6. 前端页面信息架构（导航/布局/适配）

### 6.1 主布局（PC/移动端）

- **顶部 Header**：系统名称、当前用户、退出登录
- **侧边 Sidebar**：可折叠；移动端建议抽屉/滑出
- **主体 Main**：卡片化内容区

### 6.2 页面路由

- `/login`：登录页
- `/dashboard`：总览（可选，统计卡片）
- `/companies`：客户管理（admin/superadmin）
- `/meal-standards`：餐标配置（admin/superadmin；user/customer 可只读入口可选）
- `/staff`：员工管理（仅 superadmin）
- `/weekly-menu`：一周总菜单（user/admin/superadmin）
- `/sub-menu`：子菜单管理（user/admin/superadmin；customer 可查看本企业历史）
- `/inventory`：库存管理（user/admin/superadmin）
- `/purchase-list`：采购清单（user/admin/superadmin）
- `/orders`：订单列表
- `/orders/:id`：订单详情
- `/logistics`：物流总览

### 6.3 响应式设计

- **PC 端**：侧边栏可折叠，主内容区自适应
- **移动端**：侧边栏改为抽屉式，列表采用卡片布局，表单控件宽度 100%

---

## 7. 可视化（ECharts）设计点

### 7.1 物流阶段统计（按日期）

- **柱状图**：每个阶段完成的订单数量
- **或漏斗图**：从装车→运输→到达→回收的流转量

### 7.2 订单统计（Dashboard）

- 今日/次日订单总数、总份数、总金额（可扩展）

### 7.3 颜色规范

- **主色**：绿色系（与 Element Plus 主题一致）
- **未完成**：灰色
- **异常/超时**（可选）：橙/红

---

## 8. 安全与审计（建议给后续 agent 的要求）

### 8.1 认证安全

- 密码：哈希存储（Werkzeug）
- JWT：前端存储 + 请求携带 `Authorization: Bearer <token>`

### 8.2 数据隔离

- customer 强制按 `company_id` 过滤

### 8.3 操作审计（建议后续添加）

- 订单修改记录（谁在什么时间改了什么）
- 物流阶段确认记录（操作者、时间、IP）

---

## 9. 迭代优先级（便于代码生成 agent 分阶段产出）

### 阶段 1（MVP 可用）

- ✅ 登录 + 角色路由
- ✅ 客户管理 CRUD
- ✅ 餐标管理 CRUD
- ✅ 员工管理 CRUD（仅 superadmin）
- ✅ customer 下单（次日订单）+ 查询订单
- ✅ 物流 4 阶段：查看 + 按角色确认

### 阶段 2（运营增强）

- 订单修改/关闭 + 截止时间规则
- 报表导出（Excel）
- 消息通知（物流变更/订单变更）

### 阶段 3（生产环节管理）

- 一周总菜单生成（算法适配 + 可视化）
- 子菜单选取与生成
- 库存管理（入库/出库 + 电子秤集成）
- 采购清单生成（菜单库 xlsx 解析 + 自动计算）

### 阶段 4（规模化）

- 多仓/多线路、司机管理、车辆管理（如果需要）
- 更细粒度权限（按功能点/数据范围）
- 电子秤真实设备对接

---

## 10. 字段字典（汇总速查）

### User（用户）

- `id`：主键
- `username`：登录名（唯一）
- `password_hash`：密码哈希
- `role`：角色（superadmin/admin/user/customer）
- `company_id`：客户企业 ID（仅 customer 有值）

**角色说明**：
- `superadmin`：系统最高管理员，不可被删除或修改角色
- `admin`：送餐公司管理员，可由 superadmin 管理
- `user`：送餐公司普通员工，可由 superadmin 管理
- `customer`：客户企业账号，由客户管理模块创建，不属于员工管理范围

### Company（客户企业）

- `id`：主键
- `name`：企业客户名称
- `address`：地址
- `contact_person`：联系人姓名
- `contact_phone`：联系方式
- `created_at`：添加时间

### MealStandard（餐标）

- `id`：主键
- `name`：餐标名称
- `meal_type`：餐别（中文：早餐/午餐/晚餐/夜宵）
- `price`：默认单价
- `status`：状态（enabled/disabled）
- `description`：备注说明

### Order（订单）

- `id`：主键
- `company_id`：客户企业 ID
- `order_date`：订餐日期
- `status`：状态（submitted/closed）
- `created_at`：创建时间
- `updated_at`：更新时间

### OrderItem（订单明细）

- `id`：主键
- `order_id`：订单 ID
- `meal_standard_id`：餐标 ID
- `meal_name`：餐标名称快照
- `meal_type`：餐别快照
- `unit_price`：单价快照
- `quantity`：数量

### Logistics（物流）

- `id`：主键
- `order_id`：订单 ID（一对一）
- `stage_prepare_loaded`：备餐装车阶段（布尔）
- `time_prepare_loaded`：备餐装车时间
- `stage_shipping`：运输阶段（布尔）
- `time_shipping`：运输时间
- `stage_arrived`：到达阶段（布尔）
- `time_arrived`：到达时间
- `stage_recycled`：回收阶段（布尔）
- `time_recycled`：回收时间

### WeeklyMenu（一周总菜单）

- `id`：主键
- `week_year`：年份
- `week_number`：周数（1-53）
- `week_start_date`：周开始日期（周一）
- `week_end_date`：周结束日期（周日）
- `status`：状态（draft/published）
- `created_by`：创建人 ID
- `created_at`：创建时间
- `updated_at`：更新时间

### WeeklyMenuItem（总菜单明细）

- `id`：主键
- `weekly_menu_id`：总菜单 ID
- `day_of_week`：星期几（1-7）
- `meal_type`：餐别（早餐/午餐/晚餐/夜宵）
- `dish_name`：菜品名称
- `dish_category`：菜品分类（可选）
- `sort_order`：排序

### SubMenu（子菜单）

- `id`：主键
- `weekly_menu_id`：关联的总菜单 ID
- `company_id`：客户企业 ID
- `name`：子菜单名称（可选）
- `status`：状态（draft/confirmed）
- `created_by`：创建人 ID
- `created_at`：创建时间
- `updated_at`：更新时间

### SubMenuItem（子菜单明细）

- `id`：主键
- `sub_menu_id`：子菜单 ID
- `weekly_menu_item_id`：关联的总菜单明细 ID
- `day_of_week`：星期几
- `meal_type`：餐别
- `dish_name`：菜品名称（快照）
- `dish_category`：菜品分类（快照）

### Ingredient（食材库）

- `id`：主键
- `name`：食材名称（唯一）
- `category`：食材分类
- `unit`：单位（kg/斤/包/箱等）
- `safety_stock`：安全库存
- `shelf_life_days`：保质期天数（可选）

### Inventory（库存记录）

- `id`：主键
- `ingredient_id`：食材 ID
- `quantity`：当前库存数量
- `last_in_date`：最后入库日期
- `last_out_date`：最后出库日期
- `updated_at`：更新时间

### StockIn（入库记录）

- `id`：主键
- `ingredient_id`：食材 ID
- `quantity`：入库数量
- `in_date`：入库日期
- `expiry_date`：保质期到期日期（可选）
- `operator_id`：操作人 ID
- `scale_weight`：电子秤称重值
- `created_at`：创建时间

### StockOut（出库记录）

- `id`：主键
- `ingredient_id`：食材 ID
- `quantity`：出库数量
- `out_date`：出库日期
- `purchase_order_id`：关联的采购单 ID（可选）
- `purpose`：出库用途
- `operator_id`：操作人 ID
- `scale_weight`：电子秤称重值
- `created_at`：创建时间

### PurchaseOrder（采购单）

- `id`：主键
- `order_number`：采购单号（自动生成）
- `sub_menu_id`：关联的子菜单 ID（可选）
- `total_amount`：预估总金额
- `status`：状态（draft/confirmed/purchased）
- `created_by`：创建人 ID
- `created_at`：创建时间
- `updated_at`：更新时间

### PurchaseOrderItem（采购单明细）

- `id`：主键
- `purchase_order_id`：采购单 ID
- `ingredient_id`：食材 ID
- `required_quantity`：所需数量
- `stock_quantity`：当前库存数量（快照）
- `use_stock`：是否使用库存（布尔）
- `purchase_quantity`：实际采购数量
- `unit_price`：单价（快照）
- `subtotal`：小计金额

---

## 11. 技术实现要点（给代码生成 agent）

### 11.1 后端

- **Flask 应用结构**：`app/__init__.py` 创建 app，注册蓝图
- **模型定义**：`app/models/` 下各模型文件，使用 SQLAlchemy
- **路由定义**：`app/routes/` 下各蓝图文件
- **权限控制**：使用 `@roles_required` 装饰器
- **JWT 认证**：`Flask-JWT-Extended`，token 存储在请求头

### 11.2 前端

- **路由守卫**：`router.beforeEach` 检查登录状态和角色
- **API 封装**：`src/api/` 下各模块 API 文件，使用 axios
- **状态管理**：Pinia store（auth、layout 等）
- **组件库**：Element Plus，主题色为绿色（#27ae60）
- **图表库**：ECharts，用于物流统计和状态展示

### 11.3 数据库

- **连接配置**：`app/config.py` 中配置 MySQL 连接
- **迁移工具**：Flask-Migrate（可选）
- **初始化脚本**：`init_db.py` 用于创建表和初始数据

### 11.4 外部设备集成

- **电子秤接口**：模拟接口（`/api/scale/*`），后续可对接真实设备
- **文件处理**：使用 `openpyxl` 或 `pandas` 解析菜单库 xlsx 文件

### 11.5 菜单生成算法

- **算法位置**：后端独立模块或服务
- **集成方式**：通过 API 调用或直接导入算法函数
- **输入参数**：周次、历史菜单数据（可选）、菜品库等
- **输出结果**：一周菜单数据（JSON 格式）

---

## 12. 开发规范

### 12.1 代码风格

- Python：遵循 PEP 8
- TypeScript/Vue：使用 ESLint + Prettier（可选）

### 12.2 命名规范

- **数据库表**：复数形式（users, companies, orders）
- **模型类**：单数形式（User, Company, Order）
- **API 路由**：RESTful 风格（/api/companies, /api/orders/{id}）
- **前端组件**：PascalCase（OrderList.vue, LogisticsChart.vue）

### 12.3 错误处理

- 后端：统一返回 JSON 格式错误信息
- 前端：使用 Element Plus 的 Message/Notification 提示

---

## 附录：快速参考

### 测试账号（初始化后）

- 超级管理员：`superadmin` / `admin123`
- 管理员：`admin` / `admin123`
- 普通员工：`staff1` / `user123`
- 客户1：`customer1` / `customer123`（关联公司A）
- 客户2：`customer2` / `customer123`（关联公司B）

### 数据库连接

- 服务器：`121.199.16.11:3306`
- 数据库名：`canteen`
- 配置方式：环境变量或 `.env` 文件

---

---

## 13. 生产环节管理功能详细说明

### 13.1 菜单生成流程

1. **生成总菜单**：
   - superadmin/admin 选择周次
   - 调用菜单生成算法（已有算法）
   - 系统生成一周7天的完整菜单
   - 可视化展示，支持手动调整
   - 保存总菜单

2. **选择子菜单**：
   - 在总菜单基础上，通过点击/拖拽选择子菜单
   - 选择适用的客户企业（可多选）
   - 保存子菜单关联

3. **查看历史**：
   - 查看历史总菜单
   - 按客户企业查看历史子菜单

### 13.2 库存管理流程

1. **入库流程**：
   - 选择食材
   - 连接电子秤（模拟接口）
   - 上秤自动称重
   - 确认入库，记录入库日期、数量

2. **出库流程**：
   - 选择出库类型（关联采购单 / 手动出库）
   - 选择食材、填写数量
   - 连接电子秤（模拟接口）
   - 上秤自动称重
   - 确认出库，记录出库信息

### 13.3 采购清单生成流程

1. **自动计算**：
   - 选择已生成的子菜单
   - 上传/选择菜单库 xlsx 文件
   - 系统解析 xlsx，计算所需食材清单

2. **库存匹配**：
   - 展示每个食材的库存数量和入库日期
   - 用户选择：使用库存 / 加采购

3. **生成采购单**：
   - 调整采购数量
   - 计算预估金额
   - 生成最终采购单

### 13.4 菜单库 xlsx 文件格式（建议）

**Sheet 1: 菜品表**
| 菜品名称 | 餐别 | 分类 | 描述 |
|---------|------|------|------|
| 红烧肉 | 午餐 | 荤菜 | ... |

**Sheet 2: 食材表**
| 食材名称 | 单位 | 单价 | 分类 |
|---------|------|------|------|
| 猪肉 | kg | 25.0 | 肉类 |

**Sheet 3: 菜品-食材映射表**
| 菜品名称 | 食材名称 | 用量（每100份） |
|---------|---------|----------------|
| 红烧肉 | 猪肉 | 5.0 kg |
| 红烧肉 | 酱油 | 2.0 L |

---

**文档版本**：v2.0  
**最后更新**：2024-01-XX  
**维护者**：开发团队
