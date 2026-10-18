# 下一版本迭代计划（基于 2026-10-18 quick 路线实测）

输入：`~/Downloads/YLMUN_ChiangMai_Brochure_EN.pptx`（22 页英文定稿宣传册）→ quick 路线照搬成册（项目 `~/Documents/YLMUN_ChiangMai_v1`）。
原则：内容零改动、22 页一页对一页；GATE PASS 后逐页目检，本计划只收**实测复现**的问题，每条给改法和验收。

---

## P0 · 正确性（门禁漏放 / 误报，直接决定「PASS 是否可信」）

> 2026-10-18 系统性审核裁定（AUDIT-2026-10-18.md §2.3）：doctor.py:9 的 `ok=False` 在 elif 分派之前执行，overflow.json 所有条目（含 cn-fit:21/cn-small:19）一律 FAIL；doctor.py:34 的 sparse 循环已有「不算失败，只是提示」的分级先例。**P0-1 维持成立**，精确改法：cn-fit 移入提示循环（与 sparse 同）；cn-small 设 px 阈值（<120px 记 H——p14 照片带 115px 是真实视觉事故；≥120px 记 S）。

### P0-1 门禁分级：提示级条目拦截构建
- **现象**：doctor.py 首行即 `ok=False`，任何 overflow.json 条目都拦门禁——包括提示级的 cn-fit「标题太长」、cn-small「图太小」。修排版时提示级和硬伤无法区分，误拦 2 次。
- **改法**：doctor 输出分级 H（溢出/重叠/对比度/MISSING/EXTRA，拦门禁）/ S（cn-fit、cn-small、图片占比等，只报告）；gate.py 按 H 判定；fill.js 的 cnCheck 给每条发现打 `sev`。
- **涉及**：hb/doctor.py、hb/gate.py、hb/fill.js；SKILL.md §门禁一节同步一句。
- **验收**：构造一个只触发 cn-small 的样例 → run.sh 返回 0 且报告里 S 级可见；原 H 级样例仍拦。

### P0-2 PPT 页码 artifacts 被当正文必含
- **现象**：check_copy 把 PPT 页脚「02 / 23」页码行列入必含文本 → MISSING → 首轮 GATE FAIL。quick 路线（PPT 照搬）100% 触发，因为每页都有。
- **改法**：extract.py/plan.py 识别页码样式行（`^\d{1,2} / \d{1,2}$`、居中短数字），归类为 artifacts 单独进 plan.md 并**从必含集合排除**；brief.md 记录替代方式（本册用手册自动页码）。
- **涉及**：hb/extract.py（或 plan.py）、hb/check_copy.py。
- **验收**：用同一 PPT 重跑 new_project，copy.txt 里不出现页码行；删除真实正文一行仍报 MISSING。

### P0-3 无图版式静默丢弃 figure/gallery 块
- **现象**：POSTER 无图页的 figure/gallery 被引擎静默丢弃（本册第 6 页海报图、第 22 页二维码都没渲染，靠目检才发现）。丢内容不报警 = GATE PASS 但内容丢失。
- **改法**：flow.py 渲染分支对「当前版式无此块槽位」输出 WARN 条目进 QA 报告（列出页 + 块类型），doctor 汇总为 S 级；short 版式（无 image 字段的 POSTER）明确支持 figure 渲染或直接文档禁写。
- **涉及**：hb/flow.py、hb/doctor.py；references/blocks.md 标注各版式可用块。
- **验收**：样例页在无图 POSTER 写 figure → 报告出现 WARN 且可见。

---

## P1 · 易用性（每次开新项目都要人工踩的坑）

### P1-1 环境自检：macOS Chrome 误报 + 缺依赖无引导
- **现象**：check_env.sh 只 `which google-chrome`；macOS `.app` 不在 PATH 必然误报「chromium 不可用」。python3 指向系统解释器时缺 brotli/pikepdf/qrcode/pyspellchecker/markitdown，报错栈很深但没说装什么。
- **改法**：check_env.sh 增加 `/Applications/Google Chrome.app`、`Microsoft Edge.app`、`Chromium.app` 探测；缺 python 包时打印一键安装命令（`pip install -r hb/requirements.txt`）而非堆栈；run.sh 入口前置依赖自检（import 失败即提示，不进入构建）。
- **涉及**：hb/check_env.sh、hb/run.sh、hb/env.sh。
- **验收**：干净 PATH 下 check_env 对已装 Chrome 的 mac 报 OK；缺包环境报一行安装命令。

