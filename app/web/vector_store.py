# vector_store.py
# 灵辑 RAG 向量化模块
# 负责：笔记分块 → Embedding → Cloudflare Vectorize 读写 → 语义检索
#
# 依赖：
#   - Cloudflare Vectorize（通过 wrangler.toml 绑定 VECTORIZE）
#   - 阿里云 DashScope text-embedding-v3（与现有 LLM 同一账号）
#
# 使用方式：
#   在 Cloudflare Workers 环境中，将 env.VECTORIZE 传入 VectorStore
#   在本地 FastAPI 环境中，传入 None 则自动降级为无 RAG 模式（不影响现有功能）

import json
import re
import hashlib
from typing import List, Dict, Optional, Tuple

# ── 分块配置 ──────────────────────────────────────────────────────────────────
CHUNK_SIZE = 200        # 每块最大字符数
CHUNK_OVERLAP = 30      # 相邻块重叠字符数，保留上下文连贯性
MAX_CHUNKS_PER_DOC = 50 # 单个文档最多分块数，防止超大文档占满索引
TOP_K = 3               # 检索时返回最相关的 top-k 块

# ── Embedding 维度（阿里云 text-embedding-v3 默认 1536 维）──────────────────
EMBEDDING_DIM = 1536


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """
    将文本按段落优先、字符数兜底的策略分块。
    
    策略：
    1. 先按换行符切成段落
    2. 短段落合并到 chunk_size 以内
    3. 超长段落按字符数强制切割
    """
    if not text or not text.strip():
        return []

    # 按换行切段落，过滤空行
    paragraphs = [p.strip() for p in re.split(r'\n+', text) if p.strip()]
    
    chunks = []
    current = ""

    for para in paragraphs:
        # 段落本身超过 chunk_size，强制切割
        if len(para) > chunk_size:
            # 先把 current 存起来
            if current.strip():
                chunks.append(current.strip())
                current = ""
            # 按 chunk_size 切割长段落
            for i in range(0, len(para), chunk_size - overlap):
                piece = para[i:i + chunk_size]
                if piece.strip():
                    chunks.append(piece.strip())
            continue

        # 合并短段落
        if len(current) + len(para) + 1 <= chunk_size:
            current = (current + "\n" + para).strip() if current else para
        else:
            if current.strip():
                chunks.append(current.strip())
            current = para

    if current.strip():
        chunks.append(current.strip())

    # 限制最大块数
    return chunks[:MAX_CHUNKS_PER_DOC]


def make_vector_id(session_id: str, doc_title: str, chunk_index: int) -> str:
    """
    生成向量 ID，格式：sha256(session_id:doc_title)[:16]-chunk_index
    Vectorize 要求 ID 只含字母数字和连字符。
    """
    raw = f"{session_id}:{doc_title}"
    digest = hashlib.sha256(raw.encode()).hexdigest()[:16]
    return f"{digest}-{chunk_index}"


def make_doc_prefix(session_id: str, doc_title: str) -> str:
    """生成文档前缀（用于按文档删除向量）"""
    raw = f"{session_id}:{doc_title}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


