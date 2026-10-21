---
name: handbook-designer
agent_created: true
description: 将 Word、PDF、PPT、Markdown 或文字材料做成多页手册、宣传册、品牌画册、指南或任务册，也支持旧册改版与品牌适配。先组织文案角色、图文关系和整册节奏，再用统一 HTML 排版引擎生成 PDF、可编辑 PDF、单文件 HTML 与源文件，检查内容、版面和实际导出。用户说“小册子”“把 PPT 改成手册”“把文档排得高级一点”时适用；不用于幻灯片、单页海报、网站或数据报表。
---

# 手册设计：文字稿 → 杂志级可印刷手册

先确定每页的信息角色和展示方案，再把方案映射到一份 `book.yaml`；版式是实现手段，不是填空题。先读 `references/composition.md`，用统一网格设计阅读入口、停顿、主文与图像关系；layout 管结构，style/colors 管主题，typography 管字重阶梯，fonts 管字体家族，项目管整册节奏。`hb/run.sh` 负责版面几何、图片处理、字号缩放、自动检查和预览；内容判断与视觉审稿仍由执行者完成。
这个文件只管两件事：**走哪条路线**，和**任何路线都不能破的纪律**。具体步骤在 `workflows/`，写法和参数在 `references/`，用到时再读。

## 1. 先选路线（读对应的 workflows 文件，照它做）
| 用户的情况 | 路线 | 读 |
|---|---|---|
| 给了原文，要一本新册子（默认） | new | `workflows/new.md` |
| “直接做 / 不用问 / 先出一版”，或无人值守的任务 | quick | `workflows/quick.md` |
| 定稿的 PPT / PDF / Word，“排好看点、不要改内容” | beautify | `workflows/beautify.md` |
| “照去年那本做”“和上一期一样” | reuse | `workflows/reuse.md` |
| 已有成品，用户提修改意见；或上次做到一半断了 | revise | `workflows/revise.md` |
| “用我们的品牌”且 brands/ 里没有；或要建品牌规范 | brand | `workflows/brand.md`，然后回到 new |
| 只有题目、没有原文（或原文缺关键事实） | new + 调研 | `workflows/research.md`，然后回到 new |
| 用户想自己改字 / 换图 / 多人看稿 | 在线编辑 | `workflows/edit-online.md` |

拿不准时走 new。路线定了写进 `brief.md` 的 `route:`；中途换路线或设置时沿用已有授权，用户已明确要求的改动直接记录，只有缺少影响结果的决定才询问。

同时定两个东西（第 0 步就要知道，影响整本）：
- **用途方法** `book.kind`：`purposes/index.yaml`——admissions 招生简章 / study-trip 研学任务册 / parents 家长手册 / freshman 新生手册 / annual 年度回顾。它给出读者、读完要做的事、封面钩子、页面角色词（每页 `job:` 用它开头）、必须有的页、审稿重点。都不像就不写 kind，只写 `book.purpose`（workbook 任务册 / guide 指南 / brochure 宣传册）。
- **品牌包** `book.brand`：`brands/index.yaml`（含虚构示例 `acme`）。有对应品牌包就用；用户说“和官网 / VI 一致”而没有 → brand 路线。

## 2. 纪律（任何路线都适用）

**先确认再动手。** new 路线两轮确认：①沟通合同（读者、场景、读完做什么、语气、必须 / 不能出现）②三个方向的样张（`hb/directions.py`，看图选）。16 页以上再加一轮试排（`run.sh --proof`，封面 + 两个跨页）。不要先排一整本“给用户看看”——猜错了整本重做。

**确认过的写下来，构建时自动核对。** 两轮的结果写进 `$P/brief.md`（模板 `templates/brief.md`）。`run.sh` 先跑 `lock.py`：book.yaml 的设置（style / colors / purpose / kind / brand / look / color_mode / typography / display_weight / fonts / canvas / langs）和 brief.md 不一致就停。设置变更先核已有授权 → 改 brief.md 并记一笔 → 再改 book.yaml；不重复确认用户刚提出的要求。

