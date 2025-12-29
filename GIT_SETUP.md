# Git 仓库初始化指南

## 快速开始

### 方法一：使用自动化脚本（推荐）

#### Windows 批处理脚本
双击运行 `init-git-repo.bat`，脚本会自动完成所有步骤。

#### PowerShell 脚本
在 PowerShell 中运行：
```powershell
.\init-git-repo.ps1
```

### 方法二：手动执行命令

如果 Git 已安装并配置，可以手动执行以下命令：

```bash
# 1. 初始化 Git 仓库
git init

# 2. 添加所有文件
git add .

# 3. 提交代码
git commit -m "Initial commit: 灵辑应用 - 前后端分离架构"

# 4. 重命名分支为 main
git branch -M main

# 5. 添加远程仓库
git remote add origin https://github.com/Liu-design-beep/mindscribe-app.git

# 6. 推送代码
git push -u origin main
```

## 前置要求

### 1. 安装 Git

如果系统未安装 Git，请先下载安装：
- 下载地址：https://git-scm.com/download/win
- 安装后重启终端

### 2. 配置 Git 用户信息

首次使用 Git 需要配置用户信息：

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### 3. 配置 GitHub 认证

#### 方式一：使用 Personal Access Token（推荐）

1. 登录 GitHub
2. 进入 Settings → Developer settings → Personal access tokens → Tokens (classic)
3. 点击 "Generate new token (classic)"
4. 设置权限：至少勾选 `repo` 权限
5. 生成并复制 Token
6. 推送时，用户名输入 GitHub 用户名，密码输入 Token

#### 方式二：使用 SSH 密钥

1. 生成 SSH 密钥：
```bash
ssh-keygen -t ed25519 -C "your.email@example.com"
```

2. 将公钥添加到 GitHub：
   - 复制 `~/.ssh/id_ed25519.pub` 内容
   - GitHub → Settings → SSH and GPG keys → New SSH key

3. 修改远程仓库 URL 为 SSH：
```bash
git remote set-url origin git@github.com:Liu-design-beep/mindscribe-app.git
```

## 常见问题

### 问题 1：远程仓库已存在内容

如果 GitHub 仓库已初始化（有 README 等文件），需要先拉取：

```bash
git pull origin main --allow-unrelated-histories
# 解决可能的冲突后
git push -u origin main
```

### 问题 2：推送时提示认证失败

- 检查用户名和密码（Token）是否正确
- 如果使用 Token，确保 Token 有 `repo` 权限
- 考虑使用 SSH 方式

### 问题 3：文件过大或包含敏感信息

检查 `.gitignore` 文件，确保以下内容已忽略：
- `config_local.py`（包含 API 密钥）
- `__pycache__/`（Python 缓存）
- `.env`（环境变量）
- `*.db`（数据库文件）

## 验证推送成功

推送成功后，访问以下地址查看：
https://github.com/Liu-design-beep/mindscribe-app

## 后续操作

### 日常开发流程

```bash
# 1. 查看状态
git status

# 2. 添加修改的文件
git add .

# 3. 提交更改
git commit -m "描述你的更改"

# 4. 推送到 GitHub
git push
```

### 查看提交历史

```bash
git log --oneline
```

### 查看远程仓库信息

```bash
git remote -v
```

## 注意事项

1. **不要提交敏感信息**：确保 `config_local.py` 和 `.env` 文件在 `.gitignore` 中
2. **提交前检查**：使用 `git status` 查看将要提交的文件
3. **提交信息要清晰**：使用有意义的提交信息，方便后续追踪


