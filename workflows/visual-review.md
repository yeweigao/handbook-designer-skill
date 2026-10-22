# 最终 PDF 审改

所有路线收尾执行。先运行 `check` 生成最终 PDF、技术报告及栅格。**审的是 `.build/<构建ID>/<语言>/book.pdf`**，浏览器截图只用于调试。

1. 确认当前输入/构建及各语言 PDF。打开 `.qa/<构建ID>/<语言>/raster/sheet.png` 看整册；`spreads.png` 看实际面对页；逐页看 `page-NNN.png`，密集信息、细字、照片主体和中缝必要时放大。每种语言全部页都覆盖。
2. 按 [review](../references/review.md) 判断阅读任务、排印、照片与最弱页。先看 brief 和 PDF，之后再核设计意图；若是作者自评，照实标注，不称独立评测。需要独立 reviewer 时使用获授权的工具/人员，工具不可用就记录未做独立审阅。
3. 写 `.qa/<构建ID>/visual-review.md`：执行者与方式、PDF 哈希、看过的语言/页/面对页、具体问题、改动和复核证据。没看过的页标 unverified，不用平均分盖住失败页。格式见 [审稿模板](../templates/visual-review.md)。
4. 必改项落实到作者源，按反馈影响复核同类页、续页与系列；重跑 check 后审新 PDF。复制旧报告可保留为历史问题清单，结论必须绑定新构建和新 PDF。
5. 所有必改项关闭且所有语言技术验收有效后，再记录实际结论：

```bash
node "$HB/core/cli.mjs" review "$P" --verdict deliverable --by "执行者与审阅方式" --notes <当前审稿记录.md>
node "$HB/core/cli.mjs" verify "$P"
node "$HB/core/cli.mjs" export "$P" --name <文件名>
```

`review` 只保存声明，不会替人看图。若结论不合格写 `--verdict fail`；受素材/工具限制时说明卡点，最多提供 `export --draft` 草稿。可交付与优秀的尺度分开，作者日常修订不限固定轮数；独立基准的返工预算另按评测计划执行。

每次修订把原因和实测记录在项目 `experience.md`，不要未经迁移验证改变全局默认规则。