class VectorStore:
    """
    灵辑 RAG 向量存储管理器。
    
    在 Cloudflare Workers 环境中：
        vectorize = env.VECTORIZE  （由 wrangler.toml 绑定）
        store = VectorStore(vectorize=vectorize, api_key=env.DASHSCOPE_API_KEY)
    
    在本地 FastAPI 环境中：
        store = VectorStore()  → 自动降级，所有操作静默跳过
    """

    def __init__(self, vectorize=None, api_key: str = None):
        self.vectorize = vectorize
        self.api_key = api_key
        self.enabled = (vectorize is not None)
        if not self.enabled:
            print("[VectorStore] ⚠️ Vectorize 未绑定，RAG 功能降级（不影响现有功能）")

    # ── Embedding ─────────────────────────────────────────────────────────────

    async def _embed(self, texts: List[str]) -> Optional[List[List[float]]]:
        """
        调用阿里云 DashScope text-embedding-v3 批量生成向量。
        返回 List[List[float]]，失败返回 None。
        """
        if not self.api_key:
            print("[VectorStore] ⚠️ 未配置 DASHSCOPE_API_KEY，无法生成 Embedding")
            return None

        try:
            import dashscope
            from dashscope import TextEmbedding

            dashscope.api_key = self.api_key

            # DashScope 单次最多 25 条，分批处理
            all_vectors = []
            batch_size = 25
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                resp = TextEmbedding.call(
                    model=TextEmbedding.Models.text_embedding_v3,
                    input=batch,
                    dimension=EMBEDDING_DIM
                )
                if resp.status_code != 200:
                    print(f"[VectorStore] ❌ Embedding 调用失败: {resp.message}")
                    return None
                for item in resp.output["embeddings"]:
                    all_vectors.append(item["embedding"])

            return all_vectors

        except Exception as e:
            print(f"[VectorStore] ❌ Embedding 异常: {e}")
            return None

    # ── 写入 ──────────────────────────────────────────────────────────────────

    async def upsert_document(
        self,
        session_id: str,
        doc_title: str,
        content_lines: List[str]
    ) -> bool:
        """
        将文档内容向量化并写入 Vectorize。
        每次调用会先删除该文档的旧向量，再写入新向量（全量更新）。
        
        Args:
            session_id:    用户会话 ID（区分不同用户的笔记）
            doc_title:     文档标题
            content_lines: 文档内容行列表（与 D1Storage 格式一致）
        
        Returns:
            True 表示成功，False 表示失败或降级
        """
        if not self.enabled:
            return False

        # 合并内容行为完整文本
        full_text = "\n".join(line for line in content_lines if line)
        if not full_text.strip():
            print(f"[VectorStore] ⚠️ 文档 '{doc_title}' 内容为空，跳过向量化")
            return False

        # 分块
        chunks = chunk_text(full_text)
        if not chunks:
            return False

        print(f"[VectorStore] 📄 文档 '{doc_title}' 分为 {len(chunks)} 块，开始向量化...")

        # 生成 Embedding
        vectors = await self._embed(chunks)
        if not vectors or len(vectors) != len(chunks):
            print(f"[VectorStore] ❌ Embedding 失败，跳过写入")
            return False

        # 先删除旧向量
        await self.delete_document(session_id, doc_title)

        # 构造 Vectorize upsert 数据
        doc_prefix = make_doc_prefix(session_id, doc_title)
        upsert_vectors = []
        for i, (chunk, vec) in enumerate(zip(chunks, vectors)):
            upsert_vectors.append({
                "id": make_vector_id(session_id, doc_title, i),
                "values": vec,
                "metadata": {
                    "session_id": session_id,
                    "doc_title": doc_title,
                    "doc_prefix": doc_prefix,
                    "chunk_index": i,
                    "text": chunk[:500]  # 存储原文片段（Vectorize metadata 有大小限制）
                }
            })

        try:
            # Cloudflare Vectorize upsert API
            await self.vectorize.upsert(upsert_vectors)
            print(f"[VectorStore] ✅ 文档 '{doc_title}' 写入 {len(upsert_vectors)} 个向量")
            return True
        except Exception as e:
            print(f"[VectorStore] ❌ Vectorize upsert 失败: {e}")
            return False

    async def delete_document(self, session_id: str, doc_title: str) -> bool:
        """删除文档的所有向量（通过枚举 ID 方式）"""
        if not self.enabled:
            return False
        try:
            # 枚举可能的 chunk ID（最多 MAX_CHUNKS_PER_DOC 个）
            ids_to_delete = [
                make_vector_id(session_id, doc_title, i)
                for i in range(MAX_CHUNKS_PER_DOC)
            ]
            await self.vectorize.deleteByIds(ids_to_delete)
            return True
        except Exception as e:
            print(f"[VectorStore] ⚠️ 删除向量失败（可能是正常的首次写入）: {e}")
            return False

    # ── 检索 ──────────────────────────────────────────────────────────────────

    async def search(
        self,
        query: str,
        session_id: str,
        top_k: int = TOP_K
    ) -> List[Dict]:
        """
        语义检索：将查询向量化，在 Vectorize 中找最相关的笔记片段。
        
        Args:
            query:      用户输入的查询文本
            session_id: 用户会话 ID（只检索该用户的笔记）
            top_k:      返回最相关的 top-k 结果
        
        Returns:
            List of {"text": str, "doc_title": str, "score": float}
            失败或降级时返回空列表
        """
        if not self.enabled:
            return []

        # 向量化查询
        query_vectors = await self._embed([query])
        if not query_vectors:
            return []

        try:
            # Cloudflare Vectorize query API
            result = await self.vectorize.query(
                query_vectors[0],
                {
                    "topK": top_k,
                    "filter": {"session_id": {"$eq": session_id}},
                    "returnMetadata": "all"
                }
            )

            matches = result.get("matches", []) if isinstance(result, dict) else []
            
            retrieved = []
            for match in matches:
                metadata = match.get("metadata", {})
                text = metadata.get("text", "")
                doc_title = metadata.get("doc_title", "未知文档")
                score = match.get("score", 0.0)
                if text:
                    retrieved.append({
                        "text": text,
                        "doc_title": doc_title,
                        "score": round(score, 4)
                    })

            print(f"[VectorStore] 🔍 检索到 {len(retrieved)} 个相关片段")
            return retrieved

        except Exception as e:
            print(f"[VectorStore] ❌ Vectorize 检索失败: {e}")
            return []

    # ── 格式化为 Prompt 上下文 ────────────────────────────────────────────────

    @staticmethod
    def format_context(chunks: List[Dict]) -> str:
        """
        将检索结果格式化为注入 System Prompt 的上下文字符串。
        
        格式：
            【用户笔记参考】
            来自「文档标题」：
            笔记内容片段...
            ---
        """
        if not chunks:
            return ""

        lines = ["【用户笔记参考】（以下内容来自用户的真实笔记，请优先基于此回答）\n"]
        for chunk in chunks:
            doc_title = chunk.get("doc_title", "笔记")
            text = chunk.get("text", "")
            lines.append(f"来自「{doc_title}」：\n{text}\n---")

        return "\n".join(lines)
