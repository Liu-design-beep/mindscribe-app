# smart_classifier.py
# 智能内容分类和主题识别

import os
import json
import re
from typing import Dict, Tuple, Optional
from dashscope import Application
from config import API_KEY, APP_ID

class SmartClassifier:
    """
    使用 LLM 进行智能内容分类
    """
    
    # 关键词匹配规则
    KEYWORD_RULES = {
        "物理": ["物理", "量子", "相对论", "力学", "热学", "光学", "电磁", "原子", "分子", "粒子"],
        "化学": ["化学", "元素", "反应", "分子", "原子", "化合物", "溶液", "酸碱"],
        "生物": ["生物", "生命", "细胞", "基因", "进化", "DNA", "RNA", "蛋白质", "酶"],
        "数学": ["数学", "几何", "代数", "微积分", "方程", "函数", "概率", "统计", "矩阵"],
        "英语": ["英语", "单词", "语法", "翻译", "词汇", "阅读", "写作"],
        "历史": ["历史", "古代", "近代", "朝代", "战争", "革命"],
        "地理": ["地理", "地图", "国家", "城市", "气候", "地形"],
        "工作": ["工作", "项目", "开发", "发布", "版本", "功能", "任务", "会议", "进度", "计划"],
        "项目": ["项目", "开发", "发布", "版本", "功能", "需求", "设计", "测试"],
        "会议": ["会议", "讨论", "参会", "要点", "决议", "记录"],
        "任务": ["任务", "待办", "完成", "截止", "计划", "执行"],
        "灵感": ["想法", "创意", "灵感", "思考", "启发"],
        "生活": ["日常", "健康", "娱乐", "购物", "旅行", "美食"],
    }
    
    def __init__(self, api_key: Optional[str] = None, app_id: Optional[str] = None):
        """
        初始化分类器
        
        Args:
            api_key: API 密钥（默认使用 config.py 中的）
            app_id: 应用 ID（默认使用 config.py 中的）
        """
        self.api_key = api_key or API_KEY
        self.app_id = app_id or APP_ID
    
    def classify_content(self, content: str, available_sections: Dict[str, list] = None) -> Tuple[str, Optional[str]]:
        """
        使用关键词匹配和 LLM 分类内容并返回建议的主题和子主题
        
        Args:
            content: 用户输入的内容
            available_sections: 文档中已有的章节 {"物理": [...], "数学": [...]}
        
        Returns:
            (主题, 子主题) 如 ("物理", "量子计算")
        """
        # 首先尝试关键词匹配
        matched_section = self._keyword_match(content)
        if matched_section:
            # 尝试提取子主题
            subsection = self._extract_subsection(content, matched_section)
            return matched_section, subsection
        
        # 如果关键词匹配失败，使用 LLM
        return self._llm_classify(content, available_sections)
    
    def _keyword_match(self, content: str) -> Optional[str]:
        """
        基于关键词的快速匹配
        
        Returns:
            匹配到的主题，或 None
        """
        content_lower = content.lower()
        
        # 按优先级匹配（更具体的主题优先）
        priority_order = ["项目", "会议", "任务", "物理", "化学", "生物", "数学", "英语", "历史", "地理", "工作", "灵感", "生活"]
        
        for section in priority_order:
            if section in self.KEYWORD_RULES:
                keywords = self.KEYWORD_RULES[section]
                for keyword in keywords:
                    if keyword in content_lower:
                        return section
        
        return None
    
    def _extract_subsection(self, content: str, section: str) -> Optional[str]:
        """
        从内容中提取子主题
        
        Args:
            content: 用户输入的内容
            section: 已确定的主题
        
        Returns:
            子主题，或 None
        """
        # 简单的启发式方法：查找冒号后的文本
        if "：" in content or ":" in content:
            # 尝试中文冒号和英文冒号
            for sep in ["：", ":"]:
                if sep in content:
                    parts = content.split(sep, 1)
                    if len(parts) > 1:
                        potential_subsection = parts[0].strip()
                        # 过滤掉过长的子主题（可能是完整句子）
                        if len(potential_subsection) < 20 and len(potential_subsection) > 0:
                            # 移除常见的开头词
                            potential_subsection = re.sub(r'^(今天|昨天|刚才|刚刚|现在|学习|了解|记录|添加|关于)', '', potential_subsection).strip()
                            if potential_subsection:
                                return potential_subsection
        
        # 尝试从内容中提取可能的子主题关键词
        subsection_keywords = {
            "物理": ["量子", "相对论", "力学", "热学", "光学", "电磁"],
            "数学": ["几何", "代数", "微积分", "方程", "函数", "概率"],
            "工作": ["项目", "会议", "任务", "进度"],
            "项目": ["前端", "后端", "数据库", "API", "UI", "UX"],
        }
        
        if section in subsection_keywords:
            content_lower = content.lower()
            for keyword in subsection_keywords[section]:
                if keyword in content_lower:
                    return keyword
        
        return None
    
    def _llm_classify(self, content: str, available_sections: Dict[str, list] = None) -> Tuple[str, Optional[str]]:
        """
        使用 LLM 进行分类
        
        Args:
            content: 用户输入的内容
            available_sections: 文档中已有的章节
        
        Returns:
            (主题, 子主题)
        """
        available_sections_str = ""
        if available_sections:
            available_sections_str = "\n\n已有的章节：\n" + "\n".join([f"- {section}" for section in available_sections.keys()])
        
        prompt = f"""请分析以下内容，并建议应该放在哪个主题下。

内容："{content}"
{available_sections_str}

请返回 JSON 格式的结果，包含以下字段：
- section: 主题（如"物理"、"数学"、"工作"、"灵感"、"生活"等）
- subsection: 子主题（可选，如"量子计算"、"项目A"等）

示例：
{{"section": "物理", "subsection": "量子计算"}}

只返回 JSON，不要其他文本。"""
        
        try:
            response = Application.call(
                api_key=self.api_key,
                app_id=self.app_id,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            if response.status_code == 200:
                result_text = response.output.text if hasattr(response.output, 'text') else str(response.output)
                result_text = result_text.strip()
                
                # 尝试提取 JSON
                json_match = re.search(r'\{[^}]+\}', result_text)
                if json_match:
                    result = json.loads(json_match.group())
                else:
                    result = json.loads(result_text)
                
                section = result.get("section", "其他")
                subsection = result.get("subsection")
                
                return section, subsection
            else:
                print(f"[警告] LLM 分类失败，状态码: {response.status_code}")
                return "其他", None
        except json.JSONDecodeError as e:
            print(f"[警告] LLM 返回格式错误: {e}，使用默认分类")
            return "其他", None
        except Exception as e:
            print(f"[警告] LLM 分类失败: {e}，使用默认分类")
            return "其他", None














