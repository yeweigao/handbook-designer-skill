#!/usr/bin/env python3
"""canon.py —— 基础内容版式与编辑变奏共用的网格。由 hb.py 调用，yaml 写法见 references/layouts.md。

一、网格：所有尺寸都从正文字号推出来
  A4 = 794 × 1123（1:√2）。正文 16px（印出来 12pt，小四），行距 28px。
  一栏 = 5 个字 = 80px，栏间 = 2 个字 = 32px，6 栏 = 40 个字 = 640px；版心 32 行 = 896px ≈ √2 × 640。
  页边：订口 50、切口 104（单页订口在左、双页在右），天头 88，页码在第 33 行。
  book.body: 14 → 旧的紧凑网格（正文 14px / 行距 24，一栏 6 字 = 84，栏间 28，38 行），给字多的练习册、长文；A5、小红书画布一直用 14px。
  字号（16px 网格）：13 · 16 · 23 · 33 · 47 · 56 · 80 · 112 · 160；小字号按行距等比（S = 行距 / 24）。大标题在浏览器里量字宽，撑满给定的栏宽。
二、文字栈 + 吸收体（同一套版式排中文、英文都不出问题的关键）
  文字不写死在第几行，而是一组按行距流动的块（文字栈 .cn-st），钉在版心上沿或下沿，或者跟在另一个文字栈后面。
  照片和色块是“吸收体”：边界写成相对文字栈的位置（data-y0 / data-y1，如 p3_b.top-2 = 正文栈上方 2 行），
  中文短、英文长，变的只是照片和色块的大小。所有边落在行线上（fill.js 补齐）。
  浏览器里自检：文字出版心、出色块、文字互压、照片被挤得太小 → body.dataset.cnqa → shot.js → doctor.py。
"""
import os, re, json, hashlib
from palettes import contrast, lum, on as _on

G = None
class _P:
    def __getattr__(self, k): return G[k]
h = _P()
def init(g):
    global G; G = g

# ---------------------------------------------------------------- 网格
W, H = 794, 1123
COL, GUT, LH, TOP, IN, OUT, LAST, BS = 80, 32, 28, 88, 50, 104, 32, 16
S = LH / 24   # 小字号、间距相对旧网格（行距 24）的比例
K = 1.0   # 画布相对 A4 的缩放（装饰大字、固定行号按它缩）
CANVAS = {'a4': (794, 1123, 80, 32, 88, 50, 104, 32, 28, 16),
          'a4-14': (794, 1123, 84, 28, 88, 50, 100, 38, 24, 14),
          'a5': (559, 794, 56, 24, 64, 36, 67, 28, 24, 14),
          'xhs': (600, 800, 64, 24, 64, 48, 48, 28, 24, 14)}
def setup(name, body=None):
    global W, H, COL, GUT, TOP, IN, OUT, LAST, LH, BS, S, K
    if name not in CANVAS or name == 'a4-14': raise SystemExit(f'ERROR: book.canvas 可选 a4 / a5 / xhs，当前 {name}')
    if body not in (None, 14, 16): raise SystemExit(f'ERROR: book.body 只能写 16（默认）或 14，当前 {body}')
    key = 'a4-14' if name == 'a4' and body == 14 else name
    if name != 'a4' and body == 16: print(f'提示：{name} 画布的正文固定 14px（页面小），book.body: 16 只对 A4 有效')
    W, H, COL, GUT, TOP, IN, OUT, LAST, LH, BS = CANVAS[key]; S = LH / 24; K = W / 794
    return W, H
def L(n): return round(n * LAST / 38)
def nrows(px, d=18, lo=2, hi=40):
    try: v = float(px) if px is not None else d * LH
    except (TypeError, ValueError): v = d * LH
    return max(lo, min(hi, round(v / LH)))
def left(r): return IN if r else OUT
def x(c, r): return left(r) + (c - 1) * (COL + GUT)
def xe(c, r): return x(c, r) + COL
def wd(c0, c1): return (c1 - c0 + 1) * (COL + GUT) - GUT
def y(l): return TOP + l * LH
def gc(c, r): return xe(c, r) + GUT // 2
def side_cols(r, inner=True):
    return (1, 3) if (r == inner) else (4, 6)

# ---------------------------------------------------------------- 颜色
def rgba(c, a):
    c = c.lstrip('#'); return f'rgba({int(c[0:2], 16)},{int(c[2:4], 16)},{int(c[4:6], 16)},{a})'
def MODE(): return G.get('COLOR_MODE', 'clash')
def QUIET(): return G.get('STYLE') in ('swiss', 'stijl') and MODE() == 'mono'
def NOART(): return QUIET() or G.get('STYLE') in ('editorial', 'stijl')
def BW(): return QUIET() and G.get('STYLE') == 'swiss' or G.get('STYLE') == 'stijl'
def tokens(sf):
    if sf in ('D', 'S', 'X') and G.get('STYLE') == 'stijl':
        import stijl; return stijl.tok(sf)
    T = h.TH_; A, B, P, INK = T['A'], T['B'], T['PAPER'], T['INK']
    if sf == 'dark':
        bg = INK; fg = max(('#FFFFFF', '#000000'), key=lambda c: contrast(c, bg))
        return dict(bg=bg, fg=fg, hd=fg, acc=fg, num=fg, lab=fg, mut=rgba(fg, .84), rule=fg, line=rgba(fg, .38))
    if QUIET() and sf in ('paper', 'B'):
        bg = T['TINT'] if sf == 'B' else P
        return dict(bg=bg, fg=INK, hd=INK, acc=A if contrast(A, bg) >= 4.5 else INK, num=A if contrast(A, bg) >= 3 else INK, lab=INK, mut=T['MUT'], rule=INK, line=rgba(INK, .3))
    if MODE() != 'clash' and sf in ('paper', 'A', 'B'):
        if sf == 'A':
            bg = A; fg = '#FFFFFF' if contrast('#FFFFFF', A) >= 4.5 else '#000000'
            return dict(bg=bg, fg=fg, hd=fg, acc=fg, num=fg, lab=fg, mut=rgba(fg, .84), rule=fg, line=rgba(fg, .38))
        bg = T.get('TINT') or (P if sf == 'paper' else _mix(P, A, .07)) if sf == 'B' else P
        acc = A if contrast(A, bg) >= 5 else _on5(bg, T['G'], T['OCH'], INK)
        return dict(bg=bg, fg=INK, hd=A if contrast(A, bg) >= 3 else INK, acc=acc, num=A if contrast(A, bg) >= 3 else acc, lab=acc, mut=T['MUT'], rule=INK, line=rgba(INK, .22))
    if sf in ('A', 'B'):
        bg, other = (A, B) if sf == 'A' else (B, A)
        fg = _on5(bg, other, '#FFFFFF', INK, P)
        hd = other if contrast(other, bg) >= 4.5 else fg
        sm = other if contrast(other, bg) >= 5 else fg
        return dict(bg=bg, fg=fg, hd=hd, acc=sm, num=hd, lab=sm, mut=rgba(fg, .86) if contrast(fg, bg) >= 9 else fg, rule=fg, line=rgba(fg, .38))
    if sf == 'image' and is_light_art():
        return dict(bg=P, fg=INK, hd=INK, acc=INK, num=A if contrast(A, P) >= 3 else INK, lab=INK, mut=T['MUT'], rule=INK, line=rgba(INK, .3))
    if sf == 'image':
        lt = max((A, B), key=lum); lt = lt if lum(lt) > .6 and MODE() == 'clash' else '#FFFFFF'
        acc = '#FFFFFF'
        if G.get('STYLE') == 'photo' and T.get('GOLD') and lum(T['GOLD']) > .4: lt = acc = T['GOLD']
        return dict(bg='#111111', fg='#FFFFFF', hd='#FFFFFF', acc=acc, num=lt, lab='#FFFFFF', mut='rgba(255,255,255,.88)', rule='#FFFFFF', line='rgba(255,255,255,.45)')
    acc = A if contrast(A, P) >= 5 else _on5(P, T['G'], T['OCH'], INK)
    return dict(bg=P, fg=INK, hd=acc, acc=acc, num=A if contrast(A, P) >= 3.2 else acc, lab=acc, mut=T['MUT'], rule=INK, line=rgba(INK, .22))
def _mix(a, b, t):
    from palettes import mix
    return mix(a, b, t)
def _on5(bg, *cands):
    for c in cands:
        if contrast(c, bg) >= 5: return c
    return max(cands, key=lambda c: contrast(c, bg))
LIGHT_ART = [False]
def is_light_art(): return LIGHT_ART[0]
def vs(sf): return ''.join(f'--{k}:{v};' for k, v in tokens(sf).items() if k != 'bg')
def other(sf): return 'B' if sf == 'A' else 'A'

# ---------------------------------------------------------------- 底色节奏
SURF_ALIAS = {'a': 'A', 'brand': 'A', 'split': 'A', 'ink': 'A', 'b': 'B', 'pop': 'B', 'paper': 'paper', 'tint': 'paper', 'dark': 'dark', 'image': 'image', 'photo': 'image'}
ST = dict(prev=None, last='B', count={}, run=0)
def choose(lay, p, variants):
    k = ST['count'].get(lay, 0); ST['count'][lay] = k + 1
    want = SURF_ALIAS.get(str(p.get('surface', '')).strip().lower())
    if want:
        for v in variants:
            if v[1] == want: return v[0], v[1]
    if QUIET():
        variants = list(dict.fromkeys((n, 'paper' if d == 'A' else d) for n, d in variants))
    elif MODE() != 'clash' and lay != 'FULL':
        variants = list(dict.fromkeys((n, 'B' if d == 'A' else d) for n, d in variants))
    if p.get('surface') and not want: h.WARN.append(f'第{h.CURN}页：surface 只能写 paper / A / B / dark / image（或旧写法 brand / pop / split / tint），已忽略 {p["surface"]}')
    if want:
        for v in variants:
            if v[1] == want: return v[0], v[1]
        h.WARN.append(f'第{h.CURN}页 {lay}：这一页没有 surface: {p["surface"]} 的排法，按自动轮换来')
    rot = variants[k % len(variants):] + variants[:k % len(variants)]
    calm = 4 if ST['run'] >= 2 else 0
    best = max(enumerate(rot), key=lambda iv: (3 if iv[1][1] != ST['prev'] else 0) + (1 if iv[1][1] in ('A', 'B') and iv[1][1] != ST['last'] else 0)
               + (calm if iv[1][1] not in ('A', 'B') else 0) - iv[0] * .1)
    return best[1]
