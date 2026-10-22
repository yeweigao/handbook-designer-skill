---
name: handbook-designer
metadata:
  agent_created: true
description: 将 Word、PDF、PPT、Markdown 或文字材料制作为多页手册、宣传册、画册、指南或任务册，支持系列复用、品牌适配与改版。直接创作 HTML/CSS/SVG，检查最终 PDF，交付可编辑 PDF、离线 HTML 和可重建源包。不用于幻灯片、单页海报或网站。
---

# 手册设计

目标是有表现力、阅读舒适、可可靠交付的成品。先理解材料和读者任务，提出适合这本书的视觉主张，再直接创作 HTML/CSS/SVG。家族 CSS 提供共同语言，页面构图由作者决定。技术检查证明物理与内容条件，视觉质量要看最终 PDF 的全部页面。

## 路线

| 情况 | 工作流 |
|---|---|
| 给了材料，制作新册（默认） | [new](workflows/new.md) |
| 直接做、先出一版或无人值守 | [quick](workflows/quick.md) |
| 定稿美化、内容冻结 | [beautify](workflows/beautify.md) |
| 沿用旧册或同系列 | [reuse](workflows/reuse.md) |
| 修改成品、接续中断任务 | [revise](workflows/revise.md) |
| 品牌适配、建立品牌基因 | [brand](workflows/brand.md)，再回 new |
| 缺原文或事实材料 | [research](workflows/research.md)，再回 new |
| 用户自己改字、换图 | [edit-online](workflows/edit-online.md) |

所有路线收尾执行 [visual-review](workflows/visual-review.md)。按需读 [用途](purposes/index.md)、[品牌](brands/index.md)，它们提供内容判断与品牌约束，不规定整页模板。

## 开始前与作者边界

- 沿用用户已给的授权、品牌与内容要求，写入简短的 `brief.md`。只有缺失信息会实质改变结果时才问；没有固定的两轮确认、三个方向或长册试排审批。关键页与最难页的试作由 agent 自主完成。
- 原稿保留在 `sources/original/`；提取内容及稳定段 ID 写入 `sources/source.md`、`segments.json`。先读 [文案适配](references/adaptation.md) 和 [编辑审阅](references/editorial-advisor.md)，完成简短的页面任务与整册节奏，再落版。
- `content_mode` 选 `carry`（搬运）、`polish`（授权润色）、`translate`（授权翻译）、`frozen`（冻结）。事实、数字、限定条件不因排版改变；缺失信息照实保留。不能通过改原稿、隐藏文字或声明装饰消除内容错误。
- 唯一作者源是 `book.html` + `book.css`。`design.css` 是本项目冻结的家族基因；家族升级须主动审阅，不能构建时静默替换。原生 Grid、Flex、普通流、定位与页面专属 CSS 都可用，无需新增布局注册项。
- 一页一个 `.page`、稳定的 `data-page-id`；内容写 `data-source-id`，图片编辑用 `data-edit-id`。多语言共用一份作者源：默认语言在 HTML，其余在 `copy/<lang>.json`，长度差异用 `lang/<lang>.css`。格式与白名单见 [契约](references/contract.md)。
- 尺寸、出血、安全边距和装订只在 `project.json` 维护。打印 CSS 与字体声明由运行时生成，作者不重复声明。字体、图片等资源先本地化；正式渲染不下载资源，不依赖系统字体替换。
- 运行时只测量，不自动缩字、压行距、删书写区或重裁图片。放不下先改分组、栏宽与分页；长文用 `paginate` 写回作者源并审阅 diff。物理可读性下限与局部叠放声明见契约。
- 图片来源、授权及作者记入 `sources/assets.json`。真实照片不能由合成色带代替；主题、人物、裁切与图注关系须审稿。没有照片可以用纯文字设计，不编事实、不用无关图填空。

## 命令