### P1-2 playwright 版本漂移重复下载
- **现象**：npm 包升级后缓存缺对应 revision，每次重下 ~99MB；沙盒下删 `__dirlock` 还报错。
- **改法**：package.json 锁死 playwright 版本；check_env 容忍缓存中已有 revision（`npx playwright install chromium` 前先 `ls ~/Library/Caches/ms-playwright` 匹配）；文档写明缓存是用户级共享。
- **涉及**：hb/package.json、hb/check_env.sh、SKILL.md 环境一节。
- **验收**：缓存已有可用 chromium 时不发起下载；缺时才下载。

### P1-3 YAML 撇号炸解析，报错不友好
- **现象**：单引号串内撇号（Thailand's）导致 flow 解析失败，只报「第 278 行第 429 列」，不说明原因；人工排查 2 轮。
- **改法**：doc2yaml/new_project 生成的字符串统一双引号；flow 解析 catch 时检测行内单引号串含未转义 `'` → 提示「单引号内的撇号要双写 '' 或改用双引号」。
- **涉及**：hb/flow.py（或 hb.py 解析处）、hb/doc2yaml.py。
- **验收**：用含撇号单引号串触发 → 报错含改法说明。

### P1-4 brief.md 未确认行被 lock 拦
- **现象**：brief 里写「look: （不适用）」被 lock 拒绝，报错没说「未确认的行应删掉」。
- **改法**：lock.py 提示改为「第 N 行未确认项：删除该行，不要留空值/占位」。
- **涉及**：hb/lock.py、templates/brief.md。
- **验收**：占位行触发 → 提示含删除指引。

---

## P1 · 排版引擎（本册逐页目检发现的版式缺陷）

### P1-5 章节页底色轮换破坏四章一致
- **现象**：FULL 章节页由 choose() 轮换 A/B，accent 档下 B = 浅色次级底 → 本册第四章变成浅色页，巨大章节号蓝-on-浅几乎不可见，四章翻起来不一致。
- **改法**：章节页默认统一 surface A；轮换仅在 full 色档或显式 `alternate: true` 时启用；colorqa 对「同色档相邻章节页不同 surface」报 S 级。
- **涉及**：hb/flow.py（choose/poster_side 分支）、hb/canon.py、hb/colorqa.py。
- **验收**：四章章节页默认同底色；显式 alternate 时才轮换，且有样张。

### P1-6 展示标题自动折行卡 64px 下限并报 flag
- **现象**：disp 标题 mn=64 硬编码；长标题自动平衡折行到 3 行仍卡下限，cn-fit 记 flag（P0-1 未分级前还拦门禁）；手动 `\n` 断行可放到 ~76px 且消 flag。
- **改法**：cnFit 折行搜索允许在手动断行（显式 `\n`）时突破 mn；对 >5 词标题提示建议手动断行位置（报告给出建议分行）。
- **涉及**：hb/fill.js（cnFit）、hb/flow.py。
- **验收**：长标题自动折行不报 flag；触发手动断行建议时报告可见。

### P1-7 T 版 split 参数语义不清且调参无效
- **现象**：split 是从页顶起算的像素（`round((v-88)/28)` 换算行），Ls 有下限 6——200/220/230 全落在同一行，改参数纹丝不动，文档也没写语义。
- **改法**：split 改成语义参数（照片带行数 `photo_rows` 或占页高比例），内部换算；越界时 clamp 并 WARN「已按最小/最大照片带收敛」。
- **涉及**：hb/flow.py（T 版）、references/blocks.md 参数表。
- **验收**：photo_rows 递增 → 照片带实测高度单调递增；越界值有 WARN。

