#import "report-theme.typ": report-theme

#show: report-theme.with(
  title: "刘莫昕｜智能硬件项目经理",
  author: "刘莫昕",
  rhythm: "report",
  body-size: 9.35pt,
  running-header: false,
)

#set page(
  paper: "a4",
  margin: (top: 1.05cm, bottom: 1.0cm, x: 1.25cm),
  numbering: none,
  header: none,
  footer: none,
)
#set text(font: ("Noto Sans CJK SC", "Noto Sans"), size: 9.35pt, fill: rgb("#1b2330"))
#set par(justify: false, leading: 0.76em, spacing: 0.36em)
#set heading(numbering: none)
#show link: set text(fill: rgb("#0057d9"))

#let blue = rgb("#0057d9")
#let navy = rgb("#101d35")
#let muted = rgb("#5b677a")
#let pale = rgb("#eef4ff")
#let rule = rgb("#ccd7e8")

#let section(title) = {
  v(0.86em)
  grid(
    columns: (auto, 1fr),
    column-gutter: 9pt,
    align: horizon,
    text(size: 11.2pt, weight: 700, fill: navy, title),
    line(length: 100%, stroke: 0.75pt + blue),
  )
  v(0.5em)
}

#let role-head(company, role, period) = {
  grid(
    columns: (1fr, auto),
    column-gutter: 10pt,
    [#text(weight: 700, size: 10.2pt, fill: navy)[#company] #h(0.5em) #text(weight: 600, fill: blue)[#role]],
    align(right)[#text(size: 8.8pt, weight: 600, fill: muted)[#period]],
  )
}

#let tags(items) = {
  for item in items {
    box(
      inset: (x: 6pt, y: 3pt),
      radius: 2pt,
      fill: pale,
      stroke: 0.4pt + rgb("#cfe0ff"),
      text(size: 8.2pt, weight: 600, fill: blue, item),
    )
    h(4pt)
  }
}

#let compact-list(..items) = list(
  ..items,
  tight: true,
  marker: [#text(fill: blue, weight: 700)[•]],
  indent: 10pt,
  body-indent: 5pt,
  spacing: 3.25pt,
)

#let experience-list(..items) = list(
  ..items,
  tight: true,
  marker: [#text(fill: blue, weight: 700)[•]],
  indent: 10pt,
  body-indent: 5pt,
  spacing: 5.6pt,
)

#let metric(value, label) = rect(
  width: 100%,
  inset: (x: 7pt, y: 6pt),
  radius: 2pt,
  fill: pale,
  stroke: 0.45pt + rule,
)[
  #text(size: 12.5pt, weight: 800, fill: blue)[#value]
  #linebreak()
  #text(size: 7.8pt, weight: 600, fill: muted)[#label]
]

#let product-card(title, detail) = rect(
  width: 100%,
  height: 2.05cm,
  inset: (x: 8pt, y: 7pt),
  radius: 3pt,
  fill: pale,
  stroke: 0.45pt + rule,
)[
  #text(size: 9pt, weight: 700, fill: navy)[#title]
  #v(0.25em)
  #text(size: 7.4pt, fill: muted)[#detail]
]

#grid(
  columns: (2.15cm, 1fr, auto),
  column-gutter: 12pt,
  align: center,
  [
    #image("assets/profile.webp", width: 2.15cm, height: 2.75cm, fit: "cover")
  ],
  [
    #link("https://mindscribe-app.pages.dev/")[#text(size: 23pt, weight: 800, fill: navy)[刘莫昕]]
    #v(0.2em)
    #text(size: 13pt, weight: 700, fill: blue)[智能硬件项目经理]
    #v(0.24em)
    #text(size: 8.8pt, weight: 600, fill: muted)[SMART HARDWARE PROJECT MANAGER]
  ],
  align(right)[
    #link("https://mindscribe-app.pages.dev/")[#image("assets/mindscribe-brand.png", width: 1.05cm)]
    #linebreak()
    #text(size: 7.4pt, weight: 700, fill: navy)[灵辑 · MindScribe]
    #linebreak()
    #text(size: 8.8pt, fill: navy)[杭州 · 159 9446 1673]
    #linebreak()
    #link("mailto:scretliasion@163.com")[#text("scretliasion@163.com")]
    #linebreak()
    #link("https://mindscribe-app.pages.dev/")[#text(size: 8.3pt)[作品集：mindscribe-app.pages.dev]]
    #linebreak()
    #text(size: 8.3pt, fill: muted)[英语可作为工作语言]
  ],
)

#v(0.65em)
#rect(
  width: 100%,
  inset: (x: 10pt, y: 8pt),
  radius: 3pt,
  fill: pale,
  stroke: (left: 2.2pt + blue),
)[
  #text(weight: 700, fill: navy)[职业概述] #h(0.45em)
  具备门禁机、家用门锁、玻璃门锁及房车锁多产品线全生命周期管理经验，覆盖产品定义、研发跟进、测试验证、认证合规、供应商协同、试产量产与售后闭环。硕士阶段接受全英文教学，英语可作为工作语言；具备独立对接尼泊尔等海外客户的需求澄清与项目沟通经验。能够在软硬件、结构、固件、云平台与供应链之间建立共同语言，以里程碑、风险清单和问题闭环推动智能硬件产品稳定交付。
]

