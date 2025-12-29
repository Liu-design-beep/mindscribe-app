#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
清理默认占位文本脚本
自动检测并清理所有包含"这是您的默认文档，可以随时添加内容。"的文件和数据
"""

import os
import json
import re
from pathlib import Path

# 要检测和清理的文本模式
DEFAULT_TEXT_PATTERNS = [
    "这是您的默认文档，可以随时添加内容。",
    "这是您的试用文档，可以随时添加内容。",
    "可以随时添加内容",
    "这是您的默认文档",
    "这是您的试用文档"
]

def contains_default_text(content):
    """检测内容是否包含默认占位文本"""
    if not content:
        return False
    content_str = str(content)
    for pattern in DEFAULT_TEXT_PATTERNS:
        if pattern in content_str:
            return True
    return False

def clean_txt_files():
    """清理documents目录中的txt文件"""
    print("\n" + "="*60)
    print("步骤1: 清理本地txt文件")
    print("="*60)
    
    documents_dirs = [
        Path("documents"),
        Path("web/documents")
    ]
    
    cleaned_count = 0
    for doc_dir in documents_dirs:
        if not doc_dir.exists():
            print(f"  [跳过] 目录不存在: {doc_dir}")
            continue
        
        print(f"\n  检查目录: {doc_dir}")
        for txt_file in doc_dir.glob("*.txt"):
            try:
                with open(txt_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if contains_default_text(content):
                    print(f"  [清理] 发现包含默认文本的文件: {txt_file.name}")
                    title = txt_file.stem
                    
                    # 根据文件名决定清理策略
                    if title == "试用文档":
                        new_content = ""  # 试用文档应该是空白的
                        print(f"    -> 设置为空白内容")
                    elif title == "PM问答笔记":
                        new_content = ""  # 清空，让系统重新初始化
                        print(f"    -> 清空内容，等待系统重新初始化")
                    elif title == "介绍文档":
                        new_content = ""  # 清空，让系统重新初始化
                        print(f"    -> 清空内容，等待系统重新初始化")
                    else:
                        new_content = ""  # 其他文档也清空
                        print(f"    -> 清空内容")
                    
                    # 保存清理后的内容
                    with open(txt_file, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    cleaned_count += 1
                else:
                    print(f"  [正常] {txt_file.name} - 不包含默认文本")
            except Exception as e:
                print(f"  [错误] 处理文件 {txt_file.name} 时出错: {e}")
    
    print(f"\n  [完成] 共清理了 {cleaned_count} 个文件")
    return cleaned_count

def reset_metadata():
    """重置metadata.json文件"""
    print("\n" + "="*60)
    print("步骤2: 重置元数据文件")
    print("="*60)
    
    metadata_files = [
        Path("documents/metadata.json"),
        Path("web/documents/metadata.json")
    ]
    
    for metadata_file in metadata_files:
        if metadata_file.exists():
            try:
                print(f"  重置: {metadata_file}")
                with open(metadata_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        "active_doc_title": "试用文档"
                    }, f, ensure_ascii=False, indent=2)
                print(f"    [完成] 已重置")
            except Exception as e:
                print(f"    [错误] 重置失败: {e}")
        else:
            print(f"  [跳过] 文件不存在: {metadata_file}")

def clean_python_cache():
    """清理Python缓存文件"""
    print("\n" + "="*60)
    print("步骤3: 清理Python缓存")
    print("="*60)
    
    import shutil
    
    cache_dirs = [
        Path("__pycache__"),
        Path("web/__pycache__"),
        Path(".pytest_cache"),
    ]
    
    cleaned_dirs = 0
    for cache_dir in cache_dirs:
        if cache_dir.exists():
            try:
                print(f"  删除: {cache_dir}")
                shutil.rmtree(cache_dir, ignore_errors=True)
                cleaned_dirs += 1
                print(f"    [完成] 已删除")
            except Exception as e:
                print(f"    ❌ 删除失败: {e}")
        else:
            print(f"  [跳过] 目录不存在: {cache_dir}")
    
    # 清理.pyc文件
    pyc_count = 0
    for pyc_file in Path(".").rglob("*.pyc"):
        try:
            print(f"  删除: {pyc_file}")
            pyc_file.unlink()
            pyc_count += 1
        except Exception as e:
            print(f"    ❌ 删除失败: {e}")
    
    print(f"\n  [完成] 共清理了 {cleaned_dirs} 个缓存目录和 {pyc_count} 个.pyc文件")

def check_code_files():
    """检查代码文件中是否包含默认文本（只读检查）"""
    print("\n" + "="*60)
    print("步骤4: 检查代码文件")
    print("="*60)
    
    code_files = [
        Path("web/document_manager.py"),
        Path("web/api_server.py"),
        Path("web/d1_storage.py"),
        Path("document_manager.py"),
    ]
    
    found_count = 0
    for code_file in code_files:
        if not code_file.exists():
            continue
        
        try:
            with open(code_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查是否包含默认文本（但不在注释或字符串中）
            for pattern in DEFAULT_TEXT_PATTERNS:
                if pattern in content:
                    # 检查是否在字符串字面量中（可能是检测逻辑）
                    if f'"{pattern}"' in content or f"'{pattern}'" in content:
                        print(f"  [检测] {code_file.name} - 包含检测逻辑（正常）")
                    else:
                        print(f"  ⚠️  {code_file.name} - 可能包含问题文本")
                        found_count += 1
        except Exception as e:
            print(f"  [错误] 检查 {code_file.name} 时出错: {e}")
    
    if found_count == 0:
        print("  [通过] 所有代码文件检查通过")
    else:
        print(f"  [警告] 发现 {found_count} 个可能的问题文件，请手动检查")

def print_summary():
    """打印清理总结和后续步骤"""
    print("\n" + "="*60)
    print("清理完成！")
    print("="*60)
    print("\n[后续步骤]")
    print("\n1. 重启后端服务：")
    print("   python -m uvicorn web.api_server:app --host 0.0.0.0 --port 8000 --reload")
    print("\n2. 清理浏览器本地存储：")
    print("   - 按 F12 打开开发者工具")
    print("   - 进入 Application/存储 -> Local Storage")
    print("   - 删除以下键（如果存在）：")
    print("     - trial_session_id")
    print("     - trial_documents")
    print("     - is_trial_mode")
    print("     - 任何包含 session 的键")
    print("\n3. 刷新浏览器页面")
    print("\n4. 如果问题仍然存在，可能需要清理数据库：")
    print("   - 如果使用 D1 数据库，需要清理 trial_documents 表中的旧记录")
    print("   - 或者创建新的 session_id 来避免旧数据")
    print("\n" + "="*60)

def main():
    print("="*60)
    print("灵辑 - 默认占位文本清理脚本")
    print("="*60)
    print("\n此脚本将：")
    print("1. 清理包含默认占位文本的txt文件")
    print("2. 重置metadata.json文件")
    print("3. 清理Python缓存文件")
    print("4. 检查代码文件")
    print("\n开始执行...")
    
    try:
        cleaned_files = clean_txt_files()
        reset_metadata()
        clean_python_cache()
        check_code_files()
        
        print_summary()
        
        print(f"\n[完成] 清理完成！共处理了 {cleaned_files} 个文件")
        
    except Exception as e:
        print(f"\n[错误] 执行过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

