# HTML/CSS 原生改造 · 分步实施

目标与原则见 [HTML-CSS-NATIVE-ITERATION](HTML-CSS-NATIVE-ITERATION-2026-10-21.md)（下称「总计划」）。本文把总计划拆成可由不同 agent 独立接手的步骤；进度与交接记录在 [PROGRESS](PROGRESS.md)。

工作分支：`html-native`。每完成一步提交一次。

## 接手规则（每个 agent 都要遵守）

1. 先读：总计划 → 本文 → `PROGRESS.md` 最新记录 → 本步骤列出的「先读」文件。
2. 开工前在 `PROGRESS.md` 把本步骤标为「进行中」，写上日期。一次只认领一个步骤，除非两个步骤明确可并行且文件归属不重叠。
3. 只改本步骤「归属文件」里的文件。必须改契约（`references/contract.md`、`hb/core/schema/`）时，同步更新契约文档，并在交接记录的「契约变更」里写明。
4. 新运行时代码放在 `hb/core/`。旧 YAML 引擎（`hb/` 根目录其余文件）在 S10 之前保持原样可运行，不在中途删除或修改。
5. 依赖：Node 22 + 已有的 `playwright@1.64.1`；Python 3.10 + 已有 requirements。新增依赖必须锁版本，并在交接记录写明原因。不引入前端框架或构建系统。
6. 「完成判定」里的每一条都要实际运行并留下证据（命令输出或 `.qa/` 文件路径）。做不到的写 `unverified` 并说明原因，不写成通过。
7. 做完：按下方模板在 `PROGRESS.md` 追加交接记录 → `git add` 本步骤文件 → 提交（信息以 `S<n>:` 开头）。中途额度不够时，也要先写一条「中断」交接记录再提交，说明做到哪、下一步从哪继续。

## 步骤总览与依赖

| 步骤 | 名称 | 依赖 | 可并行 |
|---|---|---|---|
| **S1** | 契约与最小样例 | — | — |
| **S2** | 渲染运行时 | S1 | — |
| **S3** | 版面测量与可读性检查 | S2 | 与 S4、S5 并行 |
| **S4** | 最终 PDF 检查与验收绑定 | S2 | 与 S3、S5 并行 |
| S5 | 内容提取与原文覆盖 | S2 | 与 S3、S4 并行 |
| S6 | 长文续页工具 | S3 | 与 S7 前半并行 |
| S7 | Campus 家族 CSS 与第一批真实样册 | S3、S4（长册需 S6） | — |
| S8 | 导出与离线交付 | S4、S5 | 与 S9 并行 |
| S9 | Folio 联动 | S2、S5 | 与 S8 并行 |
| S10 | Skill 文档重写与旧引擎退役 | S2–S9 | — |
| S11 | 视觉参考资产 | S7 | 与 S10 并行 |
| S12 | 独立生成基准与审稿校准 | S10、S11 | — |

S1–S4 是地基：没有它们，后面任何页面都无法可靠渲染、测量和验收。经验晋升闭环不在本轮（见总计划）。

---

## S1 · 契约与最小样例

**目标**：把总计划里的项目目录、作者约定、多语言文案、内容角色、构建 ID 写成一份权威契约和机器可校验的 schema，并做出最小正例/反例项目。后续所有步骤以它为准。

**先读**：总计划「目标架构与责任边界」「最小作者约定」「CSS 基因」「与 Folio 联动」。

**归属文件**：`references/contract.md`、`hb/core/validate.py`、`dev/fixtures/contract/**`、`dev/tests/core/test_validate.py`、`dev/tests/core/fixture_fonts.py`、`dev/tests/core/make_fixture_images.py`、`dev/tests/core/font-licenses/`。

**要做**：
- `references/contract.md`：
  - 项目目录与各文件职责（总计划的目录表）。
  - `project.json` 字段：语言列表与默认语言、画布（成品尺寸 mm、出血 mm、安全边距 mm）、装订方式、可读性下限覆盖值（只能提高）、字体文件清单、内容模式（carry / polish / translate / frozen）。
  - HTML 约定：`.page`、`data-page-id`、`data-source-id`、`data-edit-id`、`data-role`（body / key / aux / display / deco）、`data-flow`（可续排内容流，留给 S6）、`data-overlap`（合法叠放声明）、跨页配对 `data-spread`。
  - `copy/<lang>.json` 格式：`{ "<source_id>": "文本" }`，可选行内标记的写法（仅允许 `<em> <strong> <a> <br>` 白名单，注入时其余一律转义）。
  - 构建 ID：输入指纹的组成（见 S2），构建产物目录 `.build/<build-id>/<lang>/`。
  - 检查报告格式：每项 `{id, status: pass|fail|unverified, severity: hard|hint, page, target, evidence, message}`。
