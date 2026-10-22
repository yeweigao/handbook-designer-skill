# HTML/CSS 原生改造 · 进度与交接

分步说明见 [IMPLEMENTATION-STEPS](IMPLEMENTATION-STEPS.md)。新记录追加在最下方，不改写旧记录。

## 状态表

| 步骤 | 状态 | 最近更新 | 提交 |
|---|---|---|---|
| S1 契约与最小样例 | 完成 | 2026-10-22 | 086b8b7 |
| S2 渲染运行时 | 完成 | 2026-10-22 | c4824c5 |
| S3 版面测量与可读性检查 | 完成 | 2026-10-22 | 见记录 |
| S4 最终 PDF 检查与验收绑定 | 未开始 | | |
| S5 内容提取与原文覆盖 | 未开始 | | |
| S6 长文续页工具 | 未开始 | | |
| S7 Campus 家族与真实样册 | 未开始 | | |
| S8 导出与离线交付 | 未开始 | | |
| S9 Folio 联动 | 未开始 | | |
| S10 Skill 文档与旧引擎退役 | 未开始 | | |
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
