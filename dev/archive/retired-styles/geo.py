#!/usr/bin/env python3
"""geo.py —— 孟菲斯 / 几何拼块：book.style: geo。版式是 8 个内容版式（canon.py），拼块只在页边，正文区永远干净。
  封面、封底（无图）：底边一条拼块带（各列高低不一），文字整体让到拼块带上方
  章节页：切口一侧下角一团
  其他页：切口页边一列
拼块由网格算出来：一格一个图形（四分之一圆、半圆、同心弧、圆、条纹、三角、星、圆圈组、叶、菱形、锯齿、圆环），偶尔 2×2 的大图形；
颜色取配色的主色、强调色、次强调色和它们的浅色。字只写在纸上，拼块不碰文字。
"""
import math
import random
import canon as C
from palettes import mix

h = C.h


def on(): return C.G.get('STYLE') == 'geo'


def palette():
    T = h.TH_; P = T['PAPER']; A, B, O = T['A'], T['B'], T.get('OCH') or T['G']
    return dict(c=[A, B, O, mix(P, O, .32), mix(P, A, .3), mix(P, B, .18) if B else P], ink=T['INK'], paper=P)


def _motif(rnd, x, y, s, pal, big):
    C_ = pal['c']; pick = lambda ex=(): rnd.choice([c for c in C_ if c not in ex])
    bg = pick(); fg = pick((bg,)); o = rnd.randrange(4); cx, cy = x + s / 2, y + s / 2
    g = f'<rect x="{x}" y="{y}" width="{s}" height="{s}" fill="{bg}"/>'
    kinds = ['donut', 'quarter', 'split', 'arcs'] if big else ['quarter', 'half', 'arcs', 'circle', 'stripes', 'tri', 'star', 'rings', 'leaf', 'diamond', 'saw', 'donut', 'quarter', 'half']
    k = rnd.choice(kinds)
    px, py = [(x, y), (x + s, y), (x + s, y + s), (x, y + s)][o]; dx = 1 if px == x else -1; dy = 1 if py == y else -1
    sw = 1 if dx * dy > 0 else 0
    if k == 'quarter': g += f'<path d="M{px} {py} L{px + dx * s} {py} A{s} {s} 0 0 {sw} {px} {py + dy * s} Z" fill="{fg}"/>'
    elif k == 'half':
        if o % 2 == 0: g += f'<path d="M{x} {cy} A{s / 2} {s / 2} 0 0 {0 if o == 0 else 1} {x + s} {cy} Z" fill="{fg}"/>'
        else: g += f'<path d="M{cx} {y} A{s / 2} {s / 2} 0 0 {0 if o == 1 else 1} {cx} {y + s} Z" fill="{fg}"/>'
    elif k == 'arcs':
        line = pal['paper'] if bg != pal['paper'] else C_[1]
        for i in range(1, 5):
            rr = s * .24 * i; g += f'<path d="M{px + dx * rr} {py} A{rr} {rr} 0 0 {sw} {px} {py + dy * rr}" fill="none" stroke="{line}" stroke-width="{s * .075:.2f}"/>'
    elif k == 'circle':
        g += f'<circle cx="{cx}" cy="{cy}" r="{s * .36:.2f}" fill="{fg}"/>'
        if rnd.random() < .5: g += f'<circle cx="{cx}" cy="{cy}" r="{s * .12:.2f}" fill="{pick((fg,))}"/>'
    elif k == 'stripes':
        w = s / 5; g += ''.join(f'<rect x="{x + i * w:.2f}" y="{y}" width="{w:.2f}" height="{s}" fill="{fg}"/>' for i in range(0, 5, 2))
    elif k == 'tri': g += f'<path d="{["M%s %s L%s %s L%s %s" % (x, y + s, x + s, y + s, x + s, y), "M%s %s L%s %s L%s %s" % (x, y, x, y + s, x + s, y + s)][o % 2]} Z" fill="{fg}"/>'
    elif k == 'star':
        d = ''.join(('M' if i == 0 else 'L') + f'{cx + (s * (.18 if i % 2 else .42)) * math.cos(math.pi * i / 12):.2f} {cy + (s * (.18 if i % 2 else .42)) * math.sin(math.pi * i / 12):.2f}' for i in range(24))
        g += f'<path d="{d}Z" fill="{fg}"/>'
    elif k == 'rings':
        g = f'<rect x="{x}" y="{y}" width="{s}" height="{s}" fill="{pal["paper"]}"/>' + ''.join(
            f'<circle cx="{x + s * (.22 + .28 * i):.2f}" cy="{y + s * (.36 + .3 * j):.2f}" r="{s * .09:.2f}" fill="none" stroke="{pal["ink"]}" stroke-width="{s * .035:.2f}"/>' for i in range(3) for j in range(2))
    elif k == 'leaf': g += f'<path d="M{x + s * .15:.2f} {y + s * .85:.2f} A{s * .75:.2f} {s * .75:.2f} 0 0 1 {x + s * .85:.2f} {y + s * .15:.2f} A{s * .75:.2f} {s * .75:.2f} 0 0 1 {x + s * .15:.2f} {y + s * .85:.2f}Z" fill="{fg}"/>'
    elif k == 'diamond': g += f'<path d="M{cx} {y + s * .12:.2f} L{x + s * .88:.2f} {cy} L{cx} {y + s * .88:.2f} L{x + s * .12:.2f} {cy}Z" fill="{fg}"/>'
    elif k == 'saw': g += f'<path d="{"".join(f"M{x + i * s / 3:.2f} {y + s} L{x + i * s / 3 + s / 6:.2f} {y + s * .45:.2f} L{x + (i + 1) * s / 3:.2f} {y + s}Z" for i in range(3))}" fill="{fg}"/>'
    elif k == 'donut': g += f'<circle cx="{cx}" cy="{cy}" r="{s * .42:.2f}" fill="{fg}"/><circle cx="{cx}" cy="{cy}" r="{s * .22:.2f}" fill="{bg}"/>'
    elif k == 'split':
        a = pick((bg,)); b = pick((bg, a)); q = s * .297
        g += f'<circle cx="{cx}" cy="{cy}" r="{s * .42:.2f}" fill="{a}"/><path d="M{cx - q:.2f} {cy + q:.2f} A{s * .42:.2f} {s * .42:.2f} 0 0 0 {cx + q:.2f} {cy - q:.2f}Z" fill="{b}"/>'
    return g


