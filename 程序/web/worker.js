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
        ? JSON.stringify([
            "欢迎使用灵辑 (Mindscribe) - AI 智能笔记助手",
            "",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            "",
            "## 📖 产品概述",
            "",
            "灵辑 (Mindscribe) 是一款基于大语言模型 (LLM) 的智能笔记管理助手，致力于帮助用户高效整理和管理碎片化笔记内容。通过自然语言对话交互，智能理解用户意图，自动将笔记内容分类、整理并永久存储在云端。",
            "",
            "## ✨ 核心功能",
            "",
            "### 1. 🤖 智能对话交互",
            "• 通过自然语言与系统交互，无需记忆复杂命令",
            "• 支持多种指令：添加笔记、查看内容、切换文档、创建新文档等",
            "• AI 智能理解用户意图，提供精准响应",
            "",
            "### 2. 📝 多文档管理",
            "• 支持创建多个独立文档，分类管理不同主题的笔记",
            "• 快速切换文档，查看不同文档的内容",
            "• 文档列表清晰展示，方便快速定位",
            "",
            "### 3. ☁️ 云端永久存储",
            "• 基于 Cloudflare D1 数据库，数据安全可靠",
            "• 支持跨设备访问，随时随地查看和编辑笔记",
            "• 数据永久保存，无需担心丢失",
            "",
            "### 4. 🔐 权限管理",
            "• 开发者模式：输入 '开发者模式#000' 启用高级功能",
            "• 修改模式：输入 'set000' 启用笔记修改权限",
            "• 只读文档保护，防止误操作",
            "",
            "### 5. 👁️ 完整查看功能",
            "• 一键查看当前文档的全部内容",
            "• 支持滚动浏览，查看完整笔记",
            "• 弹窗显示，不影响当前操作",
            "",
            "## 🎯 使用场景",
            "",
            "### 个人知识管理",
            "• 记录学习笔记、读书心得、工作要点",
            "• 整理碎片化信息，构建个人知识库",
            "",
            "### 项目文档管理",
            "• 记录项目进展、会议纪要、任务清单",
            "• 分类管理不同项目的文档",
            "",
            "### 创意收集",
            "• 随时记录灵感、想法、创意",
            "• 通过对话快速添加内容，无需复杂操作",
            "",
            "## 🚀 快速开始",
            "",
            "### 基本操作",
            "1. **添加笔记**：直接输入内容，系统会自动添加到当前文档",
            "2. **查看文档**：点击「查看文档」按钮，查看当前文档的全部内容",
            "3. **切换文档**：点击文档切换按钮，选择要查看的文档",
            "4. **创建文档**：在文档列表底部点击「新建文档」，创建新的笔记文档",
            "",
            "### 常用指令",
            "• `查看所有笔记` - 查看所有文档的完整内容",
            "• `切换到[文档名]` - 切换到指定文档",
            "• `创建文档[文档名]` - 创建新的文档",
            "• `set000` - 启用修改权限（修改已有笔记）",
            "• `开发者模式#000` - 启用开发者模式",
            "",
            "## 🏗️ 技术架构",
            "",
            "### 前端技术",
            "• HTML5 + CSS3 + JavaScript",
            "• 响应式设计，支持多种设备",
            "• 现代化 UI 设计，提供流畅的用户体验",
            "",
            "### 后端技术",
            "• Python FastAPI 框架",
            "• Cloudflare D1 数据库（SQLite）",
            "• Cloudflare Workers（边缘计算）",
            "",
            "### AI 能力",
            "• 基于大语言模型的意图识别",
            "• 自然语言处理和理解",
            "• 智能内容分类和整理",
            "",
            "## 📋 模式说明",
            "",
            "### 试用模式",
            "• 无需登录即可使用",
            "• 提供「试用文档」和「PM问答笔记」两个默认文档",
            "• 数据存储在云端，但退出后可能被清理",
            "",
            "### 开发者模式",
            "• 登录后启用，提供完整功能",
            "• 包含「介绍文档」和「更新记录日志」",
            "• 数据永久保存，支持高级功能",
            "",
            "## 👨‍💻 开发团队",
            "",
            "**开发者：** 刘莫昕",
            "",
            "感谢您使用灵辑！我们致力于为您提供更好的笔记管理体验。",
            "",
            "## 📌 注意事项",
            "",
            "• 介绍文档为只读文档，用于介绍系统设计内容",
            "• 如需修改其他笔记，请先输入 'set000' 启用修改权限",
            "• 开发者模式和试用模式的文档完全独立，互不可见",
            "• 建议定期备份重要内容",
            "",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            "",
            "**版本：** Beta",
            "**更新日期：** 2024年12月",
            ""
          ])
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
      return new Response('Not Found', { status: 404, headers: CORS_HEADERS });
    }
  },
};

