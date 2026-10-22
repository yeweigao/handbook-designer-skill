# 家族 CSS 是怎么写的

> 说明性文档，不是新规则来源。硬约束仍以 `references/contract.md` + `hb/core/validate.py` 为准；
> 可读性阈值以 `hb/core/measure.mjs` 为准；家族职责边界以 `dev/maintenance.md` 的「每条规则一个主人」为准。
> 本文只解释**结构性写法**与**为什么这样分层**。当前推荐家族是 `families/folio/`（Folio CSS 1.0.0），
> `families/campus/` 保留为历史方案；两者的结构差异见第九节。

## 一、家族 CSS 是什么，不是什么

一句话：**家族 CSS 提供共同语言，页面构图由作者写 `book.css` 决定。**

| 层 | 文件 | 内容 | 变化频率 |
|---|---|---|---|
| 运行时生成 | 内存中的 `<style data-hb="print">` / `fonts` | `@page`、`.page` 几何、`--bleed` 等变量、`page-n` 计数器、`@font-face` | 由 `project.json` 决定 |
| 家族基因 | `families/<名>/design.css` → 项目 `design.css` | 颜色角色、字体角色、字号阶梯、网格、线宽、间距、低层原语 | 家族升级时（不静默） |
| 本书构图 | `book.css` | 整页结构、封面、跨页、局部尺寸、本书专属类 | 每本书 |
| 语言差异 | `lang/<lang>.css` | 断行、行长、标题换行补偿 | 每种语言 |

家族里**不许**出现 `.cover-layout-01`、`.two-column-page` 这类只能整套照抄的整页类。
家族只沉淀「在不同内容上重复证明可迁移」的低层规律；一次成功不升格为规则（见 `dev/maintenance.md`）。

## 二、一个家族最少由三个文件组成

```
families/<名>/
  family.json    # 机器读取：版本、画布、字体角色、字符集声明
  design.css     # 作者读取：init 时原样复制到项目的那一份
  README.md      # 人读：关键决定、原语清单、不能照搬的部分、版本记录
families/licenses/  # family.json 里引用的 OFL 授权文本
```

`design.css` 可以是手写的单文件（Campus），也可以是生成物（Folio）：

```
families/folio/tokens.css        # 颜色、字体、字号、行距、版心、间距、线宽
families/core/base.css           # 作用域 reset、页面基底、镜像版心 .fl-area
families/core/layouts.css        # 可选结构关系与具名子项 .fl-l-*
families/core/atoms.css          # 原子、排印角色、图片、页码
        ↓  python3 dev/build-folio-css.py
families/folio/design.css        # 单文件分发，无 @import、无运行时依赖
```

生成路线的唯一硬要求：**分发文件必须自洽**——不能 `@import` 源模块，也不能 `@font-face`（字体归 `project.json`）。
`build-folio-css.py` 在拼接时会直接拒绝这两项；`--check` 在提交物与源模块不一致时失败。
运行时不认识 `families/core/`，项目里只有一份冻结的 `design.css`。

`family.py list` 的判定很简单：**目录里存在 `family.json` 就算一个可用家族**（`hb/core/family.py:94`）。
所以漏写 `family.json` 的家族不会报错，只会静默消失。

### family.json 逐字段

```jsonc
{
  "contract": 1,
  "name": "campus",              // 与目录名一致
  "version": "1.1",              // init 时写入 project.json，家族升级靠它区分
  "title": "Campus · 学院墨蓝",   // list 命令展示
  "description": "…",            // 选家族时的判断依据，写清适合什么材料
  "fonts": [
    { "family": "Noto Serif SC", "source": "NotoSerifSC-VF.ttf",
      "weights": [700], "license": "noto-serif-sc-OFL.txt", "role": "display" }
  ],
  "canvas": { "trim_mm": [210, 297], "bleed_mm": 3, "safe_mm": 8 },
  "charset": "gb2312"
}
```

