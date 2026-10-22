"""契约校验测试：python3 -m unittest discover -s dev/tests/core -p 'test_*.py'

正例必须零错误；每个反例只在正例上引入一处违规，必须报出对应错误码。
"""
import json
import os
import shutil
import sys
import tempfile
import unittest

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "hb", "core"))
import validate  # noqa: E402

FIX = os.path.join(REPO, "dev", "fixtures", "contract")
MIN = os.path.join(FIX, "minimal-zh")
BI = os.path.join(FIX, "bilingual")
QA = os.path.join(REPO, "dev", "fixtures", "qa", "base")


def edit(path, old, new):
    with open(path, encoding="utf-8") as f:
        s = f.read()
    assert old in s, f"{old!r} 不在 {path}"
    with open(path, "w", encoding="utf-8") as f:
        f.write(s.replace(old, new, 1))


def edit_json(path, fn):
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    fn(d)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)


def append(path, text):
    with open(path, "a", encoding="utf-8") as f:
        f.write(text)


# (名称, 基础样例, 修改函数, 期望错误码)
NEGATIVE = [
    ("重复页面 ID", MIN, lambda d: edit(f"{d}/book.html", 'data-page-id="p-first-month"', 'data-page-id="p-cover"'), "html.page-id"),
    ("页面缺 ID", MIN, lambda d: edit(f"{d}/book.html", ' data-page-id="p-first-month"', ""), "html.page-id"),
    ("页面不是 body 直接子元素", MIN, lambda d: edit(f"{d}/book.html", '<section class="page cover"', '<div><section class="page cover"'), "html.page-parent"),
    ("重复内容 ID", MIN, lambda d: edit(f"{d}/book.html", 'data-source-id="month-note"', 'data-source-id="month-body"'), "html.source-dup"),
    ("内容节点嵌套", MIN, lambda d: edit(f"{d}/book.html", "沉默期是正常的", '<span data-source-id="nested">沉默期</span>是正常的'), "html.source-nested"),
    ("内容节点里放图片", MIN, lambda d: edit(f"{d}/book.html", "沉默期是正常的", '<img src="assets/fonts/NotoSansSC-400.ttf">沉默期是正常的'), "html.content-tag"),
    ("内容藏进装饰", MIN, lambda d: edit(f"{d}/book.html", 'aria-hidden="true"></div>', 'aria-hidden="true"><span data-source-id="hidden">藏起来</span></div>'), "html.source-deco"),
    ("非法角色", MIN, lambda d: edit(f"{d}/book.html", 'data-role="key"', 'data-role="important"'), "html.role"),
    ("script", MIN, lambda d: edit(f"{d}/book.html", "</body>", "<script>1</script></body>"), "html.forbidden"),
    ("style 标签", MIN, lambda d: edit(f"{d}/book.html", "</head>", "<style>p{}</style></head>"), "html.forbidden"),
    ("link stylesheet", MIN, lambda d: edit(f"{d}/book.html", "</head>", '<link rel="stylesheet" href="book.css"></head>'), "html.forbidden"),
    ("事件属性", MIN, lambda d: edit(f"{d}/book.html", '<section class="page cover"', '<section onclick="x()" class="page cover"'), "html.handler"),
    ("外链图片", MIN, lambda d: edit(f"{d}/book.html", "</footer>", '</footer><img src="https://example.com/a.jpg">'), "ref.network"),
    ("项目外文件", MIN, lambda d: edit(f"{d}/book.html", "</footer>", '</footer><img src="../bilingual/assets/images/campus.jpg">'), "ref.outside"),
    ("图片不存在", MIN, lambda d: edit(f"{d}/book.html", "</footer>", '</footer><img src="assets/none.jpg">'), "ref.missing"),
    ("CSS 写 @page", MIN, lambda d: append(f"{d}/book.css", "\n@page { size: A5; }\n"), "css.page"),
    ("CSS 写 @font-face", MIN, lambda d: append(f"{d}/design.css", '\n@font-face { font-family: X; src: url("assets/fonts/NotoSansSC-400.ttf"); }\n'), "css.font-face"),
    ("CSS 外链", MIN, lambda d: append(f"{d}/book.css", "\n.x { background: url(https://example.com/a.png); }\n"), "ref.network"),
    ("CSS @import 缺文件", MIN, lambda d: append(f"{d}/book.css", '\n@import "parts/missing.css";\n'), "ref.missing"),
    ("字体文件缺失", MIN, lambda d: os.remove(f"{d}/assets/fonts/NotoSansSC-400.ttf"), "ref.missing"),
    ("可变字体", MIN, lambda d: shutil.copyfile(os.path.join(REPO, "dev/fonts/Inter-VF.ttf"), f"{d}/assets/fonts/NotoSansSC-400.ttf"), "font.variable"),
    ("字重写成范围", MIN, lambda d: edit_json(f"{d}/project.json", lambda p: p["fonts"][1].update(weight="100 900")), "project.fonts"),
    ("降低可读性下限", MIN, lambda d: edit_json(f"{d}/project.json", lambda p: p.update(readability={"body_px": 12})), "project.readability"),
    ("版面字段", MIN, lambda d: edit_json(f"{d}/project.json", lambda p: p.update(layout=[{"page": 1}])), "project.layout"),
    ("未知字段", MIN, lambda d: edit_json(f"{d}/project.json", lambda p: p.update(theme="dark")), "project.unknown"),
    ("缺必填字段", MIN, lambda d: edit_json(f"{d}/project.json", lambda p: p.pop("canvas")), "project.required"),
    ("默认语言不在列表", MIN, lambda d: edit_json(f"{d}/project.json", lambda p: p.update(default_language="en")), "project.default_language"),
    ("styles 写了 lang", MIN, lambda d: edit_json(f"{d}/project.json", lambda p: p["styles"].append("lang/en.css")), "project.styles"),
    ("片段编号不连续", MIN, lambda d: edit(f"{d}/book.html", 'data-source-id="month-body"', 'data-source-id="month-body" data-fragment="2"'), "html.fragment"),
    ("缺译", BI, lambda d: edit_json(f"{d}/copy/en.json", lambda c: c["strings"].pop("day-p3")), "copy.untranslated"),
    ("多余译文", BI, lambda d: edit_json(f"{d}/copy/en.json", lambda c: c["strings"].update({"ghost": "Ghost"})), "copy.extra"),
    ("缺语言文案文件", BI, lambda d: os.remove(f"{d}/copy/en.json"), "copy.missing"),
    ("默认语言也建了 copy", BI, lambda d: shutil.copyfile(f"{d}/copy/en.json", f"{d}/copy/zh-CN.json"), "copy.default"),
    ("lang 样式语言不在列表", BI, lambda d: shutil.copyfile(f"{d}/lang/en.css", f"{d}/lang/fr.css"), "lang.unknown"),
    ("跨页起始在右页", BI, lambda d: edit_json(f"{d}/project.json", lambda p: p.update(first_page="left")), "html.spread"),
    ("跨页不相邻", BI, lambda d: edit(f"{d}/book.html", '<section class="page" data-page-id="p-back">', '<section class="page" data-page-id="p-back" data-spread="s-day">'), "html.spread"),
    ("data-bleed 取值", BI, lambda d: edit(f"{d}/book.html", 'data-bleed="all"></div>', 'data-bleed="outside"></div>'), "html.bleed"),
    ("data-outline 取值", MIN, lambda d: edit(f"{d}/book.html", '<h2 data-role="display"', '<h2 data-outline="4" data-role="display"'), "html.outline"),
    ("data-outline 仅标题可用", MIN, lambda d: edit(f"{d}/book.html", '<p class="intro"', '<p data-outline="1" class="intro"'), "html.outline"),
    ("data-edit-id 重复", BI, lambda d: edit(f"{d}/book.html", 'data-edit-id="img-day-right"', 'data-edit-id="img-day-left"'), "html.edit-id"),
]