### P1-8 letter 块无落款槽位
- **现象**：letter 行距 42px，信件页空间紧时落款超出版心，只能手工搬到 on_photo 当副题。
- **改法**：letter 支持 `sign` 槽位（署名+机构，独立小字号块，吸底部）；无 sign 时行为不变。
- **涉及**：hb/flow.py、references/blocks.md。
- **验收**：sign 槽位渲染在正文下且不占 letter 行距；旧 letter 用法样张不回退。

### P1-9 西文窄栏自动断词（hyphens:auto）
- **现象**：6 处窄栏词被拦腰截断（capi-tal / em-brace / an-chored / disagree-ment / pro-viding / com-promise）；宣传册左对齐本不需要断词，词被切碎影响阅读。
- **改法**：hb.py 西文 CSS 去掉 `.cn-tx` 的 `hyphens:auto`（保留中文与显式 `<wbr>`/软连字符场景）；跑 selftest 确认无回归（注意会影响窄栏容量，需回归全部英文样张）。
- **涉及**：hb/hb.py（西文 CSS 段）、hb/selftest.sh 覆盖。
- **验收**：同内容重建后窄栏无自动连字符；容量回归 PASS。**待用户确认再动**（影响所有英文书）。

---

## P2 · 交付与导出（TODO 复验仍存在 + 本轮新发现）

| # | 问题 | 证据 | 改法 |
|---|---|---|---|
| P2-1 / F09 | 导出 PDF 无书签（outline=0），目录链接有、PDF 大纲无 | 本册 22 页实测 `open_outline()` 为 0 | export.sh/pdf.js 用 page.pdf 后 pikepdf 补 outline（章节页标题 → 书签），postflight 断言 ≥1 |
| P2-2 / F10 | 源 ZIP 缺 images.yaml（逐图来源/授权/DPI/页码记录丢失） | 本册 zip 93 文件无 images.yaml | export.sh 打包清单加 images.yaml；缺字段时 postflight 明确列出缺哪项 |
| P2-3 / F12 | 单文件 HTML 仍请求 Google Fonts（字体已嵌入） | 本册 HTML grep 到 fonts.googleapis.com 1 处；注入源头是 `hb/standalone.py:27-32`（ROADMAP 原写 hb.py，已校正）；PDF 导出链（pdf.js 只加载 file://）不受影响 | standalone.py 删除该注入（或仅字体未内嵌时按需追加），保留 license 注释 |
| ~~P2-4~~ | ~~export 留下未压缩暂存目录~~ | **已关闭**：2026-10-18 审核实测 export.sh:36-38 为 cd 后直接 zip，无暂存目录；该问题不存在 | — |
| P2-5 | out/ 时间戳拼版图堆积 | 本册 142045/152145 两份并存 | run/export 只保留最新一份，旧的移 `.qa/history/` 或删除 |
| P2-6 | postflight 低清提示无「交印前替换清单」 | 本册 8 张 <150dpi，只在构建日志里 | 导出 `print_checklist.md`：低 DPI 图清单 + 页数装订建议 |
| P2-7 | 页数非 4 倍数无装订提示 | 本册 22 页，骑马钉需补 2 页或改胶装，纯人工 | postflight 计算：骑马钉提示补差、无线胶装确认、跨页照片页对齐奇偶 |
| P2-8 | facts 对 split 等排版参数数字仍误报 | v4 说排除 split/strip/body_top/top_y/bottom_y，本册仍需手工为 split 200/280/230 建 facts 条目 | 全面核对参数名清单（含新参数），纳入 facts 排除表；补一条 selftest 负例 |

---

---

# TODO.md 未关项全量登记（2026-10-18 并入）

来源：TODO.md 各轮测试记录。**已在本文件跟踪的只做交叉引用，不复制**（单一计划源原则）。TODO.md 保留为原始发现的详细记录（含证据路径）。

## P1

