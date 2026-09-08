#import "report-theme.typ": report-theme

#show: report-theme.with(
  title: "Moxin Liu | Smart Hardware Project Manager",
  author: "Moxin Liu",
  rhythm: "report",
  body-size: 9.25pt,
  running-header: false,
)

#set page(
  paper: "a4",
  margin: (top: 1.05cm, bottom: 1.0cm, x: 1.25cm),
  numbering: none,
  header: none,
  footer: none,
)
#set text(font: ("Noto Sans", "Noto Sans CJK SC"), size: 9.25pt, fill: rgb("#1b2330"))
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
    text(size: 11.1pt, weight: 700, fill: navy, title),
    line(length: 100%, stroke: 0.75pt + blue),
  )
  v(0.5em)
}

#let role-head(company, role, period) = {
  grid(
    columns: (1fr, auto),
    column-gutter: 10pt,
    [#text(weight: 700, size: 10.1pt, fill: navy)[#company] #h(0.5em) #text(weight: 600, fill: blue)[#role]],
    align(right)[#text(size: 8.7pt, weight: 600, fill: muted)[#period]],
  )
}

#let tags(items) = {
  for item in items {
    box(
      inset: (x: 6pt, y: 3pt),
      radius: 2pt,
      fill: pale,
      stroke: 0.4pt + rgb("#cfe0ff"),
      text(size: 8.1pt, weight: 600, fill: blue, item),
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
  spacing: 3.05pt,
)

#let experience-list(..items) = list(
  ..items,
  tight: true,
  marker: [#text(fill: blue, weight: 700)[•]],
  indent: 10pt,
  body-indent: 5pt,
  spacing: 4.8pt,
)

#let metric(value, label) = rect(
  width: 100%,
  inset: (x: 7pt, y: 6pt),
  radius: 2pt,
  fill: pale,
  stroke: 0.45pt + rule,
)[
  #text(size: 12.3pt, weight: 800, fill: blue)[#value]
  #linebreak()
  #text(size: 7.6pt, weight: 600, fill: muted)[#label]
]

#let product-card(title, detail) = rect(
  width: 100%,
  height: 2.05cm,
  inset: (x: 8pt, y: 7pt),
  radius: 3pt,
  fill: pale,
  stroke: 0.45pt + rule,
)[
  #text(size: 8.6pt, weight: 700, fill: navy)[#title]
  #v(0.25em)
  #text(size: 7.1pt, fill: muted)[#detail]
]

#grid(
  columns: (2.15cm, 1fr, auto),
  column-gutter: 12pt,
  align: center,
  [
    #image("assets/profile.webp", width: 2.15cm, height: 2.75cm, fit: "cover")
  ],
  [
    #link("https://mindscribe-app.pages.dev/")[#text(size: 23pt, weight: 800, fill: navy)[MOXIN LIU]]
    #v(0.2em)
    #text(size: 12.7pt, weight: 700, fill: blue)[Smart Hardware Project Manager]
  ],
  align(right)[
    #link("https://mindscribe-app.pages.dev/")[#image("assets/mindscribe-brand.png", width: 1.05cm)]
    #linebreak()
    #text(size: 7.4pt, weight: 700, fill: navy)[MindScribe]
    #linebreak()
    #text(size: 8.7pt, fill: navy)[Hangzhou, China · +86 159 9446 1673]
    #linebreak()
    #link("mailto:scretliasion@163.com")[#text("scretliasion@163.com")]
    #linebreak()
    #link("https://mindscribe-app.pages.dev/")[#text(size: 8.2pt)[Portfolio: mindscribe-app.pages.dev]]
    #linebreak()
    #text(size: 8.2pt, fill: muted)[English working proficiency]
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
  #text(weight: 700, fill: navy)[PROFILE] #h(0.45em)
  Smart hardware project manager experienced in the full lifecycle of access control terminals, residential smart locks, glass-door locks, and RV locks—from requirements and R&D tracking through verification, compliance, supplier coordination, pilot builds, mass production, and after-sales closure. Completed an English-taught master's program and use English as a working language, with independent client coordination experience across Nepal, Pakistan, and other overseas markets. Able to bridge hardware, firmware, mechanical design, cloud/LAN architecture, quality, and supply chain teams to deliver products against milestones and risks.
]

#section([CORE CAPABILITIES])
#tags(("Product Lifecycle", "Cross-functional Delivery", "HW/FW Integration", "Verification", "Compliance", "NPI & Mass Production", "Issue Closure", "English Client Communication"))

