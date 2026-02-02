# GitHub 认证问题解决方案

GitHub 已不再支持密码认证，需要使用 **Personal Access Token (PAT)** 或 **SSH Key**。

## 方案一：使用 Personal Access Token（推荐，简单快速）

### 步骤 1：生成 Personal Access Token

1. 登录 GitHub
2. 点击右上角头像 → **Settings**
3. 左侧菜单最下方 → **Developer settings**
4. 左侧菜单 → **Personal access tokens** → **Tokens (classic)**
5. 点击 **Generate new token** → **Generate new token (classic)**
6. 填写信息：
   - **Note**：`canteen-platform`（描述用途）
   - **Expiration**：选择过期时间（建议 90 天或 No expiration）
   - **Select scopes**：勾选 `repo`（完整仓库权限）
7. 点击 **Generate token**
8. **重要**：复制生成的 token（只显示一次，请保存好！）

### 步骤 2：使用 Token 推送代码

```bash
# 方法 1：在 URL 中使用 token（一次性）
git push https://YOUR_TOKEN@github.com/Carries-Ly/canteen-management-platform.git main

# 方法 2：配置 credential helper（推荐，后续自动使用）
git remote set-url origin https://YOUR_TOKEN@github.com/Carries-Ly/canteen-management-platform.git
git push -u origin main

# 方法 3：使用 Git Credential Manager（macOS）
# 推送时会提示输入用户名和密码
# 用户名：Carries-Ly
# 密码：粘贴你的 token（不是 GitHub 密码）
git push -u origin main
```

### 步骤 3：保存 Token（避免每次输入）

```bash
# macOS 使用 Keychain 保存
git config --global credential.helper osxkeychain

# 或者使用 Git Credential Manager
git config --global credential.helper store
```

---

## 方案二：使用 SSH Key（推荐，长期使用）

### 步骤 1：检查是否已有 SSH Key

```bash
ls -al ~/.ssh
```

如果看到 `id_rsa` 或 `id_ed25519`，说明已有 SSH key。

### 步骤 2：生成新的 SSH Key（如果没有）

```bash
# 生成 SSH key（将 your_email@example.com 替换为你的 GitHub 邮箱）
ssh-keygen -t ed25519 -C "your_email@example.com"

# 按 Enter 使用默认路径
# 设置密码（可选，建议设置）
```

### 步骤 3：添加 SSH Key 到 GitHub

```bash
# 复制公钥内容
cat ~/.ssh/id_ed25519.pub
# 或者
pbcopy < ~/.ssh/id_ed25519.pub  # macOS 自动复制到剪贴板
```

然后在 GitHub：
1. Settings → **SSH and GPG keys**
2. 点击 **New SSH key**
3. **Title**：`MacBook`（或你的设备名称）
4. **Key**：粘贴刚才复制的公钥
5. 点击 **Add SSH key**

### 步骤 4：测试 SSH 连接

```bash
ssh -T git@github.com
```

如果看到 "Hi Carries-Ly! You've successfully authenticated..." 说明成功。

### 步骤 5：修改远程仓库地址为 SSH

```bash
# 删除现有的 HTTPS 远程地址
git remote remove origin

# 添加 SSH 远程地址
git remote add origin git@github.com:Carries-Ly/canteen-management-platform.git

# 推送代码
git push -u origin main
```

---

## 方案三：使用 GitHub CLI（可选）

```bash
# 安装 GitHub CLI（如果未安装）
brew install gh

# 登录
gh auth login

# 选择 GitHub.com
# 选择 HTTPS
# 选择 Login with a web browser
# 按照提示完成认证

# 然后正常推送
git push -u origin main
```

---

## 推荐方案

- **快速解决**：使用方案一（Personal Access Token）
- **长期使用**：使用方案二（SSH Key）

## 常见问题

### Q: Token 在哪里查看？
A: Settings → Developer settings → Personal access tokens → Tokens (classic)

### Q: Token 过期了怎么办？
A: 重新生成新 token，更新远程仓库 URL 或重新配置 credential helper

### Q: 使用 SSH 还是 HTTPS？
A: 
- **SSH**：更安全，一次配置长期使用，适合个人开发
- **HTTPS + Token**：简单快速，适合临时使用或 CI/CD

---

**提示**：如果使用 Token，请妥善保管，不要分享给他人或提交到代码仓库。

