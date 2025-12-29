#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试 _normalize_intent_data 函数
"""

import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 模拟必要的依赖
class MockDocManager:
    pass

class MockClientConfig:
    def __init__(self):
        self.config = {
            'api_key': 'test_key',
            'app_id': 'test_app_id'
        }
    
    def get(self, key, default=None):
        return self.config.get(key, default)

# 导入 intent_recognizer
from intent_recognizer import LLMIntentRecognizer

def test_normalize_intent_data():
    """测试 _normalize_intent_data 函数"""
    print("="*80)
    print("开始测试 _normalize_intent_data 函数")
    print("="*80)
    
    # 创建 LLMIntentRecognizer 实例
    doc_manager = MockDocManager()
    client_config = MockClientConfig()
    recognizer = LLMIntentRecognizer(doc_manager, client_config)
    
    # 测试用例1：正常的 GREETING 意图（只有 intent_type，没有 intent）
    print("\n" + "="*80)
    print("测试用例1：正常的 GREETING 意图（只有 intent_type，没有 intent）")
    print("="*80)
    intent_data_1 = {
        "intent_type": "GREETING",
        "target_document": None,
        "target_location_raw": None,
        "content_to_process": "你好！我是灵辑，你的智能笔记助手。有什么可以帮你的吗？",
        "context_dependency": False,
        "confirmation_needed": False,
        "system_action_required": "DISPLAY_MESSAGE",
        "dev_mode_required": False,
        "message_style": "normal"
    }
    
    print(f"\n输入 intent_data:")
    print(f"  keys: {list(intent_data_1.keys())}")
    print(f"  intent_type: {intent_data_1.get('intent_type')}")
    print(f"  intent: {intent_data_1.get('intent')}")
    
    try:
        result_1 = recognizer._normalize_intent_data(intent_data_1)
        print(f"\n✅ 函数调用成功")
        print(f"\n返回结果:")
        print(f"  keys: {list(result_1.keys())}")
        print(f"  intent_type: {result_1.get('intent_type')}")
        print(f"  intent: {result_1.get('intent')}")
        print(f"  'intent_type' in result: {'intent_type' in result_1}")
        print(f"  result['intent_type'] is None: {result_1.get('intent_type') is None}")
        
        if "intent_type" not in result_1:
            print("\n❌ 错误：返回结果中缺少 'intent_type' 字段！")
        elif result_1.get("intent_type") is None:
            print("\n❌ 错误：返回结果中 'intent_type' 字段为 None！")
        elif result_1.get("intent_type") != "GREETING":
            print(f"\n❌ 错误：返回结果中 'intent_type' 字段值不正确！期望 'GREETING'，实际 '{result_1.get('intent_type')}'")
        else:
            print("\n✅ 测试通过：返回结果中包含正确的 'intent_type' 字段")
            
    except Exception as e:
        print(f"\n❌ 函数调用失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 测试用例2：同时有 intent_type 和 intent 的情况
    print("\n" + "="*80)
    print("测试用例2：同时有 intent_type 和 intent 的情况")
    print("="*80)
    intent_data_2 = {
        "intent_type": "GREETING",
        "intent": "GREETING",
        "target_document": None,
        "target_location_raw": None,
        "content_to_process": "你好！",
        "context_dependency": False,
        "confirmation_needed": False,
        "system_action_required": "DISPLAY_MESSAGE",
        "dev_mode_required": False,
        "message_style": "normal"
    }
    
    print(f"\n输入 intent_data:")
    print(f"  keys: {list(intent_data_2.keys())}")
    print(f"  intent_type: {intent_data_2.get('intent_type')}")
    print(f"  intent: {intent_data_2.get('intent')}")
    
    try:
        result_2 = recognizer._normalize_intent_data(intent_data_2)
        print(f"\n✅ 函数调用成功")
        print(f"\n返回结果:")
        print(f"  keys: {list(result_2.keys())}")
        print(f"  intent_type: {result_2.get('intent_type')}")
        print(f"  intent: {result_2.get('intent')}")
        print(f"  'intent_type' in result: {'intent_type' in result_2}")
        print(f"  result['intent_type'] is None: {result_2.get('intent_type') is None}")
        
        if "intent_type" not in result_2:
            print("\n❌ 错误：返回结果中缺少 'intent_type' 字段！")
        elif result_2.get("intent_type") is None:
            print("\n❌ 错误：返回结果中 'intent_type' 字段为 None！")
        elif result_2.get("intent_type") != "GREETING":
            print(f"\n❌ 错误：返回结果中 'intent_type' 字段值不正确！期望 'GREETING'，实际 '{result_2.get('intent_type')}'")
        else:
            print("\n✅ 测试通过：返回结果中包含正确的 'intent_type' 字段")
            
    except Exception as e:
        print(f"\n❌ 函数调用失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 测试用例3：intent_type 是 GREETING，但 intent 是 UNKNOWN
    print("\n" + "="*80)
    print("测试用例3：intent_type 是 GREETING，但 intent 是 UNKNOWN")
    print("="*80)
    intent_data_3 = {
        "intent_type": "GREETING",
        "intent": "UNKNOWN",
        "target_document": None,
        "target_location_raw": None,
        "content_to_process": "你好！",
        "context_dependency": False,
        "confirmation_needed": False,
        "system_action_required": "DISPLAY_MESSAGE",
        "dev_mode_required": False,
        "message_style": "normal"
    }
    
    print(f"\n输入 intent_data:")
    print(f"  keys: {list(intent_data_3.keys())}")
    print(f"  intent_type: {intent_data_3.get('intent_type')}")
    print(f"  intent: {intent_data_3.get('intent')}")
    
    try:
        result_3 = recognizer._normalize_intent_data(intent_data_3)
        print(f"\n✅ 函数调用成功")
        print(f"\n返回结果:")
        print(f"  keys: {list(result_3.keys())}")
        print(f"  intent_type: {result_3.get('intent_type')}")
        print(f"  intent: {result_3.get('intent')}")
        print(f"  'intent_type' in result: {'intent_type' in result_3}")
        print(f"  result['intent_type'] is None: {result_3.get('intent_type') is None}")
        
        if "intent_type" not in result_3:
            print("\n❌ 错误：返回结果中缺少 'intent_type' 字段！")
        elif result_3.get("intent_type") is None:
            print("\n❌ 错误：返回结果中 'intent_type' 字段为 None！")
        elif result_3.get("intent_type") != "GREETING":
            print(f"\n❌ 错误：返回结果中 'intent_type' 字段值不正确！期望 'GREETING'，实际 '{result_3.get('intent_type')}'")
        else:
            print("\n✅ 测试通过：返回结果中包含正确的 'intent_type' 字段")
            
    except Exception as e:
        print(f"\n❌ 函数调用失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*80)
    print("测试完成")
    print("="*80)

if __name__ == "__main__":
    test_normalize_intent_data()