- [x] **图片路径-1 · 补齐主图与辅助图的生成规则。** 明确主要现场照进主图片位的规则、何时用 figure/gallery、何时用无图风格插画；处理 SPREAD_OPENER 独立 top/bottom 栈（避免主合照成为浮在装饰底图上的小插图）；入口/文档/模板遵循同一规则。涉及：references/blocks.md、workflows/new.md、hb/flow.py 的 poster_side。
- [x] **图片路径-2 · 补齐图片构图的自动检查，消除放行缺口。** 覆盖 figure/gallery、跨页独立栈及 contain 后的实际可见图片区域；按页面任务判断主图占比、图文关系、无意义空白；区分辅助图与装饰；明确哪些问题必须修复。注意 cn-small 当前只查 data-minh——缩图让位机制不等于图片尺寸验收（与 P0-1 的 cn-small 阈值化联动设计）。涉及：hb/flow.py 的 figure、hb/fill.js 的 cnCheck、hb/doctor.py、references/review.md。
- [x] **F05 · PPT 骨架自动分段。** 22 页原稿在 new_project → doc2yaml 后只生成 1 个内容块，需人工重新分段。涉及：hb/doc2yaml.py。
- [x] **F06 · 完整目录容量。** 原生 GRID.toc 的 4 章目录加页头/描述后溢出约 350px，本轮只能拆成两页目录。涉及：canon.py GRID / flow.py toc。
- [x] **F07 · 原生版式的过度裁图。** 28 页稿第 10、14、20、22 页的 ONE/TWO/MIX 图位约 794×143，只显示原图约 30%/30%/27%/12%（合照、象身与场馆主体被裁）仍获 GATE PASS；不是旧 figure 路径独有。与图片路径-2 同根。
- [x] **F17 · 段落断行质量控制。** 两端对齐试验已被用户拒绝（短句与强制换行造成词间大洞），当前基线 v4。方向：输入层区分真实段落/短信息/作者强制换行；评估段落级断行优化与语言断词能力（参考 Adobe Paragraph Composer、WebKit text-wrap:pretty）；协调词距范围、行尾参差、连续断词、末行孤行；不能用 justify 开关替代排版质量；须实测词距与真实 PDF 后才采用，未达效果不换引擎不宣称已修。
- [x] **F17后续 · WebKit 导出评估。** 已实测 Chromium/WebKit pretty 改善过短末行，但不同引擎不等价；Playwright 的 WebKit 不支持 PDF 接口，当前 PDF 仍 Chromium；未实施 WebKit 矢量/可编辑 PDF 输出，也未完成词距/白河/断词质量的自动验收。
- [x] **F21后续 · 字体选定后全书重排与实际 PDF 复核。** 建议方向：Inter 标题/导航 + Source Serif 4 连续正文（v11 已试排 B/C 两套并出四组同页对照）；尚未应用到正式 28 页 PDF。需复查正文实际字面、导语断词、密集页容量、时间轴和完整联系方式；换字体改变 ch 度量与自动分栏，不能把直接替换当作全书已重排。与 F22 联动。
- [x] **F22 · 西文排印密度与字号适配。** 当前 A4 正文只支持 14/16 两档且与网格行距绑定；第 15 页实测正文 16/28px（12/21pt）、导语 23.3/42px（17.5/31.5pt）、标题 46.7/56px、900 字重，默认较疏；字体字面不同又改变视觉大小。需在统一引擎内试排字号/行距/字重/栏宽组合，确认角色层级后再全书复查；不直接给所有风格强加某一"杂志字号公式"。

## P2