#section([核心能力])
#tags(("全生命周期管理", "研发与供应商协同", "软硬件联调", "测试验证", "认证合规", "试产与量产", "客诉闭环", "英语项目沟通"))

#section([工作经历])
#role-head([得力集团], [智能硬件项目经理], [2026.03 — 至今])
#v(0.22em)
#text(size: 8.9pt, fill: muted)[负责门禁机、家用门锁、玻璃门锁与房车锁产品线，统筹自研整机与 OEM 项目的研发、测试、标准化、交付和售后。]
#v(0.28em)
#experience-list(
  [并行推进 2.4 英寸、5 英寸、7 英寸门禁机及多款 OEM 机型；完成 AL912C、AC213、AC205C 三款 2.4 英寸门禁机的研发、测试与试产，按计划于 2026 年 8 月上市。],
  [统筹 5 英寸防水门禁机 AC516/AL962C 的型式测试、硬件可靠性验证、首轮功能测试及包材设计；针对掌静脉识别与物料交期问题组织复测、分析与风险复盘。],
  [负责 AC22 人脸家用门锁新国标适配，对比检测机构方案并推进认证；同步完成 DL-AC27 等存量机型的标准差异梳理、参数与资料迭代，降低新旧国标切换风险。],
  [全流程推进房车锁项目，覆盖专利风险排查、供应商寻源、价格核定、试产验证与量产驻场；推动供应商解决低温锁舌失效问题，实现样机在 -30℃ 场景下正常动作。],
  [接手门禁与锁具售后台账后，完成 10 条历史问题中的 5 条闭环；围绕继电器虚焊、指纹识别、结构异响、门铃无响应等问题组织根因分析、固件验证、修模与效果确认。],
  [针对 AC512 门铃无响应问题拆解电路原理与典型错误接线场景，输出专项失效分析材料，为售后判定和现场整改建立标准依据。],
  [推动全系门禁机参数、操作说明和技术规范对齐，补充操作视频二维码；协同售后团队明确岗位边界、问题流转与结案标准，提升跨部门处置效率。],
  [独立对接尼泊尔、巴基斯坦及其他海外区域客户，完成定制需求澄清、技术方案同步与项目进度沟通。],
)

#v(0.5em)
#rect(width: 100%, inset: (x: 9pt, y: 7pt), radius: 3pt, fill: navy)[
  #grid(
    columns: (auto, 1fr),
    column-gutter: 12pt,
    [#text(size: 8.2pt, weight: 700, fill: white)[交付方法]],
    [#text(size: 8.2pt, fill: rgb("#dce6f7"))[里程碑拆解 → 风险清单 → 责任人 → 验证标准 → 闭环复盘]],
  )
]

#v(0.44em)
#role-head([广西诺特广电有限公司], [热融合设备实习项目经理], [2024.06 — 2024.09])
#v(0.18em)
#compact-list(
  [协调设计团队与工厂资源，参与产品开发全周期，推动 3 款新品由设计阶段进入试产。],
)

#v(0.85em)
#grid(
  columns: (1fr, 1fr, 1fr, 1fr),
  column-gutter: 6pt,
  product-card([门禁终端], [2.4 / 5 / 7 英寸与 OEM]),
  product-card([家用门锁], [整机交付与合规适配]),
  product-card([玻璃门锁], [识别、交互与项目协同]),
  product-card([房车锁], [结构、试产与量产跟进]),
)
#v(0.58em)
#rect(width: 100%, inset: (x: 10pt, y: 8pt), radius: 3pt, fill: navy)[
  #grid(
    columns: (auto, 1fr),
    column-gutter: 12pt,
    [#text(size: 8.1pt, weight: 700, fill: rgb("#8bb0ff"))[项目交付链路]],
    [#text(size: 8.1pt, fill: white)[产品定义 → 研发协同 → 测试认证 → 供应链 → 试产量产 → 售后闭环]],
  )
]
#v(0.62em)
#line(length: 100%, stroke: 0.55pt + rule)
#v(0.32em)
#align(center)[#text(size: 7.7pt, fill: muted)[求职方向：智能硬件项目经理｜产品项目经理｜智能门禁 / IoT / 机器人与自动化相关方向]]

#pagebreak()