def used(dom):
    ST['prev'] = dom; ST['run'] = ST['run'] + 1 if dom in ('A', 'B') else 0
    if dom in ('A', 'B'): ST['last'] = dom
def field_color():
    return 'B' if MODE() != 'clash' else other(ST['last'])

# ---------------------------------------------------------------- 文字
def T_(s): return re.sub(r'\*\*(.+?)\*\*', r'<b class="cn-hl">\1</b>', h.esc(str(s))).replace('\n', '<br>')
def sid(n, k): return f'p{n}_{k}'
def stack(c0, c1, r, kids, top=None, bot=None, id_='', sf='paper', y0=None, y1=None, gold=None, inside=None, cls='', style='', free=False, floor=None):
    pos = f'top:{y(top)}px;' if top is not None else f'bottom:{H - y(bot)}px;' if bot is not None else f'top:{TOP}px;'
    a = (f' id="{id_}"' if id_ else '') + f' data-anchor="{"bottom" if bot is not None and top is None else "top"}"'
    for k, v in (('y0', y0), ('y1', y1), ('gold', gold), ('in', inside)):
        if v is not None: a += f' data-{k}="{v}"'
    if free: a += ' data-free="1"'
    if floor is not None: a += f' data-floor="{floor}"'
    return f'<div class="cn-a cn-st {cls}"{a} style="left:{x(c0, r)}px;width:{wd(c0, c1)}px;{pos}{vs(sf)}{style}">{"".join(k for k in kids if k)}</div>'
def W_(cols): return f'width:{wd(1, cols)}px;' if cols else ''
def lab(t, m=0, deco=True): return f'<div class="cn-lab m{m}"{h.DECO if deco else ""}>{T_(t)}</div>' if t else ''
def disp(t, mx=112, cols=None, mn=None, m=0, lines=3, cls='', style=''):
    a = f' data-fit="{mx}"' + (f' data-min="{mn}"' if mn else '') + (f' data-lines="{lines}"' if lines != 3 else '')
    tt = T_(t)
    for ch in ('·', '，', '、', '：'):
        tt = tt.replace(ch, ch + '\u200b')
    return f'<div class="cn-disp m{m} {cls}"{a} style="{W_(cols)}{style}">{tt}</div>' if t else ''
def sub(t, m=0, cols=None): return f'<div class="cn-sub cn-snap m{m}" style="{W_(cols)}">{T_(t)}</div>' if t else ''
def reading(flow):
    if flow not in (None, 'auto', 'keep', 'columns'): raise ValueError('flow 可选 auto / keep / columns')
    return f' data-reading="{flow}"' if flow else ''
def para(t, cls='', m=0, cols=None, style='', flow=None):
    if t in (None, '', []): return ''
    if isinstance(t, list): inner = ''.join(f'<p>{T_(s)}</p>' for s in t)
    else: inner = f'<p>{T_(t)}</p>'
    return f'<div class="cn-tx {cls} m{m}"{reading(flow)} style="{W_(cols)}{style}">{inner}</div>'
def lead(t, m=0, cols=None): return para(t, 'cn-t20 cn-snap', m, cols, flow='keep')
def bullets(xs, m=0, style='plain'):
    return f'<ul class="cn-li cn-list-{style} cn-tx m{m}">' + ''.join(f'<li>{T_(s)}</li>' for s in xs) + '</ul>' if xs else ''
def TX(v, m=0):
    if v in (None, '', []): return ''
    return bullets(v, m, style='plain') if isinstance(v, list) else para(v, m=m)
def num(t, size=56, lh=None, cls='', deco=True, style=''):
    lh = lh or (size + 16 if size <= 80 else size)
    if size < 24: style = 'color:var(--acc);' + style
    return f'<div class="cn-num {cls}"{h.DECO if deco else ""} style="font-size:{size}px;line-height:{lh}px;{style}">{T_(t)}</div>'
def head(p, mx=112, cols=None, mn=None, intro=True, icols=None, lines=3):
    k = [lab(p.get('kicker')), disp(p.get('title'), mx, cols, mn, lines=lines), sub(p.get('en') or p.get('sub'), cols=cols)]
    if intro and p.get('intro'): k.append(lead(p['intro'], 1, icols or cols))
    return k
def stats_row(st, cols=6, size=36, m=1):
    if not st: return ''
    st = [s if isinstance(s, (list, tuple)) else [s, ''] for s in st][:4]
    def _sz(a):
        ln = len(str(a))
        return min(size, 36 if ln <= 4 else 28 if ln <= 6 else 22)
    cells = ''.join(f'<div style="min-width:0;overflow:hidden">{num(a, _sz(a), _sz(a) + 6, deco=False)}<div class="cn-cap" style="margin-top:4px">{T_(b)}</div></div>' for a, b in st)
    return f'<div class="cn-stats cn-snap m{m}" style="{W_(cols)}grid-template-columns:repeat({len(st)},minmax(0,1fr))">{cells}</div>'
def quote(q, by=None, m=0):
    if not q: return ''
    return (f'<div class="cn-q m{m}"><div class="cn-qt cn-snap">{T_(q)}</div>' + (f'<div class="cn-lab m1" style="color:var(--mut)">— {T_(by)}</div>' if by else '') + '</div>')
def listify(v): return [] if v is None else v if isinstance(v, list) else [v]
def IT(c):
    if isinstance(c, dict): return c
    if isinstance(c, (list, tuple)):
        if len(c) >= 3 and isinstance(c[2], str) and c[2] and not re.search(r'\.(jpe?g|png|webp|svg)$|^(ai:|placeholder)', c[2], re.I):
            raise ValueError(f'[{", ".join(map(str, c))[:40]}…] 被拆成了 {len(c)} 段——文字里的英文逗号（如 5,000+）把它拆开了 → 给这段文字加引号：\'…5,000+…\'')
        return dict(zip(('t', 'x', 'img'), c))
    return dict(t=c)
def chars(v):
    if isinstance(v, dict): return sum(chars(x) for k, x in v.items() if k not in ('img', 'focus', 'src'))
    if isinstance(v, (list, tuple)): return sum(chars(x) for x in v)
    s = str(v) if v is not None else ''; return sum(1 if ord(ch) > 0x2e80 else .5 for ch in s)

# ---------------------------------------------------------------- 框：照片、色块
def box(x0, y0, x1, y1, inner='', cls='', style='', y0r=None, y1r=None, minh=None, attr='', id_=''):
    a = (f' id="{id_}"' if id_ else '') + (f' data-y0="{y0r}"' if y0r is not None else '') + (f' data-y1="{y1r}"' if y1r is not None else '') + (f' data-minh="{minh}"' if minh else '') + attr
    return f'<div class="cn-a {cls}"{a} style="left:{x0}px;top:{y0}px;width:{x1 - x0}px;height:{max(0, y1 - y0)}px;{style}">{inner}</div>'
def field(x0, y0, x1, y1, sf, **k): return box(x0, y0, x1, y1, '', 'cn-field ' + k.pop('cls', ''), f'background:{tokens(sf)["bg"]};', **k)

_STATS = {}
def weak(path):
    try:
        key = (path, os.path.getmtime(path))
        if key in _STATS: return _STATS[key]
        import numpy as np
        from PIL import Image
        im = Image.open(path).convert('RGB'); im.thumbnail((360, 360)); a = np.asarray(im).astype('float32') / 255
        L = .2126 * a[..., 0] + .7152 * a[..., 1] + .0722 * a[..., 2]; mx, mn = a.max(-1), a.min(-1)
        sat = (mx - mn) / np.maximum(mx, 1e-3); r = float(((L > .78) & (sat < .12)).mean()) >= .3
        _STATS[key] = r; return r
    except Exception: return False
def duotone(rel_src):
    T = h.TH_; dark, light = sorted((T['A'], T['B']), key=lum)
    if lum(dark) > .12: dark = T['INK']
    if BW(): dark, light = T['INK'], T['PAPER']
    s = os.path.join(h.PROJ, rel_src)
    key = hashlib.md5(f'{rel_src}{os.path.getmtime(s)}{dark}{light}'.encode()).hexdigest()[:10]
    out = os.path.join(h.PROJ, 'img', f'duo_{key}.jpg')
    if not os.path.exists(out):
        from PIL import Image, ImageOps
        c = lambda v: tuple(int(v.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4))
        im = ImageOps.autocontrast(Image.open(s).convert('L'), cutoff=1.5).point(lambda v: int(255 * (v / 255) ** 1.08))
        ImageOps.colorize(im, c(dark), c(light)).save(out, quality=90)
    return f'img/duo_{key}.jpg'
