# Folio 本地编辑与写回

Folio 是独立的浏览器编辑器，文件在浏览器内读写。Skill 管作者源、最终 PDF 和验收；Folio 的下载打印若要成为正式交付，须回 Skill 重建。

```bash
node "$HB/core/cli.mjs" folio-pack "$P"
# 在 Folio 导入 out/folio/*.folio.html，改字/换图/调整样式，下载 HTML
node "$HB/core/cli.mjs" folio-sync "$P" <下载的HTML> --dry-run
node "$HB/core/cli.mjs" folio-sync "$P" <下载的HTML>
node "$HB/core/cli.mjs" check "$P"
```

使用与本契约联动的 Folio 版本；导入时确认编辑器保留构建标记与稳定 ID，不以历史分支名推断线上兼容性。没有兼容编辑器时仍可交付正式 PDF、离线 HTML 与源包，不能声称在线写回已验证。

编辑包是按语言生成的单文件 HTML，保留页面、内容、编辑 ID 和构建标记；基准存于 `.build/<构建ID>/<语言>/folio-base.html`，写回前不要删基准。

- 默认语言文字按片段写回 `book.html`，其他语言合并片段写回 `copy/<语言>.json`。行内强调、链接与换行按白名单清洗。
- 新图片落到 `assets/images/` 并登记在 `sources/assets.json`；授权留空，核实后才可交付。
- 位移与样式写入 `edits.css`，逐项审阅。没有稳定 ID、无法定位或不支持的改动列入未写回，不猜。其他语言的续页重新分页会改变片段，建议这类页面只改字。
- 基准、下载 HTML、当前源做三方比对；当前旧值不符时报告冲突，不覆盖。看 `.qa/folio-sync/` 报告处理；有冲突/未写回时即使部分修改已写入，也不能声称全部成功。
- 用户本人改字记入 `sources/user-edits.json`，原文覆盖承认它；agent 不可用此记录放行自己的改写。下载 HTML 不覆盖整本作者源。

写回后旧验收失效：审阅改动与授权 → check 所有语言 → [visual-review](visual-review.md) → review / export，需要继续编辑再出新包。
