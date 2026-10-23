# Folio 配方索引

由同一设计系统目录生成；正式用法只需本目录的 `folio.css`、本索引和 [recipes.json](recipes.json)。
当前 91 项配方，覆盖 353 个公开类。先查阅读任务与类名，再按 id 读取需要的配方；不必整份载入。

图片 `assets/images/<文件名>` 是待替换的项目内示例路径，随包不提供图片。以项目真实内容、已登记图片和画布替换示意；配方展示尺寸、文字和数值不是交付内容。

按 id 读取完整 HTML、约束与图表数据：

```bash
python3 - <skill目录>/families/folio/recipes.json photo-pair <<'PY'
import json, sys
data = json.load(open(sys.argv[1], encoding='utf-8'))
entry = next((item for group in ('atoms', 'layouts', 'components', 'expressions')
              for item in data[group] if item['id'] == sys.argv[2]), None)
if entry is None: raise SystemExit('未找到配方 ID：' + sys.argv[2])
print(json.dumps(entry, ensure_ascii=False, indent=2))
PY
```

## 原子 · 26 项

| ID | 名称 | 公开类 |
|---|---|---|
| `a-surface` | 表面与前景角色 | `fl-surface-paper` · `fl-surface-soft` · `fl-surface-dark` · `fl-surface-accent` · `fl-text-main` · `fl-text-muted` · `fl-text-accent` · `fl-tone-inverse` |
| `a-profiles` | 两种标题结构 | `fl-type-bold` · `fl-type-light` |
| `a-roles` | 文字的阅读任务 | `fl-display` · `fl-h1` · `fl-h2` · `fl-h3` · `fl-lead` · `fl-body` · `fl-key` · `fl-aux` · `fl-caption` · `fl-kicker` · `fl-number` |
| `a-font` | 字体与真实字重 | `fl-font-display` · `fl-font-reading` · `fl-font-body` · `fl-font-label` · `fl-font-number` · `fl-weight-regular` · `fl-weight-strong` |
| `a-scale` | 从图注到标题的字阶 | `fl-size-aux` · `fl-size-key` · `fl-size-small` · `fl-size-body` · `fl-size-lead` · `fl-size-h3` · `fl-size-h2` · `fl-size-h1` · `fl-size-display` |
| `a-large` | 大字作为画面 | `fl-size-hero` · `fl-size-giant` · `fl-size-colossal` |
| `a-leading` | 行距与字距 | `fl-leading-body` · `fl-leading-reading` · `fl-leading-lead` · `fl-leading-tight` · `fl-leading-display` · `fl-leading-hero` · `fl-tracking-tighter` · `fl-tracking-tight` · `fl-tracking-normal` · `fl-tracking-wide` |
| `a-alignment` | 对齐、标点与数字 | `fl-text-start` · `fl-text-end` · `fl-text-left` · `fl-text-center` · `fl-text-right` · `fl-tabular` · `fl-proportional` · `fl-balance` · `fl-caps` · `fl-hang` · `fl-optical` |
| `a-prose` | 连续文流与行长 | `fl-measure` · `fl-prose` · `fl-prose-columns-2` · `fl-prose-indent` |
| `a-grid` | 共同的横向网格 | `fl-grid` · `fl-cols-1` · `fl-cols-2` · `fl-cols-3` · `fl-cols-4` · `fl-cols-6` · `fl-cols-12` |
| `a-span` | 横向跨度与起点 | `fl-span-1` · `fl-span-2` · `fl-span-3` · `fl-span-4` · `fl-span-5` · `fl-span-6` · `fl-span-7` · `fl-span-8` · `fl-span-9` · `fl-span-10` · `fl-span-11` · `fl-span-12` · `fl-span-full` · `fl-start-1` · `fl-start-2` · `fl-start-3` · `fl-start-4` · `fl-start-5` · `fl-start-6` · `fl-start-7` · `fl-start-8` · `fl-start-9` · `fl-start-10` · `fl-start-11` · `fl-start-12` |
| `a-rows` | 二维模块网格 | `fl-rows-2` · `fl-rows-3` · `fl-rows-4` · `fl-rows-6` · `fl-row-start-1` · `fl-row-start-2` · `fl-row-start-3` · `fl-row-start-4` · `fl-row-start-5` · `fl-row-start-6` · `fl-row-span-1` · `fl-row-span-2` · `fl-row-span-3` · `fl-row-span-4` · `fl-row-span-5` · `fl-row-span-6` · `fl-row-span-full` |
| `a-flex` | 流动分组 | `fl-flex` · `fl-flex-col` · `fl-wrap` · `fl-grow` · `fl-shrink-0` |
| `a-align-items` | 内容的对齐轴 | `fl-items-start` · `fl-items-center` · `fl-items-end` · `fl-items-baseline` · `fl-items-stretch` · `fl-self-start` · `fl-self-center` · `fl-self-end` · `fl-self-stretch` · `fl-justify-start` · `fl-justify-center` · `fl-justify-end` · `fl-justify-between` · `fl-justify-self-start` · `fl-justify-self-center` · `fl-justify-self-end` · `fl-justify-self-stretch` · `fl-content-start` · `fl-content-center` · `fl-content-end` · `fl-content-between` |
| `a-grid-guide` | 可见的结构辅助线 | `fl-show-columns` · `fl-show-columns-12` · `fl-show-baseline` |
| `a-gaps` | 元素间距 | `fl-gap-0` · `fl-gap-1` · `fl-gap-2` · `fl-gap-3` · `fl-gap-4` · `fl-gap-5` · `fl-gap-6` · `fl-gap-7` · `fl-gap-8` · `fl-gap-x-0` · `fl-gap-x-1` · `fl-gap-x-2` · `fl-gap-x-3` · `fl-gap-x-4` · `fl-gap-x-5` · `fl-gap-x-6` · `fl-gap-x-7` · `fl-gap-x-8` · `fl-gap-y-0` · `fl-gap-y-1` · `fl-gap-y-2` · `fl-gap-y-3` · `fl-gap-y-4` · `fl-gap-y-5` · `fl-gap-y-6` · `fl-gap-y-7` · `fl-gap-y-8` |
| `a-padding` | 容器内留白 | `fl-p-0` · `fl-p-1` · `fl-p-2` · `fl-p-3` · `fl-p-4` · `fl-p-5` · `fl-p-6` · `fl-p-7` · `fl-p-8` · `fl-px-0` · `fl-px-1` · `fl-px-2` · `fl-px-3` · `fl-px-4` · `fl-px-5` · `fl-px-6` · `fl-px-7` · `fl-px-8` · `fl-py-0` · `fl-py-1` · `fl-py-2` · `fl-py-3` · `fl-py-4` · `fl-py-5` · `fl-py-6` · `fl-py-7` · `fl-py-8` · `fl-pt-0` · `fl-pt-1` · `fl-pt-2` · `fl-pt-3` · `fl-pt-4` · `fl-pt-5` · `fl-pt-6` · `fl-pt-7` · `fl-pt-8` · `fl-pb-0` · `fl-pb-1` · `fl-pb-2` · `fl-pb-3` · `fl-pb-4` · `fl-pb-5` · `fl-pb-6` · `fl-pb-7` · `fl-pb-8` |
| `a-margin` | 段落与章节停顿 | `fl-mt-0` · `fl-mt-1` · `fl-mt-2` · `fl-mt-3` · `fl-mt-4` · `fl-mt-5` · `fl-mt-6` · `fl-mt-7` · `fl-mt-8` · `fl-mb-0` · `fl-mb-1` · `fl-mb-2` · `fl-mb-3` · `fl-mb-4` · `fl-mb-5` · `fl-mb-6` · `fl-mb-7` · `fl-mb-8` · `fl-mt-auto` |
| `a-sizing` | 内容尺寸与剩余空间 | `fl-w-full` · `fl-h-full` · `fl-min-w-0` |
| `a-image` | 图像比例与原始尺寸 | `fl-image` · `fl-image-fill` · `fl-frame` · `fl-frame-fill` · `fl-ratio-square` · `fl-ratio-photo` · `fl-ratio-wide` · `fl-ratio-portrait` · `fl-ratio-tall` · `fl-ratio-landscape` |
| `a-crop` | 裁切焦点与容纳 | `fl-focus-top` · `fl-focus-bottom` · `fl-focus-left` · `fl-focus-right` · `fl-focus-center` · `fl-fit-cover` · `fl-fit-contain` · `fl-mono` |
| `a-scrim` | 图上文字的对比层 | `fl-scrim-top` · `fl-scrim-bottom` · `fl-scrim-start` · `fl-scrim-end` |
| `a-rules` | 线与色块的分量 | `fl-rule` · `fl-rule-strong` · `fl-rule-heavy` · `fl-rule-accent` · `fl-rule-bottom` · `fl-rule-none` · `fl-fill-accent` · `fl-fill-ink` · `fl-fill-soft` |
| `a-marks` | 查阅与书写 | `fl-fill-lines` · `fl-check` · `fl-running` · `fl-folio` |
| `a-page` | 页面几何与图层 | `fl-scope` · `fl-area` · `fl-relative` · `fl-absolute` · `fl-bleed` · `fl-z-0` · `fl-z-1` · `fl-z-2` |
| `a-direction` | 竖排与侧向阅读 | `fl-vertical` · `fl-sideways` |

