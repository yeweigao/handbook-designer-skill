#!/usr/bin/env python3
"""把最终 PDF 栅格化供视觉审稿（S4）：python3 hb/core/rasterize.py <项目> <构建 ID> <语言>

输出到 .qa/<构建 ID>/<语言>/raster/：
  page-NNN.png  逐页（含出血，110dpi，阅读尺度目检）
  sheet.png     整册缩略图（按成品裁切，标页码）
  spreads.png   面对页拼图（按成品裁切、左右页贴合，看中缝与跨页连续）
左右页由 project.json 的 first_page 推出。缺少 pdftoppm 时退出码 1。
"""
import glob
import json
import os
import shutil
import subprocess
import sys

from PIL import Image, ImageDraw

DPI = 110


def main(project, build, lang):
    project = os.path.abspath(project)
    with open(os.path.join(project, "project.json"), encoding="utf-8") as fh:
        proj = json.load(fh)
    pdf = os.path.join(project, ".build", build, lang, "book.pdf")
    out = os.path.join(project, ".qa", build, lang, "raster")
    if not shutil.which("pdftoppm"):
        print("缺少 pdftoppm（poppler），无法栅格化最终 PDF 供审稿")
        return 1
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(out)
    subprocess.run(["pdftoppm", "-r", str(DPI), "-png", pdf, os.path.join(out, "page")], check=True)
    files = sorted(glob.glob(os.path.join(out, "page-*.png")))
    for i, f in enumerate(files, 1):  # 统一命名 page-001.png
        os.rename(f, os.path.join(out, f"page-{i:03d}.png"))
    files = sorted(glob.glob(os.path.join(out, "page-*.png")))
    bleed_px = round(proj["canvas"]["bleed_mm"] / 25.4 * DPI)
    trimmed = []
    for f in files:
        im = Image.open(f).convert("RGB")
        trimmed.append(im.crop((bleed_px, bleed_px, im.width - bleed_px, im.height - bleed_px)) if bleed_px else im)

    # 整册缩略图
    tw = 180
    th = round(trimmed[0].height * tw / trimmed[0].width)
    cols = 6
    rows = (len(trimmed) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (tw + 16) + 16, rows * (th + 34) + 16), (200, 200, 200))
    d = ImageDraw.Draw(sheet)
    for i, im in enumerate(trimmed):
        x, y = 16 + (i % cols) * (tw + 16), 16 + (i // cols) * (th + 34)
        sheet.paste(im.resize((tw, th)), (x, y))
        d.text((x, y + th + 4), str(i + 1), fill=(40, 40, 40))
    sheet.save(os.path.join(out, "sheet.png"))

    # 面对页
    right_first = proj.get("first_page", "right") == "right"
    pairs, i = [], 0
    if right_first:
        pairs.append((None, 0))
        i = 1
    while i < len(trimmed):
        pairs.append((i, i + 1 if i + 1 < len(trimmed) else None))
        i += 2
    sw = 300
    sh = round(trimmed[0].height * sw / trimmed[0].width)
    spreads = Image.new("RGB", (2 * sw + 32, len(pairs) * (sh + 34) + 16), (200, 200, 200))
    d = ImageDraw.Draw(spreads)
    for r, (left, right) in enumerate(pairs):
        y = 16 + r * (sh + 34)
        for side, idx in ((0, left), (1, right)):
            if idx is None:
                continue
            spreads.paste(trimmed[idx].resize((sw, sh)), (16 + side * sw, y))
            d.text((16 + side * sw + 4, y + sh + 4), str(idx + 1), fill=(40, 40, 40))
    spreads.save(os.path.join(out, "spreads.png"))
    print(f"栅格 {lang}：{len(files)} 页 → {os.path.relpath(out, project)}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(*sys.argv[1:]))
