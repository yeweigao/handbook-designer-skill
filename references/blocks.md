# 进阶模式速查（book 设置 · 照片版式 layout · 内容块 block · 容量预算 · 图片）

标准模式（8 种内容版式）见 layouts.md；这里是照片版式 + 自由内容块，用于任务册书写区、照片跨页和内容版式给不了的组合。两种模式可以混用。每个版式长什么样见 `dev/gallery/<LAYOUT>.jpg`；完整可运行的样例见 `templates/`。

**和内容版式是同一个引擎**（`hb/flow.py` + `hb/canon.py` + `hb/fill.js`）：同一张 6 栏 × 28px 行线的网格、同一套行宽规则、同一个放不下时的处理顺序（layouts.md §0）。所以这里写的 px 数值（`h`、`size`、`mt`、`space`、`fill`、`kw`、`split`、`strip`、`body_top`、窗口 `size`）都**不是精确尺寸，会吸到最近的整行、整栏或字号档**——写个大概就行，表里的数是默认值。

组件控制样张：`dev/gallery/timeline_axis.jpg`（连续五天时间轴）、`dev/gallery/spread_bottom.jpg`（下部共享跨页图框；使用程序生成的控制图，无第三方照片）。

章节语义：章节起页可写`chapter: '03'`（跨页写在对应`left/right`内）；FULL的`index`自动作为章号。它把章节传到PDF书签，不代替可见编号。若用`book.series.chapters.items`登记完整章节，引擎核对起页章号的顺序与完整性；合并后的章扉可复用`series_header`显示CHAPTER、03和章名。装订页数约束见delivery.md。

## 0. book 设置
```yaml
book:
  title: 手册标题            # HTML <title>
  folio: 页脚左侧文字         # 默认 = title
  photos: photos             # 图片目录（相对项目目录）
  purpose: workbook          # workbook 任务册（有书写区）/ guide 指南（以读为主）/ brochure 宣传册（无书写区）
  style: photo               # 视觉风格：photo（默认）/ swiss / editorial / stijl / geo，见 style.md
  typography: bold          # bold 厚重 / light 轻盈，五种主题共享
  fonts: magazine            # 字体方案：magazine / swiss，或按角色覆盖，或按角色指定，见 style.md
  lang: zh                   # zh / ja / ko = 中日韩排版；en / fr / … = 西文排版（收紧字距、左对齐、正文用西文字体）
  scale: 2                   # 图片烘焙倍率：2 ≈ 190dpi（屏幕/打样），3 ≈ 290dpi（交印刷厂，构建更慢）
  colors: nature              # 可选：配色方案名（见 style.md §3），或颜色键 {G: '#1D5A43', GOLD: …}，或 {preset: nature, G: '#…'}
pages:
  - {layout: ..., ...}
```
`paper: 0.9`：photo 风格里照片淡进的半透明纸面有多不透明（0.86 通透 … 0.94 更易读）；`edge: hard` 改成不透明纸面 + 硬边。其他风格的纸面一律不透明、和画面硬边相接。

## 1. 版式 layout（每页一个；跨页类占 2 页，必须从**偶数页**开始）
除 PAPER 外，各版式都有一个“图片位”：photo 风格必须写 `image`（或 `image: placeholder` 占位）；无图风格不写 `image` 就在这一格里画风格插画（瑞士、孟菲斯、风格派是一块安静的色块）。

