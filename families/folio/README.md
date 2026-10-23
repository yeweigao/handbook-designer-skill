# Folio CSS · 2.2.0

以 Swiss 网格、对齐、比例和留白为共同底座的印刷 CSS 语言。相同的颜色角色、字体、网格和节奏可以组合出纯文字、摄影、信息查阅和混合页面。普通 HTML/CSS 是作者源，布局类是可选起点，组件是可拆开的组合示例。

[配方索引](recipe-index.md) 定位全部原子、布局、组件与变奏；[recipes.json](recipes.json) 提供普通 HTML 配方。先按任务查 id，再取对应条目，不必全量加载。图片路径需换成本项目真实资源；内容 ID 与印刷声明按项目契约补齐。正式使用不需要开发展示站。

## 文件与使用

| 文件 | 职责 |
|---|---|
| `tokens.css` | 颜色、字体、字号、行距、版心和间距的统一数值 |
| `../core/base.css` | 作用域 reset、页面基底、镜像版心 |
| `../core/layouts.css` | 可选的结构关系与具名子项 |
| `../core/components.css` | 页眉、索引、图注、表格、KPI、尺寸线等功能器件 |
| `../core/variations.css` | 显式选用的字带、裁字、双色摄影和程序图形 |
| `../core/atoms.css` | 独立原子、排印角色、图片与功能标记 |
| `folio.css` | 按上述顺序生成的完整单文件，供项目冻结复制 |
| `family.json` | 名称、版本、画布与实际字体资源 |

制作一册使用已生成的 `folio.css`，不修改共享源模块；正常项目不需要浏览器端构建或 CSS 框架依赖。源模块只供明确的主题维护任务。

```sh
python3 hb/core/family.py init folio /tmp/folio-book --title '书名' --langs zh-CN,en
```

初始化后，`project.json.styles` 依次加载 `folio.css` 和本书 `book.css`；语言覆盖、Folio 编辑覆盖由现有运行时追加。项目保存来源版本与 CSS 哈希，已建项目保持自己的冻结副本。升级时主动比较与重审受影响页面，不替换旧验收证据。Folio 会从本机读取 Noto Serif SC / Noto Sans SC / Inter 的源文件并生成本项目字体子集（OFL，可再分发）；字体文件不随本仓库分发。

## 组合层次

1. **Token** 确定共同数值，例如 `--fl-space-3`、`--fl-size-body`。
2. **原子** 完成单个选择，例如 `.fl-span-4`、`.fl-size-lead`、`.fl-fit-contain`。
3. **Layout** 表达关系，例如正文与旁栏、两图并列、时间与事项。
4. **组件配方** 组合前三层，例如人物署名、图与图注、目录、统计和引文。
5. **完整页面** 依据材料组合，具体文字、照片、分页和跨页关系由作者负责。

优先通过现有类组合完整页面，无需选整页模板。`book.css` 默认可空，只有明确的局部缺口才补丁；边界见 [主题与补丁](../../references/style.md)。普通段落不附送底色或边框；功能组件显式提供必要轴线与分隔，可用原子移除。

## 统一规则

