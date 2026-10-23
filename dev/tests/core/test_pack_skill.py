"""The distributed skill must work as a reference bundle without its dev tree."""
import importlib.util
import json
from pathlib import Path
import re
import tempfile
import unittest
from unittest.mock import patch
from urllib.parse import unquote, urlsplit
import zipfile


ROOT = Path(__file__).resolve().parents[3]
SPEC = importlib.util.spec_from_file_location("pack_skill", ROOT / "hb/core/pack_skill.py")
pack = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(pack)


class SkillPackageTests(unittest.TestCase):
    def test_default_archive_is_self_contained_without_dev(self):
        with tempfile.TemporaryDirectory() as directory:
            destination = str(Path(directory) / "skill.zip")
            pack.build(destination, quiet=True)
            with zipfile.ZipFile(destination) as archive:
                archive.extractall(directory)
            skill = Path(directory) / pack.ROOT_NAME
            self.assertFalse((skill / "dev").exists())
            self.assertFalse((skill / "docs").exists())
            self.assertTrue((skill / "families/folio/folio.css").is_file())
            self.assertFalse((skill / "families/folio/design.css").exists())
            for relative in pack.REQUIRED_FILES:
                self.assertTrue((skill / relative).is_file(), relative)
            # Every local documentation link in the normal-use package resolves
            # after extraction; remote maintenance references are allowed.
            for source in skill.rglob("*.md"):
                text = re.sub(r"```.*?```", "", source.read_text(encoding="utf-8"), flags=re.S)
                for link in re.findall(r"\]\(([^)]+)\)", text):
                    url = urlsplit(link.strip("<>"))
                    if url.scheme or not url.path:
                        continue
                    target = (source.parent / unquote(url.path)).resolve()
                    self.assertTrue(target.is_relative_to(skill.resolve()), f"{source}: {link}")
                    self.assertTrue(target.exists(), f"{source.relative_to(skill)}: {link}")

    def test_required_untracked_outputs_are_included_without_other_untracked_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for relative in pack.REQUIRED_FILES:
                target = root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text("fixture", encoding="utf-8")
            extra = root / "families/folio/private-notes.txt"
            extra.write_text("not a release artifact", encoding="utf-8")
            with patch.object(pack, "ROOT", directory), patch.object(pack, "tracked_files", return_value=[]):
                self.assertEqual(set(pack.selected()), set(pack.REQUIRED_FILES))
                (root / "families/folio/recipes.json").unlink()
                with self.assertRaisesRegex(SystemExit, "recipes.json"):
                    pack.selected()

    def test_samples_are_only_an_explicit_option(self):
        paths = ["dev/samples/native/folio-swiss/book.html", "dev/folio-css/index.html"]
        with patch.object(pack, "tracked_files", return_value=paths):
            self.assertFalse(any(path.startswith("dev/") for path in pack.selected()))
            optional = pack.selected(with_samples=True)
            self.assertIn(paths[0], optional)
            self.assertNotIn(paths[1], optional)

    def test_production_recipes_match_showcase_without_developer_locations(self):
        production = json.loads((ROOT / "families/folio/recipes.json").read_text())
        raw = (ROOT / "dev/folio-css/catalog.js").read_text().split("window.FOLIO_CATALOG = ", 1)[1]
        showcase = json.loads(raw.strip().removesuffix(";"))
        self.assertEqual(production["coverage"], showcase["coverage"])
        groups = ("atoms", "layouts", "components", "expressions")
        self.assertEqual(sum(len(production[group]) for group in groups), production["coverage"]["entries"])
        for group in groups:
            self.assertEqual([item["id"] for item in production[group]],
                             [item["id"] for item in showcase[group]])
            for recipe in production[group]:
                self.assertNotIn("specimenPage", recipe)
                self.assertNotIn("dev/", json.dumps(recipe))
                self.assertNotIn("../samples/", recipe["html"])
                for source in re.findall(r'(?:src="|url\()([^"\)]+)', recipe["html"]):
                    self.assertTrue(source.startswith("assets/images/"), f"{recipe['id']}: {source}")


if __name__ == "__main__":
    unittest.main()