#grid(
  columns: (auto, 1fr, auto),
  column-gutter: 12pt,
  align: center,
  [#link("https://mindscribe-app.pages.dev/")[#image("assets/mindscribe-brand.png", width: 0.78cm)]],
  [#text(size: 14pt, weight: 800, fill: navy)[刘莫昕] #h(0.5em) #text(size: 9.4pt, weight: 700, fill: blue)[智能硬件项目经理]],
  align(right)[#text(size: 8.4pt, fill: muted)[159 9446 1673 · #text("scretliasion@163.com")]],
)

#v(0.55em)
#grid(
  columns: (1fr, 1fr, 1fr),
  column-gutter: 6pt,
  metric([3 款], [2.4 英寸门禁机如期上市]),
  metric([5 / 10], [历史客诉完成闭环]),
  metric([-30℃], [房车锁低温验证通过]),
)

#section([代表项目与业务成果])
#text(weight: 700, fill: navy)[01｜门禁机多型号上市与 OEM 交付]
#v(0.12em)
#text(size: 8.9pt, fill: muted)[AL912C / AC213 / AC205C / AC516 / AL962C / AC611 / AC711 / AC612 / AC615]
#v(0.18em)
从项目策划、协议与功能测试、可靠性验证到试产和入库，拆解关键节点并组织研发、品质、采购、供应商及生产协同；既管理自研整机，也能处理 OEM 固件兼容、资料对齐与交付风险。

#v(0.45em)
#text(weight: 700, fill: navy)[02｜智能门锁新国标切换]
#v(0.12em)
围绕 GB 21556.2-2025 切换窗口，推进 AC22 新品认证与 AC10、AC21、AC310、DL-AC27 等在售产品升级；完成检测方案比较、测试不符合项整改、标准差异核对与资料更新，兼顾新品上市和存量产品合规。

#v(0.45em)
#text(weight: 700, fill: navy)[03｜品质问题与客诉闭环]
#v(0.12em)
建立问题台账，按“现象复现—影响评估—软硬件定位—责任与方案—验证结案”推进闭环；覆盖主板虚焊、固件异常、识别效果、结构缺陷、电源适配和现场接线等典型问题，并沉淀面向新问题的五维复盘方法。

#section([教育背景])
#role-head([浙江工商大学萨塞克斯人工智能学院], [机器人与自动化系统（全英文授课）｜硕士], [])
#v(0.12em)
#text(size: 8.9pt, fill: muted)[机器学习与深度学习、计算机视觉、运动规划与控制、嵌入式人工智能、三维建模与力学仿真]
#v(0.38em)
#role-head([浙江工商大学], [电子信息专业｜本科], [])
#v(0.12em)
#text(size: 8.9pt, fill: muted)[电路分析、数字/模拟电子技术、单片机综合、信号与系统、EDA 技术]

#section([工程与研究项目])
#compact-list(
  [*高铁 5G 波束与资源协同：* 团队构建覆盖平原、山地、隧道与高架桥的通信仿真平台，以 PPO 与 Q-learning 协同处理连续波束/功率和离散切换决策；报告仿真中直线轨道切换成功率由 92.8% 提升至 97.4%。],
  [*无人机蜂窝覆盖盲点搜索：* 设计航迹规划、信道模型与信号可视化三模块仿真系统；在城市、工厂、村落模拟场景中，内螺旋航迹较往复式航迹的模拟用时减少约 28.92%—33.33%。],
  [*糖豆智能分拣原型：* 使用 Arduino UNO、TCS34725 与双舵机构建低成本颜色分拣装置；报告记录加速测试 3 分钟分拣 76 颗，准确率 97.4%，并完成阈值、时序与防粘改进。],
  [*机器人与自主导航项目：* 基于云深处四足机器人平台集成 ROS Navigation、Cartographer 与 RViz，完成实时建图、传感器可视化和多点导航演示；同时参与五杆平面并联机器人与直流电机控制项目。],
)

#section([工具、语言与专业能力])
#grid(
  columns: (8.5em, 1fr),
  row-gutter: 3.5pt,
  column-gutter: 8pt,
  text(weight: 700, fill: navy)[项目管理], [里程碑拆解、风险识别、跨部门协同、供应商管理、测试验证、试产/量产、客诉闭环],
  text(weight: 700, fill: navy)[智能硬件], [门禁整机、门锁与电控锁、固件与协议、局域网/云平台基础、硬件失效分析、结构与装配],
  text(weight: 700, fill: navy)[工具与开发], [SolidWorks、MATLAB/Simulink、Python、Altium Designer、LabVIEW、C++、TensorFlow/PyTorch],
  text(weight: 700, fill: navy)[语言能力], [CET-6 519｜CET-4 520｜IELTS 6.0｜可进行英文需求澄清、技术沟通与项目协同],
  text(weight: 700, fill: navy)[长期习惯], [坚持每日跑步约 4 km，风雨无阻；2025—2026 年跑步记录累计超过 1,600 km。],
)

#v(0.72em)
#link("https://mindscribe-app.pages.dev/")[
  #rect(width: 100%, inset: (x: 10pt, y: 8pt), radius: 3pt, fill: navy)[
    #grid(
      columns: (1fr, auto),
      [#text(size: 8.4pt, weight: 700, fill: white)[查看完整产品实拍、项目视频与双语履历]],
      [#text(size: 8.4pt, weight: 700, fill: rgb("#8bb0ff"))[mindscribe-app.pages.dev →]],
    )
  ]
]

#v(0.75em)
#line(length: 100%, stroke: 0.6pt + rule)
#v(0.4em)
#align(center)[#text(size: 8.1pt, fill: muted)[求职方向：智能硬件项目经理｜产品项目经理｜智能门禁 / IoT / 机器人与自动化相关方向]]
