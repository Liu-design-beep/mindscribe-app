import {
  ArrowDown,
  ArrowRight,
  BriefcaseBusiness,
  Check,
  CirclePlay,
  Download,
  ExternalLink,
  Footprints,
  Globe2,
  GraduationCap,
  Languages,
  Mail,
  MapPin,
  Menu,
  Phone,
  Rocket,
  ShieldCheck,
  Sparkles,
  Target,
  Users,
  X,
} from "lucide-react";
import { useEffect, useMemo, useRef, useState, type ReactNode } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

type Lang = "zh" | "en";
type Category = "all" | "ai" | "embedded" | "control" | "structure";
type Localized = { zh: string; en: string };

type Project = {
  id: string;
  category: Exclude<Category, "all">;
  index: string;
  title: Localized;
  eyebrow: Localized;
  summary: Localized;
  role: Localized;
  image: string;
  video?: string;
  tags: string[];
  methods: Localized[];
  highlights: Localized[];
  featured?: boolean;
};

const ASSETS = {
  brand: "/manus-storage/mindscribe-brand_4da2eb81.png",
  loading: "/manus-storage/mindscribe-loading_5ed0f15f.png",
  campus: "/manus-storage/campus-presentation_b4574c22.webp",
  profile: "/manus-storage/profile_9688b303.webp",
  solidworks: "/manus-storage/solidworks_4aba9a16.webp",
  control: "/manus-storage/control_f383f8c3.webp",
  beam: "/manus-storage/beam_b9a81eb8.webp",
  candy: "/manus-storage/candy_e667b99d.webp",
  drone: "/manus-storage/drone_ea894fc2.webp",
  robotPoster: "/manus-storage/robot-poster_f6627ea5.jpg",
  robotVideo: "/manus-storage/robot-demo_a6e921cd.mp4",
  salvagePoster: "/manus-storage/salvage-poster_5b11f045.jpg",
  salvageVideo: "/manus-storage/salvage-demo_09b153ed.mp4",
  resumeZh: "/manus-storage/Moxin-Liu-Smart-Hardware-PM-CN-20260908-v4_3ded8d47.pdf",
  resumeEn: "/manus-storage/Moxin-Liu-Smart-Hardware-PM-EN-20260908-v4_8731054f.pdf",
  runningPhoto: "/manus-storage/running-photo_4fa2df38.webp",
  runningStats: "/manus-storage/running-stats_eef52e4b.webp",
  runningRecent: "/manus-storage/running-recent_3a31dbde.webp",
  access24: "/manus-storage/access-terminal-24_a91f6fad.webp",
  access5: "/manus-storage/access-terminal-5_4a716c60.webp",
  access7: "/manus-storage/access-terminal-7_eef7ddf5.webp",
  accessOem: "/manus-storage/access-terminal-oem_44612c23.webp",
  homeLock1: "/manus-storage/home-lock-01_5dd5c375.webp",
  homeLock2: "/manus-storage/home-lock-02_97790b70.webp",
  glassLock1: "/manus-storage/glass-lock-01_8567f1dc.webp",
  glassLock2: "/manus-storage/glass-lock-02_a4635eb2.webp",
  rvPilot: "/manus-storage/rv-lock-pilot_aeb4d131.webp",
  rvMechanism: "/manus-storage/rv-lock-mechanism_647bf533.webp",
  rvStructure: "/manus-storage/rv-lock-structure_4c825523.webp",
  workAccessTest: "/manus-storage/work-access-test_760f3bc5.webp",
  readerPackaged: "/manus-storage/reader-packaged_6be97ff6.webp",
  workIssueTriage: "/manus-storage/work-issue-triage_040fb2e4.webp",
  readerModel1: "/manus-storage/reader-model-01_b71d307b.webp",
  readerModel2: "/manus-storage/reader-model-02_1ea45829.webp",
  cloudDeepPoster: "/manus-storage/cloud-deep-poster-final_ba85b39e.jpg",
  cloudDeepVideo: "/manus-storage/cloud-deep-demo_17aee7d6.mp4",
};

