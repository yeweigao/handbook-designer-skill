# YAML 引擎 · 已退役

冻结日期 2026-10-22，源码基线见 VERSION.json：html-native 分支 S10 前提交 bb57494。这里保留旧引擎、原 SKILL/工作流/参考、模板、用途配置、示例品牌和专用测试，供审计与缺陷追溯。文件内容按迁移前保留。

**不是可执行安装包或兼容入口。** 旧相对路径、字体缓存、运行清单和历史输出不保证在此直接可运行；需要重现旧缺陷请从 VERSION.json 的 source_commit 建独立 checkout，并使用当时依赖。当前公开入口只有 hb/core/cli.mjs。

原 dev/gallery、dev/previews 与旧 dev/samples 已移出仓库（本地保留），不进版本库；不把它们当当前运行模板。hb/package*.json 与 requirements* 仍是新运行时沿用的依赖来源；不为归档再维护一套可运行副本。

## 有价值回归的现行归属

| 原能力/历史专用测试 | 新契约回归（dev/tests/core/） |
|---|---|
| 原文适配、冻结、用户编辑（test_adapt、test_editorial_content） | coverage.test.mjs：提取稳定 ID、隐藏/透明/页外、MISSING/ORDER/EXTRA、adapt、数字和授权；folio.test.mjs：写回与冲突 |
| 图片边界/出血/正文（test_photo_layout、test_image_bleed） | render.test.mjs：物理尺寸/媒体与成品框；measure.test.mjs：溢出、裁切、DPI、合法出血及叠放；gate.test.mjs：最终 PDF |
| 字体、排印和低层几何（test_swiss_type、test_editorial_layout） | test_validate.py + render/measure：静态字重、实际字体回退、字号/对比度、溢出、合法布局；家族实际输出看原生样册 |
| 连续阅读与双语（test_reading_layout） | paginate.test.mjs：24+ 页中英、片段、孤行和重复确定性；coverage：片段进 PDF |
| 品牌图形（test_brand_graphic） | 原生 SVG/CSS 由 validate/render/measure 检查引用、页面几何和局部叠放；源形与内容关系仍作视觉审稿，旧枚举图形配方不迁移 |
| 导出、离线、字体扩充与源包 | export.test.mjs：离线资源与输出一致、字体/文字层、解包重建、拒绝失效验收；编辑器实际改字仍 unverified |
| 旧布局枚举/四主题/自动吸附缩字断言 | 归档，不兼容；原生任意构图不要求重现其像素或类名 |

上表是责任映射，实际本轮运行结果见 PROGRESS.md；不能将归档或映射本身写成测试通过。
