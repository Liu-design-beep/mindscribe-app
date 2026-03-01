/**
 * 开发者模式前端应用
 * 全红界面，只读模式，直接显示介绍文档和更新记录日志
 */

// 本地文档内容（不需要API调用）
const LOCAL_DOCUMENTS = {
    '介绍文档': [
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
    "1) 🤖 智能对话交互：自然语言添加/查看/切换/创建文档，意图识别与结构化整理",
    "2) 📝 多文档管理：支持多文档并行，快速切换；试用/开发模式文档完全隔离",
    "3) ☁️ 云端永久存储：Cloudflare D1 持久化，跨设备访问",
    "4) 🔐 权限与只读保护：开发者模式、修改模式(set000)，只读文档防误改",
    "5) 👁️ 完整查看：弹窗滚动查看当前文档全部内容",
    "",
    "## 🧠 模型与选择",
    "",
    "• 主模型：通义千问 3 - coder - plus（针对代码与长文本处理优化）",
    "• 选型理由：代码理解与生成能力强，长文本上下文处理稳健，适合笔记/文档场景",
    "• 托管策略：前端调用后端统一网关，支持按需切换/灰度替换",
    "",
    "## 🔍 竞品分析",
    "",
    "| 维度 | Notion | Obsidian | Evernote | MindScribe (灵辑) |",
    "| :--- | :--- | :--- | :--- | :--- |",
    "| **核心方案** | 数据库 + 模板 | 双向链接 + 标签 | 笔记本分类 | F2K + 混沌缓冲区 |",
    "| **用户痛点** | 需要提前设计结构，维护成本高 | 需要手动建立连接，图谱易杂乱 | 层级固定，难以适应动态知识 | 整理太累，不想分类 |",
    "| **整理方式** | 手动分类/属性标记 | 手动引用/打标签 | 手动拖拽/归档 | **AI 自动整理 (RAG)** |",
    "| **优势** | 强大的协作与项目管理 | 本地优先，知识网络化 | 剪藏功能强，老牌稳定 | **极致懒人，丢进去就行** |",
    "",
    "## 🧪 A/B 测试与训练",
    "",
    "• A/B 范围：回复准确性、段落分段质量、长文截断与拼接、指令跟随度",
    "• 指标示例：回答一致性、命中率、格式合规率、用户二次编辑率",
    "• 数据：仅使用脱敏/合规数据；不存储用户隐私输入；日志最小化",
    "• 回滚策略：任一实验指标低于基线自动回退；支持分文档、分会话灰度",
    "",
    "## 🏗️ 技术架构（概览）",
    "",
    "• 前端：原生 JS + CSS，双模式（试用/开发），弹窗查看全文",
    "• 后端：Python FastAPI；会话管理 + 文档管理",
    "• 存储：Cloudflare D1（dev 文档/试用文档分表；session_id 作用于试用表）",
    "• 边缘：Cloudflare Workers（静态与接口代理）；KV 作为回退/缓存",
    "",
    "## 📋 模式说明",
    "",
    "• 试用模式：文档 = 试用文档（空白）、PM问答笔记；数据隔离，可能被清理",
    "• 开发者模式：文档 = 介绍文档（本页）、更新记录日志；云端长期保存",
    "",
    "## 🚀 快速开始",
    "",
    "1. 查看文档：点击「查看文档」按钮，弹窗展示全文，可滚动查看",
    "2. 切换文档：点击切换按钮，在列表中选择目标文档",
    "3. 创建文档：在文档列表底部点击「新建文档」",
    "4. 修改权限：输入 set000 开启修改；未开启时只读",
    "5. 开发者模式：输入 开发者模式#000 启用",
    "",
    "## 📌 注意事项",
    "",
    "• 介绍文档为只读；试用/开发模式文档完全隔离",
    "• D1 持久化；本地调试若无 D1 会回退内存，刷新即失",
    "• 建议重要内容定期备份",
    "",
    "## 📦 终极产品形态：混沌缓冲区 (The Chaos Box)",
    "",
    "**“别让我思考，直接记下来。”**",
    "",
    "### 1. 核心痛点",
    "用户在记录灵感或碎片信息时，往往被“放在哪里”、“叫什么标题”、“打什么标签”打断思路。MindScribe 的终极目标是消除这些阻力。",
    "",
    "### 2. 功能设计",
    "• **极速入口**：一个类似聊天框的输入界面（支持文本、语音、图片）。",
    "• **只管丢**：用户只需将任何内容“丢”进混沌缓冲区，无需任何整理操作。",
    "• **后台处理**：AI 在后台静默运行，分析缓冲区内容，自动提取主题、摘要，并归档到 F2K 结构中。",
    "• **定期汇报**：系统定期（如每天/每周）生成“整理报告”，告诉用户：“我帮你把关于‘量子力学’的笔记归档到了物理笔记本，把‘买牛奶’加到了待办事项。”",
    "",
    "### 3. 价值主张",
    "从“辅助整理”进化为“替你整理”。让用户专注于**思考和记录**，将**组织和管理**完全交给 AI。",
    "",
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
    "版本：Beta | 更新：2025-12-30 | 模型：通义千问3-coder-plus",
    ""
],
    'RAG架构设计文档': [
    "MindScribe RAG 架构设计文档",
    "",
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
    "",
    "## 🏗️ 架构概览",
    "",
    "MindScribe 的 RAG (Retrieval-Augmented Generation) 系统旨在解决个人知识库的“碎片化”和“非结构化”问题。不同于传统的企业级 RAG，我们的设计核心是**轻量级、低延迟、高相关性**。",
    "",
    "### 核心组件",
    "1. **Ingestion Pipeline (数据摄入)**：负责将用户的笔记、网页剪藏、PDF 等非结构化数据转化为向量。",
    "2. **Vector Store (向量存储)**：使用 Cloudflare Vectorize 进行边缘存储，确保极低的访问延迟。",
    "3. **Retrieval Engine (检索引擎)**：混合检索策略（关键词 + 语义向量）。",
    "4. **Generation (生成)**：基于通义千问 3-coder-plus 模型，结合检索到的上下文生成回答。",
    "",
    "## 🔄 数据流转 (Data Flow)",
    "",
    "### 1. 写入流程",
    "1. **用户输入**：用户通过对话框输入笔记或上传文件。",
    "2. **预处理**：",
    "   - **Chunking (分块)**：按语义段落进行切分，每块约 500 tokens，保留 50 tokens 重叠。",
    "   - **Metadata Extraction**：提取标题、标签、创建时间等元数据。",
    "3. **Embedding**：调用 Embedding API (如 bge-m3) 将文本块转化为 1024 维向量。",
    "4. **存储**：",
    "   - **原始文本** -> Cloudflare D1 (SQLite)",
    "   - **向量索引** -> Cloudflare Vectorize (关联 D1 中的 ID)",
    "",
    "### 2. 读取/问答流程",
    "1. **Query Analysis**：分析用户问题，提取关键词，判断是否需要检索。",
    "2. **Hybrid Search**：",
    "   - **向量检索**：在 Vectorize 中查找 Top-K 近邻。",
    "   - **全文检索**：在 D1 中进行关键词匹配 (FTS)。",
    "3. **Reranking (重排序)**：使用 Cross-Encoder 对混合检索结果进行精细排序，筛选出 Top-5。",
    "4. **Context Assembly**：将筛选出的片段拼接成 Prompt 上下文。",
    "5. **LLM Generation**：模型根据上下文生成最终回答。",
    "",
    "## 🧠 关键技术决策",
    "",
    "### 为什么选择 Cloudflare Vectorize?",
    "- **边缘计算亲和性**：与 Workers 完美集成，无需跨云调用，延迟极低。",
    "- **成本效益**：相比 Pinecone 或 Milvus，更适合个人知识库规模。",
    "- **元数据过滤**：支持基于 metadata 的快速过滤（如按时间、标签筛选）。",
    "",
    "### 为什么使用混合检索?",
    "- 纯向量检索在处理“专有名词”或“精确匹配”时表现不佳。",
    "- 结合关键词检索可以弥补语义检索的模糊性，特别是在代码片段或特定术语的查找中。",
    "",
    "## 🚀 未来演进：Chaos Box 集成",
    "",
    "RAG 架构将是“混沌缓冲区”的核心引擎：",
    "1. **自动归档**：后台 RAG 进程定期扫描缓冲区，检索相似的历史笔记。",
    "2. **知识链接**：自动发现新笔记与旧笔记的关联，主动提示用户“这与你上周记录的xxx有关”。",
    "3. **动态摘要**：基于 RAG 检索结果，动态生成今日/本周的知识摘要。",
    "",
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
    "版本：v1.0 | 更新：2025-12-30 | 状态：设计中",
    ""
],
    '用户数据埋点与数据飞轮设计': [
    "用户数据埋点与数据飞轮设计",
    "",
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
    "",
    "## 🔄 一、核心思路：数据飞轮的逻辑闭环",
    "",
    "数据飞轮的本质是「用户行为 → 数据积累 → 产品优化 → 更好体验 → 更多用户行为」的正向循环。对灵辑来说，飞轮的核心驱动力是笔记质量与 AI 响应准确度的相互提升。",
    "",
    "流程如下：",
    "",
    "  用户使用（记笔记 / 对话 / 切换文档）",
    "       ↓",
    "  行为数据埋点采集",
    "       ↓",
    "  分析用户意图模式 + 高频操作路径",
    "       ↓",
    "  优化 AI 提示词 / 文档匹配逻辑 / 功能推荐",
    "       ↓",
    "  用户获得更精准的笔记体验",
    "       ↓",
    "  留存率提升 → 更多数据",
    "",
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
    "",
    "## 📋 二、埋点分层设计",
    "",
    "埋点分为三个层次：",
    "",
    "| 层次 | 事件类型 | 采集目的 |",
    "| :--- | :--- | :--- |",
    "| **行为层** | 发送消息、切换文档、切换模式、点击功能按钮 | 了解核心使用路径和功能热度 |",
    "| **质量层** | AI 回复后是否继续追问、是否删除/修改 AI 生成内容 | 判断 AI 响应质量的隐性反馈 |",
    "| **留存层** | 会话时长、单次笔记字数、返访间隔 | 衡量产品粘性与用户价值 |",
    "",
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
    "",
    "## 🎯 三、最值得埋的关键事件",
    "",
    "### ★ 第一优先级（核心转化漏斗）",
    "",
    "• session_start：用户打开页面（区分试用 / 登录）",
    "• message_sent：发送消息（含消息长度、当前文档名、当前模式）",
    "• trial_mode_entered：进入试用模式",
    "• login_success：完成登录",
    "",
    "### ★ 第二优先级（功能使用深度）",
    "",
    "• doc_switched：切换文档（记录从哪个文档切到哪个）",
    "• mode_switched：切换对话模式（普通 / 面试）",
    "• knowledge_graph_opened：打开知识图谱系统",
    "• share_note_clicked：点击分享笔记",
    "• feedback_submitted：提交意见反馈",
    "",
    "### ★ 第三优先级（隐性质量信号）",
    "",
    "• ai_response_received：AI 回复完成（含响应时长）",
    "• user_continued_after_ai：AI 回复后用户继续输入（正向信号）",
    "• session_end：会话结束（含总消息数、总时长）",
    "",
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
    "",
    "## 🛠️ 四、技术实现方案",
    "",
    "### 方案 A：轻量自建（推荐先期）",
    "",
    "在 app.js 中封装一个 track(eventName, properties) 函数，将事件批量发送到后端的 /api/track 接口，后端写入数据库（SQLite 或 MySQL）。成本极低，数据完全自有。",
    "",
    "  // 示例封装",
    "  function track(event, props = {}) {",
    "    const payload = {",
    "      event,",
    "      timestamp: Date.now(),",
    "      session_id: AppState.sessionId,",
    "      user_type: AppState.isTrialMode ? 'trial' : 'logged_in',",
    "      ...props",
    "    };",
    "    navigator.sendBeacon('/api/track', JSON.stringify(payload));",
    "  }",
    "",
    "  // 使用示例",
    "  track('message_sent', { doc: AppState.currentDocument, mode: AppState.currentMode });",
    "",
    "### 方案 B：接入第三方（快速验证）",
    "",
    "接入 PostHog（开源可自部署）或 Mixpanel 免费版，几行代码即可获得完整的漏斗分析、留存分析、热图功能。适合快速验证阶段。",
    "",
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
    "",
    "## 📊 五、数据飞轮的三个关键分析维度",
    "",
    "### ① 试用转登录漏斗",
    "",
    "分析用户从进入试用模式到完成登录的路径，找到流失节点。关键问题：是在第几条消息后离开？是因为功能不够用还是体验问题？",
    "",
    "### ② 功能发现率",
    "",
    "知识图谱、面试模式、分享笔记等功能的实际使用率，判断哪些功能需要更显眼的入口，哪些可以下沉。",
    "",
    "### ③ AI 响应质量的隐性评分",
    "",
    "用「AI 回复后用户继续输入的速度和内容长度」作为 AI 质量的代理指标，无需用户主动评分，自动形成质量反馈。",
    "",
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
    "",
    "## 🚀 六、实施建议（三步走）",
    "",
    "### 第一步：埋点骨架（当前阶段）",
    "",
    "在 app.js 中加入 track() 函数骨架，埋入最核心的 5 个事件：session_start、message_sent、trial_mode_entered、login_success、doc_switched。后端用一张简单的 events 表存储。",
    "",
    "### 第二步：数据分析（2~4 周后）",
    "",
    "积累 2~4 周数据后，用 SQL 跑出漏斗报告，找到最大的流失点。",
    "",
    "### 第三步：产品迭代（根据数据结论）",
    "",
    "根据数据结论做一次针对性的产品迭代，验证飞轮是否转动。",
    "",
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
    "",
    "## 📝 七、关于数据展示的判断",
    "",
    "埋点数据不建议直接展示给用户，原因如下：",
    "",
    "• 埋点的受众是产品团队，而非用户。用户打开灵辑是为了记笔记，展示埋点数据会造成认知负担。",
    "• 「今天发了 23 条消息」对用户没有直接价值，不像健身 App 的步数那样具有激励作用。",
    "• 展示与笔记无关的信息会干扰沉浸式体验。",
    "",
    "如果未来要对用户展示，建议将数据转化为「个人成长反馈」形式（如周报 / 月报），而非原始埋点数据。",
    "",
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
    "版本：v1.0 | 更新：2026-03-01 | 状态：设计中",
    ""
    ],
        '更新记录日志': [], // 将在初始化时从 API 加载
    '系统提示词': [] // 将在初始化时从 API 加载
};

