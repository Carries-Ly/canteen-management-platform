# 中央厨房管理平台

中央厨房食堂服务公司管理平台，提供订单管理、物流跟踪、客户管理、库存管理、菜单生成等功能。

## 项目结构

```
├── backend/          # Flask 后端
│   ├── app/         # 应用核心代码
│   ├── init_db.py   # 数据库初始化脚本
│   └── requirements.txt
├── frontend/         # Vue3 前端
│   ├── src/         # 源代码
│   └── package.json
└── docs/            # 项目文档
    └── design.md    # 功能设计文档
```

## 技术栈

- **后端**：Python Flask + SQLAlchemy + JWT + MySQL
- **前端**：Vue3 + Vite + Element Plus + Pinia + ECharts
- **数据库**：MySQL

## 快速开始

### 后端设置

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python init_db.py
python wsgi.py
```

### 前端设置

```bash
cd frontend
npm install
npm run dev
```

详细说明请参考：
- 后端：[backend/README.md](backend/README.md)
- 设计文档：[docs/design.md](docs/design.md)

## 功能模块

- ✅ 用户认证与权限管理
- ✅ 客户企业管理
- ✅ 餐标配置
- ✅ 订单管理
- ✅ 物流跟踪（四阶段）
- ✅ 员工管理
- 🔄 菜单生成（开发中）
- 🔄 库存管理（开发中）
- 🔄 采购清单（开发中）

## 开发规范

- 代码风格：Python 遵循 PEP 8，TypeScript/Vue 使用 ESLint
- 分支管理：主分支 `main`，功能分支 `feature/*`
- 提交信息：使用清晰的中文或英文描述

## 贡献指南

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 许可证

[添加你的许可证信息]

## 联系方式

[添加联系方式]
