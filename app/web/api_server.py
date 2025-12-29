# api_server.py
# 灵辑 (Mindscribe) - FastAPI 后端服务
# 将现有的Python逻辑封装为RESTful API

import os
import re
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import uuid
from datetime import datetime
import json
from http import HTTPStatus

# 优先从当前目录（web）导入模块
# 先添加当前目录到路径的最前面，确保优先导入当前目录的模块
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from smart_clip_llm import SmartClipLLM
from document_manager import DocumentManager
from config import API_KEY, APP_ID
from chapter_extractor import extract_chapter_content, get_chapter_list  # 新增：章节提取功能

from dashscope import Application

# 尝试导入文档匹配器（如果可用）
try:
    from document_matcher import DocumentMatcher
    DOCUMENT_MATCHER_AVAILABLE = True
except ImportError:
    try:
        from web.document_matcher import DocumentMatcher
        DOCUMENT_MATCHER_AVAILABLE = True
    except ImportError:
        try:
            import sys
            import os
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            from document_matcher import DocumentMatcher
            DOCUMENT_MATCHER_AVAILABLE = True
        except ImportError:
            DOCUMENT_MATCHER_AVAILABLE = False
            print("[警告] document_matcher 模块未找到，文档匹配检查功能将被禁用")
            DocumentMatcher = None

# 尝试导入 Cloudflare 存储（如果可用）
try:
    from cloudflare_document_manager import CloudflareDocumentManager
    CLOUDFLARE_AVAILABLE = True
except ImportError:
    CLOUDFLARE_AVAILABLE = False
    CloudflareDocumentManager = None

# ============================================
# FastAPI 应用初始化
# ============================================
app = FastAPI(
    title="灵辑 API",
    description="智能笔记助手后端API",
    version="1.0.0"
)

# ============================================
# CORS 配置（允许前端跨域请求）
# ============================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 云部署时允许所有来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# 会话管理器
# ============================================
class SessionManager:
    """
    管理用户会话，每个session_id对应一个SmartClipLLM实例
    """
    def __init__(self):
        self.sessions: Dict[str, SmartClipLLM] = {}
    
    def get_or_create_session(self, session_id: Optional[str] = None) -> tuple[str, SmartClipLLM]:
        """
        获取或创建会话
        
        Args:
            session_id: 会话ID，如果为None则创建新会话
            
        Returns:
            (session_id, SmartClipLLM实例)
        """
        # 演示模式：每次都创建新会话，不复用旧会话
        # if session_id and session_id in self.sessions:
        #     return session_id, self.sessions[session_id]
        
        # 创建新会话（每次都创建新的）
        new_session_id = f"demo_{uuid.uuid4().hex[:16]}"
        print(f"[会话管理] 创建新的演示会话: {new_session_id}")
        
        # 创建 SmartClipLLM 实例（启用演示模式）
        app_instance = SmartClipLLM(demo_mode=True)
        self.sessions[new_session_id] = app_instance
        
        print(f"[会话管理] 演示会话创建完成，文档已初始化")
        
        return new_session_id, self.sessions[new_session_id]
    
    def get_documents(self, session_id: str) -> list[str]:
        """
        获取指定会话的文档列表
        
        Args:
            session_id: 会话ID
            
        Returns:
            文档标题列表
        """
        if session_id not in self.sessions:
            return []
        
        app_instance = self.sessions[session_id]
        return list(app_instance.doc_manager.documents.keys())

# 全局会话管理器实例
session_manager = SessionManager()

# 开发者模式配置
DEV_MODE_CODE = "开发者模式#000"  # 开发者模式访问代码
EDIT_MODE_CODE = "set000"  # 修改模式代码
dev_mode_sessions: Dict[str, bool] = {}  # 存储已启用开发者模式的会话
edit_mode_sessions: Dict[str, bool] = {}  # 存储已启用修改模式的会话

# ============================================
# 辅助函数：构建意图信息
# ============================================
def build_intent_info(intent_data: Dict[str, Any], intent: str) -> Dict[str, Any]:
    """
    构建意图识别信息，用于AI反馈面板显示
    
    Args:
        intent_data: LLM返回的意图识别数据
        intent: 处理后的意图类型
        
    Returns:
        包含意图识别信息的字典
    """
    intent_info = {
        "intent": intent,
        "original_intent": intent_data.get("intent_type") or intent_data.get("intent"),
        "doc_title": intent_data.get("doc_title") or intent_data.get("target_document"),
        "position": intent_data.get("position") or intent_data.get("target_location_raw"),
        "content": intent_data.get("content") or intent_data.get("content_to_process", ""),
        "content_to_process": intent_data.get("content_to_process") or intent_data.get("content", ""),
        "content_length": len(intent_data.get("content", "") or intent_data.get("content_to_process", ""))
    }
    
    # 添加消息样式信息
    if "message_style" in intent_data:
        intent_info["message_style"] = intent_data.get("message_style")
    
    return intent_info

def get_edit_mode_enabled(app_instance, cloudflare_manager=None) -> bool:
    """
    获取编辑权限状态
    Args:
        app_instance: SmartClipLLM实例
        cloudflare_manager: CloudflareDocumentManager实例（可选）
    Returns:
        是否已启用编辑权限
    """
    if cloudflare_manager and hasattr(cloudflare_manager, 'edit_mode_enabled'):
        return cloudflare_manager.edit_mode_enabled
    if hasattr(app_instance, 'doc_manager') and hasattr(app_instance.doc_manager, 'edit_mode_enabled'):
        return app_instance.doc_manager.edit_mode_enabled
    return False

def build_tools_used(intent: str, is_dev_mode: bool, use_cloudflare: bool = False, use_d1: bool = False) -> List[str]:
    """
    构建工具调用列表，用于AI反馈面板显示
    
    Args:
        intent: 意图类型
        is_dev_mode: 是否开发者模式
        use_cloudflare: 是否使用了Cloudflare存储
        use_d1: 是否使用了D1数据库
        
    Returns:
        工具调用列表
    """
    tools = []
    
    # 根据意图类型添加工具
    if intent == "ADD_CONTENT":
        tools.append("add_content")
    elif intent == "DISPLAY_DOC":
        tools.append("get_document")
    elif intent == "DELETE_CONTENT":
        tools.append("clear_document")
    elif intent == "CREATE_DOCUMENT":
        tools.append("create_document")
    elif intent == "SET_ACTIVE":
        tools.append("set_active_document")
    
    # 添加存储工具
    if use_cloudflare:
        tools.append("cloudflare_storage")
    if use_d1:
        tools.append("d1_database")
    if not use_cloudflare and not use_d1:
        tools.append("local_storage")
    
    # 添加意图识别工具
    tools.append("intent_recognizer")
    
    return tools
unknown_count_sessions: Dict[str, int] = {}  # 存储每个会话连续无法理解意图的次数
pending_new_doc_actions: Dict[str, Dict[str, Any]] = {}  # 存储待确认的新建文档操作

# Cloudflare 存储配置
USE_CLOUDFLARE = os.environ.get("USE_CLOUDFLARE", "false").lower() == "true"
CLOUDFLARE_KV = None  # 在 Cloudflare Workers 环境中，这会被注入

# D1 数据库配置
USE_D1 = os.environ.get("USE_D1", "false").lower() == "true"
D1_DATABASE_ID = os.environ.get("D1_DATABASE_ID", "8fb7b530-17e4-44f1-819f-ee585effdbf2")
D1_AVAILABLE = False
try:
    from d1_document_manager import D1DocumentManager
    D1_AVAILABLE = True
except ImportError:
    D1_AVAILABLE = False
    D1DocumentManager = None

# ============================================
# 请求/响应模型
# ============================================

class ChatRequest(BaseModel):
    """聊天请求模型"""
    session_id: Optional[str] = None
    text: str
    dev_mode_code: Optional[str] = None  # 开发者模式代码
    mode: Optional[str] = None  # 模式：chat（对话模式）或 view（完整查看模式）

class ChatResponse(BaseModel):
    """聊天响应模型"""
    response_type: str  # "TEXT" | "CONFIRMATION" | "DOCUMENT" | "DEV_MODE_REQUIRED" | "EDIT_MODE_REQUIRED" | "ALL_DOCUMENTS" | "UNKNOWN" | "CREATE_NEW_DOCUMENT_CONFIRMATION"
    content: str
    new_session_id: Optional[str] = None
    dev_mode_enabled: Optional[bool] = None  # 开发者模式状态
    edit_mode_enabled: Optional[bool] = None  # 修改模式状态
    documents: Optional[Dict[str, List[str]]] = None  # 所有文档内容（完整查看模式）
    message_style: Optional[str] = "normal"  # 消息样式："normal" | "error" | "warning"
    suggested_doc_title: Optional[str] = None  # 建议的新文档标题（用于CREATE_NEW_DOCUMENT_CONFIRMATION）
    intent_info: Optional[Dict[str, Any]] = None  # 意图识别信息（用于AI反馈面板）
    tools_used: Optional[List[str]] = None  # 调用的工具列表（用于AI反馈面板）
    match_confirmation_needed: Optional[bool] = False  # 是否需要文档匹配确认
    match_warning_message: Optional[str] = None  # 文档匹配警告消息

class DocumentsResponse(BaseModel):
    """文档列表响应模型"""
    documents: list[str]

class DevModeRequest(BaseModel):
    """开发者模式请求模型"""
    code: str  # 开发者模式代码：开发者模式#000

# ============================================
# API 路由
# ============================================

