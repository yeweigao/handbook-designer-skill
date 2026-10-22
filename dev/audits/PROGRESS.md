# HTML/CSS 原生改造 · 进度与交接

分步说明见 [IMPLEMENTATION-STEPS](IMPLEMENTATION-STEPS.md)。新记录追加在最下方，不改写旧记录。

## 状态表

| 步骤 | 状态 | 最近更新 | 提交 |
|---|---|---|---|
| S1 契约与最小样例 | 完成 | 2026-10-22 | 086b8b7 |
| S2 渲染运行时 | 完成 | 2026-10-22 | c4824c5 |
| S3 版面测量与可读性检查 | 完成 | 2026-10-22 | adaee42 |
| S4 最终 PDF 检查与验收绑定 | 完成 | 2026-10-22 | 21b4f2b |
| S5 内容提取与原文覆盖 | 完成 | 2026-10-22 | 98e4938 |
| S6 长文续页工具 | 完成 | 2026-10-22 | cb102a6 |
| S7 家族与真实样册（Folio CSS 扩展） | 完成 | 2026-10-22 | a190408 + bb57494 + 本次 S7 补验收提交 |
| S8 导出与离线交付 | 完成 | 2026-10-22 | ce515da |
| S9 Folio 联动 | 完成 | 2026-10-22 | c2cff36（Folio 162a616） |
| S10 Skill 文档与旧引擎退役 | 完成 | 2026-10-22 | 本提交（S10:） |
| S11 视觉参考资产 | 未开始 | | |
| S12 独立生成基准 | 未开始 | | |

状态取值：未开始 / 进行中 / 中断 / 完成 / 完成（有遗留）。

## 交接记录模板

每完成一步（或中途停下）复制下面的模板追加一条：

```markdown
### S<n> · <名称> · <完成 | 中断> · YYYY-MM-DD

- 改动范围：<新增 / 修改的文件，按目录列>
- 可复制命令：<从仓库根目录运行，能复现验收的命令>
- 完成判定逐条结果：
  - <判定 1>：pass / fail / unverified —— 证据：<输出摘要或文件路径>
- 契约变更：<无 / 改了什么、为什么、影响哪些步骤>
- 偏离计划的决定：<无 / 决定与理由>
- 新增依赖：<无 / 包名@版本与原因>
- 未完成与已知问题：<列表>
- 下一步从哪继续：<中断时必填：具体到文件和函数>
- 提交：<hash>
```

## 记录

### S0 · 准备 · 完成 · 2026-10-22

- 改动范围：新建分支 `html-native`；修订总计划（多语言共用作者源、可读性硬下限、长文续页、Folio 本地联动、可编辑 PDF 保留、经验层后移、审稿校准）；新增 `IMPLEMENTATION-STEPS.md` 与本文件。
- 环境（用户 Mac 上的 Linux 工作环境）：Node v22.23.2、Python 3.10.12、pdfinfo / pdftoppm / pdffonts / qpdf 可用；pyyaml、pillow、numpy、fonttools、pikepdf 已装；npm 与 pip 可联网；`hb/node_modules` 尚未安装（S2 处理）。
- 提交身份：本环境没有 git 全局身份，提交时用 `git -c user.name=yeweigao -c user.email=64359184+yeweigao@users.noreply.github.com commit ...`（与仓库既有提交一致）。
- 下一步：S1。

### S1 · 契约与最小样例 · 完成 · 2026-10-22

- 改动范围：
  - `references/contract.md`：contract 1 —— 项目目录、`project.json` 字段、渲染器生成的打印 CSS 与页面变量、作者 HTML 约定（页面、跨页、内容节点、片段、有意重复、角色、续排流、叠放、出血）、可读性下限表、多语言文案、内容模式、构建 ID、检查报告格式。
  - `hb/core/validate.py`：契约校验（标准库，Python 3.10）。
  - `dev/fixtures/contract/minimal-zh/`、`dev/fixtures/contract/bilingual/`：正例项目（含字体子集与 OFL 授权文本、合成跨页图）。
  - `dev/tests/core/test_validate.py`（正例 + 36 个反例 + 放宽授权 + 退出码）、`fixture_fonts.py`（样例字体子集）、`make_fixture_images.py`（合成图）、`font-licenses/`。
  - `.gitignore`：忽略 `.build/` 与样例的 `.qa/`。
- 可复制命令：
  - `python3 hb/core/validate.py dev/fixtures/contract/minimal-zh`
  - `python3 hb/core/validate.py dev/fixtures/contract/bilingual`
  - `python3 -m unittest discover -s dev/tests/core -p 'test_*.py'`
  - 改了样例文字后：`python3 dev/tests/core/fixture_fonts.py dev/fixtures/contract/<样例>`
- 完成判定逐条结果：
  - 两个正例退出码 0：pass —— 两者均「0 个错误，0 个警告」。
  - 反例退出码非 0 且指出文件与 ID：pass —— 36 个反例全部报出期望错误码；CLI 示例输出含 `book.html:28`、`copy/en.json` 与具体 ID。
  - 契约与总计划无冲突：pass（取舍见下）。
- 契约变更：首版，无。
- 偏离计划的决定：
  - 不建 JSON schema 文件、校验器用 Python 而非 Node：标准库自带 HTML 解析器，零新依赖；契约文档 + `validate.py` 是唯一权威，避免 schema 与代码两份真相。
  - 默认语言文案写在 `book.html`，`copy/` 只放其他语言，每种语言只有一个文案来源。
  - 字体只在 `project.json` 声明，作者 CSS 禁止 `@font-face`：S3 才能确定「声明过的字体」并识别系统回退。
  - 作者源禁止 `<style>` / `<link rel=stylesheet>`：样式只在 `styles` 列出的文件里，便于指纹与 Folio 写回。
  - 可读性下限按物理尺寸（px = 1/96 英寸），不随纸张缩放；降低只能经 `readability_waiver` 并始终报告。
  - 续页片段在多语言下的表示留给 S6 定义（契约只保留 `data-fragment`）。
- 新增依赖：无（fontTools、Pillow 已在 requirements 中，仅测试工具使用）。
- 未完成与已知问题：
  - `validate.py` 是静态检查，不知道实际渲染尺寸；页面尺寸、溢出、字体回退等由 S2/S3 在浏览器里检查。
  - 装订页数在作者阶段只报警告，硬检查在 S4 的 PDF 上做。
- 下一步：S2 渲染运行时。先 `cd hb && npm ci`（或 `npm install`）安装锁定的 playwright@1.64.1，并确认能拿到对应的 Chromium。

### S2 · 渲染运行时 · 完成 · 2026-10-22

- 改动范围（均在 `hb/core/`）：
  - `cli.mjs`（入口 `render`）、`render.mjs`（校验 → 组装 → 注入 → 快照 → 资源就绪 → 尺寸核对 → PDF → 清单）、`project.mjs`、`print-css.mjs`（打印 CSS 与字体 CSS）、`inject.mjs`（白名单行内标记、其余转义）、`server.mjs`（只服务项目目录的本地 HTTP，记录请求）、`browser.mjs`（锁定 Chromium、拦截外部请求、自动加载补齐的系统库）、`fingerprint.mjs`（静态扫描依赖闭包 + 工具哈希 → 构建 ID）。
  - `pdfboxes.py`：精确裁切 PDF 并写 MediaBox/CropBox/BleedBox/TrimBox。
  - `font_static.py`：可变字体实例化为静态字重。
  - `setup_env.sh`：一条命令准备环境（npm ci、下载 Chromium、无 root 时补系统库、试启动）。
  - `validate.py`：新增可变字体检查（`font.variable`）与单字重要求。
  - 样例字体改为静态实例（`NotoSansSC-400/700`、`NotoSerifSC-700`、`Inter-400/700`），`dev/tests/core/fixture_fonts.py` 改为子集 + 实例化。
  - `dev/tests/core/render.test.mjs`（9 项）；`test_validate.py` 增加 2 个反例（共 38 个）。
