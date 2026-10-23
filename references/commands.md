# 制作命令

`HB` 指向本 Skill 的 `hb`，`P` 是独立项目目录。新环境先读 [环境与交付](delivery.md)；已就位的依赖不重复安装。初始化只给单页骨架，不代替内容设计。

```bash
HB=<skill目录>/hb
P=<工作目录>/<项目名>
# 首次准备，已有环境跳过
bash "$HB/core/setup_env.sh"
python3 "$HB/core/fonts.py" status
# 缺源字体时：python3 "$HB/core/fonts.py" install
python3 "$HB/core/family.py" init folio "$P" --title "书名" --langs zh-CN,en --mode translate
python3 "$HB/core/extract.py" <原稿.docx> "$P"
```

创作编辑 `book.html`，按需改 `book.css / copy / lang`。初始化已有项目不会迁移家族；改版沿用其 `project.json.styles[0]`，不再次初始化。

```bash
python3 "$HB/core/family.py" fonts "$P"       # 文案超出字库时显式重建
python3 "$HB/core/validate.py" "$P"
node "$HB/core/cli.mjs" paginate "$P"         # 仅使用 data-flow 时；审阅写回差异
node "$HB/core/cli.mjs" check "$P"            # 全部语言、最终 PDF 与技术检查
node "$HB/core/cli.mjs" verify "$P"
# 实际审阅当前最终 PDF，不能跳过实看而预填结论
node "$HB/core/cli.mjs" review "$P" --verdict deliverable --by "审稿人" --notes <审稿记录.md>
node "$HB/core/cli.mjs" export "$P" --name <文件名>
```

`render` 仅生成快照与 PDF；`measure` 只读测量。`check --lang` 可定位单语言问题，正式交付须覆盖所有语言。`export --draft` 输出带水印草稿。审稿方法见 [visual-review](../workflows/visual-review.md)，检查证据格式见 [contract](contract.md)。