| layout | 页数 | 必填 | 可选参数 | 文字区 | 适合 |
|---|---|---|---|---|---|
| PAPER | 1 | — | header, body_top | body（6 栏整宽） | 没有合适照片的页：规章、日程表、通讯录、附录、笔记页、签署页 |
| POSTER | 1 | image* | focus, target, zoom, header, fig, folio:false | top、bottom 里的块会被归到封面的空位（见下） | 封面、致辞/欢迎信、章节扉页、尾页、封底 |
| T / B | 1 | image* | T: split(330) 或 photo_rows(9), body_top；B: split(760) 或 photo_rows(24)；focus, target, zoom | T: on_photo（白字，贴照片下沿）+ body（纸面）；B: body 在上 + on_photo 在下 | 带主题图的内容页、任务页、评价页、成果页 |
| SL / SR | 1 | image* | strip(270)：≥ 340 时照片占 3 栏，否则 2 栏 | body（其余几栏） | 长清单、长任务单、表单 |
| HOLE | 1 | image* | window: tr/tl/br/bl, size:[300,250]（= 2–3 栏 × 5–18 行） | beside（窗旁边几栏）、body（窗下/上整宽；beside 写长了 body 自动往下让） | 目标、要点、实验、安全须知 |
| SPREAD_P | 2 | image*(横图) | target | left/right 各自 {header, top, bottom, fig} | 总览｜公约、章节扉页、目录式大图 |
| SPREAD_H | 2 | image*(横图) | body_top(548) | left{header,on_photo,body}、right{header,on_photo(自动贴照片底),body} | 一个单元（一天/一章/一个模块）的主力页：上半图+标题+要点，下半写/读 |
| SPREAD_H（下部主图） | 2 | image*(横图)、image_position: bottom | split(564) | left/right各自body | 上部两页联合编辑，下部一张照片连续贯穿纸边与中缝；适合合照，文字不盖人脸 |
| SPREAD_OPENER | 2 | image*(横图) | right_layout: SL 或 T | left{header,top,bottom,fig}、right{header,body,(T 时 on_photo, body_top)} | 章节开篇 + 第一页内容 |

- **照片和纸面的交界落在行线上**（T/B、SPREAD_H 的 split / body_top 吸到最近的行线；侧条的内沿在栏间中线上）。photo 风格在这里用约 1.5 行淡进半透明纸面（国家地理式），其他风格是硬边。深色字只写在纸面上，照片上只放 on_photo 的白字，字下面自动压暗。浅色插画上写字时，插画停在文字上方一行，下面垫一块纸。
- **POSTER = 内容版式的 FULL**：`top` / `bottom` 里的 kicker → 小标签，短的 display（`01`、`Day 1`、`第一章`）→ 章节号，第一个 title / 长 display → 书名，en → 副题，p / letter → 导语和正文，stats → 关键数字；figure / gallery 不跟着文字走，放进网格里的一格（切口一侧三栏、从第 1 行起；图组占满六栏）；其余块排在书名下面。文字超过 ~220 字的非封面页自动排成“照片在上 + 单栏正文”（ONE）。旧写法的 `top_y`、`bottom_y` 不再需要。
- `header: [左, 右]` 页眉（英文小字或中英混排都可）；`fig: Fig. 01 · 图注` 图片说明。
- `focus:[x,y]`（0–1）= 图片里的哪个点；`target:[px,py]` = 放到页面哪个像素（单页宽 794、跨页宽 1588、高 1123）。主体被字压住 → 改 focus/target。
- 网格（A4）：页面 794×1123px，6 栏（栏宽 80、栏间 32），订口 50 / 切口 104，版心从 y=88 起 32 行、行距 28；左右页镜像。页眉在版心上方、页脚在版心下方，引擎自动放。
- `note:` 可写在任何页上（不渲染），用来记“这页对应原文哪一段”。
- `align: bottom`（PAPER、SL/SR）：文字区贴版心下沿。有书写线 / `fill` / `grow` 的文字区是定高的竖排区，`fill` 吃掉剩下的高度；其余文字区顶部对齐、块之间隔整行，不再把块均匀拉散（旧写法的 `align: spread` 等于不写）。
- \* 无图风格（style 不是 photo）里可以不写 image；写了就用照片。
- `image: placeholder`：photo 风格下还没有照片时的占位。T/B、跨页是主题色深色渐变；侧条、开窗是撞色色块 + 大号编号；POSTER 自动排成字体海报。可写 `placeholder_cover` 这类名字，方便在回复里对应拍摄清单。照片到了改成文件名，重跑一次 QA（真实照片的明暗会变）。
- 照片构图：图片会先按“铺满”缩放。横图比页面更宽时只能左右移，比页面更方时只能上下移；想往另一个方向移动主体，先 `zoom: 1.2–1.5` 放大留出余量，再调 focus/target。

## 2. 内容块 block（列表里的每一项；由“类型键”决定是哪种块，其余键是参数）
块与块之间自动隔 1 行（引语、卡片 2 行；小标签和它标注的标题之间不隔）。`mt:` 改间距，按整行算。

