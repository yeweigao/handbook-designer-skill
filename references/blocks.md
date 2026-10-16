# book.yaml 速查（book 设置 · 版式 layout · 内容块 block · 容量预算 · 图片）

写 book.yaml 前读一遍。每个版式长什么样见 `references/gallery/<LAYOUT>.jpg`；完整可运行的样例见 `templates/`。

## 0. book 设置
```yaml
book:
  title: 手册标题            # HTML <title>
  folio: 页脚左侧文字         # 默认 = title
  photos: photos             # 图片目录（相对项目目录）
  purpose: workbook          # workbook 任务册（有书写区，纸面内容上下撑满）/ guide 指南（以读为主）/ brochure 宣传册（无书写区）；后两者纸面默认顶部对齐
  style: photo               # 视觉风格：photo（默认）/ editorial / swiss / notebook / inkwash / papercut / riso / aurora，见 style.md
  fonts: magazine            # 字体方案：magazine / serif / sans / hand，或按角色指定，见 style.md
  lang: zh                   # zh / ja / ko = 中日韩排版；en / fr / … = 西文排版（收紧字距、左对齐、正文用西文字体）
  paper: 0.9                 # 纸面不透明度：0.86 通透 … 0.94 更易读（照片繁杂、字看不清时调高）
  scale: 2                   # 图片烘焙倍率：2 ≈ 190dpi（屏幕/打样），3 ≈ 290dpi（交印刷厂，构建更慢）
  colors: klein              # 可选：配色方案名（见 style.md §3），或颜色键 {G: '#1D5A43', GOLD: …}，或 {preset: klein, G: '#…'}
  gradient: spotlight        # 可选：大标题（display / title）用渐变色，见 style.md §4；默认不开
pages:
  - {layout: ..., ...}
```

## 1. 版式 layout（每页一个；跨页类占 2 页，必须从**偶数页**开始）
除 PAPER 外，各版式都有一个“图片位”：photo 风格必须写 `image`（或 `image: placeholder` 占位）；无图风格不写 `image` 就自动生成底图。

| layout | 页数 | 必填 | 可选参数 | 文字区 | 适合 |
|---|---|---|---|---|---|
| PAPER | 1 | — | header, body_top(64) | body（纸面整页） | 没有合适照片的页：规章、日程表、通讯录、附录、笔记页、签署页 |
| POSTER | 1 | image* | focus, target, zoom, header, fig, folio:false, top_y, bottom_y | top（从上往下）、bottom（贴底） | 封面、致辞/欢迎信、章节扉页、尾页、封底 |
| T / B | 1 | image* | T: split(330), body_top；B: split(760)；focus, target, zoom | T: on_photo（白字）+ body（纸面）；B: body 在上 + on_photo 在下 | 带主题图的内容页、任务页、评价页、成果页 |
| SL / SR | 1 | image* | strip(270), zoom(1.6) | body（单栏） | 长清单、长任务单、表单 |
| HOLE | 1 | image* | window: tr/tl/br/bl, size:[300,250], zoom(1.4) | beside（窗旁窄栏）、body（窗下/上整宽） | 目标、要点、实验、安全须知 |
| SPREAD_P | 2 | image*(横图) | target | left/right 各自 {header, top, bottom, fig, top_y, bottom_y} | 总览｜公约、章节扉页、目录式大图 |
| SPREAD_H | 2 | image*(横图) | body_top(548) | left{header,on_photo,body}、right{header,on_photo(自动贴照片底),body} | 一个单元（一天/一章/一个模块）的主力页：上半图+标题+要点，下半写/读 |
| SPREAD_OPENER | 2 | image*(横图) | right_layout: SL 或 T | left{header,top,bottom,fig}、right{header,body,(T 时 on_photo, body_top)} | 章节开篇 + 第一页内容 |