- **颜色**：纸面 `#FFFFFF`，次级纸面 `#F2F0EB`，正文 `#111111`，辅助 `#625F59`，强调红 `#C83024`，深色面 `#141414`。文字使用语义角色，而非在子元素里写死纸面颜色。另有信号黄 `--fl-signal: #F5C84B` 与由强调色派生的网格层（`--fl-grid-tint` 8%、`--fl-grid-line` 32%），只服务 `.fl-programme` 的程序图形和 `.fl-show-columns` 诊断层，不替代正文色或强调色；品牌可整组覆写并重新测对比度。
- **字体**：标题随排印模式切换：默认 `bold` 用 Noto Serif SC，`light` 用 Noto Sans SC；阅读用 Noto Serif SC，正文用 Noto Sans SC，标签与数字用 Inter。标签、数字的中文回退到 Noto Sans SC。家族生成的每个声明字重都是静态真实字形，不合成粗体或斜体。
- **字号与字重**：默认 `bold`；在 `.page` 或任意片段上加 `.fl-type-light` 可切换，`.fl-type-bold` 可显式恢复。1 CSS px = 0.75pt；改变纸张不等比缩小文字。

  | 实际字号 | `bold` 字重 | `light` 字重 |
  |---|---:|---:|
  | ≥64px（display / hero） | 900 | 200 |
  | 44–63px（h1） | 700 | 250 |
  | 32–43px（h2） | 700 | 300 |
  | 20–31px（h3 / lead） | 600 | 400 |
  | 16–19px（body） | 400 | 400 |
  | 14–15px（small） | 500 | 500 |
  | <14px（key / aux） | 600 | 600 |

  `bold` 的内联强调在该字号字重上加 200、最高到 900；`light` 强调不跳字重。h1–h3 与 display 都跟随标题字体模式。数字角色与正文同族（Inter），字重跟随字号档位；不再保留专用数字字面。
- **行距**：body 1.75，reading 1.5，lead 1.6，tight 1.25，display 1.12。基线 28px 是正文的起点，字号与行距可独立组合。
- **间距**：0–8 对应 0/7/14/28/42/56/84/112/168px，即基线的 0、¼、½、1、1½、2、3、4、6 倍。段落默认半基线间距。
- **版心**：上18、下21、内19、外15mm；六栏/十二栏共用6mm栏距。版心取家族边距与当前印刷安全边距的较大值，另加出血。

明暗面重新绑定 `--fl-bg / --fl-text / --fl-text-muted / --fl-text-accent / --fl-stroke`。纸面嵌在深色面中时所有角色全部恢复；深色面嵌在纸面中时同理。任意改品牌色后仍需测量实际对比度。

## 原子 API

下表中的 `{…}` 表示实际存在的有限选择；不做任意数值类名解析。

