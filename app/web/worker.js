/**
 * Cloudflare Workers 后端
 * 灵辑 (Mindscribe) - 智能笔记助手
 * 支持云端永久保存和开发者模式
 */

// 开发者模式配置
const DEV_MODE_CODE = "开发者模式#000";

// 响应头配置
const CORS_HEADERS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
};

/**
 * 处理 CORS 预检请求
 */
function handleOptions() {
  return new Response(null, {
    headers: CORS_HEADERS,
  });
}

/**
 * 从 KV 获取数据
 */
async function getKV(key, namespace) {
  try {
    return await namespace.get(key);
  } catch (error) {
    console.error(`[KV错误] 获取键 '${key}' 失败:`, error);
    return null;
  }
}

/**
 * 向 KV 写入数据
 */
async function putKV(key, value, namespace) {
  try {
    await namespace.put(key, value);
    return true;
  } catch (error) {
    console.error(`[KV错误] 写入键 '${key}' 失败:`, error);
    return false;
  }
}

/**
 * 从 KV 删除数据
 */
async function deleteKV(key, namespace) {
  try {
    await namespace.delete(key);
    return true;
  } catch (error) {
    console.error(`[KV错误] 删除键 '${key}' 失败:`, error);
    return false;
  }
}

/**
 * 列出 KV 中匹配前缀的所有键
 */
async function listKV(prefix, namespace) {
  try {
    const keys = await namespace.list({ prefix });
    return keys.keys.map(key => key.name);
  } catch (error) {
    console.error(`[KV错误] 列出键失败:`, error);
    return [];
  }
}

/**
 * 检查开发者模式状态
 */
async function checkDevMode(namespace) {
  const value = await getKV("dev_mode_enabled", namespace);
  return value === "true";
}

/**
 * 启用开发者模式
 */
async function enableDevMode(namespace) {
  return await putKV("dev_mode_enabled", "true", namespace);
}

/**
 * 获取元数据
 */
async function getMetadata(namespace) {
  const value = await getKV("metadata", namespace);
  if (value) {
    try {
      return JSON.parse(value);
    } catch (e) {
      return { active_doc_title: "试用文档" };
    }
  }
  return { active_doc_title: "试用文档" };
}

/**
 * 保存元数据
 */
async function saveMetadata(metadata, namespace) {
  return await putKV("metadata", JSON.stringify(metadata), namespace);
}

/**
 * 获取文档内容
 */
async function getDocument(title, namespace) {
  const key = `doc:${title}`;
  const value = await getKV(key, namespace);
  if (value) {
    try {
      const data = JSON.parse(value);
      return data.content || [];
    } catch (e) {
      return [];
    }
  }
  return [];
}

/**
 * 保存文档内容
 */
async function saveDocument(title, content, namespace) {
  const key = `doc:${title}`;
  const data = {
    title: title,
    content: content,
    updated_at: new Date().toISOString()
  };
  return await putKV(key, JSON.stringify(data), namespace);
}

/**
 * 列出所有文档
 */
async function listDocuments(namespace) {
  const keys = await listKV("doc:", namespace);
  return keys.map(key => key.replace("doc:", ""));
}

/**
 * 处理开发者模式请求
 */
async function handleDevMode(request, namespace, db) {
  const { code, session_id } = await request.json();
  
  if (code === DEV_MODE_CODE) {
    // 如果使用 D1 数据库
    if (db) {
      await db.prepare(
        "INSERT OR REPLACE INTO dev_mode_status (session_id, enabled, updated_at) VALUES (?, 1, CURRENT_TIMESTAMP)"
      ).bind(session_id || `session_${Date.now()}`).run();
    } else if (namespace) {
      await enableDevMode(namespace);
    }
    
    return new Response(JSON.stringify({
      response_type: "TEXT",
      content: "✅ 开发者模式已启用！您现在可以访问和修改云端永久保存的笔记。",
      dev_mode_enabled: true
    }), {
      headers: { ...CORS_HEADERS, 'Content-Type': 'application/json' },
    });
  } else {
    return new Response(JSON.stringify({
      response_type: "TEXT",
      content: "❌ 开发者模式代码不正确。请输入 '开发者模式#000'。",
      dev_mode_enabled: false
    }), {
      headers: { ...CORS_HEADERS, 'Content-Type': 'application/json' },
    });
  }
}