def band(rnd, cols, rows, heights, top=False):
    """cols×rows 格的拼块区；heights[c] = 第 c 列从底往上（top=True 时从上往下）长几格；有空位时 22% 概率放 2×2 大图形"""
    pal = palette(); occ = [[False] * cols for _ in range(rows)]; out = []
    inside = (lambda c, rw: rw < heights[c]) if top else (lambda c, rw: rw >= rows - heights[c])
    for rw in range(rows):
        for c in range(cols):
            if not inside(c, rw) or occ[rw][c]: continue
            if rnd.random() < .22 and c + 1 < cols and rw + 1 < rows and all(inside(a, b) and not occ[b][a] for a, b in ((c + 1, rw), (c, rw + 1), (c + 1, rw + 1))):
                for a, b in ((c, rw), (c + 1, rw), (c, rw + 1), (c + 1, rw + 1)): occ[b][a] = True
                out.append(_motif(rnd, c, rw, 2, pal, True)); continue
            occ[rw][c] = True; out.append(_motif(rnd, c, rw, 1, pal, False))
    return f'<svg viewBox="0 0 {cols} {rows}" preserveAspectRatio="none" style="display:block;width:100%;height:100%">{"".join(out)}</svg>'


TILE = 8          # 封面拼块带：页宽分 8 格
BAND_ROWS = 3     # 拼块带最高 3 格


def band_line():
    """封面 / 封底的文字下沿：拼块带上方留一行（行号）"""
    t = C.W / TILE; top = C.H - BAND_ROWS * t - C.LH
    return max(C.L(20), int((top - C.TOP) // C.LH))


def corner_line():
    """章节页切口下角那一团拼块（4 × 4 格）上方留一行：文字栈的下沿（行号）"""
    s = C.W / TILE * .75; top = C.H - 4 * s - C.LH
    return max(C.L(20), int((top - C.TOP) // C.LH))


def accents(n, p, r, sf):
    if not on(): return ''
    rnd = random.Random(n * 104729 + 7); outer = 'right' if r else 'left'
    lay = p.get('layout'); t = C.W / TILE
    if lay == 'FULL' and not C.has_photo(p.get('image')) and p.get('index') is None and (n == 1 or p.get('_last')):
        hs = [rnd.randint(1, BAND_ROWS) for _ in range(TILE)]
        return f'<div class="geo-band deco" style="left:0;bottom:0;width:{C.W}px;height:{BAND_ROWS * t:.1f}px">{band(rnd, TILE, BAND_ROWS, hs)}</div>'
    if lay == 'FULL' and not C.has_photo(p.get('image')):   # 章节页：切口下角一团（各列高低不一）
        k = 4; s = t * .75
        hs = sorted([rnd.randint(1, 2), rnd.randint(2, 3), 4, 4], reverse=not r)
        return f'<div class="geo-band deco" style="{outer}:0;bottom:0;width:{k * s:.1f}px;height:{k * s:.1f}px">{band(rnd, k, k, hs)}</div>'
    if sf == 'image': return ''
    w = C.W - (C.xe(6, True) + C.GUT // 2); rows = math.ceil(C.H / w)   # 其他页：切口页边一列（方格 = 页边宽）
    return f'<div class="geo-band deco" style="{outer}:0;top:0;width:{w}px;height:{rows * w}px">{band(rnd, 1, rows, [rows], True)}</div>'