**原文为准，按产物适配。** 事实、数字、措辞以用户给的稿子为准，但稿子是为 Word / 幻灯片写的，不是为册子写的，不一句不差搬进来：编号标签（「亮点一：高端品质」只留冒号后的标题）、备注批注、版本记录这类不是给读者看的，默认不印，在项目的 `adapt.yaml` 里声明，适配报告交付时列给用户；读者要用的序号（步骤一、Day 3）和「标签：值」照留。改措辞、合并压缩句子才需要用户授权，记录逐项文案对照；不能为了塞进模板擅删信息。先按语义选信息块，再调栏宽、分组和分页。流程与边界见 `references/adaptation.md`。
可以加的只有页眉页脚、图注、英文小标签、填写提示、品牌包的 logo 和联系方式、纯结构性的书写空间——都在回复里列出。原文自身有问题（错别字、空白、矛盾）→ 保留并指出，用户说改再改。原文里的 ▶ • ✓ ☐ 是格式不是内容。原文一律按文本处理；只有确认可信的内容才能用 `{html: …}` 块——它不做转义，不可信内容会变成可执行 HTML。用户明确要求润色 / 精简 / 翻译时照做，并列出改了什么。
机制：`check_copy.py` 报 MISSING（必须 0；`adapt.yaml` 声明过的去前缀 / 省略不算，明细在 `.qa/adapt-report.md`）、ORDER（逐条确认）、EXTRA（自创句删掉）；美化路线（`book.frozen: true`）ORDER、EXTRA 也必须 0，页数一页对一页，且不许用 `adapt.yaml`。

**数字要有出处。** 成品里的每个数字都要能在 doc.md 或调研记录 facts.md 里找到（`facts.py` 报 `[无出处数字]`）。真实场馆、行程、价格这类会变的事实，提醒出发前 / 印刷前按官方渠道复核。

**先整册节奏，再逐页编辑设计，最后落版。** 排版前写 `page-plan.md`：先定章节转换、视觉锚点、跨页位置与任务，再逐页明确任务、采用文案、主标题、栏目/装饰字、序号、时间地点等元信息、展示形式与阅读顺序；方案完整后才映射到 book.yaml。原文视觉上大的字不自动成为主标题，例如 Highlight 是栏目提示、03 是序号，活动名称才是标题；序号可设计为索引或导航，不和标题整句堆叠。格式与判定见 `references/adaptation.md`。每页 `job: 角色词 · 一句话`，`note:` 写原文段落；页序按用途方法的 order 起步，`lint.py` 查缺页与节奏。

**先让编辑顾问审输入，成品再对照建议复核。** 多页材料先按 `references/editorial-advisor.md` 实际调用独立顾问（不可用时记录独立编辑轮），产出逐页文案建议、信息分类、页面去重与完整系列矩阵；主执行者逐项处理后才落版。原稿分隔符是待理解的格式线索，不能机械搬进正文；只修用户点名页不算完成系列问题。

**四主题、两排印、两基础字体。** 当前维护 Photo（photo）、Swiss Minimal（swiss）、Editorial（editorial）、风格派（stijl）。`book.typography: bold / light` 是四主题共享的字重阶梯；默认全部使用思源黑体/宋体，Inter等只作按需扩展。Swiss 去掉撞色，Editorial 采用暖纸、宋体阅读、黑体功能信息与克制图像。可选真实100大标题的字体边界、用色与字重规则见 `references/style.md`。摄影铺满、出血、多图与跨页的偏好由 `references/composition.md` 统一管理，四主题共享。

**可选扩展：品牌图形延展。** 品牌识别重要且有合适源标志时，可从其结构发展暗纹、角部构图、章节锚点或跨页超级图形，增强全册识别与内容呼应。按 `references/style.md` §7.1 先写应用方案，再用既有brand_graphic矢量层落版；启用范围留在本项目，不默认每页贴logo。

