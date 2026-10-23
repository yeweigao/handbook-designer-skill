---
name: handbook-designer
metadata:
  agent_created: true
description: 将 Word、PDF、PPT、Markdown 或文字材料制作为多页手册、宣传册、画册、指南或任务册；支持品牌、系列与改版。以 Folio 主题创作 HTML/CSS/SVG，交付经检查的 PDF、离线 HTML 与可重建源包。不用于幻灯片或网站。
---

# Folio 手册设计

把真实材料做成可阅读、可查阅、有表现力的印刷册。读者能辨认主张、找到证据、完成行动；开场、密集正文、摄影与查阅页共享同一设计语言。具体构图由材料决定，避免把整册写成重复的网页卡片。

用户明确要求优先于本 Skill 的默认设计偏好；如与交付能力或硬契约冲突，说明具体影响。常规设计决定自主完成，只询问会实质改变结果且无法合理推断的信息。

## 设计契约：用 Folio，先组合，必要时补丁

**新册以 `folio.css` 为主题，`book.css` 默认留空。** 从 [Folio API](families/folio/README.md) 和 [配方索引](families/folio/recipe-index.md) 选用已有 token、原子、布局与组件；摄影、时间轴、图表均在同一系统内。正常制作不需要开发目录。

- **共同语言**：Swiss 网格、对齐、比例与留白组织阅读，连续正文左齐右松。`fl-type-bold` 用衬线标题；`fl-type-light` 用非衬线标题、大字更轻。数字用 Inter，字重随字阶。线条与色面只承担分隔、导航或表达任务，不自动给段落添加侧边线、圆角卡片、阴影或渐变底。
- **有限扩展**：仅当现有组合无法表达真实阅读任务时，在 `book.css` 加局部几何、裁切或已授权的品牌补丁。沿用 Folio token，限定页面或组件作用域；在 `style-lock.md` 合并记录“任务 → 现有能力缺口 → 补丁范围”。内联、语言 CSS 和新类名遵守同一边界，不能另造字阶、间距或全局组件皮肤。完整边界见 [主题与补丁](references/style.md)。
- **冻结主题**：项目 `styles[0]` 是只读家族副本，新 Folio 为 `folio.css`，旧项目可为 `design.css`。保留来源版本与哈希；制作一册不修改共享家族。明确授权的主题升级另存基线、记录差异并重审受影响页面，不能改哈希来掩盖意外修改。

## 必须留下的证据

- **材料**：原稿保留在 `sources/original/`，提取稿与稳定段 ID 留在 `sources/`。`carry / polish / translate / frozen` 以授权为准；事实、数字、限定条件不为排版改变，不把隐藏内容当已呈现。[文案适配](references/adaptation.md) 与 [编辑审阅](references/editorial-advisor.md) 仅在相应任务时读。
- **设计判断**：一句适合材料的视觉主张与简短页面任务。铺全册前用真实内容完成开场、密集正文、最难页三页小样，最多三轮，结论写入 [style-lock](templates/style-lock.md)；可依据已有授权自主审定，不新增固定审批。
- **作者源**：`book.html` 与必要的 `book.css`；多语言共用结构，其他文案在 `copy/`、局部差异在 `lang/`。稳定内容/页面/编辑 ID、角色、出血和叠放依 [契约](references/contract.md)。尺寸与字体只在 `project.json` 声明，图片与静态字体随项目本地化。
- **成品**：所有语言技术检查通过，并实际查看当前最终 PDF 的整册、面对页与每页阅读尺度；修订后复核。技术通过不等于设计优秀，作者自评不称独立评测。输入或 PDF 变化后旧验收失效，正式导出必须绑定当前证据。

空间不足优先调整内容分组、栏宽与分页；不靠缩字、挤行距、删书写区或隐藏文字换通过。图片核实主体、来源与授权；缺照片可做纯文字设计，不用无关图或合成占位充当真实素材。

## 按任务选路

| 请求 | 选读 |
|---|---|
| 有材料，制作新册 | [new](workflows/new.md)；直接做或无人值守用 [quick](workflows/quick.md) |
| 定稿美化、冻结内容 | [beautify](workflows/beautify.md) |
| 沿用系列 / 修改或接续 | [reuse](workflows/reuse.md) / [revise](workflows/revise.md) |
| 品牌适配 / 缺事实材料 | [brand](workflows/brand.md) / [research](workflows/research.md)，再回制作 |
| 用户自己改字换图 | [edit-online](workflows/edit-online.md) |

构图判断按需读 [Swiss](references/swiss.md)、[composition](references/composition.md)、[页面写法](references/layouts.md)、[图片](references/images.md)、[长文](references/blocks.md)、[图表](references/charts.md)，不预先加载全部参考。用途和品牌只提供与本次材料有关的约束。

## 执行与交付

常用命令见 [commands](references/commands.md)，新环境见 [delivery](references/delivery.md)。初始化 Folio → 创作作者源 → `validate` / `check` → [最终 PDF 审稿](workflows/visual-review.md) → `review` / `export` 是交付依赖，不规定中间如何构思、拆分任务或调用工具。`render` 只有快照，未经完整验收只能交带水印草稿。

交付各语言 PDF、可编辑 PDF、离线 HTML、整册/跨页预览、源包、`credits.md` 与 `delivery.json`。回复给成品链接、页数/语言、主要设计决定和实际未解决项；记录 [experience](templates/experience.md) 供接续。不能以完成计划或通过检查代替完成作品。
