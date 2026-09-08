# 给 Manus 智能体的 MindScribe 续开发说明

## 首要目标

请把本项目视为**智能硬件项目经理的双语个人品牌作品集**，而不是普通简历模板。任何改动都应加强三个核心印象：能够进入软硬件技术现场，能够组织研发、测试、供应商和量产交付，能够以英语独立协同海外客户。

## 开始工作前

先阅读本目录的 `README.md` 与 `DESIGN_SYSTEM.md`，再查看 `source-snapshot/Home.tsx` 和 `source-snapshot/index.css`。不要从正式构建产物中的压缩 JavaScript 反向修改页面。网站开发源位于 WebDev 项目 `/home/ubuntu/lingji-resume`，正式部署仓库为 `/home/ubuntu/mindscribe-live-repo`。

## 内容规则

公司名称只写“得力集团”或“Deli Group”。不要恢复任何内部公司、部门或项目组名称。全英文硕士教学、CET-6/CET-4/IELTS、尼泊尔等海外客户对接、云深处四足机器人、四类智能硬件产品线和每日约四公里跑步均属于必须保留内容。

不要把团队项目写成个人独立完成。若来源资料没有拆分职责，应继续使用“团队项目”“个人边界未单独记录”等严谨表述。对量化数据进行修改前必须有用户材料或可追溯记录。

## 视觉决策

保留瑞士工程档案风格、海军蓝/皇家蓝/珊瑚橙/象牙白配色、Space Grotesk 数据标题、IBM Plex Sans 正文、纸张噪点和章节编号。不要改成紫色渐变、玻璃拟态、通用 SaaS 卡片或大面积圆角。Logo 必须使用原 MindScribe 像素图标，加载页使用原黄色状态图标。

页面允许增加新内容，但应优先扩展现有九个章节。只有当新内容具有独立叙事价值时才新增章节。照片属于证据而不是装饰；产品图优先完整展示，现场图优先展示真实情境。

## 双语与简历同步

所有新增网页文案必须同时提供中文和英文。语言切换后不应残留另一种语言。简历事实同时存在于 `Home.tsx`、Typst 和 Word 生成脚本中，修改后必须逐项同步。

PDF 必须保持中英文各两页 A4，包含证件照、Logo 和可点击正式网站链接。Word 也必须保持两页，并在 LibreOffice 或 Word 实际渲染后检查分页。不要仅通过 DOCX 文件大小判断成功。

## 发布方式

大媒体不得放进 WebDev 的 `client/public/`。先上传为 `/manus-storage/`，再运行交接目录中的 `deploy_mindscribe_frontend.py` 替换为正式 `/portfolio-assets/`。正式网站由 GitHub `main` 分支触发 Cloudflare Pages 自动部署。[1] [2]

每次替换简历时使用新的版本化 PDF 文件名，并同时更新网站素材映射与部署脚本。发布后至少验证首页、产品图、云深处视频和两份简历返回 HTTP 200。下载到本地后比较哈希，确认不是旧缓存。

## 完成定义

一次改动只有在以下条件同时成立时才算完成：TypeScript 检查通过；生产构建成功；桌面与移动端无溢出；中英文切换完整；两份 PDF 与 Word 均为两页；正式 Cloudflare 地址已经返回新内容；WebDev 保存了最终检查点；交接快照已更新。

## References

[1]: https://mindscribe-app.pages.dev/ "MindScribe 刘莫昕个人作品集"
[2]: https://github.com/Liu-design-beep/mindscribe-app "MindScribe GitHub 仓库"