- `header: [左, 右]` 页眉（英文小字或中英混排都可）；`fig: Fig. 01 · 图注` 图片说明。
- `focus:[x,y]`（0–1）= 图片里的哪个点；`target:[px,py]` = 放到页面哪个像素（单页宽 794、跨页宽 1588、高 1123）。主体被字压住 → 改 focus/target。
- 页面 794×1123px（A4 @96dpi），边距 56px，页眉 y=34，页脚 y=1097。引擎只出 A4 竖版。
- `note:` 可写在任何页上（不渲染），用来记“这页对应原文哪一段”。
- `align: spread | top | bottom`（写在页上；跨页写一次，左右两页都生效）：纸面文字区（body / beside）的纵向排布。除 PAPER（默认 top）外默认 spread = 块之间均匀撑满，适合有书写线/fill 的页；没有 fill 的阅读型内容被拉得太散时设 `top`。有 fill 的页不需要设（fill 会吃掉空白）。
- \* 无图风格（style 不是 photo）里可以不写 image，自动生成底图；写了就用照片。
- `image: placeholder`：photo 风格下还没有照片时的占位底图（主题色深色渐变 + 柔光，效果见 gallery/placeholder_example.jpg）。POSTER、T/B、SL/SR、各类跨页都好看；HOLE 的窗里只会是一团暗色，没照片时别用 HOLE。可写 `placeholder_cover` 这类名字，方便在回复里对应拍摄清单。照片到了改成文件名，重跑一次 QA（真实照片的明暗会变）。
- 照片构图：图片会先按“铺满”缩放。横图比页面更宽时只能左右移，比页面更方时只能上下移；想往另一个方向移动主体，先 `zoom: 1.2–1.5` 放大留出余量，再调 focus/target。SPREAD_H 的渐隐位置固定在页面中部，`body_top` 只移动文字。

## 2. 内容块 block（列表里的每一项；由“类型键”决定是哪种块，其余键是参数）
| block | 写法 | 说明 |
|---|---|---|
| 大字 | `{display: 标题, size: 48, spacing: .14, color: gold/white/ink, lh: 1.15, mt: 6, gradient: energy}`（gradient 可选：渐变名、颜色列表或 false） | 海报标题、单元编号（Day 1 / Unit 3 / 第一章） |
| 标题 | `{title: 页标题, kicker: Small Label, sub: 斜体副题, size: 34, gradient: …}` | 纸面上的页标题 |
| 英文副题 | `{en: A Letter Before Takeoff, size: 17}` | Playfair 斜体 |
| 小标签 | `{kicker: Key Facts · 核心知识点, mt: 14}` | Oswald 大写小字，用来分区 |
| 段落 | `{p: 原文, lead: 引导词：, size: 14, weight: 700, mt: 12}` | lead 为加粗引导词；可内联 `<b>` `<br>` |

> 所有文字都会做 HTML 转义（原文里的 `<`、`&` 原样显示），只放行不带属性的 `<b> <strong> <i> <em> <u> <br> <sup> <sub> <small>`。需要其他 HTML 时用 `{html: ...}` 块，且只放你自己写的可信内容。

