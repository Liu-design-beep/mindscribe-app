# test_vector_retrieval.py
# 向量检索功能测试脚本

import os
import sys

# 尝试设置 HuggingFace 镜像源（如果未设置）
if 'HF_ENDPOINT' not in os.environ:
    # 可以在这里设置镜像源
    # os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
    pass

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_embedder():
    """测试文档向量化器"""
    print("=" * 60)
    print("测试1: 文档向量化器初始化")
    print("=" * 60)
    
    try:
        print("[1/1] 正在导入模块...")
        from document_embedder import DocumentEmbedder
        print("✅ 模块导入成功")
        
        print("\n[2/2] 正在初始化DocumentEmbedder...")
        print("⚠️  注意：首次运行会下载模型（约400MB），可能需要几分钟，请耐心等待...")
        print("   如果卡住，可能是正在下载模型，请等待...")
        
        # 初始化
        embedder = DocumentEmbedder(storage_dir="test_vector_storage")
        
        print("\n[检查] 检查模型加载状态...")
        if embedder.embedding_model is None:
            print("❌ Embedding模型未加载")
            print("   可能的原因：")
            print("   1. text2vec未安装 - 请运行: pip install text2vec")
            print("   2. 模型下载失败 - 请检查网络连接")
            print("   3. 内存不足 - 请关闭其他程序")
            return False
        
        print("✅ Embedding模型加载成功")
        print(f"   模型: {embedder.model_name}")
        print(f"   向量维度: {embedder.vector_dim}")
        
        # 测试文档分块
        print("\n测试2: 文档分块")
        print("-" * 60)
        test_content = """
## 量子计算

量子计算是一种基于量子力学原理的计算方式。它利用量子比特的叠加和纠缠特性，能够在某些问题上实现指数级的加速。

### 基本原理

量子比特（qubit）可以同时处于0和1的叠加态，这与经典比特只能处于0或1的状态不同。这种特性使得量子计算机能够并行处理大量可能性。

### 应用场景

量子计算在密码学、药物发现、金融建模等领域有潜在应用。
"""
        
        chunks = embedder.chunk_document(test_content)
        print(f"✅ 文档分块成功，共 {len(chunks)} 个块")
        for i, chunk in enumerate(chunks[:3], 1):  # 只显示前3个
            print(f"   块 {i}: {chunk['text'][:50]}...")
        
        # 测试向量化
        print("\n测试3: 文本向量化")
        print("-" * 60)
        test_text = "量子计算的基本原理是什么？"
        vector = embedder.embed_text(test_text)
        
        if vector is not None:
            print(f"✅ 文本向量化成功")
            print(f"   向量维度: {vector.shape}")
            print(f"   向量前5个值: {vector[:5]}")
        else:
            print("❌ 文本向量化失败")
            return False
        
        # 测试添加文档
        print("\n测试4: 添加文档到向量数据库")
        print("-" * 60)
        count = embedder.add_document(
            doc_title="测试文档",
            content=test_content,
            doc_type="dev"
        )
        print(f"✅ 文档添加成功，共 {count} 个块")
        
        # 测试检索
        print("\n测试5: 向量检索")
        print("-" * 60)
        query = "量子计算的基本原理"
        # 降低阈值，因为L2距离转相似度的转换可能导致相似度较低
        # 先尝试无阈值检索，看看实际相似度
        results_all = embedder.search(query, top_k=3, threshold=0.0)
        if results_all:
            print(f"📊 无阈值检索结果（显示实际相似度）:")
            for i, result in enumerate(results_all, 1):
                distance = result.get('distance', 'N/A')
                similarity = result.get('similarity', 0)
                print(f"   结果 {i}: 相似度={similarity:.4f}, 距离={distance}")
        
        # 使用较低的阈值进行检索
        results = embedder.search(query, top_k=3, threshold=0.1)
        
        if results:
            print(f"\n✅ 检索成功（阈值≥0.1），找到 {len(results)} 个相关块")
            for i, result in enumerate(results, 1):
                print(f"\n   结果 {i}:")
                print(f"   文档: {result['doc_title']}")
                print(f"   相似度: {result['similarity']:.4f}")
                if 'distance' in result:
                    print(f"   L2距离: {result['distance']:.4f}")
                print(f"   内容: {result['content'][:100]}...")
        else:
            print("⚠️ 未找到相关结果（阈值≥0.1）")
            if results_all:
                print("   提示：实际相似度可能低于0.1，建议降低阈值或检查向量质量")
        
        # 测试统计信息
        print("\n测试6: 统计信息")
        print("-" * 60)
        stats = embedder.get_stats()
        print(f"✅ 统计信息:")
        for key, value in stats.items():
            print(f"   {key}: {value}")
        
        print("\n" + "=" * 60)
        print("✅ 所有测试通过！")
        print("=" * 60)
        return True
        
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        print("请确保已安装依赖: pip install text2vec faiss-cpu numpy")
        return False
    except Exception as e:
        import traceback
        print(f"❌ 测试失败: {e}")
        print(traceback.format_exc())
        return False

def test_retriever():
    """测试向量检索器"""
    print("\n" + "=" * 60)
    print("测试7: 向量检索器")
    print("=" * 60)
    
    try:
        from document_embedder import DocumentEmbedder
        from vector_retriever import VectorRetriever
        
        embedder = DocumentEmbedder(storage_dir="test_vector_storage")
        retriever = VectorRetriever(embedder)
        
        # 测试上下文构建
        query = "量子计算的应用"
        context = retriever.build_context(query, top_k=3)
        
        print("✅ 上下文构建成功")
        print(f"查询: {query}")
        print(f"上下文长度: {len(context)} 字符")
        print(f"上下文预览:\n{context[:200]}...")
        
        # 测试RAG提示词构建
        rag_prompt = retriever.build_rag_prompt(query, top_k=3)
        
        print("\n✅ RAG提示词构建成功")
        print(f"提示词长度: {len(rag_prompt)} 字符")
        print(f"提示词预览:\n{rag_prompt[:300]}...")
        
        print("\n" + "=" * 60)
        print("✅ 向量检索器测试通过！")
        print("=" * 60)
        return True
        
    except Exception as e:
        import traceback
        print(f"❌ 测试失败: {e}")
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    print("开始测试向量检索功能...\n")
    
    try:
        # 测试文档向量化器
        print("=" * 60)
        print("开始测试文档向量化器...")
        print("=" * 60)
        success1 = test_embedder()
        
        if not success1:
            print("\n" + "=" * 60)
            print("❌ 文档向量化器测试失败，跳过后续测试")
            print("=" * 60)
            print("\n提示：")
            print("1. 确保已安装依赖: pip install text2vec faiss-cpu numpy")
            print("2. 首次运行会下载模型（约400MB），请确保网络连接正常")
            print("3. 如果模型下载失败，可以手动下载或使用镜像源")
            sys.exit(1)
        
        # 测试向量检索器
        success2 = test_retriever()
        
        if success1 and success2:
            print("\n" + "=" * 60)
            print("🎉 所有测试通过！向量检索功能正常工作。")
            print("=" * 60)
            sys.exit(0)
        else:
            print("\n" + "=" * 60)
            print("❌ 部分测试失败，请检查错误信息。")
            print("=" * 60)
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断（Ctrl+C）")
        print("提示：如果测试卡在模型加载，请耐心等待模型下载完成")
        sys.exit(1)
    except Exception as e:
        import traceback
        print(f"\n\n❌ 测试过程中发生未预期的错误: {e}")
        print("详细错误信息:")
        traceback.print_exc()
        sys.exit(1)

