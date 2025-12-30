# d1_document_manager.py
# 基于 Cloudflare D1 的文档管理器
# 支持开发者文档和试用文档分离

import json
from d1_storage import D1Storage
from web.update_log_content import UPDATE_LOG_TITLE, UPDATE_LOG_CONTENT

class D1DocumentManager:
    """
    基于 Cloudflare D1 的文档管理器
    支持开发者文档和试用文档分离存储
    """
    
    def __init__(self, d1_database=None, doc_type="dev", session_id=None, dev_mode_enabled=False):
        """
        初始化 D1 文档管理器
        
        Args:
            d1_database: Cloudflare D1 数据库对象
            doc_type: 文档类型，"dev"（开发者文档）或 "trial"（试用文档）
            session_id: 会话ID（试用模式必需）
            dev_mode_enabled: 是否已启用开发者模式
        """
        self.storage = D1Storage(d1_database)
        self.doc_type = doc_type
        self.session_id = session_id
        self.dev_mode_enabled = dev_mode_enabled
        self.edit_mode_enabled = False
        self.documents = {}
        # 开发者模式：默认文档是"介绍文档"
        # 试用模式：默认文档是"试用文档"
        self.active_doc_title = "介绍文档" if doc_type == "dev" else "试用文档"
        self.intro_doc_title = "介绍文档" if doc_type == "dev" else "PM问答笔记"  # 开发者模式用介绍文档，试用模式用PM问答笔记
        self.update_log_title = UPDATE_LOG_TITLE  # 更新记录日志名称
        self._initialized = False
    
    async def initialize(self):
        """异步初始化，加载文档和元数据"""
        if self._initialized:
            return
        
        # 加载元数据
        metadata = await self.storage.get_metadata(self.doc_type)
        self.active_doc_title = metadata.get("active_doc_title", self.active_doc_title)
        
        # 加载所有文档
        doc_titles = await self.storage.list_documents(self.doc_type, self.session_id)
        print(f"[D1DocumentManager] 从数据库加载的文档标题: {doc_titles}")
        for title in doc_titles:
            content = await self.storage.get_document(title, self.doc_type, self.session_id)
            self.documents[title] = content
            print(f"[D1DocumentManager] 已加载文档: {title}, 内容行数: {len(content) if content else 0}")
        
        # 如果是开发者模式，确保有介绍文档（如果已存在但内容为空或过时，也更新）
        if self.doc_type == "dev":
            # 检查介绍文档是否存在，或者内容是否为空/过时
            existing_content = self.documents.get(self.intro_doc_title, [])
            is_empty_or_old = (
                not existing_content or 
                len(existing_content) < 10 or  # 如果内容少于10行，认为是旧版本
                "产品概述" not in str(existing_content) or  # 如果缺少新内容标识
                "混沌缓冲区" not in str(existing_content)  # 如果缺少最新的混沌缓冲区章节，强制更新
            )
            
            if self.intro_doc_title not in self.documents or is_empty_or_old:
                print(f"[D1DocumentManager] 检测到介绍文档需要更新 (is_empty_or_old={is_empty_or_old})")
                from web.new_intro_content import INTRO_CONTENT_FULL
                intro_content = INTRO_CONTENT_FULL
                self.documents[self.intro_doc_title] = intro_content
                await self.storage.save_document(self.intro_doc_title, intro_content, "dev")
                await self.storage.save_metadata({"active_doc_title": self.intro_doc_title}, "dev")
        
        # 如果是开发者模式，确保有更新记录日志
        if self.doc_type == "dev" and self.update_log_title not in self.documents:
            self.documents[self.update_log_title] = UPDATE_LOG_CONTENT
            await self.storage.save_document(self.update_log_title, UPDATE_LOG_CONTENT, "dev")
        
        # 如果是试用模式，确保有试用文档（空白文档）
        if self.doc_type == "trial" and "试用文档" not in self.documents:
            print(f"[D1DocumentManager] 创建试用文档 (session_id={self.session_id})")
            default_content = [""]  # 空白文档，只有一个空字符串
            self.documents["试用文档"] = default_content
            await self.storage.save_document("试用文档", default_content, "trial", self.session_id)
            await self.storage.save_metadata({"active_doc_title": "试用文档"}, "trial")
            print(f"[D1DocumentManager] 试用文档已创建并保存")
        
        # 如果是试用模式，确保有PM问答笔记
        if self.doc_type == "trial" and "PM问答笔记" not in self.documents:
            print(f"[D1DocumentManager] 创建PM问答笔记 (session_id={self.session_id})")
            pm_content = [
                "欢迎使用灵辑 (Mindscribe) - AI 内容收藏助手",
                "",
                "## PM问答笔记",
                "",
                "这是您的PM问答笔记，用于记录产品经理相关的问答内容。",
                "",
                "## 🆕 最新功能更新（2025-01-23）",
                "",
                "### ✨ 强化意图识别",
                "",
                "系统现在能够更准确地识别您的添加意图，特别是对于数学题目、学习内容等：",
                "",
                "- **数学题目识别**：",
                "  - \"这道数学题：求解方程 x² + 5x + 6 = 0\" → 自动识别为添加意图",
                "  - \"求解：x² - 1 = 0\" → 自动识别为添加意图",
                "  - \"证明：勾股定理\" → 自动识别为添加意图",
                "",
                "- **学习内容识别**：",
                "  - \"今天学了量子计算\" → 自动识别为添加意图",
                "  - \"知识点：相对论\" → 自动识别为添加意图",
                "",
                "- **工作内容识别**：",
                "  - \"会议要点：下周发布新版本\" → 自动识别为添加意图",
                "  - \"项目进度：已完成80%\" → 自动识别为添加意图",
                "",
                "### 🔍 文档匹配检查",
                "",
                "系统现在会自动检查您要添加的内容是否与当前文档类型匹配：",
                "",
                "- **智能匹配**：",
                "  - 如果内容与文档类型匹配，直接添加",
                "  - 如果不匹配，会提示您确认或建议创建新文档",
                "",
                "- **智能建议**：",
                "  - 学习内容建议创建\"学习笔记\"",
                "  - 工作内容建议创建\"工作笔记\"",
                "  - 灵感内容建议创建\"灵感笔记\"",
                "",
                "- **新建文档功能**：",
                "  - 如果选择\"新建文档\"，系统会自动创建新文档",
                "  - 创建后会自动将您的内容填充到输入框，方便直接发送",
                "",
                "### 🎨 界面优化",
                "",
                "- **试用模式Logo动画**：",
                "  - 处理中时，logo会在顶部栏中间闪烁显示",
                "  - 处理完成后自动消失",
                "",
                "- **对话格式示例面板**：",
                "  - 默认收缩状态，界面更简洁",
                "  - 点击header任何区域都可以展开/收起",
                "",
                "- **浏览器标签页图标**：",
                "  - 添加了窗口logo作为favicon",
                "  - 提升品牌识别度",
                "",
                "### 💡 使用技巧",
                "",
                "1. **直接输入内容**：",
                "   - 无需说\"保存\"或\"添加\"，直接输入内容即可",
                "   - 例如：\"这道数学题：求解方程 x² + 5x + 6 = 0\"",
                "",
                "2. **文档匹配提示**：",
                "   - 如果系统提示文档不匹配，可以选择：",
                "     - 确定添加：继续添加到当前文档",
                "     - 新建文档：创建新文档并自动填充内容",
                "     - 取消：取消操作",
                "",
                "3. **智能归类**：",
                "   - 系统会自动将内容归类到合适的章节",
                "   - 例如：\"今天学了量子计算\"会自动归类到\"物理\"主题下的\"量子计算\"章节",
                "",
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                "",
                "## 📝 面试准备内容",
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
            self.documents["PM问答笔记"] = pm_content
            await self.storage.save_document("PM问答笔记", pm_content, "trial", self.session_id)
            print(f"[D1DocumentManager] PM问答笔记已创建并保存")
        
        # 如果是试用模式，确保有通信原理笔记
        if self.doc_type == "trial" and "通信原理笔记" not in self.documents:
            print(f"[D1DocumentManager] 创建通信原理笔记 (session_id={self.session_id})")
            communication_content = [
                "# 通信原理笔记",
                "",
                "## 第一章 绪论",
                "",
                "通信原理是研究信息传输、处理和存储的基本理论和技术。通信系统的基本任务是实现信息的有效传输，确保信息从信源准确、可靠地传送到信宿。现代通信系统已经成为信息社会的基础设施，广泛应用于电话、互联网、广播电视、移动通信等各个领域。",
                "",
                "### 1.1 通信系统的基本组成",
                "",
                "通信系统主要由五个基本部分组成：信源、发送设备、信道、接收设备和信宿。信源是产生信息的源头，可以是人、机器或其他信息源。发送设备的作用是将信源产生的信息转换为适合在信道中传输的信号形式，包括编码、调制、放大等功能。信道是信号传输的媒介，可以是导线、光纤、无线电波等。接收设备的作用是接收信道中的信号，并进行解调、解码等处理，恢复出原始信息。信宿是信息的最终接收者。",
                "",
                "### 1.2 通信系统的分类",
                "",
                "通信系统可以按照多种方式进行分类。按传输媒介可分为有线通信和无线通信。有线通信使用导线、光纤等物理媒介，具有传输稳定、抗干扰能力强的优点，但需要铺设线路，成本较高。无线通信使用电磁波在空间中传播，具有灵活性强、覆盖范围广的优点，但容易受到干扰。按信号类型可分为模拟通信和数字通信。模拟通信传输的是连续变化的模拟信号，数字通信传输的是离散的数字信号。数字通信具有抗干扰能力强、易于加密、便于存储和处理等优点，已成为现代通信的主流。",
                "",
                "### 1.3 通信系统的主要性能指标",
                "",
                "通信系统的主要性能指标包括有效性、可靠性和经济性。有效性是指系统传输信息的速率，通常用信息传输速率或频带利用率来衡量。可靠性是指系统传输信息的准确程度，通常用误码率、误信率等指标来衡量。经济性是指系统的成本效益，包括设备成本、维护成本等。在实际应用中，有效性和可靠性往往存在矛盾，需要在两者之间进行权衡。",
                "",
                "## 第二章 信号与系统",
                "",
                "信号是信息的载体，是随时间或空间变化的物理量。系统是对信号进行处理的装置，可以是物理系统或抽象系统。信号与系统理论是通信原理的基础，为分析和设计通信系统提供了数学工具。",
                "",
                "### 2.1 信号的分类",
                "",
                "信号可以按照多种方式进行分类。按时间特性可分为连续时间信号和离散时间信号。连续时间信号在任意时刻都有定义，离散时间信号只在某些离散时刻有定义。按周期性可分为周期信号和非周期信号。周期信号满足f(t+T)=f(t)，其中T为周期。按能量特性可分为能量信号和功率信号。能量信号的能量有限，功率信号的功率有限。按确定性可分为确定性信号和随机信号。确定性信号的取值可以精确预测，随机信号的取值具有随机性。",
                "",
                "### 2.2 系统的特性",
                "",
                "系统具有多种重要特性。线性性是指系统满足叠加原理，即多个输入信号的线性组合的输出等于各输入信号单独作用时输出的线性组合。时不变性是指系统的特性不随时间变化，即输入信号延迟τ，输出信号也相应延迟τ。因果性是指系统的输出只依赖于当前和过去的输入，不依赖于未来的输入。稳定性是指有界输入产生有界输出。这些特性对于分析和设计通信系统具有重要意义。",
                "",
                "### 2.3 傅里叶变换",
                "",
                "傅里叶变换是信号分析的重要工具，它将时域信号转换为频域信号，揭示了信号的频率特性。连续时间信号的傅里叶变换定义为F(ω)=∫f(t)e^(-jωt)dt，离散时间信号的傅里叶变换定义为F(e^(jω))=Σf(n)e^(-jωn)。傅里叶变换具有线性性、时移性、频移性、卷积性等重要性质，在信号处理和通信系统分析中广泛应用。",
                "",
                "## 第三章 模拟调制",
                "",
                "模拟调制是将基带信号调制到载波上的过程，目的是使信号适合在信道中传输。调制可以改变信号的频率特性，提高信号的抗干扰能力，实现多路复用等。模拟调制主要包括幅度调制、频率调制和相位调制。",
                "",
                "### 3.1 幅度调制（AM）",
                "",
                "幅度调制是通过改变载波的幅度来传输信息。标准AM信号的表达式为s(t)=A[1+m(t)]cos(ωct)，其中A为载波幅度，m(t)为调制信号，ωc为载波角频率。AM信号的频谱包含载波分量和上下边带，带宽为调制信号最高频率的两倍。AM调制的优点是实现简单，缺点是功率效率低，因为大部分功率消耗在载波上。为了提高功率效率，可以采用抑制载波的双边带调制（DSB-SC）或单边带调制（SSB）。",
                "",
                "### 3.2 频率调制（FM）",
                "",
                "频率调制是通过改变载波的频率来传输信息。FM信号的瞬时频率与调制信号成正比，表达式为ω(t)=ωc+kfm(t)，其中kf为频率灵敏度。FM信号的频谱结构复杂，理论上带宽为无穷大，但实际应用中可以采用卡森公式估算带宽：B≈2(Δf+fm)，其中Δf为最大频偏，fm为调制信号的最高频率。FM调制的优点是抗干扰能力强，功率效率高，缺点是带宽较宽。FM广泛应用于调频广播、电视伴音等领域。",
                "",
                "### 3.3 相位调制（PM）",
                "",
                "相位调制是通过改变载波的相位来传输信息。PM信号的瞬时相位与调制信号成正比，表达式为φ(t)=ωct+kpm(t)，其中kp为相位灵敏度。PM和FM在数学上密切相关，PM信号的频率变化率与调制信号成正比，而FM信号的频率与调制信号成正比。PM调制的特性与FM类似，但实现方式不同。在实际应用中，PM常用于数字通信中的相移键控（PSK）调制。",
                "",
                "## 第四章 数字基带传输",
                "",
                "数字基带传输是数字信号在基带信道中的传输，是数字通信系统的基础。数字基带信号是未经调制的数字信号，其频谱从零频率开始。数字基带传输系统包括发送端、信道和接收端，主要涉及码型选择、功率谱分析、码间干扰等问题。",
                "",
                "### 4.1 数字基带信号的码型",
                "",
                "数字基带信号的码型选择对传输性能有重要影响。常用的码型包括单极性码、双极性码、归零码、非归零码等。单极性码用正电平表示1，零电平表示0，实现简单但存在直流分量。双极性码用正负电平表示1和0，无直流分量，抗干扰能力强。归零码在码元中间回到零电平，便于提取位同步信号。非归零码在整个码元期间保持电平不变，功率效率高。此外，还有曼彻斯特码、差分码等特殊码型，各有其应用场景。",
                "",
                "### 4.2 数字基带信号的功率谱",
                "",
                "数字基带信号的功率谱密度反映了信号的频域特性，对于信道设计和滤波器设计具有重要意义。随机数字基带信号的功率谱通常包含连续谱和离散谱两部分。连续谱由码元的波形决定，离散谱由码元的周期性决定。功率谱的形状影响信号的带宽需求，对于带宽受限的信道，需要选择功率谱集中的码型。",
                "",
                "### 4.3 码间干扰与奈奎斯特准则",
                "",
                "码间干扰是数字基带传输中的主要问题，由信道的非理想特性引起。当码元速率过高或信道带宽不足时，相邻码元的响应会相互重叠，导致码间干扰。奈奎斯特第一准则指出，如果系统的冲激响应满足h(nT)=1（n=0）和h(nT)=0（n≠0），则无码间干扰。奈奎斯特第二准则给出了无码间干扰的最小带宽要求：B≥Rs/2，其中Rs为码元速率。满足奈奎斯特准则的滤波器称为奈奎斯特滤波器，常用的有升余弦滚降滤波器。",
                "",
                "## 第五章 数字带通传输",
                "",
                "数字带通传输是将数字基带信号调制到载波上进行传输，使信号适合在带通信道中传输。数字调制技术是数字通信系统的核心技术，直接影响系统的性能和复杂度。数字调制主要包括振幅键控、频移键控和相移键控。",
                "",
                "### 5.1 二进制数字调制",
                "",
                "二进制数字调制是最基本的数字调制方式。二进制振幅键控（2ASK）用载波的有无表示0和1，实现简单但抗干扰能力弱。二进制频移键控（2FSK）用两个不同频率的载波表示0和1，抗干扰能力较强但带宽较宽。二进制相移键控（2PSK）用载波的相位表示0和1，功率效率高，抗干扰能力强，但存在相位模糊问题。二进制差分相移键控（2DPSK）通过相位差表示信息，解决了相位模糊问题，应用广泛。",
                "",
                "### 5.2 多进制数字调制",
                "",
                "多进制数字调制可以提高频带利用率，在相同的码元速率下传输更多的信息。M进制振幅键控（MASK）用M个不同的幅度表示M个符号，频带利用率高但抗干扰能力弱。M进制频移键控（MFSK）用M个不同频率的载波表示M个符号，抗干扰能力强但带宽很宽。M进制相移键控（MPSK）用M个不同的相位表示M个符号，在功率效率和频带利用率之间取得良好平衡，应用最广泛。正交振幅调制（QAM）同时利用幅度和相位两个维度，进一步提高了频带利用率，是现代数字通信系统的主流调制方式。",
                "",
                "### 5.3 数字调制的性能分析",
                "",
                "数字调制的性能主要用误码率来衡量。在加性高斯白噪声（AWGN）信道中，各种数字调制方式的误码率可以通过理论分析得到。2PSK的误码率最低，2FSK次之，2ASK最高。多进制调制的误码率随进制数M的增加而增加，但频带利用率提高。在实际应用中，需要根据信道条件和系统要求选择合适的调制方式。",
                "",
                "## 第六章 信源编码",
                "",
                "信源编码是为了提高传输效率而对信源输出进行的编码，目的是减少冗余，降低码率。信源编码分为无失真信源编码和限失真信源编码。无失真信源编码要求能够完全恢复原始信息，限失真信源编码允许一定的失真以换取更高的压缩比。",
                "",
                "### 6.1 无失真信源编码",
                "",
                "无失真信源编码的理论基础是香农第一定理，它指出信源的平均码长不能小于信源的熵。霍夫曼编码是一种最优的无失真信源编码方法，它根据符号出现的概率分配不同长度的码字，概率大的符号分配短码，概率小的符号分配长码，使得平均码长最小。算术编码是另一种高效的无失真编码方法，它将整个消息编码为一个实数，编码效率接近信源熵。LZ编码是一类基于字典的编码方法，通过查找已编码的字符串来压缩数据，广泛应用于文件压缩。",
                "",
                "### 6.2 限失真信源编码",
                "",
                "限失真信源编码的理论基础是香农第三定理，它给出了在给定失真度下的最小码率。量化是限失真编码的基本方法，它将连续的模拟信号转换为离散的数字信号。均匀量化实现简单但效率低，非均匀量化根据信号的概率分布设计量化间隔，效率更高。标量量化每次量化一个样本，矢量量化同时量化多个样本，可以进一步降低码率。变换编码通过正交变换将信号转换到变换域，利用变换系数的统计特性进行编码，广泛应用于图像和视频压缩。",
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
                "",
                "### 9.3 码分复用（CDM）",
                "",
                "码分复用是利用不同的码序列来区分不同的信号，在码域上分离。CDM系统为每个用户分配一个唯一的扩频码，发送端用扩频码对信号进行扩频，接收端用相同的扩频码进行解扩。CDM的优点是抗干扰能力强，可以实现软容量，支持异步传输。缺点是实现复杂，需要精确的功率控制。CDM广泛应用于CDMA移动通信系统。码分多址（CDMA）是CDM在多址通信中的应用，是3G移动通信系统的核心技术。",
                "",
                "## 第十章 通信网",
                "",
                "通信网是由多个通信节点和传输链路组成的网络，实现用户之间的信息交换。通信网的基本功能包括传输、交换、接入等。现代通信网包括电话网、数据网、移动通信网、互联网等，形成了覆盖全球的通信基础设施。",
                "",
                "### 10.1 通信网的基本结构",
                "",
                "通信网的基本结构包括星型、总线型、环型和网状型。星型结构以中心节点为核心，所有节点都与中心节点相连，优点是结构简单、易于管理，缺点是中心节点故障会导致全网瘫痪。总线型结构所有节点共享一条总线，优点是成本低、易于扩展，缺点是总线故障会影响所有节点。环型结构节点形成环形连接，优点是结构简单、易于实现，缺点是单点故障会导致环路中断。网状型结构节点之间有多条连接路径，优点是可靠性高、路由灵活，缺点是成本高、管理复杂。实际通信网通常采用混合结构，结合各种结构的优点。",
                "",
                "### 10.2 通信网的性能指标",
                "",
                "通信网的性能指标包括时延、吞吐量、可靠性等。时延是数据从源节点到目的节点所需的时间，包括传输时延、传播时延、处理时延和排队时延。吞吐量是网络在单位时间内成功传输的数据量，反映了网络的传输能力。可靠性是网络在故障情况下保持服务的能力，通常用可用性、故障恢复时间等指标来衡量。服务质量（QoS）是网络为不同业务提供不同质量保证的能力，包括带宽、时延、丢包率等参数。",
                "",
                "### 10.3 交换技术",
                "",
                "交换技术是通信网的核心技术，包括电路交换、报文交换和分组交换。电路交换在通信前建立专用通路，通信期间通路独占，优点是时延小、实时性好，缺点是资源利用率低。报文交换以报文为单位进行存储转发，优点是资源利用率高，缺点是时延大。分组交换将报文分割成固定长度的分组进行传输，结合了电路交换和报文交换的优点，是现代数据网的主流交换方式。ATM（异步传输模式）是一种面向连接的分组交换技术，结合了电路交换和分组交换的优点，广泛应用于宽带综合业务数字网。",
                "",
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                "",
                "**通信原理笔记总结**：",
                "",
                "本笔记涵盖了通信原理的核心内容，包括信号与系统基础、模拟调制、数字基带传输、数字带通传输、信源编码、信道编码、同步技术、多路复用和多址技术、通信网等主要章节。每个章节都包含了基本概念、原理分析、性能评估和应用实例，为深入理解现代通信系统提供了理论基础。",
                "",
                "通信原理是电子信息工程、通信工程等专业的重要基础课程，掌握这些知识对于从事通信系统设计、网络规划、信号处理等工作具有重要意义。随着5G、6G等新一代通信技术的发展，通信原理的知识也在不断更新和扩展，需要持续学习和实践。"
            ]
            self.documents["通信原理笔记"] = communication_content
            await self.storage.save_document("通信原理笔记", communication_content, "trial", self.session_id)
            print(f"[D1DocumentManager] 通信原理笔记已创建并保存（内容长度: {len(' '.join(communication_content))} 字符）")
        
        # 打印最终文档列表
        print(f"[D1DocumentManager] 初始化完成，文档列表: {list(self.documents.keys())}")
        
        # 确保活跃文档存在
        if self.active_doc_title not in self.documents and self.documents:
            self.active_doc_title = list(self.documents.keys())[0]
            await self.storage.save_metadata({"active_doc_title": self.active_doc_title}, self.doc_type)
        
        self._initialized = True
    
    async def check_dev_mode(self, session_id: str = None) -> bool:
        """检查开发者模式状态"""
        if not session_id:
            session_id = self.session_id
        return await self.storage.check_dev_mode(session_id)
    
    async def enable_dev_mode(self, session_id: str = None) -> bool:
        """启用开发者模式"""
        if not session_id:
            session_id = self.session_id
        result = await self.storage.enable_dev_mode(session_id)
        if result:
            self.dev_mode_enabled = True
        return result
    
    def enable_edit_mode(self) -> bool:
        """启用修改模式（set000）"""
        if not self.dev_mode_enabled:
            raise PermissionError("需要先启用开发者模式")
        self.edit_mode_enabled = True
        return True
    
    async def enable_edit_mode_async(self, session_id: str = None) -> bool:
        """异步启用修改模式"""
        if not session_id:
            session_id = self.session_id
        if not self.dev_mode_enabled:
            raise PermissionError("需要先启用开发者模式")
        result = await self.storage.enable_edit_mode(session_id)
        if result:
            self.edit_mode_enabled = True
        return result
    
    def get_document_titles(self):
        """获取所有文档标题"""
        return list(self.documents.keys())
    
    def get_document(self, title):
        """获取指定标题的文档内容"""
        return self.documents.get(title)
    
    async def set_active_document(self, title):
        """设置当前活跃文档"""
        if title in self.documents:
            self.active_doc_title = title
            await self.storage.save_metadata({"active_doc_title": title}, self.doc_type)
            return True
        return False
    
    async def add_content(self, title, content, position="end"):
        """
        添加内容到文档
        支持定位到文档标题、开头、结尾。
        """
        # 试用模式不需要开发者模式和修改权限
        if self.doc_type == "dev":
            if not self.dev_mode_enabled:
                raise PermissionError("需要启用开发者模式才能修改文档")
            
            if not self.edit_mode_enabled:
                raise PermissionError("需要输入 'set000' 启用修改权限才能修改笔记")
            
            # 检查是否是介绍文档（开发者模式）或PM问答笔记（试用模式）或更新记录日志（只读）
            if title == self.intro_doc_title:
                doc_name = "介绍文档" if self.doc_type == "dev" else "PM问答笔记"
                raise PermissionError(f"{doc_name}为只读文档，不可修改")
            if title == self.update_log_title:
                raise PermissionError(f"文档 '{self.update_log_title}' 是只读的，不允许修改。")
        
        if title not in self.documents:
            self.documents[title] = []
            print(f"[系统] 文档 '{title}' 不存在，已为您创建。")
        
        doc = self.documents[title]
        
        # 处理内容：如果包含换行符，按行分割添加到文档
        content_lines = content.split('\n') if '\n' in content else [content]
        # 过滤掉空行（保留内容的原始格式，但去掉首尾空行）
        while content_lines and not content_lines[0].strip():
            content_lines.pop(0)
        while content_lines and not content_lines[-1].strip():
            content_lines.pop()
        
        # 处理position为None或非字符串的情况，默认为"end"
        if position is None:
            position_str = "end"
        elif not isinstance(position, str):
            try:
                position_str = str(position) if position else "end"
            except:
                position_str = "end"
        elif position == "":
            position_str = "end"
        else:
            position_str = position
        
        # 转换为小写
        try:
            position = position_str.lower()
        except (AttributeError, TypeError):
            position = "end"
        
        # 简化定位逻辑：只处理 start/end，其他视为 end
        if position == "start":
            # 插入到开头
            for line in reversed(content_lines):
                doc.insert(0, line)
            pos_desc = "开头"
        elif position == "end":
            # 追加到结尾
            for line in content_lines:
                doc.append(line)
            pos_desc = "结尾"
        else:
            # 尝试按内容定位
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
        
        # 保存到数据库
        await self.storage.save_document(title, doc, self.doc_type, self.session_id)
        
        print(f"[系统] 内容已成功添加到文档 '{title}' 的 {pos_desc}。")
        return True
    
    async def clear_document(self, title):
        """清空文档的所有内容"""
        # 试用模式不需要开发者模式和修改权限
        if self.doc_type == "dev":
            if not self.dev_mode_enabled:
                raise PermissionError("需要启用开发者模式才能修改文档")
            
            if not self.edit_mode_enabled:
                raise PermissionError("需要输入 'set000' 启用修改权限才能修改笔记")
            
            # 检查是否是介绍文档（开发者模式）或PM问答笔记（试用模式）或更新记录日志（只读）
            if title == self.intro_doc_title:
                doc_name = "介绍文档" if self.doc_type == "dev" else "PM问答笔记"
                raise PermissionError(f"{doc_name}为只读文档，不可修改")
            if title == self.update_log_title:
                raise PermissionError(f"文档 '{self.update_log_title}' 是只读的，不允许修改。")
        
        if title not in self.documents:
            print(f"[系统] 文档 '{title}' 不存在。")
            return False
        
        self.documents[title] = []
        await self.storage.save_document(title, [], self.doc_type, self.session_id)
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
    
    async def clear_trial_data(self):
        """清空试用数据（退出时调用）"""
        if self.doc_type == "trial" and self.session_id:
            await self.storage.clear_trial_documents(self.session_id)
            self.documents = {}

