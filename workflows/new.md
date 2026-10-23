# 新册

适用：从原文或已有材料制作新册。沿用已有授权；需要补充的决定写在 brief，不增加固定审批轮。

1. 读完整原稿和已有品牌/系列。判断读者、阅读场景、行动、语言、印刷规格及文案模式，使用 [brief](../templates/brief.md) 记必要决定。按需参考 [用途](../purposes/index.md)。

2. 按 [环境与资源](../references/delivery.md) 准备运行时和源字体（`python3 "$HB/core/fonts.py" status` 看缺什么，`install` 补齐可再分发的开源字面），用 `family.py init` 建项目，`extract.py` 提取原稿（命令见 [SKILL](../SKILL.md)）。通读 `sources/source.md` 与原文件；扫描 PDF 无文字层须先 OCR，不能把空提取当原文无内容。图片登记与选择见 [images](../references/images.md)。

3. 做 [编辑审阅](../references/editorial-advisor.md)，区分栏目词、序号、主标题、事实与连续正文，确认系列成员与内容去向。按 [adaptation](../references/adaptation.md) 写采用记录，保留原稿基线。

4. 提出一句适合本材料的视觉主张，并从系统里取骨架：新项目从 [Folio CSS](../families/folio/README.md) 的 [瑞士主义底座](../references/swiss.md) 起步，或按已有品牌建立项目 CSS 基因。先看 [原子、布局与组件展示](../dev/folio-css/index.html)，再按材料写简短 [页面计划](../templates/page-plan.md)：页面任务、原文 ID/定位、阅读路径、图文关系与整册节奏。不要求不同任务刻意换版式。

   同时写清两个 CSS 的分工，这一步比任何视觉决定都重要：

   - `design.css` 是本项目冻结的**家族基因**：字阶、间距、行距、基线、网格、组件。只读，不手改；升级要主动审阅并重出验收。
   - `book.css` 只做两件事：本册特有的页面几何（分栏、出血、叠放）与**克制的**品牌适配（颜色角色）。
   - **非必要不新增**：能用原子/布局/组件拼出来的不新写类；新增的每个类要能说明它服务哪条阅读任务；不得重定义字阶、间距、行距、基线（`validate` 的 `style.token / style.offladder` 会拦）。需要新组件时，先写进 `design.css` 的源模块并过展示页回归，再回书里用。

5. **风格锁定：三页小样，最多三轮。** 从全册挑三页试作——开场、正文密集页、最难页——用真实内容、真实字体与真实图片落版，看实际 PDF 而不是想象。每轮只改决定（字阶、网格、图文比例、颜色角色），不加装饰救场。用户确认或无人值守时自评后，把结论写进 [风格锁定](../templates/style-lock.md)：用了哪些原子与布局、字号档位、颜色角色、图片处理，以及明确**不做**什么。

   **小样没定下来不要铺全册。** 100 页做完才发现走样，返工的是整本；三页返工改的是判断。判断依据见 [swiss](../references/swiss.md) 与 [审稿尺度](../references/review.md)；`validate` 对 ≥12 页且没有 `style-lock.md` 的册子给提示。

6. 铺全册：用真实内容写各页 HTML/CSS，按 [composition](../references/composition.md)、[layouts](../references/layouts.md) 组合；自行看实际输出、修订。没有素材时诚实设计纯文字页，不用占位凑出正式成品。

7. 各语言共用页面结构。默认文案在 HTML，其余按契约放 `copy`；按需写语言 CSS。连续长文用 [续排工具](../references/blocks.md)，审阅写回差异。不要复制一整本作为英文作者源。

8. `validate` → `check` 所有语言，按具体检查报告修作者源。技术报告位于 `.qa/<构建ID>/<语言>/`；失败与硬项未验证不能导出正式版。改文案后必要时重建字体。

9. 执行 [最终 PDF 审稿](visual-review.md)，修订并重建到可交付。`review` 记录实际结论，`verify` / `export` 导出（[交付](../references/delivery.md)）。补 `experience.md`，回复成品、预览、实际限制与非原文元素。