下面的 `HB` 指向本 Skill 的 `hb` 目录，`P` 是独立项目目录。新环境先按 [环境与交付](references/delivery.md) 准备依赖和家族源字体。

```bash
HB=<skill目录>/hb
P=<工作目录>/<项目名>
bash "$HB/core/setup_env.sh"
python3 "$HB/core/family.py" list
python3 "$HB/core/family.py" init campus "$P" --title "书名" --langs zh-CN,en --mode translate
python3 "$HB/core/extract.py" <原稿.docx> "$P"
# 直接编辑 book.html / book.css / copy / lang；init 只是单页骨架
python3 "$HB/core/family.py" fonts "$P"       # 文案超出字库时显式重建
python3 "$HB/core/validate.py" "$P"
node "$HB/core/cli.mjs" paginate "$P"         # 只在使用 data-flow 时运行
node "$HB/core/cli.mjs" check "$P"            # 所有语言，最终 PDF + 全部技术检查
node "$HB/core/cli.mjs" verify "$P"
# 实际看完当前 PDF 后，按 visual-review 工作流记录结论
node "$HB/core/cli.mjs" review "$P" --verdict deliverable --by "审稿人" --notes <审稿记录.md>
node "$HB/core/cli.mjs" export "$P" --name <文件名>
```

`render` 仅生成快照与 PDF，不代表验收；`measure` 是只读测量。`check --lang` 可用于定位某语言问题，正式交付前必须覆盖所有语言。`export --draft` 生成带水印 PDF；不能把草稿称为最终版。

## 审稿与交付

- `check` 写 `.build/<构建ID>/<语言>/book.pdf` 与 `.qa/<构建ID>/`。检查有 `pass / fail / unverified`；硬项失败或未验证阻止正式交付。提示项须判断，不能一概忽略。
- 先看最终 PDF 的整册缩略图、真实面对页与每页阅读尺度图，再实际修改作者源、重建、复核。记录最弱页、照片主体、断行、语义、系列与跨页关系。技术通过不等于视觉优秀。
- 视觉结论为不合格 / 可交付 / 优秀；记录执行者是作者自评还是独立 reviewer。独立评测与人工校准另见开发基准，不能把自评伪称独立评测。
- 输入或 PDF 改动后旧验收失效。`review` 将结论绑定当前构建和 PDF 哈希；`export` 强制验证技术与视觉记录，再实测离线 HTML、可编辑 PDF 与源包重建。
- 正式交付包含各语言 PDF、可编辑 PDF、离线 HTML、整册/跨页预览、源包、`credits.md` 与 `delivery.json`。可编辑 PDF 的支持范围和未验证限制见 [delivery](references/delivery.md)，不承诺任意编辑器无损修改。
- 回复注明页数、语言、主要设计决定、非原文元素、未解决问题与实际交付限制，附预览和成品链接。只披露本项目相关的版权与印刷事项。
- 每轮把观察、修订及证据记入 `experience.md`（[格式](templates/experience.md)）。单次成功不晋升通用规则；经验闭环后续单独验收。

## 按需参考

- 开始构图：[composition](references/composition.md)、[layouts](references/layouts.md)、[style](references/style.md)、[rhythms](references/rhythms.md)。
- 长文、表格、工作册、跨页：[blocks](references/blocks.md)；图片：[images](references/images.md)。
- 验收尺度：[review](references/review.md)；交付、多语言与重建：[delivery](references/delivery.md)。
- 模板：[brief](templates/brief.md)、[page-plan](templates/page-plan.md)、[experience](templates/experience.md)。
- 真实作者源：`dev/samples/native/product-brochure/`（纯文字 12 页）、`dev/samples/native/nature-camp/`（摄影 16 页中英）。家族原语：`families/campus/`。样例供阅读拆解，不是必选整页菜单。
- 维护与验证：[dev/maintenance.md](dev/maintenance.md)，`bash dev/tests/selftest.sh`。
