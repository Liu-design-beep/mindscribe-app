#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
清理缓存和旧数据脚本
"""

import os
import json
from pathlib import Path

def clean_documents():
    """清理documents目录中的旧文档文件"""
    documents_dir = Path("documents")
    web_documents_dir = Path("web/documents")
    
    # 清理documents目录中的txt文件
    if documents_dir.exists():
        for txt_file in documents_dir.glob("*.txt"):
            print(f"删除文件: {txt_file}")
            txt_file.unlink()
    
    # 清理web/documents目录中的txt文件
    if web_documents_dir.exists():
        for txt_file in web_documents_dir.glob("*.txt"):
            print(f"删除文件: {txt_file}")
            txt_file.unlink()
    
    # 重置metadata.json
    metadata_files = [
        documents_dir / "metadata.json",
        web_documents_dir / "metadata.json"
    ]
    
    for metadata_file in metadata_files:
        if metadata_file.exists():
            print(f"重置元数据文件: {metadata_file}")
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "active_doc_title": "试用文档"
                }, f, ensure_ascii=False, indent=2)

def clean_python_cache():
    """清理Python缓存文件"""
    cache_dirs = [
        Path("__pycache__"),
        Path("web/__pycache__"),
        Path(".pytest_cache"),
    ]
    
    for cache_dir in cache_dirs:
        if cache_dir.exists():
            print(f"清理缓存目录: {cache_dir}")
            import shutil
            shutil.rmtree(cache_dir, ignore_errors=True)
    
    # 清理.pyc文件
    for pyc_file in Path(".").rglob("*.pyc"):
        print(f"删除缓存文件: {pyc_file}")
        pyc_file.unlink()

def main():
    print("=" * 50)
    print("开始清理缓存和旧数据...")
    print("=" * 50)
    
    clean_documents()
    print()
    clean_python_cache()
    
    print()
    print("=" * 50)
    print("清理完成！")
    print("=" * 50)
    print()
    print("请执行以下操作：")
    print("1. 重启后端服务")
    print("2. 在浏览器中按 F12，打开开发者工具")
    print("3. 进入 Application/存储 -> Local Storage")
    print("4. 删除以下键（如果存在）：")
    print("   - trial_session_id")
    print("   - trial_documents")
    print("   - is_trial_mode")
    print("   - 任何 session_id 相关的键")
    print("5. 刷新页面")

if __name__ == "__main__":
    main()

