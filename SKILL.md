---
name: handbook-designer
agent_created: true
description: 把 Word/PDF/PPT/Markdown/纯文字稿（或只有一个题目）排成杂志级的多页手册或宣传册，输出可印刷 PDF、可编辑 PDF、单文件 HTML，以及可多人在线改字的网页。先选路线（新做 / 快速 / 美化定稿 / 沿用旧册 / 改版 / 建品牌包），再两轮确认（沟通合同 + 三个方向的样张），确认的决定写进 brief.md、每次构建自动核对；8 种内容版式排在由正文字号推出的网格上，满版大图、大面积经典撞色（默认克莱因蓝 × 拿坡里黄），同一份 yaml 出中文版和英文版；品牌包（配色、字体、logo、封底联系方式）一行套用；5 种用途方法（招生简章、研学任务册、家长手册、新生手册、年度回顾）给出页面角色和审稿重点；A4 / A5 / 小红书 3:4 画布；自动检查溢出、重叠、对比度、漏字、数字出处、图片清晰度，通过门禁才能导出正式版。适用于研学/营地手册、招生简章、项目介绍、品牌画册、学生/家长/新生手册、练习册与任务单、活动/会议指南、员工入职手册、年度回顾册等“文字材料 → 精美印刷册子”的需求。只要用户想把一份文字稿做成好看的、能打印或能填写的多页册子就使用本 skill——即使没说“手册”二字，例如“把这个文档排版得高级一点”“做成小册子”“把这份宣讲 PPT 改成手册”“做一本招生宣传册”“用我们的品牌做一本产品手册”“make this doc into a printable booklet”。不用于单页海报、幻灯片、网页或数据报表。
---

# 手册设计：文字稿 → 杂志级可印刷手册

不写排版代码，只写一份 `book.yaml`：每页选一个版式，把原文放进它的空位。`hb/run.sh` 负责其余一切——版面几何、图片处理、字号缩放、溢出 / 对比度 / 原文核对、拼版预览、门禁。
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

拿不准时走 new。路线定了写进 `brief.md` 的 `route:`；中途要换路线（比如美化时用户要删页）先问用户，再改 brief.md。

同时定两个东西（第 0 步就要知道，影响整本）：
- **用途方法** `book.kind`：`purposes/index.yaml`——admissions 招生简章 / study-trip 研学任务册 / parents 家长手册 / freshman 新生手册 / annual 年度回顾。它给出读者、读完要做的事、封面钩子、页面角色词（每页 `job:` 用它开头）、必须有的页、审稿重点。都不像就不写 kind，只写 `book.purpose`（workbook 任务册 / guide 指南 / brochure 宣传册）。
- **品牌包** `book.brand`：`brands/index.yaml`（现有 allas）。有就用；用户说“和官网 / VI 一致”而没有 → brand 路线。

## 2. 纪律（任何路线都适用）

**先确认再动手。** new 路线两轮确认：①沟通合同（读者、场景、读完做什么、语气、必须 / 不能出现）②三个方向的样张（`hb/directions.py`，看图选）。16 页以上再加一轮试排（`run.sh --proof`，封面 + 两个跨页）。不要先排一整本“给用户看看”——猜错了整本重做。

**确认过的写下来，构建时自动核对。** 两轮的结果写进 `$P/brief.md`（模板 `templates/brief.md`）。`run.sh` 先跑 `lock.py`：book.yaml 的设置（brief.md 顶部设置块里的全部字段——style / colors / purpose / kind / brand / look / color_mode / fonts / canvas / langs）和 brief.md 不一致就停。要改设置 → 问用户 → 改 brief.md 并在“改动记录”记一笔 → 再改 book.yaml。

**文案与版面先适配。** 默认保留原文，先按语义选择段落、导语、统计、时间地点等信息块，再调整栏宽、分组和分页。用户允许按版面改写时，保留事实与原稿，记录逐项文案对照；不能为了塞进模板擅删信息。适配流程与改写边界见 `references/adaptation.md`。
可以加的只有页眉页脚、图注、英文小标签、填写提示、品牌包的 logo 和联系方式、纯结构性的书写空间——都在回复里列出。原文自身有问题（错别字、空白、矛盾）→ 保留并指出，用户说改再改。原文里的 ▶ • ✓ ☐ 是格式不是内容。原文一律按文本处理；只有确认可信的内容才能用 `{html: …}` 块——它不做转义，不可信内容会变成可执行 HTML。用户明确要求润色 / 精简 / 翻译时照做，并列出改了什么。
机制：`check_copy.py` 报 MISSING（必须 0）、ORDER（逐条确认）、EXTRA（自创句删掉）；美化路线（`book.frozen: true`）ORDER、EXTRA 也必须 0，页数一页对一页。