/**
 * 处理聊天请求
 */
async function handleChat(request, namespace, db) {
  const { text, session_id, mode, doc_type, is_trial_mode } = await request.json();
  
  // 检查是否是开发者模式代码
  if (text === DEV_MODE_CODE) {
    await enableDevMode(namespace);
    return new Response(JSON.stringify({
      response_type: "TEXT",
      content: "✅ 开发者模式已启用！您现在可以访问和修改云端永久保存的笔记。",
      new_session_id: session_id || `session_${Date.now()}`,
      dev_mode_enabled: true
    }), {
      headers: { ...CORS_HEADERS, 'Content-Type': 'application/json' },
    });
  }
  
  // 检查开发者模式状态
  const devModeEnabled = await checkDevMode(namespace);
  
  // 这里应该调用 LLM API 来处理用户输入
  // 由于 Cloudflare Workers 环境限制，建议使用外部 LLM API
  // 或者将 LLM 处理逻辑放在另一个服务中
  
  // 示例：简单的响应
  return new Response(JSON.stringify({
    response_type: "TEXT",
    content: "收到您的消息。开发者模式状态: " + (devModeEnabled ? "已启用" : "未启用"),
    dev_mode_enabled: devModeEnabled
  }), {
    headers: { ...CORS_HEADERS, 'Content-Type': 'application/json' },
  });
}

/**
 * 处理文档列表请求
 */