- 可复制命令：
  - 环境：`bash hb/core/setup_env.sh`（新会话第一次运行；Chromium 缓存在会话用户目录，换 agent 会话后需重跑）
  - 渲染：`node hb/core/cli.mjs render dev/fixtures/contract/bilingual [--lang en] [--out .build/xxx]`
  - 测试：`node --test dev/tests/core/*.test.mjs` 与 `python3 -m unittest discover -s dev/tests/core -p 'test_*.py'`
- 完成判定逐条结果：
  - 两个正例渲染、页尺寸核对：pass —— A4 无出血 `595.276 x 841.89 pts`；A4+3mm 出血 `612.283 x 858.898 pts`，TrimBox 每边内收 8.50pt。
  - 两次独立进程渲染一致：pass —— 构建 ID、指纹、快照哈希相同；`pdftoppm -r 60` 逐页 PNG 字节相同。
  - 改 CSS / 图片 / lang CSS / 译文后指纹变化：pass。
  - 删字体、加外链图：pass —— 删字体被契约校验拦下并指出文件；损坏字体在运行时报 `resource.font`；外链图（绕过静态校验）被拦截并报 `network.blocked`，退出码非 0。
  - 作者 CSS 改 `.page` 宽度：pass —— 报 `page.size`。
  - 测试：pass —— Node 9/9，Python 4/4（含 38 个反例子测试）。
  - 资源缓存冷/热：设计上每次渲染都是新浏览器、`Cache-Control: no-store`，不存在热缓存；全新机器的系统级冷环境：unverified。
- 契约变更（已同步 `references/contract.md` 与 `validate.py`）：
  - 字体必须是静态字体、`weight` 为单个值。原因：Chrome 把可变字体导出为 Type 3（实测），印刷与可编辑 PDF 都不接受。
  - 写明 PDF 页面框约定与精确裁切做法。
- 偏离计划的决定：
  - Chrome 只能输出按 1/75 英寸取整的纸张（A4 实测 594.96×841.92pt）：改为按每边多 1mm 输出，再用 pikepdf 精确裁到左上角媒体区域，内容不缩放。
  - 渲染经本地 HTTP 服务而不是 `file://`：才能拦截并记录每个请求、拒绝项目目录外文件。
  - 文案注入在浏览器 DOM 中按 `data-source-id` 替换，片段由 Node 端白名单清洗后生成。
  - `HB_CHROMIUM` 可显式指定浏览器（如云端预装 Chromium），会记入清单并改变构建 ID；不会静默回退系统 Chrome。
- 新增依赖：无新包。运行时现在必需 `pikepdf`（原已在 requirements 中；本环境装的是 10.13.0.post1，与 `requirements.lock` 的 10.17.0 不一致，未处理）。
- 环境备注：本机 Linux 虚拟机缺 `libXdamage.so.1`，`setup_env.sh` 已用 `apt-get download` 补到 `~/.local/hb-libs`，`browser.mjs` 自动加入 `LD_LIBRARY_PATH`。
- 未完成与已知问题：
  - 续页片段的多语言注入未实现，遇到即报 `inject.fragment`（S6）。
  - 页面内容是否溢出、遮挡、字号/对比度、实际字体回退均未检查（S3）。PDF 页数、字体嵌入的硬检查在 S4。
  - 审跨页用的拼图需要按 TrimBox 裁切，否则中缝出血会重复显示（S4 的 `rasterize.sh` 处理）。
- 下一步：S3、S4、S5 可并行。S3 先读 `render.mjs` 的快照与清单结构；测量应在 `snapshot.html` 上用 `emulateMedia({ media: 'print' })` 进行，与 PDF 同源。

### S3 · 版面测量与可读性检查 · 完成 · 2026-10-22

- 改动范围：
  - `hb/core/measure.mjs`：在快照上以打印媒体只读测量；对比度用"隐藏全部文字后截图"取真实背景；字体回退用 CDP `CSS.getPlatformFontsForNode`；写 `.qa/<构建 ID>/<语言>/measure.json` 与 `measure.md`；硬项 fail 或 unverified 时退出码非 0。
  - `hb/core/checks/collect.mjs`：浏览器内收集与几何检查（出页面、出安全区、容器裁切、文字互相遮挡、文字压图、字号下限、伪元素文字、图片有效分辨率、出血与出血不足、内容不可见、复杂变换提示）+ 对比度采样。
  - `hb/core/fontcover.py`：算出没有任何声明字体覆盖的字符，写进回退报告。
  - `hb/core/cli.mjs` 新增 `measure` 命令；`browser.mjs` 共享 `waitResources`；`fingerprint.mjs` 新增 `makeTools`，工具哈希改为递归包含 `checks/`（修复：之前改检查代码不会改变构建 ID）。
  - 样例：`dev/fixtures/qa/base/`（3 页：满版出血海报、声明的文字叠放、旋转装饰字、分栏正文、行内图、上标、页码伪元素、三边出血色带、溢出隐藏引文框）；`contract/` 两个样例改为 8mm 安全区 + CSS 版心边距，双语封面眉标颜色修正（S3 首次运行即查出其对比度仅 1.4:1）。
  - 测试：`dev/tests/core/measure.test.mjs`（正例 1 + 反例 18 + 旋转提示 1 + 放宽授权 1）；`test_validate.py` 正例加入 QA 样例。
- 可复制命令：
  - `node hb/core/cli.mjs render dev/fixtures/qa/base && node hb/core/cli.mjs measure dev/fixtures/qa/base`
  - `node --test dev/tests/core/measure.test.mjs`（约 90 秒；本环境下长命令建议后台运行并读日志）
- 完成判定逐条结果：
  - 每个检查项至少一个反例被判硬项失败：pass —— overflow.page、overflow.safe（含页码伪元素）、clip.text、overlap.text、overlap.image、readability.size（含伪元素）、readability.contrast（纯色背景与压图两种）、font.fallback（缺字、字体栈两种）、image.dpi、image.bleed（出血不足、未声明两种）、content.hidden（透明、display:none、<1px、透明色）共 18 个反例全部命中。
  - 合法版式不误报：pass —— 满版出血图、声明的叠放、旋转装饰字、页边页码、三边出血色带、溢出隐藏但放得下的引文框均为 0 硬项。旋转的内容文字只给 `geometry.unverified` 提示，不阻断。
  - 两个契约样例全部 pass：pass。
  - 测试：pass —— Node render 9/9、measure 21/21，Python 4/4。
- 契约变更（已同步 `references/contract.md`）：`safe_mm` 明确为印刷安全区（所有文字含页码必须在内），不是版心边距；版心由作者 CSS 定义。样例与契约示例改为 8mm。
- 偏离计划的决定：
  - 对比度不把"背景是图片/渐变"一律记为 unverified，而是实际测量：隐藏文字截图后在文字矩形内采样，取第 5 百分位对比度（同时给出最小值和中位数）。只有渐变文字（background-clip:text）与复杂变换记为待目检提示。
  - 内容文字带旋转/斜切、filter、mask、clip-path 时，几何检查记为 hint 级 unverified（交给视觉审稿），不阻断交付。
  - 伪元素文字（页码等）没有可测矩形：非绝对定位时用宿主盒子近似检查位置，绝对定位时给提示。
  - 可读性下限：放宽只能来自 `readability_waiver`，报告里始终保留一条说明。