#section([PROFESSIONAL EXPERIENCE])
#role-head([Deli Group], [Smart Hardware Project Manager], [Mar 2026 — Present])
#v(0.2em)
#text(size: 8.8pt, fill: muted)[Own project execution across access control terminals, residential smart locks, glass-door locks, and RV locks, covering in-house products and OEM programs.]
#v(0.25em)
#experience-list(
  [Managed concurrent 2.4-inch, 5-inch, and 7-inch access control projects and multiple OEM variants; completed development, verification, and pilot build for AL912C, AC213, and AC205C, supporting their August 2026 launch.],
  [Led type testing, hardware reliability verification, first-round functional validation, and packaging design for the waterproof AC516/AL962C; organized retesting and risk reviews for palm-vein recognition and component lead-time issues.],
  [Drove new-standard compliance for the AC22 face-recognition lock by comparing certification paths and coordinating corrective actions; also aligned legacy products including DL-AC27 with updated parameters, documentation, and compliance requirements.],
  [Managed the RV lock from patent-risk screening and supplier sourcing to pricing, pilot verification, and on-site production follow-up; coordinated a supplier fix for low-temperature latch failure, enabling normal sample operation at -30°C.],
  [Took over a 10-item historical after-sales backlog and closed 5 cases; coordinated root-cause analysis and corrective actions across relay soldering, fingerprint recognition, structural noise, doorbell response, firmware, and power compatibility.],
  [Produced a focused failure-analysis brief for AC512 doorbell response issues by mapping circuit logic and common wiring errors, improving field diagnosis and after-sales decision consistency.],
  [Standardized product parameters, operating instructions, technical specifications, and operation-video QR codes; clarified ownership and handoff rules between product and after-sales teams.],
  [Independently coordinated with customers in Nepal, Pakistan, and other overseas markets, covering requirement clarification, solution alignment, customization follow-up, and project progress communication in English.],
)

#v(0.5em)
#rect(width: 100%, inset: (x: 9pt, y: 7pt), radius: 3pt, fill: navy)[
  #grid(
    columns: (auto, 1fr),
    column-gutter: 12pt,
    [#text(size: 8.1pt, weight: 700, fill: white)[DELIVERY METHOD]],
    [#text(size: 8.1pt, fill: rgb("#dce6f7"))[Milestones → risk register → owners → acceptance criteria → verified closure]],
  )
]

#v(0.42em)
#role-head([Guangxi Nuote Broadcasting Co., Ltd.], [Thermal Fusion Equipment Project Intern], [Jun 2024 — Sep 2024])
#v(0.16em)
#compact-list(
  [Coordinated design and factory resources across the product development cycle and helped move three new products from design into pilot production.],
)

#v(0.75em)
#grid(
  columns: (1fr, 1fr, 1fr, 1fr),
  column-gutter: 6pt,
  product-card([Access Terminals], [2.4 / 5 / 7-inch and OEM]),
  product-card([Residential Locks], [Product delivery and compliance]),
  product-card([Glass-door Locks], [Recognition, interaction, delivery]),
  product-card([RV Locks], [Mechanism, pilot, production]),
)
#v(0.52em)
#rect(width: 100%, inset: (x: 10pt, y: 8pt), radius: 3pt, fill: navy)[
  #grid(
    columns: (auto, 1fr),
    column-gutter: 12pt,
    [#text(size: 7.8pt, weight: 700, fill: rgb("#8bb0ff"))[DELIVERY CHAIN]],
    [#text(size: 7.8pt, fill: white)[Definition → R&D alignment → verification → supply chain → production → issue closure]],
  )
]
#v(0.56em)
#line(length: 100%, stroke: 0.55pt + rule)
#v(0.3em)
#align(center)[#text(size: 7.3pt, fill: muted)[Target roles: Smart Hardware Project Manager · Product Project Manager · Access Control / IoT / Robotics & Automation]]

#pagebreak()