@app.get("/")
async def root():
    """根路径，返回API信息"""
    return {
        "name": "灵辑 API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "chat": "/api/chat",
            "documents": "/api/documents"
        }
    }

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    处理用户聊天消息
    
    这个接口接收用户的文本输入，通过SmartClipLLM处理，
    返回AI的回复或需要确认的操作。
    """
    try:
        # 检查开发者模式代码
        user_input = request.text.strip()
        dev_mode_code = request.dev_mode_code or ""
        
        # 如果输入是开发者模式代码，启用开发者模式
        if user_input == DEV_MODE_CODE or dev_mode_code == DEV_MODE_CODE:
            session_id = request.session_id or f"session_{uuid.uuid4().hex[:16]}"
            dev_mode_sessions[session_id] = True
            
            # 如果使用 Cloudflare 存储，启用云端开发者模式
            if USE_CLOUDFLARE and CLOUDFLARE_AVAILABLE and CLOUDFLARE_KV:
                try:
                    cloudflare_manager = CloudflareDocumentManager(CLOUDFLARE_KV, True)
                    await cloudflare_manager.initialize()
                    await cloudflare_manager.enable_dev_mode()
                except Exception as e:
                    print(f"[警告] Cloudflare 存储初始化失败: {e}")
            
            # 获取所有开发者文档内容，自动显示三个重要文档
            try:
                # 获取所有文档
                if USE_D1 and D1_AVAILABLE and D1_DATABASE_ID:
                    from d1_document_manager import D1DocumentManager
                    d1_manager = D1DocumentManager(d1_database=None, doc_type="dev", session_id=None, dev_mode_enabled=True)
                    await d1_manager.initialize()
                    all_documents = d1_manager.documents.copy()
                else:
                    # 如果没有D1，使用内存中的文档
                    all_documents = {}
                
                # 确保有介绍文档和更新记录日志
                if "介绍文档" not in all_documents or not all_documents.get("介绍文档"):
                    intro_content = [
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
                        "## 🔍 竞品对比",
                        "",
                        "### Google NotebookLM",
                        "",
                        "**产品定位：** Google 推出的 AI 驱动的笔记和研究助手",
                        "",
                        "**核心功能：**",
                        "• 📝 智能笔记整理：基于上传的文档自动生成笔记摘要和关键点",
                        "• 🎤 录音讲概念：支持语音输入，将语音转换为文字并智能整理",
                        "• 🤖 AI 诊断盲区：自动识别知识盲点，提供学习建议和补充内容",
                        "• 📚 定制 Quiz 答题：根据笔记内容自动生成个性化测验题目，帮助巩固知识",
                        "• 🔗 多源整合：支持从多个文档源整合信息，构建知识图谱",
                        "",
                        "**技术特点：**",
                        "• 基于 Gemini 3 Flash 模型，响应速度快",
                        "• 深度集成 Google 生态系统",
                        "• 强大的多模态理解能力（文本、语音、图像）",
                        "",
                        "**与灵辑的对比：**",
                        "• ✅ 灵辑优势：更轻量级、更灵活的对话交互、支持多文档并行管理",
                        "• 📊 NotebookLM 优势：更强的多模态能力、自动生成测验、知识盲点诊断",
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
                        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                        "版本：Beta | 更新：2024-12 | 模型：通义千问3-coder-plus",
                        ""
                    ]
                    all_documents["介绍文档"] = intro_content
                
                if "更新记录日志" not in all_documents:
                    try:
                        from web.update_log_content import UPDATE_LOG_CONTENT
                        all_documents["更新记录日志"] = UPDATE_LOG_CONTENT
                    except ImportError:
                        all_documents["更新记录日志"] = ["更新记录日志内容"]
                
                
                # 返回所有文档内容，让前端自动显示
                return ChatResponse(
                    response_type="ALL_DOCUMENTS",
                    content="✅ 开发者模式已启用！以下是三个重要文档：",
                    documents=all_documents,
                    new_session_id=session_id if not request.session_id else None,
                    dev_mode_enabled=True
                )
            except Exception as e:
                print(f"[API] 获取开发者文档失败: {e}")
                # 如果获取失败，至少返回成功消息
                return ChatResponse(
                    response_type="TEXT",
                    content="✅ 开发者模式已启用！您现在可以访问和修改云端永久保存的笔记。",
                    new_session_id=session_id if not request.session_id else None,
                    dev_mode_enabled=True
                )
        
        # 检查是否是 set000 修改模式代码
        if user_input == EDIT_MODE_CODE:
            session_id = request.session_id or f"session_{uuid.uuid4().hex[:16]}"
            is_dev_mode = dev_mode_sessions.get(session_id, False)
            
            if not is_dev_mode:
                return ChatResponse(
                    response_type="TEXT",
                    content="❌ 需要先启用开发者模式。请输入 '开发者模式#000'。",
                    new_session_id=session_id if not request.session_id else None,
                    dev_mode_enabled=False,
                    edit_mode_enabled=False
                )
            
            edit_mode_sessions[session_id] = True
            
            # 如果使用 Cloudflare 存储，启用修改模式
            if USE_CLOUDFLARE and CLOUDFLARE_AVAILABLE and CLOUDFLARE_KV:
                try:
                    cloudflare_manager = CloudflareDocumentManager(CLOUDFLARE_KV, True)
                    await cloudflare_manager.initialize()
                    cloudflare_manager.enable_edit_mode()
                except Exception as e:
                    print(f"[警告] Cloudflare 存储初始化失败: {e}")
            
            return ChatResponse(
                response_type="TEXT",
                content="✅ 修改权限已启用！您现在可以修改笔记内容了。",
                new_session_id=session_id if not request.session_id else None,
                dev_mode_enabled=True,
                edit_mode_enabled=True
                )
        
        # 获取或创建会话
        session_id, app_instance = session_manager.get_or_create_session(request.session_id)
        
        # 检查是否需要开发者模式
        is_dev_mode = dev_mode_sessions.get(session_id, False)
        is_edit_mode = edit_mode_sessions.get(session_id, False)
        
        # 如果使用 Cloudflare 存储，检查云端开发者模式
        cloudflare_manager = None
        if USE_CLOUDFLARE and CLOUDFLARE_AVAILABLE and CLOUDFLARE_KV:
            try:
                cloudflare_manager = CloudflareDocumentManager(CLOUDFLARE_KV, is_dev_mode)
                await cloudflare_manager.initialize()
                cloudflare_dev_mode = await cloudflare_manager.check_dev_mode()
                is_dev_mode = is_dev_mode or cloudflare_dev_mode
                if is_edit_mode:
                    cloudflare_manager.enable_edit_mode()
            except Exception as e:
                print(f"[警告] Cloudflare 存储检查失败: {e}")
        
        # 处理完整查看模式
        if request.mode == "view" or user_input.lower() in ["查看所有笔记", "完整查看", "查看全部"]:
            # 确定文档类型：开发者模式或试用模式
            # 检查是否是试用模式（通过session_id判断，或者通过is_trial参数）
            is_trial_mode = not is_dev_mode  # 如果不是开发者模式，就是试用模式
            
            # 获取所有文档内容
            # 辅助函数：检测是否包含默认占位文本
            def contains_default(c):
                if c is None:
                    return False
                s = str(c)
                return (
                    ("这是您的试用文档" in s)
                    or ("可以随时添加内容" in s)
                    or ("这是您的默认文档" in s)
                )
            
            all_documents = {}
            # 优先使用 D1 数据库（如果配置）
            # 注意：在 FastAPI 环境中，D1 数据库需要通过 HTTP API 访问
            # 这里我们尝试使用 D1DocumentManager，即使 d1_database=None
            # D1Storage 会检测到没有真实的 D1 对象，但我们可以通过其他方式获取数据
            if USE_D1 and D1_AVAILABLE and D1_DATABASE_ID:
                try:
                    from d1_document_manager import D1DocumentManager
                    # 根据模式确定doc_type
                    doc_type = "dev" if is_dev_mode else "trial"
                    # 在 FastAPI 环境中，d1_database=None，但 D1Storage 仍然可以工作
                    # 它会使用数据库 ID 通过 HTTP API 访问（如果实现了的话）
                    d1_manager = D1DocumentManager(d1_database=None, doc_type=doc_type, session_id=session_id, dev_mode_enabled=is_dev_mode)
                    await d1_manager.initialize()
                    all_documents = d1_manager.documents.copy()
                    print(f"[API] 查看所有笔记 - doc_type={doc_type}, session_id={session_id}, 文档数量={len(all_documents)}")
                    # 打印每个文档的内容长度，用于调试
                    for title, content in all_documents.items():
                        content_str = str(content) if isinstance(content, list) else str(content)
                        print(f"[API] 文档 '{title}': 内容长度={len(content) if isinstance(content, list) else 0}, 包含默认占位文本={('这是您的试用文档' in content_str) or ('可以随时添加内容' in content_str)}")
                    
                    # 在 FastAPI 环境中，如果 D1 数据库不可用（d1_database=None），
                    # D1Storage 的 is_d1 会是 False，导致无法从数据库读取
                    # 此时我们需要手动添加介绍文档和更新记录日志（开发者模式）
                    # 确保包含介绍文档和更新记录日志
                    # 检查介绍文档是否存在，或者内容是否为空/过时
                    existing_intro = all_documents.get("介绍文档", [])
                    is_empty_or_old = (
                        "介绍文档" not in all_documents or
                        not existing_intro or 
                        len(existing_intro) < 10 or
                        "产品概述" not in str(existing_intro)
                    )
                    
                    if is_empty_or_old:
                        # 如果介绍文档不存在或内容过时，创建/更新它
                        intro_content = [
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
                            "• 包含「介绍文档」、「更新记录日志」",
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
                        ]
                        all_documents["介绍文档"] = intro_content
                        # 保存到数据库
                        try:
                                await d1_manager.storage.save_document("介绍文档", intro_content, "dev")
                                print(f"[API] 介绍文档已创建/更新，内容行数: {len(intro_content)}")
                        except Exception as e:
                            print(f"[API] 保存介绍文档失败: {e}")
                    if "更新记录日志" not in all_documents:
                        try:
                            from web.update_log_content import UPDATE_LOG_CONTENT
                            all_documents["更新记录日志"] = UPDATE_LOG_CONTENT
                        except ImportError:
                            all_documents["更新记录日志"] = ["更新记录日志内容"]
                except Exception as e:
                    print(f"[警告] D1 数据库读取失败: {e}")
                    import traceback
                    print(traceback.format_exc())
                    # 回退到 Cloudflare 或本地
                    if USE_CLOUDFLARE and CLOUDFLARE_AVAILABLE and CLOUDFLARE_KV and cloudflare_manager:
                            doc_titles = cloudflare_manager.get_document_titles()
                            for title in doc_titles:
                                content = cloudflare_manager.get_document(title)
                                all_documents[title] = content
                    else:
                        # 从本地存储读取，需要检查并替换默认文本
                        all_documents = {}
                        for title, content in app_instance.doc_manager.documents.items():
                            # 使用 get_document 方法，它会自动检测并替换默认文本
                            clean_content = app_instance.doc_manager.get_document(title)
                            all_documents[title] = clean_content if clean_content is not None else []
            elif USE_CLOUDFLARE and CLOUDFLARE_AVAILABLE and CLOUDFLARE_KV and cloudflare_manager:
                doc_titles = cloudflare_manager.get_document_titles()
                for title in doc_titles:
                    content = cloudflare_manager.get_document(title)
                    all_documents[title] = content
            else:
                # 从本地存储读取，需要检查并替换默认文本
                    all_documents = {}
                    for title, content in app_instance.doc_manager.documents.items():
                        # 使用 get_document 方法，它会自动检测并替换默认文本
                        clean_content = app_instance.doc_manager.get_document(title)
                        all_documents[title] = clean_content if clean_content is not None else []
            
            # 如果没有使用D1/Cloudflare，或读取失败，补全默认文档内容
            if not USE_D1 or not D1_AVAILABLE or not D1_DATABASE_ID:
                if is_dev_mode:
                    # 开发者模式兜底：介绍文档 & 更新记录日志
                    if "介绍文档" not in all_documents or not all_documents.get("介绍文档"):
                        all_documents["介绍文档"] = [
                            "欢迎使用灵辑 (Mindscribe) - AI 智能笔记助手",
                            "",
                            "## 设计理念",
                            "灵辑是一个基于 LLM 的智能笔记助手，旨在帮助用户轻松管理和组织笔记内容。",
                            "",
                            "## 核心功能",
                            "1. 智能对话：通过自然语言与系统交互，添加、查看、管理笔记",
                            "2. 云端存储：所有笔记永久保存在云端，支持跨设备访问",
                            "3. 开发者模式：输入 '开发者模式#000' 启用开发者模式",
                            "4. 修改模式：输入 'set000' 启用笔记修改权限",
                            "",
                            "## 使用说明",
                            "- 对话模式：通过自然语言与系统交互",
                            "- 完整查看：查看所有笔记的完整内容",
                            "- 介绍文档为只读文档，用于介绍系统设计内容",
                            "",
                            "## 注意事项",
                            "介绍文档仅供查询，不可修改。如需修改其他笔记，请先输入 'set000' 启用修改权限。"
                        ]
                    if "更新记录日志" not in all_documents:
                        try:
                            from web.update_log_content import UPDATE_LOG_CONTENT
                            all_documents["更新记录日志"] = UPDATE_LOG_CONTENT
                        except ImportError:
                            all_documents["更新记录日志"] = ["更新记录日志内容"]
                    
                else:
                    # 试用模式兜底：试用文档(空) + PM问答笔记
                    if "试用文档" not in all_documents or not all_documents.get("试用文档"):
                        all_documents["试用文档"] = [""]
                    if "通信原理笔记" not in all_documents or not all_documents.get("通信原理笔记"):
                        all_documents["通信原理笔记"] = [
                            "## 通信原理笔记",
                            "",
                            "### 1. 信号与系统基础",
                            "- 信号分类：模拟信号 vs 数字信号",
                            "- 傅里叶变换：时域与频域的转换",
                            "",
                            "### 2. 调制技术",
                            "- 模拟调制：AM, FM, PM",
                            "- 数字调制：ASK, FSK, PSK, QAM",
                            "",
                            "### 3. 信道编码",
                            "- 纠错编码：汉明码, 卷积码",
                            "- 香农定理：信道容量极限"
                        ]

                    if "PM问答笔记" not in all_documents or not all_documents.get("PM问答笔记"):
                        all_documents["PM问答笔记"] = [
                            "欢迎使用灵辑 (Mindscribe) - AI 内容收藏助手",
                            "",
                            "## PM问答笔记",
                            "",
                            "场景：你正在参加腾讯 AI 产品经理的职位面试。面试官是一位经验丰富的产品总监。",
                            "",
                            "问题：",
                            "",
                            "1、您如何理解 AI 产品经理的角色，以及您认为这个角色在腾讯 AI 战略中扮演着怎样的作用？",
                            "",
                            "回答思路：",
                            "",
                            "展示你对 AI 产品经理职责的理解，包括市场调研、用户需求分析、产品设计、开发管理、数据分析等。",
                            "",
                            "结合腾讯的 AI 战略，例如腾讯云 AI、腾讯 AI Lab 等，阐述你认为 AI 产品经理在推动腾讯 AI 战略落地、打造 AI 产品生态中的重要作用。",
                            "",
                            "可以结合你对腾讯 AI 产品的了解，例如微信小程序、腾讯翻译君等，谈谈你对腾讯 AI 产品发展方向的看法。",
                            "",
                            "2、请您谈谈您对当前 AI 技术发展趋势的理解，以及您认为哪些 AI 技术将会在未来几年对腾讯产品产生重大影响？",
                            "",
                            "回答思路：",
                            "",
                            "展示你对 AI 技术发展趋势的了解，例如深度学习、自然语言处理、计算机视觉等。",
                            "",
                            "选择几个你认为对腾讯产品具有重大影响的 AI 技术，并结合具体案例进行阐述。例如，你认为自然语言处理技术可以应用于微信聊天机器人，提升用户体验；计算机视觉技术可以应用于腾讯视频，实现更精准的视频内容推荐。",
                            "",
                            "可以结合你对腾讯产品线的了解，谈谈你对 AI 技术在腾讯产品中的应用前景。",
                            "",
                            "3、请您描述一个您曾经参与过的 AI 产品项目，并详细介绍您在项目中的角色、遇到的挑战以及最终的成果。",
                            "",
                            "回答思路：",
                            "",
                            "选择一个你参与过的 AI 产品项目，并详细介绍项目的背景、目标、以及你的角色和职责。",
                            "",
                            "突出你在项目中遇到的挑战，例如技术难题、用户需求变化等，并描述你如何克服这些挑战。",
                            "",
                            "最后，阐述项目的最终成果，例如产品上线、用户增长、商业价值等。",
                            "",
                            "4、您如何看待 AI 产品的伦理问题，以及您认为腾讯在 AI 产品研发中应该如何处理这些问题？",
                            "",
                            "回答思路：",
                            "",
                            "展示你对 AI 伦理问题的理解，例如数据隐私、算法歧视、人工智能安全等。",
                            "",
                            "结合腾讯的企业文化和社会责任，阐述你认为腾讯应该如何处理这些问题，例如建立完善的 AI 伦理规范、加强数据安全管理、提升算法透明度等。",
                            "",
                            "可以结合一些具体的案例，例如腾讯 AI 翻译的语言歧视问题，谈谈你对腾讯在 AI 伦理方面的思考。",
                            "",
                            "5、您对未来 AI 产品的发展趋势有什么看法？您认为腾讯应该如何抓住机遇，引领 AI 产品的未来？",
                            "",
                            "回答思路：",
                            "",
                            "展示你对未来 AI 产品发展趋势的了解，例如 AI 与物联网、AI 与云计算、AI 与边缘计算的融合等。",
                            "",
                            "结合腾讯的优势和资源，阐述你认为腾讯应该如何抓住机遇，引领 AI 产品的未来，例如加大 AI 技术研发投入、布局 AI 生态、打造 AI 产品矩阵等。",
                            "",
                            "可以结合你对腾讯的战略布局，谈谈你对腾讯未来 AI 产品发展方向的看法。",
                            "",
                            "准备建议：",
                            "",
                            "提前了解腾讯的 AI 战略、产品线、以及相关新闻报道。",
                            "",
                            "准备几个你参与过的 AI 产品项目案例，并思考项目中的挑战和成果。",
                            "",
                            "思考 AI 伦理问题，并结合腾讯的企业文化和社会责任，提出你的观点。",
                            "",
                            "关注未来 AI 产品发展趋势，并思考腾讯如何抓住机遇。",
                            "",
                            "祝你面试顺利！"
                        ]
            
            # 确保模式下的默认文档存在且内容不为空
            if is_dev_mode:
                # 确保有介绍文档（包含模型/AB测试信息）
                if "介绍文档" not in all_documents:
                    intro_content = [
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
                        "## 🔍 竞品对比",
                        "",
                        "### Google NotebookLM",
                        "",
                        "**产品定位：** Google 推出的 AI 驱动的笔记和研究助手",
                        "",
                        "**核心功能：**",
                        "• 📝 智能笔记整理：基于上传的文档自动生成笔记摘要和关键点",
                        "• 🎤 录音讲概念：支持语音输入，将语音转换为文字并智能整理",
                        "• 🤖 AI 诊断盲区：自动识别知识盲点，提供学习建议和补充内容",
                        "• 📚 定制 Quiz 答题：根据笔记内容自动生成个性化测验题目，帮助巩固知识",
                        "• 🔗 多源整合：支持从多个文档源整合信息，构建知识图谱",
                        "",
                        "**技术特点：**",
                        "• 基于 Gemini 3 Flash 模型，响应速度快",
                        "• 深度集成 Google 生态系统",
                        "• 强大的多模态理解能力（文本、语音、图像）",
                        "",
                        "**与灵辑的对比：**",
                        "• ✅ 灵辑优势：更轻量级、更灵活的对话交互、支持多文档并行管理",
                        "• 📊 NotebookLM 优势：更强的多模态能力、自动生成测验、知识盲点诊断",
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
                        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                        "版本：Beta | 更新：2024-12 | 模型：通义千问3-coder-plus",
                        ""
                    ]
                    all_documents["介绍文档"] = intro_content
                
                # 确保有更新记录日志
                if "更新记录日志" not in all_documents:
                    try:
                        from web.update_log_content import UPDATE_LOG_CONTENT
                        all_documents["更新记录日志"] = UPDATE_LOG_CONTENT
                    except ImportError:
                        all_documents["更新记录日志"] = ["更新记录日志内容"]
                
            else:
                # 试用模式：确保有试用文档和 PM问答笔记，且内容不是默认提示
                trial_default = [""]  # 试用文档默认空
                pm_default = [
                    "欢迎使用灵辑 (Mindscribe) - AI 内容收藏助手",
                    "",
                    "## PM问答笔记",
                    "",
                    "场景：你正在参加腾讯 AI 产品经理的职位面试。面试官是一位经验丰富的产品总监。",
                    "",
                    "问题：",
                    "",
                    "1、您如何理解 AI 产品经理的角色，以及您认为这个角色在腾讯 AI 战略中扮演着怎样的作用？",
                    "",
                    "回答思路：",
                    "",
                    "展示你对 AI 产品经理职责的理解，包括市场调研、用户需求分析、产品设计、开发管理、数据分析等。",
                    "",
                    "结合腾讯的 AI 战略，例如腾讯云 AI、腾讯 AI Lab 等，阐述你认为 AI 产品经理在推动腾讯 AI 战略落地、打造 AI 产品生态中的重要作用。",
                    "",
                    "可以结合你对腾讯 AI 产品的了解，例如微信小程序、腾讯翻译君等，谈谈你对腾讯 AI 产品发展方向的看法。",
                    "",
                    "2、请您谈谈您对当前 AI 技术发展趋势的理解，以及您认为哪些 AI 技术将会在未来几年对腾讯产品产生重大影响？",
                    "",
                    "回答思路：",
                    "",
                    "展示你对 AI 技术发展趋势的了解，例如深度学习、自然语言处理、计算机视觉等。",
                    "",
                    "选择几个你认为对腾讯产品具有重大影响的 AI 技术，并结合具体案例进行阐述。例如，你认为自然语言处理技术可以应用于微信聊天机器人，提升用户体验；计算机视觉技术可以应用于腾讯视频，实现更精准的视频内容推荐。",
                    "",
                    "可以结合你对腾讯产品线的了解，谈谈你对 AI 技术在腾讯产品中的应用前景。",
                    "",
                    "3、请您描述一个您曾经参与过的 AI 产品项目，并详细介绍您在项目中的角色、遇到的挑战以及最终的成果。",
                    "",
                    "回答思路：",
                    "",
                    "选择一个你参与过的 AI 产品项目，并详细介绍项目的背景、目标、以及你的角色和职责。",
                    "",
                    "突出你在项目中遇到的挑战，例如技术难题、用户需求变化等，并描述你如何克服这些挑战。",
                    "",
                    "最后，阐述项目的最终成果，例如产品上线、用户增长、商业价值等。",
                    "",
                    "4、您如何看待 AI 产品的伦理问题，以及您认为腾讯在 AI 产品研发中应该如何处理这些问题？",
                    "",
                    "回答思路：",
                    "",
                    "展示你对 AI 伦理问题的理解，例如数据隐私、算法歧视、人工智能安全等。",
                    "",
                    "结合腾讯的企业文化和社会责任，阐述你认为腾讯应该如何处理这些问题，例如建立完善的 AI 伦理规范、加强数据安全管理、提升算法透明度等。",
                    "",
                    "可以结合一些具体的案例，例如腾讯 AI 翻译的语言歧视问题，谈谈你对腾讯在 AI 伦理方面的思考。",
                    "",
                    "5、您对未来 AI 产品的发展趋势有什么看法？您认为腾讯应该如何抓住机遇，引领 AI 产品的未来？",
                    "",
                    "回答思路：",
                    "",
                    "展示你对未来 AI 产品发展趋势的了解，例如 AI 与物联网、AI 与云计算、AI 与边缘计算的融合等。",
                    "",
                    "结合腾讯的优势和资源，阐述你认为腾讯应该如何抓住机遇，引领 AI 产品的未来，例如加大 AI 技术研发投入、布局 AI 生态、打造 AI 产品矩阵等。",
                    "",
                    "可以结合你对腾讯的战略布局，谈谈你对腾讯未来 AI 产品发展方向的看法。",
                    "",
                    "准备建议：",
                    "",
                    "提前了解腾讯的 AI 战略、产品线、以及相关新闻报道。",
                    "",
                    "准备几个你参与过的 AI 产品项目案例，并思考项目中的挑战和成果。",
                    "",
                    "思考 AI 伦理问题，并结合腾讯的企业文化和社会责任，提出你的观点。",
                    "",
                    "关注未来 AI 产品发展趋势，并思考腾讯如何抓住机遇。",
                    "",
                    "祝你面试顺利！"
                ]
                
                existing_trial = all_documents.get("试用文档", [])
                # 检测试用文档是否包含默认占位文本
                trial_has_default = contains_default(existing_trial) if existing_trial else False
                if ("试用文档" not in all_documents) or (not existing_trial) or trial_has_default:
                    all_documents["试用文档"] = trial_default
                
                existing_pm = all_documents.get("PM问答笔记", [])
                # 检测PM问答笔记是否包含默认占位文本
                pm_has_default = contains_default(existing_pm) if existing_pm else False
                if ("PM问答笔记" not in all_documents) or (not existing_pm) or pm_has_default:
                    all_documents["PM问答笔记"] = pm_default
                
                # 初始化通信原理笔记
                communication_default = [
                    "# 通信原理笔记",
                    "",
                    "## 第一章 绪论",
                    "",
                    "通信原理是研究信息传输、处理和存储的基本理论和技术。通信系统的基本任务是实现信息的有效传输，确保信息从信源准确、可靠地传送到信宿。现代通信系统已经成为信息社会的基础设施，广泛应用于电话、互联网、广播电视、移动通信等各个领域。",
                    "",
                    "### 1.1 通信系统的基本组成",
                    "",
                    "通信系统主要由五个基本部分组成：信源、发送设备、信道、接收设备和信宿。信源是产生信息的源头，可以是人、机器或其他信息源。发送设备的作用是将信源产生的信息转换为适合在信道中传输的信号形式，包括编码、调制、放大等功能。信道是信号传输的媒介，可以是导线、光纤、无线电波等。接收设备的作用是接收信道中的信号，并进行解调、解码等处理，恢复出原始信息。信宿是信息的最终接收者。",
                    "",
                    "### 1.2 通信系统的分类",
                    "",
                    "通信系统可以按照多种方式进行分类。按传输媒介可分为有线通信和无线通信。有线通信使用导线、光纤等物理媒介，具有传输稳定、抗干扰能力强的优点，但需要铺设线路，成本较高。无线通信使用电磁波在空间中传播，具有灵活性强、覆盖范围广的优点，但容易受到干扰。按信号类型可分为模拟通信和数字通信。模拟通信传输的是连续变化的模拟信号，数字通信传输的是离散的数字信号。数字通信具有抗干扰能力强、易于加密、便于存储和处理等优点，已成为现代通信的主流。",
                    "",
                    "### 1.3 通信系统的主要性能指标",
                    "",
                    "通信系统的主要性能指标包括有效性、可靠性和经济性。有效性是指系统传输信息的速率，通常用信息传输速率或频带利用率来衡量。可靠性是指系统传输信息的准确程度，通常用误码率、误信率等指标来衡量。经济性是指系统的成本效益，包括设备成本、维护成本等。在实际应用中，有效性和可靠性往往存在矛盾，需要在两者之间进行权衡。",
                    "",
                    "## 第二章 信号与系统",
                    "",
                    "信号是信息的载体，是随时间或空间变化的物理量。系统是对信号进行处理的装置，可以是物理系统或抽象系统。信号与系统理论是通信原理的基础，为分析和设计通信系统提供了数学工具。",
                    "",
                    "### 2.1 信号的分类",
                    "",
                    "信号可以按照多种方式进行分类。按时间特性可分为连续时间信号和离散时间信号。连续时间信号在任意时刻都有定义，离散时间信号只在某些离散时刻有定义。按周期性可分为周期信号和非周期信号。周期信号满足f(t+T)=f(t)，其中T为周期。按能量特性可分为能量信号和功率信号。能量信号的能量有限，功率信号的功率有限。按确定性可分为确定性信号和随机信号。确定性信号的取值可以精确预测，随机信号的取值具有随机性。",
                    "",
                    "### 2.2 系统的特性",
                    "",
                    "系统具有多种重要特性。线性性是指系统满足叠加原理，即多个输入信号的线性组合的输出等于各输入信号单独作用时输出的线性组合。时不变性是指系统的特性不随时间变化，即输入信号延迟τ，输出信号也相应延迟τ。因果性是指系统的输出只依赖于当前和过去的输入，不依赖于未来的输入。稳定性是指有界输入产生有界输出。这些特性对于分析和设计通信系统具有重要意义。",
                    "",
                    "### 2.3 傅里叶变换",
                    "",
                    "傅里叶变换是信号分析的重要工具，它将时域信号转换为频域信号，揭示了信号的频率特性。连续时间信号的傅里叶变换定义为F(ω)=∫f(t)e^(-jωt)dt，离散时间信号的傅里叶变换定义为F(e^(jω))=Σf(n)e^(-jωn)。傅里叶变换具有线性性、时移性、频移性、卷积性等重要性质，在信号处理和通信系统分析中广泛应用。",
                    "",
                    "## 第三章 模拟调制",
                    "",
                    "模拟调制是将基带信号调制到载波上的过程，目的是使信号适合在信道中传输。调制可以改变信号的频率特性，提高信号的抗干扰能力，实现多路复用等。模拟调制主要包括幅度调制、频率调制和相位调制。",
                    "",
                    "### 3.1 幅度调制（AM）",
                    "",
                    "幅度调制是通过改变载波的幅度来传输信息。标准AM信号的表达式为s(t)=A[1+m(t)]cos(ωct)，其中A为载波幅度，m(t)为调制信号，ωc为载波角频率。AM信号的频谱包含载波分量和上下边带，带宽为调制信号最高频率的两倍。AM调制的优点是实现简单，缺点是功率效率低，因为大部分功率消耗在载波上。为了提高功率效率，可以采用抑制载波的双边带调制（DSB-SC）或单边带调制（SSB）。",
                    "",
                    "### 3.2 频率调制（FM）",
                    "",
                    "频率调制是通过改变载波的频率来传输信息。FM信号的瞬时频率与调制信号成正比，表达式为ω(t)=ωc+kfm(t)，其中kf为频率灵敏度。FM信号的频谱结构复杂，理论上带宽为无穷大，但实际应用中可以采用卡森公式估算带宽：B≈2(Δf+fm)，其中Δf为最大频偏，fm为调制信号的最高频率。FM调制的优点是抗干扰能力强，功率效率高，缺点是带宽较宽。FM广泛应用于调频广播、电视伴音等领域。",
                    "",
                    "### 3.3 相位调制（PM）",
                    "",
                    "相位调制是通过改变载波的相位来传输信息。PM信号的瞬时相位与调制信号成正比，表达式为φ(t)=ωct+kpm(t)，其中kp为相位灵敏度。PM和FM在数学上密切相关，PM信号的频率变化率与调制信号成正比，而FM信号的频率与调制信号成正比。PM调制的特性与FM类似，但实现方式不同。在实际应用中，PM常用于数字通信中的相移键控（PSK）调制。",
                    "",
                    "## 第四章 数字基带传输",
                    "",
                    "数字基带传输是数字信号在基带信道中的传输，是数字通信系统的基础。数字基带信号是未经调制的数字信号，其频谱从零频率开始。数字基带传输系统包括发送端、信道和接收端，主要涉及码型选择、功率谱分析、码间干扰等问题。",
                    "",
                    "### 4.1 数字基带信号的码型",
                    "",
                    "数字基带信号的码型选择对传输性能有重要影响。常用的码型包括单极性码、双极性码、归零码、非归零码等。单极性码用正电平表示1，零电平表示0，实现简单但存在直流分量。双极性码用正负电平表示1和0，无直流分量，抗干扰能力强。归零码在码元中间回到零电平，便于提取位同步信号。非归零码在整个码元期间保持电平不变，功率效率高。此外，还有曼彻斯特码、差分码等特殊码型，各有其应用场景。",
                    "",
                    "### 4.2 数字基带信号的功率谱",
                    "",
                    "数字基带信号的功率谱密度反映了信号的频域特性，对于信道设计和滤波器设计具有重要意义。随机数字基带信号的功率谱通常包含连续谱和离散谱两部分。连续谱由码元的波形决定，离散谱由码元的周期性决定。功率谱的形状影响信号的带宽需求，对于带宽受限的信道，需要选择功率谱集中的码型。",
                    "",
                    "### 4.3 码间干扰与奈奎斯特准则",
                    "",
                    "码间干扰是数字基带传输中的主要问题，由信道的非理想特性引起。当码元速率过高或信道带宽不足时，相邻码元的响应会相互重叠，导致码间干扰。奈奎斯特第一准则指出，如果系统的冲激响应满足h(nT)=1（n=0）和h(nT)=0（n≠0），则无码间干扰。奈奎斯特第二准则给出了无码间干扰的最小带宽要求：B≥Rs/2，其中Rs为码元速率。满足奈奎斯特准则的滤波器称为奈奎斯特滤波器，常用的有升余弦滚降滤波器。",
                    "",
                    "## 第五章 数字带通传输",
                    "",
                    "数字带通传输是将数字基带信号调制到载波上进行传输，使信号适合在带通信道中传输。数字调制技术是数字通信系统的核心技术，直接影响系统的性能和复杂度。数字调制主要包括振幅键控、频移键控和相移键控。",
                    "",
                    "### 5.1 二进制数字调制",
                    "",
                    "二进制数字调制是最基本的数字调制方式。二进制振幅键控（2ASK）用载波的有无表示0和1，实现简单但抗干扰能力弱。二进制频移键控（2FSK）用两个不同频率的载波表示0和1，抗干扰能力较强但带宽较宽。二进制相移键控（2PSK）用载波的相位表示0和1，功率效率高，抗干扰能力强，但存在相位模糊问题。二进制差分相移键控（2DPSK）通过相位差表示信息，解决了相位模糊问题，应用广泛。",
                    "",
                    "### 5.2 多进制数字调制",
                    "",
                    "多进制数字调制可以提高频带利用率，在相同的码元速率下传输更多的信息。M进制振幅键控（MASK）用M个不同的幅度表示M个符号，频带利用率高但抗干扰能力弱。M进制频移键控（MFSK）用M个不同频率的载波表示M个符号，抗干扰能力强但带宽很宽。M进制相移键控（MPSK）用M个不同的相位表示M个符号，在功率效率和频带利用率之间取得良好平衡，应用最广泛。正交振幅调制（QAM）同时利用幅度和相位两个维度，进一步提高了频带利用率，是现代数字通信系统的主流调制方式。",
                    "",
                    "### 5.3 数字调制的性能分析",
                    "",
                    "数字调制的性能主要用误码率来衡量。在加性高斯白噪声（AWGN）信道中，各种数字调制方式的误码率可以通过理论分析得到。2PSK的误码率最低，2FSK次之，2ASK最高。多进制调制的误码率随进制数M的增加而增加，但频带利用率提高。在实际应用中，需要根据信道条件和系统要求选择合适的调制方式。",
                    "",
                    "## 第六章 信源编码",
                    "",
                    "信源编码是为了提高传输效率而对信源输出进行的编码，目的是减少冗余，降低码率。信源编码分为无失真信源编码和限失真信源编码。无失真信源编码要求能够完全恢复原始信息，限失真信源编码允许一定的失真以换取更高的压缩比。",
                    "",
                    "### 6.1 无失真信源编码",
                    "",
                    "无失真信源编码的理论基础是香农第一定理，它指出信源的平均码长不能小于信源的熵。霍夫曼编码是一种最优的无失真信源编码方法，它根据符号出现的概率分配不同长度的码字，概率大的符号分配短码，概率小的符号分配长码，使得平均码长最小。算术编码是另一种高效的无失真编码方法，它将整个消息编码为一个实数，编码效率接近信源熵。LZ编码是一类基于字典的编码方法，通过查找已编码的字符串来压缩数据，广泛应用于文件压缩。",
                    "",
                    "### 6.2 限失真信源编码",
                    "",
                    "限失真信源编码的理论基础是香农第三定理，它给出了在给定失真度下的最小码率。量化是限失真编码的基本方法，它将连续的模拟信号转换为离散的数字信号。均匀量化实现简单但效率低，非均匀量化根据信号的概率分布设计量化间隔，效率更高。标量量化每次量化一个样本，矢量量化同时量化多个样本，可以进一步降低码率。变换编码通过正交变换将信号转换到变换域，利用变换系数的统计特性进行编码，广泛应用于图像和视频压缩。",
                    "",
                    "## 第七章 信道编码",
                    "",
                    "信道编码是为了提高传输可靠性而添加的冗余信息，目的是检测和纠正传输错误。信道编码的理论基础是香农第二定理，它指出只要信息传输速率小于信道容量，就可以通过适当的编码实现任意小的误码率。信道编码分为分组码和卷积码两大类。",
                    "",
                    "### 7.1 线性分组码",
                    "",
                    "线性分组码是信息位和校验位满足线性关系的分组码。线性分组码可以用生成矩阵或校验矩阵来描述。生成矩阵G用于编码，校验矩阵H用于译码和检错。线性分组码具有封闭性，任意两个码字的线性组合仍是码字。汉明码是一种重要的线性分组码，可以纠正单个错误。循环码是线性分组码的一个子类，具有循环移位不变性，可以用多项式来描述，实现简单。BCH码和RS码是循环码的重要类型，具有强大的纠错能力，广泛应用于数字通信和存储系统。",
                    "",
                    "### 7.2 卷积码",
                    "",
                    "卷积码的输出不仅与当前输入有关，还与之前的输入有关，具有记忆性。卷积码可以用生成多项式或状态图来描述。维特比算法是卷积码的最优译码算法，通过动态规划找到最可能的码字序列，计算复杂度适中，应用广泛。Turbo码是一种并行级联卷积码，通过迭代译码可以获得接近香农限的性能，是3G和4G移动通信系统的关键技术。LDPC码是另一种接近香农限的编码方式，具有稀疏的校验矩阵，译码复杂度低，广泛应用于5G通信系统。",
                    "",
                    "## 第八章 同步",
                    "",
                    "同步是数字通信系统中的关键技术，包括载波同步、位同步和帧同步。同步的准确性直接影响系统的性能，同步误差会导致误码率增加甚至系统失效。",
                    "",
                    "### 8.1 载波同步",
                    "",
                    "载波同步是接收端恢复载波的过程，对于相干解调至关重要。载波同步方法分为开环法和闭环法。开环法直接从接收信号中提取载波，实现简单但性能有限。闭环法通过锁相环（PLL）跟踪载波相位，性能好但实现复杂。对于PSK信号，可以采用平方环或Costas环提取载波。载波同步的精度用相位误差来衡量，相位误差会导致解调性能下降。",
                    "",
                    "### 8.2 位同步",
                    "",
                    "位同步是接收端恢复码元时钟的过程，用于确定码元的采样时刻。位同步方法分为开环法和闭环法。开环法从接收信号中直接提取时钟，如滤波法、微分法等。闭环法通过锁相环跟踪时钟相位，性能更好。数字锁相环（DPLL）是常用的位同步方法，通过比较本地时钟和接收信号的相位差来调整时钟频率。位同步的精度用定时误差来衡量，定时误差会导致码间干扰增加。",
                    "",
                    "### 8.3 帧同步",
                    "",
                    "帧同步是接收端识别帧起始位置的过程，用于正确解帧。帧同步通常通过在帧头插入特殊的同步码来实现。同步码的选择要考虑自相关性和互相关性，常用的有巴克码、m序列等。帧同步方法分为逐码移位法和存储相关法。逐码移位法逐位比较，实现简单但速度慢。存储相关法利用相关器快速找到同步位置，速度快但实现复杂。帧同步的可靠性用漏同步概率和假同步概率来衡量。",
                    "",
                    "## 第九章 多路复用和多址技术",
                    "",
                    "多路复用和多址技术是为了提高信道利用率，允许多个用户共享同一信道。多路复用是在发送端将多个信号合并，多址是在接收端区分不同用户的信号。常用的技术包括频分复用、时分复用、码分复用等。",
                    "",
                    "### 9.1 频分复用（FDM）",
                    "",
                    "频分复用是将不同信号调制到不同频率的载波上，在频域上分离。FDM系统将可用频带划分为多个子频带，每个子频带传输一路信号。FDM的优点是实现简单，各路信号相互独立。缺点是需要保护频带防止干扰，频带利用率不高。FDM广泛应用于模拟通信系统，如调频广播、有线电视等。正交频分复用（OFDM）是FDM的改进，通过使用正交的子载波，提高了频带利用率，是4G和5G移动通信系统的核心技术。",
                    "",
                    "### 9.2 时分复用（TDM）",
                    "",
                    "时分复用是将不同信号分配到不同的时隙，在时域上分离。TDM系统将时间划分为多个时隙，每个时隙传输一路信号。TDM的优点是各路信号可以使用相同的频带，频带利用率高。缺点是需要严格的时钟同步。TDM广泛应用于数字通信系统，如数字电话、SDH等。统计时分复用（STDM）根据业务需求动态分配时隙，进一步提高了信道利用率。",
                    "",
                    "### 9.3 码分复用（CDM）",
                    "",
                    "码分复用是利用不同的码序列来区分不同的信号，在码域上分离。CDM系统为每个用户分配一个唯一的扩频码，发送端用扩频码对信号进行扩频，接收端用相同的扩频码进行解扩。CDM的优点是抗干扰能力强，可以实现软容量，支持异步传输。缺点是实现复杂，需要精确的功率控制。CDM广泛应用于CDMA移动通信系统。码分多址（CDMA）是CDM在多址通信中的应用，是3G移动通信系统的核心技术。",
                    "",
                    "## 第十章 通信网",
                    "",
                    "通信网是由多个通信节点和传输链路组成的网络，实现用户之间的信息交换。通信网的基本功能包括传输、交换、接入等。现代通信网包括电话网、数据网、移动通信网、互联网等，形成了覆盖全球的通信基础设施。",
                    "",
                    "### 10.1 通信网的基本结构",
                    "",
                    "通信网的基本结构包括星型、总线型、环型和网状型。星型结构以中心节点为核心，所有节点都与中心节点相连，优点是结构简单、易于管理，缺点是中心节点故障会导致全网瘫痪。总线型结构所有节点共享一条总线，优点是成本低、易于扩展，缺点是总线故障会影响所有节点。环型结构节点形成环形连接，优点是结构简单、易于实现，缺点是单点故障会导致环路中断。网状型结构节点之间有多条连接路径，优点是可靠性高、路由灵活，缺点是成本高、管理复杂。实际通信网通常采用混合结构，结合各种结构的优点。",
                    "",
                    "### 10.2 通信网的性能指标",
                    "",
                    "通信网的性能指标包括时延、吞吐量、可靠性等。时延是数据从源节点到目的节点所需的时间，包括传输时延、传播时延、处理时延和排队时延。吞吐量是网络在单位时间内成功传输的数据量，反映了网络的传输能力。可靠性是网络在故障情况下保持服务的能力，通常用可用性、故障恢复时间等指标来衡量。服务质量（QoS）是网络为不同业务提供不同质量保证的能力，包括带宽、时延、丢包率等参数。",
                    "",
                    "### 10.3 交换技术",
                    "",
                    "交换技术是通信网的核心技术，包括电路交换、报文交换和分组交换。电路交换在通信前建立专用通路，通信期间通路独占，优点是时延小、实时性好，缺点是资源利用率低。报文交换以报文为单位进行存储转发，优点是资源利用率高，缺点是时延大。分组交换将报文分割成固定长度的分组进行传输，结合了电路交换和报文交换的优点，是现代数据网的主流交换方式。ATM（异步传输模式）是一种面向连接的分组交换技术，结合了电路交换和分组交换的优点，广泛应用于宽带综合业务数字网。",
                    "",
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                    "",
                    "**通信原理笔记总结**：",
                    "",
                    "本笔记涵盖了通信原理的核心内容，包括信号与系统基础、模拟调制、数字基带传输、数字带通传输、信源编码、信道编码、同步技术、多路复用和多址技术、通信网等主要章节。每个章节都包含了基本概念、原理分析、性能评估和应用实例，为深入理解现代通信系统提供了理论基础。",
                    "",
                    "通信原理是电子信息工程、通信工程等专业的重要基础课程，掌握这些知识对于从事通信系统设计、网络规划、信号处理等工作具有重要意义。随着5G、6G等新一代通信技术的发展，通信原理的知识也在不断更新和扩展，需要持续学习和实践。"
                ]
                
                existing_communication = all_documents.get("通信原理笔记", [])
                # 检测通信原理笔记是否包含默认占位文本或内容为空
                communication_needs_init = False
                if "通信原理笔记" not in all_documents:
                    communication_needs_init = True
                elif not existing_communication:
                    communication_needs_init = True
                else:
                    # 检查内容是否太短（少于1000字符）
                    content_str = '\n'.join(existing_communication) if isinstance(existing_communication, list) else str(existing_communication)
                    if len(content_str.strip()) < 1000:
                        communication_needs_init = True
                
                if communication_needs_init:
                    all_documents["通信原理笔记"] = communication_default
                    print(f"[API] 通信原理笔记已初始化（内容长度: {len(' '.join(communication_default))} 字符）")
            
            
            # 最终清理：确保所有文档都不包含默认占位文本
            for title, content in list(all_documents.items()):
                if contains_default(content):
                    print(f"[API] ⚠️ 最终清理：检测到文档 '{title}' 包含默认占位文本，正在清理...")
                    if title == "试用文档":
                        all_documents[title] = [""]  # 试用文档应该是空白的
                    elif title == "PM问答笔记":
                        # PM问答笔记应该包含完整内容，如果检测到默认文本，清空让初始化逻辑重建
                        all_documents[title] = []
                    elif title == "通信原理笔记":
                        # 通信原理笔记应该包含完整内容，如果检测到默认文本，重新初始化
                        # 由于清理逻辑在 else 块之后，无法访问 communication_default，所以重新初始化
                        # 这里先清空，让后续逻辑重新初始化
                        all_documents[title] = []
                    elif title == "介绍文档":
                        # 介绍文档应该包含完整内容，如果检测到默认文本，立即用正确内容替换
                        intro_content = [
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
                            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                            "版本：Beta | 更新：2024-12 | 模型：通义千问3-coder-plus",
                            ""
                        ]
                        all_documents[title] = intro_content
                        # 同时保存到数据库
                        try:
                            if USE_D1 and D1_AVAILABLE:
                                from d1_document_manager import D1DocumentManager
                                d1_manager = D1DocumentManager(d1_database=None, doc_type="dev", session_id=None, dev_mode_enabled=True)
                                await d1_manager.storage.save_document("介绍文档", intro_content, "dev")
                                print(f"[API] 介绍文档已修复并保存到D1数据库")
                        except Exception as e:
                            print(f"[API] 保存介绍文档到D1失败: {e}")
                    else:
                        # 其他文档清空
                        all_documents[title] = []
            
            # 打印返回的文档信息，用于调试
            print(f"[API] 返回文档列表: {list(all_documents.keys())}")
            for title, content in all_documents.items():
                content_preview = str(content)[:100] if content else "空"
                has_default = contains_default(content)
                print(f"[API] 文档 '{title}': 内容预览={content_preview}..., 包含默认文本={has_default}")
            
            return ChatResponse(
                response_type="ALL_DOCUMENTS",
                content="所有笔记内容：",
                new_session_id=session_id if not request.session_id else None,
                dev_mode_enabled=is_dev_mode,
                edit_mode_enabled=is_edit_mode,
                documents=all_documents
            )
        
        # 处理用户输入
        if not user_input:
            raise HTTPException(status_code=400, detail="输入不能为空")
        
        # 注意：编辑权限设计已取消，不再检查开发者模式权限
        # 试用模式和开发者模式都可以执行添加、删除、清空、修改、编辑等操作
        
        # 【优化】优先处理"确认"/"取消"命令，避免调用LLM导致识别错误
        # 如果存在待确认的操作，优先检查是否是明确的确认/取消命令
        if app_instance.pending_action:
            user_input_lower = user_input.lower().strip()
            # 检查是否是明确的确认命令
            if user_input_lower in ['确认', 'confirm', 'yes', 'y', '是', '好的', '好']:
                # 直接处理确认操作，不调用LLM
                action = app_instance.pending_action
                if action["intent"] == "DELETE_CONTENT":
                    app_instance.doc_manager.clear_document(action["title"])
                    doc_title = action["title"]
                    app_instance.pending_action = None
                    
                    # 构建意图信息和工具调用信息
                    intent_info = {
                        "intent": "DELETE_CONTENT",
                        "doc_title": doc_title
                    }
                    tools_used = build_tools_used("DELETE_CONTENT", is_dev_mode, use_cloudflare=False, use_d1=False)
                    
                    return ChatResponse(
                        response_type="TEXT",
                        content=f"✅ 已成功清空文档 '{doc_title}' 的所有内容。",
                        new_session_id=session_id if not request.session_id else None,
                        intent_info=intent_info,
                        tools_used=tools_used
                    )
            # 检查是否是明确的取消命令
            elif user_input_lower in ['取消', 'cancel', 'no', 'n', '否', '不']:
                action = app_instance.pending_action
                app_instance.pending_action = None
                return ChatResponse(
                    response_type="TEXT",
                    content=f"❌ 已取消清空文档 '{action['title']}' 的操作。",
                    new_session_id=session_id if not request.session_id else None
                )
        
        # 调用SmartClipLLM的意图识别和处理逻辑
        # 我们需要模拟run()方法中的处理流程，但不使用input()，而是直接处理
        
        # 检查LLM配置
        if not app_instance.intent_recognizer.client_config:
            print("[API错误] LLM客户端配置未初始化！")
            print(f"[API错误] client_config: {app_instance.intent_recognizer.client_config}")
            print("[API错误] 这会导致所有LLM调用失败，返回UNKNOWN意图")
            # 返回明确的错误提示
            return ChatResponse(
                response_type="UNKNOWN",
                content="⚠️ LLM配置未初始化，无法连接大语言模型。请检查后端日志中的配置信息。",
                new_session_id=session_id if not request.session_id else None,
                message_style="error"
            )
        
        try:
            print(f"[API] 开始调用LLM识别意图，用户输入: {user_input}")
            print(f"[API] LLM配置状态: api_key={'已设置' if app_instance.intent_recognizer.client_config.get('api_key') else '未设置'}, app_id={'已设置' if app_instance.intent_recognizer.client_config.get('app_id') else '未设置'}")
            intent_data = app_instance.intent_recognizer.recognize(user_input)
            
            print(f"[API] LLM返回意图: {intent_data.get('intent', 'N/A')}")
            print(f"[API] LLM返回intent_type: {intent_data.get('intent_type', 'N/A')}")
            print(f"[API] LLM返回原始intent_data: {intent_data}")
            print(f"[API] LLM返回intent_data的所有keys: {list(intent_data.keys())}")
            print(f"[API] LLM返回intent_data中intent_type的类型: {type(intent_data.get('intent_type'))}")
            print(f"[API] LLM返回intent_data中intent_type的值是否为None: {intent_data.get('intent_type') is None}")
            
            # 检查是否是LLM连接错误
            if intent_data.get("intent") == "LLM_CONNECTION_ERROR":
                return ChatResponse(
                    response_type="UNKNOWN",
                    content=intent_data.get("content", "⚠️ 大语言模型连接失败，请检查后端配置。"),
                    new_session_id=session_id if not request.session_id else None,
                    message_style="error"
                )
        except Exception as e:
            # 如果意图识别失败，返回UNKNOWN意图而不是500错误
            import traceback
            error_detail = str(e)
            print(f"[意图识别错误] {error_detail}")
            print(traceback.format_exc())
            # 返回UNKNOWN意图，让用户知道无法理解指令
            # 增加连续无法理解的计数
            unknown_count = unknown_count_sessions.get(session_id, 0)
            unknown_count += 1
            unknown_count_sessions[session_id] = unknown_count
            
            # 如果连续3次无法理解，返回警告消息（黄色气泡）
            if unknown_count >= 3:
                # 重置计数
                unknown_count_sessions[session_id] = 0
                intent_data = {
                    "intent": "UNKNOWN",
                    "intent_type": "UNKNOWN",
                    "content": "对于这个失误，灵辑感到很抱歉。\n\n灵辑团队已经收到您对于灵辑使用上的障碍问题，并承诺进行改进。\n\n如果您能提供更多关于您想要实现的功能的信息，这将帮助我们更好地为您服务。",
                    "message_style": "warning"
                }
            else:
                intent_data = {
                    "intent": "UNKNOWN",
                    "intent_type": "UNKNOWN",
                    "content": "抱歉，我无法理解您的指令。请尝试使用更清晰的表达，或者告诉我您想要做什么。",
                    "message_style": "error"
                }
        
        # 检查是否是LLM连接错误
        if intent_data.get("intent") == "LLM_CONNECTION_ERROR":
            return ChatResponse(
                response_type="UNKNOWN",
                content=intent_data.get("content", "⚠️ 大语言模型连接失败，请检查后端配置。"),
                new_session_id=session_id if not request.session_id else None,
                message_style="error"
            )
        
        # 检查是否需要确认
        confirmation_needed = intent_data.get("confirmation_needed", False)
        # 优先使用 intent_type（如果存在且不是 UNKNOWN），否则使用 intent
        intent_type_value = intent_data.get("intent_type")
        intent_value = intent_data.get("intent")
        
        print(f"[意图识别] 提取intent_type_value: {intent_type_value}, 类型: {type(intent_type_value)}, 是否为None: {intent_type_value is None}")
        print(f"[意图识别] 提取intent_value: {intent_value}, 类型: {type(intent_value)}")
        
        # 关键修复：确保 intent_type 被正确使用
        if intent_type_value is not None and str(intent_type_value).strip().upper() != "UNKNOWN":
            intent = str(intent_type_value).strip().upper()
            print(f"[意图识别] 使用intent_type作为最终意图: {intent}")
        elif intent_value:
            intent = intent_value
            print(f"[意图识别] 使用intent作为最终意图: {intent}")
        else:
            intent = "UNKNOWN"
            print(f"[意图识别] 使用默认UNKNOWN")
        
        print(f"[意图识别] 最终使用的意图: {intent} (intent字段: {intent_value}, intent_type字段: {intent_type_value})")
        
        # 处理不同类型的意图
        if intent == "CONFIRM":
            # 用户确认操作
            if not app_instance.pending_action:
                return ChatResponse(
                    response_type="TEXT",
                    content="❌ 确认操作失败：没有待确认的操作。请先添加内容，然后进行确认。",
                    new_session_id=session_id if not request.session_id else None,
                    dev_mode_enabled=is_dev_mode,
                    edit_mode_enabled=get_edit_mode_enabled(app_instance, cloudflare_manager),
                    message_style="error"
                )
            
                # 执行待确认的操作
                action = app_instance.pending_action
            # 检查 action 是否为字典且包含 intent 键
            if not isinstance(action, dict) or "intent" not in action:
                print(f"[错误] pending_action 格式不正确: {action}, 类型: {type(action)}")
                app_instance.pending_action = None
                return ChatResponse(
                    response_type="TEXT",
                    content="❌ 确认操作失败：待确认的操作信息格式不正确。请重新尝试添加内容。",
                    new_session_id=session_id if not request.session_id else None,
                    dev_mode_enabled=is_dev_mode,
                    edit_mode_enabled=get_edit_mode_enabled(app_instance, cloudflare_manager),
                    message_style="error"
                )
            
            action_intent = action.get("intent")
            
            if action_intent == "DELETE_CONTENT":
                # 删除文档内容
                doc_title = action.get("title")
                if not doc_title:
                    app_instance.pending_action = None
                    return ChatResponse(
                        response_type="TEXT",
                        content="❌ 确认操作失败：待确认的操作缺少文档标题。",
                        new_session_id=session_id if not request.session_id else None,
                        dev_mode_enabled=is_dev_mode,
                        edit_mode_enabled=get_edit_mode_enabled(app_instance, cloudflare_manager),
                        message_style="error"
                    )
                
                app_instance.doc_manager.clear_document(doc_title)
                app_instance.pending_action = None
                
                # 构建意图信息和工具调用信息
                intent_info = {
                    "intent": "DELETE_CONTENT",
                    "doc_title": doc_title
                }
                tools_used = build_tools_used("DELETE_CONTENT", is_dev_mode, use_cloudflare=False, use_d1=False)
                
                return ChatResponse(
                    response_type="TEXT",
                    content=f"✅ 已成功清空文档 '{doc_title}' 的所有内容。",
                    new_session_id=session_id if not request.session_id else None,
                    dev_mode_enabled=is_dev_mode,
                    edit_mode_enabled=get_edit_mode_enabled(app_instance, cloudflare_manager),
                    intent_info=intent_info,
                    tools_used=tools_used
                )
            
            elif action_intent == "ADD_CONTENT":
                # 添加内容到文档
                doc_title = action.get("doc_title")
                content = action.get("content")
                position = action.get("position", "end")
                section = action.get("section")
                subsection = action.get("subsection")
                intent_data_from_action = action.get("intent_data", {})
                
                if not doc_title or not content:
                    app_instance.pending_action = None
                    return ChatResponse(
                        response_type="TEXT",
                        content="❌ 确认操作失败：待确认的操作缺少必要信息（文档标题或内容）。",
                        new_session_id=session_id if not request.session_id else None,
                        dev_mode_enabled=is_dev_mode,
                        edit_mode_enabled=get_edit_mode_enabled(app_instance, cloudflare_manager),
                        message_style="error"
                    )
                
                # 确保position不为None
                if position is None:
                    position = "end"
                
                # 注意：修改权限设计已取消，不再检查修改权限
                
                try:
                    # 如果使用 Cloudflare 存储
                    if USE_CLOUDFLARE and CLOUDFLARE_AVAILABLE and CLOUDFLARE_KV and is_dev_mode:
                        try:
                            if cloudflare_manager is None:
                                cloudflare_manager = CloudflareDocumentManager(CLOUDFLARE_KV, True)
                                await cloudflare_manager.initialize()
                            await cloudflare_manager.add_content(doc_title, content, position, section=section, subsection=subsection)
                            # 同步到本地实例
                            app_instance.doc_manager.documents[doc_title] = cloudflare_manager.documents.get(doc_title, [])
                        except Exception as e:
                            print(f"[错误] Cloudflare 存储操作失败: {e}")
                            # 检查方法是否支持 section 和 subsection 参数
                            import inspect
                            try:
                                sig = inspect.signature(app_instance.doc_manager.add_content)
                                params = list(sig.parameters.keys())
                                if 'section' in params and 'subsection' in params:
                                    app_instance.doc_manager.add_content(doc_title, content, position, section=section, subsection=subsection)
                                else:
                                    print(f"[警告] DocumentManager.add_content 不支持 section/subsection 参数，使用旧方式调用")
                                    app_instance.doc_manager.add_content(doc_title, content, position)
                            except Exception as check_error:
                                print(f"[错误] 检查方法签名失败: {check_error}")
                                app_instance.doc_manager.add_content(doc_title, content, position)
                    else:
                        # 使用本地存储，支持智能归类
                        # 检查方法是否支持 section 和 subsection 参数
                        import inspect
                        try:
                            sig = inspect.signature(app_instance.doc_manager.add_content)
                            params = list(sig.parameters.keys())
                            if 'section' in params and 'subsection' in params:
                                # 方法支持新参数，使用新方式调用
                                app_instance.doc_manager.add_content(doc_title, content, position, section=section, subsection=subsection)
                            else:
                                # 方法不支持新参数，使用旧方式调用
                                print(f"[警告] DocumentManager.add_content 不支持 section/subsection 参数，使用旧方式调用")
                                app_instance.doc_manager.add_content(doc_title, content, position)
                        except Exception as check_error:
                            # 检查失败，回退到旧方式
                            print(f"[错误] 检查方法签名失败: {check_error}")
                            app_instance.doc_manager.add_content(doc_title, content, position)
                except Exception as e:
                    # 处理所有可能的异常
                    print(f"[错误] 添加内容时发生异常: {e}")
                    import traceback
                    traceback.print_exc()
                
                # 清空待确认的操作
                app_instance.pending_action = None
                
                # 构建响应消息
                if section:
                    response_content = f"✅ 已将内容添加到文档 '{doc_title}' 的 '{section}' 部分"
                    if subsection:
                        response_content += f"（{subsection}）"
                else:
                    response_content = f"✅ 已成功将内容添加到文档 '{doc_title}' 的{('开头' if position.lower() == 'start' else '结尾')}。"
                
                # 构建意图信息和工具调用信息
                intent_info = build_intent_info(intent_data_from_action, "ADD_CONTENT")
                tools_used = build_tools_used("ADD_CONTENT", is_dev_mode, use_cloudflare=(USE_CLOUDFLARE and CLOUDFLARE_AVAILABLE and CLOUDFLARE_KV), use_d1=False)
                
                return ChatResponse(
                    response_type="TEXT",
                    content=response_content,
                    new_session_id=session_id if not request.session_id else None,
                    dev_mode_enabled=is_dev_mode,
                    edit_mode_enabled=get_edit_mode_enabled(app_instance, cloudflare_manager),
                    intent_info=intent_info,
                    tools_used=tools_used
                )
            
            else:
                # 未知的待确认操作类型
                print(f"[错误] 未知的待确认操作类型: {action_intent}")
                app_instance.pending_action = None
                return ChatResponse(
                    response_type="TEXT",
                    content=f"❌ 确认操作失败：未知的操作类型 '{action_intent}'。",
                    new_session_id=session_id if not request.session_id else None,
                    dev_mode_enabled=is_dev_mode,
                    edit_mode_enabled=get_edit_mode_enabled(app_instance, cloudflare_manager),
                    message_style="error"
                )
        
        elif intent == "CANCEL":
            # 用户取消操作
            # 首先检查是否有待取消的新建文档操作
            if session_id in pending_new_doc_actions:
                action = pending_new_doc_actions[session_id]
                original_doc_title = action.get("original_doc_title", "当前文档")
                del pending_new_doc_actions[session_id]
                return ChatResponse(
                    response_type="TEXT",
                    content=f"已取消创建新文档的操作。内容将添加到原文档 '{original_doc_title}'。",
                    new_session_id=session_id if not request.session_id else None,
                    dev_mode_enabled=is_dev_mode,
                    edit_mode_enabled=is_edit_mode
                )
            
            # 检查是否有其他待取消的操作
            if app_instance.pending_action:
                action = app_instance.pending_action
                app_instance.pending_action = None
                return ChatResponse(
                    response_type="TEXT",
                    content=f"已取消清空文档 '{action['title']}' 的操作。",
                    new_session_id=session_id if not request.session_id else None
                )
            else:
                return ChatResponse(
                    response_type="TEXT",
                    content="没有待确认的操作。",
                    new_session_id=session_id if not request.session_id else None
                )
        
        elif intent == "GREETING":
            # 问候消息处理
            content = intent_data.get("content_to_process") or intent_data.get("content", "你好！我是灵辑，你的智能笔记助手。有什么可以帮你的吗？")
            message_style = intent_data.get("message_style", "normal")
            
            # 构建意图信息和工具调用信息
            intent_info = build_intent_info(intent_data, intent)
            tools_used = build_tools_used(intent, is_dev_mode, False, False)
            
            return ChatResponse(
                response_type="TEXT",
                content=content,
                new_session_id=session_id if not request.session_id else None,
                dev_mode_enabled=is_dev_mode,
                edit_mode_enabled=is_edit_mode,
                message_style=message_style,
                intent_info=intent_info,
                tools_used=tools_used
                )
        
        elif intent == "DELETE_CONTENT" and confirmation_needed:
            # 需要确认的删除操作
            doc_title = intent_data.get("doc_title") or app_instance.doc_manager.active_doc_title
            
            # 判断是否是试用模式（通过session_id判断）
            is_trial_mode = session_id and session_id.startswith('trial_')
            
            # 根据模式生成不同的确认消息
            if is_trial_mode:
                confirmation_message = f"您确定要清空文档 '{doc_title}' 的所有内容吗？\n\n⚠️ 试用模式下删除无法恢复。"
            else:
                confirmation_message = f"您确定要清空文档 '{doc_title}' 的所有内容吗？此操作不可恢复。"
            
            app_instance.pending_action = {
                "intent": "DELETE_CONTENT",
                "title": doc_title
            }
            return ChatResponse(
                response_type="CONFIRMATION",
                content=confirmation_message,
                new_session_id=session_id if not request.session_id else None,
                dev_mode_enabled=is_dev_mode,
                edit_mode_enabled=get_edit_mode_enabled(app_instance, cloudflare_manager)
            )
        
        elif intent == "DELETE_CONTENT":
            # 直接删除（不需要确认的情况，理论上不应该发生，但保留作为兜底）
            doc_title = intent_data.get("doc_title") or app_instance.doc_manager.active_doc_title
            
            # 注意：修改权限设计已取消，不再检查修改权限
            
            # 如果使用 Cloudflare 存储，使用云端管理器
            # 注意：修改权限设计已取消，不再检查修改权限
            if USE_CLOUDFLARE and CLOUDFLARE_AVAILABLE and CLOUDFLARE_KV and is_dev_mode:
                try:
                    if cloudflare_manager is None:
                        cloudflare_manager = CloudflareDocumentManager(CLOUDFLARE_KV, True)
                        await cloudflare_manager.initialize()
                    # 不再调用 enable_edit_mode()，因为编辑权限设计已取消
                    await cloudflare_manager.clear_document(doc_title)
                    # 同步到本地实例
                    app_instance.doc_manager.documents[doc_title] = []
                except Exception as e:
                    print(f"[错误] Cloudflare 存储操作失败: {e}")
                    app_instance.doc_manager.clear_document(doc_title)
            else:
                app_instance.doc_manager.clear_document(doc_title)
            
            # 构建意图信息和工具调用信息
            intent_info = build_intent_info(intent_data, intent)
            tools_used = build_tools_used(
                intent,
                is_dev_mode,
                use_cloudflare=(USE_CLOUDFLARE and CLOUDFLARE_AVAILABLE and CLOUDFLARE_KV and is_dev_mode),
                use_d1=False
            )
            
            return ChatResponse(
                response_type="TEXT",
                content=f"已成功清空文档 '{doc_title}' 的所有内容。",
                new_session_id=session_id if not request.session_id else None,
                dev_mode_enabled=is_dev_mode,
                edit_mode_enabled=is_edit_mode,
                intent_info=intent_info,
                tools_used=tools_used
            )
        
        elif intent == "ADD_CONTENT":
            # 添加内容
            print(f"[ADD_CONTENT] 开始处理 ADD_CONTENT 意图")
            
            # 检查是否是碎片信息引导处理
            system_action = intent_data.get("system_action_required", "")
            if system_action == "GUIDE_FRAGMENT_COMPLETION":
                # 碎片信息引导处理：不执行添加操作，只返回引导消息
                content = intent_data.get("content", "") or intent_data.get("content_to_process", "")
                if not content:
                    content = "请提供完整的笔记内容，我会帮您记录到相应的文档中。"
                
                intent_info = build_intent_info(intent_data, intent)
                tools_used = build_tools_used(intent, is_dev_mode, False, False)
                
                return ChatResponse(
                    response_type="TEXT",
                    content=content,
                    new_session_id=session_id if not request.session_id else None,
                    dev_mode_enabled=is_dev_mode,
                    edit_mode_enabled=get_edit_mode_enabled(app_instance, cloudflare_manager),
                    intent_info=intent_info,
                    tools_used=tools_used,
                    message_style=intent_data.get("message_style", "normal")
                )
            
            # 获取内容
            content = intent_data.get("content", "") or intent_data.get("content_to_process", "")
            position = intent_data.get("position", "end")
            section = intent_data.get("suggested_section")
            subsection = intent_data.get("suggested_subsection")
            
            print(f"[ADD_CONTENT] 内容: {content[:50]}..., position: {position}, section: {section}, subsection: {subsection}")
            
            # 优先使用当前活动文档，除非用户明确指定了文档名
            # 判断逻辑：
            # 1. 如果 LLM 返回的文档名与当前活动文档相同，使用它
            # 2. 如果 LLM 返回的文档名是默认文档之一，使用它（用户可能明确指定了）
            # 3. 如果 LLM 返回的文档名不在现有文档列表中，说明是 LLM 自动推断的，使用当前活动文档
            # 4. 如果 LLM 返回的文档名与当前活动文档不同，且不是默认文档，使用当前活动文档
            llm_doc_title = intent_data.get("doc_title") or intent_data.get("target_document")  # 保存 LLM 原始建议的文档名，用于后续匹配检查
            active_doc_title = app_instance.doc_manager.active_doc_title
            available_docs = app_instance.doc_manager.get_document_titles()
            
            # 默认文档列表（这些文档是系统预设的，用户可能明确指定）
            default_docs = ["试用文档", "PM问答笔记", "介绍文档", "更新记录日志"]
            
            if llm_doc_title and llm_doc_title == active_doc_title:
                # LLM 返回的文档名与当前活动文档相同，使用它
                doc_title = llm_doc_title
            elif llm_doc_title and llm_doc_title in default_docs:
                # LLM 返回的文档名是默认文档之一，使用它（用户可能明确指定了）
                doc_title = llm_doc_title
            elif llm_doc_title and llm_doc_title not in available_docs:
                # LLM 返回的文档名不在现有文档列表中，说明是 LLM 自动推断的，使用当前活动文档
                doc_title = active_doc_title
                print(f"[文档选择] LLM 建议的文档 '{llm_doc_title}' 不存在，使用当前活动文档 '{doc_title}'")
            elif llm_doc_title and llm_doc_title != active_doc_title:
                # LLM 返回的文档名存在但与当前活动文档不同，且不是默认文档，说明是 LLM 自动推断的，使用当前活动文档
                doc_title = active_doc_title
                print(f"[文档选择] LLM 建议的文档 '{llm_doc_title}' 是自动推断的，使用当前活动文档 '{doc_title}'")
            else:
                # 其他情况，使用当前活动文档
                doc_title = active_doc_title
            
            # 保存 LLM 原始建议的文档名，用于后续匹配检查
            llm_suggested_doc = llm_doc_title
            
            # 注意：修改权限设计已取消，试用模式和开发者模式都可以直接添加内容
            # 不再检查修改权限
            
            # 确保position不为None
            if position is None:
                position = "end"
            
            # 文档匹配检查（如果 LLM 建议的文档不存在，或者与当前活动文档不同，需要确认）
            print(f"[ADD_CONTENT] DOCUMENT_MATCHER_AVAILABLE: {DOCUMENT_MATCHER_AVAILABLE}, DocumentMatcher: {DocumentMatcher}")
            if DOCUMENT_MATCHER_AVAILABLE and DocumentMatcher:
                # 获取当前活动文档信息（用于匹配检查）
                active_doc_content = app_instance.doc_manager.get_document(active_doc_title)
                
                # 处理不同的返回类型：可能是列表、字符串或None
                if active_doc_content is None:
                    is_empty = True
                    print(f"[文档匹配检查] 文档内容为 None，视为空文档")
                elif isinstance(active_doc_content, list):
                    # 如果是列表，检查是否为空或只包含空字符串
                    is_empty = len(active_doc_content) == 0 or all(not str(item).strip() for item in active_doc_content)
                    print(f"[文档匹配检查] 文档内容为列表，长度: {len(active_doc_content)}, 是否为空: {is_empty}")
                else:
                    # 如果是字符串或其他类型
                    is_empty = not str(active_doc_content).strip()
                    print(f"[文档匹配检查] 文档内容为字符串，长度: {len(str(active_doc_content))}, 是否为空: {is_empty}")
                
                # 检查当前活动文档与内容的匹配度
                active_doc_type = DocumentMatcher.get_document_type(active_doc_title)
                content_type = DocumentMatcher.get_content_type(str(content))
                match_degree = DocumentMatcher.check_match(active_doc_type, content_type, is_empty)
                
                print(f"[文档匹配检查] 当前活动文档类型: {active_doc_type}, 内容类型: {content_type}, 匹配度: {match_degree}")
                
                # 只有当匹配度不是"perfect"时，或者 LLM 建议的文档不存在/与当前活动文档不同时，才需要确认
                needs_confirmation = False
                
                # 情况1：LLM 建议的文档不存在
                if llm_suggested_doc and llm_suggested_doc not in available_docs:
                    needs_confirmation = True
                    print(f"[文档匹配检查] LLM 建议的文档 '{llm_suggested_doc}' 不存在，需要确认")
                
                # 情况2：LLM 建议的文档与当前活动文档不同
                elif llm_suggested_doc and llm_suggested_doc != active_doc_title and llm_suggested_doc not in default_docs:
                    needs_confirmation = True
                    print(f"[文档匹配检查] LLM 建议的文档 '{llm_suggested_doc}' 与当前活动文档 '{active_doc_title}' 不同，需要确认")
                
                # 情况3：匹配度不是"perfect"
                elif match_degree != "perfect":
                    needs_confirmation = True
                    print(f"[文档匹配检查] 匹配度不是'perfect'，需要确认")
                
                if needs_confirmation:
                    # 生成确认消息
                    if llm_suggested_doc and llm_suggested_doc not in available_docs:
                        # LLM 建议的文档不存在，建议新建文档
                        suggested_doc_name = DocumentMatcher.get_suggested_doc_name(content_type) if content_type else llm_suggested_doc
                        # 如果匹配度不是"perfect"，添加匹配判断信息
                        if match_degree != "perfect":
                            match_warning = DocumentMatcher.generate_confirmation_message(
                                active_doc_title, active_doc_type, content_type, match_degree
                            )
                            # 如果生成的消息中没有建议的文档名，添加它
                            if suggested_doc_name and suggested_doc_name not in match_warning:
                                # 消息已经包含了建议的文档名，不需要修改
                                pass
                        else:
                            match_warning = f"⚠️ 文档不存在\n\nLLM 建议的文档「{llm_suggested_doc}」不存在。\n\n确定要加入到当前文档「{active_doc_title}」吗？\n\n我建议您新建一个文档「{suggested_doc_name}」"
                    else:
                        # 匹配度不是"perfect"，生成匹配警告消息
                        match_warning = DocumentMatcher.generate_confirmation_message(
                            active_doc_title, active_doc_type, content_type, match_degree
                        )
                        suggested_doc_name = DocumentMatcher.get_suggested_doc_name(content_type) if content_type else None
                    
                    # 如果 LLM 建议了不同的文档，且该文档不存在，建议新建文档
                    if llm_suggested_doc and llm_suggested_doc != active_doc_title and llm_suggested_doc not in available_docs:
                        # LLM 建议的文档不存在，建议新建文档
                        if not match_warning or "文档不存在" not in match_warning:
                            # 如果还没有生成消息，或者消息中没有"文档不存在"的提示，生成新消息
                            if match_degree != "perfect":
                                match_warning = DocumentMatcher.generate_confirmation_message(
                                    active_doc_title, active_doc_type, content_type, match_degree
                                )
                            else:
                                suggested_doc_name = DocumentMatcher.get_suggested_doc_name(content_type) if content_type else llm_suggested_doc
                                match_warning = f"⚠️ 文档不存在\n\nLLM 建议的文档「{llm_suggested_doc}」不存在。\n\n💡 建议新建文档「{suggested_doc_name}」"
                        suggested_doc_name = DocumentMatcher.get_suggested_doc_name(content_type) if content_type else (suggested_doc_name or llm_suggested_doc)
                    elif not suggested_doc_name:
                        # 如果没有建议的文档名，使用 LLM 建议的文档名
                        suggested_doc_name = llm_suggested_doc
                    
                    # 更新 intent_data
                    intent_data["document_type"] = active_doc_type
                    intent_data["content_type"] = content_type
                    intent_data["match_degree"] = match_degree
                    intent_data["match_confirmation_needed"] = True
                    intent_data["match_warning_message"] = match_warning
                    intent_data["suggested_doc_name"] = suggested_doc_name
                    intent_data["system_action_required"] = "ASK_MATCH_CONFIRMATION"
                    intent_data["message_style"] = "warning" if match_degree == "mismatch" else "normal"
                    
                    # 存储待确认的添加操作
                    app_instance.pending_action = {
                        "intent": "ADD_CONTENT",
                        "doc_title": active_doc_title, # 存储当前活动文档
                        "content": content,
                        "position": position,
                        "section": section,
                        "subsection": subsection,
                        "intent_data": intent_data # 存储完整的 intent_data
                    }
                    
                    # 构建意图信息和工具调用信息
                    intent_info = build_intent_info(intent_data, intent)
                    tools_used = build_tools_used(intent, is_dev_mode, False, False)
                    
                    return ChatResponse(
                        response_type="CONFIRMATION",
                        content=match_warning or "是否确认添加此内容？",
                        new_session_id=session_id if not request.session_id else None,
                        dev_mode_enabled=is_dev_mode,
                        match_confirmation_needed=True,
                        match_warning_message=match_warning,
                        suggested_doc_title=suggested_doc_name,
                        intent_info=intent_info,
                        tools_used=tools_used,
                        edit_mode_enabled=get_edit_mode_enabled(app_instance, cloudflare_manager)
                    )
                else:
                    # 匹配度是"perfect"，直接添加到当前活动文档
                    doc_title = active_doc_title
            
            # 如果使用 Cloudflare 存储，使用云端管理器
            if USE_CLOUDFLARE and CLOUDFLARE_AVAILABLE and CLOUDFLARE_KV and is_dev_mode:
                try:
                    if cloudflare_manager is None:
                        cloudflare_manager = CloudflareDocumentManager(CLOUDFLARE_KV, True)
                        await cloudflare_manager.initialize()
                    # 注意：修改权限设计已取消，不再调用 enable_edit_mode()
                    await cloudflare_manager.add_content(doc_title, content, position, section=section, subsection=subsection)
                    # 同步到本地实例
                    app_instance.doc_manager.documents[doc_title] = cloudflare_manager.documents.get(doc_title, [])
                except Exception as e:
                    print(f"[错误] Cloudflare 存储操作失败: {e}")
                    # 降级到本地存储，支持智能归类
                    import inspect
                    try:
                        sig = inspect.signature(app_instance.doc_manager.add_content)
                        params = list(sig.parameters.keys())
                        if 'section' in params and 'subsection' in params:
                            app_instance.doc_manager.add_content(doc_title, content, position, section=section, subsection=subsection)
                        else:
                            print(f"[警告] DocumentManager.add_content 不支持 section/subsection 参数，使用旧方式调用")
                            app_instance.doc_manager.add_content(doc_title, content, position)
                    except Exception as check_error:
                        print(f"[错误] 检查方法签名失败: {check_error}")
                        app_instance.doc_manager.add_content(doc_title, content, position)
            else:
                # 使用本地存储，支持智能归类
                import inspect
                try:
                    sig = inspect.signature(app_instance.doc_manager.add_content)
                    params = list(sig.parameters.keys())
                    if 'section' in params and 'subsection' in params:
                        # 方法支持新参数，使用新方式调用
                        app_instance.doc_manager.add_content(doc_title, content, position, section=section, subsection=subsection)
                    else:
                        # 方法不支持新参数，使用旧方式调用
                        print(f"[警告] DocumentManager.add_content 不支持 section/subsection 参数，使用旧方式调用")
                        app_instance.doc_manager.add_content(doc_title, content, position)
                except Exception as check_error:
                    # 检查失败，回退到旧方式
                    print(f"[错误] 检查方法签名失败: {check_error}")
                    app_instance.doc_manager.add_content(doc_title, content, position)
            
            # 构建意图信息和工具调用信息
            intent_info = build_intent_info(intent_data, intent)
            tools_used = build_tools_used(
                intent, 
                is_dev_mode, 
                use_cloudflare=(USE_CLOUDFLARE and CLOUDFLARE_AVAILABLE and CLOUDFLARE_KV and is_dev_mode),
                use_d1=False
            )
            
            return ChatResponse(
                response_type="TEXT",
                content=f"已成功将内容添加到文档 '{doc_title}' 的{('开头' if position.lower() == 'start' else '结尾')}。",
                new_session_id=session_id if not request.session_id else None,
                dev_mode_enabled=is_dev_mode,
                edit_mode_enabled=is_edit_mode,
                intent_info=intent_info,
                tools_used=tools_used
            )
        
        elif intent == "CREATE_DOCUMENT" or (intent == "ADD_CONTENT" and "创建文档" in user_input):
            # 创建新文档
            # 从用户输入中提取文档名称
            doc_title = None
            if "创建文档" in user_input:
                # 提取"创建文档"后面的内容作为文档名称
                match = re.search(r'创建文档\s+(.+)', user_input)
                if match:
                    doc_title = match.group(1).strip()
            
            # 如果无法从输入中提取，尝试从intent_data获取
            if not doc_title:
                doc_title = intent_data.get("target_document") or intent_data.get("doc_title")
            
            if not doc_title:
                return ChatResponse(
                    response_type="TEXT",
                    content="❌ 请提供要创建的文档名称。例如：创建文档 项目笔记",
                    new_session_id=session_id if not request.session_id else None,
                    dev_mode_enabled=is_dev_mode,
                    edit_mode_enabled=is_edit_mode
                )
            
            # 检查文档名称长度
            if len(doc_title) > 10:
                return ChatResponse(
                    response_type="TEXT",
                    content="❌ 文档名称不能超过10个字符。",
                    new_session_id=session_id if not request.session_id else None,
                    dev_mode_enabled=is_dev_mode,
                    edit_mode_enabled=is_edit_mode
                )
            
            # 检查文档是否已存在
            try:
                if doc_title in app_instance.doc_manager.documents:
                    return ChatResponse(
                        response_type="TEXT",
                        content=f"❌ 文档 '{doc_title}' 已存在，请使用其他名称。",
                        new_session_id=session_id if not request.session_id else None,
                        dev_mode_enabled=is_dev_mode,
                        edit_mode_enabled=is_edit_mode
                    )
            except Exception as e:
                print(f"[警告] 检查文档是否存在时出错: {e}")
                import traceback
                print(traceback.format_exc())
                # 继续执行，不阻止创建文档
            
            try:
                # 创建新文档（空内容）
                empty_content = []
                
                # 必须保存到 D1 数据库，不能使用本地存储
                if not (USE_D1 and D1_AVAILABLE and D1_DATABASE_ID):
                    return ChatResponse(
                        response_type="TEXT",
                        content="❌ D1 数据库未配置或不可用，无法创建文档。请检查 D1 数据库配置。",
                        new_session_id=session_id if not request.session_id else None,
                        dev_mode_enabled=is_dev_mode,
                        edit_mode_enabled=is_edit_mode,
                        message_style="error"
                    )
                
                # 使用 D1 数据库保存到数据库
                try:
                    from d1_document_manager import D1DocumentManager
                    from d1_storage import D1Storage
                    doc_type = "dev" if is_dev_mode else "trial"
                    
                    # 创建 D1Storage 实例检查 D1 数据库是否可用
                    d1_storage = D1Storage(d1_database=None)
                    if not d1_storage.is_d1:
                        # 本地测试环境：允许使用本地存储，但提示这只是测试
                        # 生产环境必须部署到 Cloudflare Workers 才能使用 D1 数据库
                        app_instance.doc_manager.documents[doc_title] = empty_content
                        print(f"[本地测试] 创建文档 '{doc_title}'（使用本地存储，仅用于测试）")
                        return ChatResponse(
                            response_type="TEXT",
                            content=f"⚠️ 本地测试模式：文档 '{doc_title}' 已创建（使用本地存储）。\n\n注意：本地测试环境无法访问 D1 数据库，数据仅保存在内存中，刷新页面后会丢失。\n\n生产环境请部署到 Cloudflare Workers 以使用 D1 数据库永久存储。",
                            new_session_id=session_id if not request.session_id else None,
                            dev_mode_enabled=is_dev_mode,
                            edit_mode_enabled=is_edit_mode,
                            message_style="warning"
                        )
                    
                    # 在 FastAPI 环境中，d1_database=None，但 D1Storage 会使用数据库 ID
                    d1_manager = D1DocumentManager(
                        d1_database=None,  # FastAPI 环境中没有真实的 D1 对象
                        doc_type=doc_type,
                        session_id=session_id,
                        dev_mode_enabled=is_dev_mode
                    )
                    await d1_manager.initialize()
                    
                    # 创建空文档：直接使用 save_document 方法，而不是 add_content
                    # 这样可以避免权限检查（创建新文档不需要修改权限）
                    success = await d1_manager.storage.save_document(doc_title, empty_content, doc_type, session_id)
                    
                    if not success:
                        return ChatResponse(
                            response_type="TEXT",
                            content="❌ D1 数据库保存文档失败。请检查 D1 数据库连接和权限配置。",
                            new_session_id=session_id if not request.session_id else None,
                            dev_mode_enabled=is_dev_mode,
                            edit_mode_enabled=is_edit_mode,
                            message_style="error"
                        )
                    
                    # 更新本地文档列表（仅用于同步显示）
                    d1_manager.documents[doc_title] = empty_content
                    app_instance.doc_manager.documents[doc_title] = empty_content
                    
                    print(f"[成功] D1 数据库创建文档成功: {doc_title}")
                    
                    # 构建意图信息和工具调用信息
                    intent_info = build_intent_info(intent_data, intent)
                    tools_used = build_tools_used(intent, is_dev_mode, use_cloudflare=False, use_d1=True)
                    
                    return ChatResponse(
                        response_type="TEXT",
                        content=f"✅ 成功创建文档 '{doc_title}'！",
                        new_session_id=session_id if not request.session_id else None,
                        dev_mode_enabled=is_dev_mode,
                        edit_mode_enabled=is_edit_mode,
                        intent_info=intent_info,
                        tools_used=tools_used
                    )
                    
                except Exception as e:
                    import traceback
                    error_detail = str(e)
                    print(f"[错误] D1 数据库创建文档失败: {error_detail}")
                    print(traceback.format_exc())
                    
                    # 返回明确的错误提示
                    error_message = f"❌ D1 数据库创建文档失败：{error_detail}"
                    if "PermissionError" in str(type(e)):
                        error_message = f"❌ 权限错误：{error_detail}"
                    elif "ConnectionError" in str(type(e)) or "连接" in error_detail:
                        error_message = "❌ D1 数据库连接失败。请检查数据库连接配置。"
                    
                    return ChatResponse(
                        response_type="TEXT",
                        content=error_message,
                        new_session_id=session_id if not request.session_id else None,
                        dev_mode_enabled=is_dev_mode,
                        edit_mode_enabled=is_edit_mode,
                        message_style="error"
                    )
                    
            except Exception as e:
                import traceback
                error_detail = str(e)
                print(f"[创建文档错误] {error_detail}")
                print(traceback.format_exc())
                return ChatResponse(
                    response_type="TEXT",
                    content=f"❌ 创建文档失败：{error_detail}",
                    new_session_id=session_id if not request.session_id else None,
                    dev_mode_enabled=is_dev_mode,
                    edit_mode_enabled=is_edit_mode,
                    message_style="error"
                )
        
        elif intent == "SET_ACTIVE":
            # 切换文档
            doc_title = intent_data.get("doc_title")
            if doc_title:
                app_instance.doc_manager.set_active_document(doc_title)
                return ChatResponse(
                    response_type="TEXT",
                    content=f"已切换到文档：{doc_title}",
                    new_session_id=session_id if not request.session_id else None
                )
            else:
                return ChatResponse(
                    response_type="TEXT",
                    content="未指定要切换的文档。",
                    new_session_id=session_id if not request.session_id else None
                )
        
        elif intent == "DISPLAY_DOC":
            # 显示文档内容
            doc_title = intent_data.get("doc_title") or app_instance.doc_manager.active_doc_title
            
            # 如果使用 Cloudflare 存储，从云端加载
            if USE_CLOUDFLARE and CLOUDFLARE_AVAILABLE and CLOUDFLARE_KV:
                try:
                    cloudflare_manager = CloudflareDocumentManager(CLOUDFLARE_KV, is_dev_mode)
                    await cloudflare_manager.initialize()
                    doc_content = cloudflare_manager.documents.get(doc_title)
                    # 同步到本地实例
                    if doc_content:
                        app_instance.doc_manager.documents[doc_title] = doc_content
                except Exception as e:
                    print(f"[警告] Cloudflare 存储读取失败: {e}")
                    doc_content = app_instance.doc_manager.documents.get(doc_title)
            else:
                doc_content = app_instance.doc_manager.documents.get(doc_title)
            
            # 如果文档不存在，检查是否是默认文档，如果是则初始化完整内容
            if doc_title not in app_instance.doc_manager.documents or not doc_content:
                # 检查是否是默认文档，如果是则初始化完整内容
                if doc_title == "通信原理笔记":
                    print(f"[文档管理] 文档 '通信原理笔记' 不存在，正在初始化完整内容...")
                    # 从文件加载，如果文件不存在则初始化
                    communication_file = app_instance.doc_manager._get_document_file("通信原理笔记")
                    if not communication_file.exists():
                        # 初始化通信原理笔记的完整内容
                        try:
                            app_instance.doc_manager._initialize_default_documents()
                        except AttributeError:
                            # 如果方法不存在，重新加载文档（可能文件已存在）
                            app_instance.doc_manager._load_documents()
                        # 重新获取文档内容
                        doc_content = app_instance.doc_manager.documents.get(doc_title)
                    else:
                        # 文件存在但内存中没有，重新加载
                        app_instance.doc_manager._load_documents()
                        doc_content = app_instance.doc_manager.documents.get(doc_title)
                elif doc_title == "PM问答笔记":
                    print(f"[文档管理] 文档 'PM问答笔记' 不存在，正在初始化完整内容...")
                    # 从文件加载，如果文件不存在则初始化
                    pm_file = app_instance.doc_manager._get_document_file("PM问答笔记")
                    if not pm_file.exists():
                        # 初始化PM问答笔记的完整内容
                        try:
                            app_instance.doc_manager._initialize_default_documents()
                        except AttributeError:
                            # 如果方法不存在，重新加载文档（可能文件已存在）
                            app_instance.doc_manager._load_documents()
                        # 重新获取文档内容
                        doc_content = app_instance.doc_manager.documents.get(doc_title)
                    else:
                        # 文件存在但内存中没有，重新加载
                        app_instance.doc_manager._load_documents()
                        doc_content = app_instance.doc_manager.documents.get(doc_title)
                else:
                    # 其他文档，创建空文档
                    print(f"[文档管理] 文档 '{doc_title}' 不存在，自动创建空文档")
                    app_instance.doc_manager.documents[doc_title] = [""]
                    app_instance.doc_manager._save_document(doc_title)
                    doc_content = [""]
            
            if doc_content and len(doc_content) > 0 and any(line.strip() for line in doc_content):
                # 将文档内容列表合并为字符串
                content = '\n'.join(doc_content) if isinstance(doc_content, list) else str(doc_content)
                
                # 构建意图信息和工具调用信息
                intent_info = build_intent_info(intent_data, intent)
                tools_used = build_tools_used(
                    intent,
                    is_dev_mode,
                    use_cloudflare=(USE_CLOUDFLARE and CLOUDFLARE_AVAILABLE and CLOUDFLARE_KV),
                    use_d1=False
                )
                
                return ChatResponse(
                    response_type="DOCUMENT",
                    content=content,
                    new_session_id=session_id if not request.session_id else None,
                    dev_mode_enabled=is_dev_mode,
                    intent_info=intent_info,
                    tools_used=tools_used
                )
            else:
                # 文档为空，返回提示信息
                intent_info = build_intent_info(intent_data, intent)
                tools_used = build_tools_used(intent, is_dev_mode, use_cloudflare=False, use_d1=False)
                
                return ChatResponse(
                    response_type="TEXT",
                    content=f"文档 '{doc_title}' 当前为空，您可以开始添加内容。",
                    new_session_id=session_id if not request.session_id else None,
                    dev_mode_enabled=is_dev_mode,
                    intent_info=intent_info,
                    tools_used=tools_used
                )
        
        elif intent == "SUMMARY":
            # 文档总结功能
            # 调试：输出完整的 intent_data
            print(f"[SUMMARY] 完整的 intent_data: {intent_data}")
            
            doc_title = intent_data.get("doc_title") or app_instance.doc_manager.active_doc_title
            summary_scope = intent_data.get("summary_scope", "full")  # 新增：获取总结范围
            target_chapter = intent_data.get("target_chapter")  # 新增：获取目标章节
            print(f"[SUMMARY] 开始总结文档: {doc_title}, 范围: {summary_scope}, 目标章节: {target_chapter}")
            print(f"[SUMMARY] summary_scope 类型: {type(summary_scope)}, 值: '{summary_scope}'")
            print(f"[SUMMARY] target_chapter 类型: {type(target_chapter)}, 值: '{target_chapter}'")
            
            # 调试信息：检查文档是否存在于文档列表中
            all_docs = list(app_instance.doc_manager.documents.keys())
            print(f"[SUMMARY] 当前文档管理器中的所有文档: {all_docs}")
            print(f"[SUMMARY] 文档 '{doc_title}' 是否存在于documents字典中: {doc_title in app_instance.doc_manager.documents}")
            
            # 如果使用 Cloudflare 存储，从云端加载
            if USE_CLOUDFLARE and CLOUDFLARE_AVAILABLE and CLOUDFLARE_KV:
                try:
                    cloudflare_manager = CloudflareDocumentManager(CLOUDFLARE_KV, is_dev_mode)
                    await cloudflare_manager.initialize()
                    doc_content = cloudflare_manager.documents.get(doc_title)
                    # 同步到本地实例
                    if doc_content:
                        app_instance.doc_manager.documents[doc_title] = doc_content
                        print(f"[SUMMARY] 从Cloudflare加载文档内容，行数: {len(doc_content) if isinstance(doc_content, list) else 'N/A'}")
                except Exception as e:
                    print(f"[警告] Cloudflare 存储读取失败: {e}")
                    # 回退到本地获取
                    doc_content = app_instance.doc_manager.get_document(doc_title)
            else:
                # 使用改进后的 get_document 方法，支持多层回退
                doc_content = app_instance.doc_manager.get_document(doc_title)
                
                # 如果文档不存在或为空，尝试初始化（特别是默认文档）
                if doc_content is None or (isinstance(doc_content, list) and len(doc_content) == 0):
                    print(f"[SUMMARY] 文档 '{doc_title}' 不存在或为空，尝试初始化...")
                    
                    # 检查是否是默认文档，需要初始化完整内容
                    if doc_title == "通信原理笔记":
                        print(f"[SUMMARY] 检测到'通信原理笔记'，正在初始化完整内容...")
                        # 尝试从文件加载
                        doc_file = app_instance.doc_manager._get_document_file("通信原理笔记")
                        if doc_file.exists():
                            try:
                                with open(doc_file, 'r', encoding='utf-8') as f:
                                    content = f.read().strip()
                                    if content:
                                        doc_content = [line for line in content.split('\n')]
                                        app_instance.doc_manager.documents["通信原理笔记"] = doc_content
                                        print(f"[SUMMARY] 从文件加载'通信原理笔记'成功，行数: {len(doc_content)}")
                                    else:
                                        # 文件存在但为空，需要初始化
                                        print(f"[SUMMARY] 文件存在但为空，需要初始化内容")
                                        doc_content = None
                            except Exception as e:
                                print(f"[SUMMARY] 从文件加载失败: {e}")
                                doc_content = None
                        
                        # 如果文件不存在或加载失败，需要初始化完整内容
                        if doc_content is None:
                            print(f"[SUMMARY] 文件不存在或为空，需要初始化'通信原理笔记'的完整内容")
                            # 重新加载所有文档（可能文件刚被创建）
                            app_instance.doc_manager._load_documents()
                            doc_content = app_instance.doc_manager.documents.get("通信原理笔记")
                            
                            # 如果重新加载后还是没有，说明文件确实不存在，需要创建
                            if not doc_content:
                                print(f"[SUMMARY] 重新加载后仍未找到，正在初始化'通信原理笔记'的完整内容...")
                                # 初始化通信原理笔记的完整内容（复制自ADD_CONTENT处理逻辑）
                                communication_default = [
                                    "# 通信原理笔记",
                                    "",
                                    "## 第一章 绪论",
                                    "",
                                    "通信原理是研究信息传输、处理和存储的基本理论和技术。通信系统的基本任务是实现信息的有效传输，确保信息从信源准确、可靠地传送到信宿。现代通信系统已经成为信息社会的基础设施，广泛应用于电话、互联网、广播电视、移动通信等各个领域。",
                                    "",
                                    "### 1.1 通信系统的基本组成",
                                    "",
                                    "通信系统主要由五个基本部分组成：信源、发送设备、信道、接收设备和信宿。信源是产生信息的源头，可以是人、机器或其他信息源。发送设备的作用是将信源产生的信息转换为适合在信道中传输的信号形式，包括编码、调制、放大等功能。信道是信号传输的媒介，可以是导线、光纤、无线电波等。接收设备的作用是接收信道中的信号，并进行解调、解码等处理，恢复出原始信息。信宿是信息的最终接收者。",
                                    "",
                                    "### 1.2 通信系统的分类",
                                    "",
                                    "通信系统可以按照多种方式进行分类。按传输媒介可分为有线通信和无线通信。有线通信使用导线、光纤等物理媒介，具有传输稳定、抗干扰能力强的优点，但需要铺设线路，成本较高。无线通信使用电磁波在空间中传播，具有灵活性强、覆盖范围广的优点，但容易受到干扰。按信号类型可分为模拟通信和数字通信。模拟通信传输的是连续变化的模拟信号，数字通信传输的是离散的数字信号。数字通信具有抗干扰能力强、易于加密、便于存储和处理等优点，已成为现代通信的主流。",
                                    "",
                                    "### 1.3 通信系统的主要性能指标",
                                    "",
                                    "通信系统的主要性能指标包括有效性、可靠性和经济性。有效性是指系统传输信息的速率，通常用信息传输速率或频带利用率来衡量。可靠性是指系统传输信息的准确程度，通常用误码率、误信率等指标来衡量。经济性是指系统的成本效益，包括设备成本、维护成本等。在实际应用中，有效性和可靠性往往存在矛盾，需要在两者之间进行权衡。",
                                    "",
                                    "## 第二章 信号与系统",
                                    "",
                                    "信号是信息的载体，是随时间或空间变化的物理量。系统是对信号进行处理的装置，可以是物理系统或抽象系统。信号与系统理论是通信原理的基础，为分析和设计通信系统提供了数学工具。",
                                    "",
                                    "### 2.1 信号的分类",
                                    "",
                                    "信号可以按照多种方式进行分类。按时间特性可分为连续时间信号和离散时间信号。连续时间信号在任意时刻都有定义，离散时间信号只在某些离散时刻有定义。按周期性可分为周期信号和非周期信号。周期信号满足f(t+T)=f(t)，其中T为周期。按能量特性可分为能量信号和功率信号。能量信号的能量有限，功率信号的功率有限。按确定性可分为确定性信号和随机信号。确定性信号的取值可以精确预测，随机信号的取值具有随机性。",
                                    "",
                                    "### 2.2 系统的特性",
                                    "",
                                    "系统具有多种重要特性。线性性是指系统满足叠加原理，即多个输入信号的线性组合的输出等于各输入信号单独作用时输出的线性组合。时不变性是指系统的特性不随时间变化，即输入信号延迟τ，输出信号也相应延迟τ。因果性是指系统的输出只依赖于当前和过去的输入，不依赖于未来的输入。稳定性是指有界输入产生有界输出。这些特性对于分析和设计通信系统具有重要意义。",
                                    "",
                                    "### 2.3 傅里叶变换",
                                    "",
                                    "傅里叶变换是信号分析的重要工具，它将时域信号转换为频域信号，揭示了信号的频率特性。连续时间信号的傅里叶变换定义为F(ω)=∫f(t)e^(-jωt)dt，离散时间信号的傅里叶变换定义为F(e^(jω))=Σf(n)e^(-jωn)。傅里叶变换具有线性性、时移性、频移性、卷积性等重要性质，在信号处理和通信系统分析中广泛应用。",
                                    "",
                                    "## 第三章 模拟调制",
                                    "",
                                    "模拟调制是将基带信号调制到载波上的过程，目的是使信号适合在信道中传输。调制可以改变信号的频率特性，提高信号的抗干扰能力，实现多路复用等。模拟调制主要包括幅度调制、频率调制和相位调制。",
                                    "",
                                    "### 3.1 幅度调制（AM）",
                                    "",
                                    "幅度调制是通过改变载波的幅度来传输信息。标准AM信号的表达式为s(t)=A[1+m(t)]cos(ωct)，其中A为载波幅度，m(t)为调制信号，ωc为载波角频率。AM信号的频谱包含载波分量和上下边带，带宽为调制信号最高频率的两倍。AM调制的优点是实现简单，缺点是功率效率低，因为大部分功率消耗在载波上。为了提高功率效率，可以采用抑制载波的双边带调制（DSB-SC）或单边带调制（SSB）。",
                                    "",
                                    "### 3.2 频率调制（FM）",
                                    "",
                                    "频率调制是通过改变载波的频率来传输信息。FM信号的瞬时频率与调制信号成正比，表达式为ω(t)=ωc+kfm(t)，其中kf为频率灵敏度。FM信号的频谱结构复杂，理论上带宽为无穷大，但实际应用中可以采用卡森公式估算带宽：B≈2(Δf+fm)，其中Δf为最大频偏，fm为调制信号的最高频率。FM调制的优点是抗干扰能力强，功率效率高，缺点是带宽较宽。FM广泛应用于调频广播、电视伴音等领域。",
                                    "",
                                    "### 3.3 相位调制（PM）",
                                    "",
                                    "相位调制是通过改变载波的相位来传输信息。PM信号的瞬时相位与调制信号成正比，表达式为φ(t)=ωct+kpm(t)，其中kp为相位灵敏度。PM和FM在数学上密切相关，PM信号的频率变化率与调制信号成正比，而FM信号的频率与调制信号成正比。PM调制的特性与FM类似，但实现方式不同。在实际应用中，PM常用于数字通信中的相移键控（PSK）调制。",
                                    "",
                                    "## 第四章 数字基带传输",
                                    "",
                                    "数字基带传输是数字信号在基带信道中的传输，是数字通信系统的基础。数字基带信号是未经调制的数字信号，其频谱从零频率开始。数字基带传输系统包括发送端、信道和接收端，主要涉及码型选择、功率谱分析、码间干扰等问题。",
                                    "",
                                    "### 4.1 数字基带信号的码型",
                                    "",
                                    "数字基带信号的码型选择对传输性能有重要影响。常用的码型包括单极性码、双极性码、归零码、非归零码等。单极性码用正电平表示1，零电平表示0，实现简单但存在直流分量。双极性码用正负电平表示1和0，无直流分量，抗干扰能力强。归零码在码元中间回到零电平，便于提取位同步信号。非归零码在整个码元期间保持电平不变，功率效率高。此外，还有曼彻斯特码、差分码等特殊码型，各有其应用场景。",
                                    "",
                                    "### 4.2 数字基带信号的功率谱",
                                    "",
                                    "数字基带信号的功率谱密度反映了信号的频域特性，对于信道设计和滤波器设计具有重要意义。随机数字基带信号的功率谱通常包含连续谱和离散谱两部分。连续谱由码元的波形决定，离散谱由码元的周期性决定。功率谱的形状影响信号的带宽需求，对于带宽受限的信道，需要选择功率谱集中的码型。",
                                    "",
                                    "### 4.3 码间干扰与奈奎斯特准则",
                                    "",
                                    "码间干扰是数字基带传输中的主要问题，由信道的非理想特性引起。当码元速率过高或信道带宽不足时，相邻码元的响应会相互重叠，导致码间干扰。奈奎斯特第一准则指出，如果系统的冲激响应满足h(nT)=1（n=0）和h(nT)=0（n≠0），则无码间干扰。奈奎斯特第二准则给出了无码间干扰的最小带宽要求：B≥Rs/2，其中Rs为码元速率。满足奈奎斯特准则的滤波器称为奈奎斯特滤波器，常用的有升余弦滚降滤波器。",
                                    "",
                                    "## 第五章 数字带通传输",
                                    "",
                                    "数字带通传输是将数字基带信号调制到载波上进行传输，使信号适合在带通信道中传输。数字调制技术是数字通信系统的核心技术，直接影响系统的性能和复杂度。数字调制主要包括振幅键控、频移键控和相移键控。",
                                    "",
                                    "### 5.1 二进制数字调制",
                                    "",
                                    "二进制数字调制是最基本的数字调制方式。二进制振幅键控（2ASK）用载波的有无表示0和1，实现简单但抗干扰能力弱。二进制频移键控（2FSK）用两个不同频率的载波表示0和1，抗干扰能力较强但带宽较宽。二进制相移键控（2PSK）用载波的相位表示0和1，功率效率高，抗干扰能力强，但存在相位模糊问题。二进制差分相移键控（2DPSK）通过相位差表示信息，解决了相位模糊问题，应用广泛。",
                                    "",
                                    "### 5.2 多进制数字调制",
                                    "",
                                    "多进制数字调制可以提高频带利用率，在相同的码元速率下传输更多的信息。M进制振幅键控（MASK）用M个不同的幅度表示M个符号，频带利用率高但抗干扰能力弱。M进制频移键控（MFSK）用M个不同频率的载波表示M个符号，抗干扰能力强但带宽很宽。M进制相移键控（MPSK）用M个不同的相位表示M个符号，在功率效率和频带利用率之间取得良好平衡，应用最广泛。正交振幅调制（QAM）同时利用幅度和相位两个维度，进一步提高了频带利用率，是现代数字通信系统的主流调制方式。",
                                    "",
                                    "### 5.3 数字调制的性能分析",
                                    "",
                                    "数字调制的性能主要用误码率来衡量。在加性高斯白噪声（AWGN）信道中，各种数字调制方式的误码率可以通过理论分析得到。2PSK的误码率最低，2FSK次之，2ASK最高。多进制调制的误码率随进制数M的增加而增加，但频带利用率提高。在实际应用中，需要根据信道条件和系统要求选择合适的调制方式。",
                                    "",
                                    "## 第六章 信源编码",
                                    "",
                                    "信源编码是为了提高传输效率而对信源输出进行的编码，目的是减少冗余，降低码率。信源编码分为无失真信源编码和限失真信源编码。无失真信源编码要求能够完全恢复原始信息，限失真信源编码允许一定的失真以换取更高的压缩比。",
                                    "",
                                    "### 6.1 无失真信源编码",
                                    "",
                                    "无失真信源编码的理论基础是香农第一定理，它指出信源的平均码长不能小于信源的熵。霍夫曼编码是一种最优的无失真信源编码方法，它根据符号出现的概率分配不同长度的码字，概率大的符号分配短码，概率小的符号分配长码，使得平均码长最小。算术编码是另一种高效的无失真编码方法，它将整个消息编码为一个实数，编码效率接近信源熵。LZ编码是一类基于字典的编码方法，通过查找已编码的字符串来压缩数据，广泛应用于文件压缩。",
                                    "",
                                    "### 6.2 限失真信源编码",
                                    "",
                                    "限失真信源编码的理论基础是香农第三定理，它给出了在给定失真度下的最小码率。量化是限失真编码的基本方法，它将连续的模拟信号转换为离散的数字信号。均匀量化实现简单但效率低，非均匀量化根据信号的概率分布设计量化间隔，效率更高。标量量化每次量化一个样本，矢量量化同时量化多个样本，可以进一步降低码率。变换编码通过正交变换将信号转换到变换域，利用变换系数的统计特性进行编码，广泛应用于图像和视频压缩。",
                                    "",
                                    "## 第七章 信道编码",
                                    "",
                                    "信道编码是为了提高传输可靠性而添加的冗余信息，目的是检测和纠正传输错误。信道编码的理论基础是香农第二定理，它指出只要信息传输速率小于信道容量，就可以通过适当的编码实现任意小的误码率。信道编码分为分组码和卷积码两大类。",
                                    "",
                                    "### 7.1 线性分组码",
                                    "",
                                    "线性分组码是信息位和校验位满足线性关系的分组码。线性分组码可以用生成矩阵或校验矩阵来描述。生成矩阵G用于编码，校验矩阵H用于译码和检错。线性分组码具有封闭性，任意两个码字的线性组合仍是码字。汉明码是一种重要的线性分组码，可以纠正单个错误。循环码是线性分组码的一个子类，具有循环移位不变性，可以用多项式来描述，实现简单。BCH码和RS码是循环码的重要类型，具有强大的纠错能力，广泛应用于数字通信和存储系统。",
                                    "",
                                    "### 7.2 卷积码",
                                    "",
                                    "卷积码的输出不仅与当前输入有关，还与之前的输入有关，具有记忆性。卷积码可以用生成多项式或状态图来描述。维特比算法是卷积码的最优译码算法，通过动态规划找到最可能的码字序列，计算复杂度适中，应用广泛。Turbo码是一种并行级联卷积码，通过迭代译码可以获得接近香农限的性能，是3G和4G移动通信系统的关键技术。LDPC码是另一种接近香农限的编码方式，具有稀疏的校验矩阵，译码复杂度低，广泛应用于5G通信系统。",
                                    "",
                                    "## 第八章 同步",
                                    "",
                                    "同步是数字通信系统中的关键技术，包括载波同步、位同步和帧同步。同步的准确性直接影响系统的性能，同步误差会导致误码率增加甚至系统失效。",
                                    "",
                                    "### 8.1 载波同步",
                                    "",
                                    "载波同步是接收端恢复载波的过程，对于相干解调至关重要。载波同步方法分为开环法和闭环法。开环法直接从接收信号中提取载波，实现简单但性能有限。闭环法通过锁相环（PLL）跟踪载波相位，性能好但实现复杂。对于PSK信号，可以采用平方环或Costas环提取载波。载波同步的精度用相位误差来衡量，相位误差会导致解调性能下降。",
                                    "",
                                    "### 8.2 位同步",
                                    "",
                                    "位同步是接收端恢复码元时钟的过程，用于确定码元的采样时刻。位同步方法分为开环法和闭环法。开环法从接收信号中直接提取时钟，如滤波法、微分法等。闭环法通过锁相环跟踪时钟相位，性能更好。数字锁相环（DPLL）是常用的位同步方法，通过比较本地时钟和接收信号的相位差来调整时钟频率。位同步的精度用定时误差来衡量，定时误差会导致码间干扰增加。",
                                    "",
                                    "### 8.3 帧同步",
                                    "",
                                    "帧同步是接收端识别帧起始位置的过程，用于正确解帧。帧同步通常通过在帧头插入特殊的同步码来实现。同步码的选择要考虑自相关性和互相关性，常用的有巴克码、m序列等。帧同步方法分为逐码移位法和存储相关法。逐码移位法逐位比较，实现简单但速度慢。存储相关法利用相关器快速找到同步位置，速度快但实现复杂。帧同步的可靠性用漏同步概率和假同步概率来衡量。",
                                    "",
                                    "## 第九章 多路复用和多址技术",
                                    "",
                                    "多路复用和多址技术是为了提高信道利用率，允许多个用户共享同一信道。多路复用是在发送端将多个信号合并，多址是在接收端区分不同用户的信号。常用的技术包括频分复用、时分复用、码分复用等。",
                                    "",
                                    "### 9.1 频分复用（FDM）",
                                    "",
                                    "频分复用是将不同信号调制到不同频率的载波上，在频域上分离。FDM系统将可用频带划分为多个子频带，每个子频带传输一路信号。FDM的优点是实现简单，各路信号相互独立。缺点是需要保护频带防止干扰，频带利用率不高。FDM广泛应用于模拟通信系统，如调频广播、有线电视等。正交频分复用（OFDM）是FDM的改进，通过使用正交的子载波，提高了频带利用率，是4G和5G移动通信系统的核心技术。",
                                    "",
                                    "### 9.2 时分复用（TDM）",
                                    "",
                                    "时分复用是将不同信号分配到不同的时隙，在时域上分离。TDM系统将时间划分为多个时隙，每个时隙传输一路信号。TDM的优点是各路信号可以使用相同的频带，频带利用率高。缺点是需要严格的时钟同步。TDM广泛应用于数字通信系统，如数字电话、SDH等。统计时分复用（STDM）根据业务需求动态分配时隙，进一步提高了信道利用率。",
                                    "",
                                    "### 9.3 码分复用（CDM）",
                                    "",
                                    "码分复用是利用不同的码序列来区分不同的信号，在码域上分离。CDM系统为每个用户分配一个唯一的扩频码，发送端用扩频码对信号进行扩频，接收端用相同的扩频码进行解扩。CDM的优点是抗干扰能力强，可以实现软容量，支持异步传输。缺点是实现复杂，需要精确的功率控制。CDM广泛应用于CDMA移动通信系统。码分多址（CDMA）是CDM在多址通信中的应用，是3G移动通信系统的核心技术。",
                                    "",
                                    "## 第十章 通信网",
                                    "",
                                    "通信网是由多个通信节点和传输链路组成的网络，实现用户之间的信息交换。通信网的基本功能包括传输、交换、接入等。现代通信网包括电话网、数据网、移动通信网、互联网等，形成了覆盖全球的通信基础设施。",
                                    "",
                                    "### 10.1 通信网的基本结构",
                                    "",
                                    "通信网的基本结构包括星型、总线型、环型和网状型。星型结构以中心节点为核心，所有节点都与中心节点相连，优点是结构简单、易于管理，缺点是中心节点故障会导致全网瘫痪。总线型结构所有节点共享一条总线，优点是成本低、易于扩展，缺点是总线故障会影响所有节点。环型结构节点形成环形连接，优点是结构简单、易于实现，缺点是单点故障会导致环路中断。网状型结构节点之间有多条连接路径，优点是可靠性高、路由灵活，缺点是成本高、管理复杂。实际通信网通常采用混合结构，结合各种结构的优点。",
                                    "",
                                    "### 10.2 通信网的性能指标",
                                    "",
                                    "通信网的性能指标包括时延、吞吐量、可靠性等。时延是数据从源节点到目的节点所需的时间，包括传输时延、传播时延、处理时延和排队时延。吞吐量是网络在单位时间内成功传输的数据量，反映了网络的传输能力。可靠性是网络在故障情况下保持服务的能力，通常用可用性、故障恢复时间等指标来衡量。服务质量（QoS）是网络为不同业务提供不同质量保证的能力，包括带宽、时延、丢包率等参数。",
                                    "",
                                    "### 10.3 交换技术",
                                    "",
                                    "交换技术是通信网的核心技术，包括电路交换、报文交换和分组交换。电路交换在通信前建立专用通路，通信期间通路独占，优点是时延小、实时性好，缺点是资源利用率低。报文交换以报文为单位进行存储转发，优点是资源利用率高，缺点是时延大。分组交换将报文分割成固定长度的分组进行传输，结合了电路交换和报文交换的优点，是现代数据网的主流交换方式。ATM（异步传输模式）是一种面向连接的分组交换技术，结合了电路交换和分组交换的优点，广泛应用于宽带综合业务数字网。",
                                    "",
                                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                                    "",
                                    "**通信原理笔记总结**：",
                                    "",
                                    "本笔记涵盖了通信原理的核心内容，包括信号与系统基础、模拟调制、数字基带传输、数字带通传输、信源编码、信道编码、同步技术、多路复用和多址技术、通信网等主要章节。每个章节都包含了基本概念、原理分析、性能评估和应用实例，为深入理解现代通信系统提供了理论基础。",
                                    "",
                                    "通信原理是电子信息工程、通信工程等专业的重要基础课程，掌握这些知识对于从事通信系统设计、网络规划、信号处理等工作具有重要意义。随着5G、6G等新一代通信技术的发展，通信原理的知识也在不断更新和扩展，需要持续学习和实践。"
                                ]
                                
                                # 保存到内存和文件
                                app_instance.doc_manager.documents["通信原理笔记"] = communication_default
                                app_instance.doc_manager._save_document("通信原理笔记")
                                doc_content = communication_default
                                print(f"[SUMMARY] '通信原理笔记'已成功初始化并保存，内容行数: {len(doc_content)}")
                    else:
                        # 其他文档，尝试从文件系统加载
                        if doc_title in app_instance.doc_manager.get_document_titles():
                            print(f"[SUMMARY] 文档 '{doc_title}' 不在内存中，尝试从文件系统加载...")
                            doc_file = app_instance.doc_manager._get_document_file(doc_title)
                            if doc_file.exists():
                                try:
                                    with open(doc_file, 'r', encoding='utf-8') as f:
                                        content = f.read().strip()
                                        if content:
                                            doc_content = [line for line in content.split('\n')]
                                            app_instance.doc_manager.documents[doc_title] = doc_content
                                            print(f"[SUMMARY] 成功从文件系统加载文档，行数: {len(doc_content)}")
                                        else:
                                            doc_content = []
                                            app_instance.doc_manager.documents[doc_title] = doc_content
                                            print(f"[SUMMARY] 文档文件存在但内容为空")
                                except Exception as e:
                                    print(f"[SUMMARY] 从文件系统加载文档失败: {e}")
                            else:
                                print(f"[SUMMARY] 文档文件不存在: {doc_file}")
            
            # 检查文档是否有实际内容（get_document 已经处理了多层回退）
            print(f"[SUMMARY] 文档内容类型: {type(doc_content)}, 是否为None: {doc_content is None}")
            if doc_content:
                if isinstance(doc_content, str):
                    print(f"[SUMMARY] 文档内容长度（字符串）: {len(doc_content)}, 前100字符: {doc_content[:100]}")
                    has_content = len(doc_content.strip()) > 0
                elif isinstance(doc_content, list):
                    print(f"[SUMMARY] 文档内容长度（列表）: {len(doc_content)}, 前3项: {doc_content[:3]}")
                    has_content = len(doc_content) > 0 and any(line.strip() for line in doc_content)
                else:
                    print(f"[SUMMARY] 文档内容类型未知: {type(doc_content)}")
                    has_content = bool(doc_content)
            else:
                print(f"[SUMMARY] 文档内容为空或None")
                has_content = False
            
            if has_content:
                # 将文档内容列表合并为字符串
                full_content = '\n'.join(doc_content) if isinstance(doc_content, list) else str(doc_content)
                
                # 新增：章节提取逻辑
                if summary_scope == "chapter" and target_chapter:
                    print(f"[SUMMARY] 提取章节内容: {target_chapter}")
                    chapter_content = extract_chapter_content(full_content, target_chapter)
                    if chapter_content:
                        print(f"[SUMMARY] 成功提取章节内容，长度: {len(chapter_content)} 字符")
                        content_to_summarize = chapter_content
                        summary_prompt = f"请总结以下'{target_chapter}'的内容，要求简洁明了，控制在200字以内：\n\n{content_to_summarize}"
                    else:
                        print(f"[SUMMARY] 未找到章节 '{target_chapter}'")
                        # 获取文档中所有章节列表
                        chapter_list = get_chapter_list(full_content)
                        
                        # 返回友好的错误提示
                        if "此文档没有章节结构" in chapter_list:
                            # 文档完全没有章节
                            error_message = f"抱歉，《{doc_title}》没有章节结构。\n\n您可以说「总结一下」来查看全文总结。"
                        else:
                            # 文档有章节，但没有找到指定章节
                            error_message = f"抱歉，我在《{doc_title}》中没有找到「{target_chapter}」。\n\n📋 文档包含以下章节：\n{chapter_list}\n\n您可以尝试：\n1. 查询上述章节之一\n2. 说「总结一下」查看全文总结"
                        
                        return {
                            "response_type": "text",
                            "content": error_message,
                            "message_style": "warning"
                        }
                else:
                    # 全文总结
                    content_to_summarize = full_content
                    summary_prompt = f"请总结以下文档内容，要求简洁明了，控制在20字以内：\n\n{content_to_summarize}"
                
                # 调用 LLM 生成总结
                try:
                    summary_messages = [
                        {
                            "role": "system",
                            "content": "你是一个专业的文档总结助手。你的任务是阅读文档内容并生成简洁明了的总结。请直接返回总结文本，不要返回JSON格式，不要添加任何额外的格式标记。"
                        },
                        {
                            "role": "user",
                            "content": summary_prompt
                        }
                    ]
                    
                    response = Application.call(
                        api_key=API_KEY,
                        app_id=APP_ID,
                        messages=summary_messages
                    )
                    
                    if response.status_code == HTTPStatus.OK:
                        summary = response.output.text.strip()
                        # 构建意图信息和工具调用信息
                        intent_info = build_intent_info(intent_data, intent)
                        tools_used = build_tools_used(
                            intent,
                            is_dev_mode,
                            use_cloudflare=(USE_CLOUDFLARE and CLOUDFLARE_AVAILABLE and CLOUDFLARE_KV),
                            use_d1=False
                        )
                        
                        return ChatResponse(
                            response_type="TEXT",
                            content=summary,
                            new_session_id=session_id if not request.session_id else None,
                            dev_mode_enabled=is_dev_mode,
                            intent_info=intent_info,
                            tools_used=tools_used
                        )
                    else:
                        # LLM 调用失败，返回文档前500字符作为预览
                        preview = full_content[:500] + ("..." if len(full_content) > 500 else "")
                        intent_info = build_intent_info(intent_data, intent)
                        tools_used = build_tools_used(
                            intent,
                            is_dev_mode,
                            use_cloudflare=(USE_CLOUDFLARE and CLOUDFLARE_AVAILABLE and CLOUDFLARE_KV),
                            use_d1=False
                        )
                        
                        return ChatResponse(
                            response_type="TEXT",
                            content=f"⚠️ 总结生成失败，以下是文档预览：\n\n{preview}",
                            new_session_id=session_id if not request.session_id else None,
                            dev_mode_enabled=is_dev_mode,
                            intent_info=intent_info,
                            tools_used=tools_used
                        )
                except Exception as e:
                    print(f"[错误] 生成文档总结失败: {e}")
                    import traceback
                    traceback.print_exc()
                    # 降级处理：返回文档前500字符作为预览
                    preview = full_content[:500] + ("..." if len(full_content) > 500 else "")
                    intent_info = build_intent_info(intent_data, intent)
                    tools_used = build_tools_used(
                        intent,
                        is_dev_mode,
                        use_cloudflare=(USE_CLOUDFLARE and CLOUDFLARE_AVAILABLE and CLOUDFLARE_KV),
                        use_d1=False
                    )
                    
                    return ChatResponse(
                        response_type="TEXT",
                        content=f"⚠️ 总结生成失败，以下是文档预览：\n\n{preview}",
                        new_session_id=session_id if not request.session_id else None,
                        dev_mode_enabled=is_dev_mode,
                        intent_info=intent_info,
                        tools_used=tools_used
                    )
            else:
                # 文档为空，无法生成总结
                intent_info = build_intent_info(intent_data, intent)
                tools_used = build_tools_used(intent, is_dev_mode, use_cloudflare=False, use_d1=False)
                
                return ChatResponse(
                    response_type="TEXT",
                    content=f"文档 '{doc_title}' 当前为空，无法生成总结。请先添加内容后再尝试总结。",
                    new_session_id=session_id if not request.session_id else None,
                    dev_mode_enabled=is_dev_mode,
                    intent_info=intent_info,
                    tools_used=tools_used
                )
        
        elif intent == "HELP":
            # 帮助信息
            # 完全依赖LLM生成的内容，不提供硬编码的兜底文本
            # LLM应该在content_to_process字段中生成帮助内容
            content = intent_data.get("content") or intent_data.get("content_to_process")
            if content and isinstance(content, str) and len(content.strip()) > 0:
                return ChatResponse(
                    response_type="TEXT",
                    content=content,
                    new_session_id=session_id if not request.session_id else None,
                    intent_info=build_intent_info(intent_data, intent),
                    tools_used=build_tools_used(intent, is_dev_mode, use_cloudflare=False, use_d1=False)
                )
            else:
                # 如果LLM没有生成内容，返回提示信息
                # 这通常意味着系统提示词需要更新，要求LLM在HELP意图中生成content_to_process
                return ChatResponse(
                    response_type="TEXT",
                    content="抱歉，帮助信息暂时无法生成。请检查系统提示词配置，确保HELP意图能够生成帮助内容。",
                    new_session_id=session_id if not request.session_id else None,
                    intent_info=build_intent_info(intent_data, intent),
                    tools_used=build_tools_used(intent, is_dev_mode, use_cloudflare=False, use_d1=False),
                    message_style="error"
                )
        
        elif intent == "RESET_CONVERSATION" or intent == "CLEAR_CONVERSATION":
            # 重置对话
            app_instance.intent_recognizer.reset_conversation()
            if app_instance.pending_action:
                app_instance.pending_action = None
            return ChatResponse(
                response_type="TEXT",
                content="对话历史已重置，可以重新开始对话了。",
                new_session_id=session_id if not request.session_id else None
            )
        
        elif intent == "EXIT":
            # 退出（在API中，我们只返回消息，不实际退出）
            return ChatResponse(
                response_type="TEXT",
                content="感谢您的使用，再见！",
                new_session_id=session_id if not request.session_id else None
            )
        
        else:
            # 未知意图或UNKNOWN
            # 从intent_data中提取message_style（LLM返回的消息样式）
            intent = intent_data.get("intent", "")
            content = intent_data.get("content_to_process") or intent_data.get("content", "抱歉，我没有理解您的指令。请尝试使用更清晰的表达。")
            message_style = intent_data.get("message_style", "normal")  # 默认normal，如果LLM返回error则使用error
            
            # 如果intent是LLM_CONNECTION_ERROR，已经在上面的检查中处理了，这里不应该再处理
            if intent == "LLM_CONNECTION_ERROR":
                # 这种情况理论上不应该发生，因为已经在上面处理了
                # 但为了安全，再次检查
                content_str = str(content) if content is not None else "⚠️ 大语言模型连接失败，请检查后端配置。"
                return ChatResponse(
                    response_type="UNKNOWN",
                    content=content_str,
                    new_session_id=session_id if not request.session_id else None,
                    message_style="error"
                )
            
            # 如果intent是UNKNOWN，或者内容是错误提示（包含"无法理解"、"抱歉"等关键词），都返回UNKNOWN类型
            # 但排除LLM连接错误（因为连接错误应该显示明确的错误信息）
            # 确保 content 不是 None
            content_str = str(content) if content is not None else ""
            is_error_content = any(keyword in content_str for keyword in ["无法理解", "抱歉", "不清楚", "不明白", "不理解", "错误", "失败"])
            is_llm_connection_error = "大语言模型连接失败" in content_str or "LLM" in content_str.upper()
            
            if intent == "UNKNOWN" or (is_error_content and not is_llm_connection_error):
                # 增加连续无法理解的计数
                unknown_count = unknown_count_sessions.get(session_id, 0)
                unknown_count += 1
                unknown_count_sessions[session_id] = unknown_count
                
                # 如果连续3次无法理解，返回警告消息（黄色气泡）
                if unknown_count >= 3:
                    # 重置计数
                    unknown_count_sessions[session_id] = 0
                    apology_message = (
                        "对于这个失误，灵辑感到很抱歉。\n\n"
                        "灵辑团队已经收到您对于灵辑使用上的障碍问题，并承诺进行改进。\n\n"
                        "如果您能提供更多关于您想要实现的功能的信息，这将帮助我们更好地为您服务。"
                    )
                    # 构建意图信息和工具调用信息
                    intent_info = build_intent_info(intent_data, "UNKNOWN")
                    tools_used = build_tools_used("UNKNOWN", is_dev_mode, use_cloudflare=False, use_d1=False)
                    
                    return ChatResponse(
                        response_type="UNKNOWN",
                        content=apology_message,
                        new_session_id=session_id if not request.session_id else None,
                        message_style="warning",  # 三次无法理解时使用warning样式（黄色）
                        intent_info=intent_info,
                        tools_used=tools_used
                    )
                else:
                    # 前两次无法理解，使用error样式（淡红色）
                    # 构建意图信息和工具调用信息
                    intent_info = build_intent_info(intent_data, "UNKNOWN")
                    tools_used = build_tools_used("UNKNOWN", is_dev_mode, use_cloudflare=False, use_d1=False)
                    
                    return ChatResponse(
                        response_type="UNKNOWN",
                        content=str(content) if content is not None else "抱歉，我没有理解您的指令。请尝试使用更清晰的表达。",
                        new_session_id=session_id if not request.session_id else None,
                        message_style="error",  # UNKNOWN意图或错误内容强制使用error样式
                        intent_info=intent_info,
                        tools_used=tools_used
                    )
            else:
                # 正常内容，使用LLM返回的message_style（如果没有则默认normal）
                # 确保 content 不是 None
                content_str = str(content) if content is not None else "抱歉，我没有理解您的指令。请尝试使用更清晰的表达。"
                return ChatResponse(
                    response_type="TEXT",
                    content=content_str,
                    new_session_id=session_id if not request.session_id else None,
                    message_style=message_style if message_style else "normal"  # 使用LLM返回的message_style
                )
    
    except Exception as e:
        # 捕获所有异常并返回友好的错误消息
        import traceback
        error_detail = str(e)
        print(f"[API错误] {error_detail}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"处理请求时发生错误：{error_detail}"
        )

@app.get("/api/documents", response_model=DocumentsResponse)
async def get_documents(
    session_id: Optional[str] = None,
    doc_type: Optional[str] = None,
    is_trial: Optional[bool] = None
):
    """
    获取文档列表
    
    如果提供了session_id，返回该会话的文档列表；
    否则返回试用文档列表。
    如果使用 Cloudflare 存储或 D1 数据库，从云端加载。
    
    Args:
        session_id: 会话ID
        doc_type: 文档类型，"dev"（开发者文档）或 "trial"（试用文档）
        is_trial: 是否为试用模式（已废弃，使用 doc_type 代替）
    """
    try:
        # 如果使用 D1 数据库
        if USE_D1 and D1_AVAILABLE and D1_DATABASE_ID:
            try:
                from d1_document_manager import D1DocumentManager
                # 确定文档类型
                if doc_type:
                    actual_doc_type = doc_type
                elif is_trial is False:
                    actual_doc_type = "dev"
                elif is_trial is True:
                    actual_doc_type = "trial"
                else:
                    # 默认根据 session_id 判断，如果有 dev_session_id 则认为是开发者模式
                    if session_id and 'dev' in session_id.lower():
                        actual_doc_type = "dev"
                    else:
                        actual_doc_type = "trial"
                
                d1_manager = D1DocumentManager(
                    D1_DATABASE_ID,
                    doc_type=actual_doc_type,
                    session_id=session_id,
                    dev_mode_enabled=(actual_doc_type == "dev")
                )
                await d1_manager.initialize()
                documents = list(d1_manager.documents.keys())
                
                # 根据模式确保正确的文档存在
                # 开发者模式：应该有"介绍文档"和"更新记录日志"
                # 试用模式：应该有"试用文档"和"PM问答笔记"
                # initialize()应该已经创建了这些文档，但为了确保，我们检查一下
                if actual_doc_type == "trial":
                    # 试用模式：确保有"试用文档"、"PM问答笔记"和"通信原理笔记"
                    if "试用文档" not in documents:
                        documents.append("试用文档")
                    if "PM问答笔记" not in documents:
                        documents.append("PM问答笔记")
                    if "通信原理笔记" not in documents:
                        documents.append("通信原理笔记")
                elif actual_doc_type == "dev":
                    # 开发者模式：确保有"介绍文档"和"更新记录日志"
                    if "介绍文档" not in documents:
                        documents.append("介绍文档")
                    if "更新记录日志" not in documents:
                        documents.append("更新记录日志")
                
                print(f"[文档列表] D1数据库返回文档: {documents}")
                return DocumentsResponse(documents=documents)
            except Exception as e:
                print(f"[警告] D1 数据库读取失败: {e}")
                import traceback
                print(traceback.format_exc())
                # 降级到其他存储
                pass
        
        # 如果使用 Cloudflare KV 存储
        if USE_CLOUDFLARE and CLOUDFLARE_AVAILABLE and CLOUDFLARE_KV:
            try:
                # 确定文档类型
                if doc_type:
                    actual_doc_type = doc_type
                elif is_trial is False:
                    actual_doc_type = "dev"
                elif is_trial is True:
                    actual_doc_type = "trial"
                else:
                    # 默认根据 session_id 判断
                    if session_id and 'dev' in session_id.lower():
                        actual_doc_type = "dev"
                    else:
                        actual_doc_type = "trial"
                
                # Cloudflare KV存储不支持模式分离，这里需要根据实际情况处理
                is_dev_mode = (actual_doc_type == "dev")
                cloudflare_manager = CloudflareDocumentManager(CLOUDFLARE_KV, is_dev_mode)
                await cloudflare_manager.initialize()
                documents = cloudflare_manager.get_document_titles()
                
                # 根据模式确保正确的文档存在
                if actual_doc_type == "trial":
                    # 试用模式：确保有"试用文档"、"PM问答笔记"和"通信原理笔记"
                    if "试用文档" not in documents:
                        documents.append("试用文档")
                    if "PM问答笔记" not in documents:
                        documents.append("PM问答笔记")
                    if "通信原理笔记" not in documents:
                        documents.append("通信原理笔记")
                elif actual_doc_type == "dev":
                    # 开发者模式：确保有"介绍文档"和"更新记录日志"
                    if "介绍文档" not in documents:
                        documents.append("介绍文档")
                    if "更新记录日志" not in documents:
                        documents.append("更新记录日志")
                
                print(f"[文档列表] Cloudflare KV返回文档: {documents}")
                return DocumentsResponse(documents=documents)
            except Exception as e:
                print(f"[警告] Cloudflare 存储读取失败: {e}")
                # 降级到本地存储
                pass
        
        # 本地存储逻辑（降级方案）
        # 如果D1和Cloudflare都不可用，使用本地存储
        print(f"[文档列表] 使用本地存储，doc_type={doc_type}, session_id={session_id}")
        
        # 初始化 documents 列表
        documents = []
        
        # 根据模式返回默认文档列表
        if doc_type == "trial":
            # 试用模式：返回"试用文档"、"PM问答笔记"和"通信原理笔记"
            # 注意：这些文档在实际使用时需要通过chat API创建
            documents = ["试用文档", "PM问答笔记", "通信原理笔记"]
            print(f"[文档列表] 试用模式，返回文档: {documents}")
            print(f"[文档列表] 文档数量: {len(documents)}, 包含通信原理笔记: {'通信原理笔记' in documents}")
        else:
            # 开发者模式：返回"介绍文档"和"更新记录日志"
            documents = ["介绍文档", "更新记录日志"]
            print(f"[文档列表] 开发者模式，返回文档: {documents}")
        
        # 最终兜底：确保试用模式包含所有默认文档
        if doc_type == "trial":
            if "试用文档" not in documents:
                documents.append("试用文档")
            if "PM问答笔记" not in documents:
                documents.append("PM问答笔记")
            if "通信原理笔记" not in documents:
                documents.append("通信原理笔记")
            print(f"[文档列表] 试用模式最终兜底: {documents}")
        else:
            if "介绍文档" not in documents:
                documents.append("介绍文档")
            if "更新记录日志" not in documents:
                documents.append("更新记录日志")
            print(f"[文档列表] 开发者模式最终兜底: {documents}")
        
        # 过滤掉“默认文档”等无关占位文档
        documents = [d for d in documents if d not in ["默认文档"]]
        print(f"[文档列表] 过滤后文档: {documents}")
        
        return DocumentsResponse(documents=documents)
    
    except Exception as e:
        import traceback
        error_detail = str(e)
        print(f"[API错误] {error_detail}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"获取文档列表时发生错误：{error_detail}"
        )

@app.post("/api/clear-trial-data")
async def clear_trial_data(session_id: Optional[str] = None):
    """
    清空试用模式的数据（关闭网页时调用）
    只清空试用模式的数据，不影响开发者模式的数据
    """
    try:
        if not session_id:
            return {"success": False, "message": "缺少session_id"}
        
        # 如果使用 D1 数据库，清空试用数据
        if USE_D1 and D1_AVAILABLE and D1_DATABASE_ID:
            try:
                from d1_document_manager import D1DocumentManager
                d1_manager = D1DocumentManager(
                    d1_database=None,
                    doc_type="trial",
                    session_id=session_id,
                    dev_mode_enabled=False
                )
                await d1_manager.initialize()
                await d1_manager.clear_trial_data()
                return {"success": True, "message": "试用数据已清空"}
            except Exception as e:
                print(f"[警告] D1 数据库清空试用数据失败: {e}")
                import traceback
                print(traceback.format_exc())
                return {"success": False, "message": f"清空失败: {str(e)}"}
        
        # 如果使用 Cloudflare KV 存储
        if USE_CLOUDFLARE and CLOUDFLARE_AVAILABLE and CLOUDFLARE_KV:
            try:
                cloudflare_manager = CloudflareDocumentManager(CLOUDFLARE_KV, False)
                await cloudflare_manager.initialize()
                # Cloudflare KV 存储的清理逻辑（如果需要）
                return {"success": True, "message": "试用数据已清空"}
            except Exception as e:
                print(f"[警告] Cloudflare 存储清空试用数据失败: {e}")
                return {"success": False, "message": f"清空失败: {str(e)}"}
        
        # 本地存储：从会话管理器中删除会话
        if session_id in session_manager.sessions:
            del session_manager.sessions[session_id]
        
        return {"success": True, "message": "试用数据已清空"}
    
    except Exception as e:
        import traceback
        error_detail = str(e)
        print(f"[API错误] 清空试用数据失败: {error_detail}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"清空试用数据时发生错误：{error_detail}"
        )

@app.post("/api/dev-mode", response_model=ChatResponse)
async def enable_dev_mode(request: DevModeRequest):
    """
    启用开发者模式
    
    输入正确的开发者模式代码（开发者模式#000）来启用开发者模式，
    从而可以访问和修改云端永久保存的笔记。
    """
    try:
        if request.code == DEV_MODE_CODE:
            session_id = f"session_{uuid.uuid4().hex[:16]}"
            dev_mode_sessions[session_id] = True
            
            # 如果使用 Cloudflare 存储，启用云端开发者模式
            if USE_CLOUDFLARE and CLOUDFLARE_AVAILABLE and CLOUDFLARE_KV:
                try:
                    cloudflare_manager = CloudflareDocumentManager(CLOUDFLARE_KV)
                    await cloudflare_manager.initialize()
                    await cloudflare_manager.enable_dev_mode()
                except Exception as e:
                    print(f"[警告] Cloudflare 存储初始化失败: {e}")
            
            return ChatResponse(
                response_type="TEXT",
                content="✅ 开发者模式已启用！您现在可以访问和修改云端永久保存的笔记。",
                new_session_id=session_id,
                dev_mode_enabled=True
            )
        else:
            return ChatResponse(
                response_type="TEXT",
                content="❌ 开发者模式代码不正确。请输入 '开发者模式#000'。",
                dev_mode_enabled=False
            )
    except Exception as e:
        import traceback
        error_detail = str(e)
        print(f"[API错误] {error_detail}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"启用开发者模式时发生错误：{error_detail}"
        )

@app.get("/api/get-update-log")
async def get_update_log():
    """
    获取更新记录日志内容
    用于开发者模式前端加载更新记录日志
    """
    try:
        from web.update_log_content import UPDATE_LOG_CONTENT
        return {
            "success": True,
            "content": UPDATE_LOG_CONTENT
        }
    except ImportError:
        return {
            "success": False,
            "content": ["更新记录日志内容暂不可用，请检查后端服务是否运行"]
        }
    except Exception as e:
        print(f"[错误] 获取更新记录日志失败: {e}")
        import traceback
        print(traceback.format_exc())
        return {
            "success": False,
            "content": [f"获取更新记录日志时发生错误：{str(e)}"]
        }

@app.get("/api/get-manual")
async def get_manual():
    """
    获取系统说明书内容
    用于试用模式前端加载说明书
    """
    try:
        # 获取项目根目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        manual_path = os.path.join(project_root, "SYSTEM_PROMPT_COMPLETE.md")
        
        # 检查文件是否存在
        if not os.path.exists(manual_path):
            return {
                "success": False,
                "content": "# 说明书文件未找到\n\n请检查 SYSTEM_PROMPT_COMPLETE.md 文件是否存在。"
            }
        
        # 读取文件内容
        with open(manual_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return {
            "success": True,
            "content": content
        }
    except Exception as e:
        print(f"[错误] 获取说明书失败: {e}")
        import traceback
        print(traceback.format_exc())
        return {
            "success": False,
            "content": f"# 获取说明书失败\n\n错误信息：{str(e)}\n\n请检查后端服务是否正常运行。"
        }

# ============================================
# 启动服务器
# ============================================
if __name__ == "__main__":
    import uvicorn
    # 从环境变量获取端口，默认为 8000
    port = int(os.environ.get("PORT", 8000))
    print("=" * 60)
    print("灵辑 API 服务器启动中...")
    print("=" * 60)
    print(f"API文档地址: http://0.0.0.0:{port}/docs")
    print(f"API根路径: http://0.0.0.0:{port}/")
    print(f"聊天接口: http://0.0.0.0:{port}/api/chat")
    print(f"文档列表: http://0.0.0.0:{port}/api/documents")
    print(f"更新记录日志: http://0.0.0.0:{port}/api/get-update-log")
    print("=" * 60)
    # 云部署时使用 0.0.0.0 监听所有网络接口
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")

@app.post("/api/clear-trial-data")
async def clear_trial_data(session_id: Optional[str] = None):
    """
    清空试用模式的数据（关闭网页时调用）
    只清空试用模式的数据，不影响开发者模式的数据
    """
    try:
        if not session_id:
            return {"success": False, "message": "缺少session_id"}
        
        # 如果使用 D1 数据库，清空试用数据
        if USE_D1 and D1_AVAILABLE and D1_DATABASE_ID:
            try:
                from d1_document_manager import D1DocumentManager
                d1_manager = D1DocumentManager(
                    d1_database=None,
                    doc_type="trial",
                    session_id=session_id,
                    dev_mode_enabled=False
                )
                await d1_manager.initialize()
                await d1_manager.clear_trial_data()
                return {"success": True, "message": "试用数据已清空"}
            except Exception as e:
                print(f"[警告] D1 数据库清空试用数据失败: {e}")
                import traceback
                print(traceback.format_exc())
                return {"success": False, "message": f"清空失败: {str(e)}"}
        
        # 如果使用 Cloudflare KV 存储
        if USE_CLOUDFLARE and CLOUDFLARE_AVAILABLE and CLOUDFLARE_KV:
            try:
                cloudflare_manager = CloudflareDocumentManager(CLOUDFLARE_KV, False)
                await cloudflare_manager.initialize()
                # Cloudflare KV 存储的清理逻辑（如果需要）
                return {"success": True, "message": "试用数据已清空"}
            except Exception as e:
                print(f"[警告] Cloudflare 存储清空试用数据失败: {e}")
                return {"success": False, "message": f"清空失败: {str(e)}"}
        
        # 本地存储：从会话管理器中删除会话
        if session_id in session_manager.sessions:
            del session_manager.sessions[session_id]
        
        return {"success": True, "message": "试用数据已清空"}
    
    except Exception as e:
        import traceback
        error_detail = str(e)
        print(f"[API错误] 清空试用数据失败: {error_detail}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"清空试用数据时发生错误：{error_detail}"
        )

@app.post("/api/dev-mode", response_model=ChatResponse)
async def enable_dev_mode(request: DevModeRequest):
    """
    启用开发者模式
    
    输入正确的开发者模式代码（开发者模式#000）来启用开发者模式，
    从而可以访问和修改云端永久保存的笔记。
    """
    try:
        if request.code == DEV_MODE_CODE:
            session_id = f"session_{uuid.uuid4().hex[:16]}"
            dev_mode_sessions[session_id] = True
            
            # 如果使用 Cloudflare 存储，启用云端开发者模式
            if USE_CLOUDFLARE and CLOUDFLARE_AVAILABLE and CLOUDFLARE_KV:
                try:
                    cloudflare_manager = CloudflareDocumentManager(CLOUDFLARE_KV)
                    await cloudflare_manager.initialize()
                    await cloudflare_manager.enable_dev_mode()
                except Exception as e:
                    print(f"[警告] Cloudflare 存储初始化失败: {e}")
            
            return ChatResponse(
                response_type="TEXT",
                content="✅ 开发者模式已启用！您现在可以访问和修改云端永久保存的笔记。",
                new_session_id=session_id,
                dev_mode_enabled=True
            )
        else:
            return ChatResponse(
                response_type="TEXT",
                content="❌ 开发者模式代码不正确。请输入 '开发者模式#000'。",
                dev_mode_enabled=False
            )
    except Exception as e:
        import traceback
        error_detail = str(e)
        print(f"[API错误] {error_detail}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"启用开发者模式时发生错误：{error_detail}"
        )

# ============================================
# 启动服务器
# ============================================
if __name__ == "__main__":
    import uvicorn
    # 从环境变量获取端口，默认为 8000
    port = int(os.environ.get("PORT", 8000))
    print("=" * 60)
    print("灵辑 API 服务器启动中...")
    print("=" * 60)
    print(f"API文档地址: http://0.0.0.0:{port}/docs")
    print(f"API根路径: http://0.0.0.0:{port}/")
    print(f"聊天接口: http://0.0.0.0:{port}/api/chat")
    print(f"文档列表: http://0.0.0.0:{port}/api/documents")
    print("=" * 60)
    # 云部署时使用 0.0.0.0 监听所有网络接口
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")


