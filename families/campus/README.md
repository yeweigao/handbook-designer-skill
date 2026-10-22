# Campus · 学院墨蓝（家族 v1.1）

适合：学校、营地与研学、招生、机构画册、指南。照片书与纯文字书都可以。

## 关键决定

- **颜色**：墨蓝 `--primary` 负责标题、强调块与深色页；暖纸 `--paper` 是默认阅读面；赭 `--ochre` 只做眉标与次要强调；金 `--gold` 只在深色底上出现（在纸上对比度不够，不作文字色）。
- **字体**：中文标题思源宋体（Noto Serif SC 700），正文思源黑体（Noto Sans SC 400/700），西文与数字 Inter（400/600）。英文版正文切换为 Inter。
- **字号**：正文 16/28px，导语 19/32px；辅助 11px、关键信息 13px，都高于可读性下限。层级靠宋体/黑体对比与尺寸跳跃，不靠颜色。
- **网格**：六栏、6mm 栏距、28px 基线；版心内外侧左右页对称（偶数页是左页）。构图用 `.area` 加跨栏类（`.c1-4`、`.c5-6`…），也可以写本书专属的 Grid/Flex/定位。
- **断行**：标题类原语 `text-wrap: balance` + `word-break: keep-all`（中文只在标点与空格处断行，避免拆词）；正文 `text-wrap: pretty`。没有标点的超长中文标题需手动 `<br>` 或调字号，否则测量会报溢出。
- **线**：2px 墨蓝主线 + 1px 发丝线；旁注用顶线挂靠。

## 原语

`.area`（版心六栏）· `.kicker` 眉标 · `.display / .h1 / .h2 / .h3` · `.lead` 导语 · `.body` 段间距 · `.aux / .key` · `.num / .index-num` 大数字 · `.rule / .hair` · `.quote` 引文 · `.note` 旁注 · `.frame` 图框 · `.caption` · `.fill-lines` 书写线 · `.checklist` · `.step` · `.on-dark` 深色面 · `.scrim-bottom` 照片压暗 · `.folio / .running`。

内容角色仍按契约写 `data-role`（`display / body / key / aux / deco`），原语只管样子。

## 不能照搬

- 金色不作纸上文字色；深色页上的长段正文不超过两段。
- 照片上压字必须有压暗（`.scrim-bottom`）或选择天空/暗部区域，并通过对比度测量。
- 示例书见 `dev/samples/native/`。

## 版本

- v1：首版。
- v1.1：英文等非中文版加 `font-variant-east-asian: proportional-width`，修正宋体/黑体标题里 ’ “ ” 显示为全角宽度的问题；自动断词的连字符改用 U+002D（思源字体的 U+2010 是全角宽度）。v1 项目（纯中文）不受影响，无需升级。