const projects: Project[] = [
  {
    id: "beam",
    category: "ai",
    index: "01",
    featured: true,
    title: { zh: "高铁 5G 波束与资源协同", en: "5G Beam & Resource Coordination for HSR" },
    eyebrow: { zh: "强化学习 · 无线通信", en: "Reinforcement Learning · Wireless" },
    summary: {
      zh: "面向高铁复杂地形下的切换、遮挡与多普勒问题，团队构建在线—离线混合强化学习框架与四场景仿真平台。",
      en: "A hybrid online–offline reinforcement learning framework and four-scenario simulation platform for handover, blockage, and Doppler challenges in high-speed railway communications.",
    },
    role: {
      zh: "团队研究项目；报告署名刘莫昕、王雷，具体个人分工未在文档中拆分。",
      en: "Team research project authored by Moxin Liu and Lei Wang; individual workstreams were not separately documented.",
    },
    image: ASSETS.beam,
    tags: ["PPO", "Q-learning", "5G", "POMDP", "Simulation"],
    methods: [
      { zh: "以 51 维状态与 21 维动作空间建立 POMDP", en: "Modelled the problem as a POMDP with 51-dimensional state and 21-dimensional action spaces" },
      { zh: "以 PPO 处理连续波束/功率，以 Q-learning 辅助离散切换", en: "Combined PPO for continuous beam/power actions with Q-learning for discrete handovers" },
      { zh: "构建平原、山地、隧道、高架桥四类仿真场景", en: "Built simulation scenarios for plains, mountains, tunnels, and viaducts" },
    ],
    highlights: [
      { zh: "报告仿真中，直线轨道切换成功率由 92.8% 提升至 97.4%", en: "The report records straight-track handover success improving from 92.8% to 97.4%" },
      { zh: "高架桥场景断链率由 5.3% 降至 0.2%", en: "Reported viaduct disconnection rate decreased from 5.3% to 0.2%" },
    ],
  },
  {
    id: "drone",
    category: "ai",
    index: "02",
    title: { zh: "无人机蜂窝覆盖盲点搜索", en: "UAV Cellular Coverage Blind-Spot Search" },
    eyebrow: { zh: "航迹规划 · 信号可视化", en: "Path Planning · Signal Visualisation" },
    summary: {
      zh: "以航迹规划、信道模型与信号可视化三模块搭建无人机路测仿真系统，在多类模拟环境中比较覆盖航迹。",
      en: "A UAV road-testing simulation spanning path planning, channel modelling, and signal visualisation across multiple environments.",
    },
    role: {
      zh: "文档以“笔者”自述完成方案、仿真与结果分析，协作边界未单独说明。",
      en: "The report attributes system design, simulation, and analysis to the author; collaboration boundaries were not separately stated.",
    },
    image: ASSETS.drone,
    tags: ["UAV", "Python", "NumPy", "Path Planning", "Heatmap"],
    methods: [
      { zh: "设计预映射避障、内螺旋与往复式三类覆盖航迹", en: "Designed pre-mapped avoidance, inward-spiral, and reciprocating coverage paths" },
      { zh: "区分 LoS/NLoS 链路并模拟路径损耗与衰落", en: "Separated LoS/NLoS links and modelled path loss and fading" },
      { zh: "将模拟信号强度映射为二维热力图", en: "Mapped simulated signal strength into 2D heatmaps" },
    ],
    highlights: [
      { zh: "三类模拟场景中，内螺旋航迹用时减少约 28.92%—33.33%", en: "Inward-spiral paths reduced simulated mission time by approximately 28.92%–33.33%" },
      { zh: "模拟飞行距离减少约 24.65%—35.12%", en: "Simulated flight distance was reduced by approximately 24.65%–35.12%" },
    ],
  },
  {
    id: "cloud-deep",
    category: "control",
    index: "03",
    title: { zh: "云深处四足机器人自主导航", en: "DEEP Robotics Quadruped Autonomous Navigation" },
    eyebrow: { zh: "ROS Navigation · SLAM 建图", en: "ROS Navigation · SLAM Mapping" },
    summary: {
      zh: "在校工程项目：基于云深处四足机器人平台集成 ROS Navigation、Cartographer 与 RViz，完成实时建图、传感器可视化和多点导航系统演示。",
      en: "Academic engineering project integrating ROS Navigation, Cartographer, and RViz on a DEEP Robotics quadruped platform for real-time mapping, sensor visualisation, and multi-point navigation.",
    },
    role: {
      zh: "在校系统集成项目；提供资料未进一步拆分个人负责模块。",
      en: "Academic system-integration project; individual module ownership was not further separated in the provided material.",
    },
    image: ASSETS.cloudDeepPoster,
    video: ASSETS.cloudDeepVideo,
    tags: ["ROS", "Cartographer", "RViz", "LiDAR", "SLAM"],
    methods: [
      { zh: "基于 ROS Navigation 框架组织自主导航链路", en: "Structured the autonomous-navigation stack around ROS Navigation" },
      { zh: "使用 Cartographer 进行实时环境建图", en: "Used Cartographer for real-time environment mapping" },
      { zh: "在 RViz 中可视化 LiDAR、局部代价地图与全局地图", en: "Visualised LiDAR, local cost maps, and global maps in RViz" },
    ],
    highlights: [
      { zh: "视频同时展示 RViz 动态建图与四足机器人行走测试", en: "Video shows both live RViz mapping and quadruped walking tests" },
      { zh: "形成传感器采集—建图导航—机器人本体运动的联调闭环", en: "Demonstrated a sensor-to-mapping-to-robot-motion integration loop" },
    ],
  },
  {
    id: "robot",
    category: "control",
    index: "04",
    title: { zh: "五杆平面并联机器人", en: "Five-Bar Planar Parallel Robot" },
    eyebrow: { zh: "视觉识别 · 运动控制", en: "Computer Vision · Motion Control" },
    summary: {
      zh: "围绕鸡蛋自动拾取，完成五杆平面并联机构设计、正逆运动学仿真，并串联 OpenCV、Arduino 与真空吸取执行链路。",
      en: "A five-bar planar robot concept for automated egg picking, integrating kinematics, OpenCV detection, Arduino control, and vacuum actuation.",
    },
    role: {
      zh: "团队项目；文档未单独记录个人负责模块。",
      en: "Team project; individual module ownership was not separately documented.",
    },
    image: ASSETS.robotPoster,
    video: ASSETS.robotVideo,
    tags: ["OpenCV", "Arduino", "MATLAB", "Kinematics", "CAD"],
    methods: [
      { zh: "推导正逆运动学并完成圆形、方形轨迹仿真", en: "Derived forward/inverse kinematics and simulated circular and square trajectories" },
      { zh: "建立相机、识别、坐标映射、串口与执行器控制链路", en: "Connected camera input, detection, coordinate mapping, serial communication, and actuation" },
      { zh: "整理 CAD 模型、工程图与 BOM", en: "Prepared CAD models, engineering drawings, and BOM documentation" },
    ],
    highlights: [
      { zh: "形成从目标检测到抓取放置的完整系统方案", en: "Formed an end-to-end concept from target detection to pick-and-place" },
      { zh: "视频展示 OpenCV 对托盘目标的实时检测过程", en: "Video demonstrates real-time OpenCV detection of tray targets" },
    ],
  },
  {
    id: "salvage",
    category: "embedded",
    index: "05",
    title: { zh: "智能水面打捞船原型", en: "Smart Surface Salvage Boat Prototype" },
    eyebrow: { zh: "嵌入式 · 多传感器协同", en: "Embedded · Multi-sensor Integration" },
    summary: {
      zh: "基于 Arduino UNO 整合舵机、超声波、温湿度、摇杆、灯光与蜂鸣器，并通过 ESP8266 提供网络控制。",
      en: "An Arduino UNO prototype integrating servos, ultrasonic ranging, temperature/humidity sensing, joystick input, indicators, and ESP8266 control.",
    },
    role: {
      zh: "Group 10 团队项目；指定文件未拆分个人分工。",
      en: "Group 10 team project; individual responsibilities were not separated in the provided files.",
    },
    image: ASSETS.salvagePoster,
    video: ASSETS.salvageVideo,
    tags: ["Arduino", "ESP8266", "Sensors", "Servo", "HTTP"],
    methods: [
      { zh: "以分时循环与独立时间戳协调自动、手动及网络控制", en: "Coordinated automatic, manual, and network control with non-blocking timing" },
      { zh: "加入测距滤波、超时保护与异常告警", en: "Added distance filtering, timeout protection, and exception alerts" },
      { zh: "将障碍与环境检测联动到舵机暂停、蜂鸣器和 RGB 状态", en: "Linked obstacle/environment detection to servo pause, buzzer, and RGB status" },
    ],
    highlights: [
      { zh: "实物视频可见船体、超声波模块与控制接线集成", en: "Prototype video shows the hull, ultrasonic module, and integrated wiring" },
      { zh: "控制逻辑模块化，降低多模块功能耦合", en: "Modular control logic reduced coupling across hardware functions" },
    ],
  },
  {
    id: "candy",
    category: "embedded",
    index: "06",
    title: { zh: "糖豆智能分拣装置", en: "Candy Colour-Sorting System" },
    eyebrow: { zh: "颜色识别 · 原型验证", en: "Colour Sensing · Prototype Validation" },
    summary: {
      zh: "使用 Arduino UNO、TCS34725 颜色传感器与双舵机构建低成本分拣装置，并围绕阈值、时序和防粘持续改进。",
      en: "A low-cost sorter using Arduino UNO, a TCS34725 colour sensor, and dual servos, iterated through threshold, timing, and anti-sticking improvements.",
    },
    role: {
      zh: "报告署名刘莫昕；团队协作边界未单独说明。",
      en: "Report authored by Moxin Liu; team collaboration boundaries were not separately stated.",
    },
    image: ASSETS.candy,
    tags: ["Arduino", "TCS34725", "I2C", "PWM", "Prototype"],
    methods: [
      { zh: "多轮实验校准 RGB 阈值并设置遮光结构", en: "Calibrated RGB thresholds through repeated trials and added light shielding" },
      { zh: "双舵机协同完成送料、导流与复位", en: "Coordinated dual servos for feeding, routing, and reset" },
      { zh: "识别斜坡粘滞原因并测试食品级润滑改进", en: "Diagnosed ramp sticking and tested a food-grade lubrication improvement" },
    ],
    highlights: [
      { zh: "报告记录 3 分钟分拣 76 颗，准确率 97.4%", en: "The report records 76 pieces sorted in three minutes at 97.4% accuracy" },
      { zh: "实际成本记录为 293.2 元", en: "Recorded prototype cost: RMB 293.2" },
    ],
  },
  {
    id: "control",
    category: "control",
    index: "07",
    title: { zh: "直流电机速度控制", en: "DC Motor Speed Control" },
    eyebrow: { zh: "建模 · 控制性能分析", en: "Modelling · Control Analysis" },
    summary: {
      zh: "依据电气与机械方程建立直流电机传递函数，并在 MATLAB/Simulink 中比较 P、PI、PID 控制表现。",
      en: "Modelled a DC motor from electrical and mechanical equations and compared P, PI, and PID responses in MATLAB/Simulink.",
    },
    role: {
      zh: "课程项目报告署名 Moxin Liu（Candidate No. 299102）。",
      en: "Course project report authored by Moxin Liu (Candidate No. 299102).",
    },
    image: ASSETS.control,
    tags: ["MATLAB", "Simulink", "PID", "Bode", "State Space"],
    methods: [
      { zh: "建立传递函数、闭环模型与状态空间表达", en: "Built transfer-function, closed-loop, and state-space models" },
      { zh: "以调节时间、超调量与稳态误差比较控制器", en: "Compared controllers using settling time, overshoot, and steady-state error" },
      { zh: "使用 Routh 表与 Bode 图分析稳定性", en: "Analysed stability using a Routh table and Bode plots" },
    ],
    highlights: [
      { zh: "报告中的 PID 案例调节时间 0.08445 s，超调 3.974%", en: "The reported PID case achieved 0.08445 s settling time with 3.974% overshoot" },
      { zh: "通过 P、PI、PID 对比呈现速度、误差与超调的权衡", en: "P/PI/PID comparison highlighted trade-offs among speed, error, and overshoot" },
    ],
  },
  {
    id: "solidworks",
    category: "structure",
    index: "08",
    title: { zh: "SolidWorks 结构设计作品集", en: "SolidWorks Structural Design Portfolio" },
    eyebrow: { zh: "结构表达 · 三维装配", en: "Mechanical Design · 3D Assembly" },
    summary: {
      zh: "以三维零件、爆炸图和装配视图呈现连杆机构、电机组件与船体结构，展示从组件到整机的结构表达能力。",
      en: "3D parts, exploded views, and assemblies covering linkages, motor modules, and a hull concept—from component logic to system-level structure.",
    },
    role: {
      zh: "作品集展示结构建模成果；指定文档未拆分团队与个人范围。",
      en: "Portfolio demonstrates structural modelling outcomes; team and individual scope were not separated in the source document.",
    },
    image: ASSETS.solidworks,
    tags: ["SolidWorks", "3D Modelling", "Assembly", "Exploded View"],
    methods: [
      { zh: "完成零件建模、机构装配与多视角呈现", en: "Created parts, mechanism assemblies, and multi-view presentations" },
      { zh: "以爆炸图拆解连杆、紧固件与电机组件关系", en: "Used exploded views to clarify linkages, fasteners, and motor modules" },
      { zh: "保留未采用方案，呈现设计迭代", en: "Retained unselected concepts to communicate design iteration" },
    ],
    highlights: [
      { zh: "船体外形、内部隔板与局部安装结构均有呈现", en: "Included hull form, internal partitions, and local mounting details" },
      { zh: "从机构组件延伸到整机装配表达", en: "Extended from mechanism components to system-level assembly representation" },
    ],
  },
];