- `hb/core/validate.py <project>`：只用标准库，校验 project.json、作者 HTML、作者 CSS、多语言文案。契约文档 + 这个脚本就是权威，不另建 JSON schema（避免双重真相）。
- 样例：`dev/fixtures/contract/minimal-zh/`（2 页中文）、`bilingual/`（4 页中英，3mm 出血，含跨页对、跨页图和 `data-flow`）。反例不建目录，由测试在正例副本上逐项引入违规。字体为 `dev/fonts/` 的 Noto Sans/Serif SC、Inter 子集。

**完成判定**：
- `python3 hb/core/validate.py dev/fixtures/contract/minimal-zh` 与 `bilingual` 退出码 0。
- 每个反例退出码非 0，且错误信息指出文件和 ID。
- 契约文档与总计划无冲突；有取舍的地方在交接记录写明。

---

## S2 · 渲染运行时

**目标**：一条确定性的渲染路径：项目 → 注入文案 → 打印 CSS → 资源就绪 → 每种语言的渲染快照与 PDF → 输入指纹。

**先读**：`references/contract.md`、旧 `hb/pdf.js`、`hb/fonts.py`（字体本地化逻辑可复用）。

**归属文件**：`hb/core/render.mjs`、`project.mjs`、`print-css.mjs`、`inject.mjs`、`server.mjs`、`fingerprint.mjs`、`browser.mjs`、`cli.mjs`、`pdfboxes.py`、`font_static.py`、`setup_env.sh`（均在 `hb/core/`）、`dev/tests/core/render.test.mjs`。

**要做**：
- `print-css.mjs`：从 `project.json` 唯一生成 `@page` 尺寸、出血与 CSS 变量（`--trim-w` 等）；作者 CSS 里再声明 `@page size` 即报错。
- `inject.mjs`：按 `data-source-id` 把 `copy/<lang>.json` 注入（白名单行内标记，其余转义）；缺译、多余译文报错；应用 `lang/<lang>.css`；设置 `<html lang>`。
- `browser.mjs`：只用锁定版本的 Playwright Chromium，记录 revision；正式模式不回退系统 Chrome；拦截并拒绝所有非本项目文件的请求（记录被拒请求，有则失败）。
- `render.mjs`：等待 `document.fonts` 全部 loaded（逐个检查声明的 face 状态）、全部 `<img>` `decode()`、SVG 外部引用，带超时；检查每个 `.page` 的实际尺寸等于成品+出血；输出 `.build/<build-id>/<lang>/snapshot.html`（注入后的完整 HTML）与 `book.pdf`。
- `fingerprint.mjs`：输入指纹 = 项目内所有被引用文件（递归解析 HTML 的 src/href、CSS 的 `url()`/`@import`/`@font-face`）的内容哈希 + project.json + 工具版本 + Chromium revision；输出 `manifest.json`。
- `cli.mjs`：`node hb/core/cli.mjs render <project> [--lang zh]`。

**完成判定**：
- S1 的两个正例都能渲染，PDF 页尺寸用 `pdfinfo` 核对为 210×297mm（或声明的尺寸，含出血时为媒体框）。
- 同一项目两次独立进程渲染：`pdftoppm -r 100` 逐页像素比较一致；manifest 指纹一致。
- 改任意一个 CSS/字体/图片文件，指纹变化。
- 删掉一个字体文件、加一个外链图片：分别以非 0 退出并给出可操作的错误。
- 测试脚本 `node --test dev/tests/core/*.test.mjs` 通过。

---

## S3 · 版面测量与可读性检查

**目标**：对渲染快照做只读测量，不修改任何样式；结果按 pass / fail / unverified 报告，硬错误退出码非 0。

**先读**：契约、`hb/core/render.mjs`、旧 `hb/fill.js` 与 `hb/doctor.py`（只借鉴测量方法，不搬自动缩字逻辑）。

**归属文件**：`hb/core/measure.mjs`、`hb/core/checks/*.mjs`、`hb/core/fontcover.py`、`dev/fixtures/qa/**`、`dev/tests/core/measure.test.mjs`。