| 类 | 作用 |
|---|---|
| `.fl-scope` | 在非页面展示片段中启用作用域默认样式；嵌套使用会明确开始新的纸面文字上下文 |
| `.fl-area` | 页内镜像安全版心，仅负责几何，不自动变成网格 |
| `.fl-grid` + `.fl-cols-{1,2,3,4,6,12}` | 统一栏距网格；默认行间距为space-3 |
| `.fl-span-{1…12}`、`.fl-span-full`、`.fl-start-{1…12}` | 跨栏与起栏，可组合；起栏+跨栏须在当前网格内 |
| `.fl-row-start-{1…6}` | 显式起行；行高由内容或本书 CSS 决定 |
| `.fl-rows-{2,3,4,6}`、`.fl-row-span-{1…6}`、`.fl-row-span-full` | 有界网格内的等分行、跨行与全行；必须给网格明确高度，内容溢出保持可见 |
| `.fl-flex`、`.fl-flex-col`、`.fl-wrap` | 独立选择 Flex、方向及换行 |
| `.fl-grow`、`.fl-shrink-0` | 子项伸展或避免收缩，不隐藏溢出 |
| `.fl-items-{start,center,end,baseline,stretch}` | 子项在交叉轴的对齐 |
| `.fl-self-{start,center,end,stretch}` | 单项在交叉轴的对齐 |
| `.fl-justify-self-{start,center,end,stretch}` | Grid 子项沿行内轴独立对齐；对 Flex 子项无效 |
| `.fl-justify-{start,center,end,between}` | 主轴内容分布 |
| `.fl-content-{start,center,end,between}` | 多行/多轨道内容分布 |
| `.fl-gap-{0…8}`、`.fl-gap-x-{0…8}`、`.fl-gap-y-{0…8}` | 全部、列、行间距 |
| `.fl-p-{0…8}`、`.fl-px-{0…8}`、`.fl-py-{0…8}` | 全部、左右、上下内边距 |
| `.fl-pt-{0…8}`、`.fl-pb-{0…8}`、`.fl-mt-{0…8}`、`.fl-mb-{0…8}` | 上下内/外边距 |
| `.fl-mt-auto` | 在剩余空间中把当前组推向底部，通常用于纵向Flex |
| `.fl-w-full`、`.fl-h-full`、`.fl-min-w-0` | 填满已定容器，或允许网格/Flex子项合理收缩 |
| `.fl-type-{bold,light}` | 在页面或片段切换共享字重阶梯与标题字体；默认 bold |
| `.fl-font-{display,reading,body,label,number}` | 字体角色；数字角色用 Inter 并保留等宽数字 |
| `.fl-size-{aux,key,small,body,lead,h3,h2,h1,display,hero,giant,colossal}` | 改变字号并选中对应的排印阶梯字重；可与字体角色组合 |
| `.fl-weight-{regular,strong}` | 选择当前字号档的常规/强调字重；light强调不加粗，bold按阶梯加200至多900 |
| `.fl-leading-{body,reading,lead,tight,display,hero}` | 独立行距 |
| `.fl-tracking-{tighter,tight,normal,wide}` | 字距 −.04em / −.02em / 0 / .12em |
| `.fl-text-{start,end,left,center,right}` | 文字对齐 |
| `.fl-text-{main,muted,accent}` | 当前表面下的语义文字色 |
| `.fl-tabular`、`.fl-balance` | 等宽数字、标题均衡换行 |
| `.fl-measure` | 行长上限，默认34ic，可用`--fl-measure`按内容调整 |
| `.fl-prose` | 直接子段落间space-2，保留自然流和完整文字 |
| `.fl-prose-columns-2` | 一个连续 DOM 文流自动平衡为两栏，栏距使用gutter；不自动分页 |
| `.fl-prose-indent` | 直接子段落从第二段起缩进2ic、取消段距；首段齐头，适用于中文连续正文 |
| `.fl-surface-{paper,soft,dark,accent}` | 背景与完整前景角色组合 |
| `.fl-tone-inverse` | 仅反白前景角色与文字色，不增加背景；需测量照片或自定色面上的实际对比 |
| `.fl-scrim-{top,bottom}` | 显式摄影渐变层，从指定边缘向透明过渡；不决定尺寸、文字或叠放许可 |
| `.fl-rule`、`.fl-rule-strong` | 1px语义细线或2px正文色主线，均为顶边线 |
| `.fl-relative`、`.fl-absolute`、`.fl-z-{0,1,2}` | 显式定位与层叠 |
| `.fl-bleed` | 相对定位父级的绝对满铺；满页出血时直接放在`.page`内 |
| `.fl-fill-lines`、`.fl-check` | 书写线、方形勾选标记；用途明确时添加 |
| `.fl-folio`、`.fl-running` | 安全区内的页码与页眉，按左右页镜像 |

排印角色类 `.fl-display / .fl-h1 / .fl-h2 / .fl-h3 / .fl-body / .fl-lead / .fl-key / .fl-aux / .fl-caption / .fl-kicker / .fl-number` 是上述属性的常用组合。可再叠加字号、字体、行距等原子；原子写在配方之后，覆盖规则明确。字号类与内容角色不同：正文、关键信息和图注仍需正确的 `data-role`。

`.fl-prose > p + p` 表达段落关系，优先级高于单类间距；特殊段落间距由本书选择器明确覆盖。其他冲突原子以 CSS 声明顺序为准，HTML里类名的排列不能改变优先级，同一属性每个元素选一个原子即可。

## 图片 API

| 类 | 作用 |
|---|---|
| `.fl-image` | 正常流图片：块级、宽100%、自然高度、默认居中 |
| `.fl-frame` | 图片框：默认3:2；直接子`img`填满并按cover裁切，图注应放框外 |
| `.fl-frame-fill` | 与frame组合，取消固有比例并填满已定高容器；用于有界网格图像格 |
| `.fl-image-fill` | 直接图片宽高100%，保留fit/focus；父容器必须已定高，可与bleed组合 |
| `.fl-ratio-{square,photo,landscape,portrait,wide,tall}` | 比例1:1 / 3:2 / 4:3 / 3:4 / 16:9 / 2:3；可放框或图片 |
| `.fl-fit-{cover,contain}` | 裁满或完整显示；可放框或直接放图片 |
| `.fl-focus-{top,bottom,left,right,center}` | 焦点居顶、底、左、右、中心；可放框或图片 |

