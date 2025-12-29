# 灵辑 (Mindscribe) - AI 内容收藏助手

一个基于 LLM 的智能笔记助手，支持通过自然语言对话管理文档内容。

## 项目概述

灵辑是一个智能笔记管理工具，使用阿里云百炼智能体应用进行意图识别，支持通过自然语言指令添加、查看、切换和清空文档内容。

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API 密钥

复制 `config_local.py.example` 为 `config_local.py`，并填入您的阿里云百炼 API Key 和应用 ID：

```python
DASHSCOPE_API_KEY = "your_api_key_here"
APP_ID = "your_app_id_here"
```

### 3. 启动服务

**方式一：一键启动（推荐）**
- Windows: 双击 `start_all.bat`
- 这会同时启动后端 API 服务器和前端界面

**方式二：分别启动**
- 启动后端: 运行 `start_api_server.bat` 或 `python api_server.py`
- 启动前端: 在 `frontend` 目录运行 `python -m http.server 8080`
- 访问: 打开浏览器访问 `http://localhost:8080`

## 项目结构

### 核心模块

#### `main.py`
- **功能**: 程序入口文件
- **说明**: 创建 `SmartClipLLM` 实例并启动主循环，用于命令行模式运行

#### `smart_clip_llm.py`
- **功能**: 核心对话引擎
- **说明**: 
  - 管理用户会话和对话流程
  - 处理多行输入和命令过滤
  - 协调文档管理和意图识别模块
  - 处理待确认操作（如清空文档）
  - 提供 AI 主动引导式对话

#### `document_manager.py`
- **功能**: 文档管理模块
- **说明**:
  - 管理多个文档的创建、读取、更新
  - 支持文档内容添加（开头/结尾/指定位置）
  - 文档内容持久化到本地文本文件
  - 维护活跃文档状态
  - 元数据管理（存储在 `metadata.json`）

#### `intent_recognizer.py`
- **功能**: LLM 意图识别模块
- **说明**:
  - 调用阿里云百炼智能体应用进行意图识别
  - 从 LLM 返回的 JSON 中提取意图和参数
  - 处理 JSON 格式修复（如双大括号问题）
  - 维护对话历史（messages 数组）
  - 支持对话历史重置

#### `config.py`
- **功能**: 配置管理模块
- **说明**:
  - 加载 API Key 和应用 ID（优先级：本地配置 > 环境变量 > 默认值）
  - 初始化 LLM 客户端配置
  - 验证配置有效性

### API 服务器

#### `api_server.py`
- **功能**: FastAPI 后端服务器
- **说明**:
  - 提供 RESTful API 接口
  - 会话管理（每个 session_id 对应一个 SmartClipLLM 实例）
  - CORS 配置（允许前端跨域请求）
  - API 端点：
    - `GET /`: API 信息
    - `POST /api/chat`: 处理用户聊天消息
    - `GET /api/documents`: 获取文档列表
  - 自动文档: `http://127.0.0.1:8000/docs`

### 前端界面

#### `frontend/index.html`
- **功能**: 前端 HTML 结构
- **说明**:
  - 定义页面布局（顶部导航、侧边栏、聊天区域、输入区域）
  - 包含欢迎消息和功能说明
  - 确认操作模态框
  - 加载动画指示器

#### `frontend/app.js`
- **功能**: 前端核心逻辑
- **说明**:
  - 应用状态管理（会话ID、当前文档、文档列表等）
  - DOM 元素操作和事件绑定
  - API 通信（发送消息、获取文档列表）
  - UI 更新（添加消息、更新文档列表、显示确认对话框）
  - 自动调整输入框高度
  - 平滑滚动动画

#### `frontend/style.css`
- **功能**: 前端样式表
- **说明**:
  - 现代化 UI 设计（渐变背景、圆角、阴影）
  - 响应式布局
  - 动画效果（淡入、缩放、滚动）
  - 移动端适配

### 配置文件

#### `config_local.py.example`
- **功能**: 本地配置文件模板
- **说明**: 复制此文件为 `config_local.py` 并填入实际 API 密钥（不会被提交到版本控制）

#### `config_local.py`
- **功能**: 本地配置文件（需自行创建）
- **说明**: 存储实际的 API Key 和应用 ID，不应提交到版本控制

#### `requirements.txt`
- **功能**: Python 依赖包列表
- **说明**: 包含 FastAPI、uvicorn、dashscope 等依赖

### 启动脚本

#### `start_all.bat`
- **功能**: 一键启动脚本（Windows）
- **说明**: 同时启动后端 API 服务器和前端 HTTP 服务器，并自动打开浏览器

#### `start_api_server.bat`
- **功能**: 启动后端 API 服务器（Windows）
- **说明**: 检查 Python 和依赖，启动 API 服务器

#### `start_api_server.sh`
- **功能**: 启动后端 API 服务器（Unix/Linux/Mac）
- **说明**: 检查 Python 和依赖，启动 API 服务器

#### `stop_all.bat`
- **功能**: 停止所有服务器（Windows）
- **说明**: 查找并关闭占用 8000 和 8080 端口的进程

#### `启动服务器.bat`
- **功能**: 简单启动脚本（Windows）
- **说明**: 直接启动 API 服务器

#### `启动服务器.ps1`
- **功能**: PowerShell 启动脚本（Windows）
- **说明**: 使用 PowerShell 启动服务器

#### `检查后端错误.bat`
- **功能**: 检查并重启后端服务器（Windows）
- **说明**: 检查端口占用，停止现有服务器，重新启动并显示详细日志

### 工具脚本