PHWARN = set()
def pic(v, w, hgt, idx=1, sf='A', label=True):
    duo = None
    fit = v.get('fit', 'cover') if isinstance(v, dict) else 'cover'
    if isinstance(v, dict): f, (fx, fy), duo = v.get('src'), tuple(v.get('focus', [.5, .5])), v.get('duo')
    else: f, (fx, fy) = v, (.5, .5)
    if f and str(f).startswith('ai:'):
        f = h.AIFIG(f, w, hgt, '版式图位')
    if f and not h.is_art(f):
        rel = h.FIGIMG(f, w * 1.5)
        if not rel: return ''
        mode = str(h.BK.get('duotone', 'all' if BW() else 'auto')).lower()
        if rel.endswith(('.jpg', '.jpeg', '.png')) and (duo is True or (duo is None and (mode == 'all' or (mode == 'auto' and weak(os.path.join(h.PROJ, rel)))))):
            rel = duotone(rel)
            if h.USE: h.USE[-1]['img'] = rel.split('/')[-1]; h.USE[-1]['duo'] = True
        return f'<img class="cn-img" alt="" src="{rel}" style="object-fit:{fit};object-position:{fx * 100:.0f}% {fy * 100:.0f}%">'
    if h.STYLE != 'photo' and not NOART():
        d = os.path.join(h.PROJ, 'img'); os.makedirs(d, exist_ok=True)
        key = hashlib.md5(repr((h.STYLE, sorted(h.TH_.items()), h.CURN, idx, round(w), round(hgt), os.path.getmtime(h.art.__file__))).encode()).hexdigest()[:10]
        out = os.path.join(d, f'slot_{key}.jpg')
        if not os.path.exists(out):
            h.art.make(h.STYLE, max(240, round(w * 2)), max(200, round(max(hgt, w * .8) * 2)), h.CURN * 31 + idx * 7, h.TH_, (0, 0, 1, .89)).save(out, quality=90)
        return f'<img class="cn-img" alt="" src="img/slot_{key}.jpg" style="object-position:80% 50%">'
    if h.CURN not in PHWARN and not NOART():
        PHWARN.add(h.CURN); h.WARN.append(f'第{h.CURN}页：有图片位没给照片，先排成色块 + 编号（照片到了写进 image / img / images）')
    t = tokens('B' if QUIET() else sf)
    label = label and not NOART()
    return (f'<div class="cn-ph" style="background:{t["bg"]}">' + (f'<span class="cn-num deco"{h.DECO} style="color:{rgba(h.TH_["INK"], .16) if QUIET() else t["num"]};font-size:{min(220, max(64, round(min(w, max(hgt, 120)) * .7)))}px">{idx:02d}</span>' if label else '') + '</div>')
def has_photo(v): return bool(v) and not h.is_art(v if not isinstance(v, dict) else v.get('src'))

def bake_full(n, p, v):
    f, focus = (v.get('src'), v.get('focus', [.5, .5])) if isinstance(v, dict) else (v, p.get('focus', [.5, .5]))
    orig = f
    if f and not h.is_art(f):
        duo = v.get('duo') if isinstance(v, dict) else None
        mode = str(h.BK.get('duotone', 'all' if BW() else 'auto')).lower()
        src = os.path.join(h.SRC, str(f))
        if (str(f).lower().endswith(('.jpg', '.jpeg', '.png')) and
                (duo is True or (duo is None and mode == 'all')) and os.path.exists(src)):
            f = os.path.join(h.PROJ, duotone(os.path.relpath(src, h.PROJ)))
    name = f'p{n:02d}.jpg'
    h.bake(n, name, f if f else 'art', W, lambda X, Y: 0 * X, tuple(focus), p.get('target', [W / 2, H / 2]), p.get('zoom', 1.0), 'single', False, p.get('_artbox', (0, 0, 1, 1)))
    if f != orig and h.USE:
        h.USE[-1]['duo'] = True
        h.USE[-1]['file'] = str(orig)
    return name, h.IMGTAG(name)

# ---------------------------------------------------------------- 页
def folio(n, r, sf='paper', span=(1, 6), label=None):
    t = tokens(sf); lb = h.esc(label if label is not None else h.FOLIO)
    a, b = (f'<span>{lb}</span>', f'<span class="cn-num" style="font-size:{BS}px;line-height:{LH}px;color:{t["mut"]}">{n:02d}</span>')
    if not r: a, b = b, a
    return f'<div class="cn-a cn-fo"{h.DECO} style="left:{x(span[0], r)}px;width:{wd(*span)}px;top:{y(LAST + 1)}px;color:{t["mut"]}">{a}{b}</div>'
def running(p, r, sf='paper', span=(1, 6)):
    hd = p.get('header')
    if not hd: return ''
    a, b = (hd + [''])[:2] if isinstance(hd, list) else (hd, '')
    return f'<div class="cn-a cn-fo"{h.DECO} style="left:{x(span[0], r)}px;width:{wd(*span)}px;top:40px;color:{tokens(sf)["mut"]}"><span>{h.esc(a)}</span><span>{h.esc(b)}</span></div>'
def blocks(bs, c0=1, c1=6, r=True, sf='paper'):
    import flow
    return flow.R(listify(bs), flow.ctx_of(c0, c1, r, sf))
def brand_logo(n, p, r, sf):
    b = h.BRAND; lg = (b or {}).get('logo') or {}
    if not b or not lg.get('file') or p.get('logo') is False: return ''
    where = 'cover' if n == 1 else 'back' if p.get('_last') else 'page'
    if not p.get('logo') and where not in lg.get('pages', ['cover', 'back']): return ''
    t = tokens(sf); col = '#FFFFFF' if sf == 'image' and not is_light_art() else t['hd'] if sf in ('A', 'B') else t['acc']
    hh = round(float(lg.get('h', 24)) * (1.5 if where == 'cover' else 1))
    import brand as BR
    svg = BR.logo_svg(b, col, dark=lum(col) > .5)
    disc_left = p.get('layout') == 'FULL' and sf in ('A', 'B') and not r and p.get('deco', True) is not False and p.get('index') is None
    pos = f'left:{x(1, r)}px' if not (p.get('header') or disc_left) else f'right:{W - xe(6, r)}px'
    return f'<div class="cn-a cn-logo"{h.DECO} style="{pos};top:{48 - hh // 2 if hh < 40 else 28}px;height:{hh}px;color:{col}">{svg}</div>'
def brand_contact(p):
    b = h.BRAND
    if not b or not b.get('contact') or not p.get('_last') or p.get('contact') is False: return ''
    return f'<div class="cn-tx cn-contact m1"{h.DECO}>' + '<br>'.join(T_(s) for s in listify(b['contact'])) + '</div>'
def emit(n, p, r, sf, body, dom, img=None, fsf=None, fspan=(1, 6), fo=True, side='S', hsf=None, hspan=(1, 6)):
    bg = tokens(sf)['bg'] if sf != 'image' else ('#111111' if G.get('STYLE') != 'stijl' else __import__('stijl').seam())
    import stijl
    import brand_graphic
    graphic = brand_graphic.render(n, p, h.BK, h.PROJ, W, H, tokens(sf)['acc'], h.BRAND_GRAPHICS)
    html = f'<div class="cn-v" style="display:contents;{vs("paper")}">{body}</div>' + graphic + stijl.accents(n, p, r, sf) + brand_logo(n, p, r, sf) + running(p, r, hsf or fsf or sf, hspan) + (folio(n, r, fsf or sf, fspan) if fo and p.get('folio', True) else '')
    h.page(n, html, img, side, bg, f' cn sf-{sf}' + (' paper' if sf == 'paper' else '') + (' cn-brand-layered' if graphic else ''), chapter=p.get('chapter', p.get('index')))
    used(dom); h.SURF_HIST.append(dom); LIGHT_ART[0] = False
def pg(n): return n % 2 == 1

# ================================================================ 三层架构（Theme × Layout × Font）之 Layout 层
def editorial_grid(cells, gap=1, cls=''):
    """cells: (起栏 1..6, 占栏数 1..6, HTML, 起点错开行数)。基于 6 轨 CSS Grid 自然流动。"""
    out = []
    for item in cells:
        start, span, content = item[0], item[1], item[2]
        offset = item[3] if len(item) > 3 else 0
        if not content: continue
        pt = f';padding-top:{offset * LH}px' if offset else ''
        out.append(f'<div class="cn-ed-cell" style="grid-column:{start}/span {span}{pt}">{content}</div>')
    return f'<div class="cn-ed-grid {cls}" style="row-gap:{gap * LH}px">{"".join(out)}</div>' if out else ''

def editorial_surface(p, default='paper'):
    raw = str(p.get('surface', default)).strip().lower()
    sf = SURF_ALIAS.get(raw, default)
    if sf not in ('paper', 'A', 'B', 'dark'):
        raise ValueError('编辑阅读版式 surface 可选 paper / A / B / dark')
    return sf

def editorial_rule(kind='light', m=1):
    cls = 'cn-ed-rule-strong' if kind == 'strong' else 'cn-ed-rule-accent' if kind == 'accent' else 'cn-ed-rule'
    return f'<div class="{cls} m{m}"></div>'

def editorial_head(p, size=48, rule='light'):
    """标准 A4 社论页头：kicker + 横线 + 标题 + 副题 + 可选导语"""
    k = [lab(p.get('kicker'), deco=False)]
    if rule:
        k.append(editorial_rule(rule, m=0))
    if p.get('title'):
        k.append(disp(p.get('title'), round(min(size, 52) * K), 6, round(28 * K), m=1 if rule or p.get('kicker') else 0, lines=2))
    if p.get('sub') or p.get('en'):
        k.append(sub(p.get('sub') or p.get('en'), m=0))
    return k

def editorial_wash(p, sf='paper'):
    """NatGeo 风格可选的顶部或侧边柔和摄影渐融层（washDown / washSide），完全置于 .deco 背景层，不影响 6 轨网格几何。"""
    w = p.get('wash_image')
    if not w or sf != 'paper' or not has_photo(w):
        return ''
    rel = h.FIGIMG(w.get('src') if isinstance(w, dict) else w, W)
    if not rel:
        return ''
    mode = p.get('wash_mode', 'down')
    cls = 'cn-wash-side' if mode == 'side' else 'cn-wash-down'
    bg = tokens(sf)['bg']
    return f'<div class="cn-a {cls} deco" style="--page-bg:{bg}"><img alt="" src="{rel}"></div>'

def editorial_page(n, p, kids, sf=None, fo=True):
    sf = sf or editorial_surface(p)
    wash_html = editorial_wash(p, sf)
    body = wash_html + stack(1, 6, pg(n), [k for k in kids if k], top=0, sf=sf, cls='cn-editorial', id_=sid(n, 'editorial'))
    return emit(n, p, pg(n), sf, body, sf, fo=fo)