def codes(rep, level="error"):
    return {i["code"] for i in rep.items if i["level"] == level}


class ValidateTest(unittest.TestCase):
    def test_positive_fixtures(self):
        for fx in (MIN, BI, QA):
            with self.subTest(fx=os.path.basename(fx)):
                rep = validate.validate(fx)
                self.assertEqual(rep.errors, [], rep.errors)

    def test_negative_mutations(self):
        for name, base, mutate, code in NEGATIVE:
            with self.subTest(name=name):
                with tempfile.TemporaryDirectory() as tmp:
                    d = os.path.join(tmp, "p")
                    shutil.copytree(base, d)
                    mutate(d)
                    rep = validate.validate(d)
                    self.assertIn(code, codes(rep), f"{name}：期望 {code}，实际 {rep.items}")

    def test_raised_floor_and_waiver(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = os.path.join(tmp, "p")
            shutil.copytree(MIN, d)
            edit_json(f"{d}/project.json", lambda p: p.update(
                readability={"body_px": 16},
                readability_waiver={"reason": "社交媒体竖图", "approved_by": "用户", "date": "2026-10-22",
                                    "values": {"aux_px": 9}}))
            rep = validate.validate(d)
            self.assertEqual(rep.errors, [])
            self.assertIn("readability.waiver", codes(rep, "warning"))

    def test_cli_exit_codes(self):
        self.assertEqual(validate.main(["validate.py", MIN]), 0)
        with tempfile.TemporaryDirectory() as tmp:
            d = os.path.join(tmp, "p")
            shutil.copytree(MIN, d)
            append(f"{d}/book.css", "\n@page { size: A5; }\n")
            self.assertEqual(validate.main(["validate.py", d]), 1)


if __name__ == "__main__":
    unittest.main()
