---
# 决策记录：用户在第 0 步确认过的东西。run.sh 每次构建都拿它和 book.yaml 对一遍，不一致就停（防止排到一半改了用户没同意的设置）。
# 只写已经确认的项；没确认的删掉这一行。要改：先核已有授权，用户明确要求的直接记录；缺决定才询问，再改这里及 book.yaml。
route: new            # new 新做 / quick 快速 / beautify 美化（文字冻结）/ reuse 沿用旧册 / revise 改版 / brand 建品牌包
purpose: brochure     # workbook 任务册 / guide 指南 / brochure 宣传册
kind: admissions      # 用途方法（purposes/）：admissions 招生简章 / study-trip 研学任务册 / parents 家长手册 / freshman 新生手册 / annual 年度回顾
# brand: acme         # 可选：品牌包（brands/）；没有品牌包就删掉这一行
style: photo          # photo / editorial / swiss / stijl 风格派 / geo 孟菲斯 / notebook / inkwash / papercut / riso / aurora / nebula
look: classic         # 只有 style: stijl 用：classic 三原色 / tone 无线 / beat 节奏；其他风格删掉这一行
colors: klein
# fonts: {title: 'Playfair Display', body: 'Source Serif 4'}   # 可选：只锁你写了的字体角色；整册字体分工记进 page-plan.md
color_mode: auto      # auto / clash 撞色 / accent 点缀（品牌色只做强调）/ mono
langs: [zh, en]
canvas: a4            # a4 / a5 / xhs（小红书 3:4）
pages: 16             # 目标页数（实际 ±4 只提示，不拦截）
---

# 决策记录 · 〔书名〕

## 1 · 沟通合同（第 0 步第一轮，用户确认后填）
| 项 | 内容 |
|---|---|
| 读者 | 〔谁拿到这本册子：如“考虑转学的初中家长”〕 |
| 场景 | 〔在哪看、怎么拿到：开放日现场发 / 微信转发 PDF / 印刷 500 本〕 |
| 读完要做的事 | 〔一个动作：预约参观 / 扫码报名 / 带齐材料来报到〕 |
| 语气 | 〔如：可信、温暖、不夸张〕 |
| 必须出现 | 〔logo、截止日期、联系电话、某张合影……〕 |
| 不能出现 | 〔竞品名、未确认的数据、学生正脸……〕 |

## 2 · 方向（第 0 步第二轮：三个方向的样张 `.qa/directions.jpg`）
- A 〔名字〕：〔style + colors + 一句话〕
- B 〔名字〕：〔……〕
- C 〔名字〕：〔……〕
- **用户选了：〔A〕**，〔补充意见〕

## 3 · 试排（16 页以上：封面 + 两个跨页 `run.sh --proof` 给用户看过）
- 〔日期〕用户意见：〔……〕

## 4 · 原文问题怎么处理
- 〔空白 / 错别字 / 矛盾：逐条写用户的决定〕

## 改动记录
- 〔日期〕〔改了什么，谁同意的〕
