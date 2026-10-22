"""PDF outline hierarchy tests; do not require the optional pikepdf runtime."""
import importlib.util
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

try:
    import pikepdf
except ImportError:
    pikepdf = None


class FakeItem:
    def __init__(self, title, page, destination_type, *, top):
        self.title = title
        self.page = page
        self.destination_type = destination_type
        self.top = top
        self.children = []


class FakeOutline:
    def __init__(self):
        self.root = []

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False


class FakePage:
    MediaBox = (0, 0, 595, 842)


class FakePdf:
    def __init__(self, page_count):
        self.pages = [FakePage() for _ in range(page_count)]
        self.outline = FakeOutline()

    def open_outline(self):
        return self.outline


def load_pdfboxes(pikepdf_api):
    path = Path(__file__).resolve().parents[3] / "hb" / "core" / "pdfboxes.py"
    spec = importlib.util.spec_from_file_location("pdfboxes_under_test", path)
    module = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, {"pikepdf": pikepdf_api}):
        spec.loader.exec_module(module)
    return module


class PdfBoxesTest(unittest.TestCase):
    def test_outline_normalizes_titles_and_builds_nested_siblings(self):
        module = load_pdfboxes(SimpleNamespace(OutlineItem=FakeItem))
        pdf = FakePdf(4)
        module.write_outline(pdf, [
            {"title": "  Chapter   One ", "level": 1, "page": 0},
            {"title": "Section\nOne", "level": 2, "page": 1},
            {"title": "Nested detail", "level": 3, "page": 1},
            {"title": "Section Two", "level": 2, "page": 2},
            {"title": "Chapter Two", "level": 1, "page": 3},
            {"title": "Invalid page", "level": 2, "page": 4},
            {"title": "   ", "level": 2, "page": 1},
        ])

        first, second = pdf.outline.root
        self.assertEqual([first.title, second.title], ["Chapter One", "Chapter Two"])
        self.assertEqual([item.title for item in first.children], ["Section One", "Section Two"])
        self.assertEqual([item.title for item in first.children[0].children], ["Nested detail"])
        self.assertEqual((first.page, first.destination_type, first.top), (0, "XYZ", 842.0))
        self.assertEqual((first.children[0].page, first.children[0].top), (1, 842.0))

    @unittest.skipUnless(pikepdf, "pikepdf is not installed in this environment")
    def test_real_pikepdf_saves_nested_bookmarks(self):
        module = load_pdfboxes(pikepdf)
        pdf = pikepdf.Pdf.new()
        pdf.add_blank_page(page_size=(595, 842))
        pdf.add_blank_page(page_size=(595, 842))
        module.write_outline(pdf, [
            {"title": "Chapter", "level": 1, "page": 0},
            {"title": "Section", "level": 2, "page": 1},
        ])

        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "outline.pdf"
            pdf.save(path)
            with pikepdf.open(path) as saved, saved.open_outline() as outline:
                self.assertEqual(outline.root[0].title, "Chapter")
                self.assertEqual(outline.root[0].children[0].title, "Section")


if __name__ == "__main__":
    unittest.main()