## 布局 · 21 项

| ID | 名称 | 公开类 |
|---|---|---|
| `flow` | 行间与段间 | `fl-l-stack` · `fl-l-cluster` · `fl-gap-2` · `fl-gap-4` |
| `split` | 双栏阅读 | `fl-l-split` · `fl-l-full` |
| `sidebar-offset` | 主文与侧栏 | `fl-l-sidebar` · `fl-l-offset` · `fl-l-main` · `fl-l-aside` · `fl-l-full` |
| `marginalia` | 贴近段落的旁注 | `fl-l-marginalia` · `fl-l-pair` · `fl-l-main` · `fl-l-aside` |
| `hanging` | 悬挂编号 | `fl-l-hanging` · `fl-l-label` · `fl-l-main` |
| `comparison` | 同行对照 | `fl-l-comparison` · `fl-l-pair` |
| `chronology` | 时间与事件 | `fl-l-chronology` · `fl-l-item` · `fl-l-label` · `fl-l-main` |
| `photo-pair` | 并置的两张照片 | `fl-l-photo-pair` · `fl-frame` · `fl-ratio-portrait` · `fl-l-full` |
| `photo-essay` | 主图与两个细节 | `fl-l-photo-essay` · `fl-l-main` · `fl-l-aside` · `fl-l-full` |
| `contact` | 六图接触印样 | `fl-l-contact` · `fl-frame` · `fl-ratio-photo` · `fl-l-full` |
| `masonry` | 有边界的组图 | `fl-l-masonry` · `fl-l-column` · `fl-frame` · `fl-l-full` |
| `stagger` | 错位的图像叙事 | `fl-l-stagger` · `fl-l-item` · `fl-l-full` |
| `edge-photo` | 照片走到页边 | `fl-l-bleed-bottom` · `fl-l-bleed-side` · `fl-l-photo` · `fl-l-copy` · `fl-area` |
| `overlay` | 图文跨过边界 | `fl-l-overlay` · `fl-l-photo` · `fl-l-copy` · `fl-l-caption` |
| `panorama` | 同一场景的面对页 | `fl-l-panorama` · `fl-l-panorama-image` · `fl-area` |
| `typographic` | 文字的停顿 | `fl-l-typographic` · `fl-l-title` · `fl-l-aside` · `fl-l-main` |
| `bleed-top` | 顶部通栏摄影 | `fl-l-bleed-top` · `fl-l-photo` · `fl-l-copy` · `fl-area` |
| `bleed-full` | 满版摄影 | `fl-l-bleed-full` · `fl-l-photo` · `fl-l-copy` · `fl-area` |
| `bleed-outer` | 外侧出血摄影 | `fl-l-bleed-outer` · `fl-l-photo` · `fl-l-copy` · `fl-area` |
| `timeline-grid` | 同一轴线的时间 | `fl-l-timeline` · `fl-l-item` · `fl-l-full` |
| `stair-grid` | 递进与阶梯 | `fl-l-stair` |

