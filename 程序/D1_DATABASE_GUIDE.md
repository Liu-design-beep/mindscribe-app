# D1 数据库集成指南

## 概述

系统现在使用 Cloudflare D1 数据库进行数据存储，数据库 ID：`8fb7b530-17e4-44f1-819f-ee585effdbf2`

## 功能特性

### 1. 文档分离存储
- **开发者文档**：存储在 `dev_documents` 表，永久保存
- **试用文档**：存储在 `trial_documents` 表，按会话ID分离，退出时删除

### 2. 登录/试用选择
- 首次进入显示选择界面
- **登录**：点击后不做任何反馈（功能待实现）
- **试用**：立即体验，数据临时存储

### 3. 试用模式提示
- 顶部显示警告横幅
- 提示：退出网页会把记录全部删除
- 需要登录才具备云端存储功能

## 数据库表结构

### dev_documents（开发者文档表）
```sql
CREATE TABLE IF NOT EXISTS dev_documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL UNIQUE,
    content TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
)
```

### trial_documents（试用文档表）
```sql
CREATE TABLE IF NOT EXISTS trial_documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(session_id, title)
)
```

### metadata（元数据表）
```sql
CREATE TABLE IF NOT EXISTS metadata (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
)
```

### dev_mode_status（开发者模式状态表）
```sql
CREATE TABLE IF NOT EXISTS dev_mode_status (
    session_id TEXT PRIMARY KEY,
    enabled INTEGER DEFAULT 0,
    edit_mode_enabled INTEGER DEFAULT 0,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
)
```

## 文件结构

### 新增文件
```
web/
├── d1_storage.py              # D1 数据库存储适配器
└── d1_document_manager.py     # D1 文档管理器

frontend/
├── login-modal.css            # 登录/试用选择界面样式
├── login-modal.js             # 登录/试用选择逻辑
└── login-trial-modal.html     # 登录/试用选择界面（已集成到 index.html）
```

### 修改的文件
```
frontend/
└── index.html                 # 集成登录/试用选择界面
```

## 使用流程

### 1. 首次访问
- 显示登录/试用选择界面
- 用户选择"登录"或"试用"

### 2. 选择试用
- 生成试用会话ID
- 保存到 localStorage
- 显示试用模式警告横幅
- 数据存储在 `trial_documents` 表

### 3. 选择登录
- 保存选择到 localStorage
- 隐藏选择界面（不做任何反馈）
- 登录功能待实现

### 4. 退出试用模式
- 页面卸载时自动清理试用数据
- 从 D1 数据库删除该会话的所有文档

## API 集成

### 请求参数
需要在 API 请求中包含：
- `doc_type`: "dev" 或 "trial"
- `session_id`: 会话ID（试用模式必需）
- `is_trial_mode`: 是否为试用模式

### 响应格式
```json
{
  "response_type": "TEXT",
  "content": "响应内容",
  "doc_type": "trial",
  "session_id": "trial_xxx"
}
```

## Cloudflare Workers 配置

### wrangler.toml
```toml
[[d1_databases]]
binding = "DB"
database_name = "smart-clip-db"
database_id = "8fb7b530-17e4-44f1-819f-ee585effdbf2"
```

### worker.js 中使用
```javascript
export default {
  async fetch(request, env) {
    const db = env.DB; // D1 数据库对象
    // 使用 db 进行数据库操作
  }
}
```

## 注意事项

1. **数据分离**：开发者文档和试用文档完全分离，互不影响
2. **会话管理**：试用模式使用 session_id 区分不同用户的试用数据
3. **自动清理**：试用模式退出时自动清理数据
4. **登录功能**：登录功能待实现，目前点击登录不做任何反馈

## 测试清单

- [ ] 首次访问显示登录/试用选择界面
- [ ] 选择试用后进入应用
- [ ] 试用模式显示警告横幅
- [ ] 试用数据正确存储到 D1 数据库
- [ ] 退出时自动清理试用数据
- [ ] 选择登录后隐藏界面（无反馈）
- [ ] 开发者文档和试用文档分离存储

