# Cloudflare Workers 部署指南

## 概述

本文档说明如何将灵辑 (Mindscribe) 后端部署到 Cloudflare Workers，实现云端永久保存笔记功能。

## 前置要求

1. Cloudflare 账户
2. Node.js 和 npm 已安装
3. Wrangler CLI 已安装

## 安装步骤

### 1. 安装 Wrangler CLI

```bash
npm install -g wrangler
```

### 2. 登录 Cloudflare

```bash
wrangler login
```

### 3. 创建 KV Namespace

```bash
# 创建生产环境 KV Namespace
wrangler kv:namespace create "NOTES_KV"

# 创建预览环境 KV Namespace
wrangler kv:namespace create "NOTES_KV" --preview
```

执行后会返回 Namespace ID，例如：
```
🌀  Creating namespace with title "NOTES_KV"
✨  Success!
Add the following to your configuration file in your kv_namespaces array:
{ binding = "NOTES_KV", id = "abc123def456..." }
```

### 4. 更新 wrangler.toml

将返回的 Namespace ID 填入 `wrangler.toml` 文件中的 `id` 字段：

```toml
[[kv_namespaces]]
binding = "NOTES_KV"
id = "你的实际 Namespace ID"
```

### 5. 部署到 Cloudflare Workers

```bash
# 部署到生产环境
npm run deploy

# 或使用 wrangler 直接部署
wrangler deploy
```

### 6. 获取 Workers URL

部署成功后，Wrangler 会显示 Workers URL，例如：
```
https://smart-clip-api.your-subdomain.workers.dev
```

## 配置前端

更新 `frontend/app.js` 中的 `API_CONFIG.baseURL`：

```javascript
const API_CONFIG = {
    baseURL: 'https://smart-clip-api.your-subdomain.workers.dev',
    // ...
};
```

## 使用开发者模式

1. 在网页中输入：`开发者模式#000`
2. 系统会启用开发者模式
3. 现在可以访问和修改云端永久保存的笔记

## 注意事项

1. **KV 存储限制**：
   - 免费版：100,000 次读取/天，1,000 次写入/天
   - 付费版：无限制

2. **Workers 限制**：
   - 免费版：100,000 次请求/天
   - CPU 时间：10ms（免费版），50ms（付费版）

3. **LLM API 调用**：
   - 当前 `worker.js` 中的 LLM 处理是示例代码
   - 实际部署时，需要将 LLM API 调用逻辑集成到 Workers 中
   - 或者使用外部 API 服务处理 LLM 请求

## 故障排除

### KV Namespace 未绑定

如果遇到 "KV namespace not found" 错误，检查：
1. `wrangler.toml` 中的 Namespace ID 是否正确
2. 是否已创建并绑定了 KV Namespace

### CORS 错误

如果前端遇到 CORS 错误，检查 `worker.js` 中的 `CORS_HEADERS` 配置是否正确。

### 开发者模式不工作

检查：
1. 输入的代码是否完全匹配：`开发者模式#000`
2. KV 存储是否正常工作
3. Workers 日志中是否有错误信息

## 更新部署

修改代码后，重新部署：

```bash
wrangler deploy
```

## 查看日志

```bash
wrangler tail
```

## 本地开发

```bash
npm run dev
```

这会在本地启动一个开发服务器，可以测试 Workers 功能。

