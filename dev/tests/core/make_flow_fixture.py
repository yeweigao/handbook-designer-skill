#!/usr/bin/env python3
"""生成续排样例（未分页状态）：python3 dev/tests/core/make_flow_fixture.py
dev/fixtures/flow/long-bilingual/：中英双语长文，全部内容先放在第 2 页的第一个文字框里（会溢出），
用于测试 `cli.mjs paginate` 与其他语言的渲染时续排。文字是带编号的合成句子，保证每句唯一。"""
import json
import os
import subprocess
import sys

from PIL import Image, ImageDraw

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
D = os.path.join(REPO, "dev", "fixtures", "flow", "long-bilingual")
ZH = ["班主任会在放学时与家长简短沟通孩子当天的状态", "孩子们先用中文朗读再用英语复述同一个故事", "老师记录每个孩子愿意开口的次数而不是只看对错",
      "项目课上三年级正在研究校园里的植物并写观察笔记", "课间活动安排在操场和图书馆两处", "下雨时体育老师会把活动改到室内体育馆",
      "午餐前每个班有十分钟的分享时间", "家长开放日当天欢迎在教室后排安静旁听", "图书馆每周三下午向家长开放借阅",
      "新生第一周以熟悉校园和建立作息为主", "孩子出现短暂的沉默期是正常现象", "请多听孩子讲学校里发生的事而不是急于补课",
      "学校会在每周五发送一次书面小结", "校车路线以开学前一周发布的通知为准", "如有特殊饮食需求请提前告知班主任"]
EN = ["the class teacher briefly updates parents on the child's day at pick-up", "children read a story aloud in Chinese and retell it in English",
      "teachers note how often each child is willing to speak, not only whether they are right", "Grade 3 is studying the plants on campus and keeping observation notes",
      "break time is split between the playground and the library", "on rainy days the PE teachers move activities into the indoor gym",
      "every class has ten minutes of sharing time before lunch", "on Open Day you are welcome to sit quietly at the back of the classroom",
      "the library opens to parents for borrowing every Wednesday afternoon", "the first week for new pupils focuses on getting to know the campus and routines",
      "a short silent period is perfectly normal", "please listen to your child's stories about school rather than rushing into extra lessons",
      "the school sends a written summary every Friday", "bus routes follow the notice published one week before term",
      "please tell the class teacher in advance about any special dietary needs"]
CN_NUM = "零一二三四五六七八九"


def cn(n):
    return "".join(CN_NUM[int(c)] for c in str(n))


def main():
    os.makedirs(os.path.join(D, "assets", "images"), exist_ok=True)
    os.makedirs(os.path.join(D, "copy"), exist_ok=True)
    os.makedirs(os.path.join(D, "sources", "original"), exist_ok=True)
    blocks_html, copy, md = [], {}, []
    n_para = 0
    for chap in range(1, 21):
        hid = f"h{chap:02d}"
        zh_h, en_h = f"第{cn(chap)}章 · 校园生活的细节", f"Chapter {chap} · Details of school life"
        blocks_html.append(f'      <h2 data-role="display" data-source-id="{hid}">{zh_h}</h2>')
        copy[hid] = en_h
        md += [f"## {zh_h}", ""]
        for k in range(8):
            n_para += 1
            pid = f"p{n_para:03d}"
            zs, es = [], []
            for j in range(1, 7):
                ph = (n_para * 7 + j * 3) % len(ZH)
                zs.append(f"第{cn(n_para)}段第{cn(j)}句：{ZH[ph]}。")
                es.append(f"Paragraph {n_para}, sentence {j}: {EN[ph]}.")
            blocks_html.append(f'      <p data-source-id="{pid}">{"".join(zs)}</p>')
            copy[pid] = " ".join(es)
            md += ["".join(zs), ""]
        if chap == 9:
            blocks_html.append('      <figure class="fig"><img src="assets/images/figure.jpg" alt="" data-edit-id="img-figure" data-asset="figure">'
                               '<figcaption data-role="aux" data-source-id="fig-cap">图：合成示意图，仅用于续排回归。</figcaption></figure>')
            copy["fig-cap"] = "Image: a synthetic diagram for flow regression only."
    copy["book-title"] = "A Long Handbook for Flow Tests"
    copy["book-lead"] = "Twenty chapters of numbered sentences that must flow across many pages."
    copy["story-title"] = "Daily life on campus"
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>续排样例：中英双语长文</title>
</head>
<body>
<section class="page cover" data-page-id="p-cover">
  <h1 data-role="display" data-source-id="book-title">续排测试用长篇手册</h1>
  <p class="lead" data-source-id="book-lead">二十章带编号的句子，需要跨越很多页连续排版。</p>
</section>
<section class="page story story-start" data-page-id="p-story">
  <h2 class="story-title" data-role="display" data-source-id="story-title">校园里的日常</h2>
  <div class="frame" data-flow="story">
{chr(10).join(blocks_html)}
  </div>
  <footer class="folio" data-role="aux"></footer>
</section>
<section class="page story" data-page-id="p-story-next">
  <header class="running" data-role="aux"><span data-source-id="book-title" data-repeat>续排测试用长篇手册</span></header>
  <div class="frame" data-flow="story"></div>
  <footer class="folio" data-role="aux"></footer>
