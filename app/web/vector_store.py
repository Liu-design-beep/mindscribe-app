# vector_store.py
# 灵辑 RAG 向量化模块
# 负责：笔记分块 → Embedding → Cloudflare Vectorize 读写 → 语义检索
#
# 支持两种运行环境：
#   A) Cloudflare Workers：将 env.VECTORIZE 传入 vectorize 参数（原生绑定）
#   B) Render FastAPI：通过 CF_ACCOUNT_ID + CF_API_TOKEN 走 HTTP REST API
#   C) 本地开发：两者均为 None 时自动降级，不影响现有功能
#
# 环境变量（Render 部署时配置）：
#   CF_ACCOUNT_ID     - Cloudflare Account ID
#   CF_API_TOKEN      - 有 Vectorize 读写权限的 API Token
#   DASHSCOPE_API_KEY - 阿里云 DashScope API Key（用于 Embedding）

import os
import json
import re
import hashlib
from typing import List, Dict, Optional

# ── 分块配置 ──────────────────────────────────────────────────────────────────
CHUNK_SIZE = 200        # 每块最大字符数
CHUNK_OVERLAP = 30      # 相邻块重叠字符数，保留上下文连贯性
MAX_CHUNKS_PER_DOC = 50 # 单个文档最多分块数，防止超大文档占满索引
TOP_K = 3               # 检索时返回最相关的 top-k 块
SIMILARITY_THRESHOLD = 0.70  # 相似度阈值，低于此值的结果不注入

# ── Embedding 维度（阿里云 text-embedding-v3 默认 1536 维）──────────────────
EMBEDDING_DIM = 1536