- `fonts[].source` 是**可变字体**文件名，按 `$HB_FONT_DIR` → `~/.cache/handbook-designer/fonts` → `dev/fonts` 顺序查找；
  `weights` 里的每个值会被 `instancer` 实例化成静态字体再子集化，输出到项目 `assets/fonts/<Family>-<weight>.ttf`。
  这就是为什么家族可以声明多个字重却只提供一份源文件，也是为什么**排版里用到的字重必须在 `weights` 里列出**——否则运行时没有这个文件，检查会报字体回退。
- `license` 指向 `families/licenses/` 里的文件，init 时复制进项目 `assets/fonts/`。新增字体必须补授权文本。
- `canvas` 只是 init 时写进 `project.json` 的初值，之后以项目为准（家族改画布不影响老项目）。
- `charset` 目前是**说明性字段**：`family.py` 的子集实际固定为 GB2312 常用字 + 拉丁 + 标点 + 项目里出现的全部字符（`charset()`，`hb/core/family.py:29`），并不读取这个字段。写它只为表达该家族的字符覆盖预期。

## 三、运行时给家族 CSS 预置了什么

`hb/core/render.mjs:assemble()` 往 `<head>` 里按这个固定顺序插：

```
<style data-hb="print">    ← project.json 生成的 @page / .page / 变量 / 计数器
<style data-hb="fonts">    ← 由 project.json.fonts 生成的 @font-face
<link design.css> <link book.css> <link lang/<lang>.css> <link edits.css>
```

由此得到三条硬性写法：

1. **可以放心消费 `var(--bleed)`、`var(--media-w)`、`var(--safe-top)`、`var(--inset-*)`**，它们比作者 CSS 先定义。
2. **不能写 `@page`、`@font-face`**——`validate.py` 直接报 `css.page` / `css.font-face` 硬错误（`hb/core/validate.py:523`）。
   纸张与出血只在 `project.json` 的 `canvas` 声明一次。
3. **不能改 `.page` 的宽高与 `break-*`**：`.page` 尺寸由打印 CSS 给出，构建会核对实际尺寸。

`--safe-*` 是「印刷安全区」，从成品边向内量，所有文字（含页码页眉）必须落在里面；
`--m-*` 这类版心边距是**作者自己定义**的，通常写成 `calc(var(--bleed) + 18mm)`，两者不是一回事。

## 四、design.css 的写法：按「从底到顶」十段

Campus 的实际顺序就是推荐顺序，每段只解决一件事（Folio 把 1–4 段放进 `tokens.css`、5–7 放进 `base.css`、8–10 放进 `atoms.css`，另加一段可选的 `layouts.css`，内容等价，只是物理位置不同）：

| 段 | 内容 | Campus 实例 |
|---|---|---|
| 1 | `:root` 颜色角色 | `--paper / --ink / --muted / --primary / --ochre / --gold / --line / --on-dark*`，注释里写实测对比度 |
| 2 | `:root` 字体角色 | `--font-display / --font-body / --font-latin / --font-num` |
| 3 | `:root` 字号阶梯 + 行距 | `--fs-aux 11 / key 13 / body 16 / lead 19 / h3 21 / h2 30 / h1 44 / display 62 / hero 120`，`--lh-body 28` 兼作基线 |
| 4 | `:root` 网格与间距 | `--m-top/bottom/inner/outer`、`--gutter 6mm`、`--s1…s5` 全部是 28px 的倍数 |
| 5 | 页面基底 | `body` 背景（屏幕预览的灰台面）、`.page` 字体与抗锯齿 |
| 6 | reset + 断行策略 | 标题 `text-wrap: balance` + `word-break: keep-all`，正文 `text-wrap: pretty` |
| 7 | 版心 `.area` | 绝对定位六栏 + `calc(var(--bleed) + …)`，偶数页内外侧对调，配 `.c1-4` 这类跨栏类 |
| 8 | 排印原语 | `.kicker / .display / .h1-3 / .lead / .subtitle / .aux / .key / .num / .index-num / .mono` |
| 9 | 结构原语 | `.rule / .hair / .quote / .note / .frame / .caption`；功能类 `.fill-lines / .checklist / .step` |
| 10 | 面与页边 | `.on-dark* / .scrim-bottom`（照片压暗）、`.folio / .running`、`html[data-debug-grid]` 调试网格 |

