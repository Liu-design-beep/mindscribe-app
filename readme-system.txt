# 系统架构与故障排查记录 (System Architecture & Troubleshooting Log)
Date: 2026-01-13

## 1. 最终确认的系统架构 (Final System Architecture)

本项目采用前后端分离的部署架构，分别托管在不同的平台上：

*   **前端 (Frontend)**:
    *   **托管平台**: Cloudflare Pages
    *   **域名**: `mindscribe-app.pages.dev`
    *   **职责**: 托管静态 HTML、CSS、JavaScript 以及静态资源（图片、视频）。
    *   **构建流程**: 运行 `build-frontend.sh` 脚本，将 `app/web/frontend` 和 `app/web/static` 的内容整合复制到 `app/frontend` 目录（Cloudflare 配置的构建输出目录）。
    *   **关键配置**: `wrangler.toml` (用于 Workers/Functions), Cloudflare Dashboard 构建设置。

*   **后端 (Backend)**:
    *   **托管平台**: Render
    *   **职责**: 运行 Python FastAPI 服务，处理 API 请求（如 `/api/chat`, `/api/documents`）。
    *   **运行环境**: Python 3.11+
    *   **关键配置**: `render.yaml` (定义服务配置), `api_server.py` (入口文件)。

## 2. 故障排查过程 (Troubleshooting Process)

### 问题描述
用户反馈在访问网站时，静态资源（图片、视频）加载失败，返回 404 错误。

### 阶段一：误判为 Render 路径配置问题
*   **初始假设**: 认为前端和后端都部署在 Render 上，且 Render 的 Python 服务负责托管静态文件。
*   **尝试修复**:
    1.  检查 `api_server.py` 中的静态文件挂载路径，确认代码逻辑无误。
    2.  怀疑 Render 的 `rootDir` 配置导致上层目录无法访问，尝试修改 `render.yaml` 将根目录设为项目根目录。
    3.  怀疑 Render 构建环境隔离问题，将 `app/static` 和 `app/frontend` 移动到 `app/web` 下，试图创建一个自包含的部署单元。
*   **结果**: 修复无效，用户端依然报 404。

### 阶段二：发现部署平台差异
*   **关键转折**: 用户提供的错误日志显示域名为 `mindscribe-app.pages.dev`，且报错信息包含 `cdn.tailwindcss.com` 警告。
*   **重新分析**:
    *   域名后缀 `.pages.dev` 表明这是 Cloudflare Pages 的服务，而非 Render。
    *   这意味着用户访问的是 Cloudflare 托管的前端，而非 Render 托管的后端。
    *   之前的修复都在针对 Render 进行，因此对 Cloudflare 上的前端无效。

### 阶段三：定位 Cloudflare 配置问题
*   **问题定位**:
    1.  检查 `wrangler.toml`，发现配置的是 Worker (`main = "worker.js"`) 而非纯静态站点，且 `worker.js` 中没有处理静态文件的逻辑，导致所有非 API 请求都返回 404。
    2.  检查 Cloudflare Dashboard 配置（通过用户截图），发现构建命令为 `bash build-frontend.sh`，输出目录为 `app/frontend`。
    3.  由于之前的项目结构重构（文件移到了 `app/web`），导致旧的构建脚本失效或路径不匹配，Cloudflare 无法找到静态文件。

### 阶段四：最终修复
*   **修复措施**:
    1.  重写 `build-frontend.sh` 脚本。
    2.  脚本逻辑：将 `app/web/frontend`（页面）和 `app/web/static`（资源）的内容，全部复制到 Cloudflare 预期的输出目录 `app/frontend`。
    3.  确保静态资源被复制到 `app/frontend/static`，从而匹配前端代码中的 `/static/...` 引用路径。
*   **结果**: 构建脚本现在与 Cloudflare 的配置完美匹配，静态资源能够被正确打包和发布。

## 3. 经验总结 (Lessons Learned)

1.  **确认部署环境**: 在排查问题前，务必先确认用户访问的 URL 和部署平台。不同的平台（Render vs Cloudflare）有完全不同的构建和运行机制。
2.  **检查构建配置**: 对于静态站点，构建脚本和输出目录的配置至关重要。文件结构变更后，必须同步更新构建脚本。
3.  **前后端分离意识**: 在处理全栈项目时，要时刻警惕前后端是否分离部署。如果分离，前端的静态资源路径必须由前端服务器（或 CDN）解决，而不能依赖后端挂载。
