# 维护规矩：改 skill 本身的时候

给改这个 skill 的人（包括以后的你）。目的：skill 越长越难用——规则散在几处会互相打架，常驻文档太长会被跳着读。

## 每条规则只有一个主人
| 规则 | 主人（只在这里写全） | 其他地方 |
|---|---|---|
| 选哪条路线 | SKILL.md §1 | workflows 里只写“适用于” |
| 纪律（原文搬运、先确认、门禁…） | SKILL.md §2 | workflows 引用，不重复解释 |
| 某条路线的步骤 | workflows/<路线>.md | SKILL.md 只放一行指路 |
| 版式写法、空位、限制 | references/layouts.md（内容版式）、references/blocks.md（照片版式、内容块） | — |
| 网格、字号档、行宽、放不下时的让位顺序 | 引擎：canon.py（网格常数）、flow.py（块 → 字号档、吸到整行）、fill.js canon()（让位顺序）；文字说明在 layouts.md §0 | 其他文档写“见 layouts.md §0” |
| 皮肤、字体、配色、颜色角色与用色档位、品牌包结构 | references/style.md（§8 颜色角色）、palettes.py（角色映射、档位判断）、brands/allas/brand.yaml（结构样例） | — |
| 用途方法的页面角色、审稿重点 | purposes/<kind>.yaml | review.md 只引用 |
| 审稿标准 | references/review.md | — |
| 交付物、印刷、画布、多语言 | references/delivery.md | — |
| 检查的阈值和提示文字 | 对应脚本（doctor.py、lint.py、facts.py…）里，提示里直接写改法 | 文档只说“看提示” |
同一件事要在第二个地方出现时，写一句“见 X”，不要复制。

## 常驻文档有预算
- SKILL.md ≤ 12000 字符（selftest 查）：只放路线表、纪律、命令速查、交付清单、文件地图。
- 步骤、表格、例子放 workflows/ 和 references/，用到时才读。
- 加一条规则前先问：它能不能变成脚本里的检查？能 → 写进脚本（提示里带改法），文档里不写。

## 改完必须跑
```bash
bash hb/selftest.sh          # 编译、yaml、文档引用、SKILL.md 预算、所有模板中英构建 GATE PASS、品牌包、A5 / 小红书画布
```
- 改了版式 / 配色 / 网格：重新生成 `references/gallery/` 里受影响的效果图和 templates 的预览图，亲眼看。
- 改了检查（doctor / lint / fill.js 的 cnCheck）：先用一个会触发它的例子确认它报得出来，再确认所有模板仍然 PASS。
- Python 保持 3.10 能跑：f-string 里不要嵌套同种引号；不用 3.11+ 才有的语法。
- 引擎代码不写死页面尺寸：用 canon 的 W / H / COL / LAST 和 `L()`、`K`（画布换成 A5 / 小红书也能排）。
- **一个引擎**：照片版式（flow.py）和内容版式（canon.py）用同一套网格原语（`stack` / `region` / `box` / `field` / `pic`），块统一由 `flow.B()` 渲染。不要为某个风格另写一套块的排法——风格只改字体、颜色、插画、页边装饰（styles.py / art.py / stijl.py / geo.py）。
- 新的 px 参数一律吸到整行（`flow.lines` / `nrows`）、整栏（`ncols`）或字号档（`dsize`）；会挤占空间的东西给它一个让位的标记（图 `data-fh`/`data-fmin`、间距 `data-g`、书写线 `data-x`），fill.js 会按顺序收。

## 新增东西放哪
- 新路线 → workflows/<名字>.md + SKILL.md 路线表一行
- 新用途 → purposes/<名字>.yaml + purposes/index.yaml 一行（selftest 查 order 里的角色都有定义）
- 新品牌 → `bash hb/new_brand.sh`（自动登记 brands/index.yaml）
- 新版式 → 内容版式：canon.py 一个函数 + RECIPES + layouts.md 一节 + book.layouts.yaml 里用一次 + 效果图；照片版式：flow.py 一个函数 + LAYOUTS + blocks.md 表里一行
- 新检查 → 脚本 + doctor 的提示（带改法）+ 一个能触发它的测试