几条值得抄走的写法细节：

- **原语只给「样子」，不给「内容角色」**。角色由 HTML 的 `data-role`（`display/body/key/aux/deco`）声明，
  测量按角色取不同下限；`.kicker` 长得像眉标，但没标 `data-role="aux"` 时仍按正文 14px 检查。两者是分开的两套东西。
- **语言差异写在家族里，不写在每本书里**：`html[lang="en"] .page` 切拉丁字体、开断词、把连字符改成 U+002D。
  思源字体的 `’ “ ”` 默认全角，所以 `font-variant-east-asian: proportional-width` 要**逐元素**写（`font` 简写会重置它）——Campus v1.1 就是修这个。
- **奇偶页靠 `:nth-of-type`**：`.page:nth-of-type(even)` 当左页。`nth-of-type` 数的是同标签兄弟，
  所以全书页面必须是同一种标签（通常全用 `<section class="page">`），且第一页在右侧；混用 `<section>`/`<div>` 会让左右页整体错位。
- **间距全部用基线的倍数**，这样跨页对齐和大数字排版不会互相打架；需要例外就写局部 px，但要能说清理由。
- **调试网格用属性开关**（`html[data-debug-grid]`），渲染器永不设置它；调试层不许进入交付。

## 五、红线：校验器与测量会拦什么

| 约束 | 出处 | 表现 |
|---|---|---|
| 不得 `@page` | `validate.py:523` | error `css.page` |
| 不得 `@font-face` | `validate.py:526` | error `css.font-face` |
| CSS 里引用的资源必须存在且不越界 | `validate.py` `check_ref` | error，`url()` / `@import` 都查 |
| 正文 ≥ 14px、关键信息 ≥ 12px、辅助 ≥ 10px | `measure.mjs:12` `DEFAULT_FLOORS` | hard fail `readability.size` |
| 正文/关键信息对比度 ≥ 4.5:1，辅助 ≥ 3:1，展示字 ≥ 3:1 | 同上 | hard fail `readability.contrast` |
| 字体回退到系统字体 | `font.fallback` | hard fail（说明字库没覆盖或字重没生成） |

家族只能**把下限抬高**，不能压低：`project.json.readability` 取 `Math.max`；
确实要放宽必须由用户授权并写 `readability_waiver`（会始终输出一条 hint）。
Campus 与 Folio 都抬到 16/13/11，比下限高一点，而不是贴着下限写。

其余测量项（溢出、裁切、文字重叠、图片 DPI、出血、隐藏文字）与家族写法无直接关系，但家族的原语决定了它们容易不容易发生——
例如 `.area` 用绝对定位 + `overflow: hidden` 的页面，溢出表现为被裁掉而不是撑开，所以「放不下就改分组、栏宽、分页」这条在家族层就要写清楚。

## 六、写一个新家族：八步

```bash
HB=<skill目录>/hb
export HB_FONT_DIR=~/fonts          # 放授权可变字体
mkdir -p families/<名>
# 1) 写 family.json（name/version/fonts/canvas），字体授权放 families/licenses/
# 2) 写 design.css（按上面十段）；若走模块化，改源模块后必须重建
python3 dev/build-folio-css.py && python3 dev/build-folio-css.py --check
# 3) 写 README.md（关键决定 / 原语 / 不能照搬 / 版本）
python3 "$HB/core/family.py" list                       # 4) 确认能被列出
python3 "$HB/core/family.py" init <名> /tmp/try --title 试排 --langs zh-CN,en
node "$HB/core/cli.mjs" check /tmp/try                  # 5) 技术检查
```

