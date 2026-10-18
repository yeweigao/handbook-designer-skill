# 路线 revise：改版、出错后续跑

## 改版的规矩
- 改版纪律见 SKILL.md §2「改版不丢已认可的东西」：每轮新建 `_v2`/`_v3`、`check_copy.py` 对照旧版、已认可的页不顺手大改。
- 先看 `brief.md`：用户这次说的是不是推翻了当时确认的东西（风格、配色、页数、用途）？是 → 确认后改 brief.md 并记一笔；否 → 只改 book.yaml。
- 已经认可的页不顺手大改（`references/review.md`「不要动」）。
- 用户指出文案和版面不合适时，按 `references/editorial-advisor.md` 审完整输入及同系列，再走 `references/adaptation.md` 的适配检查；不能只改被截图的页。
- 先更新page-plan.md中的页面文案分工和设计方案，再修改book.yaml；同类问题一起检查栏目字、序号、主标题和时间地点的角色。

## 常见反馈 → 改 book.yaml 的哪里
| 用户说 | 改法 |
|---|---|
| 不够大气 / 太平 | 每 3–4 页插一页 FULL；有横图时章节开头换 SPREAD_P / SPREAD_OPENER |
| 这一页太空 / [留白] | 加 `image`；和相邻页合并；换图多的版式（MIX / STAGGER / COLLAGE） |
| 这一页太挤 / [溢出] | 拆成两页，用同一个版式（自动镜像）；条目多的换 GRID；去掉 intro / stats |
| 太像模板 / 每页都一样 | 相邻页换不同版式；CARDS 换 STAGGER 或 TWO；加 COLLAGE、FULL 打断节奏（看 lint 的节奏条） |
| 颜色单调 / 撞色不够 | 指定某页 `surface: A` / `B`；配色换另一组经典撞色（klein / hermes / china-red / lemon-violet） |
| 色块太多 / 想素一点 | 几页写 `surface: paper`；换对比弱一点的配色（style.md §3）；FULL 写 `deco: false` |
| 照片颜色不搭 / 发灰 | `book.duotone: all`；单张 `{src: a.jpg, duo: true}`；不要就 `duo: false` |
| 照片到了 | 放进 photos/，把占位换成文件名，重跑（images.yaml 自动更新） |
| 图片糊 / [低清] | 换原图；或从 FULL / 跨页挪到小图位 |
| 换个风格 | 改 `book.style`（只改这一行）+ brief.md 记一笔；拿不准就先出 directions.py 样张 |
| 想换字体 | 按 style.md §2.2 改 `book.fonts`（只写要覆盖的角色），整册字体分工记进 page-plan.md；brief.md 的 fonts 行同步 |
| 用我们的品牌 | `book.brand: <名字>`（brands/index.yaml）；没有品牌包 → `workflows/brand.md` |
| 字看不清（照片上） | 改 focus / target，让字落在照片较暗、较简单的区域；换更简洁的图；换让字落在纸面上的版式（T/B 调 split、HOLE 换窗的位置） |
| `[书写线收紧]` / `[字号收紧]` | 这一页内容偏多，引擎已经收了书写线或辅助字号；要原样的书写空间和字号就拆页（同一版式，自动镜像） |
| 图被缩小了 | 页面放不下时插图会先按整行缩矮；想保留原高就把一部分文字挪到相邻页 |
| 内容怎么变了 | 看 check_copy 的 MISSING / EXTRA；从 doc.md 重新复制；对照旧版恢复 |
| 不要填写的地方 | `book.purpose: brochure`，删掉书写块 |
| 要英文版 / 双语 | 文字写成 `{zh: …, en: …}` + `book.langs: [zh, en]`（layouts.md §2）；单语 yaml 用 `hb/i18n.py extract/apply` |
| 要小一点的册子 / 发小红书 | `book.canvas: a5` / `xhs`（delivery.md「画布」）：内容要按小画布重新分页 |
| 我想自己改几个字 | 在线编辑页（`workflows/edit-online.md`） |

## 出错了从哪里接着做（看 `.qa/log.md` 最后几行）
| 卡在哪 | 现象 | 从这里接着做 |
|---|---|---|
| new_project | 原文转换为空 / 抽不出图 | 装 markitdown 或 pandoc（check_env.sh），或请用户另存为 .docx / .md；图另给 |
| lock | `[决策不一致]` | 不是 bug：把 book.yaml 改回 brief.md 的设置，或问用户后改 brief.md |
| hb.py | `ERROR: …` | 按提示改 yaml（未知版式、缺图、跨页奇偶、YAML 引号）；不用重跑盘点 |
| shot / dark | 截图超时、找不到 playwright | `bash hb/check_env.sh`；字体没下载 → `python3 hb/fonts.py fetch` |
| doctor | GATE FAIL | 按提示改 yaml，只重跑 run.sh |
| 多语言 | 某种语言 FAIL | 只改那种语言的文字；`HB_SUB=1 bash hb/run.sh $P/en` 单独跑那一种 |
| export | 导出门禁不过 | 先 run.sh 到 PASS；赶时间先 `--draft` |
| export | Type 3 字体 / PDF 太大 | `fonts.py fetch`；`book.scale: 2` |
| 在线编辑同步 | `跳过 …（有人先改过）` | 打开 book.yaml 看那个字段现在的值，和用户确认用哪个 |

每次 run.sh / export.sh 都会在 `.qa/log.md` 记一行（时间、步骤、结果）。会话断了、换人接手：先读 brief.md（定了什么）→ log.md（做到哪）→ 最后一次的 doctor 输出（还差什么）。
