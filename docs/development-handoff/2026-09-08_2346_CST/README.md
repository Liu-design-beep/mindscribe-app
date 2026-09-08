# MindScribe 简历作品集开发交接档案

**归档时间：2026-09-08 23:46（CST）**

本目录记录 MindScribe 从智能笔记产品实验重构为刘莫昕双语简历与工程项目作品集后的当前设计、内容边界、源文件和发布流程。目标是让下一次开发能够直接延续，而不是重新猜测品牌、视觉和部署结构。

## 当前状态

正式网站为 [MindScribe 刘莫昕个人作品集][1]。网站定位是**智能硬件项目经理的双语个人品牌页面**，同时保留 MindScribe 原始 Logo、加载图标和个人 AI 产品经理故事。网站包含中英文完整切换、项目分类、项目详情弹窗、项目视频、产品与项目现场实拍、跑步档案和双语简历下载。

公司信息已按用户要求简化。网站、PDF 和 Word 中只允许出现“得力集团”或“Deli Group”，不得出现内部公司、部门或项目组名称。

## 目录说明

| 路径 | 内容 | 使用方式 |
|---|---|---|
| `source-snapshot/` | 当前 React 页面、全局 CSS 与 HTML 入口快照 | 用于比较和恢复前端视觉结构 |
| `resume-source/` | 中英文 Typst 简历、主题文件、证件照与 Logo | 用于重新生成正式 PDF |
| `scripts/deploy_mindscribe_frontend.py` | 将 WebDev 构建同步为 Cloudflare Pages 静态产物 | 发布前执行并检查未解析素材路径 |
| `scripts/generate_resume_docx.py` | 生成两份可编辑 Word 简历 | 内容变更后重新生成并用 LibreOffice 检查分页 |
| `DESIGN_SYSTEM.md` | 品牌、视觉、布局、响应式与交互规范 | 前端改动前阅读 |
| `MANUS_AGENT_DESIGN_NOTES.md` | 专供 Manus 智能体续开发的执行说明 | 新任务开始时优先阅读 |

## 单一事实源与同步规则

网站双语文案目前集中在 `Home.tsx` 的 `copy.zh` 与 `copy.en`。PDF 简历分别由 `resume-cn.typ` 与 `resume-en.typ` 管理。Word 简历由生成脚本中的中英文数据生成。任何事实修改必须同时更新三处，并检查中英文数字、日期、公司名称和个人职责一致。

媒体文件在 WebDev 中使用 `/manus-storage/` 地址。正式 Cloudflare Pages 产物由部署脚本将这些地址替换为 `/portfolio-assets/`。不得直接把大图片或视频加入 WebDev 的 `client/public/`。

## 发布与验证顺序

1. 更新网站、Typst 和 Word 内容。
2. 运行 TypeScript 检查与 Vite 生产构建。
3. 严格编译两份 Typst PDF，并验证均为两页 A4、图片可读、网页链接可点击。
4. 生成两份 Word，并用 LibreOffice 转成 PDF 验证实际分页为两页。
5. 为 PDF 使用新的版本化文件名，避免浏览器和 Cloudflare 缓存旧文件。
6. 运行部署脚本，确认正式产物中不存在 `/manus-storage/` 未替换路径。
7. 提交并推送 `main` 分支，等待 Cloudflare Pages 自动部署。
8. 在正式网址验证首页、项目视频、关键图片和两份简历均返回 HTTP 200。

## 不应破坏的内容

不得丢失全英文硕士教学背景、CET/IELTS 信息、英语工作能力、尼泊尔等海外客户协同、智能硬件项目经理定位、四类产品线、云深处机器人项目、每日约四公里跑步习惯，以及 MindScribe 个人 AI 产品构想。项目经历中的来源边界必须保留；没有证据时不能把团队项目改写成个人独立完成。

## References

[1]: https://mindscribe-app.pages.dev/ "MindScribe 刘莫昕个人作品集"
[2]: https://github.com/Liu-design-beep/mindscribe-app "MindScribe GitHub 仓库"