// 应用状态
const AppState = {
    sessionId: null,
    devModeEnabled: true, // 开发者模式始终启用
    editModeEnabled: false, // 开发者模式不允许修改
    currentMode: 'view', // 只支持查看模式
    currentDocument: '介绍文档', // 当前文档名称
    documents: LOCAL_DOCUMENTS, // 使用本地文档
    isLoading: false
};

// API 配置
const API_CONFIG = {
    baseURL: 'https://mindscribe-backend-nr7q.onrender.com', // 生产环境地址
    endpoints: {
        chat: '/api/chat',
        documents: '/api/documents',
        updateLog: '/api/get-update-log'
    },
    // 静态文件直接从 GitHub 加载
    staticFiles: {
        systemPrompt: 'https://raw.githubusercontent.com/Liu-design-beep/mindscribe-app/main/app/web/system_prompt.md'
    }
};

// DOM 元素
const elements = {
    backToNormalBtn: document.getElementById('back-to-normal-btn'),
    editModeStatus: document.getElementById('edit-mode-status'),
    chatModeContent: document.getElementById('chat-mode-content'),
    chatArea: document.getElementById('chat-area'),
    chapterList: document.getElementById('dev-chapter-list'),
    userInput: document.getElementById('user-input'),
    sendBtn: document.getElementById('send-btn'),
    documentsList: document.getElementById('documents-list'),
    viewAllBtn: document.getElementById('view-all-btn'),
    refreshBtn: document.getElementById('refresh-btn'),
    viewDocumentModal: document.getElementById('document-modal'),
    modalDocumentToc: document.getElementById('modal-document-toc'),
    tocList: document.getElementById('toc-list'),
    modalTitle: document.getElementById('modal-title'),
    modalContent: document.getElementById('modal-document-content'),
    closeModalBtn: document.getElementById('close-modal-btn'),
    documentModal: document.getElementById('document-modal'),  // 兼容旧代码
    devDocList: document.getElementById('dev-doc-list'),  // 左侧文档列表
    chapterList: document.getElementById('dev-chapter-list')  // 右侧章节列表
};

