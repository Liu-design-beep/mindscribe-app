# cloudflare_storage.py
# Cloudflare KV 存储适配器
# 用于在 Cloudflare Workers 环境中永久保存笔记数据

import json
import os
from typing import Optional, Dict, List

class CloudflareStorage:
    """
    Cloudflare KV 存储适配器
    用于在 Cloudflare Workers 环境中存储和读取文档数据
    """
    
    def __init__(self, kv_namespace=None):
        """
        初始化 Cloudflare 存储
        
        Args:
            kv_namespace: Cloudflare KV namespace 对象（在 Workers 环境中传入）
        """
        self.kv = kv_namespace
        self.is_cloudflare = kv_namespace is not None
        self.dev_mode_key = "dev_mode_enabled"  # 开发者模式状态键
        self.metadata_key = "metadata"  # 元数据键
        self.doc_prefix = "doc:"  # 文档键前缀
        
    async def _get(self, key: str) -> Optional[str]:
        """从 KV 获取值"""
        if not self.is_cloudflare:
            return None
        try:
            return await self.kv.get(key)
        except Exception as e:
            print(f"[存储错误] 获取键 '{key}' 失败: {e}")
            return None
    
    async def _put(self, key: str, value: str):
        """向 KV 写入值"""
        if not self.is_cloudflare:
            return False
        try:
            await self.kv.put(key, value)
            return True
        except Exception as e:
            print(f"[存储错误] 写入键 '{key}' 失败: {e}")
            return False
    
    async def _delete(self, key: str):
        """从 KV 删除值"""
        if not self.is_cloudflare:
            return False
        try:
            await self.kv.delete(key)
            return True
        except Exception as e:
            print(f"[存储错误] 删除键 '{key}' 失败: {e}")
            return False
    
    async def _list(self, prefix: str = "") -> List[str]:
        """列出所有匹配前缀的键"""
        if not self.is_cloudflare:
            return []
        try:
            keys = await self.kv.list(prefix=prefix)
            return [key.name for key in keys.keys] if hasattr(keys, 'keys') else []
        except Exception as e:
            print(f"[存储错误] 列出键失败: {e}")
            return []
    
    async def check_dev_mode(self) -> bool:
        """检查开发者模式是否已启用"""
        value = await self._get(self.dev_mode_key)
        return value == "true"
    
    async def enable_dev_mode(self) -> bool:
        """启用开发者模式"""
        return await self._put(self.dev_mode_key, "true")
    
    async def disable_dev_mode(self) -> bool:
        """禁用开发者模式"""
        return await self._delete(self.dev_mode_key)
    
    async def get_metadata(self) -> Dict:
        """获取元数据"""
        value = await self._get(self.metadata_key)
        if value:
            try:
                return json.loads(value)
            except:
                return {"active_doc_title": "PM问答笔记"}
        return {"active_doc_title": "PM问答笔记"}
    
    async def save_metadata(self, metadata: Dict) -> bool:
        """保存元数据"""
        return await self._put(self.metadata_key, json.dumps(metadata, ensure_ascii=False))
    
    async def get_document(self, title: str) -> List[str]:
        """获取文档内容"""
        key = f"{self.doc_prefix}{title}"
        value = await self._get(key)
        if value:
            try:
                data = json.loads(value)
                return data.get("content", [])
            except:
                return []
        return []
    
    async def save_document(self, title: str, content: List[str]) -> bool:
        """保存文档内容"""
        key = f"{self.doc_prefix}{title}"
        data = {
            "title": title,
            "content": content,
            "updated_at": str(os.environ.get("CF_DATE", ""))
        }
        return await self._put(key, json.dumps(data, ensure_ascii=False))
    
    async def delete_document(self, title: str) -> bool:
        """删除文档"""
        key = f"{self.doc_prefix}{title}"
        return await self._delete(key)
    
    async def list_documents(self) -> List[str]:
        """列出所有文档标题"""
        keys = await self._list(self.doc_prefix)
        titles = []
        for key in keys:
            # 移除前缀，获取文档标题
            if key.startswith(self.doc_prefix):
                title = key[len(self.doc_prefix):]
                titles.append(title)
        return titles

