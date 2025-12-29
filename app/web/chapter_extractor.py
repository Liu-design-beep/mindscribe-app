"""
章节提取工具
用于从 Markdown 文档中提取指定章节的内容
"""

import re
from typing import Optional


def extract_chapter_content(full_content: str, target_chapter: str) -> Optional[str]:
    """
    从 Markdown 文档中提取指定章节的内容
    
    Args:
        full_content: 完整的文档内容
        target_chapter: 目标章节，如"第三章"、"第一章"等
    
    Returns:
        章节内容字符串，如果未找到则返回 None
    """
    # 转换章节编号（支持"第三章"、"第3章"等格式）
    chapter_number = extract_chapter_number(target_chapter)
    if not chapter_number:
        print(f"[章节提取] 无法识别章节编号: {target_chapter}")
        return None
    
    # 构建正则表达式，匹配章节标题
    # 支持多种格式：
    # - ## 第三章 标题
    # - ## 第3章 标题
    # - ## 第三章：标题
    patterns = [
        rf"^##\s+第{chapter_number}章[：:\s]",  # 中文数字
        rf"^##\s+第{chapter_number}章[：:\s]",  # 阿拉伯数字
    ]
    
    # 如果是中文数字，也支持阿拉伯数字
    arabic_number = chinese_to_arabic(chapter_number)
    if arabic_number:
        patterns.append(rf"^##\s+第{arabic_number}章[：:\s]")
    
    # 按行分割文档
    lines = full_content.split('\n')
    
    # 查找章节起始位置
    start_index = None
    for i, line in enumerate(lines):
        for pattern in patterns:
            if re.match(pattern, line.strip()):
                start_index = i
                print(f"[章节提取] 找到章节起始位置: 第 {i} 行, 内容: {line.strip()}")
                break
        if start_index is not None:
            break
    
    if start_index is None:
        print(f"[章节提取] 未找到章节: {target_chapter}")
        return None
    
    # 查找章节结束位置（下一个同级或更高级标题）
    end_index = len(lines)
    for i in range(start_index + 1, len(lines)):
        line = lines[i].strip()
        # 检查是否是同级（##）或更高级（#）标题
        if re.match(r'^##\s+', line) or re.match(r'^#\s+[^#]', line):
            end_index = i
            print(f"[章节提取] 找到章节结束位置: 第 {i} 行, 内容: {line}")
            break
    
    # 提取章节内容
    chapter_lines = lines[start_index:end_index]
    chapter_content = '\n'.join(chapter_lines)
    
    print(f"[章节提取] 成功提取章节，行数: {len(chapter_lines)}, 字符数: {len(chapter_content)}")
    return chapter_content


def extract_chapter_number(chapter_str: str) -> Optional[str]:
    """
    从章节字符串中提取章节编号
    
    Args:
        chapter_str: 章节字符串，如"第三章"、"第3章"等
    
    Returns:
        章节编号（中文数字），如"三"、"一"等
    """
    # 匹配"第X章"格式
    match = re.search(r'第([一二三四五六七八九十百千万\d]+)章', chapter_str)
    if match:
        number = match.group(1)
        # 如果是阿拉伯数字，转换为中文数字
        if number.isdigit():
            return arabic_to_chinese(int(number))
        else:
            return number
    return None


def arabic_to_chinese(num: int) -> str:
    """
    将阿拉伯数字转换为中文数字（1-99）
    
    Args:
        num: 阿拉伯数字
    
    Returns:
        中文数字字符串
    """
    chinese_nums = ['零', '一', '二', '三', '四', '五', '六', '七', '八', '九']
    
    if num < 0 or num > 99:
        return str(num)
    
    if num < 10:
        return chinese_nums[num]
    elif num == 10:
        return '十'
    elif num < 20:
        return '十' + chinese_nums[num % 10]
    else:
        tens = num // 10
        ones = num % 10
        if ones == 0:
            return chinese_nums[tens] + '十'
        else:
            return chinese_nums[tens] + '十' + chinese_nums[ones]


def chinese_to_arabic(chinese_num: str) -> Optional[int]:
    """
    将中文数字转换为阿拉伯数字（1-99）
    
    Args:
        chinese_num: 中文数字字符串
    
    Returns:
        阿拉伯数字，如果无法转换则返回 None
    """
    chinese_nums = {'零': 0, '一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9, '十': 10}
    
    if chinese_num in chinese_nums:
        return chinese_nums[chinese_num]
    
    # 处理"十X"格式（10-19）
    if chinese_num.startswith('十') and len(chinese_num) == 2:
        ones = chinese_nums.get(chinese_num[1], 0)
        return 10 + ones
    
    # 处理"X十"或"X十Y"格式（20-99）
    if '十' in chinese_num:
        parts = chinese_num.split('十')
        if len(parts) == 2:
            tens = chinese_nums.get(parts[0], 0)
            ones = chinese_nums.get(parts[1], 0) if parts[1] else 0
            return tens * 10 + ones
    
    return None


# 测试代码
if __name__ == "__main__":
    # 测试章节提取
    test_content = """# 通信原理笔记

## 第一章 绪论

这是第一章的内容。

### 1.1 通信系统的基本组成

这是第一章第一节的内容。

## 第二章 信号与系统

这是第二章的内容。

### 2.1 信号的分类

这是第二章第一节的内容。

## 第三章 模拟调制

这是第三章的内容。

### 3.1 幅度调制（AM）

这是第三章第一节的内容。

## 第四章 数字基带传输

这是第四章的内容。
"""
    
    # 测试提取第三章
    result = extract_chapter_content(test_content, "第三章")
    print("\n提取结果：")
    print(result)
    print("\n" + "="*50)
    
    # 测试提取第一章
    result = extract_chapter_content(test_content, "第一章")
    print("\n提取结果：")
    print(result)