#grid(
  columns: (auto, 1fr, auto),
  column-gutter: 12pt,
  align: center,
  [#link("https://mindscribe-app.pages.dev/")[#image("assets/mindscribe-brand.png", width: 0.78cm)]],
  [#text(size: 14pt, weight: 800, fill: navy)[MOXIN LIU] #h(0.5em) #text(size: 9.3pt, weight: 700, fill: blue)[Smart Hardware Project Manager]],
  align(right)[#text(size: 8.3pt, fill: muted)[+86 159 9446 1673 · #text("scretliasion@163.com")]],
)

#v(0.55em)
#grid(
  columns: (1fr, 1fr, 1fr),
  column-gutter: 6pt,
  metric([3 models], [2.4-inch terminals launched]),
  metric([5 / 10], [historical issues closed]),
  metric([-30°C], [RV lock validation passed]),
)

#section([SELECTED DELIVERY CASES])
#text(weight: 700, fill: navy)[01 | Multi-model Access Control Launches & OEM Delivery]
#v(0.1em)
#text(size: 8.8pt, fill: muted)[AL912C / AC213 / AC205C / AC516 / AL962C / AC611 / AC711 / AC612 / AC615]
#v(0.16em)
Structured project gates from planning and protocol/functional tests through reliability verification, pilot builds, and warehouse release. Coordinated R&D, quality, sourcing, suppliers, and production across both in-house terminals and OEM firmware/documentation variants.

#v(0.42em)
#text(weight: 700, fill: navy)[02 | Smart Lock Compliance Transition]
#v(0.1em)
Managed the GB 21556.2-2025 transition for new and in-market products, including AC22 certification and upgrades across AC10, AC21, AC310, and DL-AC27. Balanced launch timing with test non-conformity correction, documentation updates, and legacy portfolio compliance.

#v(0.42em)
#text(weight: 700, fill: navy)[03 | Quality & Customer Issue Closure]
#v(0.1em)
Established a repeatable flow covering reproduction, impact assessment, hardware/firmware isolation, action ownership, verification, and closure. Applied it to PCB soldering, firmware defects, recognition performance, structural failure, power compatibility, and installation wiring cases.

#section([EDUCATION])
#role-head([Zhejiang Gongshang University Sussex Artificial Intelligence Institute], [M.Sc. in Robotics and Autonomous Systems — English-taught], [])
#v(0.1em)
#text(size: 8.8pt, fill: muted)[Machine Learning & Deep Learning, Computer Vision, Motion Planning & Control, Embedded AI, 3D Modelling and Mechanical Simulation]
#v(0.36em)
#role-head([Zhejiang Gongshang University], [Bachelor's Degree in Electronic Information], [])
#v(0.1em)
#text(size: 8.8pt, fill: muted)[Circuit Analysis, Digital/Analogue Electronics, Microcontrollers, Signals & Systems, EDA]

#section([ENGINEERING & RESEARCH PROJECTS])
#compact-list(
  [*High-speed railway 5G beam/resource coordination:* Contributed to a four-scenario simulation platform using PPO and Q-learning for continuous beam/power actions and discrete handover decisions; the project report records handover success improving from 92.8% to 97.4% on straight-track simulation.],
  [*UAV-based cellular coverage blind-spot search:* Built a simulation concept spanning path planning, channel modelling, and signal visualization; inward-spiral paths reduced simulated mission time by approximately 28.92%–33.33% versus reciprocating paths across three scenarios.],
  [*Candy colour-sorting prototype:* Integrated Arduino UNO, a TCS34725 sensor, and dual servos; the report records 76 pieces sorted in a three-minute accelerated test at 97.4% accuracy, followed by threshold, timing, and anti-sticking improvements.],
  [*Robotics and autonomous navigation:* Integrated ROS Navigation, Cartographer, and RViz on a DEEP Robotics quadruped platform for live mapping, sensor visualisation, and multi-point navigation; also contributed to five-bar robot and DC motor control projects.],
)

#section([TOOLS, LANGUAGES & DOMAIN KNOWLEDGE])
#grid(
  columns: (8.4em, 1fr),
  row-gutter: 3.4pt,
  column-gutter: 8pt,
  text(weight: 700, fill: navy)[Project Delivery], [Milestones, risk registers, cross-functional coordination, supplier management, verification, pilot/mass production, issue closure],
  text(weight: 700, fill: navy)[Smart Hardware], [Access control systems, smart locks, firmware/protocols, LAN/cloud fundamentals, failure analysis, mechanical integration],
  text(weight: 700, fill: navy)[Tools & Coding], [SolidWorks, MATLAB/Simulink, Python, Altium Designer, LabVIEW, C++, TensorFlow/PyTorch],
  text(weight: 700, fill: navy)[Languages], [Mandarin (native); English (working proficiency) — CET-6 519, CET-4 520, IELTS 6.0],
  text(weight: 700, fill: navy)[Long-term Habit], [Run approximately 4 km every day, regardless of weather; more than 1,600 km recorded across 2025–2026.],
)

#v(0.72em)
#link("https://mindscribe-app.pages.dev/")[
  #rect(width: 100%, inset: (x: 10pt, y: 8pt), radius: 3pt, fill: navy)[
    #grid(
      columns: (1fr, auto),
      [#text(size: 8.3pt, weight: 700, fill: white)[View product fieldwork, project videos, and the bilingual portfolio]],
      [#text(size: 8.3pt, weight: 700, fill: rgb("#8bb0ff"))[mindscribe-app.pages.dev →]],
    )
  ]
]

#v(0.75em)
#line(length: 100%, stroke: 0.6pt + rule)
#v(0.38em)
#align(center)[#text(size: 8pt, fill: muted)[Target roles: Smart Hardware Project Manager · Product Project Manager · Access Control / IoT / Robotics & Automation]]
