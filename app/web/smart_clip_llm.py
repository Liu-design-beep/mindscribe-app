# smart_clip_llm.py
# 灵辑 (Mindscribe) - AI 内容收藏助手 LLM增强版 (基于通义千问)
# 核心对话引擎 (Core Conversation Engine)

from document_manager import DocumentManager
from intent_recognizer import LLMIntentRecognizer
from config import get_llm_client

class SmartClipLLM:
    def __init__(self):
        self.doc_manager = DocumentManager()
        self.client_config = get_llm_client()
        
        # 检查LLM配置
        if not self.client_config:
            print("=" * 60)
            print("[SmartClipLLM] ⚠️ 警告：LLM客户端配置未初始化！")
            print("=" * 60)
            print("[SmartClipLLM] 这会导致所有LLM调用失败")
            print("[SmartClipLLM] 请检查 config_local.py 或环境变量配置")
            print("=" * 60)
        else:
            print(f"[SmartClipLLM] ✅ LLM配置已加载")
            api_key_preview = self.client_config.get('api_key', '')[:8] + "..." if self.client_config.get('api_key') else "未设置"
            app_id_preview = self.client_config.get('app_id', '')[:8] + "..." if self.client_config.get('app_id') else "未设置"
            print(f"[SmartClipLLM] API_KEY: {api_key_preview}")
            print(f"[SmartClipLLM] APP_ID: {app_id_preview}")
        
        self.intent_recognizer = LLMIntentRecognizer(self.doc_manager, self.client_config)
        # 重置对话历史，确保每次启动时都是干净的状态
        # 这可以避免之前对话历史中的错误格式（如双大括号）影响后续的回复
        self.intent_recognizer.reset_conversation()
        self.is_running = True
        # 待确认的操作（用于二次确认机制）
        self.pending_action = None


            print(f"[SmartClipLLM] ✅ LLM配置已加载")
            api_key_preview = self.client_config.get('api_key', '')[:8] + "..." if self.client_config.get('api_key') else "未设置"
            app_id_preview = self.client_config.get('app_id', '')[:8] + "..." if self.client_config.get('app_id') else "未设置"
            print(f"[SmartClipLLM] API_KEY: {api_key_preview}")
            print(f"[SmartClipLLM] APP_ID: {app_id_preview}")
        
        self.intent_recognizer = LLMIntentRecognizer(self.doc_manager, self.client_config)
        # 重置对话历史，确保每次启动时都是干净的状态
        # 这可以避免之前对话历史中的错误格式（如双大括号）影响后续的回复
        self.intent_recognizer.reset_conversation()
        self.is_running = True
        # 待确认的操作（用于二次确认机制）
        self.pending_action = None