**要做**（每项都要有正例和反例 fixture）：
- 溢出与裁切：内容节点超出所在 `.page`、超出安全区（`deco` 与声明出血的图片除外）、被祖先 `overflow:hidden` 裁掉的文字、滚动溢出。
- 遮挡：内容文字与内容文字/图片重叠（`data-overlap` 声明的局部关系除外）；复杂 transform / mask / filter 判为 unverified。
- 可读性下限：按 `data-role`（缺省按 body）检查字号与对比度；背景是图片或渐变时对比度记 unverified。下限默认值取契约，project.json 只能提高。
- 字体：用 CDP `CSS.getPlatformFontsForNode` 取每个文字节点实际使用的字体，出现未声明字体（系统回退）即 fail，并列出对应字符。
- 图片：缺失、未解码、有效 DPI（自然像素 ÷ 实际显示 mm）低于 150 报 fail，`cover` 裁切比例记录到报告。
- 隐藏内容：带 `data-source-id` 的节点透明、`display:none`、在页外、字号 < 1px 都算未展示（供 S5 使用）。
- 报告：`.qa/<build-id>/<lang>/measure.json` + `measure.md`；退出码反映硬错误。

**完成判定**：
- 每个检查项至少一个反例被判 fail、一个合法版式（海报叠放、满版出血图、竖排装饰字）不误报。
- S1 两个正例全部 pass 或有理由的 unverified。
- `node --test dev/tests/core/*.test.mjs` 通过。

---

## S4 · 最终 PDF 检查与验收绑定

**目标**：验收对象是最终 PDF，不是截图；验收状态绑定输入指纹和 PDF 哈希，任何变化都让旧验收失效。

**先读**：契约、`hb/core/render.mjs` 的 manifest、旧 `hb/postflight.py`、`hb/gate.py`、`hb/lock.py`。

**归属文件**：`hb/core/postflight.py`、`hb/core/gate.mjs`、`hb/core/rasterize.py`、`dev/tests/core/gate.test.mjs`。

**要做**：
- `postflight.py`：页数与 `.page` 数一致；每页 MediaBox（及有出血时的 TrimBox/BleedBox）按 mm 核对；`pdffonts` 全部嵌入且无 Type 3；抽取每页文字供 S5 覆盖检查；缺 pypdf/poppler 时该项为 unverified，不是 pass。
- `rasterize.py`：把**最终 PDF**栅格化为逐页图与整册缩略拼图、跨页对拼图（偶数左、奇数右），供视觉审稿。
- `gate.mjs`：汇总 S3 测量、postflight、（S5 接入后）原文覆盖结果，写 `.qa/<build-id>/gate.json`：`{build_id, input_fingerprint, pdf_sha256, status, checks[]}`。任何 fail 或硬项 unverified → 状态不可交付。
- 提供 `verify` 命令：给定项目和 PDF，重新计算指纹与哈希，与 gate.json 比对。

**完成判定**：
- 正例项目得到可交付状态；改一个 CSS 后 `verify` 判失效。
- 人为卸载 pypdf（或用环境变量模拟缺失）时状态为不可交付，并指出 unverified 项。
- 页尺寸错误的 PDF（构造一份）被判 fail。
- 测试通过。

---

## S5 · 内容提取与原文覆盖

**目标**：提取与排版解耦；原文逐片段有稳定 ID；覆盖检查基于 DOM 可见性 + 最终 PDF 文本，按内容模式解释 MISSING / ORDER / EXTRA。

**先读**：契约、旧 `hb/extract.py`、`hb/doc2yaml.py`、`hb/check_copy.py`、`hb/facts.py`、`hb/images.py`、`references/adaptation.md`。

**归属文件**：`hb/core/extract.py`、`hb/core/coverage.mjs`（或 `.py`）、`hb/core/facts.py`、`hb/core/assets.py`、`dev/tests/core/test_extract.py`、`dev/tests/core/coverage.test.mjs`、`dev/fixtures/content/**`。

**要做**：
- `extract.py`：docx / pptx / md / txt / pdf → `sources/source.md` + `sources/segments.json`（每段 `{id, kind, text, origin}`）+ 抽出的图片；不决定页面结构。
- 覆盖检查：source 段 ↔ HTML `data-source-id` ↔ 渲染可见性（S3 的隐藏判定）↔ PDF 文本；四种内容模式；跨页拆段按片段序号合并；重复引用需显式登记。
- `facts.py`：数字出处检查改为扫描实际内容节点，不扫 CSS。
- `assets.py`：素材清单（来源、授权、像素尺寸），替代 images.yaml。
- 接入 S4 的 gate。