def editorial_quote(p, m=1):
    if not p.get('quote'): return ''
    return (f'<div class="cn-ed-pause cn-snap m{m}"><div class="cn-qt">{T_(p["quote"])}</div>'
            + (lab(p.get('by'), m=0, deco=False) if p.get('by') else '') + '</div>')

def editorial_figure(v, span, rows, caption=None, bleed=(0, 0, 0), role='primary'):
    """有内容的图像才入图版：SVG 原样嵌入；缺图不替换成编号/随机底纹。"""
    src = v.get('src') if isinstance(v, dict) else v
    if str(src).startswith('ai:'):
        resolved = h.ai_file(src)
        v = dict(v, src=resolved) if isinstance(v, dict) else resolved
        src = resolved
    if not isinstance(src, str) or not src.strip() or not has_photo(v):
        raise ValueError('PLATE / SEQUENCE / PHOTO_OPEN / MASONRY / CONTACT 需要实际 image / img 文件；先准备内容相关的图片或 SVG，不能用占位底纹')
    left, right, top = bleed
    width, height = wd(1, span) + left + right, rows * LH + top
    im = pic(v, width, height, label=False)
    outer = f' style="position:relative;padding-top:{rows * LH}px"' if top else ''
    image_style = (f'position:absolute;top:{-top}px;' if top else 'position:relative;')
    image_style += f'left:{-left}px;width:{width}px;height:{height}px'
    tag = ' data-bleed="edge"' if any(bleed) else ''
    return (f'<figure class="cn-ed-figure" data-image-role="{role}"{outer}{tag}><div class="cn-pic" style="{image_style}">{im}</div>'
            + (f'<figcaption class="cn-cap m1">{T_(caption)}</figcaption>' if caption else '') + '</figure>')

def soft_figure(v, span, rows, caption=None, bleed=(0, 0, 0), idx=1):
    """支持无图占位或实际照片的通用网格图位（供 COVER/SIDE/BOTTOM/GALLERY/STAGGER/MIX 等复用）。"""
    left, right, top = bleed
    width, height = wd(1, span) + left + right, round(rows * LH + top)
    im = pic(v, width, height, idx, 'B', label=False)
    outer = f' style="position:relative;padding-top:{round(rows * LH)}px"' if top else ''
    image_style = (f'position:absolute;top:{-top}px;' if top else 'position:relative;')
    image_style += f'left:{-left}px;width:{width}px;height:{height}px'
    tag = ' data-bleed="edge"' if any(bleed) else ''
    return (f'<figure class="cn-ed-figure" data-image-role="supporting"{outer}{tag}><div class="cn-pic" style="{image_style}">{im}</div>'
            + (f'<figcaption class="cn-cap m1">{T_(caption)}</figcaption>' if caption else '') + '</figure>')

def photo_bleed(n, p):
    mode = p.get('bleed', 'edge')
    if mode not in ('edge', 'inset'): raise ValueError('摄影布局 bleed 可选 edge（到裁切边）/ inset（明确的版心内构图）')
    return (x(1, pg(n)), W - xe(6, pg(n))) if mode == 'edge' else (0, 0)

# ---------------------------------------------------------------- 01 COVER / 02 CHAPTER / 04 ENDING / FULL
def inset(p, r):
    out = ''
    for b in listify(p.get('inset')):
        c0, c1 = (1, 6) if 'gallery' in b else (4, 6) if r else (1, 3)
        out += stack(c0, c1, r, [blocks([b], c0, c1, r, 'image')], top=1, sf='image')
    return out

def FULL(n, p):
    """01_cover / 02_chapter / 04_ending：
    - 有照片时：满版出血摄影 + 国家地理双层渐暗遮罩（scrimTop + scrimBottom） + 顶部眉标/章节号 + 下部主标题与导语（无大色块遮挡）。
    - 无照片时：干净纸面（或显式 surface）上的 6 轨社论构成（顶部主结构线 + 章节号/眉标 + 展示大标题 + 2+4 导语说明 + 底部指标/元数据）。"""
    if G.get('STYLE') == 'stijl':
        import stijl; return stijl.FULL(n, p)
    r = pg(n); v = p.get('image'); photo = has_photo(v) or (h.STYLE != 'photo' and v is not False and not NOART())
    if p.get('inset') and not photo:
        h.WARN.append(f'第{n}页：这一页没有照片（photo 关），其中的 figure / gallery 没有图位、会被丢弃 → 改用 logos 块，或换成有图的版式（T / TWO / MIX）')
    chapter = p.get('index') is not None
    bottom_blocks = (blocks(p.get('bottom'), 1, 6, r, 'image' if photo else 'paper') if p.get('bottom') else '') + brand_contact(p)
    if photo:
        if chapter and not has_photo(v) and h.SD['tone'] != 'dark':
            p = dict(p, _artbox=(0, 0, 1, .5))
        name, im = bake_full(n, p, v); body = im
        LIGHT_ART[0] = (not has_photo(v)) and h.SD['tone'] != 'dark'
        body += inset(p, r)
        if LIGHT_ART[0]:
            body += f'<div class="cn-a cn-field cn-paper" data-y0="{sid(n, "t")}.top-1" style="left:0;top:0;width:{W}px;height:{H}px;background:{h.TH_["PAPER"]}"></div>'
        else:
            body += '<div class="cn-a deco" style="left:0;right:0;top:0;height:28%;background:linear-gradient(180deg,rgba(11,20,16,.68) 0%,rgba(11,20,16,.22) 56%,rgba(11,20,16,0) 100%)"></div>'
            body += '<div class="cn-a deco" style="left:0;right:0;bottom:0;height:64%;background:linear-gradient(180deg,rgba(11,20,16,0) 0%,rgba(11,20,16,.58) 42%,rgba(11,20,16,.92) 100%)"></div>'
        if chapter:
            body += stack(1, 6, r, [lab(p.get('kicker')), num(str(p['index']), round(72 * K), round(84 * K))], top=0, sf='image', id_=sid(n, 'ch'))
        elif p.get('kicker'):
            body += stack(1, 6, r, [lab(p.get('kicker'))], top=0, sf='image', id_=sid(n, 'kk'))
        gold_rule = '<div style="width:64px;height:4px;background:#F2C14E;margin-bottom:14px"></div>' if G.get('STYLE') == 'photo' else ''
        bot_kids = [
            gold_rule,
            disp(p.get('title'), round((64 if chapter else 72) * K), 6, round(38 * K), lines=2),
            sub(p.get('en') or p.get('sub'), cols=5, m=1),
            lead(p.get('intro'), 1, 5),
            para(listify(p.get('text')), cols=5, m=1) if p.get('text') else '',
            stats_row(p.get('stats'), m=1),
            f'<div class="m1">{bottom_blocks}</div>' if bottom_blocks else ''
        ]
        body += stack(1, 6, r, bot_kids, bot=LAST, sf='image', id_=sid(n, 't'))
        return emit(n, p, r, 'image', body, 'image', name, fo=bool(p.get('folio', False if n == 1 or p.get('_last') else True)))
    sf = editorial_surface(p, 'paper')
    top_kids = []
    if chapter:
        top_kids.append(editorial_grid([
            (1, 2, num(str(p['index']), round(64 * K), round(72 * K), deco=False), 0),
            (3, 4, lab(p.get('kicker'), deco=False), 1)
        ]))
        top_kids.append(editorial_rule('strong', m=1))
    else:
        if p.get('kicker'): top_kids.append(lab(p.get('kicker'), deco=False))
        top_kids.append(editorial_rule('strong', m=1 if p.get('kicker') else 0))
    top_kids.append(disp(p.get('title'), round((64 if chapter else 72) * K), 6, round(38 * K), m=1, lines=2))
    if p.get('en') or p.get('sub'):
        top_kids.append(sub(p.get('en') or p.get('sub'), m=1))
    lower_cells = []
    if p.get('intro') and p.get('text'):
        lower_cells = [(1, 2, lead(p.get('intro')), 0), (3, 4, para(listify(p.get('text')), flow='keep'), 0)]
    elif p.get('intro'):
        lower_cells = [(1, 5, lead(p.get('intro')), 0)]
    elif p.get('text'):
        lower_cells = [(1, 5, para(listify(p.get('text')), flow='keep'), 0)]
    if lower_cells:
        top_kids.append(f'<div class="m2">{editorial_grid(lower_cells)}</div>')
    if p.get('stats'):
        top_kids.append(f'<div class="m2">{editorial_rule("light", m=0)}{stats_row(p.get("stats"), m=1)}</div>')
    if bottom_blocks:
        top_kids.append(f'<div class="m2">{bottom_blocks}</div>')
    return editorial_page(n, p, top_kids, sf=sf, fo=bool(p.get('folio', False if n == 1 or p.get('_last') else True)))

def COVER(n, p): return FULL(n, dict(p, folio=p.get('folio', False)))
def CHAPTER(n, p): return FULL(n, dict(p, index=p.get('index', p.get('chapter', '01'))))
def ENDING(n, p):
    """04_ending：上部出血照片（若有）+ 下部收束主句与双栏联络行动区。"""
    if p.get('image') and has_photo(p.get('image')):
        left, right = photo_bleed(n, p)
        fig = soft_figure(p.get('image'), 6, L(11), p.get('caption'), (left, right, TOP if left or right else 0))
        kids = [fig] + editorial_head(p, 44, rule=None)
    else:
        kids = editorial_head(p, 56, rule='strong')
    if p.get('intro'): kids.append(lead(p['intro'], 1, 5))
    cols = listify(p.get('columns'))
    if cols:
        cells = [(1 if i % 2 == 0 else 4, 3, col_html(IT(c), 'cn-top1'), 0) for i, c in enumerate(cols[:2])]
        kids.append(f'<div class="m1">{editorial_grid(cells)}</div>')
    elif p.get('text'):
        kids.append(para(listify(p.get('text')), m=1, cols=5, flow='keep'))
    if p.get('bottom'):
        kids.append(f'<div class="m1">{blocks(p.get("bottom"), 1, 6, pg(n), editorial_surface(p))}</div>')
    if brand_contact(p):
        kids.append(f'<div class="m1">{brand_contact(p)}</div>')
    return editorial_page(n, p, kids, fo=bool(p.get('folio', False)))