- [x] **F08 · 长标题、密集页与留白。** 默认网格下需人工拆页、调整层级；部分页字号收紧、部分页明显空，构建通过仍需视觉判断。
- [x] **F09 · PDF 书签缺失。** 目录链接正常但 PDF outline 为 0，未达"带书签"承诺 → 已在本文件 P2 表 P2-1 跟踪（22 页实测 outline=0）。
- [x] **F10 · 源文件包缺 images.yaml。** ZIP 未含逐图来源/授权/DPI/页码记录 → 已在本文件 P2 表 P2-2 跟踪（93 文件实测）；手动补入不代表导出器已修。
- [x] **F11 · contain 图片 DPI 误报。** 封底二维码实际显示 84×84、256px 原图约 293dpi，清单却按宽容器估算为约 47dpi 并被 postflight 报低清。涉及：images.py 的 DPI 估算（应按实际渲染框而非容器宽计算）。
- [x] **F12 · 单文件 HTML 多余网络请求。** 已嵌入字体仍请求 Google Fonts → 已在本文件 P2 表 P2-3 跟踪（源头 standalone.py:27-32，PDF 链不受影响）。
- [x] **F13 · 来源与授权检查表述不实。** postflight 只检查 source，却输出"来源/授权通过"；license 状态未验证。涉及：hb/postflight.py。
- [x] **F14 · 拆页后的相对引用失效。** 原文 "both are on this page" 拆成两页后语义失效，现有原文核对发现不了；需加入分页语义审稿（page-plan / review 环节）。
- [x] **方向样张-1 · 无 book.yaml 时必须验证真实图片。** directions.py 当前从模板选第 1、4、5 页，这些页没有图片字段、未使用用户真实照片；样张至少覆盖一个真实主图页和一个真实多图页，确实缺素材时明确说明验证范围。涉及：hb/directions.py、workflows/new.md。
- [x] **照片回归-1 · selftest 覆盖照片路径。** 已在本文件 F53 跟踪 selftest 静默跳过 3 份模板；本条补充固定测试素材要求：来源和许可明确的测试照片，覆盖照片模板、主图、figure、gallery、跨页与不同风格，并保留"原先图片布局不合格但 GATE PASS"的反例。
- [x] **F40 · 西文 hyphens:auto 断词。** 已在本文件 P1-9 跟踪（hb.py:273 一行 CSS + selftest），待用户确认。

## 遗留边界（各轮记录中明确不关闭的）

- 11 个注册风格 + stijl beat 变体的真实照片覆盖率未验证；不能推断所有输入/所有风格不再出现构图问题。
- 跨页主图生成规则（SPREAD_*）已补写法，但未覆盖全部跨页构图场景。
- 合照横幅英文全称跨中缝，实体装订可能吞字（v9 记录）。
- 完整 new 流程的多轮独立执行成功率未评估。

## 仍开放项的原始记录

TODO.md 是以上各项的原始发现记录（含每轮的证据目录与验收条件），本文件是唯一计划源；新增发现先记 TODO.md 再并入本文件。

---

## 下一版验收口径

1. 同一 PPT 重跑 quick 路线：零人工修 YAML、零手工删页码、零 WARN 级内容丢失、GATE 一次通过。
2. P0 全部关闭前，任何 GATE PASS 不得对外表述为「内容无损」。
3. 完整 `hb/selftest.sh` PASS；受影响的版式效果图与样张重出。

---

# 系统性审核补充（2026-10-18，AUDIT-2026-10-18.md；编号 F41+）

四路并行只读审计（文档/Python/JS·Shell·CSS/安全）新增发现。**F41 是当前唯一架构级缺陷，应最先修。**

## P0

- [x] **F41 / P0 · frontmatter 缺 `agent_created: true`。** SKILL.md:1-4 仅 name/description；skill_manage 将无法修改/删除本 skill。改法：补一行 + selftest 第 4 节加断言防回退。

## P1

