# document_manager.py
# 本地文本文件存储系统 (Local Text File Storage System)

import json
from pathlib import Path

class DocumentManager:
    def __init__(self, storage_dir="documents", demo_mode=True):
        """
        初始化文档管理器
        
        Args:
            storage_dir: 文档存储目录，默认为 "documents"
            demo_mode: 演示模式，True 时不保存到文件系统，只使用内存
        """
        self.demo_mode = demo_mode  # 演示模式标志
        # 设置存储目录
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)  # 如果目录不存在则创建
        
        # 元数据文件，记录文档列表和当前活跃文档
        self.metadata_file = self.storage_dir / "metadata.json"
        
        # 从本地文件加载文档
        self.documents = {}
        self.active_doc_title = "试用文档"
        
        if self.demo_mode:
            # 演示模式：只使用内存，不加载文件
            print("[DocumentManager] 演示模式已启用，不保存到文件系统")
            self._init_demo_documents()
        else:
            # 正常模式：从文件加载
            self._load_documents()
            
            # 如果没有任何文档，创建试用文档（空白）
            if not self.documents:
                default_content = [""]
                self.documents["试用文档"] = default_content
                self._save_document("试用文档")
                self._save_metadata()

    def _get_document_file(self, title):
        """获取文档对应的文件路径"""
        # 清理文件名，移除不允许的字符
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_', '(', ')', '（', '）')).strip()
        if not safe_title:
            safe_title = "untitled"
        return self.storage_dir / f"{safe_title}.txt"
    
    def _load_documents(self):
        """从本地文件加载所有文档"""
        # 辅助函数：检测是否包含默认占位文本
        def contains_default(c):
            s = str(c)
            return (
                ("这是您的试用文档" in s)
                or ("可以随时添加内容" in s)
                or ("这是您的默认文档" in s)
            )
        
        # 加载元数据
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                    self.active_doc_title = metadata.get("active_doc_title", "试用文档")
            except Exception as e:
                print(f"[系统警告] 加载元数据失败: {e}")
        
        # 加载所有文档文件
        for file_path in self.storage_dir.glob("*.txt"):
            title = file_path.stem  # 文件名（不含扩展名）
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    # 按行分割内容，保留空行
                    if content:
                        doc_content = [line for line in content.split('\n')]
                        # 检测并清理默认占位文本
                        if contains_default(doc_content):
                            print(f"[DocumentManager] ⚠️ 检测到文档 '{title}' 包含默认占位文本，正在清理...")
                            if title == "试用文档":
                                doc_content = [""]  # 试用文档应该是空白的
                                self.documents[title] = doc_content
                                self._save_document(title)  # 立即保存清理后的内容
                            elif title == "PM问答笔记":
                                # PM问答笔记应该包含完整内容，返回空列表让初始化逻辑创建
                                doc_content = []
                                self.documents[title] = doc_content
                            else:
                                doc_content = []
                                self.documents[title] = doc_content
                        else:
                            self.documents[title] = doc_content
                    else:
                        self.documents[title] = []
            except Exception as e:
                print(f"[系统警告] 加载文档 '{title}' 失败: {e}")
        
        # 确保活跃文档存在
        if self.active_doc_title not in self.documents and self.documents:
            self.active_doc_title = list(self.documents.keys())[0]
    
    def _save_document(self, title):
        """将文档保存到本地文件"""
        if title not in self.documents:
            return
        
        # 演示模式：不保存到文件
        if self.demo_mode:
            return
        
        # 检测并清理默认占位文本（防止保存时写入）
        def contains_default(c):
            s = str(c)
            return (
                ("这是您的试用文档" in s)
                or ("可以随时添加内容" in s)
                or ("这是您的默认文档" in s)
            )
        
        content = self.documents[title]
        if contains_default(content):
            print(f"[DocumentManager] ⚠️ 保存前检测到文档 '{title}' 包含默认占位文本，正在清理...")
            if title == "试用文档":
                content = [""]  # 试用文档应该是空白的
                self.documents[title] = content
            elif title == "PM问答笔记":
                content = []  # PM问答笔记应该包含完整内容，不应该有默认文本
                self.documents[title] = content
            else:
                content = []
                self.documents[title] = content
        
        file_path = self._get_document_file(title)
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                # 将内容列表写入文件，每行一个
                f.write('\n'.join(content))
        except Exception as e:
            print(f"[系统错误] 保存文档 '{title}' 失败: {e}")
    
    def _save_metadata(self):
        """保存元数据（活跃文档等）"""
        # 演示模式：不保存到文件
        if self.demo_mode:
            return
        
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "active_doc_title": self.active_doc_title
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[系统警告] 保存元数据失败: {e}")

    def get_document_titles(self):
        """获取所有文档标题"""
        return list(self.documents.keys())

    def get_document(self, title):
        """获取指定标题的文档内容"""
        content = self.documents.get(title)
        if content is None:
            return None
        
        # 检测并清理默认占位文本
        def contains_default(c):
            s = str(c)
            return (
                ("这是您的试用文档" in s)
                or ("可以随时添加内容" in s)
                or ("这是您的默认文档" in s)
            )
        
        if contains_default(content):
            print(f"[DocumentManager] ⚠️ 检测到文档 '{title}' 包含默认占位文本，正在清理...")
            if title == "试用文档":
                content = [""]  # 试用文档应该是空白的
                self.documents[title] = content
                self._save_document(title)  # 立即保存清理后的内容
            elif title == "PM问答笔记":
                content = []  # 返回空列表，让初始化逻辑创建正确的内容
                self.documents[title] = content
            else:
                content = []
                self.documents[title] = content
        
        return content

    def set_active_document(self, title):
        """设置当前活跃文档"""
        if title in self.documents:
            self.active_doc_title = title
            self._save_metadata()
            return True
        return False

    def add_content(self, title, content, position="end"):
        """
        基础文字内容添加和极简文档定位。
        支持定位到文档标题、开头、结尾。
        """
        if title not in self.documents:
            self.documents[title] = []
            print(f"[系统] 文档 '{title}' 不存在，已为您创建。")

        doc = self.documents[title]
        
        # 处理内容：如果包含换行符，按行分割添加到文档
        # 这样可以保留多行内容的格式
        content_lines = content.split('\n') if '\n' in content else [content]
        # 过滤掉空行（保留内容的原始格式，但去掉首尾空行）
        while content_lines and not content_lines[0].strip():
            content_lines.pop(0)
        while content_lines and not content_lines[-1].strip():
            content_lines.pop()
        
        # 处理position为None或非字符串的情况，默认为"end"
        # 确保 position 始终是字符串，避免调用 .lower() 时出错
        if position is None:
            position_str = "end"
        elif not isinstance(position, str):
            # 如果不是字符串，尝试转换为字符串
            try:
                position_str = str(position) if position else "end"
            except:
                position_str = "end"
        elif position == "":
            # 空字符串也使用默认值
            position_str = "end"
        else:
            position_str = position
        
        # 转换为小写（此时 position_str 一定是字符串）
        try:
            position = position_str.lower()
        except (AttributeError, TypeError):
            # 理论上不应该到这里，但为了安全还是加上
            position = "end"
        
        # 简化定位逻辑：只处理 start/end，其他视为 end
        if position == "start":
            # 插入到开头（注意：列表在前面，所以从后往前插入）
            for line in reversed(content_lines):
                doc.insert(0, line)
            pos_desc = "开头"
        elif position == "end":
            # 追加到结尾
            for line in content_lines:
                doc.append(line)
            pos_desc = "结尾"
        else:
            # 尝试按内容定位（MVP简化版）
            try:
                index = -1
                for i, line in enumerate(doc):
                    if position in line:
                        index = i
                        break
                
                if index != -1:
                    # 插入到指定位置之后
                    for i, line in enumerate(content_lines):
                        doc.insert(index + 1 + i, line)
                    pos_desc = f"'{position}' 之后"
                else:
                    # 未找到位置，追加到结尾
                    for line in content_lines:
                        doc.append(line)
                    pos_desc = "结尾 (未找到指定位置)"
            except Exception:
                # 定位失败，追加到结尾
                for line in content_lines:
                    doc.append(line)
                pos_desc = "结尾 (定位失败)"

        # 保存到本地文件
        self._save_document(title)
        
        print(f"[系统] 内容已成功添加到文档 '{title}' 的 {pos_desc}。")
        return True

    def clear_document(self, title):
        """清空文档的所有内容"""
        if title not in self.documents:
            print(f"[系统] 文档 '{title}' 不存在。")
            return False
        
        self.documents[title] = []
        self._save_document(title)
        print(f"[系统] 文档 '{title}' 的所有内容已清空。")
        return True

    def display_document(self, title):
        """显示文档内容"""
        doc = self.documents.get(title, [])
        if not doc:
            return f"文档 '{title}' 为空。"
        
        output = f"--- 文档: {title} ---\n"
        for i, line in enumerate(doc):
            output += f"{i+1}. {line}\n"
        output += "----------------------"
        return output
    
    def _init_demo_documents(self):
        """初始化演示文档（只在内存中）"""
        print("[DocumentManager] 正在初始化演示文档...")
        
        # 初始化空白的试用文档
        self.documents["试用文档"] = [""]
        
        # 初始化通信原理笔记（完整内容）
        # 注意：这里的内容必须与 api_server.py 中的定义保持一致
        communication_notes = [
            "## 第一章 绪论",
            "通信的基本概念：通信是将信息从一地传输到另一地的过程。通信系统模型包括信源、发送设备、信道、接收设备和信宿。模拟通信系统和数字通信系统的区别在于传输信号的性质。",
            "",
            "## 第二章 确知信号",
            "确知信号是指其波形随时间的变化规律完全确定的信号。确知信号的频域分析包括傅里叶级数和傅里叶变换。功率信号和能量信号的区别。",
            "",
            "## 第三章 随机过程",
            "随机过程是随时间变化的随机变量。平稳随机过程的统计特性不随时间推移而改变。高斯随机过程的概率密度函数服从高斯分布。白噪声的功率谱密度在整个频域内为常数。",
            "",
            "## 第四章 信道",
            "信道是信号传输的媒介。信道分为有线信道和无线信道。信道的数学模型包括加性噪声信道和线性时变滤波器信道。信道容量是指信道能够无差错传输的最大信息速率，由香农公式给出。",
            "",
            "## 第五章 模拟调制系统",
            "调制是将基带信号搬移到高频载波上的过程。模拟调制包括幅度调制（AM、DSB、SSB、VSB）和角度调制（FM、PM）。抗噪声性能分析比较了不同调制方式的信噪比增益。",
            "",
            "## 第六章 数字基带传输系统",
            "数字基带传输是指不经过调制，直接在信道中传输数字信号。码间干扰（ISI）是影响数字基带传输性能的主要因素。奈奎斯特准则给出了无码间干扰的条件。眼图用于直观评估数字信号的质量。",
            "",
            "## 第七章 信道编码",
            "",
            "信道编码是为了提高传输可靠性而添加的冗余信息，目的是检测和纠正传输错误。信道编码的理论基础是香农第二定理，它指出只要信息传输速率小于信道容量，就可以通过适当的编码实现任意小的误码率。信道编码分为分组码和卷积码两大类。",
            "",
            "### 7.1 线性分组码",
            "",
            "线性分组码是信息位和校验位满足线性关系的分组码。线性分组码可以用生成矩阵或校验矩阵来描述。生成矩阵G用于编码，校验矩阵H用于译码和检错。线性分组码具有封闭性，任意两个码字的线性组合仍是码字。汉明码是一种重要的线性分组码，可以纠正单个错误。循环码是线性分组码的一个子类，具有循环移位不变性，可以用多项式来描述，实现简单。BCH码和RS码是循环码的重要类型，具有强大的纠错能力，广泛应用于数字通信和存储系统。",
            "",
            "### 7.2 卷积码",
            "",
            "卷积码的输出不仅与当前输入有关，还与之前的输入有关，具有记忆性。卷积码可以用生成多项式或状态图来描述。维特比算法是卷积码的最优译码算法，通过动态规划找到最可能的码字序列，计算复杂度适中，应用广泛。Turbo码是一种并行级联卷积码，通过迭代译码可以获得接近香农限的性能，是3G和4G移动通信系统的关键技术。LDPC码是另一种接近香农限的编码方式，具有稀疏的校验矩阵，译码复杂度低，广泛应用于5G通信系统。",
            "",
            "## 第八章 同步",
            "",
            "同步是数字通信系统中的关键技术，包括载波同步、位同步和帧同步。同步的准确性直接影响系统的性能，同步误差会导致误码率增加甚至系统失效。",
            "",
            "### 8.1 载波同步",
            "",
            "载波同步是接收端恢复载波的过程，对于相干解调至关重要。载波同步方法分为开环法和闭环法。开环法直接从接收信号中提取载波，实现简单但性能有限。闭环法通过锁相环（PLL）跟踪载波相位，性能好但实现复杂。对于PSK信号，可以采用平方环或Costas环提取载波。载波同步的精度用相位误差来衡量，相位误差会导致解调性能下降。",
            "",
            "### 8.2 位同步",
            "",
            "位同步是接收端恢复码元时钟的过程，用于确定码元的采样时刻。位同步方法分为开环法和闭环法。开环法从接收信号中直接提取时钟，如滤波法、微分法等。闭环法通过锁相环跟踪时钟相位，性能更好。数字锁相环（DPLL）是常用的位同步方法，通过比较本地时钟和接收信号的相位差来调整时钟频率。位同步的精度用定时误差来衡量，定时误差会导致码间干扰增加。",
            "",
            "### 8.3 帧同步",
            "",
            "帧同步是接收端识别帧起始位置的过程，用于正确解帧。帧同步通常通过在帧头插入特殊的同步码来实现。同步码的选择要考虑自相关性和互相关性，常用的有巴克码、m序列等。帧同步方法分为逐码移位法和存储相关法。逐码移位法逐位比较，实现简单但速度慢。存储相关法利用相关器快速找到同步位置，速度快但实现复杂。帧同步的可靠性用漏同步概率和假同步概率来衡量。",
            "",
            "## 第九章 多路复用和多址技术",
            "",
            "多路复用和多址技术是为了提高信道利用率，允许多个用户共享同一信道。多路复用是在发送端将多个信号合并，多址是在接收端区分不同用户的信号。常用的技术包括频分复用、时分复用、码分复用等。",
            "",
            "### 9.1 频分复用（FDM）",
            "",
            "频分复用是将不同信号调制到不同频率的载波上，在频域上分离。FDM系统将可用频带划分为多个子频带，每个子频带传输一路信号。FDM的优点是实现简单，各路信号相互独立。缺点是需要保护频带防止干扰，频带利用率不高。FDM广泛应用于模拟通信系统，如调频广播、有线电视等。正交频分复用（OFDM）是FDM的改进，通过使用正交的子载波，提高了频带利用率，是4G和5G移动通信系统的核心技术。",
            "",
            "### 9.2 时分复用（TDM）",
            "",
            "时分复用是将不同信号分配到不同的时隙，在时域上分离。TDM系统将时间划分为多个时隙，每个时隙传输一路信号。TDM的优点是各路信号可以使用相同的频带，频带利用率高。缺点是需要严格的时钟同步。TDM广泛应用于数字通信系统，如数字电话、SDH等。统计时分复用（STDM）根据业务需求动态分配时隙，进一步提高了信道利用率。",
            ""
        ]
        self.documents["通信原理笔记"] = communication_notes
        
        # 设置活跃文档
        self.active_doc_title = "试用文档"
        
        print(f"[DocumentManager] 演示文档初始化完成，共 {len(self.documents)} 个文档")