# ---------------------------------------------------------------- 03b SIDEBAR / ONE 单栏与旁注
def body_row(n, p, cols_if_short=6):
    text = listify(p.get('text')); q = p.get('quote')
    if q:
        side = f'<aside class="cn-ed-note"><div class="cn-qt cn-t20">{T_(q)}</div>' + (lab(p.get('by'), m=1, deco=False) if p.get('by') else '') + '</aside>'
        return editorial_grid([(1, 4, para(text, flow='keep') or '<div></div>', 0), (5, 2, side, 0)])
    flow = p.get('text_flow', 'auto')
    long_ = flow == 'columns' or (flow == 'auto' and chars(text) > (330 if h.CJK else 300) * (14 / BS) ** 2)
    return para(text, 'cn-cols2' if long_ else '', m=0, cols=6 if long_ else cols_if_short, flow=flow)

def ONE(n, p):
    h.BUDGET(p, ['intro', 'text', 'quote'], .75)
    sf = editorial_surface(p)
    v = p.get('image')
    kids = []
    if v and has_photo(v):
        left, right = photo_bleed(n, p)
        kids.append(soft_figure(v, 6, L(10), p.get('caption'), (left, right, TOP if left or right else 0)))
    if p.get('index') is not None:
        kids.append(num(str(p['index']), round(44 * K), round(52 * K), deco=False))
    kids += editorial_head(p, 44 if v else 52, rule='light' if not v else None)
    if p.get('intro'):
        kids.append(lead(p['intro'], 1, 5))
    if p.get('sidebar'):
        side_html = f'<aside class="cn-ed-note">{TX(p["sidebar"])}</aside>'
        kids.append(f'<div class="m1">{editorial_grid([(1, 4, body_row(n, p, 4), 0), (5, 2, side_html, 0)])}</div>')
    else:
        br = body_row(n, p, 6)
        if br: kids.append(f'<div class="m1">{br}</div>')
    if p.get('takeaway'):
        kids.append(f'<div class="m1">{editorial_rule("light", m=0)}<div class="cn-sub m1">{T_(p["takeaway"])}</div></div>')
    return editorial_page(n, p, kids, sf=sf)

def SIDEBAR(n, p): return ONE(n, p)

# ---------------------------------------------------------------- 03g STEPS / CARDS 卡片与序列模块
def card_html(i, c, p, size=28, withimg=False):
    no = f'<span class="cn-cardn">{i:02d}</span>' if p.get('num', True) is not False else ''
    k = lab(c.get('k'), deco=False) if c.get('k') else ''
    meta = ('<div class="cn-cardmeta">' + ''.join(f'<span class="cn-cap">{T_(x)}</span>' for x in c.get('meta', [])) + '</div>') if c.get('meta') else ''
    rule = 'cn-top1' if p.get('style') == 'line' else 'cn-top2'
    txt = f'{k}<div class="cn-h cn-t20 cn-snap">{no}{T_(c.get("t", ""))}</div>{meta}{TX(c.get("x"))}{TX(c.get("items"), 0)}'
    if withimg:
        im = soft_figure(c.get('img'), 2, L(5), None, (0, 0, 0), idx=i)
        return f'<div class="cn-card {rule} cn-snap">{im}<div class="m1">{txt}</div></div>'
    return f'<div class="cn-card {rule} cn-snap">{txt}</div>'

def CARDS(n, p):
    cs = [IT(c) for c in listify(p.get('cards'))]; h.LIMIT('CARDS', cs, 2, 9, 'cards 卡片')
    if not cs: return
    k = len(cs); cols = max(1, min(3, int(p.get('cols') or (2 if k in (2, 4) else 3))))
    span = 6 // cols
    withimg = any('img' in c for c in cs)
    h.BUDGET(p, ['intro', 'cards', 'stats'], .65 if withimg else .95)
    sf = editorial_surface(p)
    kids = editorial_head(p, 44 if withimg else 48, rule='light')
    if p.get('intro'):
        kids.append(lead(p['intro'], 1, 5))
    if p.get('stats'):
        kids.append(stats_row(p.get('stats'), 6, 44, m=1))
    cells = []
    for i, c in enumerate(cs, 1):
        col_idx = (i - 1) % cols
        start_track = 1 + col_idx * span
        cells.append((start_track, span, card_html(i, c, p, withimg=withimg), 0))
    kids.append(f'<div class="m1">{editorial_grid(cells, gap=1)}</div>')
    return editorial_page(n, p, kids, sf=sf)

def STEPS(n, p):
    its = [IT(c) for c in listify(p.get('steps') or p.get('items') or p.get('cards'))]
    sf = editorial_surface(p)
    kids = editorial_head(p, 48, rule='light')
    if p.get('intro'): kids.append(lead(p['intro'], 1, 5))
    rows = []
    for i, it in enumerate(its, 1):
        no = it.get('k') or f'{i:02d}'
        rows.append(f'<div class="cn-axisrow cn-top1" style="grid-template-columns:{wd(1, 1) + GUT}px minmax(0,1fr);padding-top:{LH // 3}px">'
                    f'<span class="cn-axisdot"></span><div class="cn-axisdate cn-h cn-t20">{T_(no)}</div>'
                    f'<div><div class="cn-h cn-t20">{T_(it.get("t", ""))}</div>{TX(it.get("x"))}{TX(it.get("items"))}</div></div>')
    kids.append(f'<div class="cn-timeaxis m1">{"".join(rows)}</div>')
    return editorial_page(n, p, kids, sf=sf)

# ---------------------------------------------------------------- 03n STAGGER 交错图文叙事
def STAGGER(n, p):
    its = [IT(c) for c in listify(p.get('items'))]; h.LIMIT('STAGGER', its, 2, 4, 'items 条目'); h.BUDGET(p, ['intro', 'items'], .65)
    if not its: return
    sf = editorial_surface(p)
    kids = editorial_head(p, 44, rule='light')
    if p.get('intro'): kids.append(lead(p['intro'], 1, 5))
    v = h.VAR('STAGGER', 2)
    img_rows = L(6) if len(its) <= 2 else L(4)
    for i, it in enumerate(its):
        flip = (i + v) % 2 == 1
        no = f'<span class="cn-cardn">{i + 1:02d}</span>' if p.get('num', True) is not False else ''
        txt = (f'<div class="cn-top2" style="padding-top:{LH // 3}px">'
               + lab(it.get('k'), deco=False)
               + f'<div class="cn-h cn-t20 cn-snap">{no}{T_(it.get("t", ""))}</div>'
               + TX(it.get('x')) + TX(it.get('items')) + '</div>')
        if it.get('img'):
            im = soft_figure(it.get('img'), 3, img_rows, None, (0, 0, 0), idx=i + 1)
            row_cells = [(1, 3, txt, 0), (4, 3, im, 0)] if flip else [(1, 3, im, 0), (4, 3, txt, 0)]
        else:
            row_cells = [(1, 2, num(it.get('k') or f'{i + 1:02d}', 36, 44, deco=False), 0),
                         (3, 4, f'<div class="cn-top1"><div class="cn-h cn-t20 cn-snap">{T_(it.get("t", ""))}</div>{TX(it.get("x"))}{TX(it.get("items"))}</div>', 0)]
        kids.append(f'<div class="m1">{editorial_grid(row_cells)}</div>')
    return editorial_page(n, p, kids, sf=sf)

# ---------------------------------------------------------------- 03a DUAL / 03s COMPARISON / TWO 双栏对照
def col_html(c, rule='cn-top2'):
    return f'<div class="cn-card {rule} cn-snap">{lab(c.get("k"), deco=False)}<div class="cn-h cn-t20 cn-snap">{T_(c.get("t", ""))}</div>{TX(c.get("x"))}{TX(c.get("items"))}</div>'

def TWO(n, p):
    sf = editorial_surface(p); v = p.get('image')
    its = [IT(c) for c in listify(p.get('items'))]; withimg = any('img' in i for i in its)
    kids = []
    if v and has_photo(v):
        left, right = photo_bleed(n, p)
        kids.append(soft_figure(v, 6, L(9), p.get('caption'), (left, right, TOP if left or right else 0)))
    kids += editorial_head(p, 44 if (v or withimg) else 48, rule='light' if not v else None)
    if p.get('intro'): kids.append(lead(p['intro'], 1, 5))
    if p.get('columns') or not withimg:
        cs = [IT(c) for c in listify(p.get('columns'))] or its
        if p.get('columns'): h.LIMIT('TWO', cs, 2, 3, 'columns 栏')
        else: h.LIMIT('TWO', cs, 2, 8, 'items 条目')
        h.BUDGET(p, ['intro', 'columns', 'items'], .8)
        k = len(cs); nc = 3 if k == 3 or (k > 4 and k % 3 == 0) else 2; span = 6 // nc
        cells = [(1 + (i % nc) * span, span, col_html(c, 'cn-top2' if i < nc else 'cn-top1'), 0) for i, c in enumerate(cs)]
        kids.append(f'<div class="m1">{editorial_grid(cells, gap=1)}</div>')
        if p.get('quote') or p.get('takeaway'):
            kids.append(editorial_quote(p) if p.get('quote') else f'<div class="m1">{editorial_rule("accent", m=0)}<div class="cn-sub m1">{T_(p["takeaway"])}</div></div>')
        return editorial_page(n, p, kids, sf=sf)
    h.LIMIT('TWO', its, 2, 8, 'items 条目'); h.BUDGET(p, ['intro', 'items'], .65)
    img_rows = L(5) if len(its) <= 4 else L(4)
    cells = []
    for i, it in enumerate(its):
        col_idx = i % 2
        im = soft_figure(it.get('img'), 3, img_rows, None, (0, 0, 0), idx=i + 1)
        tx = f'<div class="cn-snap m1">{lab(it.get("k"), deco=False)}<div class="cn-h cn-t20 cn-snap">{T_(it.get("t", ""))}</div>{TX(it.get("x"))}{TX(it.get("items"))}</div>'
        cells.append((1 + col_idx * 3, 3, f'<div class="cn-card">{im}{tx}</div>', 0))
    kids.append(f'<div class="m1">{editorial_grid(cells, gap=1)}</div>')
    return editorial_page(n, p, kids, sf=sf)

