#!/usr/bin/env python3
"""比较两份 PDF 的逐页栅格：python3 hb/core/compare_pdf.py <a.pdf> <b.pdf> [dpi=50] [容差比例=0]
页数不同或任一页差异像素比例超过容差时退出码 1。输出 JSON：每页差异比例。"""
import glob
import json
import os
import subprocess
import sys
import tempfile

from PIL import Image, ImageChops


def raster(pdf, dpi, out):
    subprocess.run(["pdftoppm", "-r", str(dpi), "-png", pdf, os.path.join(out, "p")], check=True)
    return sorted(glob.glob(os.path.join(out, "p-*.png")))


def main(a, b, dpi=50, tol=0.0):
    with tempfile.TemporaryDirectory() as ta, tempfile.TemporaryDirectory() as tb:
        pa, pb = raster(a, dpi, ta), raster(b, dpi, tb)
        res = {"pages_a": len(pa), "pages_b": len(pb), "diff": []}
        if len(pa) != len(pb):
            print(json.dumps(res))
            return 1
        worst = 0.0
        for x, y in zip(pa, pb):
            ia, ib = Image.open(x).convert("RGB"), Image.open(y).convert("RGB")
            if ia.size != ib.size:
                res["diff"].append(1.0)
                worst = 1.0
                continue
            d = ImageChops.difference(ia, ib).convert("L").point(lambda v: 255 if v > 8 else 0)
            ratio = (d.histogram()[255]) / (ia.width * ia.height)
            res["diff"].append(round(ratio, 6))
            worst = max(worst, ratio)
        res["worst"] = round(worst, 6)
        print(json.dumps(res))
        return 0 if worst <= tol else 1


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 50, float(sys.argv[4]) if len(sys.argv) > 4 else 0.0))
