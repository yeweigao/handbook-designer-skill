# 项目契约（contract 1）

HTML/CSS 原生手册项目的权威约定。渲染（`hb/core/render`）、检查（`hb/core/measure`、`postflight`、`coverage`）、续页、导出和 Folio 联动都以本文为准。机器校验入口：`python3 hb/core/validate.py <项目>`。

改动本文须同步改 `validate.py` 与相关测试，并在 `dev/audits/PROGRESS.md` 的交接记录中写明「契约变更」。

## 1. 项目目录

```text
project/
  project.json        # 项目与生产参数（§2）。不出现任何版面描述
  brief.md            # 授权、读者、阅读任务、重要假设
  page-plan.md        # 页面任务与整册节奏
  book.html           # 作者源：页面结构 + 默认语言文案（§3）
  design.css          # 家族基因（从 families/<名> 复制，记录来源与哈希）
  book.css            # 本书专属构图
  edits.css           # 可选：Folio 修改转成的覆盖规则，待 agent 审阅
  copy/<lang>.json    # 非默认语言的文案（§4）
  lang/<lang>.css     # 可选：某语言的长度、断行、字重、页面覆盖
  assets/             # 字体、图片、SVG 等本地文件
  sources/            # 原始材料、提取结果、内容 ID 映射、来源与授权清单
  experience.md       # 本项目的修订记录
  .build/             # 渲染产物（§6），不提交
  .qa/                # 检查报告与审稿记录（§7）
  out/                # 正式交付物
```

项目引用的所有文件都必须在项目目录内（不允许 `..`、绝对路径、符号链接指向项目外、网络地址）。

## 2. project.json

```json
{
  "contract": 1,
  "title": "示例手册",
  "entry": "book.html",
  "styles": ["design.css", "book.css"],
  "languages": ["zh-CN", "en"],
  "default_language": "zh-CN",
  "canvas": { "trim_mm": [210, 297], "bleed_mm": 0, "safe_mm": 8 },
  "binding": "digital",
  "first_page": "right",
  "content_mode": "carry",
  "fonts": [
    { "family": "Noto Sans SC", "file": "assets/fonts/NotoSansSC-400.ttf", "weight": "400", "style": "normal" },
    { "family": "Noto Sans SC", "file": "assets/fonts/NotoSansSC-700.ttf", "weight": "700", "style": "normal" }
  ],
  "readability": { "body_px": 16 },
  "family": { "name": "campus", "version": "1", "sha256": "…" }
}
```

| 字段 | 必填 | 说明 |
|---|---|---|
| `contract` | 是 | 固定为 `1` |
| `title` | 是 | 书名，用于文件名与元数据 |
| `entry` | 是 | 作者源 HTML，项目内相对路径 |
| `styles` | 是 | 作者 CSS，按顺序加载。渲染时最前面插入生成的打印 CSS 和字体 CSS，最后追加 `lang/<lang>.css`、`edits.css`（存在时） |
| `languages` | 是 | BCP-47 语言标签，不重复，至少一个 |
| `default_language` | 是 | 必须在 `languages` 中；它的文案写在 `book.html` 里 |
| `canvas.trim_mm` | 是 | 成品宽、高（mm），正数 |
| `canvas.bleed_mm` | 是 | 出血（mm），≥ 0。为 0 时成品框等于媒体框 |
| `canvas.safe_mm` | 是 | 印刷安全区（mm），一个数或 `[上, 右, 下, 左]`，从成品边缘向内量：所有文字与功能信息（含页码、页眉）必须在安全区内。它不是版心边距，版心由作者 CSS 决定，通常比安全区更宽 |
| `binding` | 是 | `digital` 电子版 / `loose` 散页 / `saddle` 骑马钉（页数须为 4 的倍数）/ `perfect` 胶装（页数须为偶数） |
| `first_page` | 是 | 第一页在跨页中的位置：`right`（默认，封面单独成右页）或 `left` |
| `content_mode` | 是 | `carry` 原文搬运 / `polish` 授权润色 / `translate` 授权翻译 / `frozen` 内容冻结（§5） |
| `fonts` | 是 | 至少一项。字体只在这里声明，渲染据此生成 `@font-face`；作者 CSS 不得自写 `@font-face`。每项是一个固定字重的**静态字体**（`weight` 为单个值）：可变字体在 Chrome 导出的 PDF 里会变成 Type 3，印刷与可编辑 PDF 都不接受。用 `python3 hb/core/font_static.py` 从可变字体实例化 |
| `readability` | 否 | 覆盖可读性下限（§3.4），只能比默认值更严 |
| `readability_waiver` | 否 | 用户明确授权降低下限时填写：`{"reason": "…", "approved_by": "…", "date": "YYYY-MM-DD", "values": {"aux_px": 9}}`。检查器按放宽后的值检查，并始终报告一条 hint |
| `family` | 否 | 家族 CSS 的来源名、版本与 `design.css` 复制时的哈希 |

