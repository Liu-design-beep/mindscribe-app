
import sys
import os

# 添加当前目录到 sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from chapter_extractor import extract_chapter_content

def test_chapter_extraction():
    print("开始测试章节提取功能...")
    
    # 测试用例 1: 标准格式（带空格）
    content1 = """
## 第一章 绪论
这是第一章的内容。
## 第二章 信号与系统
这是第二章的内容。
"""
    result1 = extract_chapter_content(content1, "第一章")
    assert result1 is not None and "这是第一章的内容" in result1
    print("✅ 测试用例 1 (标准格式) 通过")
    
    # 测试用例 2: 无空格格式（行尾直接结束）
    content2 = """
## 第一章
这是第一章的内容。
## 第二章
这是第二章的内容。
"""
    result2 = extract_chapter_content(content2, "第一章")
    assert result2 is not None and "这是第一章的内容" in result2
    print("✅ 测试用例 2 (无空格格式) 通过")
    
    # 测试用例 3: 冒号格式
    content3 = """
## 第一章：绪论
这是第一章的内容。
## 第二章：信号与系统
这是第二章的内容。
"""
    result3 = extract_chapter_content(content3, "第一章")
    assert result3 is not None and "这是第一章的内容" in result3
    print("✅ 测试用例 3 (冒号格式) 通过")
    
    # 测试用例 4: 数字格式
    content4 = """
## 1. 绪论
这是第一章的内容。
## 2. 信号与系统
这是第二章的内容。
"""
    result4 = extract_chapter_content(content4, "第一章") # 应该能识别 "第一章" -> 1
    assert result4 is not None and "这是第一章的内容" in result4
    print("✅ 测试用例 4 (数字格式) 通过")
    
    # 测试用例 5: 混合格式
    content5 = """
## 第一章 绪论
这是第一章的内容。
## 2. 信号与系统
这是第二章的内容。
"""
    result5 = extract_chapter_content(content5, "第二章") # 应该能识别 "第二章" -> 2
    assert result5 is not None and "这是第二章的内容" in result5
    print("✅ 测试用例 5 (混合格式) 通过")

    print("\n所有测试用例通过！")

if __name__ == "__main__":
    test_chapter_extraction()