def DUAL(n, p): return TWO(n, p)

def COMPARISON(n, p):
    sf = editorial_surface(p)
    kids = editorial_head(p, 44, rule='light')
    if p.get('intro'): kids.append(lead(p['intro'], 1, 5))
    headers = p.get('headers') or [p.get('label_left', ''), p.get('label_right', '')]
    if any(headers):
        h0, h1 = f'<div class="cn-h cn-t20">{T_(headers[0])}</div>', f'<div class="cn-h cn-t20">{T_(headers[1])}</div>'
        kids.append(f'<div class="m1">{editorial_grid([(1, 3, h0, 0), (4, 3, h1, 0)])}</div>')
        kids.append(editorial_rule('strong', m=0))
    pairs = listify(p.get('rows') or p.get('pairs') or p.get('items'))
    for pair in pairs:
        if isinstance(pair, dict):
            l_it, r_it = IT(pair.get('left', {})), IT(pair.get('right', {}))
        elif isinstance(pair, (list, tuple)) and len(pair) >= 2:
            l_it, r_it = IT(pair[0]), IT(pair[1])
        else:
            l_it, r_it = IT(pair), dict(t='')
        row_html = editorial_grid([
            (1, 3, col_html(l_it, 'cn-top1'), 0),
            (4, 3, col_html(r_it, 'cn-top1'), 0)
        ])
        kids.append(f'<div class="m1">{row_html}</div>')
    if p.get('source') or p.get('notes'):
        kids.append(f'<div class="cn-notes m1">{bullets(listify(p.get("source") or p.get("notes")))}</div>')
    return editorial_page(n, p, kids, sf=sf)

# ---------------------------------------------------------------- 03h TABLE / 03l INDEX / 03t CHRONOLOGY / GRID
GRIDKEYS = ('facts', 'table', 'timeline', 'items', 'notes', 'toc')
def chapters():
    out = []; m = 1
    for q in h.SPEC['pages']:
        lay = q.get('layout')
        if lay in ('FULL', 'CHAPTER') and q.get('index') is not None:
            out.append([str(q['index']), q.get('title', ''), q.get('en') or q.get('sub') or q.get('intro') or '', m])
        m += h.LAY.get(lay, (None, 1))[1]
    return out
def toc_es(p):
    if p['toc'] == 'auto': return chapters()
    return [list(e) + [''] * (4 - len(e)) if isinstance(e, (list, tuple)) else [e.get('no', ''), e.get('t', ''), e.get('x', ''), e.get('page', '')] for e in listify(p['toc'])]