- 新增依赖：无。
- 未完成与已知问题：
  - CSS 背景图的分辨率只给提示（未测）；SVG 内文字的字号与位置只给提示。
  - 未检测"伪粗体"（声明字重缺失时浏览器合成加粗）。
  - 对比度采样基于屏幕截图（打印媒体模拟），与最终 PDF 栅格可能有细微差异；最终以 S4 的 PDF 审稿为准。
  - 文字互相遮挡按行框计算，行距很紧的大标题若行框相交但字形不相交，可能误报，需要用 `data-overlap` 声明。
- 下一步：S4（验收绑定，汇总 measure.json）与 S5（内容覆盖）可并行。S5 的"内容是否可见"可直接读 `measure.json` 里的 `content.hidden` 项。

### S4 · 最终 PDF 检查与验收绑定 · 完成 · 2026-10-22

- 改动范围（`hb/core/`）：
  - `postflight.py`：只看最终 PDF——哈希与渲染清单一致、页数、逐页 MediaBox/TrimBox 物理尺寸（±0.05mm）、装订页数、字体全部嵌入且无 Type 3（递归表单 XObject）；用 pdftotext 逐页抽字写 `pdf-text.json`（供 S5）。缺 pikepdf / poppler 时相应项为硬项 unverified。
  - `rasterize.py`：最终 PDF → 逐页图（110dpi，含出血）、整册缩略图与面对页拼图（按成品裁切，左右页按 `first_page` 推出）。
  - `gate.mjs`：`check`（渲染 → 测量 → postflight → 栅格 → 原文覆盖 → `.qa/<构建 ID>/gate.json` 与 `gate.md`）与 `verify`（重算当前源指纹与 PDF 哈希，与 gate.json 比对）。原文覆盖通过动态加载 `coverage.mjs` 接入；模块不存在时为硬项 unverified。
  - `cli.mjs` 新增 `check`、`verify`。
  - 测试 `dev/tests/core/gate.test.mjs`（6 项）。`.gitignore` 新增 `dev/.preview/`（本地预览图中转，因设备暂存限制 7 层目录）。
- 可复制命令：
  - `node hb/core/cli.mjs check dev/fixtures/contract/bilingual`
  - `node hb/core/cli.mjs verify dev/fixtures/contract/bilingual`
  - `node --test dev/tests/core/gate.test.mjs`（约 50 秒）
- 完成判定逐条结果：
  - 正例得到可交付状态：**部分** —— 渲染、测量、PDF 检查、栅格四项全部 pass；因原文覆盖（S5）尚未实现，按"未运行即阻止"如实判为 blocked，唯一阻止项是 `coverage.missing`。S5 接入后此项应转为可交付，并需把 `gate.test.mjs` 第 1 项的断言改为 `deliverable`。
  - 改一个 CSS 后 `verify` 判失效：pass —— 报"当前源没有验收记录"。
  - PDF 在验收后被改动：pass —— 报"PDF 在验收后被改动"。
  - 缺 pypdf/pikepdf 时不可交付并指出 unverified 项：pass（用 `HB_POSTFLIGHT_NO_PIKEPDF=1` 模拟，4 项 unverified）。
  - 页尺寸错误的 PDF：pass —— 报 `pdf.boxes` 与 `pdf.hash`。
  - 额外：骑马钉 3 页报 `pdf.binding`；可变字体产生的 Type 3 被 `pdf.fonts` 查出。
- 契约变更：无。
- 偏离计划的决定：
  - 栅格脚本用 Python（`rasterize.py`）而不是 shell：需要按出血精确裁切并拼图，PIL 已在依赖内。
  - 检查器本身不依赖 pypdf，统一用 pikepdf（渲染已必需）。
  - gate.json 预留 `visual_review: "not-recorded"`；视觉审稿记录与导出前的要求由 S8 / S10 定义。
- 新增依赖：无。
- 未完成与已知问题：
  - gate 不检查视觉审稿是否完成（S8 导出前处理）。
  - `verify` 需要启动一次浏览器读取版本号（参与指纹），约 0.5 秒。
- 下一步：S5 原文覆盖。实现 `hb/core/coverage.mjs`，导出 `coverage(dir, buildId, lang)`，返回 `{status, items}`（契约 §7 格式），并写 `.qa/<构建 ID>/<语言>/coverage.json`；输入可用 `measure.json` 的 `content.hidden` 与 `pdf-text.json`。

### S5 · 内容提取与原文覆盖 · 完成 · 2026-10-22

- 改动范围（`hb/core/`）：
  - `extract.py`：原稿（md / txt / docx / pdf / pptx）→ `sources/original/`、`source.md`、`segments.json`（稳定 ID `s0001…`，kind：heading / para / item / cell / artifact）、`images/`、`assets.json`（新图片登记为待确认授权，不覆盖已填写条目）。不决定页面结构。
  - `office_extract.py`：旧 `hb/extract.py` 原样迁入（PPT 文字与图片、Word/PDF 图片），S10 退役旧引擎时无需再搬。
  - `coverage.py` + `coverage.mjs`：三方证据核对——原文段 ↔ 快照中可见的内容节点（排除 `measure.json` 的 `content.hidden`）↔ 最终 PDF 文字层。默认语言：MISSING、ORDER、EXTRA、无出处数字；所有语言：可见内容必须进入 PDF 文字层；素材：非装饰图片必须登记来源与授权。已接入 gate。
  - `postflight.py`：PDF 抽字改用 `pdftotext -raw`（默认模式会把两栏正文交错，导致误判）。
  - 契约：§5 内容模式表更新；新增「原文与素材（sources/）」小节（segments、adapt.json、facts.md、assets.json）。
  - 样例：三个样例都补了 `sources/original/原稿.md` 与提取结果；双语与 QA 样例登记了合成图素材；QA 样例的图片加 `data-asset`，并用 `adapt.json` 声明设计添加的序号。
  - 测试：`dev/tests/core/coverage.test.mjs`（12 项）；`gate.test.mjs` 第 1 项改为断言可交付且 `verify` 有效；`measure.test.mjs` 一处查找串随样例更新。
- 可复制命令：
  - `python3 hb/core/extract.py <原稿> <项目>`
  - `node hb/core/cli.mjs check dev/fixtures/contract/bilingual`（现在为「可交付（技术检查）」）
  - `node --test dev/tests/core/coverage.test.mjs`（约 3 分钟，建议后台运行）
- 完成判定逐条结果：
  - 提取与排版解耦、稳定 ID：pass —— product-brochure 原稿 160 段，重提取 ID 不变；docx（标题/段落/列表/表格）与 pptx（标题/正文）分段正确；统计数字「24」不再被误当页码。
  - 隐藏副本、透明字、页外字不算已展示：pass —— 4 种隐藏方式均判 `coverage.missing` 硬项。
  - frozen 模式多一句即 fail：pass —— 设计添加的 aux 文字在冻结模式判 EXTRA 硬项，顺序调整判 ORDER 硬项；搬运模式下顺序只作提示；冻结模式拒绝 adapt.json。
  - 其他：自创句判 EXTRA；润色模式缺段只提示；adapt.json 声明省略后通过；PDF 文字层缺失（中、英）判硬项；素材授权空缺与未登记都阻止交付；无出处数字只提示。
  - 接入 gate：pass —— 三个样例全部「可交付」，gate 测试 6/6。
  - 回归：Node render 9/9、measure 21/21、gate 6/6、coverage 12/12；Python 4/4。
