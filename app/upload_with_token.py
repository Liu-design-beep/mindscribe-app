#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用提供的 API Token 上传所有文档到 D1 数据库
"""

import json
import requests
import sys
from pathlib import Path

# API Token
API_TOKEN = "Wu98Hm6f8AeEhc_gEobnTaq2fHot3Ntanj8lw-S4"
ACCOUNT_ID = "653abf52ef7aec16367bf7967a263ec0"
D1_DATABASE_ID = "8fb7b530-17e4-44f1-819f-ee585effdbf2"

# 介绍文档内容（简化版，完整内容在 upload_all_documents_to_d1_api.py 中）
INTRO_CONTENT = [
    "欢迎使用灵辑 (Mindscribe) - AI 智能笔记助手",
    "",
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
    "",
    "## 📖 产品概述",
    "",
    "灵辑 (Mindscribe) 是一款基于大语言模型 (LLM) 的智能笔记管理助手，致力于帮助用户高效整理和管理碎片化笔记内容。通过自然语言对话交互，智能理解用户意图，自动将笔记内容分类、整理并永久存储在云端。",
    "",
    "## ✨ 核心功能",
    "",
    "1) 🤖 智能对话交互：自然语言添加/查看/切换/创建文档，意图识别与结构化整理",
    "2) 📝 多文档管理：支持多文档并行，快速切换；试用/开发模式文档完全隔离",
    "3) ☁️ 云端永久存储：Cloudflare D1 持久化，跨设备访问",
    "4) 🔐 权限与只读保护：开发者模式、修改模式(set000)，只读文档防误改",
    "5) 👁️ 完整查看：弹窗滚动查看当前文档全部内容",
    "",
    "## 🧠 模型与选择",
    "",
    "• 主模型：通义千问 3 - coder - plus（针对代码与长文本处理优化）",
    "• 选型理由：代码理解与生成能力强，长文本上下文处理稳健，适合笔记/文档场景",
    "• 托管策略：前端调用后端统一网关，支持按需切换/灰度替换",
    "",
    "## 🧪 A/B 测试与训练",
    "",
    "• A/B 范围：回复准确性、段落分段质量、长文截断与拼接、指令跟随度",
    "• 指标示例：回答一致性、命中率、格式合规率、用户二次编辑率",
    "• 数据：仅使用脱敏/合规数据；不存储用户隐私输入；日志最小化",
    "• 回滚策略：任一实验指标低于基线自动回退；支持分文档、分会话灰度",
    "",
    "## 🏗️ 技术架构（概览）",
    "",
    "• 前端：原生 JS + CSS，双模式（试用/开发），弹窗查看全文",
    "• 后端：Python FastAPI；会话管理 + 文档管理",
    "• 存储：Cloudflare D1（dev 文档/试用文档分表；session_id 作用于试用表）",
    "• 边缘：Cloudflare Workers（静态与接口代理）；KV 作为回退/缓存",
    "",
    "## 📋 模式说明",
    "",
    "• 试用模式：文档 = 试用文档（空白）、PM问答笔记；数据隔离，可能被清理",
    "• 开发者模式：文档 = 介绍文档（本页）、更新记录日志；云端长期保存",
    "",
    "## 🚀 快速开始",
    "",
    "1. 查看文档：点击「查看文档」按钮，弹窗展示全文，可滚动查看",
    "2. 切换文档：点击切换按钮，在列表中选择目标文档",
    "3. 创建文档：在文档列表底部点击「新建文档」",
    "4. 修改权限：输入 set000 开启修改；未开启时只读",
    "5. 开发者模式：输入 开发者模式#000 启用",
    "",
    "## 📌 注意事项",
    "",
    "• 介绍文档为只读；试用/开发模式文档完全隔离",
    "• D1 持久化；本地调试若无 D1 会回退内存，刷新即失",
    "• 建议重要内容定期备份",
    "",
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
    "版本：Beta | 更新：2025-12-23 | 模型：通义千问3-coder-plus",
    ""
]

# PM问答笔记内容（简化版）
PM_CONTENT = [
    "欢迎使用灵辑 (Mindscribe) - AI 内容收藏助手",
    "",
    "## PM问答笔记",
    "",
    "场景：你正在参加腾讯 AI 产品经理的职位面试。面试官是一位经验丰富的产品总监。",
    "",
    "问题：",
    "",
    "1、您如何理解 AI 产品经理的角色，以及您认为这个角色在腾讯 AI 战略中扮演着怎样的作用？",
    "",
    "回答思路：",
    "",
    "展示你对 AI 产品经理职责的理解，包括市场调研、用户需求分析、产品设计、开发管理、数据分析等。",
    "",
    "结合腾讯的 AI 战略，例如腾讯云 AI、腾讯 AI Lab 等，阐述你认为 AI 产品经理在推动腾讯 AI 战略落地、打造 AI 产品生态中的重要作用。",
    "",
    "可以结合你对腾讯 AI 产品的了解，例如微信小程序、腾讯翻译君等，谈谈你对腾讯 AI 产品发展方向的看法。",
    "",
    "2、请您谈谈您对当前 AI 技术发展趋势的理解，以及您认为哪些 AI 技术将会在未来几年对腾讯产品产生重大影响？",
    "",
    "回答思路：",
    "",
    "展示你对 AI 技术发展趋势的了解，例如深度学习、自然语言处理、计算机视觉等。",
    "",
    "选择几个你认为对腾讯产品具有重大影响的 AI 技术，并结合具体案例进行阐述。例如，你认为自然语言处理技术可以应用于微信聊天机器人，提升用户体验；计算机视觉技术可以应用于腾讯视频，实现更精准的视频内容推荐。",
    "",
    "可以结合你对腾讯产品线的了解，谈谈你对 AI 技术在腾讯产品中的应用前景。",
    "",
    "3、请您描述一个您曾经参与过的 AI 产品项目，并详细介绍您在项目中的角色、遇到的挑战以及最终的成果。",
    "",
    "回答思路：",
    "",
    "选择一个你参与过的 AI 产品项目，并详细介绍项目的背景、目标、以及你的角色和职责。",
    "",
    "突出你在项目中遇到的挑战，例如技术难题、用户需求变化等，并描述你如何克服这些挑战。",
    "",
    "最后，阐述项目的最终成果，例如产品上线、用户增长、商业价值等。",
    "",
    "4、您如何看待 AI 产品的伦理问题，以及您认为腾讯在 AI 产品研发中应该如何处理这些问题？",
    "",
    "回答思路：",
    "",
    "展示你对 AI 伦理问题的理解，例如数据隐私、算法歧视、人工智能安全等。",
    "",
    "结合腾讯的企业文化和社会责任，阐述你认为腾讯应该如何处理这些问题，例如建立完善的 AI 伦理规范、加强数据安全管理、提升算法透明度等。",
    "",
    "可以结合一些具体的案例，例如腾讯 AI 翻译的语言歧视问题，谈谈你对腾讯在 AI 伦理方面的思考。",
    "",
    "5、您对未来 AI 产品的发展趋势有什么看法？您认为腾讯应该如何抓住机遇，引领 AI 产品的未来？",
    "",
    "回答思路：",
    "",
    "展示你对未来 AI 产品发展趋势的了解，例如 AI 与物联网、AI 与云计算、AI 与边缘计算的融合等。",
    "",
    "结合腾讯的优势和资源，阐述你认为腾讯应该如何抓住机遇，引领 AI 产品的未来，例如加大 AI 技术研发投入、布局 AI 生态、打造 AI 产品矩阵等。",
    "",
    "可以结合你对腾讯的战略布局，谈谈你对腾讯未来 AI 产品发展方向的看法。",
    "",
    "准备建议：",
    "",
    "提前了解腾讯的 AI 战略、产品线、以及相关新闻报道。",
    "",
    "准备几个你参与过的 AI 产品项目案例，并思考项目中的挑战和成果。",
    "",
    "思考 AI 伦理问题，并结合腾讯的企业文化和社会责任，提出你的观点。",
    "",
    "关注未来 AI 产品发展趋势，并思考腾讯如何抓住机遇。",
    "",
    "祝你面试顺利！"
]

def load_update_log_content():
    """加载更新记录日志内容"""
    try:
        import sys
        web_path = Path(__file__).parent / "web"
        if str(web_path) not in sys.path:
            sys.path.insert(0, str(web_path))
        
        from update_log_content import UPDATE_LOG_CONTENT
        return UPDATE_LOG_CONTENT
    except ImportError:
        print("[警告] 无法导入更新记录日志内容")
        return ["更新记录日志内容"]

def get_account_id(api_token):
    """尝试获取 Account ID"""
    url = "https://api.cloudflare.com/client/v4/accounts"
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and data.get("result"):
                accounts = data["result"]
                if accounts:
                    return accounts[0]["id"]
        print(f"[获取Account ID失败] 状态码: {response.status_code}")
        print(f"[获取Account ID失败] 响应: {response.text[:300]}")
    except Exception as e:
        print(f"[获取Account ID失败] 错误: {e}")
    
    return None

def execute_d1_sql(sql_command, account_id, api_token):
    """执行 D1 SQL 命令"""
    url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/d1/database/{D1_DATABASE_ID}/query"
    
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    
    data = {"sql": sql_command}
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"[API错误] 请求失败: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"[API错误] 响应: {e.response.text[:500]}")
        return None

def upload_document(title, content, doc_type, session_id=None, account_id=None, api_token=None):
    """上传单个文档"""
    content_json = json.dumps(content, ensure_ascii=False)
    content_json_escaped = content_json.replace("'", "''")
    
    if doc_type == "dev":
        sql = f"INSERT OR REPLACE INTO dev_documents (title, content, updated_at) VALUES ('{title}', '{content_json_escaped}', CURRENT_TIMESTAMP);"
    else:
        if not session_id:
            print(f"[错误] 试用模式文档需要session_id")
            return False
        sql = f"INSERT OR REPLACE INTO trial_documents (session_id, title, content, updated_at) VALUES ('{session_id}', '{title}', '{content_json_escaped}', CURRENT_TIMESTAMP);"
    
    print(f"[上传] {title} ({doc_type})")
    
    result = execute_d1_sql(sql, account_id, api_token)
    
    if result and result.get("success"):
        print(f"[成功] {title}")
        return True
    else:
        print(f"[失败] {title}")
        if result:
            print(f"错误: {result}")
        return False

def create_tables(account_id, api_token):
    """创建数据库表"""
    print("\n[步骤1] 创建数据库表...")
    
    tables_sql = [
        # dev_documents 表
        """CREATE TABLE IF NOT EXISTS dev_documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL UNIQUE,
            content TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );""",
        
        # trial_documents 表
        """CREATE TABLE IF NOT EXISTS trial_documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(session_id, title)
        );""",
        
        # metadata 表
        """CREATE TABLE IF NOT EXISTS metadata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doc_type TEXT NOT NULL,
            session_id TEXT,
            key TEXT NOT NULL,
            value TEXT NOT NULL,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(doc_type, session_id, key)
        );""",
        
        # dev_mode_status 表
        """CREATE TABLE IF NOT EXISTS dev_mode_status (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL UNIQUE,
            enabled INTEGER DEFAULT 0,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );"""
    ]
    
    for i, sql in enumerate(tables_sql, 1):
        table_name = ["dev_documents", "trial_documents", "metadata", "dev_mode_status"][i-1]
        print(f"  [{i}/4] 创建表: {table_name}...")
        result = execute_d1_sql(sql, account_id, api_token)
        if result and result.get("success"):
            print(f"  [成功] {table_name}")
        else:
            print(f"  [失败] {table_name}")
            if result:
                print(f"  错误: {result}")

def main():
    print("=" * 60)
    print("上传所有文档到 D1 数据库")
    print("=" * 60)
    
    # 使用配置的 Account ID
    account_id = ACCOUNT_ID
    if len(sys.argv) > 1:
        account_id = sys.argv[1]  # 允许命令行覆盖
    
    print(f"\n[配置] Account ID: {account_id}")
    print(f"[配置] Database ID: {D1_DATABASE_ID}")
    
    # 创建表
    create_tables(account_id, API_TOKEN)
    
    # 上传文档
    print("\n[步骤2] 开始上传文档...")
    
    results = {}
    
    # 1. 介绍文档
    print("\n[1/3] 上传介绍文档...")
    results["介绍文档"] = upload_document("介绍文档", INTRO_CONTENT, "dev", None, account_id, API_TOKEN)
    
    # 2. 更新记录日志
    print("\n[2/3] 上传更新记录日志...")
    update_log = load_update_log_content()
    results["更新记录日志"] = upload_document("更新记录日志", update_log, "dev", None, account_id, API_TOKEN)
    
    # 3. PM问答笔记
    print("\n[3/3] 上传PM问答笔记...")
    results["PM问答笔记"] = upload_document("PM问答笔记", PM_CONTENT, "trial", "default_trial_session", account_id, API_TOKEN)
    
    # 总结
    print("\n" + "=" * 60)
    print("上传结果")
    print("=" * 60)
    success = sum(1 for v in results.values() if v)
    total = len(results)
    
    for title, ok in results.items():
        print(f"{title}: {'[成功]' if ok else '[失败]'}")
    
    print(f"\n总计: {success}/{total} 成功")
    
    if success == total:
        print("\n[完成] 所有文档已上传！")

if __name__ == "__main__":
    main()


"""
使用提供的 API Token 上传所有文档到 D1 数据库
"""

import json
import requests
import sys
from pathlib import Path

# API Token
API_TOKEN = "Wu98Hm6f8AeEhc_gEobnTaq2fHot3Ntanj8lw-S4"
ACCOUNT_ID = "653abf52ef7aec16367bf7967a263ec0"
D1_DATABASE_ID = "8fb7b530-17e4-44f1-819f-ee585effdbf2"

# 介绍文档内容（简化版，完整内容在 upload_all_documents_to_d1_api.py 中）
INTRO_CONTENT = [
    "欢迎使用灵辑 (Mindscribe) - AI 智能笔记助手",
    "",
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
    "",
    "## 📖 产品概述",
    "",
    "灵辑 (Mindscribe) 是一款基于大语言模型 (LLM) 的智能笔记管理助手，致力于帮助用户高效整理和管理碎片化笔记内容。通过自然语言对话交互，智能理解用户意图，自动将笔记内容分类、整理并永久存储在云端。",
    "",
    "## ✨ 核心功能",
    "",
    "1) 🤖 智能对话交互：自然语言添加/查看/切换/创建文档，意图识别与结构化整理",
    "2) 📝 多文档管理：支持多文档并行，快速切换；试用/开发模式文档完全隔离",
    "3) ☁️ 云端永久存储：Cloudflare D1 持久化，跨设备访问",
    "4) 🔐 权限与只读保护：开发者模式、修改模式(set000)，只读文档防误改",
    "5) 👁️ 完整查看：弹窗滚动查看当前文档全部内容",
    "",
    "## 🧠 模型与选择",
    "",
    "• 主模型：通义千问 3 - coder - plus（针对代码与长文本处理优化）",
    "• 选型理由：代码理解与生成能力强，长文本上下文处理稳健，适合笔记/文档场景",
    "• 托管策略：前端调用后端统一网关，支持按需切换/灰度替换",
    "",
    "## 🧪 A/B 测试与训练",
    "",
    "• A/B 范围：回复准确性、段落分段质量、长文截断与拼接、指令跟随度",
    "• 指标示例：回答一致性、命中率、格式合规率、用户二次编辑率",
    "• 数据：仅使用脱敏/合规数据；不存储用户隐私输入；日志最小化",
    "• 回滚策略：任一实验指标低于基线自动回退；支持分文档、分会话灰度",
    "",
    "## 🏗️ 技术架构（概览）",
    "",
    "• 前端：原生 JS + CSS，双模式（试用/开发），弹窗查看全文",
    "• 后端：Python FastAPI；会话管理 + 文档管理",
    "• 存储：Cloudflare D1（dev 文档/试用文档分表；session_id 作用于试用表）",
    "• 边缘：Cloudflare Workers（静态与接口代理）；KV 作为回退/缓存",
    "",
    "## 📋 模式说明",
    "",
    "• 试用模式：文档 = 试用文档（空白）、PM问答笔记；数据隔离，可能被清理",
    "• 开发者模式：文档 = 介绍文档（本页）、更新记录日志；云端长期保存",
    "",
    "## 🚀 快速开始",
    "",
    "1. 查看文档：点击「查看文档」按钮，弹窗展示全文，可滚动查看",
    "2. 切换文档：点击切换按钮，在列表中选择目标文档",
    "3. 创建文档：在文档列表底部点击「新建文档」",
    "4. 修改权限：输入 set000 开启修改；未开启时只读",
    "5. 开发者模式：输入 开发者模式#000 启用",
    "",
    "## 📌 注意事项",
    "",
    "• 介绍文档为只读；试用/开发模式文档完全隔离",
    "• D1 持久化；本地调试若无 D1 会回退内存，刷新即失",
    "• 建议重要内容定期备份",
    "",
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
    "版本：Beta | 更新：2025-12-23 | 模型：通义千问3-coder-plus",
    ""
]

# PM问答笔记内容（简化版）
PM_CONTENT = [
    "欢迎使用灵辑 (Mindscribe) - AI 内容收藏助手",
    "",
    "## PM问答笔记",
    "",
    "场景：你正在参加腾讯 AI 产品经理的职位面试。面试官是一位经验丰富的产品总监。",
    "",
    "问题：",
    "",
    "1、您如何理解 AI 产品经理的角色，以及您认为这个角色在腾讯 AI 战略中扮演着怎样的作用？",
    "",
    "回答思路：",
    "",
    "展示你对 AI 产品经理职责的理解，包括市场调研、用户需求分析、产品设计、开发管理、数据分析等。",
    "",
    "结合腾讯的 AI 战略，例如腾讯云 AI、腾讯 AI Lab 等，阐述你认为 AI 产品经理在推动腾讯 AI 战略落地、打造 AI 产品生态中的重要作用。",
    "",
    "可以结合你对腾讯 AI 产品的了解，例如微信小程序、腾讯翻译君等，谈谈你对腾讯 AI 产品发展方向的看法。",
    "",
    "2、请您谈谈您对当前 AI 技术发展趋势的理解，以及您认为哪些 AI 技术将会在未来几年对腾讯产品产生重大影响？",
    "",
    "回答思路：",
    "",
    "展示你对 AI 技术发展趋势的了解，例如深度学习、自然语言处理、计算机视觉等。",
    "",
    "选择几个你认为对腾讯产品具有重大影响的 AI 技术，并结合具体案例进行阐述。例如，你认为自然语言处理技术可以应用于微信聊天机器人，提升用户体验；计算机视觉技术可以应用于腾讯视频，实现更精准的视频内容推荐。",
    "",
    "可以结合你对腾讯产品线的了解，谈谈你对 AI 技术在腾讯产品中的应用前景。",
    "",
    "3、请您描述一个您曾经参与过的 AI 产品项目，并详细介绍您在项目中的角色、遇到的挑战以及最终的成果。",
    "",
    "回答思路：",
    "",
    "选择一个你参与过的 AI 产品项目，并详细介绍项目的背景、目标、以及你的角色和职责。",
    "",
    "突出你在项目中遇到的挑战，例如技术难题、用户需求变化等，并描述你如何克服这些挑战。",
    "",
    "最后，阐述项目的最终成果，例如产品上线、用户增长、商业价值等。",
    "",
    "4、您如何看待 AI 产品的伦理问题，以及您认为腾讯在 AI 产品研发中应该如何处理这些问题？",
    "",
    "回答思路：",
    "",
    "展示你对 AI 伦理问题的理解，例如数据隐私、算法歧视、人工智能安全等。",
    "",
    "结合腾讯的企业文化和社会责任，阐述你认为腾讯应该如何处理这些问题，例如建立完善的 AI 伦理规范、加强数据安全管理、提升算法透明度等。",
    "",
    "可以结合一些具体的案例，例如腾讯 AI 翻译的语言歧视问题，谈谈你对腾讯在 AI 伦理方面的思考。",
    "",
    "5、您对未来 AI 产品的发展趋势有什么看法？您认为腾讯应该如何抓住机遇，引领 AI 产品的未来？",
    "",
    "回答思路：",
    "",
    "展示你对未来 AI 产品发展趋势的了解，例如 AI 与物联网、AI 与云计算、AI 与边缘计算的融合等。",
    "",
    "结合腾讯的优势和资源，阐述你认为腾讯应该如何抓住机遇，引领 AI 产品的未来，例如加大 AI 技术研发投入、布局 AI 生态、打造 AI 产品矩阵等。",
    "",
    "可以结合你对腾讯的战略布局，谈谈你对腾讯未来 AI 产品发展方向的看法。",
    "",
    "准备建议：",
    "",
    "提前了解腾讯的 AI 战略、产品线、以及相关新闻报道。",
    "",
    "准备几个你参与过的 AI 产品项目案例，并思考项目中的挑战和成果。",
    "",
    "思考 AI 伦理问题，并结合腾讯的企业文化和社会责任，提出你的观点。",
    "",
    "关注未来 AI 产品发展趋势，并思考腾讯如何抓住机遇。",
    "",
    "祝你面试顺利！"
]

def load_update_log_content():
    """加载更新记录日志内容"""
    try:
        import sys
        web_path = Path(__file__).parent / "web"
        if str(web_path) not in sys.path:
            sys.path.insert(0, str(web_path))
        
        from update_log_content import UPDATE_LOG_CONTENT
        return UPDATE_LOG_CONTENT
    except ImportError:
        print("[警告] 无法导入更新记录日志内容")
        return ["更新记录日志内容"]

def get_account_id(api_token):
    """尝试获取 Account ID"""
    url = "https://api.cloudflare.com/client/v4/accounts"
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and data.get("result"):
                accounts = data["result"]
                if accounts:
                    return accounts[0]["id"]
        print(f"[获取Account ID失败] 状态码: {response.status_code}")
        print(f"[获取Account ID失败] 响应: {response.text[:300]}")
    except Exception as e:
        print(f"[获取Account ID失败] 错误: {e}")
    
    return None

def execute_d1_sql(sql_command, account_id, api_token):
    """执行 D1 SQL 命令"""
    url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/d1/database/{D1_DATABASE_ID}/query"
    
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    
    data = {"sql": sql_command}
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"[API错误] 请求失败: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"[API错误] 响应: {e.response.text[:500]}")
        return None

def upload_document(title, content, doc_type, session_id=None, account_id=None, api_token=None):
    """上传单个文档"""
    content_json = json.dumps(content, ensure_ascii=False)
    content_json_escaped = content_json.replace("'", "''")
    
    if doc_type == "dev":
        sql = f"INSERT OR REPLACE INTO dev_documents (title, content, updated_at) VALUES ('{title}', '{content_json_escaped}', CURRENT_TIMESTAMP);"
    else:
        if not session_id:
            print(f"[错误] 试用模式文档需要session_id")
            return False
        sql = f"INSERT OR REPLACE INTO trial_documents (session_id, title, content, updated_at) VALUES ('{session_id}', '{title}', '{content_json_escaped}', CURRENT_TIMESTAMP);"
    
    print(f"[上传] {title} ({doc_type})")
    
    result = execute_d1_sql(sql, account_id, api_token)
    
    if result and result.get("success"):
        print(f"[成功] {title}")
        return True
    else:
        print(f"[失败] {title}")
        if result:
            print(f"错误: {result}")
        return False

def create_tables(account_id, api_token):
    """创建数据库表"""
    print("\n[步骤1] 创建数据库表...")
    
    tables_sql = [
        # dev_documents 表
        """CREATE TABLE IF NOT EXISTS dev_documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL UNIQUE,
            content TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );""",
        
        # trial_documents 表
        """CREATE TABLE IF NOT EXISTS trial_documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(session_id, title)
        );""",
        
        # metadata 表
        """CREATE TABLE IF NOT EXISTS metadata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doc_type TEXT NOT NULL,
            session_id TEXT,
            key TEXT NOT NULL,
            value TEXT NOT NULL,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(doc_type, session_id, key)
        );""",
        
        # dev_mode_status 表
        """CREATE TABLE IF NOT EXISTS dev_mode_status (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL UNIQUE,
            enabled INTEGER DEFAULT 0,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );"""
    ]
    
    for i, sql in enumerate(tables_sql, 1):
        table_name = ["dev_documents", "trial_documents", "metadata", "dev_mode_status"][i-1]
        print(f"  [{i}/4] 创建表: {table_name}...")
        result = execute_d1_sql(sql, account_id, api_token)
        if result and result.get("success"):
            print(f"  [成功] {table_name}")
        else:
            print(f"  [失败] {table_name}")
            if result:
                print(f"  错误: {result}")

def main():
    print("=" * 60)
    print("上传所有文档到 D1 数据库")
    print("=" * 60)
    
    # 使用配置的 Account ID
    account_id = ACCOUNT_ID
    if len(sys.argv) > 1:
        account_id = sys.argv[1]  # 允许命令行覆盖
    
    print(f"\n[配置] Account ID: {account_id}")
    print(f"[配置] Database ID: {D1_DATABASE_ID}")
    
    # 创建表
    create_tables(account_id, API_TOKEN)
    
    # 上传文档
    print("\n[步骤2] 开始上传文档...")
    
    results = {}
    
    # 1. 介绍文档
    print("\n[1/3] 上传介绍文档...")
    results["介绍文档"] = upload_document("介绍文档", INTRO_CONTENT, "dev", None, account_id, API_TOKEN)
    
    # 2. 更新记录日志
    print("\n[2/3] 上传更新记录日志...")
    update_log = load_update_log_content()
    results["更新记录日志"] = upload_document("更新记录日志", update_log, "dev", None, account_id, API_TOKEN)
    
    # 3. PM问答笔记
    print("\n[3/3] 上传PM问答笔记...")
    results["PM问答笔记"] = upload_document("PM问答笔记", PM_CONTENT, "trial", "default_trial_session", account_id, API_TOKEN)
    
    # 总结
    print("\n" + "=" * 60)
    print("上传结果")
    print("=" * 60)
    success = sum(1 for v in results.values() if v)
    total = len(results)
    
    for title, ok in results.items():
        print(f"{title}: {'[成功]' if ok else '[失败]'}")
    
    print(f"\n总计: {success}/{total} 成功")
    
    if success == total:
        print("\n[完成] 所有文档已上传！")

if __name__ == "__main__":
    main()

