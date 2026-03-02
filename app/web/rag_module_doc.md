## 灵辑 RAG 架构说明

### 一、整体流程

```
用户输入
  │
  ├─ [检索阶段] 向量化用户输入 → Cloudflare Vectorize 语义检索 → 注入 System Prompt
  │
  ├─ [意图识别] LLM 基于增强后的上下文判断意图
  │
  └─ [写入阶段] ADD_CONTENT / SMART_ADD_CONTENT 成功后 → 文档向量化 → 写入 Vectorize
```

---

### 二、文本切分（Chunking）

**策略：段落优先 + 字符数兜底**，实现在 `chunk_text()` 函数中。

| 参数 | 值 | 说明 |
|------|----|------|
| `CHUNK_SIZE` | 200 字符 | 每块最大字符数 |
| `CHUNK_OVERLAP` | 30 字符 | 相邻块重叠字符数，保留上下文连贯性 |
| `MAX_CHUNKS_PER_DOC` | 50 块 | 单文档最多分块数，防止超大文档占满索引 |

**具体步骤：**

1. 先按 `\n+` 切成段落列表，过滤空段落
2. 遍历每个段落：
   - 若段落 **≤ 200 字符**：尝试与当前 `current` 合并，合并后仍 ≤ 200 则继续累积，否则将 `current` 存入 chunks，开启新块
   - 若段落 **> 200 字符**：先将 `current` 存入，然后对该段落按步长 `(200-30)=170` 字符强制切割，每片保留 30 字符重叠
3. 最终取前 50 块

---

### 三、向量化（Embedding）

**模型：** 阿里云 DashScope `text-embedding-v3`，**1536 维**向量。

**调用方式：** 通过 `vector_store.py` 中的 `get_embedding()` 函数调用，支持单文本或批量文本输入。

---

### 四、向量存储

**服务：** Cloudflare Vectorize

**索引结构：**
- **ID:** `f"{session_id}_{doc_prefix}_{chunk_index}"` (e.g., `demo_abc..._pmwen_0`)
- **向量:** 1536 维向量
- **元数据 (Metadata):** `session_id`、`doc_title`、`doc_prefix`、`chunk_index`、`text`（前 500 字符）。

---

### 五、语义检索

**触发时机：** 每次用户发送消息时，在意图识别（`intent_recognizer.py`）调用 LLM **之前**执行检索。

**检索流程：**
1. 将用户输入向量化（同样调用 `text-embedding-v3`）
2. 向 Vectorize 发送 query，过滤条件为 `session_id == 当前用户`，返回 **top-3** 结果
3. 过滤掉相似度 **< 0.70** 的结果
4. 将命中的片段格式化为：

```
【用户笔记参考】（以下内容来自用户的真实笔记，请优先基于此回答）

来自「文档标题」（相似度 0.85）：
笔记内容片段...
---
```

5. 将该字符串作为 **system 消息插入对话历史头部**，替换原有 system prompt，LLM 在此增强上下文下做意图识别和回答

**关键参数：**

| 参数 | 值 |
|------|----|
| `TOP_K` | 3 |
| `SIMILARITY_THRESHOLD` | 0.70 |
| 检索范围 | 仅当前用户（按 `session_id` 过滤） |

---

### 六、当前局限性

1. **试用模式下 RAG 实际未启用**：Vectorize 需要配置 `CF_ACCOUNT_ID` + `CF_API_TOKEN`，试用 session 若未配置则降级为无 RAG 模式，前端显示"RAG：已检索，未找到相关笔记"
2. **切分粒度偏小**：200 字符约等于 2~3 句话，对长文档的语义完整性有一定损失
3. **全量更新开销**：每次写入都删除并重建所有向量，对频繁更新的文档效率较低