const copy = {
  zh: {
    nav: [
      ["about", "定位"],
      ["experience", "经历"],
      ["results", "成果"],
      ["work", "项目"],
      ["education", "教育"],
      ["habit", "跑步"],
    ],
    contact: "联系我",
    language: "EN",
    languageAria: "Switch to English",
    heroEyebrow: "SMART HARDWARE PROJECT MANAGER",
    heroTitleA: "让复杂硬件项目，",
    heroTitleB: "按节点落地。",
    heroLead: "刘莫昕｜智能硬件项目经理",
    heroText: "横跨门禁、智能门锁与自动化系统，把产品定义、软硬件协同、测试认证、供应链和量产交付串成一条可控路径。",
    viewWork: "查看项目",
    download: "下载中文简历",
    available: "杭州 · 开放智能硬件项目机会",
    photoCaption: "全英文课堂项目展示",
    photoSub: "浙江工商大学萨塞克斯人工智能学院",
    portraitAlt: "刘莫昕证件照",
    campusAlt: "刘莫昕在全英文课堂中进行项目展示",
    metrics: [
      ["04", "智能硬件品类"],
      ["03", "门禁机型如期上市"],
      ["05/10", "历史客诉完成闭环"],
      ["−30℃", "房车锁低温问题改善"],
    ],
    aboutKicker: "POSITIONING / 01",
    aboutTitle: "不是“传话型”项目经理，\n而是能进入技术现场的人。",
    aboutText: "我能从产品目标向下拆解研发、测试、认证、供应商与量产节点，也能进入电路、固件、结构和通信协议的讨论，把“发生了什么”推进到“为什么发生、谁来解决、如何验证”。",
    principles: [
      ["01", "全生命周期", "从立项、试样、试产到量产与售后，围绕关键里程碑持续推进。"],
      ["02", "软硬件共同语言", "理解门禁整机、锁具、电控锁、固件、局域网与云平台之间的接口。"],
      ["03", "前置风险与闭环", "用风险清单、复现路径、责任人和验证标准，把问题关在交付之前。"],
      ["04", "国际化沟通", "硕士阶段全英文教学，独立对接尼泊尔、巴基斯坦等海外客户。"],
    ],
    experienceKicker: "EXPERIENCE / 02",
    experienceTitle: "从设计端到工厂，\n把项目推过终点线。",
    experienceIntro: "当前聚焦智能门禁与智能锁具，覆盖自研整机与 OEM 双线项目。",
    proofKicker: "PRODUCTS & FIELD NOTES",
    proofIntro: "以下均为本人负责产品线与日常项目工作的实拍记录。",
    workProofGroups: [
      { title: "门禁终端", meta: "2.4 / 5 / 7 英寸 · OEM 机型", kind: "product", wide: true, images: [ASSETS.access24, ASSETS.access5, ASSETS.access7, ASSETS.accessOem] },
      { title: "家用门锁", meta: "产品定义 · 研发协同 · 交付跟进", kind: "product", wide: false, images: [ASSETS.homeLock1, ASSETS.homeLock2] },
      { title: "玻璃门锁", meta: "生物识别 · 密码交互 · 整机落地", kind: "product", wide: false, images: [ASSETS.glassLock1, ASSETS.glassLock2] },
      { title: "房车锁", meta: "结构分析 · 量产跟进 · −30℃低温验证", kind: "field", wide: true, images: [ASSETS.rvPilot, ASSETS.rvMechanism, ASSETS.rvStructure] },
      { title: "读卡器", meta: "产品推进 · 包装确认 · 机型落地", kind: "product", wide: false, images: [ASSETS.readerPackaged, ASSETS.readerModel1, ASSETS.readerModel2] },
      { title: "日常项目现场", meta: "人脸识别联调 · 问题复现 · 工程师协同", kind: "work", wide: false, images: [ASSETS.workAccessTest, ASSETS.workIssueTriage] },
    ],
    jobs: [
      {
        period: "2026.03 — 至今",
        company: "得力集团",
        role: "智能硬件项目经理",
        scope: "智能硬件项目交付",
        bullets: [
          "负责门禁机、家用门锁、玻璃门锁与房车锁多产品线，全周期统筹研发、测试、标准化、交付与售后。",
          "并行推进 2.4 / 5 / 7 英寸门禁机及 OEM 机型，管理功能、协议、硬件可靠性与试产节点。",
          "组织研发、品质、采购、供应商、生产及售后协同，推动软硬件问题从复现、定位到验证结案。",
          "独立对接尼泊尔、巴基斯坦及其他海外市场客户，使用英语完成需求澄清与项目进度沟通。",
        ],
      },
      {
        period: "2024.06 — 2024.09",
        company: "广西诺特广电有限公司",
        role: "热融合设备实习项目经理",
        scope: "产品开发与试产协同",
        bullets: ["协调设计团队与工厂资源，参与产品开发全周期，推动 3 款新品从设计进入试产。"],
      },
    ],
    resultsKicker: "DELIVERY / 03",
    resultsTitle: "用结果说话，\n用复盘继续向前。",
    resultCards: [
      ["3 款", "2.4 英寸门禁机", "完成研发、测试与试产，于 2026 年 8 月按计划上市。"],
      ["−30℃", "房车锁低温改善", "推动供应商整改锁舌低温失效，完成样机低温场景验证。"],
      ["5 条", "历史客诉闭环", "从 10 条初始台账中完成 5 条结案，覆盖硬件、固件与结构问题。"],
      ["GB 21556.2", "智能门锁合规", "推进新品认证与存量机型标准差异对齐，降低切换窗口风险。"],
    ],
    methodTitle: "我的问题复盘五问",
    methodQuestions: ["还能否止血？", "影响有多大？", "根因与责任人？", "项目机制如何改？", "如何保证不再发生？"],
    workKicker: "SELECTED WORK / 04",
    workTitle: "技术项目，\n是我管理硬件产品的底座。",
    workIntro: "这些项目不把我定义成纯研发工程师；它们证明我能读懂研发语言、识别系统边界，并与工程团队一起把方案变成可验证的结果。",
    filters: { all: "全部", ai: "AI 与算法", embedded: "嵌入式", control: "机器人与控制", structure: "结构设计" } as Record<Category, string>,
    viewCase: "查看项目",
    video: "演示视频",
    dialogMethods: "方法与系统",
    dialogHighlights: "结果与亮点",
    dialogRole: "项目参与说明",
    close: "关闭",
    educationKicker: "EDUCATION / 05",
    educationTitle: "全英文工程教育，\n让沟通不止于翻译。",
    educationText: "硕士阶段全英文教学与项目展示，训练我用英语理解复杂技术、组织论证并向不同背景的听众解释系统方案。",
    educationItems: [
      ["硕士", "机器人与自动化系统", "浙江工商大学萨塞克斯人工智能学院 · 全英文授课", "机器学习、计算机视觉、运动规划、嵌入式 AI、三维建模与仿真"],
      ["本科", "电子信息专业", "浙江工商大学", "电路、数模电、单片机、信号与系统、EDA"],
    ],
    languageTitle: "英语能力",
    languageStats: ["CET-6 519", "CET-4 520", "IELTS 6.0"],
    languageBody: "可用于海外客户需求澄清、技术方案同步、项目进度与定制事项沟通。",
    skillsTitle: "技术工具",
    skills: ["SolidWorks", "MATLAB / Simulink", "Python", "Altium Designer", "LabVIEW", "C++", "TensorFlow / PyTorch"],
    habitKicker: "DISCIPLINE / 06",
    habitTitle: "每天 4 km，\n风雨无阻。",
    habitText: "跑步是我持续时间最长的个人项目：不等待状态，不依赖天气，把每天的四公里拆成最小可执行目标。稳定、复盘、继续前进——这也是我管理长期硬件项目的方式。",
    habitQuote: "我把“持续交付”，先用在自己身上。",
    habitMetrics: [["4 km", "每日目标"], ["1,613 km", "最新累计记录"], ["272 h 34 min", "截至 2026.09.08 的记录时长 · 持续增长中"]],
    runningPhotoAlt: "刘莫昕在跑步机上坚持每日跑步",
    runningStatsAlt: "2025到2026年跑步累计里程与时长统计",
    runningRecentAlt: "2026年9月多次四公里以上跑步记录",
    resumeKicker: "RESUME / 07",
    resumeTitle: "中英文简历，\n均为两页 A4。",
    resumeText: "我的差异化在于三点：能进入技术现场理解软硬件问题，能把研发、测试、供应商与量产节点组织成可执行路径，也能依托全英文硕士背景，用英语独立对接尼泊尔、巴基斯坦等海外客户。",
    resumeCards: [
      ["中文简历", "智能硬件项目经理 · 2 页 A4", "下载 PDF"],
      ["English Resume", "Smart Hardware Project Manager · 2-page A4", "Download PDF"],
    ],
    brandKicker: "MINDSCRIBE / 08",
    brandTitle: "“灵辑”从一开始，\n就是我的个人 AI 产品实验。",
    brandText: "灵辑最初是我以个人 AI 产品经理身份独立构想并设计的智能笔记产品：把用户随手说出、录下或输入的碎片化信息，转化为持续生长的个人知识系统。它的设想不仅包括日常交流与内容问答，也包括音频记录、语义理解与笔记自动分类整理；登录后实现跨设备云端同步，并根据笔记之间的关联自动生成知识脑图和树状图。产品定位、用户流程、信息架构、Logo、UI、交互与功能体系均由我自行设计。如今 MindScribe 被重构为我的履历与项目档案，也继续证明我能从真实痛点出发，完成 AI 产品从概念定义到体验落地的全过程。",
    designed: "PRODUCT VISION · IA · UI · INTERACTION · FUNCTION",
    contactKicker: "CONTACT / 09",
    contactTitle: "寻找能真正走进技术现场的\n智能硬件项目经理？",
    contactText: "我愿意讨论门禁、IoT、机器人与自动化相关的产品项目机会。",
    email: "发送邮件",
    call: "电话联系",
    footer: "灵辑 · 刘莫昕简历展示",
    copyright: "内容与品牌设计 © 刘莫昕",
  },
  en: {
    nav: [
      ["about", "Positioning"],
      ["experience", "Experience"],
      ["results", "Results"],
      ["work", "Projects"],
      ["education", "Education"],
      ["habit", "Running"],
    ],
    contact: "Contact",
    language: "中文",
    languageAria: "切换为中文",
    heroEyebrow: "SMART HARDWARE PROJECT MANAGER",
    heroTitleA: "Turning complex hardware",
    heroTitleB: "into controlled delivery.",
    heroLead: "Moxin Liu | Smart Hardware Project Manager",
    heroText: "Across access control, smart locks, and automation systems, I connect product definition, hardware/firmware collaboration, verification, compliance, supply chain, and mass production into one executable path.",
    viewWork: "View projects",
    download: "Download English resume",
    available: "Hangzhou · Open to smart hardware opportunities",
    photoCaption: "English-taught project presentation",
    photoSub: "ZJSU Sussex Artificial Intelligence Institute",
    portraitAlt: "Portrait of Moxin Liu",
    campusAlt: "Moxin Liu presenting a project in an English-taught classroom",
    metrics: [
      ["04", "smart hardware categories"],
      ["03", "access models launched on plan"],
      ["05/10", "historical issues closed"],
      ["−30°C", "RV lock cold-case improvement"],
    ],
    aboutKicker: "POSITIONING / 01",
    aboutTitle: "Not a message-forwarding PM.\nA project manager who enters the technical room.",
    aboutText: "I translate product objectives into R&D, verification, certification, supplier, and production gates—then stay in the discussion when the issue reaches circuits, firmware, mechanics, and protocols. The job is not only to report what happened, but to drive why it happened, who will fix it, and how closure will be verified.",
    principles: [
      ["01", "Full lifecycle", "From initiation and prototypes to pilot builds, mass production, and after-sales closure."],
      ["02", "Technical common language", "Working knowledge across access control terminals, locks, firmware, LAN, cloud, and mechanics."],
      ["03", "Risk before firefighting", "Risk registers, reproducible paths, owners, and acceptance criteria before delivery."],
      ["04", "International communication", "English-taught master's program and direct client coordination across Nepal, Pakistan, and beyond."],
    ],
    experienceKicker: "EXPERIENCE / 02",
    experienceTitle: "From design desk to factory floor,\nI move projects across the line.",
    experienceIntro: "Currently focused on access control and smart locks across both in-house hardware and OEM programmes.",
    proofKicker: "PRODUCTS & FIELD NOTES",
    proofIntro: "All images below document product lines and day-to-day project work under my responsibility.",
    workProofGroups: [
      { title: "Access Control Terminals", meta: "2.4 / 5 / 7-inch · OEM models", kind: "product", wide: true, images: [ASSETS.access24, ASSETS.access5, ASSETS.access7, ASSETS.accessOem] },
      { title: "Residential Smart Locks", meta: "Product definition · R&D coordination · delivery", kind: "product", wide: false, images: [ASSETS.homeLock1, ASSETS.homeLock2] },
      { title: "Glass-door Locks", meta: "Biometrics · keypad interaction · product delivery", kind: "product", wide: false, images: [ASSETS.glassLock1, ASSETS.glassLock2] },
      { title: "RV Locks", meta: "Mechanism analysis · pilot build · −30°C validation", kind: "field", wide: true, images: [ASSETS.rvPilot, ASSETS.rvMechanism, ASSETS.rvStructure] },
      { title: "Card Readers", meta: "Product execution · packaging check · model delivery", kind: "product", wide: false, images: [ASSETS.readerPackaged, ASSETS.readerModel1, ASSETS.readerModel2] },
      { title: "Project Fieldwork", meta: "Face-recognition testing · issue reproduction · engineering alignment", kind: "work", wide: false, images: [ASSETS.workAccessTest, ASSETS.workIssueTriage] },
    ],
    jobs: [
      {
        period: "Mar 2026 — Present",
        company: "Deli Group",
        role: "Smart Hardware Project Manager",
        scope: "Smart hardware project delivery",
        bullets: [
          "Own the lifecycle of access control terminals, residential smart locks, glass-door locks, and RV locks—from R&D and verification to standardisation, delivery, and after-sales.",
          "Run concurrent 2.4 / 5 / 7-inch terminal and OEM programmes across functional, protocol, hardware reliability, and pilot-build gates.",
          "Coordinate R&D, quality, sourcing, suppliers, production, and after-sales to move hardware/firmware issues from reproduction to validated closure.",
          "Independently coordinate with customers in Nepal, Pakistan, and other overseas markets in English across requirements, solutions, and progress.",
        ],
      },
      {
        period: "Jun 2024 — Sep 2024",
        company: "Guangxi Nuote Broadcasting Co., Ltd.",
        role: "Thermal Fusion Equipment Project Intern",
        scope: "Product development & pilot coordination",
        bullets: ["Coordinated design and factory resources and helped move three products from design into pilot production."],
      },
    ],
    resultsKicker: "DELIVERY / 03",
    resultsTitle: "Measured outcomes.\nReusable lessons.",
    resultCards: [
      ["3 models", "2.4-inch access terminals", "Completed R&D, verification, and pilot production for an August 2026 launch."],
      ["−30°C", "RV lock cold-case fix", "Coordinated supplier correction and sample validation for low-temperature latch failure."],
      ["5 cases", "historical issue closure", "Closed 5 of 10 inherited cases across hardware, firmware, and mechanical defects."],
      ["GB 21556.2", "smart lock compliance", "Advanced new-product certification and legacy model alignment through a standards transition."],
    ],
    methodTitle: "My five-question review",
    methodQuestions: ["Can we contain it now?", "What is the real impact?", "Root cause and owner?", "What must the project system change?", "How do we prevent recurrence?"],
    workKicker: "SELECTED WORK / 04",
    workTitle: "Engineering projects are the technical foundation\nbehind my project management.",
    workIntro: "These projects do not position me as a pure R&D engineer. They show that I can read engineering language, recognise system boundaries, and work with technical teams toward verifiable outcomes.",
    filters: { all: "All", ai: "AI & Algorithms", embedded: "Embedded", control: "Robotics & Control", structure: "Mechanical Design" } as Record<Category, string>,
    viewCase: "View case",
    video: "Demo video",
    dialogMethods: "Methods & system",
    dialogHighlights: "Results & highlights",
    dialogRole: "Contribution context",
    close: "Close",
    educationKicker: "EDUCATION / 05",
    educationTitle: "English-taught engineering education—\ncommunication beyond translation.",
    educationText: "An English-taught master's programme and project presentations trained me to understand complex technical material in English, structure an argument, and explain systems to audiences with different backgrounds.",
    educationItems: [
      ["M.Sc.", "Robotics and Autonomous Systems", "ZJSU Sussex Artificial Intelligence Institute · English-taught", "Machine learning, computer vision, motion planning, embedded AI, 3D modelling and simulation"],
      ["Bachelor", "Electronic Information", "Zhejiang Gongshang University", "Circuits, digital/analogue electronics, microcontrollers, signals and systems, EDA"],
    ],
    languageTitle: "English proficiency",
    languageStats: ["CET-6 519", "CET-4 520", "IELTS 6.0"],
    languageBody: "Used for overseas requirement clarification, technical alignment, project updates, and customisation discussions.",
    skillsTitle: "Technical toolkit",
    skills: ["SolidWorks", "MATLAB / Simulink", "Python", "Altium Designer", "LabVIEW", "C++", "TensorFlow / PyTorch"],
    habitKicker: "DISCIPLINE / 06",
    habitTitle: "4 km every day.\nWhatever the weather.",
    habitText: "Running is my longest-running personal project: do not wait for the perfect state, do not depend on the weather, and reduce consistency to a minimum executable target—four kilometres a day. Stabilise, review, and move forward. It is also how I manage long-horizon hardware programmes.",
    habitQuote: "I apply continuous delivery to myself first.",
    habitMetrics: [["4 km", "daily target"], ["1,613 km", "latest recorded total"], ["272 h 34 min", "recorded by 8 Sep 2026 · still growing"]],
    runningPhotoAlt: "Moxin Liu maintaining a daily running routine on a treadmill",
    runningStatsAlt: "Running distance and duration statistics from 2025 to 2026",
    runningRecentAlt: "Multiple runs exceeding four kilometres in September 2026",
    resumeKicker: "RESUME / 07",
    resumeTitle: "Chinese and English resumes,\nboth two-page A4 PDFs.",
    resumeText: "My profile combines three differentiators: enough engineering depth to enter the technical room, the delivery discipline to align R&D, verification, suppliers, and mass production, and the English capability to independently coordinate with customers in Nepal, Pakistan, and other overseas markets.",
    resumeCards: [
      ["中文简历", "智能硬件项目经理 · 2 页 A4", "下载 PDF"],
      ["English Resume", "Smart Hardware Project Manager · 2-page A4", "Download PDF"],
    ],
    brandKicker: "MINDSCRIBE / 08",
    brandTitle: "MindScribe began as\nmy personal AI product experiment.",
    brandText: "I originally conceived and designed MindScribe as an intelligent note-taking product in the role of an independent AI product manager: a system that could turn fragmented thoughts—spoken, recorded, or typed—into a continuously growing personal knowledge base. The product vision combined everyday conversation and content Q&A with audio capture, semantic understanding, automatic note classification and organisation, cross-device cloud synchronisation after sign-in, and the automatic generation of knowledge maps and tree views from relationships between notes. I independently designed the product positioning, user flows, information architecture, logo, UI, interactions, and functional system. Rebuilt today as my professional archive, MindScribe still demonstrates my ability to move an AI product from a real user problem through concept definition to a coherent experience.",
    designed: "PRODUCT VISION · IA · UI · INTERACTION · FUNCTION",
    contactKicker: "CONTACT / 09",
    contactTitle: "Looking for a smart hardware PM\nwho can enter the technical room?",
    contactText: "I am open to product and project opportunities across access control, IoT, robotics, and automation.",
    email: "Email me",
    call: "Call",
    footer: "MindScribe · Moxin Liu Portfolio",
    copyright: "Content and brand design © Moxin Liu",
  },
};

