# 新册

适用：从原文或已有材料制作新册。沿用已有授权；需要补充的决定写在 brief，不增加固定审批轮。

1. 读完整原稿和已有品牌/系列。判断读者、阅读场景、行动、语言、印刷规格及文案模式，使用 [brief](../templates/brief.md) 记必要决定。按需参考 [用途](../purposes/index.md)。
2. 按 [环境与资源](../references/delivery.md) 准备运行时和源字体，用 `family.py init` 建项目，`extract.py` 提取原稿（命令见 [SKILL](../SKILL.md)）。通读 `sources/source.md` 与原文件；扫描 PDF 无文字层须先 OCR，不能把空提取当原文无内容。图片登记与选择见 [images](../references/images.md)。
3. 做 [编辑审阅](../references/editorial-advisor.md)，区分栏目词、序号、主标题、事实与连续正文，确认系列成员与内容去向。按 [adaptation](../references/adaptation.md) 写采用记录，保留原稿基线。
4. 提出一句适合本材料的视觉主张，新项目从 [Folio CSS](../families/folio/README.md) 的统一规则起步，或按已有品牌建立项目 CSS 基因；先看 [原子、布局与组件展示](../dev/folio-css/index.html)。写简短 [页面计划](../templates/page-plan.md)：页面任务、原文 ID/定位、阅读路径、图文关系与整册节奏。不要求不同任务刻意换版式。
5. 直接写关键页与最难页的 HTML/CSS，使用真实内容、实际字体与图片试作；读 [composition](../references/composition.md)、[layouts](../references/layouts.md)。自行看实际输出、修订后扩展全册。没有素材时诚实设计纯文字页，不用占位凑出正式成品。
6. 各语言共用页面结构。默认文案在 HTML，其余按契约放 `copy`；按需写语言 CSS。连续长文用 [续排工具](../references/blocks.md)，审阅写回差异。不要复制一整本作为英文作者源。
7. `validate` → `check` 所有语言，按具体检查报告修作者源。技术报告位于 `.qa/<构建ID>/<语言>/`；失败与硬项未验证不能导出正式版。改文案后必要时重建字体。
8. 执行 [最终 PDF 审稿](visual-review.md)，修订并重建到可交付。`review` 记录实际结论，`verify` / `export` 导出（[交付](../references/delivery.md)）。补 `experience.md`，回复成品、预览、实际限制与非原文元素。