TOC_DEG = [0]
def toc_need(es, p, big, clamp, intro):
    L_ = 7 + (2 if intro else 0) + 1
    cpl = (wd(1, 4)) // BS if h.CJK else round((wd(1, 4)) / BS * 2.2)
    for e in es:
        no, t, s = (list(e) + [''] * 3)[:3]
        body = 1 + -(-chars(t) // max(1, cpl)) + (0 if clamp or not s else -(-chars(s) // max(1, cpl)))
        L_ += max(4 if big else 3, body)
    return L_
def toc_deg(es, p):
    for d in (0, 1, 2, 3):
        if toc_need(es, p, d < 2, d >= 1, d < 3) <= LAST - 1: return d
    return 3
def sec_html(key, p, r):
    if key == 'facts':
        fs = [f if isinstance(f, (list, tuple)) else [f, ''] for f in listify(p['facts'])]
        nc = min(4, len(fs)) or 1
        def _fsz(a):
            ln = len(str(a))
            base = 38 if nc <= 3 else 32
            return min(base, 36 if ln <= 4 else 28 if ln <= 7 else 22)
        return f'<div class="cn-stats" style="grid-template-columns:repeat({nc},minmax(0,1fr));row-gap:{LH // 2}px">' + ''.join(f'<div class="cn-top2 cn-snap" style="padding-top:{LH // 3}px;min-width:0;overflow:hidden">{num(a, _fsz(a), _fsz(a) + 6, deco=False)}<div class="cn-cap" style="margin-top:4px">{T_(b)}</div></div>' for a, b in fs) + '</div>'
    if key == 'timeline':
        tl = [IT(t) if isinstance(t, dict) else dict(zip(('k', 't', 'x'), t)) if isinstance(t, (list, tuple)) else dict(t=t) for t in listify(p['timeline'])]
        rows = []
        for i, it in enumerate(tl):
            t_, x_ = str(it.get('t', '')), it.get('x')
            if x_ is None and ' · ' in t_: t_, x_ = t_.split(' · ', 1)
            rule = 'cn-top2' if i == 0 else 'cn-top1'
            rows.append(editorial_grid([
                (1, 2, f'<div class="{rule}" style="padding-top:{LH // 3}px"><div class="cn-h cn-t20" style="color:var(--acc)">{T_(it.get("k", f"{i+1:02d}"))}</div></div>', 0),
                (3, 4, f'<div class="{rule}" style="padding-top:{LH // 3}px"><div class="cn-h cn-t20">{T_(t_)}</div>' + (f'<div class="cn-mut">{T_(x_)}</div>' if x_ else '') + '</div>', 0)
            ]))
        return '<div class="cn-chronology">' + ''.join(rows) + '</div>'
    if key == 'table':
        tb = p['table']; tb = tb if isinstance(tb, dict) else {'rows': tb}
        hd, rows = tb.get('head') or [], tb.get('rows') or []
        nc = max([len(hd)] + [len(rw) for rw in rows]) or 1
        tpl = tb.get('widths') or (f'{wd(1, 2)}px 1fr auto' if nc == 3 else f'{wd(1, 2)}px 1fr' if nc == 2 else ' '.join(['1fr'] * nc))
        if isinstance(tpl, list): tpl = ' '.join(f'{w}fr' if isinstance(w, (int, float)) else str(w) for w in tpl)
        cell = lambda c, j, n_: f'<span class="{"cn-h" if j == 0 else ""}" style="{"text-align:right" if j == n_ - 1 and n_ == 3 else ""}">{T_(c)}</span>'
        out = (f'<div class="cn-tr cn-th" style="grid-template-columns:{tpl}">' + ''.join(f'<span{h.DECO}>{T_(c)}</span>' for c in hd) + '</div>') if hd else ''
        out += ''.join(f'<div class="cn-tr" style="grid-template-columns:{tpl}">' + ''.join(cell(c, j, nc) for j, c in enumerate(list(rw) + [''] * (nc - len(rw)))) + '</div>' for rw in rows)
        return f'<div class="cn-tb cn-top2">{out}</div>'
    if key == 'items':
        its = [IT(c) for c in listify(p['items'])]
        nc = int(p.get('items_cols') or (3 if len(its) % 3 == 0 or len(its) > 4 else 2)); span = 6 // nc
        cells = [(1 + (i % nc) * span, span, col_html(c, 'cn-top1'), 0) for i, c in enumerate(its)]
        return editorial_grid(cells, gap=1)
    if key == 'notes':
        return f'<div class="cn-notes">{bullets(listify(p["notes"]))}</div>'
    if key == 'toc':
        es = toc_es(p)
        if p['toc'] == 'auto' and not es: h.WARN.append(f'第{h.CURN}页：toc: auto 没找到章节页（带 index 的 FULL 页）')
        TOC_DEG[0] = toc_deg(es, p)
        clamp = TOC_DEG[0] >= 1 or bool(p.get('facts')) or bool(p.get('image'))
        def row(idx_e, no, t, s, pg_):
            link = str(pg_).isdigit()
            pn = f'{int(pg_):02d}' if link else T_(pg_)
            rule = 'cn-top2' if idx_e == 0 else 'cn-top1'
            t_clean = str(t).replace('\n', ' · ')
            return ((f'<a class="cn-tocr {rule} cn-snap" href="#p{int(pg_)}"' if link else f'<div class="cn-tocr {rule} cn-snap"')
                    + f' style="grid-template-columns:{COL}px 1fr {COL}px;column-gap:{GUT}px;padding:{LH // 4}px 0">'
                    + f'{num(no, 28, 32)}<div style="min-width:0"><div class="cn-h cn-t20">{T_(t_clean)}</div>'
                    + (f'<div class="cn-mut" style="{"white-space:nowrap;overflow:hidden;text-overflow:ellipsis" if clamp else ""}">{T_(s)}</div>' if s else '') + '</div>'
                    + f'<div class="cn-num" style="font-size:{round(16 * S)}px;line-height:{LH}px;text-align:right;color:var(--mut)"{h.DECO}>{pn}</div>'
                    + ('</a>' if link else '</div>'))
        return '<div class="cn-toc">' + ''.join(row(i, *e) for i, e in enumerate(es)) + '</div>'
    return ''
GRID_TIGHT = [False]
def GRID(n, p):
    h.BUDGET(p, ['intro'] + list(GRIDKEYS), 1.1)
    TOC_DEG[0] = 0
    r = pg(n); v = p.get('image')
    sf = editorial_surface(p)
    keys = [k for k in p if k in GRIDKEYS]
    kids = []
    if v and has_photo(v):
        left, right = photo_bleed(n, p)
        im_rows = L(5) if len(keys) >= 2 else L(7)
        kids.append(soft_figure(v, 6, im_rows, p.get('caption'), (left, right, TOP if left or right else 0)))
    kids += editorial_head(p, 40 if (v and len(keys) >= 2) else 46, rule='light' if not v else None)
    if p.get('intro') and TOC_DEG[0] < 3:
        kids.append(lead(p['intro'], 1, 5))
    for k in keys:
        kids.append(f'<div class="cn-sec cn-snap m1">{sec_html(k, p, r)}</div>')
    return editorial_page(n, p, kids, sf=sf)

def TABLE(n, p): return GRID(n, p)
def INDEX(n, p): return GRID(n, p)
def CHRONOLOGY(n, p): return GRID(n, p)

# ---------------------------------------------------------------- 03i GALLERY / COLLAGE 组图叙事
def COLLAGE(n, p):
    ims = listify(p.get('images')); h.LIMIT('COLLAGE', ims, 2, 7, 'images 图片'); h.BUDGET(p, ['intro', 'text'], .35)
    if not ims: return
    sf = editorial_surface(p)
    left, right = photo_bleed(n, p)
    caps = listify(p.get('captions'))
    kids = []
    kids.append(soft_figure(ims[0], 6, L(9 if len(ims) <= 3 else 7), None, (left, right, TOP if left or right else 0), idx=1))
    rest = ims[1:]
    if rest:
        nc = 2 if len(rest) in (1, 2, 4) else 3
        span = 6 // nc
        r_rows = L(6 if len(rest) <= 3 else 4)
        cells = []
        for idx_r, img_v in enumerate(rest):
            c_idx = idx_r % nc
            b_l = left if c_idx == 0 else 0
            b_r = right if c_idx == nc - 1 else 0
            cells.append((1 + c_idx * span, span, soft_figure(img_v, span, r_rows, None, (b_l, b_r, 0), idx=idx_r + 2), 0))
        kids.append(f'<div class="m1">{editorial_grid(cells, gap=1)}</div>')
    kids += editorial_head(p, 42, rule=None)
    if p.get('intro') or p.get('text'):
        kids.append(para(listify(p.get('text')) or p.get('intro'), m=1, cols=5, flow='keep'))
    if caps:
        legend = ''.join(f'<span class="cn-lg"><span class="cn-num" style="font-size:{BS}px;color:var(--acc)">{i + 1:02d}</span> {T_(cp)}</span>' for i, cp in enumerate(caps[:len(ims)]) if cp)
        kids.append(f'<div class="cn-cap cn-legend m1">{legend}</div>')
    return editorial_page(n, p, kids, sf=sf)

def GALLERY(n, p): return COLLAGE(n, p)

# ---------------------------------------------------------------- 03c BOTTOM / 03d SIDE / MIX 图文组合
def MIX(n, p):
    ss = [IT(c) for c in listify(p.get('sections'))]; h.LIMIT('MIX', ss, 1, 4, 'sections 分段')
    ims = listify(p.get('images')) or ([p['image']] if p.get('image') else [])
    kind = p.get('variant') or ('side' if len(ims) >= 2 else 'hero'); h.BUDGET(p, ['intro', 'sections', 'quote'], .65)
    sf = editorial_surface(p)
    left, right = photo_bleed(n, p)
    if kind == 'side' and ims:
        sec_htmls = ''.join(f'<div class="cn-card cn-top1 cn-snap m1">{lab(s.get("k"), deco=False)}<div class="cn-h cn-t20 cn-snap">{T_(s.get("t", ""))}</div>{TX(s.get("x"))}{TX(s.get("items"))}</div>' for s in ss)
        left_col = ''.join(editorial_head(p, 42, rule='light')) + (lead(p['intro'], 1) if p.get('intro') else '') + sec_htmls + (editorial_quote(p, 1) if p.get('quote') else '')
        img_h = L(10 if len(ims) == 2 else 21 // max(1, len(ims[:3])))
        right_imgs = ''.join(f'<div class="{"m1" if i else ""}">{soft_figure(im_v, 3, img_h, None, (0, right, 0), idx=i+1)}</div>' for i, im_v in enumerate(ims[:3]))
        return editorial_page(n, p, [editorial_grid([(1, 3, left_col, 0), (4, 3, right_imgs, 0)])], sf=sf)
    kids = []
    if ims:
        kids.append(soft_figure(ims[0], 6, L(9), p.get('caption'), (left, right, TOP if left or right else 0), idx=1))
    kids += editorial_head(p, 44, rule=None if ims else 'light')
    if p.get('intro'): kids.append(lead(p['intro'], 1, 5))
    nc = len(ss) if len(ss) <= 3 else 2; span = 6 // nc
    cells = [(1 + (i % nc) * span, span, col_html(s, 'cn-top2'), 0) for i, s in enumerate(ss)]
    kids.append(f'<div class="m1">{editorial_grid(cells, gap=1)}</div>')
    if p.get('quote'): kids.append(editorial_quote(p, 1))
    return editorial_page(n, p, kids, sf=sf)

def BOTTOM(n, p):
    sf = editorial_surface(p)
    left, right = photo_bleed(n, p)
    kids = editorial_head(p, 44, rule='light')
    if p.get('intro'): kids.append(lead(p['intro'], 1, 5))
    text = listify(p.get('text'))
    if len(text) >= 2:
        kids.append(f'<div class="m1">{editorial_grid([(1, 3, para(text[0], flow="keep"), 0), (4, 3, para(text[1:], flow="keep"), 0)])}</div>')
    elif text:
        kids.append(para(text, 'cn-cols2', m=1))
    if p.get('image'):
        kids.append(f'<div class="m1">{soft_figure(p.get("image"), 6, L(11), p.get("caption"), (left, right, 0))}</div>')
    return editorial_page(n, p, kids, sf=sf)

def SIDE(n, p):
    sf = editorial_surface(p)
    left, right = photo_bleed(n, p)
    left_col = (lab(p.get('kicker'), deco=False)
                + editorial_rule('light', m=0)
                + disp(p.get('title'), round(40 * K), 3, round(24 * K), m=1, lines=3)
                + (sub(p.get('sub') or p.get('en'), m=0) if (p.get('sub') or p.get('en')) else '')
                + (lead(p['intro'], 1) if p.get('intro') else '')
                + para(listify(p.get('text')), m=1, flow='keep'))
    if p.get('caption'): left_col += f'<div class="cn-cap m1">{T_(p["caption"])}</div>'
    right_col = soft_figure(p.get('image'), 3, L(24), None, (0, right, TOP if right else 0))
    return editorial_page(n, p, [editorial_grid([(1, 3, left_col, 0), (4, 3, right_col, 0)])], sf=sf)

# ---------------------------------------------------------------- 03j RHYTHM / 03k MARGINALIA / 03p OVERLAY / 03q GEOMETRY / 03r EVIDENCE / 03u TYPOGRAPHIC
def RHYTHM(n, p):
    text = listify(p.get('text'))
    kids = editorial_head(p, 48, rule='strong')
    opening = editorial_grid([(1, 2, para(p.get('intro'), flow='keep'), 0),
                              (3, 4, para(text[:1], flow='keep'), 0)])
    kids += [f'<div class="m1">{opening}</div>', editorial_quote(p, m=1)]
    if len(text) > 1:
        cells = [(1 if i % 2 == 0 else 4, 3, para(t, flow='keep'), i % 2)
                 for i, t in enumerate(text[1:])]
        kids += [f'<div class="m1">{editorial_grid(cells)}</div>']
    return editorial_page(n, p, kids)

def MARGINALIA(n, p):
    sections = listify(p.get('sections'))
    if not sections: raise ValueError('MARGINALIA 需要 sections: [{t, x, note_title, note}]')
    kids = editorial_head(p, 48, rule='light')
    if p.get('intro'): kids.append(lead(p['intro'], 1, 4))
    for i, s in enumerate(sections):
        if not isinstance(s, dict): raise ValueError('MARGINALIA 的每个 section 需要 x 正文，可加 t / note_title / note')
        main = (f'<div class="cn-h cn-t20 cn-snap">{T_(s["t"])}</div>' if s.get('t') else '') + para(s.get('x'), m=0, flow='keep')
        note = (lab(s.get('note_title'), deco=False) + para(s.get('note'), flow='keep'))
        aside = f'<aside class="cn-ed-note">{note}</aside>' if note else ''
        kids.append(f'<div class="m1">{editorial_grid([(1, 4, main, 0), (5, 2, aside, 0)])}</div>')
        if i == 0 and p.get('quote'): kids.append(editorial_quote(p, m=1))
    return editorial_page(n, p, kids)

def PLATE(n, p):
    sf = editorial_surface(p)
    v = p.get('image')
    v = dict(v) if isinstance(v, dict) else dict(src=v)
    v.setdefault('fit', 'contain')
    v.setdefault('duo', False)
    notes = []
    for i, a in enumerate(listify(p.get('annotations'))):
        a = IT(a)
        notes.append(f'<div class="cn-ed-note cn-snap">{lab(a.get("k", f"{i + 1:02d}"), deco=False)}'
                     + f'<div class="cn-h">{T_(a.get("t", ""))}</div>' + para(a.get('x'), flow='keep') + '</div>')
    figure = editorial_figure(v, 4, L(13), p.get('caption'))
    grid = editorial_grid([(1, 4, figure, 0), (5, 2, ''.join(notes), 0)])
    kids = editorial_head(p, 44) + ([lead(p['intro'], 1, 4)] if p.get('intro') else [])
    kids += [f'<div class="m1">{grid}</div>', para(p.get('text'), m=1, cols=4, flow='keep')]
    return editorial_page(n, p, kids, sf)

def EVIDENCE(n, p): return PLATE(n, p)

def OVERLAY(n, p):
    sf = editorial_surface(p)
    left, right = photo_bleed(n, p)
    top_grid = editorial_grid([
        (1, 2, lab(p.get('kicker'), deco=False) + editorial_rule('accent', m=1), 0),
        (3, 4, soft_figure(p.get('image'), 4, L(15), None, (0, right, TOP if right else 0)), 0)
    ])
    plate = (f'<div class="cn-overlay-plate">{disp(p.get("title"), round(44 * K), 4, round(28 * K), lines=2)}'
             + (sub(p.get('sub') or p.get('en'), m=0) if (p.get('sub') or p.get('en')) else '') + '</div>')
    lower = editorial_grid([
        (1, 2, f'<div class="cn-ed-note"><div class="cn-cap">{T_(p.get("caption") or p.get("source") or "")}</div></div>', 0),
        (3, 4, (lead(p['intro']) if p.get('intro') else '') + para(listify(p.get('text')), m=1 if p.get('intro') else 0, flow='keep'), 0)
    ])
    return editorial_page(n, p, [top_grid, plate, f'<div class="m1">{lower}</div>'], sf=sf)

def GEOMETRY(n, p):
    sf = editorial_surface(p)
    ims = listify(p.get('images')) or [p.get('image'), p.get('detail_image')]
    kids = editorial_head(p, 44, rule='light')
    main_im = soft_figure(ims[0] if ims else None, 4, L(12), None, (0, 0, 0), idx=1)
    det_im = soft_figure(ims[1] if len(ims) > 1 else (ims[0] if ims else None), 2, L(6), None, (0, 0, 0), idx=2)
    side_col = (f'<aside class="cn-ed-note">{para(p.get("note") or p.get("intro"), flow="keep")}</aside>' if (p.get('note') or p.get('intro')) else '') + f'<div class="m1">{det_im}</div>'
    kids.append(f'<div class="cn-geo-field m1">{editorial_grid([(1, 4, main_im, 0), (5, 2, side_col, 0)])}</div>')
    if p.get('text'):
        kids.append(f'<div class="m1">{editorial_rule("accent", m=0)}{para(listify(p.get("text")), m=1, cols=4, flow="keep")}</div>')
    return editorial_page(n, p, kids, sf=sf)

def TYPOGRAPHIC(n, p):
    sf = editorial_surface(p)
    kids = [lab(p.get('kicker'), deco=False),
            editorial_rule('strong', m=0),
            disp(p.get('title'), round(56 * K), 6, round(32 * K), m=1, lines=2)]
    if p.get('intro') or p.get('sub') or p.get('en'):
        kids.append(f'<div class="m1">{editorial_grid([(3, 4, lead(p.get("intro") or p.get("sub") or p.get("en")) + editorial_rule("accent", m=1), 0)])}</div>')
    text = listify(p.get('text'))
    left_voice = quote(p.get('quote'), p.get('by')) if p.get('quote') else para(text[:1], flow='keep')
    right_voice = para(text[1:] if not p.get('quote') else text, flow='keep')
    kids.append(f'<div class="m1">{editorial_grid([(1, 3, left_voice, 0), (4, 3, right_voice, 0)])}</div>')
    kids.append(editorial_rule('light', m=1))
    return editorial_page(n, p, kids, sf=sf)

def SEQUENCE(n, p):
    items = [IT(it) for it in listify(p.get('items'))]
    if len(items) != 3: raise ValueError('SEQUENCE 需要 3 个 items，每个含 img，可加 k / t / x；按主场景、细节、延伸编排')
    def text(it):
        return lab(it.get('k'), deco=False) + (f'<div class="cn-h cn-t20 cn-snap">{T_(it["t"])}</div>' if it.get('t') else '') + para(it.get('x'), m=1, flow='keep')
    first = editorial_grid([(1, 4, editorial_figure(items[0].get('img'), 4, L(10)), 0),
                            (5, 2, text(items[0]), 0)])
    second = editorial_grid([
        (1, 3, editorial_figure(items[1].get('img'), 3, L(7)) + text(items[1]), 0),
        (4, 3, editorial_figure(items[2].get('img'), 3, L(7)) + text(items[2]), 1)])
    return editorial_page(n, p, editorial_head(p, 44) + [f'<div class="m1">{first}</div>', f'<div class="m1">{second}</div>'])

def PHOTO_OPEN(n, p):
    left, right = photo_bleed(n, p)
    figure = editorial_figure(p.get('image'), 6, L(16), p.get('caption'), (left, right, TOP if left or right else 0))
    title = lab(p.get('kicker'), deco=False) + disp(p.get('title'), round(48 * K), 4, round(28 * K), lines=2)
    title += sub(p.get('sub') or p.get('en'), m=0)
    opening = editorial_grid([(1, 4, title, 0), (5, 2, para(p.get('intro'), flow='keep'), 0)])
    kids = [figure, f'<div class="m1">{opening}</div>', para(p.get('text'), m=1, cols=4, flow='keep')]
    return editorial_page(n, p, kids)

def MASONRY(n, p):
    items = [IT(it) for it in listify(p.get('items'))]
    if len(items) != 6: raise ValueError('MASONRY 需要6个items，每个含img与可选caption；不以重复填图补数量')
    left, right = photo_bleed(n, p)
    cells, captions = [], []
    top = TOP if left or right else 0
    rows = L(26)
    gap = LH / 4
    extend = (GUT - gap) / 2
    for col, first in enumerate((L(9), L(16), L(6))):
        parts = []
        notes = []
        for row, height in enumerate((first, rows - first - gap / LH)):
            i = col * 2 + row
            it = items[i]
            ident = sid(n, 'photo_%s' % (i + 1))
            figure = editorial_figure(it.get('img'), 2, height, None,
                                      (left if col == 0 else extend, right if col == 2 else extend, top if row == 0 else 0), role='supporting')
            parts.append(f'<div class="cn-masonry-item" role="group" aria-describedby="{ident}" style="margin-top:{gap if row else 0}px">{figure}</div>')
            notes.append(f'<div class="cn-cap" id="{ident}"><span{h.DECO} aria-hidden="true">{i + 1:02d}</span> {T_(it.get("caption") or "")}</div>')
        cells.append((1 + col * 2, 2, ''.join(parts), 0))
        captions.append((1 + col * 2, 2, ''.join(notes), 0))
    kids = [f'<div class="cn-masonry">{editorial_grid(cells)}</div>',
            f'<div style="margin-top:{LH // 2}px">{lab(p.get("kicker"), deco=False)}</div>',
            disp(p.get('title'), round(38 * K), 6, round(24 * K), lines=2),
            sub(p.get('sub') or p.get('en')),
            f'<div class="cn-masonry-legend" style="margin-top:{LH // 2}px">{editorial_grid(captions)}</div>']
    return editorial_page(n, p, kids)

def CONTACT(n, p):
    items = [IT(it) for it in listify(p.get('items'))]
    if len(items) != 6: raise ValueError('CONTACT 需要image主图和6个含img的items')
    left, right = photo_bleed(n, p)
    hero = editorial_figure(p.get('image'), 6, max(6, L(7)), p.get('caption'), (left, right, 0))
    cells = []
    for i, it in enumerate(items):
        col = i % 3
        figure = editorial_figure(it.get('img'), 2, max(4, L(4)), it.get('caption'),
                                  (left if col == 0 else 0, right if col == 2 else 0, 0), role='supporting')
        cells.append((1 + col * 2, 2, figure, 0))
    kids = [hero, f'<div style="margin-top:{LH // 2}px">{ "".join(editorial_head(p, 38, rule=None)) }</div>',
            f'<div style="margin-top:{LH // 2}px">{editorial_grid(cells, gap=1)}</div>']
    return editorial_page(n, p, kids)

def READING(n, p):
    sf = editorial_surface(p)
    header = ''
    if p.get('series_header'):
        import flow
        header = flow.B({'series_header': dict(p['series_header'], compact=True)},
                        flow.ctx_of(1, 2, pg(n), sf))
    elif p.get('title'):
        header = (lab(p.get('kicker'), deco=False)
                  + f'<div class="cn-h cn-ttl cn-t28">{T_(p["title"])}</div>'
                  + sub(p.get('sub') or p.get('en'), m=1))
    notes = []
    if p.get('intro'):
        notes.append(f'<div class="cn-ed-note">{para(p["intro"], flow="keep")}</div>')
    for item in listify(p.get('notes') or p.get('sidebar')):
        notes.append(f'<div class="cn-ed-note">{TX(item)}</div>')
    side = header + (f'<div class="m2">{"".join(notes)}</div>' if notes else '')
    main = para(p.get('text'), flow=p.get('text_flow', 'keep'))
    if p.get('quote'):
        main += editorial_quote(p)
    grid = editorial_grid([(1, 2, side, 0), (3, 4, main, 0)], cls='cn-reading')
    return editorial_page(n, p, [grid], sf=sf)

# ---------------------------------------------------------------- 登记表
RECIPES = {
    'COVER': COVER, 'CHAPTER': CHAPTER, 'ENDING': ENDING, 'FULL': FULL,
    'DUAL': DUAL, 'TWO': TWO,
    'SIDEBAR': SIDEBAR, 'ONE': ONE,
    'RHYTHM': RHYTHM,
    'MARGINALIA': MARGINALIA,
    'TYPOGRAPHIC': TYPOGRAPHIC,
    'READING': READING,
    'STEPS': STEPS, 'CARDS': CARDS,
    'TABLE': TABLE, 'INDEX': INDEX, 'CHRONOLOGY': CHRONOLOGY, 'GRID': GRID,
    'EVIDENCE': EVIDENCE, 'PLATE': PLATE,
    'COMPARISON': COMPARISON,
    'BOTTOM': BOTTOM, 'SIDE': SIDE, 'MIX': MIX,
    'GALLERY': GALLERY, 'COLLAGE': COLLAGE,
    'MASONRY': MASONRY,
    'STAGGER': STAGGER,
    'CONTACT': CONTACT,
    'OVERLAY': OVERLAY,
    'GEOMETRY': GEOMETRY,
    'SEQUENCE': SEQUENCE,
    'PHOTO_OPEN': PHOTO_OPEN,
}