</section>
</body>
</html>
"""
    open(os.path.join(D, "book.html"), "w", encoding="utf-8").write(html)
    order = ["book-title", "book-lead", "story-title"]
    json.dump({"contract": 1, "lang": "en", "strings": {k: copy[k] for k in order + [k for k in copy if k not in order]}},
              open(os.path.join(D, "copy", "en.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    md = ["# 续排测试用长篇手册", "", "二十章带编号的句子，需要跨越很多页连续排版。", "", "## 校园里的日常", ""] + md + ["图：合成示意图，仅用于续排回归。", ""]
    open(os.path.join(D, "sources", "original", "原稿.md"), "w", encoding="utf-8").write("\n".join(md))
    project = {"contract": 1, "title": "续排样例：中英双语长文", "entry": "book.html", "styles": ["design.css", "book.css"],
               "languages": ["zh-CN", "en"], "default_language": "zh-CN",
               "canvas": {"trim_mm": [210, 297], "bleed_mm": 3, "safe_mm": 8}, "binding": "digital", "first_page": "right",
               "content_mode": "translate",
               "fonts": [{"family": "Noto Serif SC", "file": "assets/fonts/NotoSerifSC-700.ttf", "weight": "700", "style": "normal"},
                         {"family": "Noto Sans SC", "file": "assets/fonts/NotoSansSC-400.ttf", "weight": "400", "style": "normal"},
                         {"family": "Noto Sans SC", "file": "assets/fonts/NotoSansSC-700.ttf", "weight": "700", "style": "normal"},
                         {"family": "Inter", "file": "assets/fonts/Inter-400.ttf", "weight": "400", "style": "normal"},
                         {"family": "Inter", "file": "assets/fonts/Inter-700.ttf", "weight": "700", "style": "normal"}]}
    json.dump(project, open(os.path.join(D, "project.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    open(os.path.join(D, "design.css"), "w", encoding="utf-8").write("""/* 续排样例的最小家族基因，只为测试。 */
:root { --paper: #fffefb; --ink: #1d2329; --muted: #56606b; --primary: #1f3b5c; --line: #d9d3c7;
  --font-display: "Noto Serif SC", serif; --font-body: "Noto Sans SC", sans-serif; --font-latin: "Inter", "Noto Sans SC", sans-serif;
  --m-top: 18mm; --m-right: 16mm; --m-bottom: 22mm; --m-left: 16mm; }
body { margin: 0; }
.page { background: var(--paper); color: var(--ink); font: 400 16px/28px var(--font-body); }
h1, h2 { margin: 0; font-family: var(--font-display); font-weight: 700; color: var(--primary); }
p { margin: 0; }
[data-role="aux"] { font-size: 11px; line-height: 1.5; color: var(--muted); }
.folio { position: absolute; bottom: calc(var(--bleed) + 12mm); right: calc(var(--bleed) + var(--m-right)); }
.folio::after { content: counter(page-n); }
html[lang="en"] .page { font-family: var(--font-latin); }
""")
    open(os.path.join(D, "book.css"), "w", encoding="utf-8").write(""".cover { padding: calc(var(--bleed) + 60mm) calc(var(--bleed) + 20mm); }
.cover h1 { font-size: 46px; line-height: 1.25; }
.cover .lead { margin-top: 18px; color: var(--muted); }
.story-title { position: absolute; top: calc(var(--bleed) + var(--m-top)); left: calc(var(--bleed) + var(--m-left)); font-size: 34px; line-height: 1.3; }
.running { position: absolute; top: calc(var(--bleed) + 10mm); left: calc(var(--bleed) + var(--m-left)); }
.frame { position: absolute; left: calc(var(--bleed) + var(--m-left)); right: calc(var(--bleed) + var(--m-right));
         top: calc(var(--bleed) + var(--m-top)); bottom: calc(var(--bleed) + var(--m-bottom)); }
.story-start .frame { top: calc(var(--bleed) + 50mm); }
.frame p + p { margin-top: 14px; }
.frame h2 { font-size: 22px; line-height: 1.4; margin: 26px 0 10px; }
.frame > h2:first-child { margin-top: 0; }
.fig { margin: 22px 0; }
.fig img { display: block; width: 120mm; height: 70mm; object-fit: cover; }
.fig figcaption { margin-top: 6px; }
""")
    w, h = round(120 / 25.4 * 220), round(70 / 25.4 * 220)
    im = Image.new("RGB", (w, h), (226, 232, 238))
    d = ImageDraw.Draw(im)
    for i in range(0, w, 36):
        d.line([(i, 0), (i, h)], fill=(190, 200, 214), width=3)
    d.rectangle([w // 4, h // 4, 3 * w // 4, 3 * h // 4], outline=(31, 59, 92), width=12)
    im.save(os.path.join(D, "assets", "images", "figure.jpg"), quality=86)
    open(os.path.join(D, "sources", "README.md"), "w", encoding="utf-8").write(
        "续排样例：由 dev/tests/core/make_flow_fixture.py 生成，提交的是**未分页**状态（全部内容在第一个文字框里，直接 check 会溢出）。"
        "测试先复制再运行 paginate。图片为合成图。\n")
    subprocess.run([sys.executable, os.path.join(REPO, "hb/core/extract.py"), os.path.join(D, "sources/original/原稿.md"), D], check=True)
    a = json.load(open(os.path.join(D, "sources", "assets.json"), encoding="utf-8"))
    a["assets"]["figure"] = {"file": "assets/images/figure.jpg", "source": "合成图：dev/tests/core/make_flow_fixture.py 生成",
                             "license": "项目自有（测试素材）", "credit": ""}
    json.dump(a, open(os.path.join(D, "sources", "assets.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    subprocess.run([sys.executable, os.path.join(REPO, "dev/tests/core/fixture_fonts.py"), D], check=True)
    print("ok", n_para, "段")


if __name__ == "__main__":
    main()