物理尺寸、出血、装订只在 `project.json` 声明一次。渲染器据此生成打印 CSS，作者 CSS 出现 `@page` 即为错误。生成的内容固定为：

- `@page { size: <媒体宽>mm <媒体高>mm; margin: 0 }`，媒体尺寸 = 成品 + 2 × 出血；
- `.page { position: relative; box-sizing: border-box; width: var(--media-w); height: var(--media-h); overflow: hidden; break-after: page }`。作者 CSS 不要改 `.page` 的宽高与 `break-*`，S3 会核对实际尺寸；
- 变量：`--trim-w`、`--trim-h`、`--bleed`、`--media-w`、`--media-h`、`--safe-top`、`--safe-right`、`--safe-bottom`、`--safe-left`（从成品边向内量），以及 `--inset-top`… `--inset-left`（= 出血 + 安全边距，即安全区在 `.page` 内的位置）。版心边距由作者 CSS 自己定义（通常写成 `calc(var(--bleed) + 版心边距)`）；
- 页码计数器 `page-n`：每个 `.page` 自增，作者可用 `counter(page-n)` 显示页码。

PDF 页面框：MediaBox = CropBox = BleedBox = 媒体尺寸（成品 + 出血），TrimBox = 成品尺寸。Chrome 只能输出 1/75 英寸取整的纸张，渲染器先按稍大纸张输出，再精确裁切到左上角的媒体区域（`hb/core/pdfboxes.py`），内容不缩放。

## 3. 作者源 HTML

### 3.1 页面

```html
<section class="page" data-page-id="p-cover">
  <h1 data-source-id="cover-title" data-role="display">原文标题</h1>
  <p data-source-id="cover-intro">原文导语</p>
</section>
```

- 每个 `.page` 对应一张物理输出页（含出血时，`.page` 是含出血的整张媒体页）。`.page` 是 `<body>` 的直接子元素，不嵌套。
- `data-page-id` 必填，全书唯一，格式 `[a-z0-9][a-z0-9-]*`。页面重排不改 ID。
- 页码与左右页由顺序和 `first_page` 推出，不手写在属性里。
- 跨页：组成跨页的两页写同一个 `data-spread="<跨页 ID>"`，必须恰好两页且相邻；按 `first_page` 推出的位置须为左页在前、右页在后。
- 作者源是静态页面：不得有 `<script>`、内联事件属性（`onclick` 等）、`<iframe>`、`<object>`、`<embed>`、`<base>`。
- 样式只放在 `project.json` 的 `styles` 文件里：不得有 `<style>` 和 `<link rel="stylesheet">`。元素上的 `style` 属性可以用。
- 不得引用网络地址（`http:`、`https:`、`//`）。

### 3.2 内容节点

- `data-source-id`：承载原文内容的元素，格式 `[a-z0-9][a-z0-9._-]*`。它的文字（含白名单行内标记）就是这段内容的默认语言文本。
- 内容节点是叶子：内容节点内部不能再有内容节点。
- 同一个 `data-source-id` 在全书只能出现一次，以下两种情况除外：
  - 续页片段：同一 ID 的各片段带 `data-fragment="1"`、`"2"`…，从 1 连续编号（由 S6 续页工具生成）；
  - 有意重复（如页眉重复书名）：除第一处外都写 `data-repeat`，检查时只把第一处算作展示。
- 行内标记白名单：`<em> <strong> <a href> <br> <sup> <sub> <span class> <span lang>`。内容节点里出现其他元素即为错误（图片、SVG 不放在内容节点里）。
- 可编辑：有 `data-source-id` 的元素就是可编辑文字，编辑 ID 默认等于内容 ID（片段为 `<ID>#<片段号>`）。图片等非文字可编辑对象写 `data-edit-id`，全书唯一。

### 3.3 其他属性

