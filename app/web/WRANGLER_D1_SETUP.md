# Wrangler D1 数据库配置指南

## 确认配置

是的，项目使用 **Wrangler** 管理 Cloudflare Workers。

## D1 数据库绑定配置

已在 `wrangler.toml` 中添加 D1 数据库绑定配置：

```toml
[[d1_databases]]
binding = "DB"
database_name = "smart-clip-db"
database_id = "8fb7b530-17e4-44f1-819f-ee585effdbf2"
```

## 配置说明

### 1. 绑定名称
- `binding = "DB"`：在 Worker 代码中通过 `env.DB` 访问 D1 数据库

### 2. 数据库信息
- `database_name = "smart-clip-db"`：数据库名称（用于标识）
- `database_id = "8fb7b530-17e4-44f1-819f-ee585effdbf2"`：您的 D1 数据库 ID

## 在 Worker 中使用

在 `worker.js` 中，D1 数据库通过 `env.DB` 访问：

```javascript
export default {
  async fetch(request, env) {
    const DB = env.DB; // D1 数据库对象
    
    // 使用 D1 数据库
    if (DB) {
      const result = await DB.prepare("SELECT * FROM dev_documents").all();
      // ...
    }
  }
}
```

## 数据库表结构

系统会自动创建以下表：

1. **dev_documents** - 开发者文档表
2. **trial_documents** - 试用文档表
3. **metadata** - 元数据表
4. **dev_mode_status** - 开发者模式状态表

## 部署步骤

1. **确认 D1 数据库已创建**
   ```bash
   wrangler d1 list
   ```

2. **部署 Worker**
   ```bash
   cd web
   wrangler deploy
   ```

3. **验证配置**
   访问 Worker URL，检查响应中是否显示 `"storage": "D1 Database"`

## 本地开发

使用 Wrangler 本地开发时，D1 数据库会自动绑定：

```bash
wrangler dev
```

## 注意事项

1. **数据库 ID**：确保 `database_id` 与您的 D1 数据库 ID 完全匹配
2. **权限**：确保 Worker 有访问 D1 数据库的权限
3. **初始化**：首次部署时，系统会自动创建所需的表结构

## 验证配置

部署后，访问根路径 `/` 应该返回：

```json
{
  "name": "灵辑 API (Cloudflare Workers)",
  "version": "1.0.0",
  "status": "running",
  "storage": "D1 Database",
  "endpoints": {
    "chat": "/api/chat",
    "documents": "/api/documents",
    "dev_mode": "/api/dev-mode"
  }
}
```

如果 `storage` 显示 `"D1 Database"`，说明配置成功！

