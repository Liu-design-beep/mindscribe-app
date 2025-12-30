
import re
from chapter_extractor import extract_chapter_content, extract_chapter_number

# 模拟通信原理笔记内容
comm_content = [
    "## 第一章 绪论",
    "通信的基本概念：通信是将信息从一地传输到另一地的过程。",
    "",
    "## 第二章 确知信号",
    "确知信号是指其波形随时间的变化规律完全确定的信号。",
    "",
    "## 第三章 随机过程",
    "随机过程是随时间变化的随机变量。平稳随机过程的统计特性不随时间推移而改变。",
    "",
    "## 第四章 信道",
    "信道是信号传输的媒介。",
]

full_content = '\n'.join(comm_content)

def test_extraction(target_chapter):
    print(f"测试目标章节: '{target_chapter}'")
    
    # 1. 测试 extract_chapter_number
    chapter_number = extract_chapter_number(target_chapter)
    print(f"提取到的章节编号: '{chapter_number}'")
    
    if not chapter_number:
        print("❌ 章节编号提取失败")
        return

    # 2. 手动构建正则进行测试
    patterns = [
        rf"^\s*##\s+第{chapter_number}章[：:\s]",
    ]
    print(f"构建的正则: {patterns}")
    
    # 3. 测试 extract_chapter_content
    content = extract_chapter_content(full_content, target_chapter)
    if content:
        print(f"✅ 提取成功，内容长度: {len(content)}")
        print(f"内容预览: {content[:50]}...")
    else:
        print("❌ 提取失败")

if __name__ == "__main__":
    test_extraction("第三章")
    print("-" * 30)
    test_extraction("第3章")
    print("-" * 30)
    test_extraction("3")
