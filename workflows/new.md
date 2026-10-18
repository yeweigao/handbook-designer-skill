# 路线 new：从一份文字稿新做一本（默认路线）

适用：用户给了原文（Word / PDF / PPT / Markdown / 纯文字），要一本新的册子。整本流程分两轮确认，确认的东西写进 `brief.md`，之后每次构建都拿它对一遍，排到一半不会偏。

```
建项目 → 盘点 → 第 1 轮：沟通合同 → 第 2 轮：三个方向样张 → 写 brief.md
       → 写 book.yaml → （16 页以上）试排 --proof → 全本 run.sh → 审稿 → 导出 → 交付
```

## 1 · 建项目、盘点
```bash
HB=<skill目录>/hb; P=<工作目录>/<项目名>_v1
bash $HB/check_env.sh                          # 新环境第一次用时跑一次
bash $HB/new_project.sh $P 原文.pptx 照片目录/   # → doc.md + plan.md + photos/（资料里的图自动抽出）
```
读 `plan.md`（字数、照片按清晰度分档、每段建议版式、页数估计、原文里的空白 / 重复 / 页码问题），再自己通读原文，补上脚本查不出的：错别字、前后矛盾、过时信息、要复核的事实。

## 2 · 第 1 轮：沟通合同（先对齐“给谁看、读完做什么”）
先判断用途方法：`purposes/index.yaml` 里哪一种最接近（招生简章 admissions / 研学任务册 study-trip / 家长手册 parents / 新生手册 freshman / 年度回顾 annual）。读那个 yaml 的 reader / action / hook / roles。
照这个格式回复，然后**停下来等回答**：
```
我看完了你发的文件：〔一句话：什么文件、多少页、讲什么〕。〔图片：几张、够不够印刷〕
我理解这本册子是这样的，你看对不对：
| 读者 | 〔……〕 |  | 场景 | 〔……〕 |  | 读完要做的事 | 〔一个动作〕 |
| 语气 | 〔……〕 |  | 必须出现 | 〔……〕 |  | 不能出现 | 〔……〕 |
用途：〔招生简章 / 家长手册……〕，约 〔N〕 页（4 的倍数），〔印刷 / 电子版〕，〔中文 / 中英两版〕〔，品牌包 allas〕
需要你确认
1. 上面这张表对不对（改哪一格）
2. 原文里的空白：〔逐条〕——给我数字，还是先留空？
3. 原文疑似错误：〔逐条〕——你说改，我再改
4. 素材：〔logo / 二维码 / 照片不够时补原图还是 AI 补图〕
```
只列真正影响结果的问题。用户的回答只覆盖一部分时，没回答的按你推荐的来，交付时说明。

## 3 · 第 2 轮：三个方向的样张（让用户看图选，而不是读文字选）
```bash
python3 $HB/directions.py $P "A=style:photo,colors:klein" "B=style:swiss,colors:hermes" "C=style:papercut,colors:china-red" \
        --title "〔书名〕" --kicker "〔小标签〕"
# 有品牌包：其中一个方向写 brand:allas；还没写 book.yaml 时用模板的版式 + 真书名
```
→ `$P/.qa/directions.jpg`（每行一个方向：封面 | 章节页 + 卡片；样例 `references/gallery/directions_sample.jpg`）。三个方向要真的不同（风格 × 撞色 × 有无照片），不是同一套换颜色。
发图给用户，每个方向一句话说明适合什么，推荐一个，等用户选。配色先从四组经典撞色里挑（klein / hermes / china-red / lemon-violet，style.md §3）。

## 4 · 写 brief.md
`cp <skill>/templates/brief.md $P/brief.md`，把两轮确认的东西写进去：顶部设置块（route、purpose、kind、brand、style、colors、langs、canvas、pages）+ 沟通合同 + 选中的方向 + 原文问题的处理。
从这一刻起，`run.sh` 每次都先跑 `lock.py`：book.yaml 的设置和 brief.md 不一致就停（`[决策不一致]`）。要改设置 → 先问用户 → 改 brief.md 并在“改动记录”记一笔 → 再改 book.yaml。

## 5 · 写 book.yaml
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
按 `references/review.md` 逐页过（H 硬伤必改、S 软问题记下来一起说、“不要动”的别碰），结果写 `.qa/review.md`。双语再看 `.qa/compare_*.jpg`。24 页以上可以分组并行看（review.md 末尾）。

## 9 · 导出、交付
```bash
bash $HB/export.sh $P/〔语言〕 〔文件名〕   # 门禁：必须是 GATE PASS 之后没改过的版本；只想先给人看 → 加 --draft
```
→ `out/`：PDF、可编辑 PDF、单文件 HTML、源文件 zip、拼版图（小红书画布另有每页 1080×1440 图片）；`.qa/postflight.md` 是导出自检。
交付清单和回复写法见 SKILL.md「交付」和 `references/delivery.md`。用户要在线改字：`workflows/edit-online.md`。
