#!/usr/bin/env python3
"""生成测试样例用的合成图片（几何回归用，不是照片）：python3 dev/tests/core/make_fixture_images.py"""
import os
from PIL import Image, ImageDraw

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))


def band(path, w_mm, h_mm, dpi=300):
    w, h = round(w_mm / 25.4 * dpi), round(h_mm / 25.4 * dpi)
    img = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(img)
    for x in range(w):
        t = x / (w - 1)
        d.line([(x, 0), (x, h)], fill=(int(20 + 40 * t), int(70 + 90 * t), int(140 + 60 * (1 - t))))
    for i in range(9):
        cx = int(w * (i + 0.5) / 9)
        d.ellipse([cx - h // 6, h // 3, cx + h // 6, h // 3 + h // 3], outline=(242, 183, 5), width=max(4, h // 120))
    d.line([(w // 2, 0), (w // 2, h)], fill=(255, 255, 255), width=max(2, h // 400))  # 中缝参照线
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path, quality=86, optimize=True)
    print(os.path.relpath(path, REPO), img.size)


if __name__ == "__main__":
    # 跨页图：两页成品宽 + 两侧出血，高 = 上出血 + 150mm
    band(os.path.join(REPO, "dev/fixtures/contract/bilingual/assets/images/campus.jpg"), 2 * 210 + 2 * 3, 3 + 150)