**完成判定**：用 `dev/samples/product-brochure` 的原始材料提取并构造对应的 HTML 片段，隐藏副本、透明字、页外字不被算作已展示；frozen 模式下多一句即 fail；测试通过。

---

## S6 · 长文续页工具

**目标**：确定性地把 `data-flow` 内容流拆到后续页框，写回作者源，只移动内容。

**先读**：总计划「长文与续页」、契约、S3 测量接口、旧 `hb/flow.py`（了解原续页规则）。

**归属文件**：`hb/core/paginate.mjs`、`dev/fixtures/flow/**`、`dev/tests/core/paginate.test.mjs`。

**完成判定**：24 页以上中英双语长文样例拆分后 S3 无溢出；拆分前后差异文件可读；`data-source-id` 片段序号完整，S5 覆盖检查通过；标题孤行、段首/段尾单行、图注与图分离、表格行切断有反例测试；重复运行结果一致。

---

## S7 · Campus 家族 CSS 与第一批真实样册

**目标**：一份可追溯的家族基因 + 用真实材料做出的完整样册，全部通过 S2–S4（长册通过 S6）。

**归属文件**：`families/campus/**`、`dev/samples/native/**`。

**完成判定**：家族 CSS 含颜色角色、字体角色、字号层级与可读性下限、网格与间距、低层原语、打印安全变量，无整页模板类；至少两本样册（产品册 + 含真实 CC0 照片的宣传册，其中一本 ≥ 16 页、中英双语），最终 PDF 栅格审稿记录在 `.qa/visual-review.md`。

---

## S8 · 导出与离线交付

**归属文件**：`hb/core/export.mjs`、`hb/core/pack.mjs`、`hb/core/editable_pdf.py`、相关测试。

**完成判定**：最终 PDF、可编辑 PDF（实测文字与图片与普通 PDF 一致，写明支持范围）、离线单文件 HTML（依赖闭包完整，断网打开无外部请求）、源包；源包在新临时目录、断网解包后重建，输出与原 PDF 栅格一致；导出前 `verify` 失败则拒绝正式导出，`--draft` 加水印且状态明确。

---

## S9 · Folio 联动

**归属文件**：`hb/core/folio-pack.mjs`、`hb/core/folio-sync.mjs`、相关测试；外部仓库 `folio-html-studio` 的对应改动（在该仓库单独提交）。

**完成判定**：导出编辑包 → 用 Folio 的浏览器测试脚本模拟改字、换图、拖动 → 下载 HTML → `folio-sync` 对比写回 `copy/<lang>.json`、`assets/`、`edits.css` → 重建通过；旧值不符的冲突被报告；无 ID 改动被列出；Folio 保留 ID 与构建 ID、显示构建版本、提示无 ID 修改，其原有测试仍通过。

---

## S10 · Skill 文档重写与旧引擎退役

**归属文件**：`SKILL.md`、`workflows/`、`references/`、`templates/`、`purposes/`、`brands/`、`dev/maintenance.md`、`dev/tests/selftest.sh`、旧引擎文件（移入 `dev/archive/yaml-engine/`）。

**完成判定**：SKILL.md ≤ 12000 字符且只指向新路径；全部工作流按总计划改写；旧 YAML 引擎、模板与专用测试归档并标明版本，仍有价值的回归已转成新契约测试；`grep -rn "book.yaml" SKILL.md workflows references hb/core` 无活跃引用；新 selftest 通过；经验记录格式（`experience.md`）就位。

## S11 · 视觉参考资产

**完成判定**：审计 `dev/gallery` 等现有资产并记录取舍；每个保留家族有开场、连续正文、密集信息、跨页示例（真实材料、实际 PDF 与源文件、关键决定说明）；至少两个反例含失败图与修订结果。

## S12 · 独立生成基准与审稿校准

**完成判定**：按总计划「独立生成基准」执行 6 类 × 3 次；先做人工校准（≥ 6 份）；报告首轮合格率、预算内合格率、修订次数、失败类别、人工抽查结果；未达门槛时列出失败页与原因，不降低门槛。