6. 用**两本真实材料**的样册（一本纯文字、一本有真实照片；至少一本 ≥16 页且双语）验证，放 `dev/samples/native/`。
7. 用实际 PDF 走 `workflows/visual-review.md`：整册缩略图、真实面对页、每页阅读尺度图。技术通过 ≠ 视觉合格。
8. 在 README 里记版本与改动理由。后续改家族属于家族级决定：**已建项目不会自动跟随**，要主动审阅全册再更新来源记录。

### 最小可跑骨架

```css
/* <家族名> 家族基因 v1 —— 只放共同语言，不放整页模板 */
:root {
  --paper: #FBFAF7; --ink: #202B32; --muted: #4B575E;
  --primary: #253C4C; --line: #D6CEBF; --on-dark: #F4F1EA;
  --font-display: "Noto Serif SC", serif;
  --font-body: "Noto Sans SC", sans-serif;
  --fs-aux: 11px; --fs-key: 13px; --fs-body: 16px; --fs-h1: 44px;
  --lh-body: 28px;
  --m-top: 18mm; --m-bottom: 21mm; --m-inner: 19mm; --m-outer: 15mm; --gutter: 6mm;
  --s1: 7px; --s2: 14px; --s3: 28px; --s4: 56px;
}
body { margin: 0; background: #E8E4DC; }
.page { background: var(--paper); color: var(--ink); font: 400 var(--fs-body)/var(--lh-body) var(--font-body); }
h1, h2, h3, p { margin: 0; }
h1, h2, h3 { text-wrap: balance; word-break: keep-all; }
p { text-wrap: pretty; }

.area {
  position: absolute;
  top: calc(var(--bleed) + var(--m-top)); bottom: calc(var(--bleed) + var(--m-bottom));
  left: calc(var(--bleed) + var(--m-inner)); right: calc(var(--bleed) + var(--m-outer));
  display: grid; grid-template-columns: repeat(6, minmax(0, 1fr)); column-gap: var(--gutter);
}
.page:nth-of-type(even) .area { left: calc(var(--bleed) + var(--m-outer)); right: calc(var(--bleed) + var(--m-inner)); }
.area > * { grid-column: 1 / -1; }

.h1 { font: 700 var(--fs-h1)/1.25 var(--font-display); color: var(--primary); }
.aux { font-size: var(--fs-aux); color: var(--muted); }
.rule { border-top: 2px solid var(--primary); }
```

## 七、常见坑

| 现象 | 原因 | 处理 |
|---|---|---|
| 英文标点看起来特别宽 | 思源字体把 `’ “ ”` 当全角 | `font-variant-east-asian: proportional-width`，且逐元素写 |
| 自动断词的连字符又宽又怪 | 默认 `hyphenate-character` 是 U+2010，思源里全角 | 显式改成 `"-"`（U+002D） |
| 标题整块溢出报错 | `keep-all` 让无标点长标题无法断行 | 手动 `<br>` 或调字号；不要靠 `overflow` 遮住 |
| 新建家族 `list` 里看不到 | 缺 `family.json` | 补文件，目录名与 `name` 一致 |
| 某个字重没用却在 PDF 里变了 | `weights` 没声明该字重 | 加进 `weights` 并 `family.py fonts` 重建 |
| 左右页页边距整体反过来 | 页面标签混用，或 `first_page` 不是 `right` | 统一 `<section class="page">`，确认 `project.json.first_page` |
| 页码不显示 | `.folio::after` 依赖运行时 `counter(page-n)` | 不要在作者 CSS 里另建计数器；`.folio` 必须放在 `.page` 内 |
| 家族改了但老项目没变 | 设计如此：项目 `design.css` 已冻结 | 主动审阅、按需更新项目并记原因 |

