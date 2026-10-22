#!/usr/bin/env python3
"""文字标（品牌包没有 logo 文件时的替身）：把一行字转成 SVG 路径（不依赖字体，PDF 里是矢量）。
  python3 wordmark.py "Acme Studio" comfortaa brands/acme/logo.svg [--weight 700] [--mark "A"] [--color "#4B3BFF"]
--mark：在字前面加一个圆形字母标（品牌的图形标还没给时的占位）。颜色默认 currentColor（排版时跟着当页的字色走）。
拿到真正的 logo 后直接替换 logo.svg（单色 SVG 最好；彩色的在 brand.yaml 里写 mono: false）。"""
import sys, os
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fonts as F
a = sys.argv[1:]; opt = {}
for k in ('--weight', '--mark', '--color', '--track'):
    if k in a: i = a.index(k); opt[k[2:]] = a[i + 1]; del a[i:i + 2]
if len(a) < 3: sys.exit(__doc__)
text, fid, out = a
p = F.path_of(fid)
if not p:
    F.prefetch_bg([fid])
    for sys_ttf in (
        '/System/Library/Fonts/Supplemental/Arial Rounded Bold.ttf',
        '/System/Library/Fonts/Supplemental/Arial Bold.ttf',
        '/System/Library/Fonts/Supplemental/Georgia Bold.ttf',
        '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
    ):
        if os.path.exists(sys_ttf):
            p = sys_ttf
            break
if not p:
    p = F.fetch(fid, quiet=True) or sys.exit(f'找不到字体 {fid}（python3 hb/fonts.py fetch {fid}）')
t = TTFont(p); loc = {'wght': int(opt.get('weight', 700))} if 'fvar' in t else None
gs = t.getGlyphSet(location=loc) if loc else t.getGlyphSet(); cm = t.getBestCmap(); upm = t['head'].unitsPerEm
cap = (getattr(t['OS/2'], 'sCapHeight', 0) or upm * .7) / upm
S = 100; color = opt.get('color', 'currentColor'); track = float(opt.get('track', 0))
x = 0; paths = []; Y = [S, S]
def bound(g, m):
    bp = BoundsPen(gs); g.draw(TransformPen(bp, m))
    if bp.bounds: Y[0] = min(Y[0], bp.bounds[1]); Y[1] = max(Y[1], bp.bounds[3])
if opt.get('mark'):   # 圆形字母标：直径 = 字高 1.5 倍
    d = cap * S * 1.5; cy = S - cap * S / 2; r = d / 2
    ch = opt['mark']; g = gs[cm[ord(ch)]]; sc = S * .9 / upm
    pen = SVGPathPen(gs); g.draw(TransformPen(pen, (sc, 0, 0, -sc, r - g.width * sc / 2, cy + cap * S * .9 / 2)))
    circ = f'M0 {cy:.1f}a{r:.1f} {r:.1f} 0 1 0 {d:.1f} 0a{r:.1f} {r:.1f} 0 1 0 {-d:.1f} 0Z'   # 字母从圆里镂空（单色，深浅底都能用）
    paths.append(f'<path fill-rule="evenodd" d="{circ}{pen.getCommands()}" fill="{color}"/>')
    x = d + S * .28; Y[0] = min(Y[0], cy - r); Y[1] = max(Y[1], cy + r)
for ch in text:
    if ord(ch) not in cm: x += S * .3; continue
    g = gs[cm[ord(ch)]]; sc = S / upm
    pen = SVGPathPen(gs); g.draw(TransformPen(pen, (sc, 0, 0, -sc, x, S))); bound(g, (sc, 0, 0, -sc, x, S))
    if pen.getCommands(): paths.append(f'<path d="{pen.getCommands()}" fill="{color}"/>')
    x += g.width * sc + S * track
top = Y[0] - 1; hgt = Y[1] - Y[0] + 2
open(out, 'w', encoding='utf-8').write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 {top:.1f} {x:.1f} {hgt:.1f}" width="{x:.1f}" height="{hgt:.1f}">{"".join(paths)}</svg>\n')
print(out, f'{x:.0f}×{hgt:.0f}')