自定义焦点可写 `style="--fl-focus-x:38%;--fl-focus-y:45%"`。焦点取决于实际照片，不做题材猜测。`contain` 保留图表、地图或标志全貌；`cover` 须审实际裁切。框只为图片设置裁切，不给文字增加隐藏或省略行为。

```html
<section class="page" data-page-id="p-observation">
  <div class="fl-area fl-grid fl-cols-6 fl-content-start">
    <header class="fl-span-full">
      <h1 class="fl-h1" data-role="display" data-source-id="title">走近树林</h1>
    </header>
    <figure class="fl-span-4">
      <div class="fl-frame fl-ratio-photo fl-focus-left">
        <img src="assets/images/forest.jpg" data-asset="forest" data-edit-id="forest-p1" alt="森林">
      </div>
      <figcaption class="fl-caption fl-mt-1" data-role="aux" data-source-id="caption">在真实图像下说明观察对象。</figcaption>
    </figure>
    <div class="fl-span-2 fl-prose">
      <p data-source-id="body">根据材料决定文字与图片的关系，再确认实际行长与裁切。</p>
    </div>
  </div>
  <span class="fl-folio" data-role="aux"></span>
</section>
```

## Layout 与组件

布局层负责比例、对齐、间距和定位，不设置字体、颜色或装饰。具名子项为 `.fl-l-main / .fl-l-aside / .fl-l-label / .fl-l-item / .fl-l-photo / .fl-l-copy / .fl-l-caption`，具体可用子项见展示的对应配方。stack、cluster、split、sidebar、offset、marginalia、hanging、comparison、chronology、photo-pair、photo-essay、contact、stagger、overlay、panorama 等按阅读关系选择。

组件配方应能展开为真实原子与布局。例如引文由字体、字号、行长、署名和留白组成；图注由照片与说明的关系组成；目录由标题与页码的对齐组成。线、底色和图片裁切均为显式选择。

## 有界模块、连续正文与摄影文字

二维网格需要一个明确的高度，例如 `class="fl-area fl-grid fl-cols-12 fl-rows-4"`。`fl-area` 的上下边界给它高度；跨行图片使用 `fl-frame fl-frame-fill`，文字仍完整显示。行轨道不会自动缩字、裁字或续排。起行与跨行必须落在声明的网格内；内容变长后重新测量。

`fl-prose-columns-2` 在同一个容器内继续文章，无需手工把左右栏拆为两份文案。默认自然高度按实际内容平衡；若人为固定高度，CSS 可能继续生成第三栏，必须检查完整阅读顺序与横向溢出，不可用隐藏修饰。`fl-prose-indent` 是另一种段落节奏，适合中文连续论述，英文或清单不默认套用。`fl-font-reading fl-leading-reading` 提供真实400字重衬线与1.5行距，可独立组合。

`fl-l-bleed-outer` 的子项仍为 `fl-l-photo` 和 `fl-l-copy fl-area`。照片以 `--fl-image-width`（默认43%）向书本外侧出血，文案保留内侧安全边距。偶数页默认向左、奇数页向右，显式 `data-side` 优先。照片仍需按实际方向声明 `data-bleed`；文本的安全与阅读宽度必须检查。原有 `fl-l-bleed-side` 保持物理右侧，已有项目不因新版改变方向。

照片叠字时，优先根据实际画面选择位置。`fl-tone-inverse` 只提供反白角色，照片本身保持可见。需要局部压暗时，显式增加 `fl-scrim-top` 或 `fl-scrim-bottom` 图层（例如再加 `fl-bleed`），默认色为 `--fl-scrim-color:rgb(8 18 30 / .88)`，在 `--fl-scrim-stop:72%` 处过渡透明；两项均可按实际画面调整。不要把渐变当作自动保证可读性的滤镜。

