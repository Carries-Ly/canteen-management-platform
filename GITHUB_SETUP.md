# GitHub 仓库设置指南

## 1. 在 GitHub 上创建新仓库

1. 登录 GitHub 账号
2. 点击右上角 "+" → "New repository"
3. 填写仓库信息：
   - Repository name: `canteen-management-platform`（或你喜欢的名称）
   - Description: `中央厨房食堂服务公司管理平台`
   - 选择 Public 或 Private
   - **不要**勾选 "Initialize this repository with a README"（因为我们已经有了文件）
4. 点击 "Create repository"

## 2. 将本地代码推送到 GitHub

在项目根目录执行以下命令：

```bash
# 添加远程仓库（将 YOUR_USERNAME 和 REPO_NAME 替换为你的实际信息）
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git

# 或者使用 SSH（如果你配置了 SSH key）
# git remote add origin git@github.com:YOUR_USERNAME/REPO_NAME.git

# 推送到 GitHub
git branch -M main
git push -u origin main
```

## 3. 允许其他合作者上传

### 方法一：添加协作者（推荐）

1. 进入 GitHub 仓库页面
2. 点击 "Settings" → "Collaborators"
3. 点击 "Add people"
4. 输入合作者的 GitHub 用户名或邮箱
5. 选择权限级别：
   - **Write**：允许推送代码、创建分支、合并 PR（推荐）
   - **Admin**：完全管理权限
6. 合作者会收到邀请邮件，接受后即可推送代码

### 方法二：使用组织（Organization）

如果有多人协作，可以创建 GitHub Organization：
1. 创建 Organization
2. 将仓库转移到 Organization
3. 在 Organization 中添加成员
4. 设置团队权限

## 4. 合作者克隆和协作流程

### 首次克隆项目

```bash
# 克隆仓库
git clone https://github.com/YOUR_USERNAME/REPO_NAME.git
cd REPO_NAME

# 前端安装依赖
cd frontend
npm install
cd ..

# 后端安装依赖（可选，如果使用虚拟环境）
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 日常协作流程

```bash
# 1. 拉取最新代码
git pull origin main

# 2. 创建新分支（推荐，避免直接在主分支上工作）
git checkout -b feature/your-feature-name

# 3. 进行开发...

# 4. 提交更改
git add .
git commit -m "描述你的更改"

# 5. 推送到远程仓库
git push origin feature/your-feature-name

# 6. 在 GitHub 上创建 Pull Request（PR）
# 或者直接推送到 main（如果权限允许）
git push origin main
```

## 5. 重要注意事项

### 不要上传的文件

以下文件已被 `.gitignore` 排除，不会上传：
- `frontend/node_modules/` - 前端依赖包（需要运行 `npm install` 安装）
- `backend/venv/` - Python 虚拟环境
- `.env` - 环境变量文件（包含敏感信息）
- `__pycache__/` - Python 缓存文件
- `*.db` - 数据库文件

### 环境配置

每个开发者需要：
1. 复制 `backend/config_example.env` 为 `.env`（如果存在）
2. 配置自己的数据库连接信息
3. 运行 `npm install` 安装前端依赖

### 分支管理建议

- `main`：主分支，稳定版本
- `develop`：开发分支（可选）
- `feature/*`：功能分支
- `fix/*`：修复分支

## 6. 常见问题

### Q: 如何更新代码？

```bash
git pull origin main
```

### Q: 如何解决冲突？

```bash
# 拉取最新代码
git pull origin main

# 如果有冲突，手动解决后
git add .
git commit -m "解决冲突"
git push origin main
```

### Q: 如何撤销本地更改？

```bash
# 查看更改
git status

# 撤销未暂存的更改
git checkout -- <file>

# 撤销所有未暂存的更改
git checkout -- .
```

## 7. 保护主分支（可选）

在 GitHub 仓库设置中：
1. Settings → Branches
2. Add rule for `main` branch
3. 勾选 "Require pull request reviews before merging"
4. 这样可以防止直接推送到主分支，必须通过 PR

---

**提示**：首次推送后，记得在 GitHub 仓库页面添加项目描述和 README 说明。

