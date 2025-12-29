# smart_clip_llm.py
# 灵辑 (Smart Clip) - AI 内容收藏助手 LLM增强版 (基于通义千问)
# 核心对话引擎 (Core Conversation Engine)

from document_manager import DocumentManager
from intent_recognizer import LLMIntentRecognizer
from config import get_llm_client

class SmartClipLLM:
    def __init__(self):
        self.doc_manager = DocumentManager()
        self.client_config = get_llm_client()
        self.intent_recognizer = LLMIntentRecognizer(self.doc_manager, self.client_config)
        # 重置对话历史，确保每次启动时都是干净的状态
        # 这可以避免之前对话历史中的错误格式（如双大括号）影响后续的回复
        self.intent_recognizer.reset_conversation()
        self.is_running = True
        # 待确认的操作（用于二次确认机制）
        self.pending_action = None

    def _get_multiline_input(self):
        """
        获取多行输入，支持长文本输入和粘贴
        在 Windows 中，Ctrl+V 粘贴的内容会被 input() 一次性接收
        支持两种方式：
        1. 单行输入（直接粘贴或输入，按 Enter 提交）
        2. 多行输入（输入空行结束）
        """
        print("\n[用户] 请输入指令（可直接 Ctrl+V 粘贴，或输入空行结束多行输入）：")
        
        try:
            # 先读取第一行（在 Windows 中，粘贴的多行内容会被 input() 一次性接收）
            first_input = input()
            
            # 如果输入是空行，返回 None
            if not first_input.strip():
                return None
            
            # 首先检查是否是命令输入（可能是终端自动输入的）
            first_input_stripped = first_input.strip()
            # 更准确的命令检测：检查是否包含常见的命令模式
            is_command = (
                first_input_stripped.startswith(('&', 'python', 'E:/', 'i:/', 'I:/', './', '/')) or
                'python.exe' in first_input_stripped or
                'smart_clip_llm.py' in first_input_stripped or
                (first_input_stripped.startswith('&') and ('python' in first_input_stripped or '.py' in first_input_stripped))
            )
            
            if is_command:
                # 这是命令输入，忽略并继续等待真正的用户输入
                print(f"[系统提示] 检测到命令输入，已自动忽略（这是终端自动输入的命令）")
                print("[系统提示] 请直接输入您的指令")
                # 继续读取，直到得到真正的用户输入
                command_count = 1
                while command_count < 10:  # 最多尝试10次
                    try:
                        next_input = input()
                        if not next_input.strip():
                            return None
                        next_stripped = next_input.strip()
                        # 使用相同的检测逻辑
                        is_next_command = (
                            next_stripped.startswith(('&', 'python', 'E:/', 'i:/', 'I:/', './', '/')) or
                            'python.exe' in next_stripped or
                            'smart_clip_llm.py' in next_stripped or
                            (next_stripped.startswith('&') and ('python' in next_stripped or '.py' in next_stripped))
                        )
                        if is_next_command:
                            command_count += 1
                            if command_count <= 3:
                                print(f"[系统提示] 检测到命令输入，已自动忽略（第 {command_count} 次）")
                            continue
                        # 找到了真正的用户输入
                        first_input = next_input
                        break
                    except (KeyboardInterrupt, EOFError):
                        return None
                else:
                    # 如果连续10次都是命令，返回None
                    print("[系统提示] 检测到多次命令输入，请重新运行程序")
                    return None
            
            # 检查输入是否包含换行符（可能是粘贴的多行内容）
            # 在 Windows PowerShell 中，粘贴的多行内容可能包含 \r\n
            if '\n' in first_input or '\r' in first_input:
                # 处理粘贴的多行内容
                lines = first_input.replace('\r\n', '\n').replace('\r', '\n').split('\n')
                # 过滤掉命令行（使用改进的检测逻辑）
                def is_command_line(line):
                    stripped = line.strip()
                    return (
                        stripped.startswith(('&', 'python', 'E:/', 'i:/', 'I:/', './', '/')) or
                        'python.exe' in stripped or
                        'smart_clip_llm.py' in stripped or
                        (stripped.startswith('&') and ('python' in stripped or '.py' in stripped))
                    )
                lines = [line for line in lines if line.strip() and not is_command_line(line)]
                # 保留所有行（包括空行，因为可能是格式的一部分）
                # 但过滤掉首尾的空行
                while lines and not lines[0].strip():
                    lines.pop(0)
                while lines and not lines[-1].strip():
                    lines.pop()
                if lines:
                    return '\n'.join(lines)
                return None
            
            # 单行输入，检查用户是否要继续输入多行
            # 如果用户想输入多行，会继续输入；如果想提交单行，直接按 Enter（空行）
            lines = [first_input]
            
            # 继续读取，直到遇到空行
            command_count = 0
            max_command_ignore = 10  # 最多忽略10个连续的命令输入
            
            while True:
                try:
                    line = input()
                    if not line.strip():
                        # 空行表示输入完成
                        break
                    
                    # 过滤掉看起来像是命令行的输入（可能是误触或自动补全）
                    line_stripped = line.strip()
                    # 使用改进的命令检测逻辑
                    is_line_command = (
                        line_stripped.startswith(('&', 'python', 'E:/', 'i:/', 'I:/', './', '/')) or
                        'python.exe' in line_stripped or
                        'smart_clip_llm.py' in line_stripped or
                        (line_stripped.startswith('&') and ('python' in line_stripped or '.py' in line_stripped))
                    )
                    if is_line_command:
                        command_count += 1
                        if command_count <= 3:  # 只显示前3次的提示
                            print(f"[系统提示] 检测到命令输入，已自动忽略（第 {command_count} 次）")
                        elif command_count == 4:
                            print("[系统提示] 检测到多次命令输入，已全部自动忽略")
                            print("[系统提示] 提示：这些是终端自动输入的命令，不影响程序使用")
                            print("[系统提示] 请直接输入您的指令，或按 Enter（空行）提交当前内容")
                        
                        # 如果连续出现太多命令，可能是终端问题，直接返回已输入的内容
                        if command_count >= max_command_ignore:
                            print(f"[系统提示] 检测到 {command_count} 个连续的命令输入，可能是终端问题")
                            print("[系统提示] 已自动提交您之前输入的内容")
                            break
                        continue
                    
                    # 如果输入了正常内容，重置命令计数
                    command_count = 0
                    lines.append(line)
                except KeyboardInterrupt:
                    # 在输入过程中按 Ctrl+C
                    if lines:
                        print("\n[系统提示] 检测到 Ctrl+C，已保存当前输入。")
                        print("[系统提示] 如需继续输入，请继续输入；如需提交，请按 Enter（空行）")
                        print("[系统提示] 提示：如果出现自动输入的命令，程序会自动忽略，请继续输入您的指令")
                    else:
                        print("\n[系统提示] 检测到 Ctrl+C，输入已取消。")
                        return None
                except EOFError:
                    break
            
            # 合并所有行
            if lines:
                return '\n'.join(lines)
            return None
            
        except KeyboardInterrupt:
            print("\n[系统提示] 检测到 Ctrl+C，输入已取消。")
            return None
        except EOFError:
            return None
    
    def _ai_proactive_guide(self):
        """AI 主动引导式对话 (PRD 5.1)"""
        print("--------------------------------------------------")
        print("你好！我是你的文档助手‘灵辑’ (LLM增强版)。")
        print(f"当前活跃文档是：'{self.doc_manager.active_doc_title}'")
        print("你可以直接告诉我需要记录什么，或者想把内容添加到哪篇文档里。")
        print("试试对我说：‘把这句话记到我的日记里’")
        print("或者：‘把量子计算的科普文章加到学习笔记的第三章’")
        print("输入 '帮助' 查看更多指令，输入 '退出' 结束会话。")
        print("--------------------------------------------------")

    def _handle_intent(self, intent_data):
        """根据意图执行操作"""
        intent = intent_data.get("intent", "UNKNOWN")
        
        if intent == "ADD_CONTENT":
            title = intent_data.get("doc_title")
            content = intent_data.get("content")
            position = intent_data.get("position", "end")
            
            # 容错处理：确保position不是None、空字符串或其他无效值
            if position is None or position == "" or not isinstance(position, str):
                position = "end"
            
            # 容错处理：如果LLM没有返回doc_title，使用当前活跃文档
            if not title:
                title = self.doc_manager.active_doc_title
            
            # 调试信息：检查position的值
            if position is None:
                print(f"[调试] 警告：position 仍然是 None，使用默认值 'end'")
                position = "end"
            
            print(f"[AI反馈] 正在处理您的请求：将内容 '{content}' 添加到文档 '{title}' 的 '{position}' 位置...")
            self.doc_manager.add_content(title, content, position)
            print("[AI反馈] 搞定！内容已成功添加。")
            
        elif intent == "SET_ACTIVE":
            title = intent_data.get("doc_title")
            if title and self.doc_manager.set_active_document(title):
                print(f"[AI反馈] 已成功切换到文档 '{title}'。")
            else:
                print(f"[AI反馈] 文档 '{title}' 不存在或指令不明确。")

        elif intent == "DISPLAY_DOC":
            title = intent_data.get("doc_title")
            if not title:
                title = self.doc_manager.active_doc_title
            
            print(f"[AI反馈] 正在为您显示文档 '{title}' 的内容：")
            print(self.doc_manager.display_document(title))

        elif intent == "DELETE_CONTENT":
            title = intent_data.get("doc_title")
            content = intent_data.get("content")
            confirmation_needed = intent_data.get("confirmation_needed", False)
            
            # 容错处理：如果LLM没有返回doc_title，使用当前活跃文档
            if not title:
                title = self.doc_manager.active_doc_title
            
            # 如果需要确认，保存操作信息并询问用户
            if confirmation_needed:
                self.pending_action = {
                    "intent": "DELETE_CONTENT",
                    "title": title,
                    "content": content
                }
                print(f"\n[系统确认] 您要清空文档 '{title}' 的所有内容吗？")
                print(f"[系统确认] 此操作将删除文档中的所有内容，且无法恢复。")
                print(f"[系统确认] 请输入 '确认' 或 '是' 来执行，或输入 '取消' 或 '否' 来取消操作。")
                return  # 等待用户确认，不立即执行
            
            # 不需要确认，直接执行
            # 如果content为空或包含"所有内容"、"全部"等关键词，清空整个文档
            if not content or any(keyword in str(content).lower() for keyword in ["所有内容", "全部", "清空", "删除所有", "all"]):
                print(f"[AI反馈] 正在清空文档 '{title}' 的所有内容...")
                if self.doc_manager.clear_document(title):
                    print("[AI反馈] 搞定！文档已清空。")
                else:
                    print("[AI反馈] 清空文档失败。")
            else:
                # 删除特定内容（暂未实现，可以提示用户）
                print(f"[AI反馈] 删除特定内容的功能暂未实现。如需清空整个文档，请使用'删除[文档名]所有内容'")
        
        elif intent == "CONFIRM":
            # 处理用户确认
            if self.pending_action:
                action = self.pending_action
                if action["intent"] == "DELETE_CONTENT":
                    print(f"[AI反馈] 已确认，正在清空文档 '{action['title']}' 的所有内容...")
                    if self.doc_manager.clear_document(action["title"]):
                        print("[AI反馈] 搞定！文档已清空。")
                    else:
                        print("[AI反馈] 清空文档失败。")
                # 清除待确认操作
                self.pending_action = None
            else:
                print("[AI反馈] 没有待确认的操作。")
        
        elif intent == "CANCEL":
            # 处理用户取消
            if self.pending_action:
                action = self.pending_action
                print(f"[AI反馈] 已取消清空文档 '{action['title']}' 的操作。")
                self.pending_action = None
            else:
                print("[AI反馈] 没有待确认的操作。")

        elif intent == "HELP":
            # 优先检查LLM是否生成了可以直接回复的内容（如自我介绍、详细说明等）
            content = intent_data.get("content")
            if content and isinstance(content, str) and len(content.strip()) > 0:
                # 如果有LLM生成的内容，直接打印（更自然、更人性化）
                print(f"[AI反馈] {content}")
            else:
                # 如果没有LLM生成的内容，打印固定的帮助菜单（标准化功能说明）
                print("[AI反馈] 我能理解以下指令：")
                print("1. 添加内容：'把[内容]加到[文档名]的[开头/结尾/某个段落之后]'")
                print("   示例：'把今天的会议要点加到项目周报的结尾'")
                print("2. 切换文档：'打开[文档名]'")
                print("   示例：'打开学习笔记'")
                print("3. 查看文档：'查看[文档名]'")
                print("   示例：'显示项目周报'")
                print("4. 删除/清空文档：'删除[文档名]所有内容' 或 '清空[文档名]'")
                print("   示例：'删除默认文档所有内容'")
                print("5. 重置对话：'重置对话' 或 '清空对话历史'")
                print("   示例：'重置对话'（清空对话历史，重新开始）")
                print("6. 退出：'退出'")

        elif intent == "RESET_CONVERSATION" or intent == "CLEAR_CONVERSATION":
            # 重置对话历史（由LLM识别自然表达，如"让我们重新开始聊天"）
            self.intent_recognizer.reset_conversation()
            # 同时清除待确认的操作
            if self.pending_action:
                self.pending_action = None
                print("[AI反馈] 已清除待确认的操作。")
            print("[AI反馈] 对话历史已重置，可以重新开始对话了。")

        elif intent == "EXIT":
            print("[AI反馈] 感谢您的使用，再见！")
            self.is_running = False

        elif intent == "UNKNOWN":
            print("[AI反馈] 抱歉，我没有理解您的指令。请尝试使用更清晰的表达，例如：")
            print("  '把[内容]加到[文档名]的[开头/结尾]'")
            print("  '打开[文档名]'")
            print("  '查看[文档名]'")
            
        # 成功反馈与功能扩展 (PRD 5.1)
        if intent in ["ADD_CONTENT", "SET_ACTIVE", "DISPLAY_DOC"]:
            print("\n[AI反馈] 下次你还可以试试更复杂的指令，比如：‘把刚才的会议纪要加到项目周报的开头’，我能帮你自动找到位置。")


    def run(self):
        """主循环"""
        self._ai_proactive_guide()
        
        while self.is_running:
            try:
                # 支持多行输入
                user_input = self._get_multiline_input()
                if user_input is None:  # Ctrl+C 或 EOF
                    continue
                
                # 过滤掉空输入
                if not user_input or not user_input.strip():
                    continue
                
                # 过滤掉看起来像是命令行的输入（可能是误触或自动补全）
                user_input_stripped = user_input.strip()
                # 使用改进的命令检测逻辑
                is_command_input = (
                    user_input_stripped.startswith(('&', 'python', 'E:/', 'i:/', 'I:/', './', '/')) or
                    'python.exe' in user_input_stripped or
                    'smart_clip_llm.py' in user_input_stripped or
                    (user_input_stripped.startswith('&') and ('python' in user_input_stripped or '.py' in user_input_stripped))
                )
                if is_command_input:
                    print("[系统提示] 检测到可能是命令输入，已忽略。请输入文档操作指令。")
                    print("[系统提示] 示例：'把测试内容加到默认文档'")
                    print("[系统提示] 提示：如果出现自动输入的命令，程序会自动忽略，请继续输入您的指令")
                    continue
                
                # 检查是否包含多个重复的命令行（可能是终端自动输入）
                lines = user_input.split('\n')
                def is_command_line(line):
                    stripped = line.strip()
                    return (
                        stripped.startswith(('&', 'python', 'E:/', 'i:/', 'I:/', './', '/')) or
                        'python.exe' in stripped or
                        'smart_clip_llm.py' in stripped or
                        (stripped.startswith('&') and ('python' in stripped or '.py' in stripped))
                    )
                command_lines = [line for line in lines if line.strip() and is_command_line(line)]
                if len(command_lines) > 1:
                    print(f"[系统提示] 检测到 {len(command_lines)} 行命令输入，已全部忽略。")
                    print("[系统提示] 请重新输入您的文档操作指令")
                    continue
                
                # 深度优化：智能处理待确认操作
                intent_data = None  # 初始化，用于存储解析后的意图
                
                if self.pending_action:
                    user_input_lower = user_input.strip().lower()
                    
                    # 1. 优先处理明确的确认/取消
                    if user_input_lower in ["确认", "是", "yes", "y", "ok", "确定"]:
                        self._handle_intent({"intent": "CONFIRM"})
                        continue
                    elif user_input_lower in ["取消", "否", "no", "n", "不"]:
                        self._handle_intent({"intent": "CANCEL"})
                        continue
                    
                    # 2. 如果不是明确的确认/取消，将新指令发给LLM预解析
                    print("[系统] 正在解析您的新指令，请稍候...")
                    new_intent_data = self.intent_recognizer.recognize(user_input)
                    
                    # 3. 对比新旧意图
                    old_action = self.pending_action
                    # 检查新意图是否与待确认操作一致（都是删除同一个文档）
                    new_intent = new_intent_data.get("intent")
                    new_doc_title = new_intent_data.get("doc_title")
                    # 处理 new_intent_data['doc_title'] 可能为 None 的情况
                    if not new_doc_title:
                        new_doc_title = self.doc_manager.active_doc_title
                    
                    is_same_intent = (
                        new_intent == "DELETE_CONTENT" and
                        old_action["intent"] == "DELETE_CONTENT" and
                        new_doc_title == old_action["title"]
                    )
                    
                    if is_same_intent:
                        # 3.1 如果意图一致，视为用户在重复指令以确认
                        print(f"\n[AI反馈] 您似乎在重复清空文档 '{old_action['title']}' 的指令，我将此理解为确认操作。")
                        self._handle_intent({"intent": "CONFIRM"})  # 直接执行确认
                        continue
                    else:
                        # 3.2 如果意图不一致，给用户选择权
                        print(f"\n[系统提示] 您当前有一个待确认的操作（清空文档 '{old_action['title']}'）。")
                        print(f"[系统提示] 而您输入了一个新的指令（意图：{new_intent}）。")
                        print(f"[系统提示] 请问您想：")
                        print(f"  1. 继续执行新指令（将自动取消清空操作）")
                        print(f"  2. 返回并确认/取消之前的清空操作")
                        print(f"[系统提示] 请输入 '1' 或 '2' 作出选择：")
                        
                        try:
                            choice = input().strip()
                            if choice == '1':
                                print("[AI反馈] 好的，已取消之前的清空操作，现在执行您的新指令。")
                                self.pending_action = None  # 清除待确认操作
                                # 使用已经解析好的新意图数据，避免重复调用LLM
                                intent_data = new_intent_data
                            else:
                                print("[AI反馈] 好的，请继续对清空操作进行确认或取消。")
                                # 不做任何事，等待下一轮循环用户输入"确认"或"取消"
                                continue
                        except (KeyboardInterrupt, EOFError):
                            print("\n[系统提示] 输入已取消，请继续对清空操作进行确认或取消。")
                            continue
                
                # 如果没有pending_action，或者pending_action存在但用户选择了执行新指令，才需要解析意图
                if intent_data is None:
                    # 先检查是否是重置对话的指令（快速检查，避免不必要的LLM调用）
                    user_input_lower = user_input.strip().lower()
                    if any(keyword in user_input_lower for keyword in ["重置对话", "清空对话", "清空对话历史", "重置对话历史", "重新开始", "reset conversation", "clear conversation"]):
                        self.intent_recognizer.reset_conversation()
                        if self.pending_action:
                            self.pending_action = None
                            print("[AI反馈] 已清除待确认的操作。")
                        print("[AI反馈] 对话历史已重置，可以重新开始对话了。")
                        continue
                    
                    # 意图识别
                    intent_data = self.intent_recognizer.recognize(user_input)
                
                # 检查是否需要确认
                confirmation_needed = intent_data.get("confirmation_needed", False)
                if confirmation_needed and intent_data.get("intent") == "DELETE_CONTENT":
                    # 需要确认的操作，保存到 pending_action 并在 _handle_intent 中处理
                    pass  # _handle_intent 中已经处理了
                
                # 执行意图
                self._handle_intent(intent_data)
                
            except KeyboardInterrupt:
                # 捕获 Ctrl+C，允许用户复制终端内容
                print("\n[系统提示] 检测到 Ctrl+C，程序暂停。")
                print("[系统提示] 如需退出程序，请输入 '退出' 或再次按 Ctrl+C")
                print("[系统提示] 如需继续，请直接输入指令")
                continue
            except EOFError:
                print("\n[AI反馈] 会话已结束。")
                self.is_running = False
                break
            except Exception as e:
                # 如果是 KeyboardInterrupt 或 EOFError，不应该到这里（应该被上面的 except 捕获）
                # 但为了安全，还是检查一下
                if isinstance(e, (KeyboardInterrupt, EOFError)):
                    if isinstance(e, KeyboardInterrupt):
                        print("\n[系统提示] 检测到 Ctrl+C，程序暂停。")
                        print("[系统提示] 如需退出程序，请输入 '退出'")
                        print("[系统提示] 如需继续，请直接输入指令")
                        continue
                    else:  # EOFError
                        print("\n[AI反馈] 会话已结束。")
                        self.is_running = False
                        break
                
                # 其他异常：打印详细的错误信息
                import traceback
                import sys
                print("\n" + "="*60)
                print(f"[系统错误] 发生了一个错误: {e}")
                print(f"[系统错误] 错误类型: {type(e).__name__}")
                print(f"[系统错误] 详细错误信息:")
                print("-"*60)
                # 获取错误堆栈
                exc_type, exc_value, exc_traceback = sys.exc_info()
                tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
                # 过滤掉包含误导性信息的行，但保留所有实际的错误位置
                filtered_lines = []
                for line in tb_lines:
                    # 保留所有文件位置行和错误信息行
                    if 'File "' in line or 'Traceback' in line or exc_type.__name__ in line:
                        filtered_lines.append(line)
                    # 跳过包含误导性信息的代码行（如 Ctrl+C、print 语句等）
                    elif 'Ctrl+C' not in line and 'print(' not in line and 'input()' not in line:
                        filtered_lines.append(line)
                # 如果没有过滤掉所有行，使用过滤后的；否则使用原始的
                if filtered_lines:
                    print(''.join(filtered_lines))
                else:
                    traceback.print_exc()
                print("="*60 + "\n")
                print("[提示] 如需复制错误信息，请：")
                print("  1. 用鼠标选中上面的错误文本")
                print("  2. 按 Enter 键或右键点击即可复制到剪贴板")
                print("  3. 或使用 Ctrl+Shift+C（部分终端支持）")
                
if __name__ == "__main__":
    app = SmartClipLLM()
    app.run()