| block | 写法 | 说明 |
|---|---|---|
| 系列页头 | `{series_header: {series: highlights, item: '01'}}` | 栏目、序号、主标题共用一个组件；标题从book.series登记读取，不在单页覆盖。续页加continuation: true，可另给title说明本页任务；compact: true 为侧栏排法，READING 自动使用（layouts.md §8） |
| 大字 | `{display: 标题, size: 56, color: gold, stroke: 1.2, gradient: energy}` | 海报标题、单元编号（Day 1 / Unit 3 / 第一章）。size 吸到 23 · 33 · 47 · 56 · 72 · 96 · 120 · 160（和网格字号同一套档） |
| 标题 | `{title: 页标题, kicker: Small Label, sub: 斜体副题, size: 34}` | 纸面上的页标题：默认 47px 档；size ≤ 30 → 33px 档，≥ 52 → 展示大字 |
| 英文副题 | `{en: A Letter Before Takeoff}` | 斜体 |
| 小标签 | `{kicker: Key Facts · 核心知识点}` | 大写小字，用来分区 |
| 段落 | `{p: 原文, lead: 引导词：, size: 18, weight: 700}` | lead 为加粗引导词；size ≥ 18 → 23px 导语档（只在 ≥ 4 栏宽的栏里）；可内联 `<b>` `<br>` |

> 所有文字都会做 HTML 转义（原文里的 `<`、`&` 原样显示），只放行不带属性的 `<b> <strong> <i> <em> <u> <br> <sup> <sub> <small>`。需要其他 HTML 时用 `{html: ...}` 块，且只放你自己写的可信内容。

| block | 写法 | 说明 |
|---|---|---|
| 书信 | `{letter: [段1, 段2], sign: '署名 · 机构'}` | 致辞页（≥ 4 栏宽时用 23px 导语档）；`sign` 是独立小字号落款，吸在正文下方，不占 letter 行距 |
| 阅读流向 | `{p: '一段连续正文', flow: keep}` / `flow: columns` | p/letter 默认auto；keep保留同一阅读块，仍自然换行；columns明确两栏；统计与时间地点先按 adaptation.md 组织 |
| 连续时间轴 | `{timeline: [[D1, 'Fri · Arrival', 'Evening\n活动说明'], [D2, 'Sat · Session', '活动说明']], style: axis, next: 'D3 →'}` | 日期/星期或主题/说明是三层；竖轴、节点和大号日期统一。跨页使用相同组件和栏宽；next是可选导航提示 |
| 清单 | `{items: [..], heading: 小标题, style: big}` | 原文的项目符号列表；style:big 为大号编号（窄栏里条目回到正文字号） |
| 键值 | `{kv: [[左, 右], …], kw: 90}` | 日程、时间表、联系方式、术语表；kw 吸到整栏 |
| 任务大标题 | `{task: A, name: 任务名, sub: 副题}` | 大号字母/编号 + 标题 |
| 编号步骤 | `{step: 1, lead: 引导词, text: 原文, write: [块…], grow: true}` | write 里放书写区；grow 让它吃掉剩余高度；lead 后自动加冒号（原文自带冒号不会重复） |
| 问答 | `{q: 1, text: 原文问题, write: [{fill: 64}]}` | 默认自动铺线 |
| 工作单标签 | `{worksheet: 名称}` | 显示为 “Worksheet · 名称” |
| 填写栏 | `{field: 标签}` / `{fields: [A, B], cols: 1fr 2fr}` | 标签 + 下划线 |
| 书写线 | `{lines: 3}` | 每行 28px（一行网格）；页面放不下时第 2 行起可以被收掉，每组至少留 1 行 |
| 自动铺线 | `{fill: 64}` | 占满剩余空间，最小高度按整行算 |
| 方框 | `{box: 提示, h: 140}` / `{boxes: [1, 2, 3], h: 110}` | 画图、贴照片/贴纸、粘票据；h 吸到整行 |
| 圈选 | `{choice: 提示（圈出）, options: [甲, 乙, 丙]}` | 代替 ☐ 方框的单选/多选、自评等级 |
| 表格 | `{table: ['', 列1, 列2], widths: 24px 1fr 1fr, rows: ['1','2','3'], lines: 1}` | 第一列为行名；lines = 每行几条书写线 |
| 姓名栏 | `{blanks: [姓名, 班级], w: 180}` | 封面/扉页一行式填写 |
| 签名 | `{sign: 声明文字, label: 签名}` | 声明 + 签名线（声明很长时改用 p + fields） |
| 多栏 | `{cols: [[块…], [块…]], widths: 1fr 1fr}` | 一栏一组块，栏间 = 网格栏间 |
| 空白 | `{space: 28}` | 按整行算；页面放不下时先被收掉 |
| 原始 HTML | `{html: '<div>…</div>'}` | 最后手段（翻译时需手工处理） |

