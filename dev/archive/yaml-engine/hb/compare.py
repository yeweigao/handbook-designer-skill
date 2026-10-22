#!/usr/bin/env python3
"""多语言逐页对照图：python3 compare.py <project> zh en → <project>/.qa/compare_N_<时间>.jpg（每行一页，各语言并排；每张 6 行）"""
import sys, os, glob, time
from PIL import Image, ImageDraw
P = os.path.abspath(sys.argv[1]); L = sys.argv[2:]; Q = os.path.join(P, '.qa'); os.makedirs(Q, exist_ok=True)
for f in glob.glob(os.path.join(Q, 'compare_*.jpg')): os.remove(f)
pages = [sorted(glob.glob(os.path.join(P, l, '.qa', 'pg*.png')), key=lambda f: int(os.path.basename(f)[2:-4])) for l in L]
n = max(len(p) for p in pages); w = 397; h = round(w * Image.open(pages[0][0]).height / Image.open(pages[0][0]).width) if pages[0] else 561; g = 16; per = 6; ts = time.strftime('%H%M%S')
for k in range(0, n, per):
    rows = range(k, min(n, k + per))
    c = Image.new('RGB', (len(L) * (w + g) + g + 36, len(rows) * (h + g) + g + 24), '#3a3a3a'); d = ImageDraw.Draw(c)
    for j, l in enumerate(L): d.text((36 + g + j * (w + g), 6), l, fill='#ddd')
    for r_, i in enumerate(rows):
        d.text((8, 24 + g + r_ * (h + g)), f'p{i + 1}', fill='#ddd')
        for j in range(len(L)):
            if i < len(pages[j]): c.paste(Image.open(pages[j][i]).convert('RGB').resize((w, h), Image.LANCZOS), (36 + g + j * (w + g), 24 + g + r_ * (h + g)))
    c.save(os.path.join(Q, f'compare_{k // per + 1}_{ts}.jpg'), quality=85)
print('ok')
