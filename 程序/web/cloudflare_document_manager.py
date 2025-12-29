# cloudflare_document_manager.py
# 基于 Cloudflare KV 的文档管理器
# 支持云端永久保存和开发者模式

import json
from cloudflare_storage import CloudflareStorage
from web.update_log_content import UPDATE_LOG_TITLE, UPDATE_LOG_CONTENT

class CloudflareDocumentManager:
    """
    基于 Cloudflare KV 的文档管理器
    提供与 DocumentManager 相同的接口，但使用云端存储
    """
    
    def __init__(self, kv_namespace=None, dev_mode_enabled=False):
        """
        初始化云端文档管理器
        
        Args:
            kv_namespace: Cloudflare KV namespace 对象
            dev_mode_enabled: 是否已启用开发者模式
        """
        self.storage = CloudflareStorage(kv_namespace)
        self.dev_mode_enabled = dev_mode_enabled
        self.edit_mode_enabled = False  # set000 修改模式
        self.documents = {}
        self.active_doc_title = "PM问答笔记"
        self.intro_doc_title = "PM问答笔记"  # PM问答笔记名称，只读
        self.update_log_title = UPDATE_LOG_TITLE  # 更新记录日志名称
        self._initialized = False
    
    async def initialize(self):
        """异步初始化，加载文档和元数据"""
        if self._initialized:
            return
        
        # 加载元数据
        metadata = await self.storage.get_metadata()
        self.active_doc_title = metadata.get("active_doc_title", "PM问答笔记")
        
        # 加载所有文档
        doc_titles = await self.storage.list_documents()
        for title in doc_titles:
            content = await self.storage.get_document(title)
            self.documents[title] = content
        
        # 如果没有PM问答笔记，创建PM问答笔记（只读）
        if self.intro_doc_title not in self.documents:
            intro_content = [
                "欢迎使用灵辑 (Mindscribe) - AI 内容收藏助手",
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
                "- PM问答笔记为只读文档，用于记录PM问答内容",
                "",
                "## 注意事项",
                "PM问答笔记仅供查询，不可修改。如需修改其他笔记，请先输入 'set000' 启用修改权限。"
            ]
            self.documents[self.intro_doc_title] = intro_content
            await self.storage.save_document(self.intro_doc_title, intro_content)
            await self.storage.save_metadata({"active_doc_title": self.intro_doc_title})
        
        # 创建更新记录日志（如果不存在）
        if self.update_log_title not in self.documents:
            self.documents[self.update_log_title] = UPDATE_LOG_CONTENT
            await self.storage.save_document(self.update_log_title, UPDATE_LOG_CONTENT)
        
        # 确保活跃文档存在
        if self.active_doc_title not in self.documents and self.documents:
            self.active_doc_title = list(self.documents.keys())[0]
            await self.storage.save_metadata({"active_doc_title": self.active_doc_title})
        
        self._initialized = True
    
    async def check_dev_mode(self) -> bool:
        """检查开发者模式状态"""
        return await self.storage.check_dev_mode()
    
    async def enable_dev_mode(self) -> bool:
        """启用开发者模式"""
        result = await self.storage.enable_dev_mode()
        if result:
            self.dev_mode_enabled = True
        return result
    
    def enable_edit_mode(self) -> bool:
        """启用修改模式（set000）"""
        if not self.dev_mode_enabled:
            raise PermissionError("需要先启用开发者模式")
        self.edit_mode_enabled = True
        return True
    
    def get_document_titles(self):
        """获取所有文档标题"""
        return list(self.documents.keys())
    
    def get_document(self, title):
        """获取指定标题的文档内容"""
        return self.documents.get(title)
    
    async def set_active_document(self, title):
        """设置当前活跃文档"""
        if title in self.documents:
            self.active_doc_title = title
            await self.storage.save_metadata({"active_doc_title": title})
            return True
        return False
    
    async def add_content(self, title, content, position="end", section=None, subsection=None):
        """
        添加内容到文档
        支持定位到文档标题、开头、结尾。
        支持智能归类到指定章节。
        
        Args:
            title: 文档标题
            content: 要添加的内容
            position: 位置（"start" 或 "end"），用于向后兼容
            section: 一级章节（主题），如 "物理"、"数学"
            subsection: 二级章节（子主题），如 "量子计算"、"项目A"
        """
        if not self.dev_mode_enabled:
            raise PermissionError("需要启用开发者模式才能修改文档")
        
        if not self.edit_mode_enabled:
            raise PermissionError("需要输入 'set000' 启用修改权限才能修改笔记")
        
        # 检查是否是PM问答笔记或更新记录日志（只读）
        if title == self.intro_doc_title:
            raise PermissionError("PM问答笔记为只读文档，不可修改")
        if title == self.update_log_title:
            raise PermissionError("更新记录日志为只读文档，不可修改")
        
        if title not in self.documents:
            self.documents[title] = []
            print(f"[系统] 文档 '{title}' 不存在，已为您创建。")
        
        doc = self.documents[title]
        
        # 如果指定了 section，使用智能归类逻辑
        if section:
            import re
            # 查找或创建章节
            section_pattern = rf'^# {re.escape(section)}$'
            subsection_pattern = rf'^## {re.escape(subsection)}$' if subsection else None
            
            section_index = -1
            subsection_index = -1
            
            # 查找章节位置
            for i, line in enumerate(doc):
                if isinstance(line, str) and re.match(section_pattern, line.strip()):
                    section_index = i
                    
                    # 如果指定了子章节，继续查找
                    if subsection:
                        for j in range(i + 1, len(doc)):
                            line_str = str(doc[j]).strip() if isinstance(doc[j], str) else ""
                            if re.match(subsection_pattern, line_str):
                                subsection_index = j
                                break
                            elif line_str.startswith('# ') and not line_str.startswith('## '):
                                # 遇到下一个一级章节，子章节不存在
                                break
                    break
            
            # 如果章节不存在，创建它
            if section_index == -1:
                if doc and doc[-1] != "":
                    doc.append("")
                doc.append(f"# {section}")
                
                if subsection:
                    doc.append(f"## {subsection}")
                
                doc.append(f"- {content}")
            else:
                # 章节存在
                if subsection:
                    if subsection_index == -1:
                        # 子章节不存在，创建它
                        # 找到下一个一级章节或文件末尾
                        insert_pos = len(doc)
                        for j in range(section_index + 1, len(doc)):
                            line_str = str(doc[j]).strip() if isinstance(doc[j], str) else ""
                            if line_str.startswith('# ') and not line_str.startswith('## '):
                                insert_pos = j
                                break
                        
                        doc.insert(insert_pos, f"## {subsection}")
                        doc.insert(insert_pos + 1, f"- {content}")
                    else:
                        # 子章节存在，找到下一个子章节或一级章节
                        insert_pos = len(doc)
                        for j in range(subsection_index + 1, len(doc)):
                            line_str = str(doc[j]).strip() if isinstance(doc[j], str) else ""
                            if line_str.startswith('# ') or (line_str.startswith('## ') and j != subsection_index):
                                insert_pos = j
                                break
                        
                        doc.insert(insert_pos, f"- {content}")
                else:
                    # 没有子章节，直接在章节末尾添加
                    insert_pos = len(doc)
                    for j in range(section_index + 1, len(doc)):
                        line_str = str(doc[j]).strip() if isinstance(doc[j], str) else ""
                        if line_str.startswith('# ') and not line_str.startswith('## '):
                            insert_pos = j
                            break
                    
                    doc.insert(insert_pos, f"- {content}")
            
            # 保存到云端
            await self.storage.save_document(title, doc)
            print(f"[系统] 内容已成功添加到文档 '{title}' 的 '{section}' 部分" + (f"（{subsection}）" if subsection else "") + "。")
            return True
        
        # 向后兼容：如果没有指定 section，使用旧的逻辑
        # 处理内容：如果包含换行符，按行分割添加到文档
        content_lines = content.split('\n') if '\n' in content else [content]
        # 过滤掉空行（保留内容的原始格式，但去掉首尾空行）
        while content_lines and not content_lines[0].strip():
            content_lines.pop(0)
        while content_lines and not content_lines[-1].strip():
            content_lines.pop()
        
        # 处理position为None或非字符串的情况，默认为"end"
        if position is None:
            position_str = "end"
        elif not isinstance(position, str):
            try:
                position_str = str(position) if position else "end"
            except:
                position_str = "end"
        elif position == "":
            position_str = "end"
        else:
            position_str = position
        
        # 转换为小写
        try:
            position = position_str.lower()
        except (AttributeError, TypeError):
            position = "end"
        
        # 简化定位逻辑：只处理 start/end，其他视为 end
        if position == "start":
            # 插入到开头
            for line in reversed(content_lines):
                doc.insert(0, line)
            pos_desc = "开头"
        elif position == "end":
            # 追加到结尾
            for line in content_lines:
                doc.append(line)
            pos_desc = "结尾"
        else:
            # 尝试按内容定位
            try:
                index = -1
                for i, line in enumerate(doc):
                    if position in line:
                        index = i
                        break
                
                if index != -1:
                    # 插入到指定位置之后
                    for i, line in enumerate(content_lines):
                        doc.insert(index + 1 + i, line)
                    pos_desc = f"'{position}' 之后"
                else:
                    # 未找到位置，追加到结尾
                    for line in content_lines:
                        doc.append(line)
                    pos_desc = "结尾 (未找到指定位置)"
            except Exception:
                # 定位失败，追加到结尾
                for line in content_lines:
                    doc.append(line)
                pos_desc = "结尾 (定位失败)"
        
        # 保存到云端
        await self.storage.save_document(title, doc)
        
        print(f"[系统] 内容已成功添加到文档 '{title}' 的 {pos_desc}。")
        return True
    
    async def clear_document(self, title):
        """清空文档的所有内容"""
        # 注意：修改权限设计已取消，不再检查修改权限
        # 只检查是否是PM问答笔记或更新记录日志（只读）
        if title == self.intro_doc_title:
            raise PermissionError("PM问答笔记为只读文档，不可修改")
        if title == self.update_log_title:
            raise PermissionError("更新记录日志为只读文档，不可修改")
        
        if title not in self.documents:
            print(f"[系统] 文档 '{title}' 不存在。")
            return False
        
        self.documents[title] = []
        await self.storage.save_document(title, [])
        print(f"[系统] 文档 '{title}' 的所有内容已清空。")
        return True
    
    def display_document(self, title):
        """显示文档内容"""
        doc = self.documents.get(title, [])
        if not doc:
            return f"文档 '{title}' 为空。"
        
        output = f"--- 文档: {title} ---\n"
        for i, line in enumerate(doc):
            output += f"{i+1}. {line}\n"
        output += "----------------------"
        return output