### 2.1 图片与宣传块（宣传册、指南常用；任务册里也能用）
| block | 写法 | 说明 |
|---|---|---|
| 插图 | `{figure: a.jpg, h: 220, fit: cover, focus: [.5, .4], caption: 图注, frame: true}` | 纸面上的图（照片在 `photos/`），宽 = 所在栏宽，h 吸到整行。`fit: contain` 不裁切（截图、图表、logo 必须用）；`frame: true` 加白底细框（截图）。图注算“装饰”，不进原文核对。页面放不下时图先按整行缩矮（最多到一半左右） |
| 图组 | `{gallery: [a.jpg, b.jpg, c.jpg], h: 160, captions: [甲, 乙, 丙], widths: 2fr 1fr 1fr}` | 一行 2–4 张，栏间 = 网格栏间；现场照片、作品、校园一角 |
| 关键数字 | `{stats: [['12', 年办学], ['3000+', 名学员]], size: 56, cols: 4}` | 大号数字 + 说明，数字要加引号（避免 YAML 当数字）；size 吸到 47 · 56 · 72 |
| 亮点卡片 | `{cards: [[标题, 说明], [标题, 说明]], cols: 2, num: true}` | 项目亮点、课程特色、常见问题；`num` 加 01 02 编号 |
| 引语 | `{quote: 引语原文, by: 署名}` | 学员说、校长寄语、家长反馈。原文自带的引号会去掉、“——署名”会自动拆到 by |
| 二维码 | `{qr: 'https://…', caption: 扫码报名, size: 104}` | 矢量二维码，永远深色码 + 白底（反色码很多手机扫不出）。需要 `pip install qrcode`；没有时把二维码图片放进 photos 用 figure |
| 对比条形图 | `{bars: [['识别正确率', 85, 50], …], series: [本产品, 通用方案], unit: '%'}` | 我方 vs 对照的指标对比（实测、调研） |
| 产品卡 | `{product: 名称, text: 说明, image: a.png, tag: 主推, h: 200, fit: contain}` | 图区 + 标签 + 名称 + 说明；两三张并排用 `cols` |
| 胶囊标签 | `{chips: [L1 集团, L2 学校, L3 课堂, L4 家庭], on: 2}` | 层级/分类导航，`on` 高亮第几个 |
| 循环图 | `{cycle: [[L3, 课堂], [L1, 集团], [L2, 学校], [L4, 家庭]], center: 越用越聪明, size: 300}` | 飞轮、闭环；节点文字算装饰，说明写在旁边的块里 |
| 时间轴 | `{timeline: [['第 1 天', 抵达], ['第 2 天', 古城]], direction: v}` | 日程、里程碑；≤5 项默认横排，更多自动竖排 |
| 已填表格 | `{sheet: [[学费, 包含], [机票, 另计]], head: [项目, 费用], widths: '120px 1fr'}` | 费用、参数、课表（有内容的表；要读者填写的用 table） |
| logo 墙 | `{logos: [a.png, b.svg], h: 40}` | 主办方、合作机构；只放封面/封底 |

- `display` 加 `stroke: 1.2` = 描边空心大字（章节号、L1–L4），自动转成矢量路径（不产生 Type 3 字体）；`display` 里可用 `<br>` 断行。
- `cards` 的每一项可以写成 `{k: 眉标, t: 标题, meta: [地点, 类型], x: 说明, img: 图标.png}`；meta分别显示信息字段，不把副名/地点用分号拼入正文。`style: line` = 线条式（发丝线分隔、无底框），比白卡片更像印刷品。
- 系列先在项目登记，再在全部成员页引用；`item`加引号，避免丢前导零。配图位置可按内容变化，不能因此另拼一种系列标题。示例：
  ```yaml
  book:
    series:
      highlights:
        label: HIGHLIGHT
        items: {'01': Cultural Night, '02': Eco-Diplomat Field Day}
  pages:
    - layout: PAPER
      body:
        - series_header: {series: highlights, item: '01'}
  ```
