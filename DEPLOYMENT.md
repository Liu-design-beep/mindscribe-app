# 灵辑项目部署指南

本文档说明如何将灵辑项目部署到 Cloudflare Pages（前端）和 Render（后端）。

## 部署架构

- **前端**: Cloudflare Pages
- **后端**: Render
- **数据库**: SQLite（本地文件存储）

## 前置准备

### 1. GitHub 仓库设置

确保项目已推送到 GitHub 仓库。

### 2. Cloudflare Pages 设置

1. 登录 [Cloudflare Dashboard](https://dash.cloudflare.com/)
2. 进入 **Pages** 部分
3. 点击 **Create a project**，选择 **Connect to Git**
4. 选择你的 GitHub 仓库
5. 配置构建设置：
   - **Build command**: `chmod +x build-frontend.sh && ./build-frontend.sh`
   - **Build output directory**: `dist`
   - **Root directory**: `/`（项目根目录）

### 3. Render 设置

1. 登录 [Render Dashboard](https://dashboard.render.com/)
2. 点击 **New +** → **Web Service**
3. 连接你的 GitHub 仓库
4. 配置服务：
   - **Name**: `lingji-backend`（或你喜欢的名称）
   - **Environment**: `Python 3`
   - **Build Command**: `chmod +x build-backend.sh && ./build-backend.sh`
   - **Start Command**: `cd 程序/web && python api_server.py`
   - **Root Directory**: `程序/web`

### 4. GitHub Secrets 配置

在 GitHub 仓库的 **Settings** → **Secrets and variables** → **Actions** 中添加以下密钥：

#### Cloudflare Pages
- `CLOUDFLARE_API_TOKEN`: Cloudflare API Token
  - 获取方式：Cloudflare Dashboard → My Profile → API Tokens → Create Token
  - 权限：Account - Cloudflare Pages - Edit
- `CLOUDFLARE_ACCOUNT_ID`: Cloudflare Account ID
  - 获取方式：Cloudflare Dashboard 右侧边栏
- `CLOUDFLARE_PAGES_PROJECT_NAME`: Cloudflare Pages 项目名称

#### Render（可选，用于自动触发部署）
- `RENDER_API_KEY`: Render API Key
  - 获取方式：Render Dashboard → Account Settings → API Keys
- `RENDER_SERVICE_ID`: Render Service ID
  - 获取方式：Render 服务页面 URL 中的服务 ID

## 环境变量配置

### Render 后端环境变量

在 Render 服务设置中添加以下环境变量：

```
DASHSCOPE_API_KEY=your_dashscope_api_key
APP_ID=your_app_id
```

### Cloudflare Pages 前端环境变量（可选）

如果需要在前端构建时替换 API URL，可以添加：

```
VITE_API_URL=https://your-render-backend.onrender.com
```

## 部署流程

### 自动部署

配置完成后，当代码推送到 `main` 或 `master` 分支时：

1. **前端自动部署**：GitHub Actions 会自动构建前端并部署到 Cloudflare Pages
2. **后端自动部署**：Render 会自动检测代码变更并部署（如果已连接 GitHub）

### 手动部署

#### 前端手动部署

```bash
# 本地构建
chmod +x build-frontend.sh
./build-frontend.sh

# 构建输出在 dist/ 目录
# 可以通过 Cloudflare Pages Dashboard 手动上传
```

#### 后端手动部署

```bash
# 进入后端目录
cd 程序/web

# 安装依赖
pip install -r requirements.txt

# 启动服务（本地测试）
python api_server.py
```

## 本地开发

### 使用 Docker Compose

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

访问：
- 前端: http://localhost:8080
- 后端: http://localhost:8000
- API 文档: http://localhost:8000/docs

### 手动启动

#### 启动后端

```bash
cd 程序/web
python api_server.py
```

#### 启动前端

```bash
cd 程序/frontend
python -m http.server 8080
```

## 配置前端 API 地址

部署后，需要更新前端代码中的 API 地址：

1. 编辑 `程序/frontend/app.js`
2. 找到 `API_CONFIG.baseURL`
3. 将其更新为 Render 后端 URL（例如：`https://your-backend.onrender.com`）

或者使用环境变量在构建时替换（已在 `build-frontend.sh` 中配置）。

## 故障排查

### 前端部署问题

1. **构建失败**
   - 检查 `build-frontend.sh` 是否有执行权限
   - 检查 `程序/frontend/` 目录是否存在
   - 查看 GitHub Actions 日志

2. **API 连接失败**
   - 检查前端代码中的 API URL 是否正确
   - 检查后端 CORS 配置是否允许 Cloudflare Pages 域名

### 后端部署问题

1. **服务启动失败**
   - 检查 `Procfile` 中的启动命令是否正确
   - 检查 `requirements.txt` 是否完整
   - 查看 Render 日志

2. **依赖安装失败**
   - 检查 `runtime.txt` 中的 Python 版本
   - 确保所有依赖在 `requirements.txt` 中列出

3. **环境变量未设置**
   - 在 Render Dashboard 中检查环境变量配置
   - 确保 `DASHSCOPE_API_KEY` 和 `APP_ID` 已设置

## 文件说明

### 前端部署文件

- `.github/workflows/deploy-frontend.yml`: GitHub Actions 工作流，自动部署前端到 Cloudflare Pages
- `build-frontend.sh`: 前端构建脚本，复制文件到 `dist/` 目录

### 后端部署文件

- `.github/workflows/deploy-backend.yml`: GitHub Actions 工作流，触发 Render 部署
- `程序/web/Procfile`: Render 启动命令配置
- `程序/web/runtime.txt`: Python 版本指定
- `程序/web/requirements.txt`: Python 依赖列表
- `build-backend.sh`: 后端构建脚本，安装依赖

### 通用文件

- `.gitignore`: Git 忽略文件配置
- `docker-compose.yml`: Docker Compose 配置，用于本地开发
- `DEPLOYMENT.md`: 本部署文档

## 注意事项

1. **CORS 配置**: 确保后端 `api_server.py` 中的 CORS 配置包含 Cloudflare Pages 域名
2. **API 密钥安全**: 不要在代码中硬编码 API 密钥，使用环境变量
3. **数据库持久化**: SQLite 文件存储在 Render 的临时文件系统中，重启可能丢失数据。如需持久化，考虑使用 Render 的持久化磁盘或外部数据库
4. **构建时间**: Cloudflare Pages 和 Render 都有构建时间限制，确保构建脚本高效

## 更新部署

每次更新代码后：

1. 推送到 GitHub `main` 分支
2. GitHub Actions 会自动触发前端部署
3. Render 会自动检测并部署后端（如果已连接 GitHub）

或者手动触发：

- **前端**: 在 GitHub Actions 中手动运行工作流
- **后端**: 在 Render Dashboard 中点击 **Manual Deploy**

## 支持

如有问题，请查看：
- [Cloudflare Pages 文档](https://developers.cloudflare.com/pages/)
- [Render 文档](https://render.com/docs)
- [GitHub Actions 文档](https://docs.github.com/en/actions)

