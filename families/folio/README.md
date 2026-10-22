# Folio CSS · 1.0.0

一套供印刷页面使用的 CSS 语言。相同的颜色角色、字体、网格和节奏可以组合出纯文字、摄影、信息查阅和混合页面。普通 HTML/CSS 是作者源，布局类是可选起点，组件是可拆开的组合示例。

[交互展示](../../dev/folio-css/index.html) 展示原子、布局及组件；[示例目录](../../dev/folio-css/catalog.json) 保存真实 HTML 配方。示例中的代码使用本家族实际 CSS，展示网页的导航和缩放不进入印刷文件。

## 文件与使用

| 文件 | 职责 |
|---|---|
| `tokens.css` | 颜色、字体、字号、行距、版心和间距的统一数值 |
| `../core/base.css` | 作用域 reset、页面基底、镜像版心 |
| `../core/layouts.css` | 可选的结构关系与具名子项 |
| `../core/atoms.css` | 独立原子、排印角色、图片与功能标记 |
| `design.css` | 按上述顺序生成的完整单文件，供项目冻结复制 |
| `family.json` | 名称、版本、画布与实际字体资源 |

修改源模块后执行 `python3 dev/build-folio-css.py` 重建 `design.css`。项目初始化仍只复制一个 CSS 文件，不在运行时加载共享模块，不需要浏览器端构建或 CSS 框架依赖。

```sh
python3 hb/core/family.py init folio /tmp/folio-book --title '书名' --langs zh-CN,en
```

初始化后，`project.json.styles` 依次加载 `design.css` 和本书 `book.css`；语言覆盖、Folio 编辑覆盖由现有运行时追加。项目保存来源版本与 CSS 哈希，已建项目保持自己的冻结副本。升级时主动比较与重审受影响页面，不替换旧验收证据。

## 组合层次

1. **Token** 确定共同数值，例如 `--fl-space-3`、`--fl-size-body`。
2. **原子** 完成单个选择，例如 `.fl-span-4`、`.fl-size-lead`、`.fl-fit-contain`。
3. **Layout** 表达关系，例如正文与旁栏、两图并列、时间与事项。
4. **组件配方** 组合前三层，例如人物署名、图与图注、目录、统计和引文。
5. **完整页面** 依据材料组合，具体文字、照片、分页和跨页关系由作者负责。

无需选整页模板才能开始。可保留布局的结构，调整原子或使用本书 CSS；也可直接写新的原生 Grid/Flex。组件不自动附送底色、边框或装饰。

## 统一规则

- **颜色**：纸面 `#FFFEFA`，次级纸面 `#F0EEE8`，正文 `#202B32`，辅助 `#56616A`，强调蓝 `#164BE8`，深色面 `#182238`。文字使用语义角色，而非在子元素里写死纸面颜色。
- **字体**：展示 Noto Serif SC 700；正文 Noto Sans SC 400/700；标签 Inter 400/600；数字 Inter 600。标签和数字的中文回退为已声明 Noto Sans SC。没有假斜体或模拟 900 字重。
- **字号**：aux 11、key 13、body 16、lead 20、h3 24、h2 32、h1 46、display 64、hero 112px。1 CSS px = 0.75pt；改变纸张不等比缩小文字。
- **行距**：body 1.75，lead 1.6，tight 1.25，display 1.12。基线 28px 是正文的起点，字号与行距可独立组合。
- **间距**：0–6 对应 0/7/14/28/42/56/84px，即基线的 0、¼、½、1、1½、2、3 倍。段落默认半基线间距。
- **版心**：上18、下21、内19、外15mm；六栏/十二栏共用6mm栏距。版心取家族边距与当前印刷安全边距的较大值，另加出血。

明暗面重新绑定 `--fl-text / --fl-text-muted / --fl-text-accent / --fl-stroke`。纸面嵌在深色面中时四个角色全部恢复；深色面嵌在纸面中时同理。任意改品牌色后仍需测量实际对比度。

## 原子 API

下表中的 `{…}` 表示实际存在的有限选择；不做任意数值类名解析。

