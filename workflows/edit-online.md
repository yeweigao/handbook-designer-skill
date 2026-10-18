# 在线编辑：把成品发成网页，用户自己改字、换图、批注，再同步回 book.yaml

适用：用户想自己改几个字 / 换几张图，或者多人（老师、家长代表、领导）要看稿提意见。比在聊天里说“第 5 页右下那张卡片”准确得多。
前提：这本书已经 `run.sh` 通过。每种语言一个编辑页。

## 1 · 生成并发布
```bash
python3 $HB/edit_page.py $P/zh          # 多语言：$P/zh、$P/en 各一个；单语：$P → $P/out/edit_zh.html
```
它在成品上标好每段文字对应 book.yaml 的哪个字段（`pages[4].cards[2].x`）、每张照片的原文件名，嵌入字体和图片成单文件，加上编辑工具条。
用 Artifact 工具发布这个 html，**capabilities 一定要带**：
```
{"db": {}, "user": {}, "assets": {}, "comments": {"composer_only": true}, "downloads": true}
```
告诉用户：点「改字」直接在页面上改，离开输入框就保存；改完放不下的页会标红（当场重排、当场检查）；「换图」点照片上传新图；「批注」点任意位置写意见；改完回来说“同步修改”。
页面可以分享给别人一起改（他们要有编辑权限才能改字和换图；只读的人只能看和批注）。

## 2 · 同步回 book.yaml（用户说“同步修改 / 应用修改”）
1. 读修改：ArtifactData `list` 集合 `edits` 和 `images`（这个编辑页的地址），都带 `out_dir: $P/.qa/db` → 存成 `$P/.qa/db/edits/*.json`、`$P/.qa/db/images/*.json`（sync_edits.py 直接读这个目录，`status: synced` 的行自动跳过）。
   用户是用“导出修改”下载的 edits_zh.json 发给你的 → 直接用那个文件。
2. 换图：每行 `asset` 是上传的图片 id。用 Artifact 工具 `read` 这个编辑页、`path` = asset id，存到 `$P/photos/edit_<原文件名去扩展名>_<日期>.jpg`，在那一行的 json 文件里加上 `"local": "<新文件名>"`。
3. 读批注：ArtifactComments 列出这个页面的评论，逐条判断——能直接改的（错字、换词）按 path 改；涉及结构 / 风格的，列给用户确认。
4. 写回：
   ```bash
   python3 $HB/sync_edits.py $P $P/.qa/db              # 或 edits.json 文件；多语言的书传上层项目 $P（只改对应语言那一半）
   ```
   它会核对每处“改之前的值”还对得上（对不上 = 有人先改过，跳过并列出来）、就地替换（保留注释）、把改动记进 `.qa/edits_applied.json`——原文核对把这些当用户认可的改动，不会报 MISSING / EXTRA。
5. `bash $HB/run.sh $P` → GATE PASS 后重新 `edit_page.py`，**发布到同一个文件路径**（同一个网址），用户刷新就是新版。
6. 把同步过的行标成已同步：ArtifactData `batch` 把这些行 `update` 成 `{"status": "synced"}`（或删掉）。
7. 回复：改了几处、跳过几处（为什么）、批注怎么处理的、有没有页面因为改字变挤。

## 限制
- 只有内容版式（8 种）和大多数块的文字能对上字段；对不上的（工具条会显示数量）让用户在聊天里说。
- 加粗 / 斜体标记：改过的那段会变成纯文字（sync 时提示）。
- 改字不能加段落、加卡片、加页——结构性的改动在聊天里说，你改 yaml。
- 美化模式（frozen）的书：用户自己改的字算用户认可的改动；你不要顺手改别处。