| 属性 | 用于 | 说明 |
|---|---|---|
| `data-role` | 任意元素 | `display` 标题展示字 / `body` 正文 / `key` 关键功能信息 / `aux` 辅助信息 / `deco` 装饰。作用于自身及后代，最近的祖先优先；未标记按 `body` |
| `data-flow` | 文字框容器 | 可续排内容流的名称；同名容器按文档顺序组成一条流（S6 使用） |
| `data-overlap` | 内容元素 | 允许与之重叠的元素 ID，空格分隔；`*` 表示允许与任意装饰性元素重叠。只解释局部关系，不豁免整页 |
| `data-bleed` | 图片、色块 | 允许进入出血/越过安全区的边：`top right bottom left` 的组合或 `all` |
| `data-asset` | 图片 | 对应 `sources/assets.json` 中的素材 ID（S5） |

`deco` 元素不得带 `data-source-id`：装饰不算内容，内容也不能藏进装饰里逃避检查。

### 3.4 可读性下限

| 角色 | 最小字号（A4） | 最小对比度 |
|---|---|---|
| `body` | 14px（10.5pt）；常规阅读册建议 16px | 4.5 : 1 |
| `key` | 12px（9pt） | 4.5 : 1 |
| `aux` | 10px（7.5pt） | 3 : 1 |
| `display` | 不低于 `body` 下限 | 3 : 1 |
| `deco` | 不检查 | 不检查 |

字号以 CSS px 计（1px = 1/96 英寸 = 0.75pt），是印刷物理尺寸，不随纸张大小缩放。`project.json` 的 `readability` 可用 `body_px`、`key_px`、`aux_px`、`body_contrast`、`key_contrast`、`aux_contrast`、`display_contrast` 提高下限，不能降低。确需降低（例如屏幕用的社交媒体画布）时，须用户明确授权并写入 brief 与 `readability_waiver`。

## 4. 多语言

- 默认语言的文案直接写在 `book.html`。
- 其他语言：`copy/<lang>.json`

```json
{ "contract": 1, "lang": "en", "strings": { "cover-title": "Sample Handbook", "cover-intro": "…" } }
```

- `strings` 的键必须与 `book.html` 中的 `data-source-id` 一一对应：缺译、多余键都是错误。值按 §3.2 的白名单解析，白名单外的标记一律转义为文本。
- 语言差异先用 `lang/<lang>.css` 处理（`:lang()` 或 `html[lang]` 选择器）。某语言必须改变分页时，由 S6 定义的语言页面覆盖处理，不复制整本作者源。
- 每种语言独立渲染、独立检查、独立交付。

## 5. 内容模式

| 模式 | 允许 | 检查 |
|---|---|---|
| `carry` 原文搬运 | 删去编号标签、批注等非读者内容（须在 `sources/` 中声明）；调整页序 | MISSING 必须为 0；ORDER 逐条确认；EXTRA 只允许结构性文字（页眉、图注、填写提示等，须标 `data-role="aux"` 或声明） |
| `polish` 授权润色 | 改写措辞、合并压缩 | 逐段对照表；事实与数字不变 |
| `translate` 授权翻译 | 生成或改写译文 | 译文与原文按内容 ID 对应 |
| `frozen` 内容冻结 | 只改版面 | MISSING / ORDER / EXTRA 全为 0；页序与原稿一一对应 |

## 6. 构建产物与构建 ID

- 输入指纹：入口 HTML、全部作者 CSS（递归 `@import`）、被 HTML/CSS 引用的全部文件、`copy/`、`lang/`、`edits.css`、`project.json` 的内容哈希，加上渲染工具版本与浏览器版本号。
- 构建 ID：输入指纹 SHA-256 的前 12 位十六进制。
- 产物：`.build/<构建 ID>/<lang>/snapshot.html`（注入后的完整页面）、`book.pdf`、`manifest.json`（指纹明细）。
- 交付给 Folio 的编辑包带构建 ID；写回时据此找到原版本。

## 7. 检查报告

每项检查结果：

```json
{ "id": "readability.size", "status": "fail", "severity": "hard",
  "lang": "zh-CN", "page": "p-cover", "target": "cover-intro",
  "evidence": { "font_px": 11, "min_px": 14 }, "message": "正文 11px 低于下限 14px" }
```

- `status`：`pass` / `fail` / `unverified`。检查没有运行、缺依赖或无法可靠判断时一律 `unverified`，不写成 `pass`。
- `severity`：`hard` 硬项（fail 或 unverified 都阻止正式交付）/ `hint` 提示（只报告）。
- 报告位置：`.qa/<构建 ID>/<lang>/<检查名>.json`，汇总在 `.qa/<构建 ID>/gate.json`（S4）。
- 命令退出码：存在硬项 fail 或硬项 unverified 时非 0。