- 契约变更：`translate` 模式下默认语言按 carry 严格检查；`polish` 下 MISSING/EXTRA/ORDER 为提示；新增 `sources/` 约定。
- 偏离计划的决定：
  - 数字出处与素材清单合并进 `coverage.py`（不再单独建 `facts.py`、`assets.py`），共用同一次快照解析。
  - 覆盖按文本句子匹配，而不是要求作者源的 `data-source-id` 与原文段 ID 一一对应：作者可以自由拆分、合并段落，内容 ID 仍服务于多语言和编辑回写。
  - 数字出处仍只作提示（与旧引擎一致）。
- 新增依赖：无（python-docx、python-pptx、markitdown、pandoc 在本环境已有；markitdown/pandoc 缺失时 docx 回退到 python-docx）。
- 未完成与已知问题：
  - PDF 原稿只抽文字与图片，不保留版面结构；扫描版 PDF 没有文字层时提取为空（需 OCR，未做）。
  - 续页片段（S6）的跨页句子在 PDF 文字层中可能被页眉页脚隔开：PDF 层检查是按内容节点各自的句子进行的，片段各自独立核对，已考虑；S6 落地后需加回归。
  - 译文与原文的语义对应（是否译错）不做自动判断，属于语义审稿。
- 下一步：S6 续页工具（依赖 S3 已完成）；S7、S8、S9 的依赖也已满足，可以分给不同 agent 并行。

### S6 · 长文续页工具 · 完成 · 2026-10-22

- 改动范围：
  - `hb/core/checks/flow.mjs`：浏览器内续排算法（合并旧片段 → 依次填框 → 必要时按最后一个文字框所在页克隆续页 → 片段编号 → 跨页左右位置检查）。只移动内容。
  - `hb/core/paginate.mjs` 与 `cli.mjs paginate`：默认语言续排并写回 `book.html`（只替换 `<body>` 内的页面，`<head>` 原样保留），输出 `.qa/paginate/book.html.diff` 与 `report.json`；有错误时不写回。
  - `hb/core/render.mjs`：其他语言在注入前合并片段、注入后用同一算法重新续排（结果记入清单 `flows`）；组装阶段改为打印媒体并在续排前等待字体与图片。原「片段多语言注入未实现」的报错移除。
  - 契约：新增 `data-flow-keep`、`data-flow-generated`，写明文字框必须固定高度与续排规则。
  - 样例：`dev/fixtures/flow/long-bilingual/`（由 `dev/tests/core/make_flow_fixture.py` 生成；提交的是**未分页**状态，直接 check 会溢出，测试先复制再 paginate）。
  - 测试：`dev/tests/core/paginate.test.mjs`（6 项）。
- 可复制命令：
  - `node hb/core/cli.mjs paginate <项目> [--flow <名称>]`
  - `node --test dev/tests/core/paginate.test.mjs`（约 2 分钟）
- 完成判定逐条结果：
  - 24 页以上中英双语长文拆分后无溢出：pass —— 中文 25 页（新增续页 22），英文渲染时续排为 39 页；`check` 中英两版均「可交付」（测量、PDF、原文覆盖全过）。
  - 差异文件可读：pass —— `.qa/paginate/book.html.diff`（统一 diff 格式）。
  - 片段编号完整、覆盖检查通过：pass —— 契约校验通过；原文覆盖与 PDF 文字层检查通过。
  - 标题孤行、段首/段尾单行、图注与图分离：pass —— 报告中所有框末块不是标题，所有片段 ≥ 2 行，图片与图注作为整体移动。表格行切断：表格按整体不拆（未单独构造表格反例）。
  - 重复运行结果一致：pass —— 第二次 paginate「无需改动」，作者源字节不变；英文两次渲染快照哈希相同。
  - 反例：文字框没有固定高度 → `flow.unbounded` 且作者源不变；图比文字框还高 → `flow.too-large`。
  - 回归：Node 48/48（render、measure、gate、coverage）+ paginate 6/6；Python 4/4。
- 契约变更：见上（新增属性与续排规则）。
- 偏离计划的决定：
  - 除句末外允许在可断行处拆分：只按句末拆时，每段只有约 5 个拆点，框底常空 2–4 行。现在先试句末，句末拆完仍空一行以上才改为行尾拆（中日韩字之间、空格后，避头尾）。本样例结果：拆分 4 段，均为行尾拆。
  - 片段首尾各至少两行（与 CSS 默认 orphans/widows 一致）：段间距 14px 时框底需 ≥ 70px 才能放下两行，因此仍会有 ≤ 约 2.5 行的框底空白；标题前的空白可达标题高度 + 两行。这是孤行控制的代价，不再进一步压缩。
  - 其他语言不写回作者源，而在渲染时续排：作者源只有一份，译文长度不同；续页只存在于该语言的快照与 PDF 中。
- 新增依赖：无。
- 未完成与已知问题：
  - 续页按最后一个文字框所在页克隆：该页的装饰与结构元素（页码、页眉）会复制；图片、内容节点与其他流的文字框会被移除。需要不同版式的续页时，作者应自己多放几个文字框。
  - 插入续页导致后面的跨页左右错位时只报错（`flow.spread-shift`），不自动补空白页。
  - 列表、表格不拆；超长表格需要作者拆成多个表。
  - 其他语言的续页在 Folio 中编辑时，回写只能按内容 ID 合并到 `copy/<lang>.json`（S9 处理）。
- 下一步：S7（Campus 家族与真实样册）、S8（导出）、S9（Folio）依赖都已满足，可并行。

### S7 · Campus 家族与真实样册 · 完成 · 2026-10-22

- 改动范围：
  - `families/campus/`：家族 CSS（颜色/字体/字号角色、可读性下限内的字号阶梯、六栏网格与 28px 基线、排印/线/引文/图框/清单/步骤/深色面/压暗层/页码页眉原语，无整页模板类）、`family.json`、README；`families/licenses/`。
    - v1.1（本次）：英文版 `font-variant-east-asian: proportional-width` 写到每个元素（`font` 简写会重置它），修正宋体/黑体里 ’ “ ” 全角；`hyphenate-character: "-"`（思源字体的 U+2010 是全角）。v1 的纯中文项目不受影响。
  - `hb/core/family.py`：`list / init / fonts`，从家族建项目（复制家族 CSS、按 GB2312 + 项目文字子集字体、写 project.json 的 family 名/版本/sha256）。
  - `dev/samples/native/product-brochure/`（12 页中文纯文字，提交 a190408）。
  - `dev/samples/native/nature-camp/`（16 页中英双语，9 张 Wikimedia Commons 公有领域照片）：`book.html`、`book.css`、`copy/en.json`、`sources/`（原稿、segments、adapt.json 声明设计添加的照片署名/书名/页眉、assets.json 逐张写来源页/授权/作者）、`brief.md`、`page-plan.md`、`experience.md`、`.qa/<构建>/gate.json + visual-review.json`。
- 可复制命令：
  - `node hb/core/cli.mjs check dev/samples/native/nature-camp` → 构建 c063f2f71ce6，中英两版 render/measure/postflight/raster/coverage 全 pass
  - `node hb/core/cli.mjs verify dev/samples/native/nature-camp` → 有效
  - `node hb/core/cli.mjs check dev/samples/native/product-brochure` → 3d1f501feb03 可交付
  - 新项目：`python3 hb/core/family.py init campus <目录> --title … --langs zh-CN,en --mode translate`