**秩序来自网格，层级来自排印和图文比例。** 所有风格、所有版式共用一个排版引擎：8 种基础内容版式（FULL 全屏 / ONE 单栏 / TWO 双栏 / CARDS 卡片 / STAGGER 错位 / GRID 网格 / COLLAGE 拼贴 / MIX 组合）、8 种编辑变奏和照片版式（POSTER / T / SL / HOLE / SPREAD…）都排在同一张 6 栏网格上（A4 32 行，正文 16px 印出来 12pt / 小四；字多的册子写 `book.body: 14` 回到 10.5pt；A5、小红书 28 行、14px），同一套字号档和行宽规则，英文正文同样用所选正文字号；照片和插画只放在网格里的一格或满版，边落在行线上（photo 风格淡进半透明纸面，其余硬边）；大标题撑满栏宽；纸面与照片按阅读任务组织，不机械轮换大色块。风格只换字体、颜色、插画和页边装饰。只选版式、放原文，**不写尺寸、坐标、颜色**；写了的 px 数也会吸到整行、整栏、字号档（`references/layouts.md` §0）。

**中文版、英文版同一套版式。** 文字写成 `{zh: …, en: …}` + `book.langs: [zh, en]`，`run.sh` 一次出两本、各自检查、出逐页对照图。

**图片出血与正文行长分别决定。** 用户要求图片贴边时用项目的 `book.image_bleed: both`，独立图版可整页出血；连续正文收在阅读栏内，不靠通栏长句填空。短标题可以通栏，报名条件、联系方式等短信息不应被拆成两个栏尾。写法见 layouts.md §7 和 blocks.md。

**落版后由视觉排版总监逐页审改。** 所有路线收尾执行 `workflows/visual-review.md`：按 `references/review.md` 看整册、逐页及真实面对页，给具体修改、实际改源、重建重导，再核新PDF直到本轮必改项关闭。前置编辑顾问与后置视觉审核分工；`GATE: PASS`不能替代视觉验收，报告已写也不代表修改完成。

**门禁通过才导出正式版。** 门禁分两级：硬伤（溢出、重叠、对比度、缺字、主图被压到 <120px）拦构建；提示（标题缩短建议、留白、标题卡在最小字号）只报告、不拦。 `export.sh` 只导出 GATE PASS 之后没再改过的版本；只想先给人看 → `--draft`（每页“草稿 DRAFT”水印）。

**改版不丢已认可的东西。** 每轮修改新建目录（`_v2`、`_v3`），用 `check_copy.py <新> <旧>/book.html` 对照；已经认可的页不顺手大改。
修订范围按反馈涉及的规则确定：同系列、相邻面对页及整册引用的连带复核见 `references/adaptation.md`；保留无关已认可页，不等于只修被截图的一页。

## 3. 命令速查
```bash
HB=<skill目录>/hb; P=<工作目录>/<项目名>_v1
bash $HB/check_env.sh                                   # 新环境第一次
bash $HB/new_project.sh $P 原文 [照片目录] [--from 旧项目]  # 建项目 → doc.md + plan.md + copy_map.md + page-plan.md 骨架 + photos/
python3 $HB/directions.py $P "A=style:photo,colors:nature" "B=style:swiss,colors:swiss" "C=style:editorial,colors:ink" --title "书名"   # 三个方向的样张（风格见 references/style.md §1）
bash $HB/run.sh $P [--proof]                            # 构建 + 全部检查 + 门禁（--proof 只排前 5 页）
bash $HB/export.sh $P[/语言] [文件名] [--draft]           # PDF + 可编辑 PDF + HTML + 源文件 + 拼版图
python3 $HB/edit_page.py $P[/语言]                      # 在线编辑页（发布、同步见 workflows/edit-online.md）
bash $HB/new_brand.sh 名字 "显示名" [logo.svg] [主色] [强调色]   # 新品牌包
bash <skill目录>/dev/tests/selftest.sh [--quick]         # 改了 skill 本身之后跑（位于 dev/ 开发包）
```
产出都在项目目录：`brief.md` 决定、`book.yaml` 排版、`.qa/` 检查结果（review_*.jpg 拼版、compare_*.jpg 中英对照、directions.jpg 方向样张、log.md 构建日志、lint.txt 页序、facts.txt 数字出处、postflight.md 导出自检）、`images.yaml` 图片清单（来源、授权、清晰度）、`out/` 交付物。