所有压在照片上的文字组仍写精确 `data-overlap="图片目标ID"`，不透明文字底板也不例外。图片优先使用真实 `img`，使有效分辨率与裁切可检查；不能用背景图或装饰角色绕过检查。叠放声明只解释几何关系，不降低真实背景上的对比度下限；印刷文字、图片与渐变应在最终PDF中一起复核。

## 物理边界与验证

- `.page` 尺寸、分页、出血变量和字体声明由运行时生成；家族不定义 `@page` 或 `@font-face`。
- 默认首张为右页，偶数同标签页面为左页。页面标签保持一致；左页起始或展示单页时显式设置 `data-side="left|right"`，实际全册页序仍以项目装订约定为准。
- `.fl-bleed` 仅提供几何；作者仍写`data-bleed`，叠放写相应局部声明，文字仍须在安全区。布局类不豁免测量。
- `.fl-area`、页码、页眉都读取实际安全边距。局部绝对定位、超长标题、跨栏数和任意自定义token仍需技术检查与PDF审稿。
- 不提供缩字救溢出、正文截断、line-clamp或隐藏内容的快捷类。放不下应调整分组、比例或分页。
- 展示与CSS组合说明不能替代最终PDF审稿；完整页、密集页、正文页和真实面对页均需检查。连续跨页图还须核对同源坐标、中缝和左右页。

## 版本

- **2.2.0**：选择性吸收用户提供的2.1参考包；Swiss结构、双排印、数字与正文同族；增加可覆写功能组件、摄影布局、显式表现工具与新样刊。
- **1.2.0**：恢复共享 bold/light 字重阶梯；标题字族随模式切换衬线/无衬线；字号原子同时选择字重。
- **1.1.0**：增加有界二维网格、填满图框、Grid单项横向对齐、镜像外侧出血、连续双栏/缩进、真实400衬线阅读字体、1.5行距、透明反白上下文与显式摄影渐变。布局与原子不改变检查下限；旧项目保留冻结副本。
- **1.0.0**：统一 tokens、作用域基底、组合原子、可选布局和可拆解组件示例。保留`.area`与`.display`两项最小初始化兼容别名；新写页面使用`.fl-*`。

## 企业信息与行程组件

展示目录同时包括多日行程、纵向时刻、比例节奏带、里程碑、并行泳道、KPI、目标对照、五力、定性矩阵、价值链与能力证据。完整范围见 [配方索引](recipe-index.md)。四种定量图表通过 [数据构造工具](../../references/charts.md) 输出，HTML标签接受原生印刷审计；CSS不承担数学计算。

图框默认 `--fl-frame-width:100%`、`--fl-frame-position:relative`；侧向出血布局在槽位中设定这两个变量，避免通用 `.fl-frame` 覆盖布局几何。直接尺寸原子或本书CSS仍可明确覆盖。


## Swiss 基础与新增 API（2.2）

参见[构图原则](../../references/swiss.md)。Swiss 决定共同的对齐与层级；标题继续使用 **bold 衬线 / light 无衬线**。摄影、企业数据和文字使用同一套类。默认纸白 #FFFFFF、墨黑 #111111、强调 #C83024、软纸 #F2F0EB；没有「每页必须一个红色块」的规则。

新增 `fl-size-giant` 196px、`fl-size-colossal` 280px，沿用 hero 的字重（bold900/light200）；大字仍用内容任务与实际页宽决定，不自动缩放。`fl-number / fl-font-number` 只换字体与数字特性，不覆盖字号阶梯的字重：字重仍由字号档位与 `fl-weight-*` 决定。数值表列使用 `fl-num`，混合文本中的纯数字可单独套 `fl-font-number`。没有自动扫描并替换所有数字。