- `timeline`的`style: axis`除了旧`[日期, 主题, 说明]`，也支持`{k: D1, t: Arrival, period: Evening, events: [Check-in, Dinner]}`。period为原文已知时段，events为活动清单；不为每项臆配钟点。普通竖向timeline可用第三字段为节点说明，不必用分隔符拼进主题。
- `items`默认有序；无顺序清单用`style: bullet`（圆点）或`style: plain`（无标记但保留列表语义）。包含/不含等已由栏目分组、逐行可辨的短信息优先plain，避免再生成一排短横；不能自动设计成步骤。原稿Markdown的`-`是格式线索，不是要印出的文字。
- 卡片`x`、栏目说明、`notes`注释等接受文字数组的字段，默认排成无标记语义列表；不能仅因输入是数组就补短横。需要圆点时用显式`items: …, style: bullet`块。
  共用卡片块与CARDS版式的控制样张见 `dev/gallery/card_lists.jpg`（虚构内容）。
- `logos`在深色纸面上可写`frame: true`，整组保留白底承托；不把原logo反色、裁切或重画。改完仍需看实际图，确认原图含透明字/深色字时可读。
- 系列组件控制预览：`dev/gallery/series_header.jpg`；时间轴结构化活动预览：`dev/gallery/timeline_axis.jpg`。均为自编控制文案，不含用户照片，不代表真实内容已通过审稿。
- `figure` 加 `bleed: right | left | both` = 出血到页边；项目的 `book.image_bleed: both` 统一作用于整版心的 figure/gallery，图组接成出血照片带。栏内小图不自动越过旁边的正文，应重组页面或选择 T/SL 等接纸边版式。二维码、logo、图表用 `role: qr | logo | diagram` 保持完整。
- 独立 `PAPER` 图版只放 `{figure: poster.jpg, bleed: page}`，并写 `folio: false`，图片覆盖四边。正文/说明移到相邻页，不能追加在满页图下方。
- `cards` 的两栏奇数条目可写 `balance: true`：末项横跨两栏，但标题和说明仍各占一个阅读栏，不把说明拉成整行。
- `figure: logo.svg` 矢量直接嵌入。
- 图片写 `ai:编号`（版式 image、figure、产品卡 image）= AI 配图位，见 references/images.md §4；页上写 `tone: dark | light` 指定图上文字用白字还是深色字。

清晰度：构建时 hb.py 按实际显示尺寸估算 dpi，低于 96 会提示“满版会糊”、96–130 提示“印刷偏软”。插图显示得越小越清楚。

### YAML 易错点
- 花括号 `{…}` / 方括号 `[…]` 里的文字含有半角 `: , ? # [ ] { }` → **给整段文字加引号**：`{p: '时间：9:00, 地点：礼堂'}`。英文原文几乎每句都有逗号，`items: [...]` 里每条都要加引号，否则一条会被拆成两条。
- 中文全角标点（，：？）不受影响。
- 需要任意 HTML 用 `{html: …}` 块：它**不做转义**，只用于你确认可信的内容；来自原文 / 第三方的文字不要放进 `{html:}`。
- 像数字的文字会被当成数字：`[Day 1, 11.20]` 会印成 “11.2”，`08:30` 在某些写法下也会变形 → 日期、时间、编号统一加引号：`'11.20'`、`'08:30'`。
- hb.py 会指出出错的行号。

## 3. 容量预算（按行算，排页前估算）
网格与容量常数见 layouts.md §0（A4 版心 32 行）。各文字区大约有：PAPER 32 行 · T（split 330）纸面约 22 行 · B（split 760）纸面约 23 行 · SL/SR 32 行（3–4 栏宽）· HOLE 窗旁 ≈ 窗高、窗下 ≈ 32 − 窗高 − 1 · SPREAD_H 每页纸面约 16 行。
常见块占几行：kicker + title 3 · task 3 · p 每行 1（整宽 6 栏 40 个汉字或约 75 个英文字母一行；4 栏 26 字、3 栏 19 字）· items 每条 1–2 · kv 每行 1 · step（引导词 + 2 行书写 + 1 个填写栏）≈ 5 · q 最少 4 · table 每行 lines 行 + 表头 1 · box = h ÷ 28 · figure = h ÷ 28 + 图注 1 · stats 3 · quote 每行 1 + 署名 2 · 块间 1。
英文比中文长 30–60%：同样内容的西文版要留更多余量。
超出预算时引擎会先缩图、收空行、少书写线、缩标题（layouts.md §0），构建时报 `[书写线收紧]` `[字号收紧]` 的页最好拆开：把原文挪到相邻页（不要删原文、不要手写小字号）。

