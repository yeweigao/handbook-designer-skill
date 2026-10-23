"""Family CSS filenames are metadata; existing projects remain frozen."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "hb" / "core"))
import family  # noqa: E402


class FamilyInit(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="hb-family-init-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.families = self.root / "families"
        self.families.mkdir()

    def make_family(self, name, css_name=None):
        source = self.families / name
        source.mkdir()
        meta = {"name": name, "title": name, "version": "2.2.0", "fonts": [],
                "canvas": {"trim_mm": [210, 297], "bleed_mm": 3, "safe_mm": 8}}
        if css_name is not None:
            meta["css"] = css_name
        (source / "family.json").write_text(json.dumps(meta), encoding="utf-8")
        css = ":root { --fl-size-body: 16px; }\n"
        (source / (css_name or "design.css")).write_text(css, encoding="utf-8")
        return css

    def assert_created(self, name, css_name):
        project = self.root / "book"
        with mock.patch.object(family, "FAMILIES", str(self.families)), \
                mock.patch.object(family, "build_fonts", return_value=[]), \
                mock.patch.object(family, "charset", return_value="书名"):
            family.init(name, str(project), "书名", ["zh-CN"], "carry")
        meta = json.loads((project / "project.json").read_text(encoding="utf-8"))
        self.assertEqual(meta["styles"], [css_name, "book.css"])
        self.assertEqual(meta["family"]["sha256"], hashlib.sha256((project / css_name).read_bytes()).hexdigest())
        self.assertEqual(sorted(p.name for p in project.glob("*.css")), sorted([css_name, "book.css"]))
        self.assertIn("默认可空", (project / "book.css").read_text(encoding="utf-8"))
        return project

    def test_folio_uses_its_declared_filename(self):
        css = self.make_family("folio", "folio.css")
        project = self.assert_created("folio", "folio.css")
        self.assertEqual((project / "folio.css").read_text(encoding="utf-8"), css)

    def test_family_without_css_field_keeps_design_filename(self):
        css = self.make_family("campus")
        project = self.assert_created("campus", "design.css")
        self.assertEqual((project / "design.css").read_text(encoding="utf-8"), css)

    def test_existing_project_is_a_zero_write_noop_for_both_filenames(self):
        for css_name in ("design.css", "folio.css"):
            with self.subTest(css_name=css_name):
                project = self.root / css_name.replace(".css", "")
                project.mkdir()
                (project / "project.json").write_text(json.dumps({"styles": [css_name, "book.css"]}), encoding="utf-8")
                (project / css_name).write_text("/* frozen family */\n", encoding="utf-8")
                (project / "book.css").write_text("/* author patch */\n", encoding="utf-8")
                (project / "assets").mkdir()
                (project / "assets" / "font.ttf").write_bytes(b"frozen font")

                def snapshot():
                    return {str(p.relative_to(project)): (p.stat().st_mtime_ns, p.read_bytes() if p.is_file() else None)
                            for p in [project, *project.rglob("*")]}

                before = snapshot()
                with mock.patch.object(family, "load_family") as load, \
                        mock.patch.object(family, "build_fonts") as fonts, \
                        mock.patch.object(family, "write_new") as write:
                    family.init("folio", str(project), "new title", ["en"], "translate")
                load.assert_not_called()
                fonts.assert_not_called()
                write.assert_not_called()
                self.assertEqual(snapshot(), before)


if __name__ == "__main__":
    unittest.main(verbosity=2)