// 初始化
function init() {
    // 绑定事件
    bindEvents();
    
    // 初始化当前文档显示（默认为介绍文档）
    AppState.currentDocument = '介绍文档';
    
    // 更新左侧文档列表
    updateDocumentList();
    
    // 直接加载本地文档内容（不需要API调用）
    loadLocalDocuments();
    // 初始化时先显示已有的文档列表（介绍文档）
    updateDocumentList();
}

// 生成会话ID
function generateSessionId() {
    return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

// 绑定事件
function bindEvents() {
    // 返回正常界面
    if (elements.backToNormalBtn) {
        elements.backToNormalBtn.addEventListener('click', () => {
            window.location.href = 'index.html';
        });
    }
    
    // 开发者模式不需要对话功能，隐藏输入框和发送按钮
    if (elements.sendBtn) {
        elements.sendBtn.style.display = 'none';
    }
    if (elements.userInput) {
        elements.userInput.style.display = 'none';
    }
    
    // 查看所有笔记
    if (elements.viewAllBtn) {
        elements.viewAllBtn.addEventListener('click', viewAllDocuments);
    } else {
        console.error('[开发者模式] 查看所有笔记按钮元素不存在');
    }
    
    if (elements.refreshBtn) {
        elements.refreshBtn.addEventListener('click', viewAllDocuments);
    } else {
        console.error('[开发者模式] 刷新按钮元素不存在');
    }
    
    // 关闭弹窗
    if (elements.closeModalBtn) {
        elements.closeModalBtn.addEventListener('click', closeModal);
    } else {
        console.error('[开发者模式] 关闭弹窗按钮元素不存在');
    }
    
    if (elements.viewDocumentModal) {
        elements.viewDocumentModal.addEventListener('click', (e) => {
            if (e.target === elements.viewDocumentModal) {
                closeModal();
            }
        });
    } else {
        console.error('[开发者模式] 查看文档模态框元素不存在');
    }
}

// 切换模式（已废弃，改为弹窗显示）
// 现在"完整查看"按钮会弹出模态框显示当前文档
function switchMode(mode) {
    AppState.currentMode = mode;
    
    if (mode === 'chat') {
        elements.chatModeBtn.classList.add('active');
        elements.viewModeBtn.classList.remove('active');
        elements.chatModeContent.classList.remove('hidden');
        elements.viewModeContent.classList.add('hidden');
    } else {
        // 点击"完整查看"时，弹出模态框显示当前文档
        showViewDocumentModal();
        // 保持对话模式状态
        elements.chatModeBtn.classList.add('active');
        elements.viewModeBtn.classList.remove('active');
        elements.chatModeContent.classList.remove('hidden');
        elements.viewModeContent.classList.add('hidden');
    }
}

// 加载本地文档内容（不需要API调用）
function loadLocalDocuments() {
    console.log('[开发者模式] 加载本地文档内容...');
    
    // 更新状态
    AppState.devModeEnabled = true;
    AppState.editModeEnabled = false; // 开发者模式不允许修改
    updateStatus();
    
    // 加载更新记录日志和系统提示词（从API获取，只读，不需要D1）
    Promise.all([
        loadUpdateLogFromFile(),
        loadSystemPromptFromFile()
    ]).then(() => {
        // 更新文档列表（确保所有文档显示在列表中）
        updateDocumentList();
        // 直接显示介绍文档的完整内容（首次加载，清空之前的消息）
        displayCurrentDocument(true);
    });
}

// 从文件加载更新记录日志
async function loadUpdateLogFromFile() {
    try {
        // 尝试从后端API获取更新记录日志内容（只读，不需要D1）
        const response = await fetch(API_CONFIG.baseURL + API_CONFIG.endpoints.updateLog);
        if (response.ok) {
            const data = await response.json();
            if (data.content && Array.isArray(data.content)) {
                LOCAL_DOCUMENTS['更新记录日志'] = data.content;
                AppState.documents['更新记录日志'] = data.content;
                console.log('[开发者模式] 更新记录日志已加载，行数:', data.content.length);
                // 立即更新文档列表，确保"更新记录日志"显示在左侧列表中
                updateDocumentList();
            }
        } else {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
    } catch (error) {
        console.warn('[开发者模式] 无法从API加载更新记录日志，使用空内容:', error);
        // 如果API不可用，使用空数组
        LOCAL_DOCUMENTS['更新记录日志'] = ['更新记录日志内容暂不可用，请检查后端服务是否运行'];
        AppState.documents['更新记录日志'] = LOCAL_DOCUMENTS['更新记录日志'];
        // 即使加载失败，也要更新文档列表，确保"更新记录日志"显示在列表中
        updateDocumentList();
    }
}

// 从文件加载系统提示词
async function loadSystemPromptFromFile() {
    try {
        // 直接从 GitHub Raw URL 获取 system_prompt.md 文件
        const response = await fetch(API_CONFIG.staticFiles.systemPrompt);
        if (response.ok) {
            const text = await response.text();
            // 将 Markdown 文本按行分割
            const lines = text.split('\n');
            LOCAL_DOCUMENTS['系统提示词'] = lines;
            AppState.documents['系统提示词'] = lines;
            console.log('[开发者模式] 系统提示词已加载，行数:', lines.length);
            // 立即更新文档列表
            updateDocumentList();
        } else {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
    } catch (error) {
        console.warn('[开发者模式] 无法从 API 加载系统提示词，使用空内容:', error);
        // 如果 API 不可用，使用空数组
        LOCAL_DOCUMENTS['系统提示词'] = ['系统提示词内容暂不可用，请检查后端服务是否运行'];
        AppState.documents['系统提示词'] = LOCAL_DOCUMENTS['系统提示词'];
        // 即使加载失败，也要更新文档列表
        updateDocumentList();
    }
}

// 显示当前文档的完整内容（无参数版本，用于loadLocalDocuments）
// clearPrevious: 是否清空之前的消息（首次加载时为true，切换文档时为false）
function displayCurrentDocument(clearPrevious = false) {
    const currentDoc = AppState.currentDocument || '介绍文档';
    const docContent = AppState.documents[currentDoc];
    
    // 只有在首次加载时才清空聊天区域
    if (clearPrevious && elements.chatArea) {
        elements.chatArea.innerHTML = '';
    }
    
    if (docContent && Array.isArray(docContent) && docContent.length > 0) {
        const content = docContent.join('\n');
        // 解析文档内容，提取章节并生成带锚点的HTML
        const { htmlContent, chapters } = parseDocumentChapters(content, currentDoc);
        
        // 显示文档内容（使用HTML格式）
        const messageDiv = document.createElement('div');
        messageDiv.className = 'chat-bubble ai';
        messageDiv.innerHTML = `<strong>📄 ${currentDoc}</strong><div class="document-content-html" style="margin-top: 10px; white-space: pre-wrap; word-wrap: break-word; font-family: 'Courier New', monospace; font-size: 14px; line-height: 1.8; color: #5a3a3a;">${htmlContent}</div>`;
        if (elements.chatArea) {
            elements.chatArea.appendChild(messageDiv);
            // 滚动到底部
            elements.chatArea.scrollTop = elements.chatArea.scrollHeight;
        }
        
        // 生成章节列表
        generateChapterList(chapters);
        
        // 添加滚动监听，自动高亮当前章节
        if (elements.chatArea) {
            // 移除旧的监听器（如果存在）
            elements.chatArea.removeEventListener('scroll', handleChapterScroll);
            elements.chatArea.addEventListener('scroll', handleChapterScroll);
        }
    } else {
        addMessage('ai', `⚠️ 文档 "${currentDoc}" 内容为空`);
        // 清空章节列表
        if (elements.chapterList) {
            elements.chapterList.innerHTML = '';
        }
    }
}

// 切换文档
function switchDocument(docName) {
    if (!LOCAL_DOCUMENTS[docName] || (Array.isArray(LOCAL_DOCUMENTS[docName]) && LOCAL_DOCUMENTS[docName].length === 0)) {
        console.warn('[开发者模式] 文档不存在或为空:', docName);
        return;
    }
    
    AppState.currentDocument = docName;
    // 更新文档列表的高亮状态
    updateDocumentList();
    
    // 显示新文档的完整内容，不清空之前的消息（把旧的往下顶）
    displayCurrentDocument(false);
}

// 获取本地文档列表（不需要API调用）
function getLocalDocumentList() {
    return Object.keys(LOCAL_DOCUMENTS).filter(key => {
        const content = LOCAL_DOCUMENTS[key];
        return content && Array.isArray(content) && content.length > 0;
    });
}

// 显示三个重要的介绍文档内容
async function displayImportantDocuments(documents) {
    try {
        AppState.documents = documents;
        
        // 更新当前文档显示为介绍文档
        updateActiveDocTitle('介绍文档');
        AppState.currentDocument = '介绍文档';
        
        // 1. 显示介绍文档的完整内容
        const introDoc = documents['介绍文档'];
        if (introDoc) {
            const introContent = Array.isArray(introDoc) ? introDoc.join('\n') : introDoc;
            addMessage('ai', `📄 **介绍文档**\n\n${introContent}`);
        } else {
            addMessage('ai', '⚠️ 未找到介绍文档');
        }
        
        // 2. 显示更新记录日志的完整内容
        const updateLog = documents['更新记录日志'];
        if (updateLog) {
            const updateContent = Array.isArray(updateLog) ? updateLog.join('\n') : updateLog;
            addMessage('ai', `📋 **更新记录日志**\n\n${updateContent}`);
        } else {
            addMessage('ai', '⚠️ 未找到更新记录日志');
        }
        
        // 3. 显示技术架构说明（从介绍文档中提取，或单独显示）
        // 如果介绍文档中包含技术架构部分，已经显示过了
        // 这里可以显示一个总结性的技术说明
        const techSummary = `🏗️ **技术架构总结**\n\n` +
            `• 前端：原生 JS + CSS，双模式（试用/开发），弹窗查看全文\n` +
            `• 后端：Python FastAPI；会话管理 + 文档管理\n` +
            `• 存储：Cloudflare D1（dev 文档/试用文档分表；session_id 作用于试用表）\n` +
            `• 边缘：Cloudflare Workers（静态与接口代理）；KV 作为回退/缓存\n` +
            `• 模型：通义千问 3 - coder - plus（针对代码与长文本处理优化）`;
        addMessage('ai', techSummary);
        
    } catch (error) {
        console.error('显示重要文档失败:', error);
        addMessage('ai', '⚠️ 无法显示文档内容，请稍后重试');
    }
}

// 已废弃：loadIntroDocument函数不再需要，使用loadLocalDocuments代替

// 提取更新记录日志中最新的三个重要更新
function extractLatestUpdates(updateContent) {
    try {
        const lines = updateContent.split('\n');
        const updates = [];
        let currentUpdate = null;
        let currentSection = '';
        let inUpdate = false;
        
        for (let i = 0; i < lines.length; i++) {
            const line = lines[i].trim();
            
            // 检测更新日期标题（格式：## 📅 日期 - 版本）
            if (line.match(/^##\s*📅\s*\d{4}年\d{1,2}月\d{1,2}日/)) {
                // 如果已经有更新，保存它
                if (currentUpdate && inUpdate) {
                    updates.push(currentUpdate);
                }
                // 开始新的更新
                currentUpdate = {
                    date: line,
                    content: []
                };
                inUpdate = true;
                currentSection = '';
            }
            // 如果已经收集了三个更新，停止
            else if (updates.length >= 3 && currentUpdate && currentUpdate.content.length > 0) {
                break;
            }
            // 收集更新内容
            else if (inUpdate && currentUpdate) {
                // 检测新的章节（### 或 ####）
                if (line.startsWith('###') || line.startsWith('####')) {
                    if (currentSection) {
                        currentUpdate.content.push('');
                    }
                    currentSection = line;
                    currentUpdate.content.push(line);
                }
                // 收集内容行
                else if (line && !line.startsWith('---')) {
                    currentUpdate.content.push(line);
                }
            }
        }
        
        // 添加最后一个更新
        if (currentUpdate && inUpdate && currentUpdate.content.length > 0) {
            updates.push(currentUpdate);
        }
        
        // 如果找到了更新，格式化输出
        if (updates.length > 0) {
            let result = '';
            updates.forEach((update, index) => {
                result += `${update.date}\n\n`;
                result += update.content.join('\n');
                if (index < updates.length - 1) {
                    result += '\n\n---\n\n';
                }
            });
            return result;
        }
        
        return null;
    } catch (error) {
        console.error('提取更新内容失败:', error);
        return null;
    }
}

// 解析介绍文档，提取关键信息
function parseIntroDocument(introContent) {
    const content = Array.isArray(introContent) ? introContent : [introContent];
    const fullText = content.join('\n');
    const lines = fullText.split('\n');
    
    const keyInfo = {
        designConcept: '',
        coreFeatures: [],
        usageInstructions: [],
        notes: ''
    };
    
    let currentSection = '';
    let currentContent = [];
    
    for (let i = 0; i < lines.length; i++) {
        const line = lines[i].trim();
        
        // 检测章节标题
        if (line.startsWith('## ')) {
            // 保存上一章节的内容
            if (currentSection && currentContent.length > 0) {
                const content = currentContent.join(' ').trim();
                if (currentSection === '设计理念') {
                    keyInfo.designConcept = content;
                } else if (currentSection === '注意事项') {
                    keyInfo.notes = content;
                }
                currentContent = [];
            }
            
            // 提取章节名称
            const sectionMatch = line.match(/##\s*(.+)/);
            if (sectionMatch) {
                currentSection = sectionMatch[1].trim();
            }
        }
        // 检测核心功能列表
        else if (currentSection === '核心功能' && /^\d+\./.test(line)) {
            const feature = line.replace(/^\d+\.\s*/, '').trim();
            if (feature) {
                keyInfo.coreFeatures.push(feature);
            }
        }
        // 检测使用说明列表
        else if (currentSection === '使用说明' && line.startsWith('-')) {
            const instruction = line.replace(/^-\s*/, '').trim();
            if (instruction) {
                keyInfo.usageInstructions.push(instruction);
            }
        }
        // 收集其他内容
        else if (line && !line.startsWith('#') && !line.startsWith('---')) {
            currentContent.push(line);
        }
    }
    
    // 保存最后一个章节的内容
    if (currentSection && currentContent.length > 0) {
        const content = currentContent.join(' ').trim();
        if (currentSection === '设计理念') {
            keyInfo.designConcept = content;
        } else if (currentSection === '注意事项') {
            keyInfo.notes = content;
        }
    }
    
    // 如果提取到了任何信息，返回keyInfo，否则返回null
    if (keyInfo.designConcept || keyInfo.coreFeatures.length > 0 || keyInfo.usageInstructions.length > 0 || keyInfo.notes) {
        return keyInfo;
    }
    return null;
}

// 加载更新日志文档（保留此函数，可能以后会用到）
async function loadUpdateLog() {
    try {
        // 尝试通过完整查看模式获取所有文档，然后显示更新日志
        const allDocsResponse = await sendMessage('查看所有笔记', 'view');
        if (allDocsResponse.response_type === 'ALL_DOCUMENTS' && allDocsResponse.documents) {
            AppState.documents = allDocsResponse.documents;
            const updateLogDoc = allDocsResponse.documents['更新记录日志'];
            if (updateLogDoc) {
                // 解析更新日志，提取最新的三个更新
                const latestUpdates = parseLatestUpdates(updateLogDoc);
                
                // 更新当前文档显示
                updateActiveDocTitle('更新记录日志');
                AppState.currentDocument = '更新记录日志';
                
                // 显示最新的三个更新
                if (latestUpdates.length > 0) {
                    let updateMessage = '📋 **最新更新记录**\n\n';
                    latestUpdates.forEach((update, index) => {
                        updateMessage += `### ${index + 1}. ${update.title}\n`;
                        updateMessage += `📅 ${update.date}\n\n`;
                        updateMessage += `${update.content}\n\n`;
                        updateMessage += '---\n\n';
                    });
                    addMessage('ai', updateMessage);
                } else {
                    // 如果没有找到更新，显示完整内容
                    const updateContent = Array.isArray(updateLogDoc) ? updateLogDoc.join('\n') : updateLogDoc;
                    addMessage('ai', `📄 更新记录日志：\n\n${updateContent}`);
                }
            } else {
                addMessage('ai', '⚠️ 未找到更新记录日志');
            }
        }
    } catch (error) {
        console.error('加载更新日志失败:', error);
        addMessage('ai', '⚠️ 无法加载更新记录日志，请稍后重试');
    }
}

// 解析更新日志，提取最新的三个更新
function parseLatestUpdates(updateLogContent) {
    const updates = [];
    const content = Array.isArray(updateLogContent) ? updateLogContent : [updateLogContent];
    const fullText = content.join('\n');
    
    let currentDate = '';
    let currentTitle = '';
    let currentContent = [];
    let inUpdateSection = false;
    
    const lines = fullText.split('\n');
    
    for (let i = 0; i < lines.length; i++) {
        const line = lines[i].trim();
        
        // 检测日期标题
        const dateMatch = line.match(/##\s*📅\s*(\d{4}年\d{1,2}月\d{1,2}日)/);
        if (dateMatch) {
            // 保存上一个更新项
            if (currentDate && currentTitle && currentContent.length > 0) {
                updates.push({
                    date: currentDate,
                    title: currentTitle,
                    content: currentContent.join('\n').substring(0, 200) + '...'
                });
            }
            currentDate = dateMatch[1];
            currentTitle = '';
            currentContent = [];
            inUpdateSection = true;
        }
        // 检测更新标题
        else if (line.startsWith('####') && inUpdateSection) {
            // 如果已经有标题，保存当前更新项
            if (currentTitle && currentContent.length > 0) {
                updates.push({
                    date: currentDate,
                    title: currentTitle,
                    content: currentContent.join('\n').substring(0, 200) + '...'
                });
                currentContent = [];
            }
            // 提取标题（移除####和表情符号）
            currentTitle = line.replace(/^####\s*[^\s]+\s*/, '').trim();
        }
        // 收集内容
        else if (inUpdateSection && line && !line.startsWith('---') && !line.startsWith('**') && line.length > 10) {
            currentContent.push(line);
        }
    }
    
    // 保存最后一个更新项
    if (currentDate && currentTitle && currentContent.length > 0) {
        updates.push({
            date: currentDate,
            title: currentTitle,
            content: currentContent.join('\n').substring(0, 200) + '...'
        });
    }
    
    // 返回最新的三个更新（倒序）
    return updates.slice(-3).reverse();
}

// 更新状态显示
function updateStatus() {
    elements.editModeStatus.textContent = `修改权限: ${AppState.editModeEnabled ? '已启用' : '未启用'}`;
}

// 发送消息
async function handleSendMessage() {
    const text = elements.userInput.value.trim();
    if (!text || AppState.isLoading) return;
    
    // 清空输入
    elements.userInput.value = '';
    
    // 显示用户消息
    addMessage('user', text);
    
    // 检查是否是 set000
    if (text === 'set000') {
        try {
            AppState.isLoading = true;
            elements.sendBtn.disabled = true;
            const response = await sendMessage(text);
            if (response.edit_mode_enabled) {
                AppState.editModeEnabled = true;
                updateStatus();
            }
            addMessage('ai', response.content);
        } catch (error) {
            addMessage('ai', `错误: ${error.message}`);
        } finally {
            AppState.isLoading = false;
            elements.sendBtn.disabled = false;
        }
        return;
    }
    
    // 发送到后端
    try {
        AppState.isLoading = true;
        elements.sendBtn.disabled = true;
        const response = await sendMessage(text);
        
        // 更新状态
        if (response.dev_mode_enabled !== undefined) {
            AppState.devModeEnabled = response.dev_mode_enabled;
        }
        if (response.edit_mode_enabled !== undefined) {
            AppState.editModeEnabled = response.edit_mode_enabled;
        }
        updateStatus();
        
        // 处理响应
        handleResponse(response);
    } catch (error) {
        addMessage('ai', `错误: ${error.message}`);
    } finally {
        AppState.isLoading = false;
        elements.sendBtn.disabled = false;
    }
}

// 发送消息到后端
async function sendMessage(text, mode = 'chat') {
    const url = API_CONFIG.baseURL + API_CONFIG.endpoints.chat;
    console.log('[API请求]', { url, text, mode, session_id: AppState.sessionId });
    
    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            session_id: AppState.sessionId,
            text: text,
            mode: mode,
            dev_mode_code: '开发者模式#000' // 确保开发者模式已启用
        })
    });
    
    if (!response.ok) {
        const errorText = await response.text();
        console.error(`[API错误] HTTP ${response.status}:`, errorText);
        throw new Error(`HTTP error! status: ${response.status}, message: ${errorText.substring(0, 200)}`);
    }
    
    const responseData = await response.json();
    console.log('[API响应]', {
        response_type: responseData.response_type,
        has_documents: !!responseData.documents,
        document_count: responseData.documents ? Object.keys(responseData.documents).length : 0,
        document_keys: responseData.documents ? Object.keys(responseData.documents) : []
    });
    return responseData;
}

// 处理响应
function handleResponse(response) {
    if (response.response_type === 'ALL_DOCUMENTS') {
        // 完整查看模式
        AppState.documents = response.documents || {};
        // 如果当前是完整查看模式，显示当前文档
        if (AppState.currentMode === 'view') {
            viewCurrentDocument();
        } else {
            displayAllDocuments();
            addMessage('ai', '已加载所有笔记内容');
        }
    } else if (response.response_type === 'EDIT_MODE_REQUIRED') {
        addMessage('ai', response.content);
    } else if (response.response_type === 'DEV_MODE_REQUIRED') {
        addMessage('ai', response.content);
    } else {
        addMessage('ai', response.content);
        
        // 如果响应中包含当前文档信息，更新显示（但开发者模式下不能是"试用文档"）
        if (response.current_document) {
            // 开发者模式下，如果返回的是"试用文档"，则使用"介绍文档"
            const docTitle = response.current_document === '试用文档' ? '介绍文档' : response.current_document;
            // 确保不会设置为"试用文档"
            if (docTitle !== '试用文档') {
                AppState.currentDocument = docTitle;
                updateActiveDocTitle(docTitle);
            }
        }
    }
}

// 添加消息到聊天区域
function addMessage(sender, content) {
    const bubble = document.createElement('div');
    bubble.className = `chat-bubble ${sender}`;
    
    // 简单的 Markdown 支持：将 **文本** 转换为 <strong>文本</strong>
    const processedContent = content.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // 如果是多行内容，保持换行格式
    if (processedContent.includes('\n')) {
        const lines = processedContent.split('\n');
        lines.forEach((line, index) => {
            if (line.trim() || index === 0) {
                const lineEl = document.createElement('div');
                lineEl.innerHTML = line || ' '; // 空行也显示，使用 innerHTML 支持 HTML
                bubble.appendChild(lineEl);
            }
        });
    } else {
        bubble.innerHTML = processedContent;
    }
    
    elements.chatArea.appendChild(bubble);
    elements.chatArea.scrollTop = elements.chatArea.scrollHeight;
}

// 更新左侧文档列表
function updateDocumentList() {
    if (!elements.devDocList) {
        console.error('[开发者模式] 文档列表元素不存在');
        return;
    }
    
    // 清空现有列表
    elements.devDocList.innerHTML = '';
    
    // 获取文档列表
    const documentList = getLocalDocumentList();
    console.log('[开发者模式] 更新文档列表:', documentList);
    
    // 为每个文档创建列表项
    documentList.forEach(docTitle => {
        const listItem = document.createElement('li');
        listItem.className = 'dev-doc-list-item';
        
        // 如果是当前文档，添加 active 类
        if (docTitle === AppState.currentDocument) {
            listItem.classList.add('active');
        }
        
        listItem.textContent = docTitle;
        
        // 添加点击事件
        listItem.addEventListener('click', () => {
            console.log('[开发者模式] 点击文档:', docTitle);
            switchDocument(docTitle);
        });
        
        elements.devDocList.appendChild(listItem);
    });
}

// 更新当前文档标题显示
function updateActiveDocTitle(title) {
    // 开发者模式下，确保不会设置为"试用文档"或其他不存在的文档
    // 开发者模式只有"介绍文档"和"更新记录日志"，不存在"默认文档"或"试用文档"
    if (title === '试用文档' || title === '默认文档' || !title) {
        title = '介绍文档';
    }
    
    // 确保标题是有效的开发者模式文档
    const validDevDocs = ['介绍文档', '更新记录日志', 'RAG架构设计文档', '用户数据埋点与数据飞轮设计'];
    if (!validDevDocs.includes(title)) {
        console.warn(`[开发者模式] 无效的文档名称: ${title}，强制设置为"介绍文档"`);
        title = '介绍文档';
    }
    
    AppState.currentDocument = title;
    // 更新文档列表的高亮状态
    updateDocumentList();
    console.log(`[开发者模式] 当前文档已更新为: ${title}`);
}

// 加载文档列表
async function loadDocumentList() {
    try {
        const url = API_CONFIG.baseURL + API_CONFIG.endpoints.documents;
        const response = await fetch(url + `?session_id=${AppState.sessionId}&doc_type=dev&is_trial=false`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            console.log('[开发者模式] 文档列表API响应:', data);
            
            // 开发者模式：始终显示"介绍文档"，不存在其他默认文档
            // 如果文档列表中有"介绍文档"，使用它；否则强制设置为"介绍文档"
            if (data.documents && data.documents.length > 0) {
                const introDoc = data.documents.find(doc => doc === '介绍文档');
                if (introDoc) {
                    console.log('[开发者模式] 找到介绍文档，设置为当前文档');
                    AppState.currentDocument = '介绍文档';
                    updateActiveDocTitle('介绍文档');
                } else {
                    // 如果文档列表中没有"介绍文档"，强制设置为"介绍文档"
                    console.warn('[开发者模式] 文档列表中没有"介绍文档"，强制设置为"介绍文档"');
                    AppState.currentDocument = '介绍文档';
                    updateActiveDocTitle('介绍文档');
                }
            } else {
                // 如果没有文档，确保显示介绍文档
                console.log('[开发者模式] 文档列表为空，设置为介绍文档');
                AppState.currentDocument = '介绍文档';
                updateActiveDocTitle('介绍文档');
            }
        } else {
            console.warn('[开发者模式] API请求失败，设置为介绍文档');
            AppState.currentDocument = '介绍文档';
            updateActiveDocTitle('介绍文档');
        }
    } catch (error) {
        console.error('[开发者模式] 加载文档列表失败:', error);
        // 即使加载失败，也确保显示介绍文档
        AppState.currentDocument = '介绍文档';
        updateActiveDocTitle('介绍文档');
    }
}

// 显示文档选择器（弹窗）
function showDocumentSelector() {
    console.log('[开发者模式] 显示文档选择器');
    // 创建一个简单的文档选择弹窗
    const modal = document.createElement('div');
    modal.className = 'modal-overlay show';
    modal.style.display = 'flex';
    modal.style.zIndex = '2000'; // 确保在最上层
    
    const content = document.createElement('div');
    content.className = 'modal-content';
    
    const header = document.createElement('div');
    header.className = 'modal-header';
    header.innerHTML = '<h2>选择文档</h2><button class="close-btn" id="close-selector-btn">×</button>';
    
    const body = document.createElement('div');
    body.className = 'modal-body';
    body.style.maxHeight = '400px';
    body.style.overflowY = 'auto';
    
    // 直接从本地文档列表获取
    const documentList = getLocalDocumentList();
    console.log('[开发者模式] 本地文档列表:', documentList);
    
    if (documentList.length === 0) {
        body.innerHTML = '<div style="padding: 20px; text-align: center; color: #8b5a5a;">暂无可用文档</div>';
    } else {
        documentList.forEach(docTitle => {
            const item = document.createElement('div');
            item.className = 'document-item';
            item.style.cursor = 'pointer';
            item.style.padding = '15px';
            item.style.marginBottom = '10px';
            item.style.borderRadius = '8px';
            item.style.border = '1px solid #f5d5d5';
            item.style.background = docTitle === AppState.currentDocument 
                ? 'rgba(245, 213, 213, 0.5)' 
                : 'rgba(255, 255, 255, 0.7)';
            item.textContent = docTitle;
            
            item.addEventListener('click', () => {
                console.log('[开发者模式] 选择文档:', docTitle);
                switchDocument(docTitle);
                modal.remove();
            });
            body.appendChild(item);
        });
    }
    
    content.appendChild(header);
    content.appendChild(body);
    modal.appendChild(content);
    document.body.appendChild(modal);
    
    // 关闭按钮事件
    header.querySelector('#close-selector-btn').addEventListener('click', () => {
        modal.remove();
    });
    
    // 点击遮罩关闭
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.remove();
        }
    });
}