## 4. 图片
- 资料里自带的图（PPT/Word/PDF）：`new_project.sh` 已用 `extract.py` 抽到 photos/，先看 `images.md` 和 `photos/_contact.jpg`；`doc.md` 的注释写着每页原来配哪几张图。照片按“建议用法”进版式，图形（截图、图表）只进 `figure`。
- **主图与辅助图分工**：主要现场照（人物、场馆、活动主体）进主图位（版式 `image`、ONE/TWO/MIX 的主图带、跨页、POSTER）；`figure` / `gallery` 只放辅助图、图形（截图、图表）和小图；不要靠执行者碰巧选对 ONE——主图位不够就换版式或拆页（会报 `[主图过小]`）。
- 横图（宽 ≥ 1.4×高）→ 跨页；竖图 → POSTER；任意 → T/B/SL/SR/HOLE。
- 按内容选图：每个单元用和它对应的地点/活动/对象；同一张图不要用两次；主体（人脸、建筑）别放在文字区。
- 印刷清晰度：档位以 images.md §2 为准（A4 单页 ≥ 2500px、跨页 ≥ 5000px 撑 300dpi；低于 1500px 只适合小区域：HOLE、SL/SR 侧条、figure）。
- 主图可见高度 < 150px（封面 / 跨页 / ONE / TWO / MIX 的主图带）会报 `[主图过小]`：减少该页文字或拆页，不要把合照压成一条边。
- 没有照片：先问用户要（活动现场、学校、产品、往届照片都行）；拿不到就用无图风格（style.md §1），或 photo 风格 + `image: placeholder` 占位；环境里有图像生成工具时可以生成，提示词骨架：`documentary photo, {场景}, natural light, {时间}, wide angle, no text, 3:2`（横图）/ `2:3`（竖图）——在交付说明里标明哪些是生成图。

## 5. 照片版式的节奏（进阶模式）
| layout | 页数 | 样子 | 常见用途 |
|---|---|---|---|
| POSTER | 1 | 满版照片，白字 + 自动渐进压暗 | 封面、欢迎信/致辞、章节扉页、封底 |
| PAPER | 1 | 纯纸面，无照片；`surface: paper / A / B / dark`，见style.md §8 | 规章、日程表、通讯录、附录、笔记页、签署页 |
| T / B | 1 | 照片在上 / 在下（交界落在行线上），其余是纸面 | 带主题图的内容页、任务页、评价页 |
| SL / SR | 1 | 照片在左 / 右侧条（出血到页边，内沿在栏间中线上），文字在其余几栏 | 长清单、长任务单、表单 |
| HOLE | 1 | 版心里开一个窗（2–3 栏 × 若干行）放照片 | 目标、要点、实验、安全须知 |
| SPREAD_P | 2 | 一张横图铺满两页，两页都是海报 | 总览｜公约、章节大扉页 |
| SPREAD_H | 2 | 横图贯穿两页上半部，标题与要点压在图上，下半纸面 | 一个单元（一天/一章/一个模块）的主力页 |
| SPREAD_OPENER | 2 | 左页开篇海报，照片延伸到右页（侧条或上部），其余是纸面 | 单元开篇 + 第一页内容 |

节奏建议（按篇幅缩放）：
- **跨页是这套风格最出彩的地方，要舍得用**：内页一半以上放在跨页里（8 页册 ≥ 2 组，12 页 ≥ 3 组，16 页 ≥ 4 组），并混用不同跨页类型（SPREAD_H / SPREAD_OPENER / SPREAD_P）。每个主要单元（一天、一章、一个模块）最好有自己的跨页。
- 开头是封面 POSTER；有致辞/欢迎信时用 POSTER（letter）或放进跨页左页。
- 单页在 T/B/SL/SR/HOLE 之间轮换；相邻页不用同一版式（hb.py 会提示）。
- PAPER 留给真正需要满版纸面的页：大表单、密集表格、通讯录、整页笔记。一本里通常不超过 1/4。
- 跨页必须从偶数页开始（hb.py 会报错）。页数不对时先挪内容；需要补页时，笔记页是最自然的补法（宣传册不用笔记页：补一页图组 `gallery`、引语 `quote` 或常见问题 `cards`）。