- 完成判定逐条结果：
  - 家族 CSS 含颜色/字体/字号/网格/间距/低层原语/打印安全变量，无整页模板类：pass —— `families/campus/design.css`；两本样册的整页构图都写在各自 `book.css`。
  - 至少两本样册，其中含真实 CC0/公有领域照片、≥16 页、中英双语：pass —— 产品手册 12 页中文；山海自然探索营 16 页中英，照片授权逐张登记，封底署名并注明"拍摄地与营地无关，仅作示意"。
  - 全部通过 S2–S4（与 S5 原文覆盖）：pass —— 见上方构建 ID。
  - 最终 PDF 栅格审稿记录：pass —— 两本的 `.qa/<构建>/visual-review.json` 均为 deliverable，绑定 PDF 哈希。
- 检查在样册上抓到的真问题（都已修，记录在各自 `experience.md`）：压在亮云/亮岩上的序号与眉标对比度不足；`-webkit-text-stroke` 描边字在 PDF 里变 Type 3；大数字行高过小与说明文字重叠；标题孤字与拆词；`.mono` 字体栈缺中文导致回退。视觉审稿另外抓到：英文标点与连字符全角、多页下部大片空白、封面裁切里的告示牌、署名被截断。
- 契约变更：无。
- 偏离计划的决定：
  - 照片来自 Wikimedia Commons 的美国林务局/土地管理局/国家公园管理局公有领域作品（不是严格意义的 CC0，但同样无需授权）；拍摄地与"营地"无关，所以往届回顾页不配照片，避免让人以为是实拍。
  - 家族在样册过程中升到 v1.1；产品手册仍记录 v1（纯中文，不受影响），不强制升级。
  - 样册的 `book.html` 是用一次性脚本从原稿模板填出来的，之后作为作者源直接维护；脚本不入库。
- 新增依赖：无。
- 未完成与已知问题：
  - 自然营素材 21MB（图片 13MB：封面只用到原图 40% 宽度，再压缩会过不了栅格分辨率检查）。
  - 中文行末标点被 Chrome 默认 `text-spacing-trim` 挤压成半宽，属正常排印，未改。
  - 第 10 页（深色纯文字）中部留白偏大，审稿判可接受。
- 下一步：S10（Skill 文档重写与旧引擎退役）、S11（视觉参考资产）可并行开始。
- 提交：见 git log（S7 收尾提交）

### S8 · 导出与离线交付 · 完成 · 2026-10-22

- 改动范围（`hb/core/`）：
  - `export.mjs` 与 `cli.mjs review / export`：
    - `review <项目> --verdict deliverable|excellent|fail --by <审稿人> [--notes <文件>]`：仅在技术验收有效时，把视觉审稿结论绑定到当前构建 ID 与各语言 PDF 哈希（`.qa/<构建 ID>/visual-review.json`）。
    - `export <项目> [--name <文件名>]`：verify 有效 + 视觉审稿为可交付/优秀，才在 `out/.staging-<构建 ID>/` 生成交付物并逐项实测；全部通过才改名发布到 `out/<文件名>/`，失败保留暂存目录供诊断。
    - `export --draft`：不需要验收，在 PDF 上叠加「草稿 DRAFT」水印（不重新渲染），输出到 `out/<文件名>-draft/`。
  - `editable_pdf.py`：不重新渲染，把 PDF 里每个嵌入字体替换为同一项目字体的扩充版（GB2312 常用字 + 拉丁 + 本书用字，`retain_gids` 保持字形编号）；保留 Chrome 写入的宽度表、只给新增字形补宽度；去掉子集前缀。
  - `offline_html.py`：快照 → 单文件 HTML（样式表递归 @import、CSS url、img/srcset、style 属性、SVG href 全部内嵌）；网络地址、项目外文件、缺失文件一律报错。
  - `pack.py`：源文件包 = 构建清单全部输入 + brief/page-plan/experience + `sources/` 全部 + 字体与素材旁的授权文本 + `REBUILD.md`（重建命令、预期构建 ID、工具版本）；不含 `.build/.qa/out`。
  - `compare_pdf.py`：两份 PDF 逐页栅格对比（差异像素比例）。
- 交付物（每种语言）：`<名>.<语言>.pdf`、`.editable.pdf`、`.html`、`.sheet.png`、`.spreads.png`；另有 `<名>.source.zip`、`credits.md`（素材与字体来源授权）、`delivery.json`（检查结果与每个文件哈希）。
- 可复制命令：
  - `node hb/core/cli.mjs check <项目> && node hb/core/cli.mjs review <项目> --verdict deliverable --by <审稿人> && node hb/core/cli.mjs export <项目> --name <文件名>`
  - `node --test dev/tests/core/export.test.mjs`（约 2.5 分钟）
- 完成判定逐条结果：
  - 最终 PDF：pass —— 复制自验收的 PDF，哈希与 gate 一致。
  - 可编辑 PDF：pass —— 字体非子集、无 Type 3；中英两版与正式版 60dpi 逐页**零像素差异**，文字层相同。支持范围：Chrome 导出、静态 TrueType 字体；扩充字库为 GB2312 + 拉丁 + 本书用字。**未在 Acrobat 等编辑器里实测改字**（本环境没有），这一点记为 unverified。
  - 离线 HTML：pass —— 浏览器打开时除 data: 与文件本身外无任何请求，字体与图片全部就绪；打印出的 PDF 与正式版逐页一致（容差 0.1%，实测 0）。
  - 源文件包重建：pass —— 在新的临时目录解包后运行 check，构建 ID 与原构建相同、验收通过、逐页栅格零差异。渲染器本身拒绝一切外部请求，因此即"断网"重建；系统级断网（关闭网卡）未单独验证。
  - verify 失败拒绝正式导出：pass —— 没有验收、没有审稿、审稿不合格、PDF 在验收后被改动，四种情况都拒绝，且不留下发布目录。
  - `--draft` 水印与状态：pass。
  - 回归：export 4/4、gate 6/6。
- 契约变更：无（`visual-review.json` 是新的 .qa 产物）。
- 偏离计划的决定：
  - 可编辑 PDF 改为直接替换嵌入字体，不再像旧引擎那样用扩充字库重新渲染：省一次渲染，并保证版式与正式版逐像素一致。
  - 视觉审稿结论用 `review` 命令落为绑定构建的记录；正式导出强制要求它。审稿本身怎么做由 S10 的 visual-review 工作流规定。
  - 离线 HTML 保留原图，不缩小（与 PDF 同源，便于核对）；大量照片的书 HTML 会很大，S10 可以视需要增加"屏幕版"选项。
  - 草稿水印用叠加方式，正式 PDF 不受影响。
- 新增依赖：无。
- 未完成与已知问题：
  - PDF 书签（旧引擎有）没有迁移：需要章节结构信息，留给 S10（可从 h1/h2 与 data-page-id 生成）。
  - 文件名会保留书名里的全角标点；跨平台分发若有问题，用 `--name` 指定。
  - Pillow 14 将移除 `getdata`，`compare_pdf.py` 已改用 histogram。
- 下一步：S9（Folio 联动）。S7（家族 CSS 与真实样册）也可以开始。

### S9 · Folio 联动 · 完成 · 2026-10-22

