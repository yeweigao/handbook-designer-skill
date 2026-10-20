# 路线 new：从一份文字稿新做一本（默认路线）

适用：用户给了原文（Word / PDF / PPT / Markdown / 纯文字），要一本新的册子。整本流程分两轮确认，确认的东西写进 `brief.md`，之后每次构建都拿它对一遍，排到一半不会偏。

```
建项目 → 盘点 → 第 1 轮：沟通合同 → 第 2 轮：三个方向样张 → 写 brief.md
       → 编辑顾问 → page-plan → book.yaml → （16 页以上）试排 --proof → 全本 run.sh → 导出 → 视觉总监审改/重导复核 → 交付
```

## 1 · 建项目、盘点
```bash
HB=<skill目录>/hb; P=<工作目录>/<项目名>_v1
bash $HB/check_env.sh                          # 新环境第一次用时跑一次
bash $HB/new_project.sh $P 原文.pptx 照片目录/   # → doc.md + plan.md + copy_map.md + page-plan.md 骨架 + photos/（资料里的图自动抽出）
```
读 `plan.md`（字数、照片按清晰度分档、每段建议版式、页数估计、原文里的空白 / 重复 / 页码问题、编号标签和备注类候选），再自己通读原文，补上脚本查不出的：错别字、前后矛盾、过时信息、要复核的事实，以及哪些是给 Word 排的脚手架而不是给读者看的（「亮点一：」、备注、版本记录），按 `references/adaptation.md`「按产物适配」处理。
`copy_map.md` 是逐段编号的文案清单（S01…，带位置、类型猜测、字数），之后 page-plan.md 用这些编号写每页放哪几段。类型是脚本猜的，对照原文改对四件事：**层级**（PPT 里字大 ≠ 层级高；Word 里加粗短句常是小标题）、**成组**（一个任务的标题 + 说明 + 产出是一组，设计时不拆开）、**阅读顺序**（PPT 已按幻灯片上从上到下、从左到右抽取，仍要对照原幻灯片确认）、**原文问题**（空白、错字、重复、矛盾——只记录，不改）。PPT 先把幻灯片导出成图看一遍原作者的重点（`soffice --headless --convert-to pdf 原文.pptx && pdftoppm -r 40 -jpeg 原文.pdf slide`）；演讲者备注在 notes.md，默认不排版。

## 2 · 第 1 轮：沟通合同（先对齐“给谁看、读完做什么”）
先判断用途方法：`purposes/index.yaml` 里哪一种最接近（招生简章 admissions / 研学任务册 study-trip / 家长手册 parents / 新生手册 freshman / 年度回顾 annual）。读那个 yaml 的 reader / action / hook / roles。
照这个格式回复，然后**停下来等回答**：
```
我看完了你发的文件：〔一句话：什么文件、多少页、讲什么〕。〔图片：几张、够不够印刷〕
我理解这本册子是这样的，你看对不对：
| 读者 | 〔……〕 |  | 场景 | 〔……〕 |  | 读完要做的事 | 〔一个动作〕 |
| 语气 | 〔……〕 |  | 必须出现 | 〔……〕 |  | 不能出现 | 〔……〕 |
用途：〔招生简章 / 家长手册……〕，约 〔N〕 页（4 的倍数），〔印刷 / 电子版〕，〔中文 / 中英两版〕〔，品牌包 <名字>〕
需要你确认
1. 上面这张表对不对（改哪一格）
2. 原文里的空白：〔逐条〕——给我数字，还是先留空？
3. 原文疑似错误：〔逐条〕——你说改，我再改
4. 素材：〔logo / 二维码 / 照片不够时补原图还是 AI 补图〕
5. 册子里默认不印的：〔「亮点一：」这类编号只留冒号后的标题；备注、批注、版本记录不印——逐类列出，附 1–2 个原文例子〕——有要保留的告诉我
```
只列真正影响结果的问题。用户的回答只覆盖一部分时，没回答的按你推荐的来，交付时说明。