| 组合 | 结构与边界 |
|---|---|
| `fl-meta / fl-foot / fl-foot-end` | 共用页眉/页脚轴线；线条可用 `fl-rule-none` 移除，不强制每页重复 |
| `fl-term` | 24px标题的对应术语，服从h3阶梯；可用字号/颜色原子覆盖 |
| `fl-index > li` + `fl-index-n / fl-index-end` | 编号、条目、页码/日期三列；前后数字与正文同族，可用 `fl-font-number` 等宽 |
| `fl-legend / fl-abb` | 编号—说明—来源的六轨图注，或普通行内编号 |
| `fl-dim / fl-dim-v` | 横/竖尺寸线，长度是容器尺寸；文字用子span，标注值由作者核实 |
| `fl-stat / fl-unit` | 数值、单位、解释；配fl-number，长数字改分栏，不挤压字宽 |
| `fl-table` + `fl-num` | 实际table结构、数值右齐；保留标题、单位、来源与th scope |
| `fl-list / fl-mark` | 悬挂列表、可选信号方点；不代替语义标签 |
| `fl-l-timeline / fl-l-item / fl-l-full` | `--fl-timeline-count`明确列数（默认4）；通栏说明不会新增隐式轨道 |
| `fl-axis / fl-axis-now` | 可选共享横轴与当前节点，强调色取当前表面角色 |
| `fl-l-bleed-top / fl-l-bleed-full` | `fl-l-photo`与`fl-l-copy fl-area`组合；顶部图高由`--fl-image-height`指定 |
| `fl-l-stair` | 每行依六轨错位，`--fl-step`可逐行指定；真实阅读顺序仍为DOM顺序 |
| `fl-show-columns / fl-show-columns-12 / fl-show-baseline` | 显式网格诊断层，可同时或嵌套使用；出成品前按页面目的决定是否移除 |
| `fl-hang / fl-optical` | 悬挂开头标点、微调大字左侧视觉对齐；检查安全区和真实字形 |
| `fl-proportional / fl-caps / fl-mono` | 比例数字、拉丁大写、灰度照片 |
| `fl-rule-heavy / fl-rule-accent / fl-rule-bottom / fl-rule-none` | 8px/强调色/下边线/移除边线，均显式选择 |
| `fl-scrim-start / fl-scrim-end` | 左/右摄影对比层；须检查实际照片文字，不保证可读性 |

## 显式表现工具

`variations.css` 在原子之前加载，默认值均可覆盖。不把装饰加入常规段落、引用或照片。正式配方的 `expressions` 分组给出这些能力的组合示例。

- `fl-band`：紧贴文字的硬边字带，可与任意 `fl-surface-*` 组合；完整可读标题仍是内容。
- `fl-crop` + `fl-crop-{top,bottom,left,right}`：锚定页边的巨字，偏移 `--fl-crop-offset`。被裁文字只能是重复装饰，需另有完整内容。
- `fl-type-photo`：本地照片填字；仅限重复装饰字，提供真实照片/等价标题，最终PDF检查字形和图片。
- `fl-duotone`：灰度照片乘色，变量 `--fl-duotone`；`fl-overprint`：CSS混合。两者不创建专色、印刷叠印或保证输出分辨率。
- `fl-programme`：显式空单元构成的程序纹样，可定列数/三色/间距；不是数据图，不能赋予随机单元业务含义。
- `fl-sign / fl-bullet`：导向组和字母/数字路线圆点，颜色必须伴随文字。底面另用surface原子。
- `fl-rotate-{6,n6} / fl-vertical / fl-sideways`：显式方向；旋转可能产生几何未验证，最终内容须满足契约，不能靠deco标签绕过检查。
- `fl-bleed-left / fl-bleed-right`：从版心边缘延伸到纸边，内部补偿留白；仅放在版心边缘，配真实data-bleed声明。

这些能力不是对任意内容和组合的预先保证；新册仍需技术验收与最终 PDF 逐页审稿。主题维护者的展示和回归记录位于源码仓库的开发目录，不属于正常制作依赖。