- 改动范围（本仓库）：
  - `hb/core/folio.mjs` 与 `cli.mjs folio-pack <项目> [--lang] [--name]`：当前源对应构建的快照 → 离线单文件 HTML + 构建标记（`hb-contract / hb-build / hb-lang / hb-title`），写到 `out/folio/<名>.<语言>.folio.html`；同一份存为 `.build/<构建 ID>/<语言>/folio-base.html` 作写回基准。
  - `hb/core/folio_sync.py` 与 `cli.mjs folio-sync <项目> <下载的 HTML> [--dry-run]`：三方比对（编辑包基准 ↔ Folio 交回的 HTML ↔ 当前作者源）。
    - 改字：默认语言按片段写回 `book.html`；其他语言合并片段后写回 `copy/<语言>.json`；富文本按白名单清洗（b→strong、i→em、换行→br）。
    - 换图：新图存为 `assets/images/folio-<编辑 ID>-<哈希>`，改作者源的 `src` 与 `data-asset`，在 `sources/assets.json` 登记且授权留空（交付前必须确认）。
    - 样式与位置：`data-folio-overrides` 与 `folio-shared-styles` 批量规则 → `edits.css`（按 `data-edit-id` / `data-source-id` / `.page` 选择器；其他语言限定 `html[lang]`）。
    - 冲突（作者源在导出编辑包后改过）不覆盖；没有 ID 的改字、换图、样式列为未写回。
    - 用户改字记入 `sources/user-edits.json`，原文覆盖检查视为用户认可的改动（`coverage.py` 相应更新）。
  - 契约：`sources/user-edits.json` 说明。
  - 测试：`dev/tests/core/folio.test.mjs`（模拟写回 2 项 + 真实 Folio 界面往返 1 项）。
- 改动范围（`folio-html-studio`，分支 `hb-package`，提交 162a616）：
  - `src/bridge.js`：读取构建标记；选中对象时给出 `sourceId / editId / traceable{text, style, image}`。
  - `src/App.tsx`、`src/types.ts`、`src/style.css`：顶栏显示「基于构建 xxx · 语言」；对不可写回的修改在属性面板给出提示（仍允许修改）。
  - `tests/handbook-package.test.mjs`；README 增加联动说明。不新增导出功能，不需要服务器。
- 可复制命令：
  - `node hb/core/cli.mjs folio-pack <项目>` → 在 Folio 导入 `out/folio/*.folio.html` → 下载 HTML → `node hb/core/cli.mjs folio-sync <项目> <下载的 HTML>` → `check`
  - 本仓库：`node --test dev/tests/core/folio.test.mjs`（会启动 `../folio-html-studio` 的开发服务器；找不到时真实往返项跳过）
  - Folio 仓库：`npm test`（本机 Linux 虚拟机需 `LD_LIBRARY_PATH` 指向 `~/.local/hb-libs` 补的系统库）
- 完成判定逐条结果：
  - 真实界面往返：pass —— 在 Folio 里改导语、拖动标题、给跨页图换一张 2600×1850 的新图 → 下载 → folio-sync 写回 `book.html`、`edits.css`、新图片与素材登记 → 授权未确认时 check 不可交付 → 确认授权后 check **可交付**。
  - 旧值不符的冲突被报告：pass —— 同一份修改再次写回时全部判冲突、作者源字节不变；其他语言的译文在导出后被改过时判冲突、不覆盖。
  - 无 ID 改动被列出：pass —— 无 ID 的新段落、无 ID 色块的样式都列入「未写回」。
  - Folio 保留 ID 与构建标记、显示构建版本、提示无 ID 修改：pass —— Folio 新测试；顶栏显示与提示文案经截图确认。
  - Folio 原有测试：pass —— 10/10。
  - 回归：coverage 12/12。
- 契约变更：新增 `sources/user-edits.json`；原文覆盖在所有内容模式下承认用户本人的修改。
- 偏离计划的决定：
  - 不另做"修改清单导出"，交回的就是 Folio 正常下载的 HTML（与用户确认过的方案一致）。
  - 用户改字以"用户认可的改动"记录，覆盖检查据此放行；冻结模式也承认（沿用旧引擎规则）。agent 自己的改写不能用这个文件。
  - 写回的样式统一加 `!important` 追加在 `edits.css` 末尾（与 Folio 的覆盖语义一致），文件头注明"待审阅"。
- 新增依赖：本仓库无；Folio 仓库无新依赖（`npm ci` 安装既有锁定依赖）。
- 环境备注：Playwright 的 `locator.click` 会把比页面还宽的跨页图滚到中央（连 `overflow:hidden` 的页面也会被程序化滚动），测试里改为按可见位置用鼠标点击；真实用户点击不受影响。
- 未完成与已知问题：
  - Folio 的品牌图形内部样式（`graphicStyles`）不写回，会列为未写回。
  - 其他语言的续页在 Folio 中拖动位置时，样式写回限定在该语言的 `html[lang]` 下，但目标是渲染时生成的片段编号，重新续排后可能对不上；建议其他语言只改字。
  - Folio 仓库改动在 `hb-package` 分支，尚未合并到 main、尚未部署。
- 下一步：S7（Campus 家族 CSS 与真实样册）、S10（Skill 文档重写与旧引擎退役）。S10 依赖 S7 的家族与样册路径。

### S10 · Skill 文档重写与旧引擎退役 · 完成 · 2026-10-22

- 改动范围：
  - `SKILL.md`：HTML/CSS/SVG 唯一作者源，路线、授权边界、家族/构图分工、内容/语言、技术与视觉验收、导出及按需文档路由；4,199 字符。原 `agent_created` 移入合法 metadata。
  - `workflows/` 九条工作流、`references/` 十份作者指南全部改写；移除固定多轮确认、布局枚举入口、自动缩字及后台字体替换说明。契约保持工作区原样。
  - `templates/`：brief、page-plan、experience、visual-review Markdown；`purposes/`：五种用途转为内容任务/审稿指南；`brands/`：虚构 Acme 的 CSS/资源与说明，不再自动加 logo/联系方式。
  - `dev/archive/yaml-engine/`：107 份原引擎/模板/配置/专用测试/文档按迁移前字节保留，另加 README 与 VERSION.json；基线 `bb574941a5b13462720c9918b8a4584c727d7744`，说明冻结、重现方法和新回归归属。旧 gallery/previews/samples 原位保留，交 S11 审计。
  - `dev/maintenance.md` 与 `dev/tests/selftest.sh`：责任表、依赖成本、经验边界；quick 检查静态/链接/语法/契约，完整模式加全部 core 测试和隔离真实样册 check/verify，不自动安装依赖。
  - 归档必要解耦：`hb/core/family.py` 去除指向退役字体下载器的报错命令；`office_extract.py` 的联系表字体复用现有本地源查找，不再 import 旧 fonts 模块，更新说明。
  - 经用户本轮明确允许，修改 `dev/tests/core/export.test.mjs`（水印文本空格可选）与 `folio.test.mjs`（读取 HB_CHROMIUM、避开悬浮工具条发起真实拖动），保留原结果断言。
- 可复制命令（从仓库根目录）：
  - `bash dev/tests/selftest.sh --quick`
  - 完整自检：`HB_CHROMIUM="<已有浏览器可执行文件>" PYTHONPATH="<已有依赖目录>" bash dev/tests/selftest.sh`；常规已配置环境不必设置两项。没有自动浏览器回退，显式版本记入 manifest。
  - `python3 /Users/apple/.codex/skills/.system/skill-creator/scripts/quick_validate.py .`（本机 Skill 格式校验器）
  - `grep -rn "book.yaml" SKILL.md workflows references hb/core`（无输出，退出码 1）。
- 完成判定逐条结果：
  - Skill ≤ 12000 字符、只指向新路径：pass —— 4,199 字符；Skill 格式合法、34 份文档链接存在，活跃入口无旧作者源引用。
  - 全部工作流按总计划改写：pass —— 九条路线均使用原生作者源与当前公开命令，涵盖冻结、系列、品牌、研究、Folio、安全回写与最终 PDF 全页审改。
  - 旧链路归档并注明版本、有价值回归迁移：pass —— 107 个归档源文件与基线逐字节一致；README 按能力列出现行 core 正反例，不保留兼容入口，不删除旧失败证据。
  - 新 selftest：pass —— Python 4/4，Node 61/61（零失败、零跳过，含真实 Folio 改字/拖动/换图往返）；两本真实样册的所有语言 render/measure/postflight/raster/coverage 均 pass，verify 有效。产品手册构建 `83a86b17eae4`；自然营中英构建 `266eb68f015e`。最后文档微调后 quick 也通过（`hb-native-selftest.YYV4GJ`）。
  - experience 格式与写入职责：pass —— `templates/experience.md` 与各流程、维护文档，含材料条件/观察/修改/证据/适用范围/未验项，不自动晋升。
  - 带图片 Word 提取及联系表：pass —— 临时目录 `hb-s10-office-0qns7vjb`，两段文字、一张图片和联系表生成；授权保持待确认。