## 3 · 第 2 轮：三个方向的样张（让用户看图选，而不是读文字选）
```bash
python3 $HB/directions.py $P "A=style:photo,colors:klein" "B=style:swiss,colors:hermes" "C=style:papercut,colors:china-red" \
        --title "〔书名〕" --kicker "〔小标签〕"
# 有品牌包：其中一个方向写 brand:<名字>；还没写 book.yaml 时用模板的版式 + 真书名
```
→ `$P/.qa/directions.jpg`（每行一个方向：封面 | 章节页 + 卡片；样例 `dev/gallery/directions_sample.jpg`）。三个方向要真的不同（风格 × 撞色 × 有无照片），不是同一套换颜色。
发图给用户，每个方向一句话说明适合什么，推荐一个，等用户选。无指定品牌或配色时再从经典配色推荐（style.md §3）；已有决定优先。风格名和配色分开标识，换配色不另造风格名；同一方向的照片处理也要说明，不能从“单色版面”推导用户同意黑白照片。样张应覆盖真实主图、信息密集页；脚本未选到时补样张或明确未覆盖，模板色块不算照片验证。

## 4 · 写 brief.md
`cp <skill>/templates/brief.md $P/brief.md`，把两轮确认的东西写进去：顶部设置块（route、purpose、kind、brand、style、colors、langs、canvas、pages）+ 沟通合同 + 选中的方向 + 原文问题的处理。
排版前读 `references/adaptation.md`，按内容角色选择信息块，并在 brief.md 记明本轮文案保留或允许改写的范围；已有明确授权不重复询问。
从这一刻起，`run.sh` 每次都先跑 `lock.py`；设置变更按 SKILL.md §2 的已有授权与决策记录处理。

## 5 · 写 book.yaml
- 先按 `references/editorial-advisor.md` 调用顾问审核完整输入（逐页文案、页面去重、系列建议），已有授权不重复询问。
- 先完成 `page-plan.md`（格式见 `references/adaptation.md`）：逐页采用文案、角色层级、展示与阅读顺序；再执行以下映射，不直接从原稿大字猜title。
- 先排页序：按 `purposes/<kind>.yaml` 的 order 和 roles，每页写 `job: 角色词 · 一句话`（如 `job: apply · 报名三步 + 截止日期`），再给每页选版式（`references/layouts.md`），最后填字。
- 文字一律从 `doc.md` 复制，不凭记忆重写；中英两版写成 `{zh: …, en: …}` + `book.langs: [zh, en]`。
- 完整样例 `templates/book.layouts.yaml`。
- `python3 $HB/lint.py $P`（run.sh 也会跑）：job 有没有、必需的页有没有、节奏条 ■▤□ 有没有起伏。

## 6 · 试排（16 页以上必须做）
```bash
bash $HB/run.sh $P --proof      # 只排第 1–5 页（封面 + 两个跨页）→ $P/.proof/.qa/review_*.jpg
```
发给用户看字号、撞色、照片处理对不对。用户的意见记进 brief.md 第 3 节，再排全本。小于 16 页可以跳过，直接全本。

## 7 · 全本构建、改到 GATE PASS
```bash
bash $HB/run.sh $P              # 最后一行 GATE: PASS / FAIL（双语是 ALL LANGS: …）
```
按 doctor 的 `[溢出] [重叠] [出界] [看不清] [图太小] [标题太长] [缺字] [决策不一致]` 后面的改法改 yaml 重跑。
`[留白]`、`[节奏]`、`[无出处数字]`、`[同图两用]`、`[低清]` 是提示：宣传册里要处理，其他看情况。
check_copy 的 `ORDER` 逐条确认是不是有意的，`EXTRA` 里的自创句删掉。

## 8 · 审稿
先审构建图并对照编辑建议；下一步导出后执行 `workflows/visual-review.md` 的视觉总监逐页审改，标准见 `references/review.md`。双语再看 `.qa/compare_*.jpg`。

## 9 · 导出、交付
```bash
bash $HB/export.sh $P/〔语言〕 〔文件名〕   # 门禁：必须是 GATE PASS 之后没改过的版本；只想先给人看 → 加 --draft
```
→ `out/`：PDF、可编辑 PDF、单文件 HTML、源文件 zip、拼版图（小红书画布另有每页 1080×1440 图片）；`.qa/postflight.md` 是导出自检。
交付前完成 `workflows/visual-review.md`，将修改落实到源文件并复核新PDF，再更新审稿记录、预览与源文件包。
交付清单和回复写法见 SKILL.md「交付」和 `references/delivery.md`。用户要在线改字：`workflows/edit-online.md`。
