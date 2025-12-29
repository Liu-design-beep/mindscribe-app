# document_matcher.py
# 文档内容匹配检查器

class DocumentMatcher:
    """文档内容匹配检查器"""
    
    # 文档类型定义
    DOCUMENT_TYPES = {
        "学习": ["学习笔记", "笔记", "知识", "物理笔记", "数学笔记", "英语笔记", "化学笔记", "学习"],
        "工作": ["工作笔记", "项目周报", "项目笔记", "工作", "项目"],
        "灵感": ["灵感笔记", "想法", "创意", "思路", "灵感"],
        "生活": ["生活笔记", "日记", "日常", "生活"],
        "通用": ["试用文档", "默认文档", "临时笔记", "笔记"]
    }
    
    # 内容类型关键词
    CONTENT_KEYWORDS = {
        "学习": [
            # 基础学习关键词
            "学了", "知识点", "概念", "原理", "定义", 
            "这道题", "这题", "题目", "求解", "证明", "计算", "求",
            # 数学相关
            "不等式", "方程", "函数", "导数", "积分", "极限", "矩阵", "向量",
            "几何", "代数", "三角函数", "对数", "指数", "数列", "级数",
            "数学", "数学题", "数学问题",
            # 数学符号和表达式模式（需要特殊处理）
            # 注意：这些符号在 get_content_type 中需要特殊匹配逻辑
            # 物理相关
            "物理", "物理题", "力学", "电学", "光学", "热学", "量子",
            # 化学相关
            "化学", "化学式", "反应", "元素", "化合物",
            # 其他学科
            "生物", "英语", "语文", "历史", "地理",
            # 数学术语和解题方法
            "分情况讨论", "分类讨论", "讨论", "解集", "定义域", "值域",
            "单调性", "奇偶性", "周期性", "对称性",
            "最大值", "最小值", "极值", "零点", "交点",
            "因式分解", "配方法", "换元法", "待定系数法"
        ],
        "工作": ["会议", "项目", "任务", "工作", "工作要点", "会议记录", "会议要点"],
        "灵感": ["灵感", "想法", "创意", "思路", "想到"],
        "生活": ["生活", "日常", "日记", "今天", "明天", "发生了"]
    }
    
    @staticmethod
    def get_document_type(doc_name):
        """根据文档名称获取文档类型"""
        if not doc_name:
            return "通用"
        
        doc_name_lower = doc_name.lower()
        for doc_type, keywords in DocumentMatcher.DOCUMENT_TYPES.items():
            for keyword in keywords:
                if keyword in doc_name_lower:
                    return doc_type
        return "通用"
    
    @staticmethod
    def get_content_type(content):
        """根据内容识别内容类型"""
        if not content:
            return None
        
        content_lower = content.lower()
        
        # 首先检查关键词匹配
        for content_type, keywords in DocumentMatcher.CONTENT_KEYWORDS.items():
            for keyword in keywords:
                if keyword in content_lower:
                    return content_type
        
        # 如果没有匹配到关键词，检查是否包含数学表达式模式
        # 数学表达式特征：包含变量（x, y, z等）和数学符号（<, >, =, |, +, -, *, /等）
        math_patterns = [
            r'[xyz]\s*[<>=≤≥≠±]',  # 变量与比较符号，如 "x < 5", "y >= 3"
            r'[<>=≤≥≠]\s*[xyz]',  # 比较符号与变量，如 "< x", "= y"
            r'\|[xyz]\s*[+-]\s*\d+\|',  # 绝对值表达式，如 "|x - 3|", "|y + 5|"
            r'[xyz]\s*[+-]\s*\d+\s*[<>=≤≥≠]',  # 变量加减常数与比较，如 "x - 3 < 5"
            r'[<>=≤≥≠]\s*\d+\s*[<>=≤≥≠]\s*[xyz]',  # 区间表示，如 "-2 < x < 8"
            r'[xyz]\s*\^',  # 幂次，如 "x^2", "y^3"
            r'[xyz]\s*[*/]\s*[xyz]',  # 变量运算，如 "x/y", "x*z"
            r'\([xyz]\s*[+-]\s*\d+\)',  # 括号表达式，如 "(x + 3)", "(y - 2)"
        ]
        
        import re
        for pattern in math_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return "学习"
        
        return None
    
    @staticmethod
    def check_match(doc_type, content_type, is_empty):
        """检查文档与内容是否匹配"""
        if doc_type == "通用" or is_empty:
            return "partial"
        if content_type is None:
            return "partial"
        if doc_type == content_type:
            return "perfect"
        return "mismatch"
    
    @staticmethod
    def generate_confirmation_message(doc_name, doc_type, content_type, match_degree):
        """生成确认提示消息"""
        if match_degree == "perfect":
            return None
        
        # 文档类型和内容类型的友好名称
        doc_type_name = {
            "学习": "学习笔记",
            "工作": "工作笔记",
            "灵感": "灵感笔记",
            "生活": "生活笔记",
            "通用": "通用文档"
        }.get(doc_type, doc_name)
        
        content_type_name = {
            "学习": "学习相关的内容",
            "工作": "工作相关的内容",
            "灵感": "灵感相关的内容",
            "生活": "生活相关的内容"
        }.get(content_type, "此内容")
        
        # 建议新建文档名称
        suggested_doc_name = {
            "学习": "学习笔记",
            "工作": "工作笔记",
            "灵感": "灵感笔记",
            "生活": "生活笔记"
        }.get(content_type, "新文档")
        
        if match_degree == "partial":
            # 部分匹配：文档类型和内容类型不完全匹配
            return f"⚠️ 内容类型不匹配\n\n当前文档「{doc_name}」是{doc_type_name}类型\n您要添加的是{content_type_name}\n\n💡 建议新建文档「{suggested_doc_name}」"
        elif match_degree == "mismatch":
            # 完全不匹配：文档类型和内容类型完全不匹配
            return f"⚠️ 内容类型不匹配\n\n当前文档「{doc_name}」是{doc_type_name}类型\n您要添加的是{content_type_name}\n\n💡 建议新建文档「{suggested_doc_name}」"
        
        return None
    
    @staticmethod
    def get_suggested_doc_name(content_type):
        """获取建议的文档名称"""
        return {
            "学习": "学习笔记",
            "工作": "工作笔记",
            "灵感": "灵感笔记",
            "生活": "生活笔记"
        }.get(content_type, "新文档")