async function handleDocuments(request, namespace, db) {
  const url = new URL(request.url);
  const sessionId = url.searchParams.get('session_id');
  const docType = url.searchParams.get('doc_type') || 'dev';
  const isTrial = url.searchParams.get('is_trial') === 'true';
  
  let documents = [];
  
  // 如果使用 D1 数据库
  if (db) {
    if (docType === 'dev' || !isTrial) {
      // 获取开发者文档
      const result = await db.prepare("SELECT title FROM dev_documents").all();
      documents = result.results ? result.results.map(row => row.title) : [];
    } else {
      // 获取试用文档
      if (sessionId) {
        const result = await db.prepare(
          "SELECT title FROM trial_documents WHERE session_id = ?"
        ).bind(sessionId).all();
        documents = result.results ? result.results.map(row => row.title) : [];
      }
    }
    
    // 如果没有文档，创建试用文档
    if (documents.length === 0) {
      const defaultTitle = docType === 'dev' ? '介绍文档' : '试用文档';
      const defaultContent = docType === 'dev' 
        ? JSON.stringify(["欢迎使用灵辑 (Mindscribe) - AI 智能笔记助手", "", "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", "", "## 📖 产品概述", "", "灵辑 (Mindscribe) 是一款基于大语言模型 (LLM) 的智能笔记管理助手，致力于帮助用户高效整理和管理碎片化笔记内容。通过自然语言对话交互，智能理解用户意图，自动将笔记内容分类、整理并永久存储在云端。", "", "## ✨ 核心功能", "", "1) 🤖 智能对话交互：自然语言添加/查看/切换/创建文档，意图识别与结构化整理", "2) 📝 多文档管理：支持多文档并行，快速切换；试用/开发模式文档完全隔离", "3) ☁️ 云端永久存储：Cloudflare D1 持久化，跨设备访问", "4) 🔐 权限与只读保护：开发者模式、修改模式(set000)，只读文档防误改", "5) 👁️ 完整查看：弹窗滚动查看当前文档全部内容", "", "## 🧠 模型与选择", "", "• 主模型：通义千问 3 - coder - plus（针对代码与长文本处理优化）", "• 选型理由：代码理解与生成能力强，长文本上下文处理稳健，适合笔记/文档场景", "• 托管策略：前端调用后端统一网关，支持按需切换/灰度替换", "", "## 🔍 竞品分析", "", "| 维度 | Notion | Obsidian | Evernote | MindScribe (灵辑) |", "| :--- | :--- | :--- | :--- | :--- |", "| **核心方案** | 数据库 + 模板 | 双向链接 + 标签 | 笔记本分类 | F2K + 混沌缓冲区 |", "| **用户痛点** | 需要提前设计结构，维护成本高 | 需要手动建立连接，图谱易杂乱 | 层级固定，难以适应动态知识 | 整理太累，不想分类 |", "| **整理方式** | 手动分类/属性标记 | 手动引用/打标签 | 手动拖拽/归档 | **AI 自动整理 (RAG)** |", "| **优势** | 强大的协作与项目管理 | 本地优先，知识网络化 | 剪藏功能强，老牌稳定 | **极致懒人，丢进去就行** |", "", "## 🧪 A/B 测试与训练", "", "• A/B 范围：回复准确性、段落分段质量、长文截断与拼接、指令跟随度", "• 指标示例：回答一致性、命中率、格式合规率、用户二次编辑率", "• 数据：仅使用脱敏/合规数据；不存储用户隐私输入；日志最小化", "• 回滚策略：任一实验指标低于基线自动回退；支持分文档、分会话灰度", "", "## 🏗️ 技术架构（概览）", "", "• 前端：原生 JS + CSS，双模式（试用/开发），弹窗查看全文", "• 后端：Python FastAPI；会话管理 + 文档管理", "• 存储：Cloudflare D1（dev 文档/试用文档分表；session_id 作用于试用表）", "• 边缘：Cloudflare Workers（静态与接口代理）；KV 作为回退/缓存", "", "## 📋 模式说明", "", "• 试用模式：文档 = 试用文档（空白）、PM问答笔记；数据隔离，可能被清理", "• 开发者模式：文档 = 介绍文档（本页）、更新记录日志；云端长期保存", "", "## 🚀 快速开始", "", "1. 查看文档：点击「查看文档」按钮，弹窗展示全文，可滚动查看", "2. 切换文档：点击切换按钮，在列表中选择目标文档", "3. 创建文档：在文档列表底部点击「新建文档」", "4. 修改权限：输入 set000 开启修改；未开启时只读", "5. 开发者模式：输入 开发者模式#000 启用", "", "## 📌 注意事项", "", "• 介绍文档为只读；试用/开发模式文档完全隔离", "• D1 持久化；本地调试若无 D1 会回退内存，刷新即失", "• 建议重要内容定期备份", "", "## 📦 终极产品形态：混沌缓冲区 (The Chaos Box)", "", "**“别让我思考，直接记下来。”**", "", "### 1. 核心痛点", "用户在记录灵感或碎片信息时，往往被“放在哪里”、“叫什么标题”、“打什么标签”打断思路。MindScribe 的终极目标是消除这些阻力。", "", "### 2. 功能设计", "• **极速入口**：一个类似聊天框的输入界面（支持文本、语音、图片）。", "• **只管丢**：用户只需将任何内容“丢”进混沌缓冲区，无需任何整理操作。", "• **后台处理**：AI 在后台静默运行，分析缓冲区内容，自动提取主题、摘要，并归档到 F2K 结构中。", "• **定期汇报**：系统定期（如每天/每周）生成“整理报告”，告诉用户：“我帮你把关于‘量子力学’的笔记归档到了物理笔记本，把‘买牛奶’加到了待办事项。”", "", "### 3. 价值主张", "从“辅助整理”进化为“替你整理”。让用户专注于**思考和记录**，将**组织和管理**完全交给 AI。", "", "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", "版本：Beta | 更新：2025-12-30 | 模型：通义千问3-coder-plus", ""])
        : JSON.stringify([""]); // 试用文档默认空白
      
      if (docType === 'dev') {
        await db.prepare(
          "INSERT OR REPLACE INTO dev_documents (title, content, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP)"
        ).bind(defaultTitle, defaultContent).run();
      } else if (sessionId) {
        await db.prepare(
          "INSERT OR REPLACE INTO trial_documents (session_id, title, content, updated_at) VALUES (?, ?, ?, CURRENT_TIMESTAMP)"
        ).bind(sessionId, defaultTitle, defaultContent).run();
      }
      documents = [defaultTitle];
    }
  } else if (namespace) {
    // 使用 KV 存储（向后兼容）
    documents = await listDocuments(namespace);
    
    if (documents.length === 0) {
      await saveDocument("试用文档", [""], namespace);
      await saveMetadata({ active_doc_title: "试用文档" }, namespace);
      documents = ["试用文档"];
    }
  }
  
  return new Response(JSON.stringify({
    documents: documents
  }), {
    headers: { ...CORS_HEADERS, 'Content-Type': 'application/json' },
  });
}