- 验证环境与证据：
  - 最终 selftest 目录：`/var/folders/cd/w5hb78m12v3cpcs3cmc_zkwh0000gn/T/hb-native-selftest.5GO6AQ/`（static.log、validate-tests.log、browser.log、core-tests.log、样册 check/verify 日志及 `.build/.qa`）。
  - Node 24.9.0、Python 3.13.3、Playwright 1.64.1、显式本机 Chromium 149.0.7827.55；复用 `/tmp/hb-editorial-test-deps` 的 pikepdf 10.17.0 等已有包。本轮没有新增安装或依赖。
  - 首轮全测 59/61；水印提取空格与外部测试未读浏览器选项导致两项失败，保留首轮日志 `hb-native-selftest.R6fqyz/core-tests.log`。Folio 实际拖动又暴露浮动工具栏遮挡旧测试坐标，截图定位后修正手势，真实往返单测已通过。
- 契约变更：本步骤无。开工时已有 `hb/core/pdfboxes.py`、`render.mjs`、`validate.py` 和 `references/contract.md` 四个未提交文件，字节完整保留且不纳入本提交；本轮验证基于包含这些预存改动的工作区，未单独验证只含 S10 提交的干净 checkout。
- 偏离计划的决定：
  - 字体资源准备与 Office 联系表两处解耦随旧引擎退役完成，否则新链路仍引用已退役的 helper；没有恢复字体下载、系统字体替换或旧布局。
  - 用户质疑整套依赖成本后停止下载尝试，改为显式复用已有 Chromium；文档区分实际模块依赖和未实现的轻量默认路径，`requirements*` 未改。
  - 经用户明确允许扩展两处现有测试文件的环境适配；没有放宽实际水印存在、拖动写回或交付门禁要求。
- 新增依赖：无。
- 未完成与已知问题：
  - Node 22 / Python 3.10 的参考运行环境未实测（unverified）；做了 Python 3.10 语法检查，全部运行结果以上述实际环境为准。精确版本复现不能等同本轮环境复用。
  - 依赖分层、轻量默认运行路径及按功能加载尚未实现，需要后续调整 S2–S4 的契约与运行时；已写入 maintenance。当前 hb/requirements* 仍含历史组件，不要求每次安装全部。
  - 可编辑 PDF 在 Acrobat 等编辑器实际改字的既有 unverified 保留；本轮没有新视觉审稿或重做 S12 独立生成/人工校准。
- 下一步：S11 视觉参考资产（审计 gallery、原生样册与反例）；S12 在 S11 后继续，不把 S10 技术回归冒充独立创作评测。
- 提交：本记录所在的 `S10:` 提交（见 git log）。


### S7 · 全页补验收与构图纠正 · 完成 · 2026-10-22

- 重新打开的原因：旧记录标为完成，但审稿只抽看部分页面，且以公有领域照片替代了明确要求的 CC0。补审期间用户进一步指出“侧边线 + 浅底色”的引文像网页提示框、新作者源仍沿用旧 demo；旧视觉判断标准偏低。本记录补充并纠正旧结论，不改写历史记录。
- 改动范围（仅 S7 归属与交接）：
  - `families/campus/README.md`：明确家族原语与页面构图分工，示例不是整页模板；线/色面需有内容用途，不一概禁用。
  - 两册 `book.html / book.css`、自然营英文版权文案及素材表/森林照片；`brief.md / page-plan.md / experience.md / design-revision.md`。
  - 两册稳定 `.qa/visual-review.md` 入口、最终构建的 gate/visual-review、逐页栅格哈希、面对页拼图、前后证据和导出验证结果。
- 可复制命令（仓库根目录，复用已有环境，不安装依赖）：
  ```sh
  export HB_CHROMIUM='/Users/apple/Library/Caches/ms-playwright/chromium_headless_shell-1228/chrome-headless-shell-mac-arm64/chrome-headless-shell'
  export PYTHONPATH=/tmp/hb-editorial-test-deps
  node hb/core/cli.mjs check dev/samples/native/product-brochure
  node hb/core/cli.mjs check dev/samples/native/nature-camp
  node hb/core/cli.mjs review dev/samples/native/product-brochure --verdict deliverable --by 'Codex（作者全页复核，非独立评测）' --notes dev/samples/native/product-brochure/.qa/a9f9e48c6865/visual-review.md
  node hb/core/cli.mjs review dev/samples/native/nature-camp --verdict deliverable --by 'Codex（作者全页复核，非独立评测）' --notes dev/samples/native/nature-camp/.qa/e1151e2c854d/visual-review.md
  node hb/core/cli.mjs verify dev/samples/native/product-brochure
  node hb/core/cli.mjs verify dev/samples/native/nature-camp
  node hb/core/cli.mjs export dev/samples/native/product-brochure --name product-brochure-s7-revised
  node hb/core/cli.mjs export dev/samples/native/nature-camp --name nature-camp-s7-revised
  bash dev/tests/selftest.sh --quick
  ```
- 完成判定逐条结果：
  - 家族颜色/字体/字号/网格/低层原语与打印安全变量、无整页模板：pass —— 复核 `families/campus/design.css`；整页 CSS 在样册中，家族 CSS 本轮未改，两个 project.json 的冻结 SHA256 均与各自文件一致。
  - 两本真实材料样册、其中一本 ≥16 页中英且含真实 CC0：pass —— 产品册中文 12 页；自然营中文/英文各 16 页，九张真实照片中第 4 页为 SpessiG 的 CC0 森林照片（来源文件页及 revision、许可 URL、像素、哈希登记在 assets.json），另八张维持既有公有领域来源与“仅示意”声明。原“用 PD 代替 CC0”的偏离已关闭。
  - S2–S4 与 S5：pass —— 产品册构建 `a9f9e48c6865`；自然营构建 `e1151e2c854d`。三个语言产物 render / measure / postflight / raster / coverage 全 pass，硬项 fail=0、unverified=0，verify 有效。
  - 最终 PDF 全页栅格审稿：pass（作者复核）—— 共 44 页、19 对真实面对页、封面/封底及整册图。用户反馈后重排产品第 3/5/6/8 页与自然营第 3/5/15 页（中英），重看 10 张物理页及全部面对页；其余 34 页与此前逐页看过的版本栅格逐字节一致，`evidence/revision-parity.json` 保存前后哈希。不是抽查，不是独立人工评测，不评为优秀。
  - 交付补充验证：pass —— 三个语言的正式 PDF 与审稿哈希一致；可编辑 PDF 扩充字体后无 Type 3 且逐页像素一致；离线 HTML 无外部请求且打印一致；两册源包在干净目录重建为相同构建、相同栅格。结果留在各最终 `.qa/<id>/evidence/delivery.json`，交付物在 `out/*-s7-revised/`（不将大体积交付物入库）。
  - quick 自检：pass —— 34 份活跃文档链接、4 个 Python 契约测试、语法及静态项；日志 `hb-native-selftest.b9yNCu`。quick 中浏览器项明确 unverified，本条不代替上述真实样册检查/导出。