// 显示查看文档弹窗（完整查看当前文档）
function showViewDocumentModal() {
    if (!elements.viewDocumentModal || !elements.modalTitle || !elements.modalContent) {
        console.error('[开发者模式] 查看文档模态框元素不存在');
        return;
    }
    
    const currentDoc = AppState.currentDocument || '介绍文档';
    elements.modalTitle.textContent = currentDoc;
    
    // 直接从本地文档获取内容
    const docContent = AppState.documents[currentDoc];
    
    if (docContent && Array.isArray(docContent) && docContent.length > 0) {
        const content = docContent.join('\n');
        // 解析并显示文档内容（带锚点）
        const { htmlContent, tocItems } = parseDocumentContent(content, currentDoc);
        elements.modalContent.innerHTML = htmlContent;
        
        // 生成目录
        generateTOC(tocItems);
        
        console.log('[开发者模式] 显示文档内容，长度:', content.length);
    } else {
        console.warn('[开发者模式] 文档不存在或为空:', currentDoc);
        elements.modalContent.textContent = `文档 "${currentDoc}" 不存在或为空。`;
        // 清空目录
        if (elements.tocList) {
            elements.tocList.innerHTML = '';
        }
    }
    
    // 显示弹窗
    elements.viewDocumentModal.classList.add('show');
    elements.viewDocumentModal.style.display = 'flex';
    
    // 添加滚动监听，自动高亮当前章节
    if (elements.modalContent) {
        elements.modalContent.addEventListener('scroll', handleTOCScroll);
    }
}