/**
 * D1 数据库初始化
 */
async function initD1Database(db) {
  try {
    // 创建开发者文档表
    await db.exec(`
      CREATE TABLE IF NOT EXISTS dev_documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL UNIQUE,
        content TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
      )
    `);
    
    // 创建试用文档表
    await db.exec(`
      CREATE TABLE IF NOT EXISTS trial_documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(session_id, title)
      )
    `);
    
    // 创建元数据表
    await db.exec(`
      CREATE TABLE IF NOT EXISTS metadata (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
      )
    `);
    
    // 创建开发者模式状态表
    await db.exec(`
      CREATE TABLE IF NOT EXISTS dev_mode_status (
        session_id TEXT PRIMARY KEY,
        enabled INTEGER DEFAULT 0,
        edit_mode_enabled INTEGER DEFAULT 0,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
      )
    `);
    
    return true;
  } catch (error) {
    console.error('[D1错误] 初始化数据库失败:', error);
    return false;
  }
}

/**
 * 主处理函数
 */
export default {
  async fetch(request, env) {
    // 处理 CORS 预检请求
    if (request.method === 'OPTIONS') {
      return handleOptions();
    }
    
    const url = new URL(request.url);
    const path = url.pathname;
    
    // 获取 KV namespace 和 D1 数据库（需要在 wrangler.toml 中配置）
    const NOTES_KV = env.NOTES_KV;
    const DB = env.DB; // D1 数据库
    
    // 初始化 D1 数据库（如果存在）
    if (DB) {
      await initD1Database(DB);
    }
    
    // 路由处理
    if (path === '/api/chat' && request.method === 'POST') {
      return handleChat(request, NOTES_KV, DB);
    } else if (path === '/api/documents' && request.method === 'GET') {
      return handleDocuments(request, NOTES_KV, DB);
    } else if (path === '/api/dev-mode' && request.method === 'POST') {
      return handleDevMode(request, NOTES_KV, DB);
    } else if (path === '/' || path === '') {
      return new Response(JSON.stringify({
        name: "灵辑 API (Cloudflare Workers)",
        version: "1.0.0",
        status: "running",
        storage: DB ? "D1 Database" : (NOTES_KV ? "KV Storage" : "None"),
        endpoints: {
          chat: "/api/chat",
          documents: "/api/documents",
          dev_mode: "/api/dev-mode"
        }
      }), {
        headers: { ...CORS_HEADERS, 'Content-Type': 'application/json' },
      });
    } else {
      // 尝试从静态资源获取 (Cloudflare Pages 特性)
      if (env.ASSETS) {
        try {
          const assetResponse = await env.ASSETS.fetch(request);
          if (assetResponse.status !== 404) {
            return assetResponse;
          }
        } catch (e) {
          console.error("Error fetching asset:", e);
        }
      }
      
      return new Response('Not Found', { status: 404, headers: CORS_HEADERS });
    }
  },
};

