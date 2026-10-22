# 维护规矩：改 skill 本身的时候

给改这个 skill 的人（包括以后的你）。本文件与 `dev/tests/`、`dev/gallery/`、`dev/previews/`、`dev/audits/` 均存放在 `dev/` 开发目录下，与纯 Skill 运行时文件分离。

> **2026-10-21 交接：** HTML/CSS 原生改造的目标、边界和验收统一见 [完整迭代计划](audits/HTML-CSS-NATIVE-ITERATION-2026-10-21.md)。该改造尚未实施；下文描述现有引擎。实施本轮时按新计划同步更新规则归属、测试与文档，不以旧 YAML/固定版式约定阻止已授权的架构替换。

## 每条规则只有一个主人
| 规则 | 主人（只在这里写全） | 其他地方 |
|---|---|---|
| 选哪条路线 | SKILL.md §1 | workflows 里只写“适用于” |
| 纪律（原文搬运、先确认、门禁…） | SKILL.md §2 | workflows 引用，不重复解释 |
| 某条路线的步骤 | workflows/<路线>.md | SKILL.md 只放一行指路 |
| 版式写法、空位、限制 | references/layouts.md（内容版式）、references/blocks.md（照片版式、内容块） | — |
| Grid / Layout / Theme / Brand / Project 分工、编辑变奏与阅读节奏 | references/composition.md | 路线文档只引用 |
| 网格、字号档、行宽、放不下时的让位顺序 | 引擎：hb/canon.py（网格常数）、hb/flow.py（块 → 字号档、吸到整行）、hb/fill.js canon()（让位顺序）；文字说明在 references/layouts.md §0 | 其他文档写“见 layouts.md §0” |
| 皮肤、字体、配色、颜色角色与用色档位、品牌包结构 | references/style.md（§8 颜色角色）、hb/palettes.py（角色映射、档位判断）、brands/acme/brand.yaml（结构样例） | — |
| 用途方法的页面角色、审稿重点 | purposes/<kind>.yaml | references/review.md 只引用 |
| 审稿标准 | references/review.md | — |
| 后置视觉总监的逐页审改闭环 | workflows/visual-review.md | 各路线只链接，review.md保留统一标准 |
| 交付物、印刷、画布、多语言 | references/delivery.md | — |
| 检查的阈值和提示文字 | 对应脚本（hb/doctor.py、hb/lint.py、hb/facts.py…）里，提示里直接写改法 | 文档只说“看提示” |
同一件事要在第二个地方出现时，写一句“见 X”，不要复制。

## 纯 Skill 运行文件 vs `dev/` 开发资源
- **纯 Skill 运行时目录**：`SKILL.md`、`workflows/`、`references/`、`templates/`（仅 `.yaml` 与 `brief.md`）、`purposes/`、`brands/`（仅 `index.yaml` 与虚构示例 `acme`）、`hb/`（仅排版与门禁运行脚本）。
- **`dev/` 开发与预览资源**（打包分发纯 Skill 时可排除）：
  - `dev/maintenance.md`：本维护规矩
  - `dev/tests/`：`selftest.sh`、`make_test_photos.py`、`test_adapt.py`、`test_brand_graphic.py`、`test_photo_layout.py`、`test_editorial_layout.py`、`test_editorial_content.py`、`test_reading_layout.py`、`test_swiss_type.py`、`test_image_bleed.py`
  - `dev/gallery/`：各风格与版式控制效果图
  - `dev/previews/`：模板的拼版预览图（使用合成插画及原创示意图生成）
  - `dev/sample_photos/`：无版权 CC0 模板样张配图
  - `dev/fonts/`：离线回归测试用的开源西文字体包（运行时通过 `hb/fonts.py` 按需下载，纯 Skill 包无需附带）
  - `dev/audits/`：历史复盘、审计报告与迭代计划（`TODO.md`、`ROADMAP.md`、`AUDIT-*.md`）；**`IDEAL-FORM.md` 是这个 skill 的理想形态（参照系）——每次改 skill 前先对照它，问一句「这次改动是更接近还是更远」**

## 从实测反馈迭代

先区分项目偏好、设计决策、流程漏项和引擎缺陷。项目选定的配色、字号、照片出血或暗纹浓度留在brief/方案，不直接变成所有风格默认；已存在但未执行的规则先修入口与交接，不再叠一条同义规则。能确定检查的不变量进入共用引擎，并保留“旧版放行、修后拒绝”的反例；语义和视觉判断保留人工验收，不把GATE PASS当成设计合格。

复测既走完整书册，也走受影响的普通入口（方向样张、--proof、导出、源包重建等），不只调用底层函数。区分本项目验证、控制回归、全风格真实照片与独立执行评测；只关闭已有对应证据的范围。新发现先记 `dev/audits/TODO.md`，当前待办与验收收敛到 `dev/audits/ROADMAP.md`。

## 常驻文档有预算
- SKILL.md ≤ 12000 字符（selftest 查）：只放路线表、纪律、命令速查、交付清单、文件地图。
- 步骤、表格、例子放 workflows/ 和 references/，用到时才读。
- 加一条规则前先问：它能不能变成脚本里的检查？能 → 写进脚本（提示里带改法），文档里不写。

## 改完必须跑
```bash
bash dev/tests/selftest.sh          # 编译、yaml、文档引用、SKILL.md 预算、所有模板中英构建 GATE PASS、品牌包、A5 / 小红书画布
```
- 改了版式 / 配色 / 网格：重新生成 `dev/gallery/` 里受影响的效果图和 `dev/previews/` 的预览图，亲眼看。
- 改了检查（doctor / lint / fill.js 的 cnCheck）：先用一个会触发它的例子确认它报得出来，再确认所有模板仍然 PASS。
- Python 保持 3.10 能跑：f-string 里不要嵌套同种引号；不用 3.11+ 才有的语法。
- 引擎代码不写死页面尺寸：用 canon 的 W / H / COL / LAST 和 `L()`、`K`（画布换成 A5 / 小红书也能排）。
- **一个引擎**：照片版式（flow.py）和内容版式（canon.py）用同一套网格原语（`stack` / `region` / `box` / `field` / `pic`），块统一由 `flow.B()` 渲染。不要为某个风格另写一套块的排法——风格只改字体、颜色、插画、页边装饰（styles.py / art.py / stijl.py）。
- 新的 px 参数一律吸到整行（`flow.lines` / `nrows`）、整栏（`ncols`）或字号档（`dsize`）；会挤占空间的东西给它一个让位的标记（图 `data-fh`/`data-fmin`、间距 `data-g`、书写线 `data-x`），fill.js 会按顺序收。

## 新增东西放哪
- 新路线 → workflows/<名字>.md + SKILL.md 路线表一行
- 新用途 → purposes/<名字>.yaml + purposes/index.yaml 一行（selftest 查 order 里的角色都有定义）
- 新品牌 → `bash hb/new_brand.sh`（自动登记 brands/index.yaml）
- 新版式 → 内容版式：canon.py 组合共用网格原语 + RECIPES + layouts.md 一节 + 模板用例 + 效果图；基础版式用 book.layouts.yaml，编辑变奏用 book.editorial.zh.yaml，连续阅读用 book.reading.yaml。照片版式：flow.py 一个函数 + LAYOUTS + blocks.md 表里一行
- 新检查 → 脚本 + doctor 的提示（带改法）+ `dev/tests/` 下一个能触发它的测试
