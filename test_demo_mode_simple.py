#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试演示模式功能（简化版，不需要 dashscope）
"""

import sys
import os

# 添加 app/web 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app', 'web'))

from document_manager import DocumentManager

def test_document_manager_demo_mode():
    """测试 DocumentManager 演示模式"""
    print("=" * 60)
    print("测试 1: DocumentManager 演示模式")
    print("=" * 60)
    
    # 创建演示模式的 DocumentManager
    dm = DocumentManager(demo_mode=True)
    
    # 检查初始状态
    print(f"\n初始文档列表: {dm.get_document_titles()}")
    print(f"活跃文档: {dm.active_doc_title}")
    
    # 检查试用文档
    trial_doc = dm.get_document("试用文档")
    print(f"\n试用文档内容: {trial_doc}")
    
    # 检查通信原理笔记
    comm_doc = dm.get_document("通信原理笔记")
    if comm_doc:
        print(f"\n通信原理笔记前 5 行:")
        for i, line in enumerate(comm_doc[:5]):
            print(f"  {i+1}. {line}")
    
    # 测试添加内容
    print("\n" + "-" * 60)
    print("测试添加内容...")
    dm.add_content("试用文档", "今天学了量子计算")
    trial_doc_after = dm.get_document("试用文档")
    print(f"添加后的试用文档内容: {trial_doc_after}")
    
    # 检查文件系统（应该没有保存）
    doc_file = dm._get_document_file("试用文档")
    print(f"\n文件是否存在: {doc_file.exists()}")
    if not doc_file.exists():
        print("✅ 文件未保存（符合演示模式预期）")
    else:
        print("❌ 文件已保存（不符合演示模式预期）")
        return False
    
    print("\n✅ DocumentManager 演示模式测试通过！")
    return True

def test_multiple_instances():
    """测试多个实例的隔离性"""
    print("\n" + "=" * 60)
    print("测试 2: 多个实例的隔离性")
    print("=" * 60)
    
    # 创建两个独立的实例
    dm1 = DocumentManager(demo_mode=True)
    dm2 = DocumentManager(demo_mode=True)
    
    # 在 dm1 中添加内容
    print("\n在实例 1 中添加内容...")
    dm1.add_content("试用文档", "实例 1 的内容")
    content1 = dm1.get_document("试用文档")
    print(f"实例 1 的内容: {content1}")
    
    # 检查 dm2 是否受影响
    content2 = dm2.get_document("试用文档")
    print(f"实例 2 的内容: {content2}")
    
    # 验证隔离性
    if "实例 1 的内容" not in str(content2):
        print("\n✅ 实例隔离性测试通过！")
        return True
    else:
        print("\n❌ 实例隔离性测试失败！")
        return False

def test_no_file_persistence():
    """测试文件不持久化"""
    print("\n" + "=" * 60)
    print("测试 3: 文件不持久化")
    print("=" * 60)
    
    # 创建演示模式的 DocumentManager
    dm = DocumentManager(demo_mode=True)
    
    # 添加内容
    dm.add_content("试用文档", "测试内容")
    
    # 检查 documents 目录
    import os
    doc_dir = dm.storage_dir
    print(f"\n文档目录: {doc_dir}")
    
    # 列出目录中的文件
    if doc_dir.exists():
        files = list(doc_dir.glob("*.txt"))
        print(f"目录中的 .txt 文件数量: {len(files)}")
        if len(files) > 0:
            print("文件列表:")
            for f in files:
                print(f"  - {f.name}")
    
    # 检查试用文档文件
    trial_file = dm._get_document_file("试用文档")
    print(f"\n试用文档文件路径: {trial_file}")
    print(f"文件是否存在: {trial_file.exists()}")
    
    if not trial_file.exists():
        print("\n✅ 文件不持久化测试通过！")
        return True
    else:
        print("\n❌ 文件不持久化测试失败！文件被保存了。")
        return False

if __name__ == "__main__":
    print("开始测试演示模式功能...\n")
    
    try:
        # 测试 1
        test1 = test_document_manager_demo_mode()
        
        # 测试 2
        test2 = test_multiple_instances()
        
        # 测试 3
        test3 = test_no_file_persistence()
        
        # 总结
        print("\n" + "=" * 60)
        if test1 and test2 and test3:
            print("🎉 所有测试通过！演示模式功能正常工作。")
            print("=" * 60)
            print("\n功能确认：")
            print("✅ 1. 演示模式正确初始化文档")
            print("✅ 2. 文档内容只保存在内存中")
            print("✅ 3. 不保存到文件系统")
            print("✅ 4. 多个实例相互隔离")
            print("✅ 5. 每次创建新实例都是原始状态")
            sys.exit(0)
        else:
            print("❌ 部分测试失败，请检查错误信息。")
            print("=" * 60)
            sys.exit(1)
    except Exception as e:
        import traceback
        print(f"\n\n❌ 测试过程中发生错误: {e}")
        print("详细错误信息:")
        traceback.print_exc()
        sys.exit(1)