**数字要有出处。** 成品里的每个数字都要能在 doc.md 或调研记录 facts.md 里找到（`facts.py` 报 `[无出处数字]`）。真实场馆、行程、价格这类会变的事实，提醒出发前 / 印刷前按官方渠道复核。

**先整册节奏，再逐页编辑设计，最后落版。** 排版前写 `page-plan.md`：先定章节转换、视觉锚点、跨页位置与任务，再逐页明确任务、采用文案、主标题、栏目/装饰字、序号、时间地点等元信息、展示形式与阅读顺序；方案完整后才映射到 book.yaml。原文视觉上大的字不自动成为主标题，例如 Highlight 是栏目提示、03 是序号，活动名称才是标题；序号可设计为索引或导航，不和标题整句堆叠。格式与判定见 `references/adaptation.md`。每页 `job: 角色词 · 一句话`，`note:` 写原文段落；页序按用途方法的 order 起步，`lint.py` 查缺页与节奏。

**先让编辑顾问审输入，成品再对照建议复核。** 多页材料先按 `references/editorial-advisor.md` 实际调用独立顾问（不可用时记录独立编辑轮），产出逐页文案建议、信息分类、页面去重与完整系列矩阵；主执行者逐项处理后才落版。原稿分隔符是待理解的格式线索，不能机械搬进正文；只修用户点名页不算完成系列问题。

**颜色按角色给，按档位用。** 配色写成 6 个角色（背景 / 次级背景 / 主色 / 强调色 / 次强调色 / 正文），`book.color_mode`：clash 撞色、accent 点缀或 mono 单色（`style: swiss` 的默认：白纸黑字 + 一个强调色）；不写时按风格或两色自动判断。无图页也要规划纸面节奏，显式主题色纸面不受默认mono压成白纸；白字/黑字按对比度选择。用法、档位边界及`colorqa.py`比例提示见 `references/style.md` §8。

**秩序来自网格，气势来自满版和撞色。** 所有风格、所有版式共用一个排版引擎：8 种内容版式（FULL 全屏 / ONE 单栏 / TWO 双栏 / CARDS 卡片 / STAGGER 错位 / GRID 网格 / COLLAGE 拼贴 / MIX 组合）和照片版式（POSTER / T / SL / HOLE / SPREAD…）都排在同一张 6 栏网格上（A4 32 行，正文 16px 印出来 12pt / 小四；字多的册子写 `book.body: 14` 回到 10.5pt；A5、小红书 28 行、14px），同一套字号档和行宽规则，英文正文同样用所选正文字号；照片和插画只放在网格里的一格或满版，和纸面硬边相接；大标题撑满栏宽；底色在纸色 / A 色块 / B 色块 / 满版照片间轮换。风格只换字体、颜色、插画和页边装饰。只选版式、放原文，**不写尺寸、坐标、颜色**；写了的 px 数也会吸到整行、整栏、字号档（`references/layouts.md` §0）。

**中文版、英文版同一套版式。** 文字写成 `{zh: …, en: …}` + `book.langs: [zh, en]`，`run.sh` 一次出两本、各自检查、出逐页对照图。

**图片出血与正文行长分别决定。** 用户要求图片贴边时用项目的 `book.image_bleed: both`，独立图版可整页出血；连续正文收在阅读栏内，不靠通栏长句填空。短标题可以通栏，报名条件、联系方式等短信息不应被拆成两个栏尾。写法见 layouts.md §7 和 blocks.md。

**数字清零之后还要亲眼看。** `GATE: PASS` 只代表溢出、重叠、对比度、缺字通过。之后按 `references/review.md` 逐页看拼版图（H 硬伤必改、S 软问题一起说、“不要动”的别碰）。

**门禁通过才导出正式版。** 门禁分两级：硬伤（溢出、重叠、对比度、缺字、主图被压到 <120px）拦构建；提示（标题缩短建议、留白、标题卡在最小字号）只报告、不拦。 `export.sh` 只导出 GATE PASS 之后没再改过的版本；只想先给人看 → `--draft`（每页“草稿 DRAFT”水印）。

