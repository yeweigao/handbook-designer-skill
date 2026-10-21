# 交付与多语言

## 交付物
`bash hb/export.sh <project> [文件名]` 生成到 `<project>/out/`（文件名缺省 handbook）：
| 文件 | 给谁 | 说明 |
|---|---|---|
| `<名>.pdf` | 打印、发群 | A4 校样：成品尺寸，背景与照片完整，带书签；不含出血和裁切线，不是印厂制版文件 |
| `<名>_可编辑.pdf` | 需要自己改字的人（老师、行政） | 同一版式，字体完整嵌入常用字库（GB2312 全部 6763 个常用汉字 + 符号 + 西文），可在 Acrobat 等 PDF 编辑器里直接改字、加字；文件更大（约 6–20MB），导出多花 1–4 分钟 |
| `<名>.html` | 想在浏览器看/改字的人 | 单文件，图片与本书用到的字体子集全部内嵌，换电脑打开字形不变；页尾附字体许可（屏幕可见、打印不出） |
| `<名>_源文件.zip` | 下一轮修改 | book.yaml + 照片目录（按 book.photos）+ 烘焙后的图片 + 字体 + 项目根目录的 .md（原文、image_credits.md 等）；解压后 `bash hb/run.sh` 可重建 |
| `review_*.jpg` | 回复里快速预览 | 封面 + 每个跨页的拼版 |

用当前环境的方式把文件交给用户（文件发送工具、写回用户指定的文件夹、或已连接的网盘/Notion 等应用）。工作目录可能在会话结束后消失，所以每一轮都把 zip 一并交付。

成册交付前完成workflows/visual-review.md的后置审改，核对最终PDF、预览与源包对应同一版本；审稿标准仍见review.md。

需要读者撕下上交的页（报名表、承诺书、“我的宝贝”）：骑马钉装订后撕下一页会带掉对面一页，在回复里提醒：整本回收、把这些页另印成活页/插页，或把它们排在同一张对开纸上并加撕线。

印刷提示（写进回复）：交印刷厂前用 `book.scale: 3` 重新构建、换成高清原图；引擎输出的是成品尺寸、不含 3mm 出血，满版照片页裁切后边缘可能露白，需要出血时提醒用户和印刷厂确认处理方式。已确定骑马钉时写`book.binding: saddle`，总页数含封面封底须为4的倍数，hb.py硬性检查，不自动塞空白；未确定装订方式时不写binding，页数仅提示。合页后先完成内容与封面封底的整体分配，再做拼版。

## 字体与许可
- 构建时按本书用字裁切字体子集（`<project>/fonts/hb-*.woff2`），内部字体名改为 `HB Subset …`，许可清单在 `fonts/LICENSES.txt`，源文件 zip 会一起打包。
- OFL 字体：可商用、可嵌入、可随文档分发。霞鹜新晰黑/新致宋（IPA Font License 1.0）：印刷与 PDF 嵌入明确允许；网页（单文件 HTML）嵌入需附许可与原字体获取方式——导出脚本已自动附上。
- PDF 可编辑性：子集字体都转成静态 TrueType 嵌入（可变字体和 CFF/OTF 字体会被 Chrome 写成 Type 3，Acrobat 无法编辑、部分印厂退稿）；export.sh 会检查并报告 Type 3。若出现，通常是某个字体没下载、回退到了系统字体 → `python3 hb/fonts.py fetch` 后重导。
  普通版 PDF 只嵌入书里用到的字（体积小），在编辑器里加新字会缺字形；要给别人改字，发 `_可编辑.pdf`。
  改字说明（写进回复）：用 Acrobat（或其他支持编辑文字的 PDF 编辑器）打开 `_可编辑.pdf` 直接改；超出常用字库的生僻字会缺字形；改动多于几处、或要增删整段时，仍建议改 book.yaml 重新构建（排版、书写线、QA 会一起更新）。Mac 预览不能编辑任何 PDF 的正文。用了渐变标题（`gradient`）的话，那几个标题在 PDF 里是文字蒙版，编辑器改不了，要说明。
- 换电脑重建：源文件 zip 里已有字体子集；改了文字需要新字时，新电脑上运行 `python3 hb/fonts.py fetch` 下载完整字体。

## 多语言版本

