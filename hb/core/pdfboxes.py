#!/usr/bin/env python3
"""把 Chrome 导出的 PDF 裁成精确物理尺寸并写入页面框：
python3 hb/core/pdfboxes.py <pdf> <媒体宽mm> <媒体高mm> <出血mm>

Chrome 只能输出 1/75 英寸取整的纸张，导不出精确 A4。渲染器让 Chrome 按稍大的纸张输出，
内容从左上角开始；这里把每页 MediaBox 裁到左上角的精确媒体区域（不缩放内容），
CropBox = BleedBox = MediaBox，TrimBox = MediaBox 向内收出血。原地改写。
"""
import sys

import pikepdf

MM = 72 / 25.4


def main(path, media_w, media_h, bleed):
    W, H, B = media_w * MM, media_h * MM, bleed * MM
    with pikepdf.open(path, allow_overwriting_input=True) as pdf:
        for page in pdf.pages:
            x0, y0, x1, y1 = [float(v) for v in page.MediaBox]
            if x1 - x0 + 0.01 < W or y1 - y0 + 0.01 < H:
                print(f"PDF 页面 {x1 - x0:.2f}×{y1 - y0:.2f}pt 小于目标 {W:.2f}×{H:.2f}pt", file=sys.stderr)
                return 1
            media = pikepdf.Array([x0, y1 - H, x0 + W, y1])
            page.MediaBox = media
            page.CropBox = media
            page.BleedBox = media
            page.TrimBox = pikepdf.Array([x0 + B, y1 - H + B, x0 + W - B, y1 - B])
        pdf.save(path)
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4])))