#### `add_iteration.py`
- **功能**: 添加代码迭代记录
- **说明**: 向 `代码迭代记录.docx` 添加新的迭代版本记录，包括版本号、变更内容、技术细节等

#### `create_iteration_log.py`
- **功能**: 创建代码迭代记录文档
- **说明**: 初始化 `代码迭代记录.docx` 文件，包含项目说明和初始迭代记录

### 数据文件

#### `documents/`
- **功能**: 文档存储目录
- **说明**: 
  - 每个文档存储为独立的 `.txt` 文件
  - `metadata.json` 存储文档元数据（活跃文档等）

#### `代码迭代记录.docx`
- **功能**: 代码迭代历史记录
- **说明**: Word 文档，记录项目的版本迭代历史

### Web 部署目录 (`web/`)

`web/` 目录包含用于云部署的代码和配置文件：

#### `web/api_server.py`
- **功能**: 云部署版本的 API 服务器
- **说明**: 适配云平台部署的 API 服务器代码

#### `web/config.py`, `web/document_manager.py`, `web/intent_recognizer.py`, `web/smart_clip_llm.py`, `web/main.py`
- **功能**: 云部署版本的核心模块
- **说明**: 与主目录中的对应文件功能相同，但针对云部署进行了优化

#### `web/Dockerfile`
- **功能**: Docker 容器化配置
- **说明**: 用于将应用打包为 Docker 镜像

#### `web/Procfile`
- **功能**: Heroku 部署配置
- **说明**: 定义 Heroku 平台上的进程启动命令

#### `web/railway.json`
- **功能**: Railway 部署配置
- **说明**: Railway 平台的部署配置

#### `web/render.yaml`
- **功能**: Render 部署配置
- **说明**: Render 平台的部署配置

#### `web/runtime.txt`
- **功能**: Python 运行时版本
- **说明**: 指定云平台使用的 Python 版本

#### `web/requirements.txt`
- **功能**: 云部署版本的依赖列表
- **说明**: 与主目录的 `requirements.txt` 相同

#### `web/env.example`
- **功能**: 环境变量配置示例
- **说明**: 云部署时使用的环境变量模板

#### `web/start.bat`, `web/start.sh`
- **功能**: 云部署版本的启动脚本
- **说明**: 用于在云平台上启动服务

## 使用说明

### 基本指令

1. **添加内容**: "把[内容]加到[文档名]的[开头/结尾]"
   - 示例: "把今天的会议要点加到项目周报的结尾"

2. **切换文档**: "打开[文档名]"
   - 示例: "打开学习笔记"

3. **查看文档**: "查看[文档名]" 或 "显示[文档名]"
   - 示例: "显示项目周报"

4. **清空文档**: "删除[文档名]所有内容" 或 "清空[文档名]"
   - 示例: "删除默认文档所有内容"
   - 注意: 此操作需要二次确认

5. **重置对话**: "重置对话" 或 "清空对话历史"
   - 示例: "重置对话"

6. **帮助**: "帮助" 或 "能做什么"
   - 显示功能说明

7. **退出**: "退出"
   - 结束会话

### API 使用

#### 聊天接口

```bash
POST /api/chat
Content-Type: application/json

{
  "session_id": "session_xxx",  # 可选，首次请求可不提供
  "text": "把测试内容加到默认文档"
}
```

响应:
```json
{
  "response_type": "TEXT",  # TEXT | CONFIRMATION | DOCUMENT
  "content": "已成功将内容添加到文档 '默认文档' 的结尾。",
  "new_session_id": "session_xxx"  # 首次请求时返回
}
```

#### 文档列表接口

```bash
GET /api/documents?session_id=session_xxx
```

响应:
```json
{
  "documents": ["默认文档", "项目周报", "学习笔记"]
}
```

## 技术栈

- **后端**: Python 3.8+, FastAPI, Uvicorn
- **前端**: HTML5, CSS3, JavaScript (原生)
- **LLM**: 阿里云百炼智能体应用（基于通义千问）
- **存储**: 本地文本文件

## 开发说明

### 代码结构

项目采用模块化设计：
- `config.py`: 配置管理
- `document_manager.py`: 文档管理
- `intent_recognizer.py`: 意图识别
- `smart_clip_llm.py`: 核心对话引擎
- `api_server.py`: API 服务器
- `main.py`: 命令行入口

### 扩展开发

1. **添加新意图**: 在 `intent_recognizer.py` 中扩展意图识别逻辑
2. **添加新功能**: 在 `document_manager.py` 中添加新的文档操作方法
3. **修改 UI**: 编辑 `frontend/` 目录下的 HTML、CSS、JS 文件

## 常见问题

### 1. 后端无法启动
- 检查 Python 版本（需要 3.8+）
- 检查依赖是否安装: `pip install -r requirements.txt`
- 检查端口 8000 是否被占用

### 2. 前端无法连接后端
- 确认后端服务器已启动（访问 `http://127.0.0.1:8000/docs` 测试）
- 检查 `frontend/app.js` 中的 `API_CONFIG.baseURL` 配置
- 检查浏览器控制台的错误信息

### 3. LLM 调用失败
- 检查 `config_local.py` 中的 API Key 和应用 ID 是否正确
- 检查网络连接
- 查看后端日志中的错误信息

### 4. 端口被占用
- 使用 `stop_all.bat` 停止所有服务器
- 或手动查找并关闭占用端口的进程

## 许可证

本项目为个人项目，仅供学习和参考使用。

## 更新日志

详细的代码迭代记录请查看 `代码迭代记录.docx` 文件。

