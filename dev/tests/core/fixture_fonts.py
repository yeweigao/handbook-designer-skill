#!/usr/bin/env python3
"""为测试样例项目生成字体子集：python3 dev/tests/core/fixture_fonts.py <样例项目>…

按样例 project.json 的 fonts[].file 文件名，从 dev/fonts/ 找到对应的完整字体，
只保留样例 HTML、copy/*.json、CSS 中出现的字符（加 ASCII 与常用标点），
写到样例的 assets/fonts/ 下，并复制对应的 OFL 授权文本。
改了样例文字之后重跑本脚本。故意制造缺字的样例在 project.json 外另放说明，不用本脚本。
"""
import glob
import json
import os
import shutil
import sys

from fontTools import subset
from fontTools.ttLib import TTFont

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SOURCES = {
    "NotoSansSC.ttf": ("dev/fonts/NotoSansSC-VF.ttf", "noto-sans-sc-OFL.txt"),
    "NotoSerifSC.ttf": ("dev/fonts/NotoSerifSC-VF.ttf", "noto-serif-sc-OFL.txt"),
    "Inter.ttf": ("dev/fonts/Inter-VF.ttf", "inter-OFL.txt"),
}
LICENSE_DIR = os.path.join(REPO, "dev", "tests", "core", "font-licenses")
EXTRA = "".join(chr(c) for c in range(0x20, 0x7F)) + "，。、；：？！“”‘’（）《》—…·「」【】％ "


def collect_text(proj):
    chunks = []
    for pat in ("*.html", "copy/*.json", "*.css", "lang/*.css"):
        for f in glob.glob(os.path.join(proj, pat)):
            with open(f, encoding="utf-8") as fh:
                chunks.append(fh.read())
    return "".join(chunks) + EXTRA


def main(projects):
    for proj in projects:
        proj = os.path.abspath(proj)
        with open(os.path.join(proj, "project.json"), encoding="utf-8") as f:
            p = json.load(f)
        text = collect_text(proj)
        for font in p["fonts"]:
            name = os.path.basename(font["file"])
            if name not in SOURCES:
                print(f"跳过 {name}：不在 SOURCES 映射里")
                continue
            src, lic = SOURCES[name]
            out = os.path.join(proj, font["file"])
            os.makedirs(os.path.dirname(out), exist_ok=True)
            opts = subset.Options()
            opts.layout_features = ["*"]
            opts.name_IDs = ["*"]
            opts.name_languages = ["*"]
            opts.notdef_outline = True
            opts.hinting = False
            f_in = TTFont(os.path.join(REPO, src))
            sub = subset.Subsetter(options=opts)
            sub.populate(text=text)
            sub.subset(f_in)
            f_in.save(out)
            shutil.copyfile(os.path.join(LICENSE_DIR, lic), os.path.join(os.path.dirname(out), lic))
            print(f"{os.path.relpath(out, REPO)}  {os.path.getsize(out) // 1024} KB")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    main(sys.argv[1:])
