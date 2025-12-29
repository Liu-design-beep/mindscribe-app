# d1_storage.py
# Cloudflare D1 数据库存储适配器
# 用于在 Cloudflare Workers 环境中使用 D1 数据库永久保存笔记数据

import json
from typing import Optional, Dict, List

class D1Storage:
    """
    Cloudflare D1 数据库存储适配器
    用于在 Cloudflare Workers 环境中存储和读取文档数据
    """
    
    def __init__(self, d1_database=None):
        """
        初始化 D1 存储
        
        Args:
            d1_database: Cloudflare D1 数据库对象（在 Workers 环境中传入）
        """
        self.db = d1_database
        self.is_d1 = d1_database is not None
        self.db_id = "8fb7b530-17e4-44f1-819f-ee585effdbf2"  # D1 数据库 ID
        
        # 初始化数据库表
        if self.is_d1:
            self._init_tables()
    
    async def _init_tables(self):
        """初始化数据库表"""
        if not self.is_d1:
            return
        
        try:
            # 创建文档表（开发者文档）
            await self.db.execute("""
                CREATE TABLE IF NOT EXISTS dev_documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL UNIQUE,
                    content TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 创建试用文档表（试用文档，临时存储）
            await self.db.execute("""
                CREATE TABLE IF NOT EXISTS trial_documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(session_id, title)
                )
            """)
            
            # 创建元数据表
            await self.db.execute("""
                CREATE TABLE IF NOT EXISTS metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 创建开发者模式状态表
            await self.db.execute("""
                CREATE TABLE IF NOT EXISTS dev_mode_status (
                    session_id TEXT PRIMARY KEY,
                    enabled INTEGER DEFAULT 0,
                    edit_mode_enabled INTEGER DEFAULT 0,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
        except Exception as e:
            print(f"[D1错误] 初始化表失败: {e}")
    
    async def _execute(self, query: str, params: List = None):
        """执行 SQL 查询"""
        if not self.is_d1:
            return None
        try:
            if params:
                return await self.db.prepare(query).bind(*params).all()
            else:
                return await self.db.prepare(query).all()
        except Exception as e:
            print(f"[D1错误] 执行查询失败: {e}")
            return None
    
    async def _execute_write(self, query: str, params: List = None):
        """执行写入操作"""
        if not self.is_d1:
            return False
        try:
            if params:
                await self.db.prepare(query).bind(*params).run()
            else:
                await self.db.prepare(query).run()
            return True
        except Exception as e:
            print(f"[D1错误] 执行写入失败: {e}")
            return False
    
    async def check_dev_mode(self, session_id: str = None) -> bool:
        """检查开发者模式是否已启用"""
        if not session_id:
            return False
        result = await self._execute(
            "SELECT enabled FROM dev_mode_status WHERE session_id = ?",
            [session_id]
        )
        if result and result.results:
            return result.results[0].enabled == 1
        return False
    
    async def enable_dev_mode(self, session_id: str) -> bool:
        """启用开发者模式"""
        return await self._execute_write(
            """INSERT OR REPLACE INTO dev_mode_status 
               (session_id, enabled, updated_at) 
               VALUES (?, 1, CURRENT_TIMESTAMP)""",
            [session_id]
        )
    
    async def enable_edit_mode(self, session_id: str) -> bool:
        """启用修改模式"""
        return await self._execute_write(
            """UPDATE dev_mode_status 
               SET edit_mode_enabled = 1, updated_at = CURRENT_TIMESTAMP 
               WHERE session_id = ?""",
            [session_id]
        )
    
    async def check_edit_mode(self, session_id: str) -> bool:
        """检查修改模式是否已启用"""
        result = await self._execute(
            "SELECT edit_mode_enabled FROM dev_mode_status WHERE session_id = ?",
            [session_id]
        )
        if result and result.results:
            return result.results[0].edit_mode_enabled == 1
        return False
    
    async def get_metadata(self, doc_type: str = "dev") -> Dict:
        """获取元数据"""
        result = await self._execute(
            "SELECT value FROM metadata WHERE key = ?",
            [f"active_doc_title_{doc_type}"]
        )
        if result and result.results:
            try:
                return json.loads(result.results[0].value)
            except:
                return {"active_doc_title": "介绍文档" if doc_type == "dev" else "试用文档"}
        return {"active_doc_title": "介绍文档" if doc_type == "dev" else "试用文档"}
    
    async def save_metadata(self, metadata: Dict, doc_type: str = "dev") -> bool:
        """保存元数据"""
        return await self._execute_write(
            """INSERT OR REPLACE INTO metadata (key, value, updated_at) 
               VALUES (?, ?, CURRENT_TIMESTAMP)""",
            [f"active_doc_title_{doc_type}", json.dumps(metadata, ensure_ascii=False)]
        )
    
    async def get_document(self, title: str, doc_type: str = "dev", session_id: str = None) -> List[str]:
        """获取文档内容"""
        if doc_type == "dev":
            result = await self._execute(
                "SELECT content FROM dev_documents WHERE title = ?",
                [title]
            )
        else:
            if not session_id:
                return []
            result = await self._execute(
                "SELECT content FROM trial_documents WHERE session_id = ? AND title = ?",
                [session_id, title]
            )
        
        if result and result.results:
            try:
                content_str = result.results[0].content
                # 检查是否是旧的字符串格式（包含默认文本）
                if isinstance(content_str, str) and (
                    "这是您的试用文档" in content_str
                    or "可以随时添加内容" in content_str
                    or "这是您的默认文档" in content_str
                ):
                    # 如果是旧的默认文本，返回空列表或正确的内容
                    print(f"[D1Storage] ⚠️ 检测到旧格式的默认文本，文档: {title}, 内容: {content_str[:50]}...")
                    if title == "试用文档":
                        return [""]  # 试用文档应该是空白的
                    elif title == "PM问答笔记":
                        # 返回空列表，让初始化逻辑创建正确的内容
                        return []
                    else:
                        return []
                
                # 尝试解析JSON
                data = json.loads(content_str)
                # 确保返回的是列表
                if isinstance(data, list):
                    # 检查列表中的内容是否包含默认文本
                    content_str_check = str(data)
                    if (
                        "这是您的试用文档" in content_str_check
                        or "可以随时添加内容" in content_str_check
                        or "这是您的默认文档" in content_str_check
                    ):
                        print(f"[D1Storage] ⚠️ 检测到列表格式的默认文本，文档: {title}, 内容: {content_str_check[:100]}...")
                        if title == "试用文档":
                            return [""]  # 试用文档应该是空白的
                        elif title == "PM问答笔记":
                            return []  # 返回空列表，让初始化逻辑创建正确的内容
                        else:
                            return []
                    return data
                elif isinstance(data, str):
                    # 如果是字符串，检查是否包含默认文本
                    if (
                        "这是您的试用文档" in data
                        or "可以随时添加内容" in data
                        or "这是您的默认文档" in data
                    ):
                        print(f"[D1Storage] ⚠️ 检测到字符串格式的默认文本，文档: {title}")
                        if title == "试用文档":
                            return [""]
                        elif title == "PM问答笔记":
                            return []
                        else:
                            return []
                    return [data]
                else:
                    return []
            except json.JSONDecodeError:
                # 如果不是有效的JSON，可能是旧的字符串格式
                content_str = result.results[0].content
                if isinstance(content_str, str) and (
                    "这是您的试用文档" in content_str
                    or "可以随时添加内容" in content_str
                    or "这是您的默认文档" in content_str
                ):
                    print(f"[D1Storage] ⚠️ JSON解析失败，但检测到默认文本，文档: {title}")
                    if title == "试用文档":
                        return [""]
                    elif title == "PM问答笔记":
                        return []
                    else:
                        return []
                return []
            except Exception as e:
                print(f"[D1Storage] 获取文档失败: {e}")
                return []
        return []
    
    async def save_document(self, title: str, content: List[str], doc_type: str = "dev", session_id: str = None) -> bool:
        """保存文档内容"""
        # 确保content是列表格式
        if not isinstance(content, list):
            content = [content] if content else []
        
        content_json = json.dumps(content, ensure_ascii=False)
        
        if doc_type == "dev":
            return await self._execute_write(
                """INSERT OR REPLACE INTO dev_documents 
                   (title, content, updated_at) 
                   VALUES (?, ?, CURRENT_TIMESTAMP)""",
                [title, content_json]
            )
        else:
            if not session_id:
                return False
            return await self._execute_write(
                """INSERT OR REPLACE INTO trial_documents 
                   (session_id, title, content, updated_at) 
                   VALUES (?, ?, ?, CURRENT_TIMESTAMP)""",
                [session_id, title, content_json]
            )
    
    async def delete_document(self, title: str, doc_type: str = "dev", session_id: str = None) -> bool:
        """删除文档"""
        if doc_type == "dev":
            return await self._execute_write(
                "DELETE FROM dev_documents WHERE title = ?",
                [title]
            )
        else:
            if not session_id:
                return False
            return await self._execute_write(
                "DELETE FROM trial_documents WHERE session_id = ? AND title = ?",
                [session_id, title]
            )
    
    async def list_documents(self, doc_type: str = "dev", session_id: str = None) -> List[str]:
        """列出所有文档标题"""
        if doc_type == "dev":
            result = await self._execute("SELECT title FROM dev_documents")
        else:
            if not session_id:
                return []
            result = await self._execute(
                "SELECT title FROM trial_documents WHERE session_id = ?",
                [session_id]
            )
        
        if result and result.results:
            return [row.title for row in result.results]
        return []
    
    async def clear_trial_documents(self, session_id: str) -> bool:
        """清空试用文档（退出时删除）"""
        return await self._execute_write(
            "DELETE FROM trial_documents WHERE session_id = ?",
            [session_id]
        )
