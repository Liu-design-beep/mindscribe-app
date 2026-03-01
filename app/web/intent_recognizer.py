# intent_recognizer.py
# LLM意图识别模块 (LLM Intent Recognition Module)

import json
import re
from http import HTTPStatus
from dashscope import Application
from config import API_KEY, APP_ID

# 尝试导入 VectorStore（RAG 功能）
try:
    from vector_store import VectorStore
    VECTOR_STORE_AVAILABLE = True
except ImportError:
    try:
        from web.vector_store import VectorStore
        VECTOR_STORE_AVAILABLE = True
    except ImportError:
        VECTOR_STORE_AVAILABLE = False
        VectorStore = None

class LLMIntentRecognizer:
    def __init__(self, doc_manager, client_config, vector_store=None, session_id: str = ""):
        self.doc_manager = doc_manager
        self.client_config = client_config
        # 维护对话历史的 messages 数组
        self.messages = []
        # RAG 向量存储（可选，不传则降级）
        self.vector_store = vector_store
        # 当前会话 ID（用于向量检索过滤）
        self.session_id: str = session_id
        
        # ============================================================
        # 系统提示词配置说明
        # ============================================================
        # 系统提示词（System Prompt）现在在阿里云百炼应用中配置
        # 请在阿里云百炼控制台的"应用配置"中修改系统提示词
        # 本地参考文件：system_prompt_full.md（仅作为备份和参考）
        # 
        # 注意：
        # 1. 云端配置的系统提示词会覆盖代码中的任何设置
        # 2. 如果需要在系统提示词中包含动态上下文（如当前文档列表），
        #    可以在云端配置时使用占位符，或通过 messages 数组传递
        # 3. 当前代码不再维护 system_prompt 变量
        # ============================================================
    
    def reset_conversation(self):
        """
        重置对话历史，清空 messages 数组
        用于解决对话历史中可能包含错误格式（如双大括号）的问题
        """
        self.messages = []
        print("[系统提示] 对话历史已重置")
    
    def _extract_json(self, text):
        """
        从文本中提取JSON内容，处理各种可能的格式
        """
        if not text or not text.strip():
            return ""
        
        print(f"[调试] _extract_json 输入文本长度: {len(text)} 字符")
        print(f"[调试] _extract_json 输入文本前200字符: {text[:200]}")
        
        # 1. 尝试提取 markdown 代码块中的 JSON（支持多行和格式不完整的情况）
        # 处理完整的代码块：```json ... ```
        # 注意：使用非贪婪匹配可能导致问题，改为使用平衡括号匹配
        json_block_pattern = r'```(?:json)?\s*(\{[\s\S]*?\})\s*```'
        match = re.search(json_block_pattern, text, re.MULTILINE)
        if match:
            print(f"[调试] _extract_json 步骤1: 在markdown代码块中找到匹配")
            extracted = match.group(1).strip()
            print(f"[调试] _extract_json 步骤1: 提取的内容前50字符: {extracted[:50]}")
            print(f"[调试] _extract_json 步骤1: 是否以{{开头: {extracted.startswith('{')}")
            print(f"[调试] _extract_json 步骤1: 是否以{{{{开头: {extracted.startswith('{{')}")
            # 验证提取的内容：确保括号匹配，且是单大括号开头
            if extracted and extracted.startswith('{') and not extracted.startswith('{{'):
                # 检查括号是否匹配
                brace_count = extracted.count('{') - extracted.count('}')
                print(f"[调试] _extract_json 步骤1: 括号计数差: {brace_count}")
                if brace_count == 0:
                    print(f"[调试] _extract_json 步骤1: 返回提取的内容（括号匹配）")
                    return extracted
                else:
                    # 如果括号不匹配，尝试找到匹配的结束位置
                    brace_count = 0
                    json_end = -1
                    for i, char in enumerate(extracted):
                        if char == '{':
                            brace_count += 1
                        elif char == '}':
                            brace_count -= 1
                            if brace_count == 0:
                                json_end = i
                                break
                    if json_end > 0:
                        result = extracted[:json_end + 1]
                        print(f"[调试] _extract_json 步骤1: 返回修正后的内容（找到匹配的结束位置）")
                        return result
            else:
                print(f"[调试] _extract_json 步骤1: 提取的内容不符合要求（双大括号或格式错误），继续查找")
        
        # 1.1 处理不完整的代码块（只有开头标记，没有结尾）
        # 匹配 ```json 或 ``` 后面的内容，直到找到完整的JSON对象
        incomplete_block_pattern = r'```(?:json)?\s*\n?\s*(\{[\s\S]*?\})'
        match = re.search(incomplete_block_pattern, text, re.MULTILINE)
        if match:
            print(f"[调试] _extract_json 步骤1.1: 在不完整代码块中找到匹配")
            extracted = match.group(1).strip()
            print(f"[调试] _extract_json 步骤1.1: 提取的内容前50字符: {extracted[:50]}")
            print(f"[调试] _extract_json 步骤1.1: 是否以{{{{开头: {extracted.startswith('{{')}")
            # 验证：确保是单大括号开头，不是双大括号
            if extracted.startswith('{{'):
                # 如果是双大括号，跳过这个匹配，继续查找
                print(f"[调试] _extract_json 步骤1.1: 检测到双大括号，跳过此匹配")
                pass
            else:
                # 找到匹配的最后一个 }
                brace_count = 0
                json_end = -1
                for i, char in enumerate(extracted):
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            json_end = i
                            break
                if json_end > 0:
                    extracted = extracted[:json_end + 1]
                if extracted and extracted.startswith('{') and not extracted.startswith('{{'):
                    print(f"[调试] _extract_json 步骤1.1: 返回提取的内容")
                    return extracted
        
        # 2. 尝试找到第一个 { 到匹配的最后一个 } 之间的内容（支持嵌套）
        # 注意：跳过双大括号，只查找单大括号
        json_start = -1
        for i in range(len(text) - 1):
            if text[i] == '{' and text[i+1] != '{':
                # 找到单大括号开头
                json_start = i
                break
        
        if json_start >= 0:
            # 从第一个 { 开始，找到匹配的最后一个 }
            brace_count = 0
            json_end = -1
            for i in range(json_start, len(text)):
                if text[i] == '{':
                    brace_count += 1
                elif text[i] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        json_end = i
                        break
            
            if json_end > json_start:
                json_text = text[json_start:json_end + 1].strip()
                # 验证是否是有效的JSON结构（括号匹配，且是单大括号）
                if json_text and json_text.startswith('{') and not json_text.startswith('{{') and json_text.endswith('}'):
                    if json_text.count('{') == json_text.count('}'):
                        return json_text
        
        # 3. 尝试查找行内的JSON（可能没有换行）
        # 查找类似 {"key": "value"} 这样的简单JSON
        simple_json_pattern = r'\{[^{}]*"[^{}]*"[^{}]*\}'
        match = re.search(simple_json_pattern, text)
        if match:
            return match.group(0).strip()
        
        # 4. 如果都没找到，返回原始文本（去除首尾空白）
        result = text.strip()
        # 如果结果为空或太短，返回空字符串
        if len(result) < 2 or not result.startswith('{'):
            return ""
        return result
    
    def _fix_json_format(self, json_text):
        """
        尝试修复常见的JSON格式问题
        """
        original_text = json_text  # 保存原始文本用于调试
        
        print(f"[调试] _fix_json_format 输入: {json_text[:100]}")
        print(f"[调试] _fix_json_format 输入长度: {len(json_text)}")
        print(f"[调试] _fix_json_format 是否以{{{{开头: {json_text.startswith('{{')}")
        print(f"[调试] _fix_json_format 是否以}}结尾: {json_text.endswith('}}')}")
        
        # 移除可能的 BOM 标记
        if json_text.startswith('\ufeff'):
            json_text = json_text[1:]
        
        # 先去除首尾空白字符，确保判断准确
        json_text_stripped = json_text.strip()
        print(f"[调试] _fix_json_format 去除空白后: {json_text_stripped[:100]}")
        # 修复 f-string 语法错误：将包含反斜杠的表达式提取到变量中
        starts_with_brace_quote = json_text_stripped.startswith('{"')
        ends_with_quote_brace = json_text_stripped.endswith('}"')
        starts_with_double_brace = json_text_stripped.startswith('{{')
        ends_with_double_brace = json_text_stripped.endswith('}}')
        print(f"[调试] _fix_json_format 去除空白后是否以{{\"开头: {starts_with_brace_quote}")
        print(f"[调试] _fix_json_format 去除空白后是否以}}\"结尾: {ends_with_quote_brace}")
        print(f"[调试] _fix_json_format 去除空白后是否以{{{{开头: {starts_with_double_brace}")
        print(f"[调试] _fix_json_format 去除空白后是否以}}结尾: {ends_with_double_brace}")
        
        # 修复双大括号问题：{{"key": "value"}} -> {"key": "value"}
        # 这是云端系统提示词配置问题导致的，LLM返回了双大括号格式
        # 处理以 {{" 开头，以 }}" 结尾的双大括号JSON
        if json_text_stripped.startswith('{{"') and json_text_stripped.endswith('}}"'):
            # 去掉最外层的双大括号：去掉开头的 {{ 和结尾的 }}
            json_text = json_text_stripped[2:]  # 去掉开头的 {{
            json_text = json_text[:-2]  # 去掉结尾的 }}
            print(f"[调试] _fix_json_format 检测到双大括号格式（{{{{\"开头），已修复")
            print(f"[调试] _fix_json_format 修复后: {json_text[:100]}")
        # 处理其他可能的双大括号格式（以 {{ 开头但不一定是 {{"）
        elif json_text_stripped.startswith('{{') and json_text_stripped.endswith('}}'):
            # 更通用的处理：去掉最外层的一对大括号
            # 但要小心，确保不会破坏内部的JSON结构
            # 简单方法：如果开头是 {{ 且结尾是 }}，去掉各一个
            json_text = json_text_stripped[1:]  # 去掉第一个 {
            json_text = json_text[:-1]  # 去掉最后一个 }
            print(f"[调试] _fix_json_format 检测到双大括号格式（通用{{{{），已修复")
            print(f"[调试] _fix_json_format 修复后: {json_text[:100]}")
        else:
            print(f"[调试] _fix_json_format 前两个条件都不匹配，尝试备用方法")
            # 如果开头和结尾不匹配，尝试更激进的修复：直接替换双大括号
            if '{{' in json_text and '}}' in json_text:
                print(f"[调试] _fix_json_format 检测到文本中包含{{{{和}}")
                # 只在最外层替换一次
                if json_text.count('{{') == 1 and json_text.count('}}') == 1:
                    json_text = json_text.replace('{{', '{', 1).rsplit('}}', 1)[0] + '}'
                    print(f"[调试] _fix_json_format 使用替换方法修复双大括号")
                    print(f"[调试] _fix_json_format 修复后: {json_text[:100]}")
                else:
                    print(f"[调试] _fix_json_format 双大括号数量不唯一，无法使用替换方法")
            else:
                print(f"[调试] _fix_json_format 文本中不包含{{{{或}}")
        
        # 尝试修复单引号（将单引号替换为双引号，但要小心处理字符串内容）
        # 这是一个简单的修复，可能不适用于所有情况
        json_text = json_text.replace("'", '"')
        
        # 移除可能的尾随逗号（在对象或数组的最后一个元素后）
        json_text = re.sub(r',\s*}', '}', json_text)
        json_text = re.sub(r',\s*]', ']', json_text)
        
        print(f"[调试] _fix_json_format 最终返回: {json_text[:100]}")
        print(f"[调试] _fix_json_format 最终返回长度: {len(json_text)}")
        print(f"[调试] _fix_json_format 最终返回是否以{{开头: {json_text.startswith('{')}")
        print(f"[调试] _fix_json_format 最终返回是否以}}结尾: {json_text.endswith('}')}")
        print(f"[调试] _fix_json_format 最终返回是否以{{{{开头: {json_text.startswith('{{')}")
        print(f"[调试] _fix_json_format 最终返回是否以}}}}结尾: {json_text.endswith('}}')}")
        
        return json_text
    
    def _normalize_intent_data(self, intent_data):
        """
        将新的JSON Schema格式转换为兼容旧代码的格式
        支持新旧两种格式的自动转换
        """
        # 首先保存原始的 intent_type（在处理前保存，避免丢失）
        original_intent_type_raw = intent_data.get("intent_type")
        intent_from_field = intent_data.get("intent")
        
        print("="*80)
        print("[调试] ⭐⭐⭐ _normalize_intent_data函数开始执行 ⭐⭐⭐")
        print(f"[调试] 转换前的intent_data (llm_response): {intent_data}")
        print(f"[调试] intent_data类型: {type(intent_data)}")
        print(f"[调试] intent_data的所有keys: {list(intent_data.keys())}")
        print(f"[调试] intent_data.get('intent_type'): {intent_data.get('intent_type')}")
        print(f"[调试] intent_data.get('intent_type')类型: {type(intent_data.get('intent_type'))}")
        print(f"[调试] intent_data.get('intent_type')是否为None: {intent_data.get('intent_type') is None}")
        print(f"[调试] 'intent_type' in intent_data: {'intent_type' in intent_data}")
        print(f"[意图识别] _normalize_intent_data: 输入intent_data中的intent_type={original_intent_type_raw}, intent={intent_from_field}, 完整keys={list(intent_data.keys())}")
        print(f"[意图识别] _normalize_intent_data: 输入intent_data完整内容: {intent_data}")
        print("="*80)
        
        # 检查是否需要重新转换（当 intent 是 UNKNOWN 但 intent_type 不是 UNKNOWN 时）
        intent_from_type = intent_data.get("intent_type")
        need_reconvert = False
        
        if "intent" in intent_data and "intent_type" in intent_data:
            # 如果 intent_type 存在且不是 UNKNOWN，而 intent 是 UNKNOWN，需要重新转换
            if intent_from_type and str(intent_from_type).upper() != "UNKNOWN" and intent_from_field == "UNKNOWN":
                print(f"[意图识别] 检测到 intent='UNKNOWN' 但 intent_type='{intent_from_type}'，将重新转换")
                need_reconvert = True
        
        # 关键修复：如果 intent_type 存在且不是 UNKNOWN，即使 intent 是 UNKNOWN 或不存在，也应该继续转换
        # 不要早期返回，确保 intent_type 被正确处理
        # 只有当 intent 存在且不是 UNKNOWN，并且 intent_type 也存在且匹配时，才可以直接返回
        if "intent" in intent_data and not need_reconvert and intent_from_field and intent_from_field != "UNKNOWN":
            # 确保 intent_type 也被保留
            if "intent_type" not in intent_data:
                # 如果没有 intent_type，尝试从 intent 反推
                if original_intent_type_raw:
                    intent_data["intent_type"] = str(original_intent_type_raw).strip().upper()
                    print(f"[意图识别] _normalize_intent_data: 从原始值添加intent_type={intent_data['intent_type']}")
                elif intent_from_type:
                    intent_data["intent_type"] = str(intent_from_type).strip().upper()
                    print(f"[意图识别] _normalize_intent_data: 从intent_from_type添加intent_type={intent_data['intent_type']}")
            # 关键修复：确保 intent_type 字段存在，优先使用 original_intent_type_raw
            if original_intent_type_raw:
                intent_data["intent_type"] = str(original_intent_type_raw).strip().upper()
                print(f"[意图识别] _normalize_intent_data: ✅ 强制设置intent_type={intent_data['intent_type']} (从original_intent_type_raw)")
            elif "intent_type" not in intent_data or intent_data.get("intent_type") is None:
                # 如果还是没有，使用默认值
                intent_data["intent_type"] = "UNKNOWN"
                print(f"[意图识别] _normalize_intent_data: ⚠️ 无法获取intent_type，使用默认值UNKNOWN")
            # 关键修复：即使有 intent 字段，如果 intent_type 是 GREETING 但 intent 不是 GREETING，也需要重新转换
            if original_intent_type_raw and str(original_intent_type_raw).strip().upper() == "GREETING":
                if intent_from_field != "GREETING":
                    print(f"[意图识别] _normalize_intent_data: 检测到intent_type=GREETING但intent={intent_from_field}，需要重新转换")
                    need_reconvert = True
                else:
                    print(f"[意图识别] _normalize_intent_data: 直接返回旧格式, intent={intent_from_field}, intent_type={intent_data.get('intent_type')}")
                    # 关键修复：确保返回的字典包含 intent_type
                    if "intent_type" not in intent_data or intent_data.get("intent_type") is None:
                        intent_data["intent_type"] = str(original_intent_type_raw).strip().upper() if original_intent_type_raw else "UNKNOWN"
                    return intent_data
            else:
                print(f"[意图识别] _normalize_intent_data: 直接返回旧格式, intent={intent_from_field}, intent_type={intent_data.get('intent_type')}")
                # 关键修复：确保返回的字典包含 intent_type
                if "intent_type" not in intent_data or intent_data.get("intent_type") is None:
                    intent_data["intent_type"] = str(original_intent_type_raw).strip().upper() if original_intent_type_raw else "UNKNOWN"
                return intent_data
        
        # 关键修复：如果 intent_type 存在且不是 UNKNOWN，但 intent 是 UNKNOWN 或不存在，强制重新转换
        if original_intent_type_raw and str(original_intent_type_raw).upper() != "UNKNOWN":
            if not intent_from_field or intent_from_field == "UNKNOWN":
                print(f"[意图识别] _normalize_intent_data: 检测到intent_type='{original_intent_type_raw}'但intent='{intent_from_field}'，强制重新转换")
                need_reconvert = True
        
        # 新格式转换为旧格式
        normalized = {}
        
        # 关键修复：直接使用原始 intent_type，不要转换
        # 如果 intent_type 存在且不是 UNKNOWN，直接使用它
        if original_intent_type_raw and str(original_intent_type_raw).strip().upper() != "UNKNOWN":
            # 直接使用原始值，不进行映射转换
            intent_type_for_mapping = str(original_intent_type_raw).strip().upper()
            print(f"[意图识别] _normalize_intent_data: 直接使用原始intent_type={intent_type_for_mapping}")
        else:
            # 如果原始值为空，尝试从 intent_data 中获取
            intent_type_for_mapping = intent_data.get("intent_type")
            if intent_type_for_mapping and str(intent_type_for_mapping).strip().upper() != "UNKNOWN":
                intent_type_for_mapping = str(intent_type_for_mapping).strip().upper()
                print(f"[意图识别] _normalize_intent_data: 从intent_data中获取intent_type={intent_type_for_mapping}")
            else:
                # 如果都没有，尝试从 intent 反推
                intent_value = intent_data.get("intent")
                if intent_value and intent_value != "UNKNOWN":
                    # 尝试从 intent 反推 intent_type（反向映射）
                    reverse_mapping = {
                        "ADD_CONTENT": "ADD",
                        "EDIT_CONTENT": "EDIT",
                        "MOVE_CONTENT": "MOVE",
                        "DELETE_CONTENT": "DELETE",
                        "DISPLAY_DOC": "QUERY",
                        "SUMMARY": "SUMMARY",
                        "SET_ACTIVE": "SET_ACTIVE",
                        "GREETING": "GREETING",
                        "HELP": "HELP",
                        "EXIT": "EXIT",
                        "CONFIRM": "CONFIRM",
                        "CANCEL": "CANCEL",
                        "RESET_CONVERSATION": "RESET_CONVERSATION",
                        "CREATE_DOCUMENT": "CREATE_DOCUMENT"
                    }
                    intent_type_for_mapping = reverse_mapping.get(intent_value, "UNKNOWN")
                    print(f"[意图识别] _normalize_intent_data: 从intent反推intent_type={intent_type_for_mapping}")
                else:
                    intent_type_for_mapping = "UNKNOWN"
                    print(f"[意图识别] _normalize_intent_data: 使用默认值UNKNOWN")
        
        # 类型检查和转换：确保 intent_type_for_mapping 是字符串
        if not intent_type_for_mapping or intent_type_for_mapping is None:
            intent_type_for_mapping = "UNKNOWN"
        elif not isinstance(intent_type_for_mapping, str):
            try:
                intent_type_for_mapping = str(intent_type_for_mapping).upper()
            except Exception:
                intent_type_for_mapping = "UNKNOWN"
        else:
            intent_type_for_mapping = intent_type_for_mapping.upper()
        
        # 意图映射：将 intent_type 映射到 intent
        intent_mapping = {
            "ADD": "ADD_CONTENT",
            "EDIT": "EDIT_CONTENT",
            "MOVE": "MOVE_CONTENT",
            "DELETE": "DELETE_CONTENT",
            "QUERY": "DISPLAY_DOC",
            "SUMMARY": "SUMMARY",
            "SET_ACTIVE": "SET_ACTIVE",
            "GREETING": "GREETING",  # 问候/打招呼 - 直接映射，不转换
            "HELP": "HELP",
            "EXIT": "EXIT",
            "CONFIRM": "CONFIRM",
            "CANCEL": "CANCEL",
            "RESET_CONVERSATION": "RESET_CONVERSATION",
            "CREATE_DOCUMENT": "CREATE_DOCUMENT",
            "UNKNOWN": "UNKNOWN"
        }
        
        # 关键修复：如果 intent_type_for_mapping 是 "GREETING"，直接设置为 "GREETING"，不要通过映射
        if intent_type_for_mapping == "GREETING":
            normalized["intent"] = "GREETING"
            print(f"[意图识别] _normalize_intent_data: 直接设置intent=GREETING（不通过映射）")
        else:
            normalized["intent"] = intent_mapping.get(intent_type_for_mapping, "UNKNOWN")
            print(f"[意图识别] _normalize_intent_data: 通过映射设置intent={normalized['intent']}, intent_type_for_mapping={intent_type_for_mapping}")
        
        # 关键修复：直接使用原始 intent_type，确保不被覆盖
        # 优先使用 original_intent_type_raw（在处理前保存的原始值）
        print(f"[意图识别] _normalize_intent_data: 保存的原始intent_type_raw={original_intent_type_raw}, 处理后的intent_type_for_mapping={intent_type_for_mapping}")
        
        # 关键修复：确保 intent_type 字段一定被设置，优先使用 original_intent_type_raw
        # 注意：即使 original_intent_type_raw 是 None，也要尝试从 intent_data 中获取
        if original_intent_type_raw is not None:
            normalized["intent_type"] = str(original_intent_type_raw).strip().upper()
            print(f"[意图识别] _normalize_intent_data: ✅ 使用原始intent_type_raw={normalized['intent_type']}")
        # 如果原始值为None，尝试从intent_data中再次获取
        elif intent_data.get("intent_type") is not None:
            normalized["intent_type"] = str(intent_data.get("intent_type")).strip().upper()
            print(f"[意图识别] _normalize_intent_data: ✅ 从intent_data中获取intent_type={normalized['intent_type']}")
        # 如果都没有，使用处理后的 intent_type_for_mapping
        elif intent_type_for_mapping:
            normalized["intent_type"] = intent_type_for_mapping
            print(f"[意图识别] _normalize_intent_data: ✅ 使用处理后的intent_type_for_mapping={normalized['intent_type']}")
        else:
            # 如果都没有，使用 UNKNOWN，但确保字段存在
            normalized["intent_type"] = "UNKNOWN"
            print(f"[意图识别] _normalize_intent_data: ⚠️ 使用默认值UNKNOWN")
        
        # 关键修复：强制设置 intent_type，确保它一定存在
        if "intent_type" not in normalized or normalized.get("intent_type") is None:
            # 再次尝试从 original_intent_type_raw 或 intent_data 中获取
            if original_intent_type_raw:
                normalized["intent_type"] = str(original_intent_type_raw).strip().upper()
                print(f"[意图识别] _normalize_intent_data: ✅ [强制设置] 从original_intent_type_raw恢复intent_type={normalized['intent_type']}")
            elif intent_data.get("intent_type"):
                normalized["intent_type"] = str(intent_data.get("intent_type")).strip().upper()
                print(f"[意图识别] _normalize_intent_data: ✅ [强制设置] 从intent_data恢复intent_type={normalized['intent_type']}")
            else:
                normalized["intent_type"] = intent_type_for_mapping if intent_type_for_mapping else "UNKNOWN"
                print(f"[意图识别] _normalize_intent_data: ⚠️ [强制设置] 使用默认值UNKNOWN")
        
        # 关键修复：最终检查，确保 intent_type 字段一定存在
        if "intent_type" not in normalized:
            print(f"[意图识别] ⚠️ 严重错误：normalized字典中缺少intent_type字段！")
            # 强制设置 intent_type
            if original_intent_type_raw:
                normalized["intent_type"] = str(original_intent_type_raw).strip().upper()
            elif intent_data.get("intent_type"):
                normalized["intent_type"] = str(intent_data.get("intent_type")).strip().upper()
            else:
                normalized["intent_type"] = intent_type_for_mapping if intent_type_for_mapping else "UNKNOWN"
            print(f"[意图识别] ✅ 已强制添加intent_type: {normalized['intent_type']}")
        
        print(f"[意图识别] _normalize_intent_data: 最终normalized['intent']={normalized.get('intent')}, normalized['intent_type']={normalized.get('intent_type')}")
        
        # 字段映射
        normalized["doc_title"] = intent_data.get("target_document")
        normalized["content"] = intent_data.get("content_to_process")
        # 修复：添加 target_chapter 和 summary_scope 映射
        normalized["target_chapter"] = intent_data.get("target_chapter")
        normalized["summary_scope"] = intent_data.get("summary_scope")
        
        # 处理position：如果target_location_raw是None或不存在，默认为"end"
        position_raw = intent_data.get("target_location_raw")
        normalized["position"] = position_raw if position_raw is not None else "end"
        
        # 智能归类字段（新增）
        normalized["suggested_section"] = intent_data.get("suggested_section")
        normalized["suggested_subsection"] = intent_data.get("suggested_subsection")
        
        # 保留新格式的额外信息（用于未来扩展）
        normalized["context_dependency"] = intent_data.get("context_dependency", False)
        normalized["confirmation_needed"] = intent_data.get("confirmation_needed", False)
        normalized["system_action_required"] = intent_data.get("system_action_required", "")
        
        # 保留 message_style 字段（如果存在）
        if "message_style" in intent_data:
            normalized["message_style"] = intent_data.get("message_style")
        
        # 最终检查：确保 intent_type 字段存在
        if "intent_type" not in normalized:
            print(f"[意图识别] ⚠️ 警告：normalized字典中缺少intent_type字段！")
            print(f"[意图识别] normalized的所有keys: {list(normalized.keys())}")
            print(f"[意图识别] 尝试从intent_data中获取intent_type: {intent_data.get('intent_type')}")
            if intent_data.get("intent_type"):
                normalized["intent_type"] = str(intent_data.get("intent_type")).strip().upper()
                print(f"[意图识别] 已从intent_data中恢复intent_type: {normalized['intent_type']}")
            else:
                normalized["intent_type"] = "UNKNOWN"
                print(f"[意图识别] 无法恢复intent_type，使用默认值UNKNOWN")
        
        # 关键修复：返回前最终检查，确保 intent_type 字段一定存在
        if "intent_type" not in normalized or normalized.get("intent_type") is None:
            print(f"[意图识别] ⚠️ 严重错误：_normalize_intent_data返回前，normalized中缺少intent_type字段或为None！")
            print(f"[意图识别] normalized的所有keys: {list(normalized.keys())}")
            # 尝试从原始数据中恢复
            original_intent_type = intent_data.get("intent_type")
            if original_intent_type:
                normalized["intent_type"] = str(original_intent_type).strip().upper()
                print(f"[意图识别] ✅ 已从intent_data中恢复intent_type: {normalized['intent_type']}")
            else:
                normalized["intent_type"] = "UNKNOWN"
                print(f"[意图识别] ⚠️ 无法恢复intent_type，使用默认值UNKNOWN")
        
        print(f"[意图识别] _normalize_intent_data: 最终返回normalized的所有keys: {list(normalized.keys())}")
        print(f"[意图识别] _normalize_intent_data: 最终返回normalized['intent_type']={normalized.get('intent_type')}")
        
        print("="*80)
        print("[调试] ⭐⭐⭐ _normalize_intent_data函数执行完成 ⭐⭐⭐")
        print(f"[调试] 转换后的intent_data (normalized): {normalized}")
        print(f"[调试] normalized类型: {type(normalized)}")
        print(f"[调试] normalized的所有keys: {list(normalized.keys())}")
        print(f"[调试] normalized.get('intent_type'): {normalized.get('intent_type')}")
        print(f"[调试] normalized.get('intent'): {normalized.get('intent')}")
        print(f"[调试] normalized.get('intent_type')类型: {type(normalized.get('intent_type'))}")
        print(f"[调试] normalized.get('intent_type')是否为None: {normalized.get('intent_type') is None}")
        print(f"[调试] 'intent_type' in normalized: {'intent_type' in normalized}")
        print("="*80)
        
        # 关键修复：返回前再次验证
        if "intent_type" not in normalized:
            print(f"[意图识别] ⚠️ 严重错误：返回前最终检查，normalized中仍然缺少intent_type字段！")
            normalized["intent_type"] = str(intent_data.get("intent_type", "UNKNOWN")).strip().upper()
            print(f"[意图识别] ✅ 已强制添加intent_type: {normalized['intent_type']}")
        
        # 关键修复：统一的最终处理，确保返回的字典始终包含 intent_type 字段
        # 这是最后的保障，无论前面的逻辑如何，都要确保 intent_type 存在
        if "intent_type" not in normalized or normalized.get("intent_type") is None or normalized.get("intent_type") == "":
            # 优先使用 original_intent_type_raw（在处理前保存的原始值）
            if original_intent_type_raw:
                normalized["intent_type"] = str(original_intent_type_raw).strip().upper()
                print(f"[意图识别] ✅ [最终保障] 从original_intent_type_raw恢复intent_type: {normalized['intent_type']}")
            # 其次从 intent_data 中获取
            elif intent_data.get("intent_type"):
                normalized["intent_type"] = str(intent_data.get("intent_type")).strip().upper()
                print(f"[意图识别] ✅ [最终保障] 从intent_data恢复intent_type: {normalized['intent_type']}")
            # 最后使用默认值
            else:
                normalized["intent_type"] = "UNKNOWN"
                print(f"[意图识别] ⚠️ [最终保障] 使用默认值UNKNOWN")
        
        # 最终验证：确保 intent_type 字段确实存在且不为空
        assert "intent_type" in normalized, "严重错误：normalized字典中必须包含intent_type字段！"
        assert normalized.get("intent_type") is not None, "严重错误：normalized['intent_type']不能为None！"
        assert normalized.get("intent_type") != "", "严重错误：normalized['intent_type']不能为空字符串！"
        
        print(f"[意图识别] ✅ [最终验证] normalized字典包含intent_type字段: {normalized.get('intent_type')}")
        
        # 关键修复：在返回前最后一次强制检查，确保 intent_type 字段一定存在且正确
        # 这是最后的保障，无论前面的逻辑如何，都要确保 intent_type 存在
        if "intent_type" not in normalized or normalized.get("intent_type") is None or normalized.get("intent_type") == "":
            print(f"[意图识别] ⚠️ 严重错误：返回前最后一次检查，normalized中仍然缺少intent_type字段或为None/空！")
            print(f"[意图识别] normalized的所有keys: {list(normalized.keys())}")
            print(f"[意图识别] original_intent_type_raw: {original_intent_type_raw}")
            print(f"[意图识别] intent_data.get('intent_type'): {intent_data.get('intent_type')}")
            # 强制设置 intent_type
            if original_intent_type_raw:
                normalized["intent_type"] = str(original_intent_type_raw).strip().upper()
                print(f"[意图识别] ✅ [最后保障] 强制从original_intent_type_raw设置intent_type: {normalized['intent_type']}")
            elif intent_data.get("intent_type"):
                normalized["intent_type"] = str(intent_data.get("intent_type")).strip().upper()
                print(f"[意图识别] ✅ [最后保障] 强制从intent_data设置intent_type: {normalized['intent_type']}")
            else:
                normalized["intent_type"] = "UNKNOWN"
                print(f"[意图识别] ⚠️ [最后保障] 无法获取intent_type，使用默认值UNKNOWN")
        
        # 最终断言：确保 intent_type 字段确实存在且不为空
        assert "intent_type" in normalized, f"严重错误：normalized字典中必须包含intent_type字段！normalized的所有keys: {list(normalized.keys())}"
        assert normalized.get("intent_type") is not None, f"严重错误：normalized['intent_type']不能为None！original_intent_type_raw: {original_intent_type_raw}"
        assert normalized.get("intent_type") != "", f"严重错误：normalized['intent_type']不能为空字符串！original_intent_type_raw: {original_intent_type_raw}"
        
        print(f"[意图识别] ✅ [最终返回] normalized['intent']={normalized.get('intent')}, normalized['intent_type']={normalized.get('intent_type')}")
        print(f"[意图识别] ✅ [最终返回] normalized的所有keys: {list(normalized.keys())}")
        
        return normalized

    def recognize(self, user_input):
        """使用LLM识别用户意图并提取参数"""
        print("="*80)
        print("[调试] ⭐⭐⭐ recognize()函数开始执行 ⭐⭐⭐")
        print(f"[调试] 收到的user_input: {user_input}")
        print("="*80)
        
        if not self.client_config:
            print("=" * 60)
            print("[LLM错误] ⚠️ LLM配置未初始化，无法调用大语言模型！")
            print("=" * 60)
            print("[LLM错误] client_config 为 None")
            print("[LLM错误] 这通常是因为 config_local.py 未正确配置")
            print("[LLM错误] 或 get_llm_client() 返回了 None")
            print("=" * 60)
            return {
                "intent": "LLM_CONNECTION_ERROR",
                "content": "⚠️ 大语言模型连接失败：LLM配置未初始化。\n\n请检查后端服务器日志，确认 config_local.py 文件中的 API_KEY 和 APP_ID 是否正确配置。",
                "message_style": "error"
            }

        # 注意：系统提示词现在在阿里云百炼应用中配置
        # 如果需要在系统提示词中包含动态上下文（如当前文档列表），
        # 可以通过 messages 数组传递 system role 的消息来补充或覆盖云端配置
        # 当前实现：不在代码中传递 system role 消息，完全依赖云端配置
        
        # 如果需要动态上下文，可以在这里构建并添加到 messages
        # 例如：
        # doc_titles = ", ".join(self.doc_manager.get_document_titles())
        # active_doc = self.doc_manager.active_doc_title
        # context_info = f"当前可用的文档标题: {doc_titles}\n当前活跃文档: {active_doc}"
        # if not self.messages:
        #     self.messages.append({
        #         "role": "system",
        #         "content": context_info
        #     })
        
        # ── RAG：如果向量存储可用，先检索相关笔记片段并注入上下文 ──
        rag_info = {
            "enabled": bool(self.vector_store and self.vector_store.enabled),
            "status": "disabled",   # disabled | searched | empty | error
            "chunks_found": 0,
            "error": None
        }
        if self.vector_store and self.vector_store.enabled and self.session_id:
            rag_info["status"] = "searching"
            try:
                import asyncio
                # recognize() 是同步函数，使用 asyncio.run() 运行异步检索
                # 如果已有事件循环在运行（如 Jupyter），使用 nest_asyncio；否则直接 asyncio.run()
                try:
                    loop = asyncio.get_running_loop()
                    # 已有运行中的循环，创建新线程运行
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as pool:
                        future = pool.submit(
                            asyncio.run,
                            self.vector_store.search(
                                query=user_input,
                                session_id=self.session_id,
                                top_k=3
                            )
                        )
                        rag_chunks = future.result(timeout=10)
                except RuntimeError:
                    # 没有运行中的循环，直接创建新循环
                    rag_chunks = asyncio.run(
                        self.vector_store.search(
                            query=user_input,
                            session_id=self.session_id,
                            top_k=3
                        )
                    )

                if rag_chunks:
                    context_str = VectorStore.format_context(rag_chunks)
                    print(f"[RAG] ✅ 检索到 {len(rag_chunks)} 个相关片段，注入上下文")
                    rag_info["status"] = "searched"
                    rag_info["chunks_found"] = len(rag_chunks)
                    # 将笔记上下文作为 system 消息插入当前轮对话头部
                    rag_system_msg = {
                        "role": "system",
                        "content": context_str
                    }
                    if self.messages and self.messages[0].get("role") == "system":
                        self.messages[0] = rag_system_msg
                    else:
                        self.messages.insert(0, rag_system_msg)
                else:
                    print("[RAG] ⚠️ 未检索到相关笔记，使用原始提示词")
                    rag_info["status"] = "empty"
            except Exception as e:
                print(f"[RAG] ❌ 检索失败（不影响对话）: {e}")
                rag_info["status"] = "error"
                rag_info["error"] = str(e)[:100]

        # 将用户输入添加到 messages
        self.messages.append({
            "role": "user",
            "content": user_input
        })
        
        # 打印对话历史信息（用于调试去重功能）
        print("\n" + "="*60)
        print("[对话历史] 当前对话历史信息")
        print("-"*60)
        print(f"[对话历史] 消息总数: {len(self.messages)}")
        # 统计最近三次用户输入
        user_messages = [msg for msg in self.messages if msg.get("role") == "user"]
        recent_user_inputs = user_messages[-3:] if len(user_messages) >= 3 else user_messages
        print(f"[对话历史] 最近三次用户输入数量: {len(recent_user_inputs)}")
        for i, msg in enumerate(recent_user_inputs, 1):
            content_preview = msg.get("content", "")[:50] + ("..." if len(msg.get("content", "")) > 50 else "")
            print(f"[对话历史] 用户输入 #{i}: {content_preview}")
        print(f"[对话历史] 当前用户输入: {user_input[:50]}...")
        print("-"*60)
        
        try:
            # 调用阿里云百炼智能体应用，使用 messages 参数
            # 注意：如果应用已在应用内配置了知识库，知识库检索会自动启用，无需额外参数
            print("\n" + "="*60)
            print("[LLM调用] 开始调用阿里云百炼智能体应用")
            print("-"*60)
            print(f"[LLM调用] APP_ID: {self.client_config.get('app_id') or APP_ID}")
            print(f"[LLM调用] API_KEY: {(self.client_config.get('api_key') or API_KEY)[:8]}...")
            print(f"[LLM调用] 消息数量: {len(self.messages)}")
            print(f"[LLM调用] 最后一条用户消息: {self.messages[-1].get('content', '')[:100]}...")
            print("-"*60)
            
            response = Application.call(
                api_key=self.client_config.get("api_key") or API_KEY,
                app_id=self.client_config.get("app_id") or APP_ID,
                messages=self.messages
            )
            
            # 打印响应状态信息
            print(f"[LLM调用] 响应状态码: {response.status_code}")
            if hasattr(response, 'request_id'):
                print(f"[LLM调用] 请求ID: {response.request_id}")
            
            if response.status_code != HTTPStatus.OK:
                print("=" * 60)
                print("[LLM错误] ⚠️ 调用智能体应用失败")
                print("=" * 60)
                print(f"  request_id: {response.request_id}")
                print(f"  status_code: {response.status_code}")
                print(f"  message: {response.message}")
                if hasattr(response, 'code'):
                    print(f"  error_code: {response.code}")
                print("=" * 60)
                # API 调用失败，移除刚才添加的用户消息，避免对话历史不完整
                if self.messages and self.messages[-1].get("role") == "user":
                    self.messages.pop()
                # 返回明确的连接错误，而不是UNKNOWN
                error_msg = f"⚠️ 大语言模型连接失败（状态码: {response.status_code}）\n\n"
                if response.status_code == 401:
                    error_msg += "API Key 可能无效或已过期，请检查 config_local.py 中的 DASHSCOPE_API_KEY。"
                elif response.status_code == 404:
                    error_msg += "APP_ID 可能无效，请检查 config_local.py 中的 APP_ID。"
                elif response.status_code == 429:
                    error_msg += "API 调用频率超限，请稍后再试。"
                else:
                    error_msg += f"错误信息: {response.message}\n\n请检查后端日志获取详细信息。"
                return {
                    "intent": "LLM_CONNECTION_ERROR",
                    "content": error_msg,
                    "message_style": "error"
                }
            
            # 解析JSON输出
            output_text = response.output.text.strip()
            
            # ===== 调试信息：显示LLM的完整原始返回（JSON解析之前）=====
            print("\n" + "="*60)
            print("[LLM原始响应] ════════════════════════════════════════")
            print("[LLM原始响应] LLM 完整原始返回内容（JSON解析之前）:")
            print("[LLM原始响应] " + "-"*56)
            print("[LLM原始响应] " + output_text)
            print("[LLM原始响应] " + "-"*56)
            print(f"[LLM原始响应] 返回内容长度: {len(output_text)} 字符")
            print(f"[LLM原始响应] 是否包含{{: {output_text.count('{')}")
            print(f"[LLM原始响应] 是否包含}}: {output_text.count('}')}")
            print(f"[LLM原始响应] 是否包含intent_type: {'intent_type' in output_text}")
            print(f"[LLM原始响应] 是否包含GREETING: {'GREETING' in output_text.upper()}")
            print("[LLM原始响应] ════════════════════════════════════════")
            print()  # 空行
            
            # 将 AI 的回复添加到 messages 中，维护对话历史
            self.messages.append({
                "role": "assistant",
                "content": output_text
            })
            
            # 改进的JSON提取逻辑：处理各种可能的格式
            print("[调试] 开始提取JSON，原始文本前200字符:")
            print(output_text[:200])
            print()
            json_text = self._extract_json(output_text)
            
            print("[调试] 提取的JSON文本:")
            print("-"*60)
            if json_text:
                print(f"[调试] 提取的JSON文本长度: {len(json_text)} 字符")
                print(f"[调试] 提取的JSON文本开头10字符: {json_text[:10]}")
                print(f"[调试] 提取的JSON文本结尾10字符: {json_text[-10:]}")
                print(f"[调试] 提取的JSON是否以{{开头: {json_text.startswith('{')}")
                print(f"[调试] 提取的JSON是否以}}结尾: {json_text.endswith('}')}")
                print(f"[调试] 提取的JSON中{{的数量: {json_text.count('{')}")
                print(f"[调试] 提取的JSON中}}的数量: {json_text.count('}')}")
                # 尝试格式化JSON以便阅读
                try:
                    import json as json_module
                    formatted_json = json_module.dumps(json_module.loads(json_text), ensure_ascii=False, indent=2)
                    print("[调试] JSON格式验证成功，格式化后:")
                    print(formatted_json)
                except Exception as e:
                    # 如果无法格式化，显示原始文本（限制长度）
                    print(f"[调试] JSON格式验证失败: {e}")
                    print("[调试] 原始提取的文本:")
                    print(json_text[:500] + ("..." if len(json_text) > 500 else ""))
            else:
                print("(空)")
            print("-"*60)
            print()  # 空行
            
            # 检查提取的 JSON 是否为空
            if not json_text or not json_text.strip():
                print(f"[LLM错误] 无法从输出中提取JSON内容")
                print(f"[LLM错误] 原始输出完整内容:")
                print(output_text)
                print(f"[LLM错误] 原始输出类型: {type(output_text)}")
                # 降级处理
                if re.search(r"(退出|再见|结束)", user_input):
                    return {"intent": "EXIT"}
                if re.search(r"(帮助|能做什么|怎么用)", user_input):
                    return {"intent": "HELP"}
                return {"intent": "UNKNOWN"}
            
            # 尝试解析JSON
            try:
                intent_data = json.loads(json_text)
                print("[调试] JSON解析成功:")
                print("-"*60)
                import json as json_module
                print(json_module.dumps(intent_data, ensure_ascii=False, indent=2))
                print("-"*60)
                print(f"[调试] ⭐⭐⭐ JSON解析后的intent_data ⭐⭐⭐")
                print(f"[调试] JSON解析后, intent_data类型: {type(intent_data)}")
                print(f"[调试] JSON解析后, intent_data完整内容: {intent_data}")
                print(f"[调试] JSON解析后, intent_data的所有keys: {list(intent_data.keys())}")
                print(f"[调试] JSON解析后, intent_data.get('intent_type')={intent_data.get('intent_type')}")
                print(f"[调试] JSON解析后, intent_data.get('intent')={intent_data.get('intent')}")
                print(f"[调试] JSON解析后, intent_data['intent_type']的类型={type(intent_data.get('intent_type'))}")
                print(f"[调试] JSON解析后, intent_data['intent_type']是否为None={intent_data.get('intent_type') is None}")
                print(f"[调试] JSON解析后, intent_data['intent_type']的值={repr(intent_data.get('intent_type'))}")
                print(f"[调试] JSON解析后, 'intent_type' in intent_data={'intent_type' in intent_data}")
                print("="*80)
                
                # 关键调试：立即检查intent_type是否存在
                if "intent_type" not in intent_data:
                    print("[调试] ⚠️ 警告：JSON解析后，intent_data中没有'intent_type'字段！")
                elif intent_data.get("intent_type") is None:
                    print("[调试] ⚠️ 警告：JSON解析后，intent_data['intent_type']为None！")
                else:
                    print(f"[调试] ✅ JSON解析后，intent_data['intent_type']存在且不为None: {intent_data.get('intent_type')}")
                
                print()  # 空行
                
                # 关键调试：立即打印，确保日志不被截断
                import sys
                print("="*80, flush=True)
                print("[关键调试] JSON解析完成，准备调用_normalize_intent_data", flush=True)
                print(f"[关键调试] intent_data类型: {type(intent_data)}", flush=True)
                print(f"[关键调试] intent_data内容: {intent_data}", flush=True)
                print(f"[关键调试] intent_data['intent_type']: {intent_data.get('intent_type')}", flush=True)
                print("="*80, flush=True)
                sys.stdout.flush()
                
                # 关键修复：确保代码继续执行，不要在这里return
                # 继续执行到下面的_normalize_intent_data调用
                print("[关键调试] ⭐⭐⭐ JSON解析成功，代码应该继续执行到_normalize_intent_data ⭐⭐⭐", flush=True)
                sys.stdout.flush()
                
            except json.JSONDecodeError as e:
                # 如果第一次解析失败，尝试修复常见的JSON格式问题
                print("[调试] 第一次JSON解析失败:")
                print(f"  错误: {e}")
                print(f"[调试] 修复前的JSON文本（前100字符）: {json_text[:100]}")
                print(f"[调试] 修复前是否以{{{{开头: {json_text.startswith('{{')}")
                print(f"[调试] 修复前是否以}}结尾: {json_text.endswith('}}')}")
                print()
                fixed_json = self._fix_json_format(json_text)
                print("[调试] 修复后的JSON:")
                print("-"*60)
                print(fixed_json[:500] + ("..." if len(fixed_json) > 500 else ""))
                print("-"*60)
                print(f"[调试] 修复后是否以{{开头: {fixed_json.startswith('{')}")
                print(f"[调试] 修复后是否以}}结尾: {fixed_json.endswith('}')}")
                print()
                try:
                    intent_data = json.loads(fixed_json)
                    print("[调试] 修复后JSON解析成功:")
                    print("-"*60)
                    import json as json_module
                    print(json_module.dumps(intent_data, ensure_ascii=False, indent=2))
                    print("-"*60)
                    print(f"[调试] 修复后JSON解析, intent_data.get('intent_type')={intent_data.get('intent_type')}")
                    print(f"[调试] 修复后JSON解析, intent_data.get('intent')={intent_data.get('intent')}")
                    print(f"[调试] 修复后JSON解析, intent_data的所有keys={list(intent_data.keys())}")
                    print(f"[调试] 修复后JSON解析, intent_data['intent_type']的类型={type(intent_data.get('intent_type'))}")
                    print(f"[调试] 修复后JSON解析, intent_data['intent_type']是否为None={intent_data.get('intent_type') is None}")
                    print(f"[调试] 修复后JSON解析, intent_data['intent_type']的值={repr(intent_data.get('intent_type'))}")
                    
                    # 关键调试：立即检查intent_type是否存在
                    if "intent_type" not in intent_data:
                        print("[调试] ⚠️ 警告：修复后JSON解析，intent_data中没有'intent_type'字段！")
                    elif intent_data.get("intent_type") is None:
                        print("[调试] ⚠️ 警告：修复后JSON解析，intent_data['intent_type']为None！")
                    else:
                        print(f"[调试] ✅ 修复后JSON解析，intent_data['intent_type']存在且不为None: {intent_data.get('intent_type')}")
                    
                    print()  # 空行
                    
                    # 关键调试：立即打印，确保日志不被截断
                    print("="*80)
                    print("[关键调试] 修复后JSON解析完成，准备调用_normalize_intent_data")
                    print(f"[关键调试] intent_data类型: {type(intent_data)}")
                    print(f"[关键调试] intent_data内容: {intent_data}")
                    print(f"[关键调试] intent_data['intent_type']: {intent_data.get('intent_type')}")
                    print("="*80)
                    
                except json.JSONDecodeError as e2:
                    # 如果还是失败，显示详细错误信息
                    print(f"\n[LLM错误] JSON解析失败: {e2}")
                    print(f"[LLM错误] 错误位置: line {e2.lineno}, column {e2.colno}")
                    print(f"[LLM错误] 原始输出完整内容:")
                    print(output_text)
                    print(f"[LLM错误] 提取的JSON文本:")
                    print(json_text)
                    print(f"[LLM错误] 修复后的JSON文本:")
                    print(fixed_json)
                    # 抛出异常让外层处理
                    raise
            
            # 转换为兼容格式（支持新旧两种格式）
            import sys
            print("="*80, flush=True)
            print("[关键调试] ⭐⭐⭐ 代码执行到这里了！准备调用_normalize_intent_data ⭐⭐⭐", flush=True)
            print(f"[意图识别] recognize函数: 调用_normalize_intent_data前, intent_data={intent_data}", flush=True)
            print(f"[意图识别] recognize函数: 调用_normalize_intent_data前, intent_data.keys()={list(intent_data.keys())}", flush=True)
            print(f"[意图识别] recognize函数: 调用_normalize_intent_data前, intent_data.get('intent_type')={intent_data.get('intent_type')}", flush=True)
            print(f"[意图识别] recognize函数: 调用_normalize_intent_data前, intent_data.get('intent')={intent_data.get('intent')}", flush=True)
            print(f"[意图识别] recognize函数: 调用_normalize_intent_data前, 'intent_type' in intent_data={'intent_type' in intent_data}", flush=True)
            print(f"[意图识别] recognize函数: 调用_normalize_intent_data前, intent_data['intent_type']={intent_data.get('intent_type', 'KEY_NOT_EXISTS')}", flush=True)
            print("[关键调试] ⭐⭐⭐ 准备调用_normalize_intent_data函数 ⭐⭐⭐", flush=True)
            sys.stdout.flush()
            
            # 关键修复：在处理前保存原始的intent_type，防止丢失
            original_intent_type_before_normalize = intent_data.get("intent_type")
            print(f"[意图识别] recognize函数: 保存原始intent_type={original_intent_type_before_normalize}, 类型={type(original_intent_type_before_normalize)}", flush=True)
            sys.stdout.flush()
            
            # 关键修复：如果intent_data中没有intent_type字段，立即报错
            if "intent_type" not in intent_data:
                print(f"[意图识别] ⚠️ 严重错误：intent_data中没有'intent_type'字段！", flush=True)
                print(f"[意图识别] intent_data的所有keys: {list(intent_data.keys())}", flush=True)
                sys.stdout.flush()
            elif intent_data.get("intent_type") is None:
                print(f"[意图识别] ⚠️ 严重错误：intent_data['intent_type']为None！", flush=True)
                sys.stdout.flush()
            
            try:
                print(f"[意图识别] ⭐⭐⭐ 准备调用_normalize_intent_data ⭐⭐⭐", flush=True)
                print(f"[意图识别] 调用前 intent_data.get('intent_type')={intent_data.get('intent_type')}", flush=True)
                print(f"[意图识别] 调用前 intent_data的所有keys={list(intent_data.keys())}", flush=True)
                print(f"[意图识别] 调用前 intent_data完整内容={intent_data}", flush=True)
                sys.stdout.flush()
                
                normalized_result = self._normalize_intent_data(intent_data)
                
                print(f"[意图识别] recognize函数: _normalize_intent_data调用成功", flush=True)
                print(f"[意图识别] 调用后 normalized_result.get('intent_type')={normalized_result.get('intent_type')}", flush=True)
                print(f"[意图识别] 调用后 normalized_result的所有keys={list(normalized_result.keys())}", flush=True)
                print(f"[意图识别] 调用后 normalized_result完整内容={normalized_result}", flush=True)
                print(f"[意图识别] 调用后 'intent_type' in normalized_result={'intent_type' in normalized_result}", flush=True)
                sys.stdout.flush()
            except Exception as normalize_error:
                print(f"[意图识别] ⚠️ 警告：_normalize_intent_data调用失败: {normalize_error}", flush=True)
                import traceback
                print(traceback.format_exc(), flush=True)
                sys.stdout.flush()
                # 如果normalize失败，直接使用原始数据，但确保intent_type被正确设置
                normalized_result = {
                    "intent": original_intent_type_before_normalize or "UNKNOWN",
                    "intent_type": original_intent_type_before_normalize or "UNKNOWN",
                    "content": intent_data.get("content_to_process") or intent_data.get("content", ""),
                    "doc_title": intent_data.get("target_document"),
                    "position": intent_data.get("target_location_raw", "end"),
                    "message_style": intent_data.get("message_style", "error")
                }
                print(f"[意图识别] 使用fallback结果: {normalized_result}", flush=True)
                sys.stdout.flush()
            
            print(f"[意图识别] recognize函数: 调用_normalize_intent_data后, normalized_result={normalized_result}")
            print(f"[意图识别] recognize函数: 调用_normalize_intent_data后, normalized_result.keys()={list(normalized_result.keys())}")
            print(f"[意图识别] recognize函数: 调用_normalize_intent_data后, normalized_result.get('intent_type')={normalized_result.get('intent_type')}")
            print(f"[意图识别] recognize函数: 调用_normalize_intent_data后, normalized_result.get('intent')={normalized_result.get('intent')}")
            
            # 关键修复：最终检查，确保intent_type字段存在且正确
            if "intent_type" not in normalized_result or normalized_result.get("intent_type") is None:
                print(f"[意图识别] ⚠️ 警告：normalized_result中缺少intent_type字段或为None！")
                print(f"[意图识别] normalized_result的所有keys: {list(normalized_result.keys())}")
                if original_intent_type_before_normalize:
                    normalized_result["intent_type"] = str(original_intent_type_before_normalize).strip().upper()
                    print(f"[意图识别] ✅ 已从原始数据中恢复intent_type: {normalized_result['intent_type']}")
                else:
                    normalized_result["intent_type"] = "UNKNOWN"
                    print(f"[意图识别] ⚠️ 无法恢复intent_type，使用默认值UNKNOWN")
            
            # 关键修复：如果intent是UNKNOWN但intent_type不是UNKNOWN，使用intent_type作为intent
            if normalized_result.get("intent") == "UNKNOWN" and normalized_result.get("intent_type") and normalized_result.get("intent_type") != "UNKNOWN":
                # 根据intent_type设置正确的intent
                intent_type_value = normalized_result.get("intent_type")
                intent_mapping = {
                    "GREETING": "GREETING",
                    "ADD": "ADD_CONTENT",
                    "EDIT": "EDIT_CONTENT",
                    "MOVE": "MOVE_CONTENT",
                    "DELETE": "DELETE_CONTENT",
                    "QUERY": "DISPLAY_DOC",
                    "SUMMARY": "SUMMARY",
                    "SET_ACTIVE": "SET_ACTIVE",
                    "HELP": "HELP",
                    "EXIT": "EXIT",
                    "CONFIRM": "CONFIRM",
                    "CANCEL": "CANCEL",
                    "RESET_CONVERSATION": "RESET_CONVERSATION",
                    "CREATE_DOCUMENT": "CREATE_DOCUMENT"
                }
                mapped_intent = intent_mapping.get(intent_type_value, intent_type_value)
                normalized_result["intent"] = mapped_intent
                print(f"[意图识别] ✅ 修复intent: 从UNKNOWN改为{normalized_result['intent']} (基于intent_type={intent_type_value})")
            
            print(f"[意图识别] recognize函数: 最终返回normalized_result的所有keys: {list(normalized_result.keys())}")
            print(f"[意图识别] recognize函数: 最终返回normalized_result['intent']={normalized_result.get('intent')}, normalized_result['intent_type']={normalized_result.get('intent_type')}")
            
            # 关键修复：最终检查，确保 intent_type 字段存在
            if "intent_type" not in normalized_result or normalized_result.get("intent_type") is None:
                print(f"[意图识别] ⚠️ 严重警告：recognize函数返回前，normalized_result中缺少intent_type字段或为None！")
                print(f"[意图识别] normalized_result的所有keys: {list(normalized_result.keys())}")
                if original_intent_type_before_normalize:
                    normalized_result["intent_type"] = str(original_intent_type_before_normalize).strip().upper()
                    print(f"[意图识别] ✅ 已从原始数据中恢复intent_type: {normalized_result['intent_type']}")
                else:
                    normalized_result["intent_type"] = "UNKNOWN"
                    print(f"[意图识别] ⚠️ 无法恢复intent_type，使用默认值UNKNOWN")
            
            print("="*80)
            print("[调试] ⭐⭐⭐ recognize函数准备返回结果 ⭐⭐⭐")
            print(f"[调试] recognize函数返回的normalized_result: {normalized_result}")
            print(f"[调试] normalized_result类型: {type(normalized_result)}")
            print(f"[调试] normalized_result的所有keys: {list(normalized_result.keys())}")
            print(f"[调试] normalized_result.get('intent_type'): {normalized_result.get('intent_type')}")
            print(f"[调试] normalized_result.get('intent'): {normalized_result.get('intent')}")
            print(f"[调试] normalized_result.get('intent_type')类型: {type(normalized_result.get('intent_type'))}")
            print(f"[调试] normalized_result.get('intent_type')是否为None: {normalized_result.get('intent_type') is None}")
            print(f"[调试] 'intent_type' in normalized_result: {'intent_type' in normalized_result}")
            print("="*80)
            
            # 关键修复：最终验证，确保返回的字典包含 intent_type
            if "intent_type" not in normalized_result:
                print(f"[意图识别] ⚠️ 严重错误：返回前检查，normalized_result中仍然缺少intent_type字段！")
                normalized_result["intent_type"] = str(original_intent_type_before_normalize).strip().upper() if original_intent_type_before_normalize else "UNKNOWN"
                print(f"[意图识别] ✅ 已强制添加intent_type: {normalized_result['intent_type']}")
            
            # 将 rag_info 附加到返回结果中
            normalized_result["rag_info"] = rag_info
            return normalized_result

        except json.JSONDecodeError as e:
            print(f"[LLM错误] JSON解析失败: {e}")
            if 'response' in locals() and response.status_code == HTTPStatus.OK:
                output_text = response.output.text.strip()
                print(f"[LLM错误] 原始输出: {output_text}")
                print(f"[LLM错误] 提取的JSON文本: {self._extract_json(output_text) if hasattr(self, '_extract_json') else 'N/A'}")
            else:
                print(f"[LLM错误] 原始输出: N/A")
            # JSON 解析失败，但 API 调用成功，仍然将 assistant 回复添加到 messages
            if 'response' in locals() and response.status_code == HTTPStatus.OK:
                output_text = response.output.text.strip()
                self.messages.append({
                    "role": "assistant",
                    "content": output_text
                })
            else:
                # API 调用失败，移除刚才添加的用户消息
                if self.messages and self.messages[-1].get("role") == "user":
                    self.messages.pop()
            # 降级处理
            if re.search(r"(退出|再见|结束)", user_input):
                return {"intent": "EXIT", "intent_type": "EXIT"}
            if re.search(r"(帮助|能做什么|怎么用)", user_input):
                return {"intent": "HELP", "intent_type": "HELP"}
            return {"intent": "UNKNOWN", "intent_type": "UNKNOWN"}
        except Exception as e:
            print(f"[LLM错误] 调用智能体应用失败: {e}")
            import traceback
            print(traceback.format_exc())
            # 异常情况，移除刚才添加的用户消息，避免对话历史不完整
            if self.messages and self.messages[-1].get("role") == "user":
                self.messages.pop()
            # 降级处理：尝试使用简单的正则匹配（作为LLM失败的备用方案）
            if re.search(r"(退出|再见|结束)", user_input):
                return {"intent": "EXIT", "intent_type": "EXIT"}
            if re.search(r"(帮助|能做什么|怎么用)", user_input):
                return {"intent": "HELP", "intent_type": "HELP"}
            return {"intent": "UNKNOWN", "intent_type": "UNKNOWN"}