| 书信 | `{letter: [段1, 段2]}` | 致辞页（衬线大号段落） |
| 清单 | `{items: [..], heading: 小标题, style: big, size: 16}` | 原文的项目符号列表；style:big 为大号编号 |
| 键值 | `{kv: [[左, 右], …], kw: 90, gap: 10, ksize: 15, vsize: 14}` | 日程、时间表、联系方式、术语表 |
| 任务大标题 | `{task: A, name: 任务名, sub: 副题}` | 大号斜体字母/编号 + 标题 |
| 编号步骤 | `{step: 1, lead: 引导词, text: 原文, write: [块…], grow: true}` | write 里放书写区；grow 让它吃掉剩余高度；lead 后自动加冒号（中文“：”/西文“: ”，原文自带冒号不会重复） |
| 问答 | `{q: 1, text: 原文问题, write: [{fill: 64}]}` | 默认自动铺线 |
| 工作单标签 | `{worksheet: 名称}` | 显示为 “Worksheet · 名称” |
| 填写栏 | `{field: 标签, size: 13}` / `{fields: [A, B], cols: 1fr 2fr, size: 13}` | 标签 + 下划线；标签默认 11px，给家长/低龄读者填的表单可调到 13–14 |
| 书写线 | `{lines: 3}` | 每行 32px（≈8.5mm，适合手写） |
| 自动铺线 | `{fill: 64}` | 占满剩余空间，最小高度 64 |
| 方框 | `{box: 提示, h: 140}` / `{boxes: [1, 2, 3], h: 110}` | 画图、贴照片/贴纸、粘票据 |
| 圈选 | `{choice: 提示（圈出）, options: [甲, 乙, 丙]}` | 代替 ☐ 方框的单选/多选、自评等级 |
| 表格 | `{table: ['', 列1, 列2], widths: 24px 1fr 1fr, rows: ['1','2','3'], lines: 1}` | 第一列为行名；lines = 每行几条书写线 |
| 姓名栏 | `{blanks: [姓名, 班级], w: 180}` | 封面/扉页一行式填写 |
| 签名 | `{sign: 声明文字, label: 签名}` | 声明 + 签名线（声明很长时改用 p + fields） |
| 多栏 | `{cols: [[块…], [块…]], widths: 1fr 1fr, gap: 36}` | 一栏一组块 |
| 空白 | `{space: 20}` | 微调 |
| 原始 HTML | `{html: '<div>…</div>'}` | 最后手段（翻译时需手工处理） |

### 2.1 图片与宣传块（宣传册、指南常用；任务册里也能用）
| block | 写法 | 说明 |
|---|---|---|
| 插图 | `{figure: a.jpg, h: 220, fit: cover, focus: [.5, .4], caption: 图注, frame: true}` | 纸面上的图（照片在 `photos/`）。`fit: contain` 不裁切（截图、图表、logo 必须用）；`frame: true` 加白底细框（截图）。图注算“装饰”，不进原文核对 |
| 图组 | `{gallery: [a.jpg, b.jpg, c.jpg], h: 160, captions: [甲, 乙, 丙], widths: 2fr 1fr 1fr}` | 一行 2–4 张；现场照片、作品、校园一角 |
| 关键数字 | `{stats: [['12', 年办学], ['3000+', 名学员]], size: 44, cols: 4}` | 大号数字 + 说明，数字要加引号（避免 YAML 当数字）。随 `book.gradient` 一起渐变 |
| 亮点卡片 | `{cards: [[标题, 说明], [标题, 说明]], cols: 2, num: true}` | 项目亮点、课程特色、常见问题；`num` 加 01 02 编号。各风格有自己的卡片样子（玻璃、纸片、虚线…） |
| 引语 | `{quote: 引语原文, by: 署名, size: 19}` | 学员说、校长寄语、家长反馈。原文自带的引号会去掉、“——署名”会自动拆到 by |
| 二维码 | `{qr: 'https://…', caption: 扫码报名, size: 104}` | 矢量二维码，永远深色码 + 白底（反色码很多手机扫不出）。需要 `pip install qrcode`；没有时把二维码图片放进 photos 用 figure |

| 对比条形图 | `{bars: [['识别正确率', 85, 50], …], series: [本产品, 通用方案], unit: '%'}` | 我方 vs 对照的指标对比（实测、调研） |
| 产品卡 | `{product: 名称, text: 说明, image: a.png, tag: 主推, h: 200, fit: contain}` | 渐变图区 + 标签 + 名称 + 说明；两三张并排用 `cols` |
| 胶囊标签 | `{chips: [L1 集团, L2 学校, L3 课堂, L4 家庭], on: 2}` | 层级/分类导航，`on` 高亮第几个 |
| 循环图 | `{cycle: [[L3, 课堂], [L1, 集团], [L2, 学校], [L4, 家庭]], center: 越用越聪明, size: 300}` | 飞轮、闭环；节点文字算装饰，说明写在旁边的块里 |

