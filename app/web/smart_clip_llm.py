# smart_clip_llm.py
# 灵辑 (Mindscribe) - AI 内容收藏助手 LLM增强版 (基于通义千问)
# 核心对话引擎 (Core Conversation Engine)

import os
from document_manager import DocumentManager
from intent_recognizer import LLMIntentRecognizer
from config import get_llm_client

# 尝试导入 VectorStore（降级安全）
try:
    from vector_store import VectorStore
    VECTOR_STORE_AVAILABLE = True
except ImportError:
    VectorStore = None
    VECTOR_STORE_AVAILABLE = False
    print("[SmartClipLLM] ⚠️ vector_store 模块未找到，RAG 功能降级")


class SmartClipLLM:
    def __init__(self, demo_mode=True, session_id: str = None):
        """
        初始化 SmartClipLLM

        Args:
            demo_mode:  演示模式，True 时不保存到文件系统
            session_id: 用户会话 ID，用于 RAG 检索时区分用户笔记
        """
        self.demo_mode = demo_mode
        self.session_id = session_id
        self.doc_manager = DocumentManager(demo_mode=demo_mode)
        self.client_config = get_llm_client()

        # ── LLM 配置检查 ──────────────────────────────────────────────────────
        if not self.client_config:
            print("=" * 60)
            print("[SmartClipLLM] ⚠️ 警告：LLM客户端配置未初始化！")
            print("=" * 60)
            print("[SmartClipLLM] 这会导致所有LLM调用失败")
            print("[SmartClipLLM] 请检查 config_local.py 或环境变量配置")
            print("=" * 60)
        else:
            print("[SmartClipLLM] ✅ LLM配置已加载")
            api_key_preview = (self.client_config.get('api_key', '')[:8] + "...") if self.client_config.get('api_key') else "未设置"
            app_id_preview  = (self.client_config.get('app_id',  '')[:8] + "...") if self.client_config.get('app_id')  else "未设置"
            print(f"[SmartClipLLM] API_KEY: {api_key_preview}")
            print(f"[SmartClipLLM] APP_ID:  {app_id_preview}")

        # ── VectorStore 初始化（从环境变量自动读取，失败则降级）──────────────
        self.vector_store = None
        if VECTOR_STORE_AVAILABLE and VectorStore is not None:
            cf_account_id = os.environ.get("CF_ACCOUNT_ID")
            cf_api_token  = os.environ.get("CF_API_TOKEN")
            dashscope_key = os.environ.get("DASHSCOPE_API_KEY")

            if cf_account_id and cf_api_token and dashscope_key:
                self.vector_store = VectorStore(
                    cf_account_id=cf_account_id,
                    cf_api_token=cf_api_token,
                    api_key=dashscope_key,
                )
                print(f"[SmartClipLLM] ✅ RAG VectorStore 已初始化（HTTP 模式）")
                if session_id:
                    print(f"[SmartClipLLM] ✅ session_id: {session_id[:16]}...")
            else:
                missing = []
                if not cf_account_id: missing.append("CF_ACCOUNT_ID")
                if not cf_api_token:  missing.append("CF_API_TOKEN")
                if not dashscope_key: missing.append("DASHSCOPE_API_KEY")
                print(f"[SmartClipLLM] ⚠️ RAG 降级：缺少环境变量 {', '.join(missing)}")

        # ── 初始化意图识别器，传入 vector_store 和 session_id ─────────────────
        self.intent_recognizer = LLMIntentRecognizer(
            self.doc_manager,
            self.client_config,
            vector_store=self.vector_store,
            session_id=self.session_id,
        )
        # 重置对话历史，确保每次启动时都是干净的状态
        self.intent_recognizer.reset_conversation()

        self.is_running = True
        # 待确认的操作（用于二次确认机制）
        self.pending_action = None

    def update_session_id(self, session_id: str):
        """
        更新会话 ID（在 api_server 分配 session_id 后调用）。
        同步更新 intent_recognizer 的 session_id，确保 RAG 检索使用正确的用户标识。
        """
        self.session_id = session_id
        if self.intent_recognizer:
            self.intent_recognizer.session_id = session_id
        print(f"[SmartClipLLM] 🔄 session_id 已更新: {session_id[:16]}...")
