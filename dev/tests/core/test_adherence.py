"""样式一致性检查（adherence）单元测试：python3 dev/tests/core/test_adherence.py"""
import os
import shutil
import sys
import tempfile
import unittest

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "hb", "core"))
import adherence  # noqa: E402

DESIGN = """
:root {
  --fl-paper: #FFFFFF; --fl-ink: #111111; --fl-accent: #C83024;
  --fl-size-aux: 11px; --fl-size-key: 13px; --fl-size-small: 14px;
  --fl-size-body: 16px; --fl-size-lead: 20px; --fl-size-h3: 24px;
  --fl-size-h2: 32px; --fl-size-h1: 46px; --fl-size-display: 64px;
  --fl-size-hero: 112px; --fl-size-giant: 196px; --fl-size-colossal: 280px;
  --fl-space-3: 28px; --fl-leading-body: 1.75;
}
"""


class Stub:
    def __init__(self):
        self.items = []

    def error(self, code, where, msg):
        self.items.append((code, "error", where, msg))

    def warn(self, code, where, msg):
        self.items.append((code, "warning", where, msg))

    def codes(self):
        return [i[0] for i in self.items]


class Adherence(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp(prefix="hb-adherence-")
        self.write("design.css", DESIGN)
        self.write("book.html", "<!doctype html><html><body></body></html>")

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    def write(self, rel, text):
        with open(os.path.join(self.dir, rel), "w", encoding="utf-8") as f:
            f.write(text)

    def run_check(self, book_css, version="2.2.0", waiver=None, html=None):
        self.write("book.css", book_css)
        if html is not None:
            self.write("book.html", html)
        project = {"styles": ["design.css", "book.css"], "entry": "book.html",
                   "family": {"name": "folio", "version": version}}
        if waiver:
            project["style_waiver"] = waiver
        rep = Stub()
        adherence.check_style(rep, self.dir, project)
        return rep

    def test_only_ladder_sizes_pass(self):
        rep = self.run_check(".cover { font-size: 112px; } .body { font-size: 16px; }")
        self.assertEqual(rep.items, [])

    def test_oversized_decoration_uses_max_multiple(self):
        rep = self.run_check(".crop { font-size: 560px; } .type { font-size: 280px; }")
        self.assertEqual(rep.items, [])

    def test_off_ladder_size_is_an_error(self):
        rep = self.run_check(".x { font-size: 640px; }")
        self.assertIn("style.offladder", rep.codes())
        self.assertEqual(rep.items[0][1], "error")

    def test_off_ladder_inline_size_is_an_error(self):
        rep = self.run_check(".x{}", html='<p style="font-size:38px">x</p>')
        self.assertIn("style.offladder", rep.codes())

    def test_rhythm_token_override_is_an_error(self):
        rep = self.run_check(":root { --fl-size-body: 18px; --fl-leading-body: 1.2; }")
        self.assertIn("style.token", rep.codes())
        self.assertEqual([i[1] for i in rep.items if i[0] == "style.token"], ["error"])

    def test_colour_token_override_is_a_warning(self):
        rep = self.run_check(":root { --fl-accent: #2255AA; }")
        self.assertEqual(rep.codes(), ["style.brand"])
        self.assertEqual(rep.items[0][1], "warning")

    def test_decorative_effects_are_reported(self):
        rep = self.run_check(".card { border-radius: 12px; box-shadow: 0 2px 8px #0002; background: linear-gradient(#fff, #eee); }")
        self.assertIn("style.decor", rep.codes())

    def test_many_custom_classes_are_reported(self):
        css = "".join(f".c{i} {{ color: #111; }}\n" for i in range(13))
        rep = self.run_check(css)
        self.assertIn("style.custom", rep.codes())

    def test_waiver_downgrades_hard_items(self):
        rep = self.run_check(":root { --fl-size-body: 18px; }", waiver="客户指定字号")
        self.assertEqual(rep.codes(), ["style.token"])
        self.assertEqual(rep.items[0][1], "warning")

    def test_older_family_versions_are_not_judged(self):
        rep = self.run_check(":root { --fl-size-body: 18px; } .x { font-size: 640px; }", version="1.1.0")
        self.assertEqual(rep.items, [])

    def test_language_css_is_checked_too(self):
        os.makedirs(os.path.join(self.dir, "lang"), exist_ok=True)
        with open(os.path.join(self.dir, "lang", "en.css"), "w", encoding="utf-8") as f:
            f.write(".x { font-size: 34px; }")
        rep = self.run_check(".x{}")
        self.assertIn("style.offladder", rep.codes())


if __name__ == "__main__":
    unittest.main(verbosity=2)


class Process(unittest.TestCase):
    """长册没有风格锁定记录时要给出提示，而不是等下一个人返工。"""

    def test_style_lock_prompt_for_long_books(self):
        import validate
        d = tempfile.mkdtemp(prefix="hb-process-")
        try:
            html = "<!doctype html><body>" + "".join(f'<section class="page" data-page-id="p{i}"></section>' for i in range(12)) + "</body>"
            with open(os.path.join(d, "book.html"), "w", encoding="utf-8") as f:
                f.write(html)
            rep = Stub()
            validate.check_process(rep, d, {"entry": "book.html"})
            self.assertIn("process.style-lock", rep.codes())
            with open(os.path.join(d, "style-lock.md"), "w", encoding="utf-8") as f:
                f.write("# 风格锁定\n")
            rep2 = Stub()
            validate.check_process(rep2, d, {"entry": "book.html"})
            self.assertEqual(rep2.items, [])
        finally:
            shutil.rmtree(d, ignore_errors=True)

    def test_short_books_are_not_prompted(self):
        import validate
        d = tempfile.mkdtemp(prefix="hb-process-")
        try:
            with open(os.path.join(d, "book.html"), "w", encoding="utf-8") as f:
                f.write('<section class="page" data-page-id="p1"></section>')
            rep = Stub()
            validate.check_process(rep, d, {"entry": "book.html"})
            self.assertEqual(rep.items, [])
        finally:
            shutil.rmtree(d, ignore_errors=True)