# ── Cloudflare Vectorize REST API ─────────────────────────────────────────────
VECTORIZE_INDEX_NAME = "mindscribe-notes"


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """
    将文本按段落优先、字符数兜底的策略分块。

    策略：
    1. 先按换行符切成段落
    2. 短段落合并到 chunk_size 以内
    3. 超长段落按字符数强制切割，相邻块保留 overlap 字符重叠
    """
    if not text or not text.strip():
        return []

    paragraphs = [p.strip() for p in re.split(r'\n+', text) if p.strip()]

    chunks = []
    current = ""

    for para in paragraphs:
        if len(para) > chunk_size:
            if current.strip():
                chunks.append(current.strip())
                current = ""
            for i in range(0, len(para), chunk_size - overlap):
                piece = para[i:i + chunk_size]
                if piece.strip():
                    chunks.append(piece.strip())
            continue

        if len(current) + len(para) + 1 <= chunk_size:
            current = (current + "\n" + para).strip() if current else para
        else:
            if current.strip():
                chunks.append(current.strip())
            current = para

    if current.strip():
        chunks.append(current.strip())

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

    初始化方式：
        # Cloudflare Workers 原生绑定（在 Workers 入口中使用）
        store = VectorStore(vectorize=env.VECTORIZE, api_key=env.DASHSCOPE_API_KEY)

        # Render FastAPI 通过 HTTP API（推荐，从环境变量自动读取）
        store = VectorStore.from_env()

        # 本地开发降级模式（不影响现有功能）
        store = VectorStore()
    """

    def __init__(
        self,
        vectorize=None,
        api_key: str = None,
        cf_account_id: str = None,
        cf_api_token: str = None,
    ):
        # Workers 原生绑定模式
        self.vectorize = vectorize
        # HTTP API 模式
        self.cf_account_id = cf_account_id
        self.cf_api_token = cf_api_token
        # Embedding API Key
        self.api_key = api_key

        # 判断启用模式
        if vectorize is not None:
            self.mode = "workers"
            self.enabled = True
            print("[VectorStore] ✅ 模式：Cloudflare Workers 原生绑定")
        elif cf_account_id and cf_api_token:
            self.mode = "http"
            self.enabled = True
            self._base_url = (
                f"https://api.cloudflare.com/client/v4/accounts/"
                f"{cf_account_id}/vectorize/v2/indexes/{VECTORIZE_INDEX_NAME}"
            )
            print(f"[VectorStore] ✅ 模式：HTTP REST API（账号 {cf_account_id[:8]}...）")
        else:
            self.mode = "disabled"
            self.enabled = False
            print("[VectorStore] ⚠️ 未配置 Vectorize，RAG 功能降级（不影响现有功能）")

    @classmethod
    def from_env(cls) -> "VectorStore":
        """
        从环境变量自动初始化（适用于 Render FastAPI 部署）。

        需要配置的环境变量：
            CF_ACCOUNT_ID     - Cloudflare Account ID
            CF_API_TOKEN      - 有 Vectorize 读写权限的 API Token
            DASHSCOPE_API_KEY - 阿里云 DashScope API Key
        """
        return cls(
            cf_account_id=os.environ.get("CF_ACCOUNT_ID"),
            cf_api_token=os.environ.get("CF_API_TOKEN"),
            api_key=os.environ.get("DASHSCOPE_API_KEY"),
        )

    # ── HTTP 请求辅助 ─────────────────────────────────────────────────────────

    async def _http_post(self, endpoint: str, payload: dict) -> Optional[dict]:
        """向 Cloudflare Vectorize REST API 发送 POST 请求"""
        try:
            import aiohttp
            headers = {
                "Authorization": f"Bearer {self.cf_api_token}",
                "Content-Type": "application/json",
            }
            url = f"{self._base_url}/{endpoint}"
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                    data = await resp.json()
                    if not data.get("success"):
                        errors = data.get("errors", [])
                        print(f"[VectorStore] ❌ HTTP API 错误 ({endpoint}): {errors}")
                        return None
                    return data.get("result")
        except Exception as e:
            print(f"[VectorStore] ❌ HTTP 请求异常 ({endpoint}): {e}")
            return None

    async def _http_delete_by_ids(self, ids: List[str]) -> bool:
        """通过 ID 列表删除向量"""
        try:
            import aiohttp
            headers = {
                "Authorization": f"Bearer {self.cf_api_token}",
                "Content-Type": "application/json",
            }
            url = f"{self._base_url}/delete-by-ids"
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json={"ids": ids}, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                    data = await resp.json()
                    return data.get("success", False)
        except Exception as e:
            print(f"[VectorStore] ⚠️ 删除向量异常: {e}")
            return False

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

            all_vectors = []
            batch_size = 25  # DashScope 单次最多 25 条
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

        full_text = "\n".join(line for line in content_lines if line)
        if not full_text.strip():
            print(f"[VectorStore] ⚠️ 文档 '{doc_title}' 内容为空，跳过向量化")
            return False

        chunks = chunk_text(full_text)
        if not chunks:
            return False

        print(f"[VectorStore] 📄 文档 '{doc_title}' 分为 {len(chunks)} 块，开始向量化...")

        vectors = await self._embed(chunks)
        if not vectors or len(vectors) != len(chunks):
            print(f"[VectorStore] ❌ Embedding 失败，跳过写入")
            return False

        # 先删除旧向量
        await self.delete_document(session_id, doc_title)

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
                    "text": chunk[:500]
                }
            })

        try:
            if self.mode == "workers":
                # Workers 原生绑定
                await self.vectorize.upsert(upsert_vectors)
            else:
                # HTTP REST API
                result = await self._http_post("upsert", {"vectors": upsert_vectors})
                if result is None:
                    return False

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
            ids_to_delete = [
                make_vector_id(session_id, doc_title, i)
                for i in range(MAX_CHUNKS_PER_DOC)
            ]
            if self.mode == "workers":
                await self.vectorize.deleteByIds(ids_to_delete)
            else:
                await self._http_delete_by_ids(ids_to_delete)
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

        query_vectors = await self._embed([query])
        if not query_vectors:
            return []

        try:
            query_payload = {
                "vector": query_vectors[0],
                "topK": top_k,
                "filter": {"session_id": {"$eq": session_id}},
                "returnMetadata": "all"
            }

            if self.mode == "workers":
                result = await self.vectorize.query(query_vectors[0], {
                    "topK": top_k,
                    "filter": {"session_id": {"$eq": session_id}},
                    "returnMetadata": "all"
                })
                matches = result.get("matches", []) if isinstance(result, dict) else []
            else:
                result = await self._http_post("query", query_payload)
                matches = result.get("matches", []) if result else []

            retrieved = []
            for match in matches:
                metadata = match.get("metadata", {})
                text = metadata.get("text", "")
                doc_title = metadata.get("doc_title", "未知文档")
                score = match.get("score", 0.0)
                # 过滤低相似度结果
                if text and score >= SIMILARITY_THRESHOLD:
                    retrieved.append({
                        "text": text,
                        "doc_title": doc_title,
                        "score": round(score, 4)
                    })

            print(f"[VectorStore] 🔍 检索到 {len(retrieved)} 个相关片段（阈值 {SIMILARITY_THRESHOLD}）")
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
            来自「文档标题」（相似度 0.85）：
            笔记内容片段...
            ---
        """
        if not chunks:
            return ""

        lines = ["【用户笔记参考】（以下内容来自用户的真实笔记，请优先基于此回答）\n"]
        for chunk in chunks:
            doc_title = chunk.get("doc_title", "笔记")
            text = chunk.get("text", "")
            score = chunk.get("score", 0.0)
            lines.append(f"来自「{doc_title}」（相似度 {score:.2f}）：\n{text}\n---")

        return "\n".join(lines)