function BrandMark({ className = "" }: { className?: string }) {
  return <img className={className} src={ASSETS.brand} alt="" aria-hidden="true" draggable={false} />;
}

function Reveal({ children, className = "", delay = 0 }: { children: ReactNode; className?: string; delay?: number }) {
  const ref = useRef<HTMLDivElement>(null);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const element = ref.current;
    if (!element) return;
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setVisible(true);
          observer.disconnect();
        }
      },
      { threshold: 0.12 },
    );
    observer.observe(element);
    return () => observer.disconnect();
  }, []);

  return (
    <div
      ref={ref}
      className={`reveal ${visible ? "is-visible" : ""} ${className}`}
      style={{ transitionDelay: `${delay}ms` }}
    >
      {children}
    </div>
  );
}

function Kicker({ children, inverse = false }: { children: ReactNode; inverse?: boolean }) {
  return <p className={`section-kicker ${inverse ? "inverse" : ""}`}>{children}</p>;
}

export default function Home() {
  const [lang, setLang] = useState<Lang>(() => (localStorage.getItem("lingji-language") === "en" ? "en" : "zh"));
  const [menuOpen, setMenuOpen] = useState(false);
  const [filter, setFilter] = useState<Category>("all");
  const [selected, setSelected] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);
  const c = copy[lang];

  useEffect(() => {
    localStorage.setItem("lingji-language", lang);
    document.documentElement.lang = lang === "zh" ? "zh-CN" : "en";
    document.title = lang === "zh" ? "灵辑 · 刘莫昕简历展示" : "MindScribe · Moxin Liu Portfolio";
  }, [lang]);

  useEffect(() => {
    const timer = window.setTimeout(() => setLoading(false), 760);
    return () => window.clearTimeout(timer);
  }, []);

  const filteredProjects = useMemo(
    () => (filter === "all" ? projects : projects.filter((project) => project.category === filter)),
    [filter],
  );

  const toggleLanguage = () => {
    setLang((current) => (current === "zh" ? "en" : "zh"));
    setMenuOpen(false);
  };

  return (
    <div className="site-shell">
      {loading && (
        <div className="loading-screen" aria-label={lang === "zh" ? "页面加载中" : "Loading"}>
          <div className="loading-mark-wrap">
            <img className="loading-mark" src={ASSETS.loading} alt="" aria-hidden="true" />
            <span>{lang === "zh" ? "灵辑" : "MINDSCRIBE"}</span>
          </div>
        </div>
      )}

      <header className="site-header">
        <div className="header-inner">
          <a className="brand" href="#top" aria-label={c.footer}>
            <BrandMark className="brand-icon" />
            <span className="brand-lockup">
              <strong>{lang === "zh" ? "灵辑" : "MindScribe"}</strong>
              <small>{lang === "zh" ? "刘莫昕简历展示" : "Moxin Liu Portfolio"}</small>
            </span>
          </a>

          <nav className={`desktop-nav ${menuOpen ? "is-open" : ""}`} aria-label="Primary navigation">
            {c.nav.map(([id, label]) => (
              <a key={id} href={`#${id}`} onClick={() => setMenuOpen(false)}>{label}</a>
            ))}
          </nav>

          <div className="header-actions">
            <button className="language-switch" type="button" onClick={toggleLanguage} aria-label={c.languageAria}>
              <Globe2 size={16} />
              <span>{c.language}</span>
            </button>
            <a className="header-contact" href="#contact">{c.contact}<ArrowRight size={15} /></a>
            <button className="menu-button" type="button" onClick={() => setMenuOpen((value) => !value)} aria-label="Menu">
              {menuOpen ? <X size={22} /> : <Menu size={22} />}
            </button>
          </div>
        </div>
      </header>

      <main id="top">
        <section className="hero-section">
          <div className="hero-grid-lines" aria-hidden="true" />
          <div className="container hero-layout">
            <div className="hero-copy">
              <div className="hero-eyebrow"><span />{c.heroEyebrow}</div>
              <h1>
                <span>{c.heroTitleA}</span>
                <em>{c.heroTitleB}</em>
              </h1>
              <p className="hero-lead">{c.heroLead}</p>
              <p className="hero-description">{c.heroText}</p>
              <div className="hero-actions">
                <a className="button button-primary" href="#work">{c.viewWork}<ArrowDown size={17} /></a>
                <a className="button button-ghost" href={lang === "zh" ? ASSETS.resumeZh : ASSETS.resumeEn} target="_blank" rel="noreferrer">
                  <Download size={17} />{c.download}
                </a>
              </div>
              <div className="availability"><span className="status-dot" />{c.available}</div>
            </div>

            <div className="hero-visual" aria-label={c.campusAlt}>
              <div className="campus-frame">
                <img src={ASSETS.campus} alt={c.campusAlt} />
                <div className="campus-overlay" />
                <div className="campus-caption">
                  <span>{c.photoCaption}</span>
                  <small>{c.photoSub}</small>
                </div>
              </div>
              <div className="profile-card">
                <img src={ASSETS.profile} alt={c.portraitAlt} />
                <div><strong>{lang === "zh" ? "刘莫昕" : "Moxin Liu"}</strong><span>PM · AI · HARDWARE</span></div>
              </div>
              <div className="orbit-label">2026<br />PORTFOLIO</div>
            </div>
          </div>

          <div className="container metrics-strip">
            {c.metrics.map(([value, label], index) => (
              <div className="metric" key={label}>
                <span className="metric-index">0{index + 1}</span>
                <strong>{value}</strong>
                <p>{label}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="section section-about" id="about">
          <div className="container about-layout">
            <Reveal className="about-heading">
              <Kicker>{c.aboutKicker}</Kicker>
              <h2 className="section-title preserve-lines">{c.aboutTitle}</h2>
            </Reveal>
            <Reveal className="about-body" delay={70}>
              <p className="section-intro">{c.aboutText}</p>
              <div className="principles-grid">
                {c.principles.map(([index, title, text]) => (
                  <article className="principle-card" key={index}>
                    <span>{index}</span>
                    <h3>{title}</h3>
                    <p>{text}</p>
                  </article>
                ))}
              </div>
            </Reveal>
          </div>
        </section>

        <section className="section experience-section" id="experience">
          <div className="container experience-layout">
            <Reveal className="experience-sticky">
              <Kicker inverse>{c.experienceKicker}</Kicker>
              <h2 className="section-title inverse preserve-lines">{c.experienceTitle}</h2>
              <p>{c.experienceIntro}</p>
              <div className="experience-icon"><BriefcaseBusiness size={28} /></div>
            </Reveal>

            <div className="timeline">
              {c.jobs.map((job, jobIndex) => (
                <Reveal className="timeline-item" key={job.company} delay={jobIndex * 70}>
                  <div className="timeline-marker"><span>{String(jobIndex + 1).padStart(2, "0")}</span></div>
                  <div className="timeline-content">
                    <div className="timeline-meta"><span>{job.period}</span><span>{job.scope}</span></div>
                    <h3>{job.company}</h3>
                    <h4>{job.role}</h4>
                    <ul>
                      {job.bullets.map((bullet) => <li key={bullet}><Check size={16} />{bullet}</li>)}
                    </ul>
                    {jobIndex === 0 && (
                      <div className="work-proof">
                        <div className="work-proof-heading">
                          <span>{c.proofKicker}</span>
                          <p>{c.proofIntro}</p>
                        </div>
                        <div className="work-proof-grid">
                          {c.workProofGroups.map((group) => (
                            <article className={`work-proof-card ${group.wide ? "is-wide" : ""}`} key={group.title}>
                              <div className={`work-proof-images is-${group.kind}`}>
                                {group.images.map((image, imageIndex) => (
                                  <img src={image} alt={`${group.title} ${imageIndex + 1}`} loading="lazy" key={image} />
                                ))}
                              </div>
                              <div className="work-proof-copy"><h5>{group.title}</h5><p>{group.meta}</p></div>
                            </article>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </Reveal>
              ))}
            </div>
          </div>
        </section>

        <section className="section results-section" id="results">
          <div className="container">
            <Reveal className="results-heading">
              <div>
                <Kicker>{c.resultsKicker}</Kicker>
                <h2 className="section-title preserve-lines">{c.resultsTitle}</h2>
              </div>
              <p>{lang === "zh" ? "数据均来自试用期工作报告与项目记录。" : "Metrics are drawn from the probation report and project records."}</p>
            </Reveal>

            <div className="results-grid">
              {c.resultCards.map(([value, title, text], index) => (
                <Reveal className="result-card" key={title} delay={index * 45}>
                  <span className="result-number">{value}</span>
                  <h3>{title}</h3>
                  <p>{text}</p>
                  <span className="result-corner">0{index + 1}</span>
                </Reveal>
              ))}
            </div>

            <Reveal className="review-method">
              <div className="method-title"><Target size={24} /><h3>{c.methodTitle}</h3></div>
              <div className="method-questions">
                {c.methodQuestions.map((question, index) => (
                  <div key={question}><span>{index + 1}</span><p>{question}</p></div>
                ))}
              </div>
            </Reveal>
          </div>
        </section>

        <section className="section work-section" id="work">
          <div className="container">
            <Reveal className="work-heading">
              <div>
                <Kicker>{c.workKicker}</Kicker>
                <h2 className="section-title preserve-lines">{c.workTitle}</h2>
              </div>
              <p>{c.workIntro}</p>
            </Reveal>

            <div className="project-filters" role="tablist" aria-label="Project filters">
              {(Object.keys(c.filters) as Category[]).map((category) => (
                <button
                  key={category}
                  type="button"
                  className={filter === category ? "is-active" : ""}
                  onClick={() => setFilter(category)}
                  role="tab"
                  aria-selected={filter === category}
                >
                  {c.filters[category]}
                </button>
              ))}
            </div>

            <div className="projects-grid">
              {filteredProjects.map((project, index) => (
                <Reveal className={`project-card ${project.featured ? "featured" : ""}`} key={project.id} delay={(index % 3) * 50}>
                  <div className="project-media">
                    <img src={project.image} alt={project.title[lang]} />
                    <div className="project-media-shade" />
                    <span className="project-index">{project.index}</span>
                    {project.video && <span className="video-badge"><CirclePlay size={15} />{c.video}</span>}
                  </div>
                  <div className="project-content">
                    <p className="project-eyebrow">{project.eyebrow[lang]}</p>
                    <h3>{project.title[lang]}</h3>
                    <p>{project.summary[lang]}</p>
                    <div className="project-tags">{project.tags.slice(0, 4).map((tag) => <span key={tag}>{tag}</span>)}</div>
                    <button type="button" className="project-link" onClick={() => setSelected(project)}>
                      {c.viewCase}<ArrowRight size={16} />
                    </button>
                  </div>
                </Reveal>
              ))}
            </div>
          </div>
        </section>

        <section className="section education-section" id="education">
          <div className="container education-layout">
            <Reveal className="education-image">
              <img src={ASSETS.campus} alt={c.campusAlt} />
              <div className="education-image-label"><Languages size={20} /><span>{lang === "zh" ? "全英文教学 · 项目演讲" : "English-taught · Project presentations"}</span></div>
            </Reveal>

            <Reveal className="education-content" delay={70}>
              <Kicker>{c.educationKicker}</Kicker>
              <h2 className="section-title preserve-lines">{c.educationTitle}</h2>
              <p className="education-lead">{c.educationText}</p>
              <div className="education-list">
                {c.educationItems.map(([degree, major, school, courses]) => (
                  <article key={degree + major}>
                    <span>{degree}</span>
                    <div><h3>{major}</h3><h4>{school}</h4><p>{courses}</p></div>
                  </article>
                ))}
              </div>
              <div className="language-card">
                <div><Globe2 size={23} /><h3>{c.languageTitle}</h3></div>
                <div className="language-stats">{c.languageStats.map((item) => <span key={item}>{item}</span>)}</div>
                <p>{c.languageBody}</p>
              </div>
              <div className="skills-row"><strong>{c.skillsTitle}</strong><div>{c.skills.map((skill) => <span key={skill}>{skill}</span>)}</div></div>
            </Reveal>
          </div>
        </section>

        <section className="section habit-section" id="habit">
          <div className="container habit-layout">
            <Reveal className="habit-copy">
              <Kicker inverse>{c.habitKicker}</Kicker>
              <h2 className="section-title inverse preserve-lines">{c.habitTitle}</h2>
              <p>{c.habitText}</p>
              <blockquote><Footprints size={22} /><span>{c.habitQuote}</span></blockquote>
              <div className="habit-metrics">
                {c.habitMetrics.map(([value, label]) => (
                  <div key={label}><strong>{value}</strong><span>{label}</span></div>
                ))}
              </div>
            </Reveal>
            <Reveal className="habit-gallery" delay={70}>
              <figure className="habit-photo">
                <img src={ASSETS.runningPhoto} alt={c.runningPhotoAlt} />
                <figcaption>EVERY DAY · KEEP MOVING</figcaption>
              </figure>
              <div className="habit-screens">
                <img src={ASSETS.runningStats} alt={c.runningStatsAlt} />
                <img src={ASSETS.runningRecent} alt={c.runningRecentAlt} />
              </div>
            </Reveal>
          </div>
        </section>

        <section className="section resume-section" id="resume">
          <div className="container resume-layout">
            <Reveal>
              <Kicker inverse>{c.resumeKicker}</Kicker>
              <h2 className="section-title inverse preserve-lines">{c.resumeTitle}</h2>
              <p>{c.resumeText}</p>
            </Reveal>
            <div className="resume-cards">
              {[ASSETS.resumeZh, ASSETS.resumeEn].map((href, index) => {
                const [title, meta, action] = c.resumeCards[index];
                return (
                  <Reveal key={href} delay={index * 70}>
                    <a className="resume-card" href={href} target="_blank" rel="noreferrer">
                      <div className="resume-paper">
                        <div className="paper-head"><span /><span /></div>
                        <div className="paper-name">{index === 0 ? "刘莫昕" : "MOXIN LIU"}</div>
                        <div className="paper-lines"><i /><i /><i /><i /></div>
                      </div>
                      <div><h3>{title}</h3><p>{meta}</p><span>{action}<ExternalLink size={14} /></span></div>
                    </a>
                  </Reveal>
                );
              })}
            </div>
          </div>
        </section>

        <section className="section brand-section" id="lingji">
          <div className="container brand-story">
            <Reveal className="brand-story-mark">
              <BrandMark />
              <span>{c.designed}</span>
            </Reveal>
            <Reveal className="brand-story-copy" delay={70}>
              <Kicker inverse>{c.brandKicker}</Kicker>
              <h2 className="section-title inverse preserve-lines">{c.brandTitle}</h2>
              <p>{c.brandText}</p>
              <div className="brand-capabilities">
                {[Sparkles, ShieldCheck, Rocket, Users].map((Icon, index) => <span key={index}><Icon size={18} /></span>)}
              </div>
            </Reveal>
          </div>
        </section>

        <section className="section contact-section" id="contact">
          <div className="container contact-layout">
            <Reveal>
              <Kicker>{c.contactKicker}</Kicker>
              <h2 className="contact-title preserve-lines">{c.contactTitle}</h2>
              <p>{c.contactText}</p>
            </Reveal>
            <Reveal className="contact-actions" delay={70}>
              <a href="mailto:scretliasion@163.com"><Mail size={20} /><span><small>{c.email}</small>scretliasion@163.com</span><ArrowRight size={18} /></a>
              <a href="tel:+8615994461673"><Phone size={20} /><span><small>{c.call}</small>+86 159 9446 1673</span><ArrowRight size={18} /></a>
              <div className="location"><MapPin size={18} /><span>{lang === "zh" ? "浙江 · 杭州" : "Hangzhou · Zhejiang"}</span></div>
            </Reveal>
          </div>
        </section>
      </main>

      <footer className="site-footer">
        <div className="container footer-inner">
          <div className="footer-brand"><BrandMark /><span><strong>{c.footer}</strong><small>{c.copyright}</small></span></div>
          <a href="#top">{lang === "zh" ? "返回顶部" : "Back to top"}<ArrowRight size={14} /></a>
        </div>
      </footer>

      <Dialog open={Boolean(selected)} onOpenChange={(open) => !open && setSelected(null)}>
        <DialogContent className="project-dialog">
          {selected && (
            <div className="dialog-scroll">
              <div className="dialog-media">
                {selected.video ? (
                  <video controls poster={selected.image} preload="metadata">
                    <source src={selected.video} type="video/mp4" />
                  </video>
                ) : (
                  <img src={selected.image} alt={selected.title[lang]} />
                )}
                <span>{selected.index}</span>
              </div>
              <DialogHeader className="dialog-header">
                <p>{selected.eyebrow[lang]}</p>
                <DialogTitle>{selected.title[lang]}</DialogTitle>
                <DialogDescription>{selected.summary[lang]}</DialogDescription>
              </DialogHeader>
              <div className="dialog-tags">{selected.tags.map((tag) => <span key={tag}>{tag}</span>)}</div>
              <div className="dialog-columns">
                <div><h4>{c.dialogMethods}</h4><ul>{selected.methods.map((item) => <li key={item[lang]}><Check size={15} />{item[lang]}</li>)}</ul></div>
                <div><h4>{c.dialogHighlights}</h4><ul>{selected.highlights.map((item) => <li key={item[lang]}><ArrowRight size={15} />{item[lang]}</li>)}</ul></div>
              </div>
              <div className="dialog-role"><strong>{c.dialogRole}</strong><p>{selected.role[lang]}</p></div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