## 八、参考实物：Folio（当前）与 Campus（历史）

- `families/folio/design.css`（623 行 / 286 条规则 / 74 个 `--fl-*` 变量）是当前分发文件；它由 `tokens.css` + `core/{base,layouts,atoms}.css` 拼接生成，源模块约 550 行。
- `dev/build-folio-css.py --check` 会在源模块与生成物不一致时报错，是改 CSS 后的必跑项；生成器同时输出展示页用的 `catalog.js`。
- `families/campus/design.css`（约 140 行）是单文件手写家族的完整样本，十段内容可直接对照；`families/campus/README.md` 的章节结构（适合什么材料 → 关键决定 → 原语 → 不能照搬 → 版本 → 已审样册）仍可当模板。
- 两者的分工差异见下节，不要混用类名：Campus 用 `.h1/.body/.on-dark`，Folio 用 `.fl-h1/.fl-body/.fl-surface-dark`。

## 九、Folio 换了什么写法

| 维度 | Campus v1.1（单文件） | Folio 1.0.0（模块生成） |
|---|---|---|
| 命名 | `.display/.h1/.on-dark` 等语义短名 | `.fl-*` 原子 + `--fl-*` 变量，原语与原子分开 |
| 结构 | 一个文件按十段手写 | tokens → base → layouts → atoms 四段分别维护，拼接分发 |
| 版心 | `.area` 固定六栏 + 跨栏类 | `.fl-area` 只给几何；`.fl-grid`/`.fl-cols-*` 决定栏数，可 1/2/3/4/6/12 |
| 间距 | 全部 28px 倍数 | 0/7/14/28/42/56/84，含 1.5 倍基线 |
| 作用域 | 直接作用于 `body/.page` | 一律 `:where(.page, .fl-scope)`，默认零特异性，原子可覆盖 |
| 明暗面 | `.on-dark` 只改色，后代逐个覆盖 | `.fl-surface-*` 一次性重绑 `--fl-text/-muted/-accent/-stroke`，可嵌套回纸面 |
| 左右页 | 只靠 `nth-of-type(even)` | 仍是 `nth-of-type(even)`，另加 `data-side="left|right"` 显式覆盖 |
| 中文断行 | 标题 `word-break: keep-all`，只在标点处断 | 只有 `text-wrap: balance`，断行依赖作者 `<br>`（见下方注意） |
| 字重 | 直接写 700/600 | 角色带 `--fl-current-weight/--fl-current-strong`，只请求真实存在的字重 |
| 图片 | `.frame` + `object-fit` | `.fl-frame` + `.fl-ratio-*`/`.fl-fit-*`/`.fl-focus-*`，焦点可写 CSS 变量 |
| 结构布局 | 无，全部写在 `book.css` | 可选 `.fl-l-*`（split/sidebar/marginalia/chronology/panorama…），只负责关系 |

由此带来两条写作变化：

1. **原子顺序即优先级**。所有工具类都是单类选择器，冲突由文件内的声明顺序决定，HTML 里类名的先后没有意义；同一属性每个元素只选一个原子。
2. **角色与样式分离更彻底**。`.fl-key` 只改变字号，`data-role="key"` 才决定被按 12px 下限检查；两者都不能省。

中文标题的断行是 Folio 相对 Campus 的一处回退：Chrome 在 `word-break: normal` 下允许在任意两个汉字之间断行，
`balance` 只均衡行宽、不保护词边界。样册里靠手写 `<br>` 规避（见 `dev/samples/native/folio-system/book.html`）。
如果正文来自提取稿、标题长度不可预知，建议给标题补 `word-break: keep-all`，或在本书 `book.css` 里加一条
`.fl-display, .fl-h1, .fl-h2 { word-break: keep-all; }` 后重跑测量——代价是无标点超长标题可能溢出，需要配 `<br>`。
