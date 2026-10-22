# 原生手册 Skill 维护

当前作者源为 HTML/CSS/SVG，运行时在 `hb/core/`。本轮范围和交接以 [总计划](audits/HTML-CSS-NATIVE-ITERATION-2026-10-21.md)、[实施步骤](audits/IMPLEMENTATION-STEPS.md) 与 [进度](audits/PROGRESS.md) 为准。历史设计草案只作背景；与现行契约冲突时不作为规则。

## 每条规则一个主人

| 职责 | 权威位置 |
|---|---|
| 目标、授权、路线与入口 | SKILL.md；具体路线 workflows/ |
| 机器可验证作者契约 | references/contract.md + hb/core/validate.py；不另立重复 schema |
| 物理页、字体和语言注入 | hb/core/project.mjs、print-css.mjs、inject.mjs |
| 资源就绪、隔离、构建指纹 | browser.mjs、server.mjs、fingerprint.mjs、render.mjs |
| 只读几何与可读性测量 | measure.mjs、checks/collect.mjs、fontcover.py |
| 显式续排与写回差异 | paginate.mjs、checks/flow.mjs |
| 最终 PDF 检查与验收绑定 | postflight.py、pdfboxes.py、rasterize.py、gate.mjs |
| 原稿、内容/数字及素材覆盖 | extract.py、office_extract.py、coverage.py/mjs |
| 交付、离线与源包重建 | export.mjs、editable_pdf.py、offline_html.py、pack.py |
| Folio 逐项安全写回 | folio.mjs、folio_sync.py；编辑器独立仓库 |
| 家族 CSS 与版本 | families/；项目复制后 design.css 为权威，不自动跟随升级 |
| 语义/构图/最终 PDF 视觉判断 | references/review.md、workflows/visual-review.md；不可伪装机器证明 |
| 项目修订与经验 | 项目 experience.md；格式 templates/experience.md |

文档引用权威，不复制检查阈值或创造另一套布局语言。共享层只存低层原语，作品整页结构留在项目。

## 修改与验证

1. 先检查工作区，保护已有改动，按接手规则认领一个步骤。契约变更同步文档、校验器与实际行为，保留正反例。新运行时代码放 core，Python 保持 3.10 语法兼容，不加前端框架。
2. 改动优先最小相关检查，集成后跑公开入口。检查不变量须有合法例和违规例，输出区分 pass/fail/unverified；缺依赖不得静默跳过并写成功。
3. `bash dev/tests/selftest.sh --quick` 做静态预算/链接/归档边界/语法与契约正反例；不启动浏览器，不代表成品验收。`bash dev/tests/selftest.sh` 再跑全部新链路测试和两本真实样册的 check/verify。日志、隔离样册与报告留在输出的临时目录；未运行项明示，正式交付的硬项未知仍阻止。
4. 复用已有依赖与资源，按需准备，避免默认下载整套工具。当前依赖和显式使用现有浏览器的方法见 [delivery](../references/delivery.md)。新依赖须锁版本并说明原因。参考环境 Node 22/Python 3.10 与实际环境不同时如实记录，不宣称等同复现。
5. 基因/字体/图像/分页变化须看实际 PDF 的受影响页及全册节奏；技术回归不替代视觉审稿。正式生成基准与人工校准留 S12，S10 selftest 不能代替成绩。

## 运行包与开发证据

运行包包括 SKILL、workflows、references、Markdown 项目模板/用途指南、品牌资源、families、hb/core 和 hb 的依赖清单；实际使用的字体与许可放项目 assets。开发字体、fixtures、样册、历史审计与归档不属于必装运行依赖。纯运行包没有 dev 字库时用 HB_FONT_DIR 提供源字体，已有项目可直接使用自带静态字体。

旧引擎、模板、用途配置、品牌配置和专用测试冻结在 [dev/archive/yaml-engine](archive/yaml-engine/README.md)，版本与能力映射见该目录。旧样册、gallery 与 previews 保留历史输入/输出，不承诺原地重建，也不作为当前推荐家族清单。S11 再审视觉参考的保留与取舍。

## 经验边界与依赖后续

修订把材料条件、失败页、修改原因与证据写 experience；两次出现只成为候选，未经未见材料验证不自动更新 Skill 或家族。经验晋升/撤回闭环另验收。

用户在 S10 明确质疑整套依赖的安装成本。后续应评估轻量默认路径、按功能加载提取/PDF 工具、将精确浏览器环境用于确定性基准；涉及 S2–S4 的运行时与验收契约，S10 不悄悄改变。现有明确 HB_CHROMIUM 选项可复用已装浏览器，必须记录实际环境与重新验收。
