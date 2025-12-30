# MindScribe "Fragment-to-Knowledge" (F2K) 评测体系

**版本**：1.2
**日期**：2025-12-30
**适用场景**：非结构化短文本（碎片笔记）的自动化整理与检索

---

## 一、 背景与目标

MindScribe 系统的核心技术挑战在于处理**高频、低结构化、语义离散**的用户输入（即“碎片笔记”）。传统的 RAG 评测框架（如 RAGAS）侧重于端到端的问答准确性（QA Accuracy），难以有效评估系统在**信息架构重组（Information Re-architecture）**和**模糊检索（Fuzzy Retrieval）**方面的性能。

本框架（F2K）旨在建立一套针对**非结构化数据治理能力**的量化评估标准，重点考察系统在**数据写入阶段的结构化能力**和**数据读取阶段的召回能力**。

---

## 二、 评测维度架构

本体系将评测指标划分为两个技术域（写入域、读取域）和一个用户域。

### 2.1 写入域：数据结构化能力 (Ingestion & Structuring Metrics)
*评估系统将非结构化输入转化为结构化知识库的能力。*

| 指标 (Metric) | 定义 (Definition) | 评测方法 (Methodology) | 目标值 (Target) |
| :--- | :--- | :--- | :--- |
| **分类准确率**<br>(Topic Classification Accuracy) | 输入文本被正确映射到预定义或动态生成的语义类别的比例。 | 基于标注数据集（Ground Truth Labels）计算 Accuracy。 | > 90% |
| **语义概括度**<br>(Semantic Abstraction Score) | 自动生成的标题/标签对原始内容语义覆盖的完整性和准确性。 | **LLM-as-a-Judge**：计算生成标题与原文的语义相似度（Semantic Similarity）及关键信息覆盖率。 | > 0.85 (Cosine Sim) |
| **去重查准率/查全率**<br>(Deduplication Precision/Recall) | 系统识别重复内容的能力。重点考察对语义重复（Semantic Duplicates）的识别。 | 构造包含精确重复、语义重复和非重复样本的测试集。 | P > 99%, R > 95% |
| **增量融合成功率**<br>(Incremental Fusion Rate) | 系统识别新输入与现有条目的关联，并执行合并（Merge）而非追加（Append）操作的比例。 | 模拟多轮输入场景，检测知识库最终状态的紧凑度（Compactness）。 | > 80% |

### 2.2 读取域：检索与召回能力 (Retrieval & Recall Metrics)
*评估系统在模糊查询条件下的信息召回能力。*

| 指标 (Metric) | 定义 (Definition) | 评测方法 (Methodology) | 目标值 (Target) |
| :--- | :--- | :--- | :--- |
| **模糊查询召回率**<br>(Fuzzy Query Recall@K) | 针对非精确关键词（语义描述、时间线索）查询，目标条目出现在 Top-K 结果中的比例。 | 构建 Query-Document 对，包含同义词替换、抽象描述等干扰项。 | Recall@3 > 85% |
| **上下文完整性**<br>(Context Completeness) | 召回的文本片段是否包含了解析该片段所需的全部依赖信息（如前置条件、定义）。 | **人工/模型评分**：评估召回片段的独立可理解性（Self-containedness）。 | > 90% |
| **多跳聚合准确率**<br>(Multi-hop Aggregation Accuracy) | 针对涉及多个独立条目的聚合查询，系统正确检索并组合所有相关条目的能力。 | 构建多跳查询测试集，计算检索结果的交并比（IoU）。 | > 80% |
| **幻觉率**<br>(Hallucination Rate) | 生成内容中包含源文档未提及的事实性错误的比例。 | **NLI (Natural Language Inference)**：检测生成内容是否蕴含于（Entailed by）源文档。 | < 5% |

---

## 三、 用户域：交互与效能指标 (User Interaction & Efficacy Metrics)

*评估系统对用户行为模式的影响及实际效能。*

### 3.1 效能指标 (Efficacy Metrics)

| 指标 (Metric) | 定义 (Definition) | 数据采集方式 (Data Source) |
| :--- | :--- | :--- |
| **平均检索耗时**<br>(Mean Time to Retrieval, MTTR) | 从用户发起查询到确认找到目标信息的平均操作时长。 | 客户端埋点：Session Duration (Search Start -> Click/Copy)。 |
| **高价值内容占比**<br>(High-Value Content Ratio) | 知识库中被标记为重要（如收藏、高频访问）的内容占比。 | 行为日志分析。 |

### 3.2 行为修正指标 (Behavioral Correction Metrics)

| 指标 (Metric) | 定义 (Definition) | 业务含义 (Implication) |
| :--- | :--- | :--- |
| **人工干预率**<br>(Human Intervention Rate) | 用户对系统自动生成的分类、标题或摘要进行手动修改的比例。 | 反映系统自动化处理的**可接受度**。越低越好。 |
| **条目激活率**<br>(Item Activation Rate) | 存入系统的条目在特定周期（如30天）内被检索、引用或查看的比例。 | 反映系统构建的知识库的**可用性**。高激活率表明数据未形成“数据孤岛”。 |
| **非结构化输入占比**<br>(Unstructured Input Ratio) | 用户直接提交原始文本而不进行手动分类/打标的比例。 | 反映用户对系统整理能力的**信任度**。越高越好。 |

---

## 四、 评测数据集构建 (Benchmark Construction)

构建专用数据集 **MindScribe-Bench** 以支持上述指标的自动化计算。

### 4.1 数据集构成
包含 200+ 条经过人工清洗和标注的非结构化文本样本，覆盖：
*   **STEM 领域**：包含公式、定理的笔记片段。
*   **非结构化日志**：会议纪要、待办事项、即时通讯记录。
*   **混合语义**：包含多主题交叉的复杂文本。

### 4.2 标注规范
每条样本需包含：
*   **Source Text**: 原始输入文本。
*   **Ground Truth Category**: 标准分类标签。
*   **Ground Truth Title**: 标准标题摘要。
*   **Reference Queries**: 3-5 个对应的检索查询词（包含精确、模糊、语义查询）。
*   **Related Items**: 知识库中已存在的关联条目 ID（用于测试融合能力）。

---

## 五、 实施计划

1.  **基线测试 (Baseline)**：基于当前版本（v1.0）在 MindScribe-Bench 上运行全量测试，确立性能基线。
2.  **迭代验证 (A/B Testing)**：在引入新的 NLP 处理模块（如向量检索、动态聚类）时，对比关键指标（如 Recall@K, Intervention Rate）的变化。
3.  **持续集成 (CI/CD)**：将自动化评测脚本集成至开发流水线，确保代码变更不导致核心指标退化。