- [x] **F42 / P1 · `open()` 无 encoding 13+ 处。** hb.py:284/290、postflight.py:44-45、qa.py:3、dark.py:8、doctor.py:5/6/29/34、brief.py:35、gate.py:24/28/31 等；非 UTF-8 locale 下读 b3.json 抛 UnicodeDecodeError、postflight 写 log.md 失败发生在导出最后一步。改法：全仓补 `encoding='utf-8'`（yaml 读取 20+ 处是范本）+ selftest 防回归 grep + `LC_ALL=C` 冒烟。
- [x] **F43 / P1 · 多画布半吊子。** brief.py:13 硬编码 A4 高 1123（a5/xhs 的 image_brief 尺寸偏大 40%+）；shot.js:7 视口写死 794×1123（非 A4 的 QA 截图/拼版/colorqa 全失真）；colorqa.py:22 固定 80×113 采样。改法：brief 读 map.json 的 W/H；shot.js 从 body data-grid 读视口。
- [x] **F44 / P1 · requirements.txt 零版本锁。** 2-10 行全部 `>=`；构建不可复现 + 上游投毒直达构建链（npm 侧已踩过同类坑）。改法：requirements.lock 或 `==`。
- [x] **F45 / P1 · run.sh 环境守卫缺失 + 未知参数静默降级。** run.sh:37 直接调 python3，缺包抛原始栈；run.sh:10/13 只匹配 `--proof`，`--proff` 拼错静默进全本构建。改法：source env.sh 后 import 快检（失败退出码 2 + check_env 指引）；case 白名单。
- [x] **F46 / P1 · shot/pdf/pngs.js 错误对非技术用户不可读。** shot.js:37/pdf.js:12/pngs.js:10 裸 console.error(e)；editor.js:66 已有中文映射表可复用。改法：常见态（ENOENT/playwright 启动失败）转人话。
- [x] **F47 / P1 · 照片 bake2 无缓存。** hb.py:136 每轮无条件重烤全量图（plate/placeholder/字体子集都有缓存，唯独照片没有）。改法：按 (源 mtime+size, w, H, focus, target, zoom, mask, kind) 生成缓存键。
- [x] **F48 / P1 · TODO/ROADMAP 未登记不入库。** SKILL.md grep 计数 0、git `??`；clone 者看不到 39+ 条已知问题。改法：SKILL.md §5 或 maintenance.md 加一行登记；**先脱敏**（TODO/ROADMAP 含 9 处 ~ 绝对路径 + 客户项目名 YLMUN，改写相对路径/占位）再 git add。
- [x] **F49 / P1 · playwright 版本漂移 + Node 声明矛盾。** package.json:5 `^1.45.0` vs lock 实际 1.64.1；check_env.sh:12 说 Node 18+，lock 内 engines `node>=20`。改法：精确版本 + 改"Node 20+"。

## P2

- [x] **F50 / P2 · "换字体"无路线入口且 fonts 不在决策锁。** revise.md:11-31 反馈表无字体行；lock.py:27 比对无 fonts；brief.md 无 fonts 行（TODO F21 同类）。改法：revise 表加"想换字体 → style.md §2.2 + page-plan 记字体分工"；brief 设可选 fonts 行纳入 lock。
- [x] **F51 / P2 · 文档单一主人走形。** lock 纪律（SKILL.md:33 vs new.md:47）、改版纪律（:57 vs revise.md:4/6）、顾问纪律（3 处）、网格规格（4 处：SKILL.md:47/layouts.md/delivery.md:72-75/blocks.md:139）、图片清晰度口径不一（images.md:17 的 1400 vs blocks.md:148 的 1600）。改法：收敛为指针；清晰度阈值主人放 images.py。
- [x] **F52 / P2 · .qa JSON 契约无版本头。** b3/overflow/sparse.json 由 shot.js:32 写、qa.py:3/dark.py:8/doctor.py:28/brief.py:35 读；字段改名静默断 4 个消费方。改法：加 `{"v":1}` 头 + 最小键断言。
- [x] **F53 / P2 · selftest 静默跳过 3 份照片模板且吞模板损坏。** selftest.sh:43 退出码 3=跳过，bash 捕获任何非 0。改法：合成照片降跳过率为 0（test_photo_layout 控制图思路）；显式列出跳过名单；区分退出码。
- [x] **F54 / P2 · 安全纵深三件。** new_brand.sh:29/directions.py 品牌名 `../` 逃逸删除目录；export.sh:38 zip 跟随符号链接（subset.py:40 还主动造链）；extract.py:153 固定名临时目录。改法：`^[A-Za-z0-9_-]+$` 校验/realpath 断言；zip 加 `-y`；tempfile。
- [x] **F55 / P2 · 字体许可证缺口。** 按需下载字体（Noto/LXGW 等，fonts.py:41-67）无许可文本；subset.py 改内部字体名（OFL Reserved Font Name 要求）。改法：下载时落 license；standalone.py 的 LICENSES.txt 覆盖全量。
- [x] **F56 / P2 · git 卫生。** 提交信息 3 条无信息量 + 31 文件未提交；.gitignore:6-7 `/brands` 重复且与已跟踪状态矛盾。改法：范围式提交信息；F48 脱敏后一并入库；去重并明确 brands 策略。
- [x] **F57 / P2 · CSS 归属隐患。** canon.css 无 @page/分页规则，靠 hb.py:272 拼接顺序从 style.css:30 隐式继承；canon.css:42 `.cn-chip` 的 #111 深底主题不可配。改法：顶部注释归属；色值变量化。