## 4. 交付
- [ ] 路线和用户的确认都在 brief.md 里（quick：回复开头写明替用户做了哪些决定）
- [ ] `GATE: PASS`（双语 `ALL LANGS: GATE PASS`）；ORDER 逐条确认过；EXTRA 里没有自创句；`[无出处数字]` 清掉或说明
- [ ] 已按 visual-review 工作流审改实际PDF，逐页/面对页覆盖与必改项复核记在 .qa/visual-review.md；整册节奏及系列、跨页一致
- [ ] 印刷：images.yaml 里没有低于 150dpi 的图；没有占位色块、TODO、AI 配图占位
- [ ] 版权与授权：images.yaml 里所有照片都核对了 source / license（原稿抽取照片也须提醒用户确认商用版权与人物肖像权）
- [ ] 正式导出（不是 --draft）：PDF + 可编辑 PDF + 单文件 HTML + 源文件 zip + 拼版图；postflight 全 ✓
- [ ] 回复：结论先行——页数、结构一句话、非原文元素、原文里待用户决定的问题、待复核的事实、版权与印刷提示；附拼版图；需要时给在线编辑页

## 5. 文件地图
```
workflows/   new · quick · beautify · reuse · revise（反馈对照表、出错续跑表）· brand · research · edit-online
             visual-review（所有路线收尾：视觉总监逐页审改、重导复核）
references/  layouts.md（8 种基础版式 + 8 种编辑变奏）· composition.md（统一网格、主题分层与阅读节奏）
             rhythms.md（页序起点）· review.md（审稿表）· style.md（主题、字体、配色、品牌包）
             adaptation.md（文案角色与 page-plan）· editorial-advisor.md（落版前顾问审）· images.md（照片、版权授权、AI 配图）
             blocks.md（进阶：照片版式与内容块、书写区）· delivery.md（交付、印刷、多语言、画布）
purposes/    5 种用途方法（页面角色、必需页、审稿重点）     brands/   品牌包（示例 acme）
templates/   brief.md（决策记录）· book.layouts.yaml（16 页中英双语，8 种版式全用到）· book.nophoto.zh.yaml（无图风格整本样例）
             book.family-handbook.en.yaml（英文家长手册样例）· book.brochure.zh.yaml（宣传册样例）· book.study-trip.zh.yaml（研学手册样例）
hb/          引擎：run.sh 构建门禁 · hb.py + canon.py（内容版式）+ flow.py（照片版式、内容块）排版 · fill.js 浏览器里的网格、让位与自检 · lock / lint / facts / images / gate / postflight 检查
             directions / subset 样张 · edit_page + editor.js + sync_edits 在线编辑 · brand / wordmark / new_brand 品牌包 · reuse 沿用旧册
dev/         仓库开发与预览资源（与纯 Skill 运行文件分离）：maintenance.md 维护规矩 · tests/ 自测与合成图脚本 · gallery/ 风格效果图 · previews/ 模板预览图 · audits/ 历史复盘与迭代计划
```
进阶模式（任务册书写区、照片跨页、自由内容块）见 `references/blocks.md`；和内容版式是同一个引擎、同一张网格，只有 A4 画布支持。按阅读任务选版式：叙述与停顿用 RHYTHM，正文与边注用 MARGINALIA，图解用 PLATE，多图叙事用 SEQUENCE，图片开场用 PHOTO_OPEN，连续长文与续页用 READING；清单和查阅仍用基础版式。编辑变奏样册见 `templates/book.editorial.zh.yaml`，双语连续阅读见 `templates/book.reading.yaml`。