- 实际修复与证据：
  - 产品封面眉标在 DOM 测量正常但最终 PDF 贴在媒体页原点；改静态网格元信息组，PDF 首字由 (0.529, 0.620)mm 回到 (22.527, 21.522)mm，安全内缩要求 11mm；`evidence/pdf-bounds.json` 与封面前后图。
  - 产品第 12 页 Theme/Layout/Font 分组断行；封面显式标记历史文稿，旧命令不冒充当前指南。
  - 用户截图对应第 6 页取消竖边和底色，五栏引文按语义断行；第 3/5 页取消引文装饰线，第 8 页改开放分类索引。自然营第 3 页取消提示框，第 5 页取消纸色卡/装饰大编号，第 15 页改四行并列问答。取舍与替代方向见各册 design-revision.md，前后图在 evidence/。
  - 自然营第 14 页原照片横倒，作者 CSS 转正且保留原图；中英最终页复核照片主体与三栏安全信息，前后图留档。
- 契约变更：无。开工时已有 `hb/core/pdfboxes.py`、`render.mjs`、`validate.py`、`references/contract.md` 四个未提交改动；逐字节保留、不纳入本次提交。本轮验证基于含这些预存改动的工作区，未单独验证仅含提交的干净 checkout。
- 偏离计划的决定：无新增范围偏离；CC0 缺口已关闭。家族 v1/v1.1 保持冻结，没有为单本构图改动抬升家族版本；本项目视觉取舍不自动晋升全局经验。
- 新增依赖：无。实际 Node 24.9.0 / Python 3.13.3 / Playwright 1.64.1 / 显式 Chromium 149.0.7827.55，复用既有 Python 依赖；Node 22 / Python 3.10 参考环境未实测（unverified）。
- 未完成与已知问题：
  - 本轮是制作执行者全页复核；用户尚未给修订版评分，未做独立人工校准/纸样或 Acrobat 实际改字，不计入 S12。
  - 产品册原稿为旧引擎介绍，保留“五步但实际四项”等原稿疑点；自然营原稿沿用 2026 年 7 月与旧截止日、未提供具体报价/报名渠道。两者为排版样册，原稿问题在审稿中披露，不能直接当现行使用指南/招生承诺。
  - 产品第 7 页、自然营第 7/10 页的留白作为章节/阅读停顿保留。样册没有联合跨缝全景图，不冒充已完成 S11 的全景案例。
- 下一步从哪继续：S11，审计旧 gallery 与现有视觉资产；需有可解释的内容/构图判断和反例，不把本轮作者自评或示例造型当作通用优秀标准。S12 仍未开始。
- 提交：本记录所在的 `S7:` 补验收提交（见 git log）。

### S7 · Folio CSS 统一排版系统扩展 · 进行中 · 2026-10-22

- 用户明确扩展原 S7 范围：完整可组合的原子、共享布局与组件展示；Campus 与 Photo 合并为同一套能力，品牌统一为 Folio CSS，与 Folio 编辑器一致。
- 本次归属：`families/core/**`、`families/folio/**`、`dev/folio-css/**`、`dev/build-folio-css.py`、新样册 `dev/samples/native/folio-system/**`、对应测试、作者入口与架构说明。本项不冒充 S11 全量旧资产审计或 S12 独立评测。
- 使用者复制一份零依赖 CSS；开发源文件分层组织，无 Tailwind/npm 构建依赖。布局是可选组合，不是渲染器的枚举。
- 现有 Campus 与两本 S7 冻结样册维持原文件；此前四处运行时/契约改动及未跟踪 `docs/family-css.md` 属于既有工作，不纳入本项。

### S7 · Folio CSS 统一排版系统扩展 · 完成 · 2026-10-22

- 用户决定：与 Folio 编辑器统一品牌；文字与摄影共用底层，图片比例/焦点/出血/组图/跨页属于同一套系统。Campus 作为历史方案与旧样册保持冻结。
- 改动范围：
  - `families/folio/`（tokens、family.json、单文件 design.css、API说明）+ `families/core/`（基础、布局、原子）：完整的有限类词表，颜色角色、实际字重、字阶、空间、六/十二轨、对齐、比例、焦点、出血和功能标记。
  - `dev/folio-css/`：16组布局、8个纯原子/布局组件配方；规则演示、筛选、结构视图、源码复制、样册预览。配方使用实际分发CSS，无额外组件样式。
  - `dev/build-folio-css.py`：标准库拼接与`--check`；无npm框架或浏览器端编译。
  - `dev/samples/native/folio-system/`：原创8页中文观看练习册，四张已有授权照片，6–7页为真正连续全景；8行页面专属CSS，其余由共用规则组合。
  - 新的7项浏览器回归、selftest生成文件一致性检查；Skill、style/layouts、new/brand入口与架构说明；分步计划记入用户追加范围。
- 可复制命令：
  ```sh
  python3 dev/build-folio-css.py --check
  export HB_CHROMIUM='/Users/apple/Library/Caches/ms-playwright/chromium_headless_shell-1228/chrome-headless-shell-mac-arm64/chrome-headless-shell'
  export PYTHONPATH=/tmp/hb-editorial-test-deps
  node --test dev/tests/core/family-css.test.mjs
  node hb/core/cli.mjs check dev/samples/native/folio-system
  node hb/core/cli.mjs verify dev/samples/native/folio-system
  python3 dev/folio-css/update-preview.py bebe29aa0866
  node hb/core/cli.mjs export dev/samples/native/folio-system --name folio-css-specimen
  bash dev/tests/selftest.sh --quick
  ```
- 完成判定：
  - 原子、布局、组件、可用入口：pass；build一致性检查、初始化真实字体与SHA、契约validate均通过。
  - 组合回归：7/7 pass，检查真实computed geometry与面色，覆盖原子优先级、嵌套色面、safe镜像、字重、图框、跨页；展示页1440/390px无溢出，图片全部加载，复制结果与配方相同。
  - 真实PDF：构建`bebe29aa0866`，8页全技术项pass；已逐页及全部面对页审稿，记录 `.qa/visual-review.md`。作者结论可交付，不评优秀、不计S12。
  - 导出：正式PDF哈希一致、可编辑PDF/离线HTML逐页一致、源包干净重建同构建同栅格。详细产物在`out/folio-css-specimen/`，未将大体积交付包入库。
  - quick：pass，记录`hb-native-selftest.1EhV1u`。完整既有core套件本轮未重跑；新浏览器回归与样册生产链已实际执行。
- 修复：布局选择器降为低优先级使原子可覆盖；figure左右声明优先于page推导；图框约束自身宽度使有界组图不撑列。对应浏览器反例已回归。
- 契约变更：无。四个既有运行时/契约改动逐字节一致并排除提交；预存未跟踪`docs/family-css.md`在工作期间有外部变化，本任务未编辑、不纳入提交；新出现的`output/`同样未触碰。
- 偏离计划：用户已明确允许共享可选layout与组件展示，扩展了原S7文件边界及过窄的“只有低层原语”约束；没有新增运行时版式枚举或Photo第二体系。
- 新增依赖：无。Node24.9.0/Python3.13.3/Playwright1.64.1/显式Chromium149.0.7827.55；全部素材与字体复用本地。
- 边界：Node22/Python3.10实际运行、其他浏览器、纸样、Acrobat改字仍unverified；8页样册不代替独立人工校准。原S7两册未重写。完整证据摘要见 `dev/folio-css/verification.md`。
- 下一步：按原计划S11审计视觉资产，再做S12独立生成与人工校准；Folio CSS已可用于新项目。
- 提交：本条所在`S7:`提交（见git log）。