| 类 | 作用 |
|---|---|
| `.fl-scope` | 在非页面展示片段中启用作用域默认样式；嵌套使用会明确开始新的纸面文字上下文 |
| `.fl-area` | 页内镜像安全版心，仅负责几何，不自动变成网格 |
| `.fl-grid` + `.fl-cols-{1,2,3,4,6,12}` | 统一栏距网格；默认行间距为space-3 |
| `.fl-span-{1…12}`、`.fl-span-full`、`.fl-start-{1…12}` | 跨栏与起栏，可组合；起栏+跨栏须在当前网格内 |
| `.fl-row-start-{1…6}` | 显式起行；行高由内容或本书 CSS 决定 |
| `.fl-flex`、`.fl-flex-col`、`.fl-wrap` | 独立选择 Flex、方向及换行 |
| `.fl-grow`、`.fl-shrink-0` | 子项伸展或避免收缩，不隐藏溢出 |
| `.fl-items-{start,center,end,baseline,stretch}` | 子项在交叉轴的对齐 |
| `.fl-self-{start,center,end,stretch}` | 单项在交叉轴的对齐 |
| `.fl-justify-{start,center,end,between}` | 主轴内容分布 |
| `.fl-content-{start,center,end,between}` | 多行/多轨道内容分布 |
| `.fl-gap-{0…6}`、`.fl-gap-x-{0…6}`、`.fl-gap-y-{0…6}` | 全部、列、行间距 |
| `.fl-p-{0…6}`、`.fl-px-{0…6}`、`.fl-py-{0…6}` | 全部、左右、上下内边距 |
| `.fl-pt-{0…6}`、`.fl-pb-{0…6}`、`.fl-mt-{0…6}`、`.fl-mb-{0…6}` | 上下内/外边距 |
| `.fl-mt-auto` | 在剩余空间中把当前组推向底部，通常用于纵向Flex |
| `.fl-w-full`、`.fl-h-full`、`.fl-min-w-0` | 填满已定容器，或允许网格/Flex子项合理收缩 |
| `.fl-font-{display,body,label,number}` | 字体角色及它对应的真实常规/强调字重 |
| `.fl-size-{aux,key,body,lead,h3,h2,h1,display,hero}` | 只改变字号 |
| `.fl-weight-{regular,strong}` | 按当前字体角色选实际字重；display两者均700，number两者均600 |
| `.fl-leading-{body,lead,tight,display}` | 独立行距 |
| `.fl-tracking-{tight,normal,wide}` | 字距 −.02em / 0 / .12em |
| `.fl-text-{left,center,right}` | 文字对齐 |
| `.fl-text-{main,muted,accent}` | 当前表面下的语义文字色 |
| `.fl-tabular`、`.fl-balance` | 等宽数字、标题均衡换行 |
| `.fl-measure` | 行长上限，默认34ic，可用`--fl-measure`按内容调整 |
| `.fl-prose` | 直接子段落间space-2，保留自然流和完整文字 |
| `.fl-surface-{paper,soft,dark,accent}` | 背景与完整前景角色组合 |
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

## 物理边界与验证

- `.page` 尺寸、分页、出血变量和字体声明由运行时生成；家族不定义 `@page` 或 `@font-face`。
- 默认首张为右页，偶数同标签页面为左页。页面标签保持一致；左页起始或展示单页时显式设置 `data-side="left|right"`，实际全册页序仍以项目装订约定为准。
- `.fl-bleed` 仅提供几何；作者仍写`data-bleed`，叠放写相应局部声明，文字仍须在安全区。布局类不豁免测量。
- `.fl-area`、页码、页眉都读取实际安全边距。局部绝对定位、超长标题、跨栏数和任意自定义token仍需技术检查与PDF审稿。
- 不提供缩字救溢出、正文截断、line-clamp或隐藏内容的快捷类。放不下应调整分组、比例或分页。
- 展示与CSS组合说明不能替代最终PDF审稿；完整页、密集页、正文页和真实面对页均需检查。连续跨页图还须核对同源坐标、中缝和左右页。

## 版本

- **1.0.0**：统一 tokens、作用域基底、组合原子、可选布局和可拆解组件示例。保留`.area`与`.display`两项最小初始化兼容别名；新写页面使用`.fl-*`。