宣传册（`purpose: brochure`）用照片版式时的节奏，样例见 `templates/book.brochure.zh.yaml`（用内容版式的节奏见 rhythms.md）：
- 封面 POSTER（一张最好的图 + 名称 + 一句定位）→ 开篇跨页（为什么 / 关键数字 `stats` + 亮点 `cards`）→ 内容跨页（行程、课程、现场图组 `gallery`）→ 口碑（`quote`）→ 报名方式 / 费用（`step` 不带 write、`kv`）→ 封底 POSTER（联系方式 + `qr` 二维码）。
- 每页都要“满”：宣传册的纸面不能大片留白——用插图、图组填，或把相邻两页合并；但不编造内容，原文不够就少排一页。
- 数字、亮点、引语都来自原文；原文没有的不要为了版面补。二维码永远深色码 + 白底（引擎自动），链接要用户给。

## 6. yaml 做不到时
- 单个特殊元素用 `{html: ...}` 块。
- 引擎原理：`flow.py` 把每个照片版式拆成网格上的几块——照片 / 插画格、不透明的纸面格、文字区（`region`，块按整行排）；照片烘焙成整页底图（`hb.py bake`），`shot.js` 隐藏文字截背景 → `dark.py` 只在白字所在的行带做整宽渐进压暗（目标对比度 ×1.03）→ `qa.py` 用 95 分位亮度算对比度（< 18px 需 ≥ 4.5，大字 ≥ 3）；`fill.js` 在浏览器里把文字栈对齐到行线、按 layouts.md §0 的顺序让出空间、`fill` 按 28px 铺线，并做溢出 / 重叠 / 越界自检。新版式加在 `flow.py` 的 `LAYOUTS` 表里，只用 `region`、`paper`、`zone`、`C.box` 这些网格原语，不写像素坐标。


## 品牌图形背景 brand_graphic

可选装饰层，复用所有版式的emit，不改网格与文字流。决策流程见style.md §7.1。将可信、单色、纯几何SVG放在项目photos/中（随门禁指纹与源文件打包），不含脚本/图片/外部引用；引擎内联为矢量，单文件HTML和PDF保留。file为项目相对路径；试排/语言子项目可使用工具共享的book.photos目录，其他越界路径拒绝。

```yaml
book:
  brand_graphic:
    file: photos/_assets/symbol.svg
    opacity: 0.05
    variants:
      junction: {view: [20, 30, 120, 140]} # 源SVG坐标焦点窗，仅定位/缩放完整母形
pages:
- layout: PAPER
  brand_graphic:
    variant: junction
    frame: [0.55, 0.35, 0.8, 0.7] # 页面比例[x,y,w,h]，可超出纸边
    angle: 90
    meaning: 本页协作内容采用源符号交汇处 # 仅方案，不印出
  body: [{title: Collaboration}]
```

每页显式选用，未写/false则不画；跨页写在left/right里。view默认源viewBox，frame默认整页，angle默认0；取色跟随本页纸面（浅底强调色，深底白/黑由既有对比色选择）。组透明度避免交叠处变浓，源SVG完整路径通过单一仿射矩阵等比放大/旋转/移动，不创建嵌套SVG裁窗；局部只由纸边或前景照片自然遮挡显现，不能切断母形。frame是定位参照，不是剪刀。cnBrandGraphics在最后实际布局后遮掉图片可见框，文字栈位于图形上方；只有经设计且实看过的图上应用才显式over_image:true。印刷共享超大图形时，偶数页写`spread: left`、下一奇数页写`spread: right`，两页使用完全相同的variant/view/frame/angle；frame改以整张2W×H面对页为参照。引擎在同一坐标系变换完整母形，右页只平移−W，旋转中心不另算；单双页不合会拒绝。仍须联合看PDF中缝，不能用两个独立局部冒充跨页。

共享跨页除单双页外，还检查配对是否齐全及实际变换/透明度是否一致；只给一侧、角度/位置/透明度不合会拦构建。颜色按两张纸面分别取色，允许蓝纸白纹接白纸蓝纹。控制样张见`dev/gallery/brand_graphic.jpg`（自编几何、纯色照片，无用户标志）。控制验证：dev/tests/test_brand_graphic.py检查无重排、图片/跨页保护、纸面取色、实际PDF、非法资源与跨页拒绝，以及普通--proof入口/共享素材/正式导出隔离。