## 组件 · 36 项

| ID | 名称 | 公开类 |
|---|---|---|
| `opening` | 眉题、标题、导语 | `fl-l-stack` · `fl-kicker` · `fl-h1` · `fl-lead` · `fl-gap-2` |
| `quotation` | 引文与署名 | `fl-l-stack` · `fl-font-display` · `fl-size-h3` · `fl-leading-lead` · `fl-key` |
| `caption` | 图片与分层图注 | `fl-frame` · `fl-ratio-wide` · `fl-caption` · `fl-aux` · `fl-l-stack` |
| `number-unit` | 数字、单位与解释 | `fl-l-cluster` · `fl-items-baseline` · `fl-number` · `fl-size-hero` · `fl-tabular` · `fl-key` |
| `contents` | 目录条目 | `fl-l-stack` · `fl-l-hanging` · `fl-l-label` · `fl-l-main` · `fl-flex` · `fl-justify-between` |
| `question-answer` | 问答条目 | `fl-l-stack` · `fl-l-hanging` · `fl-l-label` · `fl-l-main` · `fl-h3` · `fl-body` |
| `checklist` | 可勾选清单 | `fl-l-stack` · `fl-l-hanging` · `fl-check` · `fl-body` |
| `open-table` | 开放式表格 | `fl-w-full` · `fl-rule` · `fl-rule-strong` · `fl-key` · `fl-weight-strong` · `fl-py-2` · `fl-px-2` |
| `itinerary-days` | 多日行程 · 张弛安排 | `fl-cols-3` · `fl-grid` · `fl-h3` · `fl-key` · `fl-kicker` · `fl-mb-2` |
| `timeline-vertical` | 纵向 timeline · 当日时刻 | `fl-h3` · `fl-key` · `fl-l-chronology` · `fl-l-item` · `fl-l-label` · `fl-l-main` · `fl-mb-2` · `fl-tabular` |
| `rhythm-band` | 节奏时间带 · 按时长比例 | `fl-caption` · `fl-cols-12` · `fl-cols-3` · `fl-gap-0` · `fl-gap-2` · `fl-grid` · `fl-key` · `fl-l-stack` · `fl-span-1` · `fl-span-2` · `fl-span-3` · `fl-span-4` · `fl-surface-accent` · `fl-surface-dark` · `fl-surface-soft` · `fl-weight-strong` |
| `milestones` | 横向 timeline · 阶段里程碑 | `fl-cols-3` · `fl-grid` · `fl-h3` · `fl-key` · `fl-kicker` · `fl-mb-2` |
| `swimlane` | 并行泳道 · 谁在何时做什么 | `fl-key` · `fl-py-2` · `fl-rule` |
| `kpi-evidence` | 关键指标 · 数字与口径 | `fl-caption` · `fl-cols-3` · `fl-grid` · `fl-h3` · `fl-key` · `fl-kicker` · `fl-mb-2` · `fl-mt-3` |
| `target-actual` | 目标与实际 · 差距可见 | `fl-caption` · `fl-key` · `fl-mt-2` · `fl-py-2` · `fl-rule` · `fl-tabular` |
| `five-forces` | 波特五力 · 行业结构 | `fl-caption` · `fl-cols-3` · `fl-gap-3` · `fl-grid` · `fl-h3` · `fl-key` · `fl-mb-2` · `fl-mt-3` · `fl-p-3` · `fl-row-start-2` · `fl-row-start-3` · `fl-start-1` · `fl-start-2` · `fl-surface-dark` |
| `decision-matrix` | 二维决策矩阵 · 取舍有轴 | `fl-caption` · `fl-cols-2` · `fl-gap-0` · `fl-gap-2` · `fl-grid` · `fl-h3` · `fl-key` · `fl-l-stack` · `fl-mb-2` · `fl-p-3` · `fl-rule` · `fl-surface-soft` · `fl-weight-strong` |
| `value-chain` | 价值链 · 从能力到结果 | `fl-caption` · `fl-cols-3` · `fl-grid` · `fl-h3` · `fl-key` · `fl-kicker` · `fl-mb-2` · `fl-mt-3` |
| `capability-table` | 能力对照 · 可核验的主张 | `fl-caption` · `fl-key` · `fl-mt-2` · `fl-py-2` · `fl-rule` |
| `claim-evidence` | 结论与证据 · 咨询式图文组 | `fl-body` · `fl-h3` · `fl-key` · `fl-kicker` · `fl-l-aside` · `fl-l-main` · `fl-l-sidebar` · `fl-mb-2` · `fl-weight-strong` |
| `swiss-furniture` | 页眉与页脚 · 阅读坐标 | `fl-foot` · `fl-foot-end` · `fl-gap-5` · `fl-h1` · `fl-key` · `fl-l-aside` · `fl-l-main` · `fl-l-sidebar` · `fl-l-stack` · `fl-meta` · `fl-pt-4` · `fl-text-muted` |
| `swiss-index` | 目录与索引 · 编号先行 | `fl-body` · `fl-gap-4` · `fl-h1` · `fl-index` · `fl-index-end` · `fl-index-n` · `fl-l-stack` |
| `swiss-term` | 双语术语 · 同一语义层级 | `fl-body` · `fl-display` · `fl-gap-2` · `fl-key` · `fl-l-aside` · `fl-l-main` · `fl-l-offset` · `fl-l-stack` · `fl-mt-4` · `fl-term` · `fl-text-muted` |
| `swiss-legend` | 照片图注 · 编号、说明与来源 | `fl-frame` · `fl-gap-2` · `fl-l-stack` · `fl-legend` · `fl-ratio-wide` |
| `swiss-dimensions` | 尺寸标注 · 观察与测量 | `fl-abb` · `fl-caption` · `fl-dim` · `fl-dim-v` · `fl-frame` · `fl-gap-3` · `fl-grid` · `fl-h2` · `fl-l-stack` · `fl-ratio-wide` |
| `swiss-statistics` | 关键数字 · 数值与口径 | `fl-caption` · `fl-cols-3` · `fl-gap-4` · `fl-grid` · `fl-h2` · `fl-key` · `fl-l-stack` · `fl-mb-2` · `fl-number` · `fl-stat` · `fl-text-muted` · `fl-unit` |
| `swiss-data-table` | 经营表格 · 文字左齐，数字右齐 | `fl-caption` · `fl-gap-3` · `fl-h2` · `fl-key` · `fl-l-stack` · `fl-mb-2` · `fl-num` · `fl-table` · `fl-text-left` |
| `swiss-hanging-list` | 悬挂列表 · 保持左边界 | `fl-body` · `fl-h2` · `fl-key` · `fl-l-aside` · `fl-l-main` · `fl-l-offset` · `fl-list` · `fl-mb-2` · `fl-text-muted` |
| `swiss-event-axis` | 时间轴 · 节点与当前阶段 | `fl-axis` · `fl-axis-now` · `fl-font-number` · `fl-gap-4` · `fl-h2` · `fl-h3` · `fl-key` · `fl-l-item` · `fl-l-stack` · `fl-l-timeline` |
| `swiss-stair-heading` | 阶梯标题 · 按阅读顺序递进 | `fl-gap-4` · `fl-h1` · `fl-key` · `fl-l-stack` · `fl-l-stair` · `fl-mt-3` · `fl-text-muted` |
| `swiss-negative-space` | 留白构图 · 空轨也有作用 | `fl-body` · `fl-cols-6` · `fl-foot` · `fl-grid` · `fl-h1` · `fl-key` · `fl-lead` · `fl-mb-2` · `fl-mt-3` · `fl-mt-4` · `fl-mt-7` · `fl-span-4` · `fl-span-full` · `fl-start-3` · `fl-text-muted` |
| `swiss-type-image` | 字即构图 · 巨字与真实标题 | `fl-cols-6` · `fl-font-display` · `fl-grid` · `fl-h2` · `fl-items-end` · `fl-key` · `fl-leading-display` · `fl-mark` · `fl-mt-3` · `fl-size-giant` · `fl-span-3` |
| `chart-bar` | 排名比较 · 直接标值 | `fl-caption` · `fl-mt-2` |
| `chart-line` | 经营趋势 · 连续期间 | `fl-caption` · `fl-mt-2` |
| `chart-stacked` | 构成比较 · 每组共 100% | `fl-caption` · `fl-mt-2` |
| `chart-waterfall` | 瀑布图 · 解释增减 | `fl-caption` · `fl-mt-2` |

## 表现与变奏 · 8 项

| ID | 名称 | 公开类 |
|---|---|---|
| `x-band` | 硬边字带与反白 | `fl-band` · `fl-surface-dark` · `fl-surface-accent` · `fl-surface-soft` |
| `x-crop` | 裁字与页边 | `fl-crop` · `fl-crop-top` · `fl-crop-bottom` · `fl-crop-left` · `fl-crop-right` · `fl-bleed-right` |
| `x-photo-type` | 照片进入字形 | `fl-type-photo` |
| `x-duotone` | 双色摄影与原色 | `fl-duotone` · `fl-frame-fill` |
| `x-overprint` | 交叠与方向 | `fl-overprint` · `fl-rotate-6` · `fl-rotate-n6` · `fl-surface-accent` |
| `x-programme` | 规则生成的图形 | `fl-programme` |
| `x-sign` | 导向与路线标识 | `fl-sign` · `fl-bullet` |
| `x-edge` | 色面抵达纸边 | `fl-bleed-left` · `fl-bleed-right` |