### 推荐：一份 book.yaml 写两种语言，一次出两本
```yaml
book:
  title: {zh: 山海自然探索营, en: Horizon Nature Discovery Camp}
  langs: [zh, en]
pages:
- layout: CARDS
  title: {zh: 六个关键词, en: Six keywords}
  cards:
    - [{zh: 海岸地质, en: Coastal geology}, {zh: 走进潮间带与海蚀崖……, en: 'Explore tide pools and sea cliffs, …'}]
```
- `bash hb/run.sh $P` 自动拆成 `$P/zh`、`$P/en` 两个子项目（照片目录链接回原项目），分别构建、分别跑完整 QA，最后一行 `ALL LANGS: GATE PASS / FAIL`；逐页对照图在 `$P/.qa/compare_*.jpg`。
- 内容版式是为中英共用设计的：英文比中文长时，照片和色块变小、标题自动缩一档，版式不变。某种语言缺了某段文字 → 构建报错并指出位置。
- 英文里有逗号、冒号、问号、`#` 时整段加单引号（`en: 'Five days, four nights'`），否则 YAML 会把它拆开——构建时会报错指出位置。
- 各语言的原文核对：把原文放成 `doc.zh.md`、`doc.en.md`，拆分时自动放进对应子项目当 doc.md。
- 导出：分别 `bash hb/export.sh $P/zh 手册_中文`、`bash hb/export.sh $P/en Handbook_EN`。

### 已有单语 yaml：在 book.yaml 层翻译
版式、图片、参数全部沿用，只换文字，所以译本的排版质量和原版一致：
```bash
python3 hb/i18n.py extract $P/book.yaml $P/strings.json          # {"原文": ""}
#   把每个值填成译文（值留空 = 保留原文）。要求信达雅、意思不增不减、保留 <b> <br>。
python3 hb/i18n.py apply $P/book.yaml $P/strings.json ${P}_en en  # 新项目，book.lang=en，照片共用
bash hb/run.sh ${P}_en                                            # 照常 QA：西文更长，溢出就调 size / 挪内容
```
- `lang` 不是中日韩时引擎自动切换西文排版（Playfair 标题、收紧字距、左对齐、西文字体优先）。
- 中英双语同页（一本书里两种语言并排）：直接在 book.yaml 里写两种语言（如 `{title: 研学目标, en: Learning Goals}` 的副题），不必走翻译流程。
- 译本没有中文 doc.md，不跑原文核对；改为对照 strings.json 抽查是否有漏译（apply 会列出未翻译条目）。


## 导出门禁、草稿、导出自检
- `export.sh` 先跑 `gate.py check`：必须是 `run.sh` 通过（GATE PASS）之后、book.yaml / brief.md / 原文 / 照片都没再改过的版本，否则拒绝导出并说明原因。
- 赶时间先给人看：`bash hb/export.sh $P 名字 --draft` → 文件名带“_草稿 / _draft”，每页斜着打“草稿 DRAFT”水印，不出可编辑 PDF。草稿不能交印刷厂。
- 导出后自动跑 `postflight.py` → `.qa/postflight.md`：页数（和排版计划对得上、是否 4 的倍数）、成品尺寸、可点链接数、字体（Type 3）、文件大小、images.yaml 里的低清图和没写来源的图。全 ✓ 再交付。
- `--proof`和方向样张只核抽取页，门禁标记为proof，不代表整册章序/装订通过；不能正式导出该样张，需先构建完整项目。最终PDF的视觉复核见review.md，不能由postflight替代。
- 每次构建、导出都在 `.qa/log.md` 记一行。

## 可点链接
- 目录（GRID 的 `toc`）每一行都能点，跳到对应页（HTML 和 PDF 都能跳）。
- 文字里的网址（www.… / https://…）和邮箱自动变成链接，样式不变。

## 画布：A4 / A5 / 小红书 3:4（`book.canvas`）
| canvas | 尺寸 | 网格 | 适合 |
|---|---|---|---|
| `a4`（默认） | 210×297mm（794×1123px） | 网格与字号档见 layouts.md §0（正文 16px；`book.body: 14` 为紧凑档） | 手册、宣传册、印刷 |
| `a5` | 148×210mm（559×794px） | 6 栏 × 28 行，栏宽 4 字 | 口袋手册、随身指南 |
| `xhs` | 3:4，导出 1080×1440 图片 | 6 栏 × 28 行，左右页边相同、单页 | 小红书 / 朋友圈图文 |
- A5、小红书正文是 14px（印出来 10.5pt），小画布一页放的字只有 A4 的一半左右：同一份内容换小画布要重新分页（doctor 会报溢出，按提示拆页）。
- 小画布使用已登记的内容版式（含编辑变奏）；照片版式（POSTER、T、SPREAD_* 等）只在 A4 上有。小红书画布不能用跨页。
- 效果：`dev/gallery/canvas_a5_xhs.jpg`（上 A5、下小红书，同一份内容）。
- 小红书：`export.sh` 额外输出 `out/<名>_小红书/01.png …`（每页一张 1080×1440）。封面那张就是笔记封面，第一页的标题要短、字要大。

## 在线编辑页
成品可以发成一个网页，用户和同事直接在页面上改字、换图、批注，改完说“同步修改”写回 book.yaml。见 `workflows/edit-online.md`。