- `display` 加 `stroke: 1.2` = 描边空心大字（章节号、L1–L4），自动转成矢量路径（不产生 Type 3 字体）；`display` 里可用 `<br>` 断行。
- `cards` 的每一项可以写成 `{k: 眉标, t: 标题, x: 说明, img: 图标.png}`；`style: line` = 线条式（发丝线分隔、无底框），比白卡片更像印刷品。
- `figure` 加 `bleed: right | left | both` = 出血到页边；`figure: logo.svg` 矢量直接嵌入。
- 图片写 `ai:编号`（版式 image、figure、产品卡 image）= AI 配图位，见 SKILL.md“AI 配图”；页上写 `tone: dark | light` 指定图上文字用白字还是深色字。

高度预算：figure / gallery = h + 图注 18 · stats ≈ size + 40 · cards 每行 ≈ 70–110（看说明长度）· quote 每行 ≈ size × 1.7 + 50 · qr ≈ size + 30。
清晰度：构建时 hb.py 按实际显示尺寸估算 dpi，低于 96 会提示“满版会糊”、96–130 提示“印刷偏软”。插图显示得越小越清楚。

### YAML 易错点
- 花括号 `{…}` / 方括号 `[…]` 里的文字含有半角 `: , ? # [ ] { }` → **给整段文字加引号**：`{p: '时间：9:00, 地点：礼堂'}`。英文原文几乎每句都有逗号，`items: [...]` 里每条都要加引号，否则一条会被拆成两条。
- 中文全角标点（，：？）不受影响。
- 像数字的文字会被当成数字：`[Day 1, 11.20]` 会印成 “11.2”，`08:30` 在某些写法下也会变形 → 日期、时间、编号统一加引号：`'11.20'`、`'08:30'`。
- hb.py 会指出出错的行号。

## 3. 容量预算（排页前估算，避免溢出）
纸面可用高度：PAPER ≈ 1000px · T(split 330) ≈ 730 · SL/SR ≈ 1000 · HOLE body ≈ 480、beside ≈ 500 · SPREAD_H body ≈ 510/页 · B(split 760) ≈ 700。
常见块高度：title 60–80 · task 90 · p 每行 22（整宽约 36 个汉字或 90 个英文字符/行）· items 每条 22–40 · kv 每行 25–35 · step(含 2 行书写) 100 · q 最少 96 · table 每行 32×lines + 表头 26 · box = h+10。
英文比中文长 30–60%：同样内容的西文版要留更多余量。
超出预算 → 先减书写线/调小 fill → 仍不够就把原文挪到相邻页（不要删原文、不要把字缩到 12px 以下）。

## 4. 图片
- 资料里自带的图（PPT/Word/PDF）：`new_project.sh` 已用 `extract.py` 抽到 photos/，先看 `images.md` 和 `photos/_contact.jpg`；`doc.md` 的注释写着每页原来配哪几张图。照片按“建议用法”进版式，图形（截图、图表）只进 `figure`。
- 横图（宽 ≥ 1.4×高）→ 跨页；竖图 → POSTER；任意 → T/B/SL/SR/HOLE。
- 按内容选图：每个单元用和它对应的地点/活动/对象；同一张图不要用两次；主体（人脸、建筑）别放在文字区。
- 印刷清晰度：A4 单页图 ≥ 2500px 宽、跨页图 ≥ 5000px 宽才能撑到 300dpi；手机原图一般够单页。低于 1600px 的图只适合小区域（HOLE、SL/SR 侧条）。
- 没有照片：先问用户要（活动现场、学校、产品、往届照片都行）；拿不到就用无图风格（style.md §1），或 photo 风格 + `image: placeholder` 占位；环境里有图像生成工具时可以生成，提示词骨架：`documentary photo, {场景}, natural light, {时间}, wide angle, no text, 3:2`（横图）/ `2:3`（竖图）——在交付说明里标明哪些是生成图。
