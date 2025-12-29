# 如何打开本地网页

## 方法一：直接打开 HTML 文件（最简单）

### Windows 系统

1. **使用批处理文件（推荐）**
   - 双击 `打开网页.bat` 文件
   - 网页会自动在默认浏览器中打开

2. **手动打开**
   - 进入 `frontend` 文件夹
   - 找到 `index.html` 文件
   - 双击打开，会在默认浏览器中打开

3. **使用 PowerShell**
   - 右键点击 `打开网页.ps1`
   - 选择"使用 PowerShell 运行"
   - 网页会自动打开

### Mac/Linux 系统

```bash
# 进入前端目录
cd frontend

# 使用默认浏览器打开
open index.html        # Mac
xdg-open index.html    # Linux
```

---

## 方法二：使用本地服务器（推荐，避免 CORS 问题）

### 使用 Python 内置服务器

```bash
# 进入前端目录
cd frontend

# Python 3
python -m http.server 8080

# Python 2
python -m SimpleHTTPServer 8080
```

然后在浏览器中访问：`http://localhost:8080`

### 使用 Node.js http-server

```bash
# 安装 http-server（如果还没有）
npm install -g http-server

# 进入前端目录
cd frontend

# 启动服务器
http-server -p 8080
```

然后在浏览器中访问：`http://localhost:8080`

### 使用 VS Code Live Server 扩展

1. 在 VS Code 中安装 "Live Server" 扩展
2. 右键点击 `index.html`
3. 选择 "Open with Live Server"
4. 网页会自动在浏览器中打开

---

## 方法三：使用 Wrangler 本地开发（如果使用 Cloudflare Workers）

```bash
# 进入 web 目录
cd web

# 启动本地开发服务器
wrangler dev
```

---

## 重要提示

### 1. 后端 API 配置

当前前端配置的 API 地址是：
- **默认地址**：`https://mindscribe-api-8zop.onrender.com`（云端部署）

如果您的后端在本地运行：

1. **修改 API 地址**
   - 打开 `frontend/app.js`
   - 找到 `API_CONFIG` 配置
   - 修改 `baseURL` 为本地地址：
     ```javascript
     const API_CONFIG = {
         baseURL: 'http://localhost:8000',  // 本地后端地址
         endpoints: {
             chat: '/api/chat',
             documents: '/api/documents'
         }
     };
     ```

2. **启动本地后端服务器**
   ```bash
   # 进入项目根目录
   cd 程序
   
   # 启动 API 服务器
   python api_server.py
   # 或
   python web/api_server.py
   ```

### 2. 开发者模式页面

如果要打开开发者模式页面：
- 直接打开 `frontend/dev-mode.html`
- 或访问 `http://localhost:8080/dev-mode.html`（如果使用本地服务器）

### 3. 登录/试用选择

首次打开 `index.html` 时，会自动显示登录/试用选择界面：
- **登录**：点击后不做任何反馈（功能待实现）
- **试用**：立即体验，数据临时存储

---

## 快速开始

### 最简单的方式（推荐）

1. **双击 `打开网页.bat`**（Windows）
   - 或右键 `打开网页.ps1` → "使用 PowerShell 运行"

2. **网页会自动在浏览器中打开**

3. **选择"试用"开始体验**

---

## 故障排除

### 问题 1：网页打开但无法连接后端

**解决方法：**
- 检查后端服务器是否运行
- 检查 API 地址配置是否正确
- 查看浏览器控制台（F12）的错误信息

### 问题 2：CORS 错误

**解决方法：**
- 使用本地服务器（方法二）而不是直接打开文件
- 或确保后端服务器已配置 CORS

### 问题 3：样式或脚本未加载

**解决方法：**
- 确保所有文件都在 `frontend` 目录下
- 检查文件路径是否正确
- 使用本地服务器而不是直接打开文件

---

## 文件结构

```
程序/
├── frontend/
│   ├── index.html          # 主页面（登录/试用选择）
│   ├── dev-mode.html       # 开发者模式页面
│   ├── app.js              # 主应用逻辑
│   ├── dev-mode-app.js     # 开发者模式逻辑
│   ├── style.css           # 主样式
│   ├── dev-mode-style.css  # 开发者模式样式
│   ├── login-modal.css     # 登录/试用界面样式
│   └── login-modal.js      # 登录/试用逻辑
├── 打开网页.bat            # Windows 快速打开脚本
└── 打开网页.ps1            # PowerShell 快速打开脚本
```

---

## 下一步

打开网页后：
1. 选择"试用"或"登录"
2. 开始使用灵辑智能笔记助手
3. 输入 `开发者模式#000` 进入开发者模式（全红界面）

