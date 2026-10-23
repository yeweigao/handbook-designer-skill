#!/usr/bin/env python3
"""Build compact variable-font subsets used only by the Folio browser showcase."""
import json
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[2]
SHOWCASE = ROOT / "dev" / "folio-css"
SOURCES = ROOT / "dev" / "fonts"
FONTS = SHOWCASE / "fonts"
FONT_SOURCES = {
    "NotoSansSC-demo.woff2": "NotoSansSC-VF.ttf",
    "NotoSerifSC-demo.woff2": "NotoSerifSC-VF.ttf",
    "Inter-demo.woff2": "Inter-VF.ttf",
}


def showcase_text():
    text = (SHOWCASE / "index.html").read_text(encoding="utf-8")
    for name in ("catalog.json", "business-recipes.json", "chart-examples.json", "swiss-recipes.json", "system-recipes.json"):
        text += json.dumps(json.loads((SHOWCASE / name).read_text(encoding="utf-8")), ensure_ascii=False)
    return text + "AaBbCc0123456789 ·—–：；，。！？“”‘’（）《》【】%￥$↑↓←→×÷±≈≤≥"


def build_one(source, destination, text):
    font = TTFont(SOURCES / source)
    options = subset.Options()
    options.flavor = "woff2"
    options.layout_features = ["*"]
    options.name_IDs = ["*"]
    options.name_languages = ["*"]
    options.notdef_outline = True
    options.hinting = False
    subsetter = subset.Subsetter(options=options)
    cmap = font.getBestCmap() or {}
    subsetter.populate(unicodes=sorted({ord(char) for char in text if ord(char) in cmap}))
    subsetter.subset(font)
    font.save(destination)


def main():
    FONTS.mkdir(exist_ok=True)
    text = showcase_text()
    for output, source in FONT_SOURCES.items():
        path = FONTS / output
        build_one(source, path, text)
        print(f"Built {path.relative_to(ROOT)} ({path.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