**改版不丢已认可的东西。** 每轮修改新建目录（`_v2`、`_v3`），用 `check_copy.py <新> <旧>/book.html` 对照；已经认可的页不顺手大改。

## 3. 命令速查
```bash
HB=<skill目录>/hb; P=<工作目录>/<项目名>_v1
bash $HB/check_env.sh                                   # 新环境第一次
bash $HB/new_project.sh $P 原文 [照片目录] [--from 旧项目]  # 建项目 → doc.md + plan.md + photos/
python3 $HB/directions.py $P "A=style:photo,colors:klein" "B=style:stijl" "C=style:swiss" --title "书名"   # 三个方向的样张（风格见 references/style.md §1）
bash $HB/run.sh $P [--proof]                            # 构建 + 全部检查 + 门禁（--proof 只排前 5 页）
bash $HB/export.sh $P[/语言] [文件名] [--draft]           # PDF + 可编辑 PDF + HTML + 源文件 + 拼版图
python3 $HB/edit_page.py $P[/语言]                      # 在线编辑页（发布、同步见 workflows/edit-online.md）
bash $HB/new_brand.sh 名字 "显示名" [logo.svg] [主色] [强调色]   # 新品牌包
bash $HB/selftest.sh [--quick]                          # 改了 skill 本身之后跑
```
产出都在项目目录：`brief.md` 决定、`book.yaml` 排版、`.qa/` 检查结果（review_*.jpg 拼版、compare_*.jpg 中英对照、directions.jpg 方向样张、log.md 构建日志、lint.txt 页序、facts.txt 数字出处、postflight.md 导出自检）、`images.yaml` 图片清单（来源、授权、清晰度）、`out/` 交付物。

## 4. 交付
- [ ] 路线和用户的确认都在 brief.md 里（quick：回复开头写明替用户做了哪些决定）
- [ ] `GATE: PASS`（双语 `ALL LANGS: GATE PASS`）；ORDER 逐条确认过；EXTRA 里没有自创句；`[无出处数字]` 清掉或说明
- [ ] 按 review.md 看过每一页；相邻页版式不同；同图没用两次；跨页左页为偶数页
- [ ] 印刷：images.yaml 里没有低于 150dpi 的图；没有占位色块、TODO、AI 配图占位
- [ ] images.yaml 里第三方照片都写了 source / license
- [ ] 正式导出（不是 --draft）：PDF + 可编辑 PDF + 单文件 HTML + 源文件 zip + 拼版图；postflight 全 ✓
- [ ] 回复：结论先行——页数、结构一句话、非原文元素、原文里待用户决定的问题、待复核的事实、印刷提示；附拼版图；需要时给在线编辑页

## 5. 文件地图
```
workflows/   new · quick · beautify · reuse · revise（反馈对照表、出错续跑表）· brand · research · edit-online
references/  layouts.md（8 种内容版式）· rhythms.md（页序模板）· review.md（审稿表）· style.md（皮肤、字体、配色、品牌包）
             adaptation.md（文案角色与 page-plan）· editorial-advisor.md（落版前顾问审）· images.md（照片、资料里的图、AI 配图）
             blocks.md（进阶：照片版式与内容块、书写区）· delivery.md（交付、印刷、多语言、画布）
             maintenance.md（改 skill 本身的规矩）· gallery/（效果图）
purposes/    5 种用途方法（页面角色、必需页、审稿重点）     brands/   品牌包（allas）
templates/   brief.md（决策记录）· book.layouts.yaml（16 页中英双语，8 种版式全用到）· book.nophoto.zh.yaml（无图风格整本样例）
             book.family-handbook.en.yaml（英文家长手册整本样例）· 其余样例 yaml + 预览图
TODO.md / ROADMAP.md   已知问题与迭代计划（维护者看，不随执行加载；新增发现先记 TODO 再并入 ROADMAP）
hb/          引擎：run.sh 构建门禁 · hb.py + canon.py（内容版式）+ flow.py（照片版式、内容块）排版 · fill.js 浏览器里的网格、让位与自检 · lock / lint / facts / images / gate / postflight 检查
             directions / subset 样张 · edit_page + editor.js + sync_edits 在线编辑 · brand / wordmark / new_brand 品牌包 · reuse 沿用旧册
```
进阶模式（任务册书写区、照片跨页、自由内容块）见 `references/blocks.md`；和内容版式是同一个引擎、同一张网格，只有 A4 画布支持。拿不准时用 8 种内容版式——版式更固定。