// 处理目录滚动，自动高亮当前章节
function handleTOCScroll() {
    if (!elements.modalContent || !elements.tocList) {
        return;
    }
    
    const anchors = elements.modalContent.querySelectorAll('.toc-anchor');
    const scrollTop = elements.modalContent.scrollTop;
    const offset = 100; // 偏移量
    
    let currentAnchor = null;
    
    for (let i = anchors.length - 1; i >= 0; i--) {
        const anchor = anchors[i];
        const rect = anchor.getBoundingClientRect();
        const containerRect = elements.modalContent.getBoundingClientRect();
        const relativeTop = rect.top - containerRect.top;
        
        if (relativeTop <= offset) {
            currentAnchor = anchor.id;
            break;
        }
    }
    
    // 更新目录高亮
    if (currentAnchor) {
        document.querySelectorAll('.toc-item').forEach(el => {
            el.classList.remove('active');
            if (el.getAttribute('data-anchor') === currentAnchor) {
                el.classList.add('active');
                // 确保活动项可见
                el.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }
        });
    }
}

// 解析文档内容，提取标题并生成带锚点的HTML
function parseDocumentContent(content, docTitle) {
    const lines = content.split('\n');
    const tocItems = [];
    let htmlContent = '';
    let anchorIndex = 0;
    
    for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        const trimmedLine = line.trim();
        
        // 匹配 Markdown 标题：## 或 ### 或 ####（允许前面有空格）
        const h2Match = trimmedLine.match(/^##\s+(.+)$/);
        const h3Match = trimmedLine.match(/^###\s+(.+)$/);
        const h4Match = trimmedLine.match(/^####\s+(.+)$/);
        
        if (h2Match) {
            const title = h2Match[1].trim();
            const anchor = `toc-${anchorIndex++}`;
            tocItems.push({ level: 1, title, anchor });
            htmlContent += `<h2 class="toc-anchor" id="${anchor}" style="margin-top: 20px; margin-bottom: 10px; color: #8b5a5a; font-size: 18px; font-weight: 600;">${escapeHtml(line)}</h2>\n`;
        } else if (h3Match) {
            const title = h3Match[1].trim();
            const anchor = `toc-${anchorIndex++}`;
            tocItems.push({ level: 2, title, anchor });
            htmlContent += `<h3 class="toc-anchor" id="${anchor}" style="margin-top: 15px; margin-bottom: 8px; color: #8b5a5a; font-size: 16px; font-weight: 600;">${escapeHtml(line)}</h3>\n`;
        } else if (h4Match) {
            const title = h4Match[1].trim();
            const anchor = `toc-${anchorIndex++}`;
            tocItems.push({ level: 3, title, anchor });
            htmlContent += `<h4 class="toc-anchor" id="${anchor}" style="margin-top: 12px; margin-bottom: 6px; color: #8b5a5a; font-size: 14px; font-weight: 600;">${escapeHtml(line)}</h4>\n`;
        } else {
            // 普通文本，保持原样
            if (trimmedLine === '') {
                htmlContent += '<br>\n';
            } else {
                htmlContent += escapeHtml(line) + '\n';
            }
        }
    }
    
    return { htmlContent, tocItems };
}

// 生成目录
function generateTOC(tocItems) {
    if (!elements.tocList) {
        console.warn('[开发者模式] 目录列表元素不存在');
        return;
    }
    
    elements.tocList.innerHTML = '';
    
    if (tocItems.length === 0) {
        elements.tocList.innerHTML = '<div style="color: #8b5a5a; font-size: 12px; padding: 10px;">暂无目录</div>';
        return;
    }
    
    tocItems.forEach(item => {
        const tocItem = document.createElement('div');
        tocItem.className = `toc-item level-${item.level}`;
        tocItem.textContent = item.title;
        tocItem.setAttribute('data-anchor', item.anchor);
        
        tocItem.addEventListener('click', () => {
            scrollToAnchor(item.anchor);
            // 更新活动状态
            document.querySelectorAll('.toc-item').forEach(el => el.classList.remove('active'));
            tocItem.classList.add('active');
        });
        
        elements.tocList.appendChild(tocItem);
    });
}

// 滚动到指定锚点
function scrollToAnchor(anchorId) {
    const anchor = document.getElementById(anchorId);
    if (anchor) {
        anchor.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

// HTML转义
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// 解析文档内容，提取章节（## 标题）- 用于主界面章节列表
function parseDocumentChapters(content, docTitle) {
    const lines = content.split('\n');
    const chapters = [];
    let htmlContent = '';
    let anchorIndex = 0;
    
    for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        const trimmedLine = line.trim();
        
        // 匹配 Markdown 二级标题（##）
        const h2Match = trimmedLine.match(/^##\s+(.+)$/);
        
        if (h2Match) {
            const title = h2Match[1].trim();
            const anchor = `chapter-${anchorIndex++}`;
            chapters.push({ title, anchor });
            htmlContent += `<h2 class="chapter-anchor" id="${anchor}" style="margin-top: 20px; margin-bottom: 10px; color: #8b5a5a; font-size: 18px; font-weight: 600; border-bottom: 2px solid #f5d5d5; padding-bottom: 5px;">${escapeHtml(line)}</h2>\n`;
        } else {
            // 普通文本，保持原样
            if (trimmedLine === '') {
                htmlContent += '<br>\n';
            } else {
                htmlContent += escapeHtml(line) + '\n';
            }
        }
    }
    
    return { htmlContent, chapters };
}

// 生成章节列表（用于主界面右侧）
function generateChapterList(chapters) {
    if (!elements.chapterList) {
        console.warn('[开发者模式] 章节列表元素不存在');
        return;
    }
    
    elements.chapterList.innerHTML = '';
    
    if (chapters.length === 0) {
        elements.chapterList.innerHTML = '<div style="color: #8b5a5a; font-size: 12px; padding: 10px;">暂无章节</div>';
        return;
    }
    
    chapters.forEach(chapter => {
        const chapterItem = document.createElement('div');
        chapterItem.className = 'dev-chapter-item';
        chapterItem.textContent = chapter.title;
        chapterItem.setAttribute('data-anchor', chapter.anchor);
        
        chapterItem.addEventListener('click', () => {
            scrollToChapter(chapter.anchor);
            // 更新活动状态
            document.querySelectorAll('.dev-chapter-item').forEach(el => el.classList.remove('active'));
            chapterItem.classList.add('active');
        });
        
        elements.chapterList.appendChild(chapterItem);
    });
}

// 滚动到指定章节
function scrollToChapter(anchorId) {
    const anchor = document.getElementById(anchorId);
    if (anchor && elements.chatArea) {
        // 计算锚点相对于chat-area的位置
        const chatAreaRect = elements.chatArea.getBoundingClientRect();
        const anchorRect = anchor.getBoundingClientRect();
        const scrollTop = elements.chatArea.scrollTop;
        const targetScrollTop = scrollTop + anchorRect.top - chatAreaRect.top - 20; // 20px偏移
        
        elements.chatArea.scrollTo({
            top: targetScrollTop,
            behavior: 'smooth'
        });
    }
}

// 处理章节滚动，自动高亮当前章节
function handleChapterScroll() {
    if (!elements.chatArea || !elements.chapterList) {
        return;
    }
    
    const anchors = elements.chatArea.querySelectorAll('.chapter-anchor');
    const scrollTop = elements.chatArea.scrollTop;
    const offset = 100; // 偏移量
    
    let currentAnchor = null;
    
    for (let i = anchors.length - 1; i >= 0; i--) {
        const anchor = anchors[i];
        const chatAreaRect = elements.chatArea.getBoundingClientRect();
        const anchorRect = anchor.getBoundingClientRect();
        const relativeTop = anchorRect.top - chatAreaRect.top;
        
        if (relativeTop <= offset) {
            currentAnchor = anchor.id;
            break;
        }
    }
    
    // 更新章节高亮
    if (currentAnchor) {
        document.querySelectorAll('.dev-chapter-item').forEach(el => {
            el.classList.remove('active');
            if (el.getAttribute('data-anchor') === currentAnchor) {
                el.classList.add('active');
                // 确保活动项可见
                el.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }
        });
    }
}

// 查看当前文档的全部内容（保留此函数，供其他功能使用）
async function viewCurrentDocument() {
    try {
        // 确保当前文档不是"试用文档"
        let currentDocTitle = AppState.currentDocument || '介绍文档';
        if (currentDocTitle === '试用文档') {
            currentDocTitle = '介绍文档';
            AppState.currentDocument = '介绍文档';
            updateActiveDocTitle('介绍文档');
        }
        
        // 先获取所有文档，然后显示当前文档
        const response = await sendMessage('查看所有笔记', 'view');
        if (response.response_type === 'ALL_DOCUMENTS' && response.documents) {
            AppState.documents = response.documents;
            
            // 获取当前文档的内容
            let currentDocContent = response.documents[currentDocTitle];
            
            // 如果当前文档不存在，尝试使用"介绍文档"
            if (!currentDocContent && currentDocTitle !== '介绍文档') {
                currentDocContent = response.documents['介绍文档'];
                if (currentDocContent) {
                    currentDocTitle = '介绍文档';
                    AppState.currentDocument = '介绍文档';
                    updateActiveDocTitle('介绍文档');
                }
            }
            
            if (currentDocContent) {
                // 直接显示当前文档的全部内容（在文档列表中）
                displayDocumentInList(currentDocTitle, currentDocContent);
            } else {
                // 如果当前文档不存在，显示提示
                if (elements.documentsList) {
                    elements.documentsList.innerHTML = `<div class="document-item" style="padding: 20px; text-align: center; color: #8b5a5a;">未找到文档：${currentDocTitle}</div>`;
                }
            }
        } else {
            if (elements.documentsList) {
                elements.documentsList.innerHTML = `<div class="document-item" style="padding: 20px; text-align: center; color: #8b5a5a;">${response.content || '无法加载文档'}</div>`;
            }
        }
    } catch (error) {
        console.error('查看当前文档错误:', error);
        if (elements.documentsList) {
            elements.documentsList.innerHTML = `<div class="document-item" style="padding: 20px; text-align: center; color: #8b5a5a;">错误: ${error.message}</div>`;
        }
    }
}

// 显示当前文档的全部内容（在文档列表中，不是聊天区域）
function displayDocumentInList(title, content) {
    elements.documentsList.innerHTML = '';
    
    // 创建文档容器
    const docContainer = document.createElement('div');
    docContainer.className = 'document-full-view';
    docContainer.style.padding = '20px';
    docContainer.style.background = 'rgba(255, 255, 255, 0.6)';
    docContainer.style.borderRadius = '10px';
    docContainer.style.border = '1px solid rgba(245, 213, 213, 0.3)';
    docContainer.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.1)';
    docContainer.style.maxHeight = 'calc(100vh - 200px)';
    docContainer.style.overflowY = 'auto';
    
    // 文档标题
    const titleEl = document.createElement('h2');
    titleEl.textContent = title;
    titleEl.style.marginBottom = '15px';
    titleEl.style.color = '#8b5a5a';
    titleEl.style.fontSize = '18px';
    titleEl.style.fontWeight = '600';
    docContainer.appendChild(titleEl);
    
    // 文档内容
    const contentEl = document.createElement('div');
    contentEl.className = 'document-content-full';
    contentEl.style.whiteSpace = 'pre-wrap';
    contentEl.style.wordBreak = 'break-word';
    contentEl.style.lineHeight = '1.6';
    contentEl.style.color = '#5a3a3a';
    contentEl.style.fontSize = '14px';
    
    if (Array.isArray(content)) {
        contentEl.textContent = content.join('\n');
    } else {
        contentEl.textContent = content;
    }
    
    docContainer.appendChild(contentEl);
    elements.documentsList.appendChild(docContainer);
}

// 查看所有文档（保留此函数，供"查看所有笔记"按钮使用）
async function viewAllDocuments() {
    try {
        console.log('开始获取所有文档...');
        const response = await sendMessage('查看所有笔记', 'view');
        console.log('获取文档响应:', response);
        
        if (response.response_type === 'ALL_DOCUMENTS') {
            AppState.documents = response.documents || {};
            console.log('文档数据:', AppState.documents);
            console.log('文档数量:', Object.keys(AppState.documents).length);
            console.log('文档列表:', Object.keys(AppState.documents));
            
            // 确保至少显示介绍文档和更新记录日志
            if (Object.keys(AppState.documents).length === 0) {
                console.warn('文档列表为空，尝试从D1数据库加载...');
                // 如果文档列表为空，可能是D1数据库没有正确加载，尝试重新获取
                // 这里可以添加重试逻辑
            }
            
            displayAllDocuments();
        } else {
            // 使用控制台日志代替 alert
            console.error('查看所有文档失败:', response);
            if (elements.documentsList) {
                elements.documentsList.innerHTML = `<div class="document-item" style="padding: 20px; text-align: center; color: #8b5a5a;">${response.content || '无法加载文档'}</div>`;
            }
        }
    } catch (error) {
        // 使用控制台日志代替 alert
        console.error('查看所有文档错误:', error);
        if (elements.documentsList) {
            elements.documentsList.innerHTML = `<div class="document-item" style="padding: 20px; text-align: center; color: #8b5a5a;">错误: ${error.message}</div>`;
        }
    }
}

// 查看指定文档的完整内容（用于弹窗）
async function viewDocumentFullContent(docTitle) {
    try {
        // 先获取所有文档
        if (Object.keys(AppState.documents).length === 0) {
            const response = await sendMessage('查看所有笔记', 'view');
            if (response.response_type === 'ALL_DOCUMENTS') {
                AppState.documents = response.documents || {};
            }
        }
        
        // 获取指定文档的内容
        const docContent = AppState.documents[docTitle];
        if (docContent) {
            showDocumentModal(docTitle, docContent);
        } else {
            // 如果文档不在缓存中，尝试单独获取
            const response = await sendMessage(`查看${docTitle}`, 'chat');
            if (response.response_type === 'DOCUMENT' || response.response_type === 'TEXT') {
                const content = response.content || '';
                showDocumentModal(docTitle, content.split('\n'));
            } else {
                alert(`无法加载文档：${docTitle}`);
            }
        }
    } catch (error) {
        console.error('查看文档完整内容失败:', error);
        alert(`查看文档失败：${error.message}`);
    }
}

// 显示所有文档
function displayAllDocuments() {
    if (!elements.documentsList) {
        console.error('documentsList元素不存在！');
        return;
    }
    
    elements.documentsList.innerHTML = '';
    
    console.log('显示文档列表，文档数量:', Object.keys(AppState.documents).length);
    console.log('文档列表:', Object.keys(AppState.documents));
    
    if (Object.keys(AppState.documents).length === 0) {
        elements.documentsList.innerHTML = '<div class="document-item" style="padding: 20px; text-align: center; color: #8b5a5a;">暂无文档，请点击"刷新"按钮重新加载</div>';
        return;
    }
    
    // 按顺序显示文档：先显示介绍文档，然后是更新记录日志，最后是其他文档
    const sortedTitles = [];
    if (AppState.documents['介绍文档']) {
        sortedTitles.push('介绍文档');
    }
    if (AppState.documents['更新记录日志']) {
        sortedTitles.push('更新记录日志');
    }
    // 添加其他文档（排除已添加的）
    for (const title of Object.keys(AppState.documents)) {
        if (title !== '介绍文档' && title !== '更新记录日志') {
            sortedTitles.push(title);
        }
    }
    
    console.log('排序后的文档列表:', sortedTitles);
    
    for (const title of sortedTitles) {
        const content = AppState.documents[title];
        if (!content) {
            continue;
        }
        
        const item = document.createElement('div');
        item.className = 'document-item';
        item.style.cursor = 'pointer';
        item.style.marginBottom = '15px';
        item.style.padding = '15px';
        item.style.background = 'rgba(255, 255, 255, 0.6)';
        item.style.borderRadius = '8px';
        item.style.border = '1px solid rgba(245, 213, 213, 0.3)';
        item.style.transition = 'all 0.2s';
        
        // 悬停效果
        item.addEventListener('mouseenter', () => {
            item.style.background = 'rgba(255, 255, 255, 0.8)';
            item.style.transform = 'translateY(-2px)';
            item.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.15)';
        });
        item.addEventListener('mouseleave', () => {
            item.style.background = 'rgba(255, 255, 255, 0.6)';
            item.style.transform = 'translateY(0)';
            item.style.boxShadow = 'none';
        });
        
        const titleEl = document.createElement('div');
        titleEl.className = 'document-title';
        titleEl.textContent = title;
        titleEl.style.fontSize = '16px';
        titleEl.style.fontWeight = '600';
        titleEl.style.color = '#8b5a5a';
        titleEl.style.marginBottom = '10px';
        
        const preview = document.createElement('div');
        preview.className = 'document-preview';
        preview.style.color = '#5a3a3a';
        preview.style.fontSize = '13px';
        preview.style.lineHeight = '1.6';
        preview.style.maxHeight = '60px';
        preview.style.overflow = 'hidden';
        
        let previewText = '';
        if (Array.isArray(content)) {
            previewText = content.slice(0, 3).join('\n');
            if (content.length > 3) {
                previewText += '...';
            }
        } else if (typeof content === 'string') {
            previewText = content.substring(0, 100);
            if (content.length > 100) {
                previewText += '...';
            }
        } else {
            previewText = String(content).substring(0, 100);
        }
        preview.textContent = previewText || '(空文档)';
        
        const meta = document.createElement('div');
        meta.className = 'document-meta';
        meta.style.marginTop = '8px';
        meta.style.fontSize = '12px';
        meta.style.color = '#8b5a5a';
        const lineCount = Array.isArray(content) ? content.length : (typeof content === 'string' ? content.split('\n').length : 1);
        meta.textContent = `行数: ${lineCount} | 点击查看完整内容`;
        
        item.appendChild(titleEl);
        item.appendChild(preview);
        item.appendChild(meta);
        
        item.addEventListener('click', () => {
            console.log('点击查看文档:', title);
            showDocumentModal(title, content);
        });
        
        elements.documentsList.appendChild(item);
    }
    
    console.log('文档列表显示完成');
}

// 显示文档弹窗
function showDocumentModal(title, content) {
    elements.modalTitle.textContent = title;
    
    const contentEl = elements.modalContent;
    contentEl.innerHTML = '';
    
    // 处理内容，支持数组和字符串
    let contentArray = [];
    if (Array.isArray(content)) {
        contentArray = content;
    } else if (typeof content === 'string') {
        contentArray = content.split('\n');
    } else {
        contentArray = [String(content)];
    }
    
    // 创建可滚动的容器
    const scrollContainer = document.createElement('div');
    scrollContainer.style.cssText = 'max-height: 70vh; overflow-y: auto; padding: 10px;';
    
    contentArray.forEach((line, index) => {
        const lineEl = document.createElement('div');
        lineEl.className = 'line';
        lineEl.style.cssText = 'padding: 4px 0; line-height: 1.6; white-space: pre-wrap;';
        lineEl.textContent = line || ' '; // 空行显示为空格
        scrollContainer.appendChild(lineEl);
    });
    
    contentEl.appendChild(scrollContainer);
    elements.documentModal.classList.add('show');
}

// 关闭弹窗
function closeModal() {
    // 移除滚动监听
    if (elements.modalContent) {
        elements.modalContent.removeEventListener('scroll', handleTOCScroll);
    }
    if (elements.viewDocumentModal) {
        elements.viewDocumentModal.classList.remove('show');
        elements.viewDocumentModal.style.display = 'none';
    }
}

// 页面加载完成后初始化
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}