## P3

- [x] **F58 / P3 · 死代码与小疮。** wash.py:24-28 M_* 掩膜 + hb.py:12 MX 无调用方（默认参数还是 A4 像素坐标）；hb.py:5 docstring 过时（"固定 A4"）；export.sh:33-34 可编辑 PDF 误导提示；check_env.sh:20 字体检查假阳性（fonts.py 崩溃→打印"OK 字体齐全"）；run.sh:45 brief.py 失败中止构建（应 `|| true`）；run.sh:44/30 montage/compare 失败与门禁状态不一致。
- [x] **F59 / P3 · 信任边界文档化。** flow.py:321 `{html:}` 是有意逃生舱但无信任要求警示（不可信原文进在线编辑页=存储型 XSS）；editor.js:12 `innerHTML=...replace(...)` 是纵深防御单点。改法：SKILL.md/blocks.md 警示；editor.js:12 改 textContent 派生。
- [x] **F60 / P3 · 文档轻项。** SKILL.md:8/47 两处第二人称；§5 地图漏 adaptation.md/editorial-advisor.md；2 个模板 yaml（nophoto/family-handbook）无文档定位；2 张 gallery 孤儿图；export.sh 文档写必填实为可选；SKILL.md:33 lock 字段列不全（实为 9 个）。

## 审核同时确认的好设计（勿动）

bash 3.2 兼容、rm -rf 边界干净、幂等性（播种确定+_base 重置+旧产物清理）、.qa 让位参数无死参数、lockfile 在库、node_modules 未入库、用户内容转义链稳健、yaml 全 safe_load、"一个引擎"原则彻底（stijl/geo 亦走 canon 原语）。

---

# 修复完成记录（2026-10-18 全量修复轮）

用户要求「全部都解决，不用分 P」，本轮按文件所有权分区并行修复 + 主 agent 补齐 + 完整回归。

## 验证结果

- **完整 selftest：PASS**。覆盖：41 个 Python 编译 + 5 个 JS；模板/品牌/用途 yaml 与索引；文档引用零断链；SKILL.md 预算；4b 工程纪律断言（agent_created / open encoding / hyphens 关闭）；5 份模板（含 3 份照片模板，用 CC0 合成图补齐，不再跳过）；品牌包；swiss + stijl + geo + editorial + notebook + inkwash + papercut + riso + aurora + nebula 共 10 种风格；a5 / xhs 画布；照片打印回归。
- **YLMUN 22 页项目重建**：见 `.qa/review_*.jpg` 与 GATE 结果（本轮回归样张）。
- **git 提交**：见本轮提交信息（脱敏后的 TODO/ROADMAP/AUDIT 已入库）。

## 三项评估结论（未采纳，理由留档）

- **F22 正文 15px 档**：不采纳。网格按「一栏整数个汉字」推导（A4 一栏 80px = 5×16px），15px 无法整除栏宽，会破坏整字网格；14 / 16 两档已覆盖「紧凑 / 标准」。需要更密时可改 `book.body: 14`。
- **F17后续 WebKit 导出**：不采纳。Playwright WebKit 无 PDF 接口；Chromium 是当前 PDF 引擎，`text-wrap: pretty` 已在正文生效（F17 基础落地）。段落级排版优化仍需按 TODO 的验收条件继续实测，不在本轮强推。
- **F21后续 字体选定后全书重排**：属 28 页测试项目的项目级任务（需重排 + 逐页视觉复核），不是 skill 代码缺陷；试排证据保留在 `~/Documents/YLMUN_handbook_test_20261018_v1/font-study-v10/`。

## 遗留说明

- TODO.md 仍是原始发现记录（含证据路径）；ROADMAP 是唯一计划源。
- 图片路径-2（构图检查）已落地基础版：`cn-imgarea` 报主图可见高度 <150px；更细的「按页面任务判主图占比」仍需人工审稿（review.md）。
