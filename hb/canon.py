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
三、撞色与装饰
  每页的底在 纸色 / A 色块 / B 色块 / 满版照片 之间按前后页轮换（A 上的字用 B，B 上的字用 A，见 palettes.pair）。
  装饰只用信息本身：章节号、条目数、编号——不放随机几何。照片太灰太白（褪色、过曝）自动做成 A/B 双色调。
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
# 画布：(宽, 高, 栏宽, 栏间, 天头, 订口, 切口, 行数, 行距, 正文字号)。1px = 0.75pt
CANVAS = {'a4': (794, 1123, 80, 32, 88, 50, 104, 32, 28, 16),     # A4 210×297mm：正文 16px = 12pt（小四），一栏 5 字
          'a4-14': (794, 1123, 84, 28, 88, 50, 100, 38, 24, 14),  # A4 紧凑（book.body: 14）：正文 10.5pt（五号），一栏 6 字
          'a5': (559, 794, 56, 24, 64, 36, 67, 28, 24, 14),       # A5 148×210mm：一栏 4 字，版心 28 行
          'xhs': (600, 800, 64, 24, 64, 48, 48, 28, 24, 14)}      # 小红书 3:4（导出 1080×1440 图片）：单页、左右页边相同
def setup(name, body=None):
    global W, H, COL, GUT, TOP, IN, OUT, LAST, LH, BS, S, K
    if name not in CANVAS or name == 'a4-14': raise SystemExit(f'ERROR: book.canvas 可选 a4 / a5 / xhs，当前 {name}')
    if body not in (None, 14, 16): raise SystemExit(f'ERROR: book.body 只能写 16（默认）或 14，当前 {body}')
    key = 'a4-14' if name == 'a4' and body == 14 else name
    if name != 'a4' and body == 16: print(f'提示：{name} 画布的正文固定 14px（页面小），book.body: 16 只对 A4 有效')
    W, H, COL, GUT, TOP, IN, OUT, LAST, LH, BS = CANVAS[key]; S = LH / 24; K = W / 794
    return W, H
def L(n): return round(n * LAST / 38)   # A4 上的第 n 行 → 当前画布上对应的行
def nrows(px, d=18, lo=2, hi=40):
    """旧写法的高度（像素）→ 整行数（照片位、方框的高度落在行线上；A4 上 520px ≈ 19 行、300px ≈ 11 行）。
    和 flow.nrows 同一套换算（flow 导入 canon，这里不能再回头 import flow）。"""
    try: v = float(px) if px is not None else d * LH
    except (TypeError, ValueError): v = d * LH
    return max(lo, min(hi, round(v / LH)))
def left(r): return IN if r else OUT
def x(c, r): return left(r) + (c - 1) * (COL + GUT)
def xe(c, r): return x(c, r) + COL
def wd(c0, c1): return (c1 - c0 + 1) * (COL + GUT) - GUT
def y(l): return TOP + l * LH
def gc(c, r): return xe(c, r) + GUT // 2          # 第 c 栏右边那条栏间的中线（拼贴、色块的分界线）
def side_cols(r, inner=True):                     # 一页的“里侧三栏 / 外侧三栏”（单页订口在左）
    return (1, 3) if (r == inner) else (4, 6)

# ---------------------------------------------------------------- 颜色
def rgba(c, a):
    c = c.lstrip('#'); return f'rgba({int(c[0:2], 16)},{int(c[2:4], 16)},{int(c[4:6], 16)},{a})'
def MODE(): return G.get('COLOR_MODE', 'clash')
def QUIET(): return G.get('STYLE') in ('swiss', 'geo', 'stijl') and MODE() == 'mono'   # 默认节制用色；显式surface仍可选实色纸面，不生成底图
def NOART(): return QUIET() or G.get('STYLE') in ('editorial', 'stijl', 'geo')   # 不以自动气氛插画填充无图页
def BW(): return QUIET() and G.get('STYLE') == 'swiss' or G.get('STYLE') == 'stijl'   # 照片一律转黑白
def tokens(sf):
    if sf in ('D', 'S', 'X') and G.get('STYLE') == 'stijl':   # 风格派的三原色格（stijl.py）
        import stijl; return stijl.tok(sf)
    T = h.TH_; A, B, P, INK = T['A'], T['B'], T['PAPER'], T['INK']
    if sf == 'dark':
        bg = INK; fg = max(('#FFFFFF', '#000000'), key=lambda c: contrast(c, bg))
        return dict(bg=bg, fg=fg, hd=fg, acc=fg, num=fg, lab=fg, mut=rgba(fg, .84), rule=fg, line=rgba(fg, .38))
    if QUIET() and sf in ('paper', 'B'):   # 单色默认纸色/浅灰；显式 A 保留主题色纸面
        bg = T['TINT'] if sf == 'B' else P
        return dict(bg=bg, fg=INK, hd=INK, acc=A if contrast(A, bg) >= 4.5 else INK, num=A if contrast(A, bg) >= 3 else INK, lab=INK, mut=T['MUT'], rule=INK, line=rgba(INK, .3))
    if MODE() != 'clash' and sf in ('paper', 'A', 'B'):   # 点缀 / 单色档：A = 主色整块（只给封面、章节页），B = 次级背景（浅色块），强调色只上数字、标签、细线
        if sf == 'A':
            bg = A; fg = '#FFFFFF' if contrast('#FFFFFF', A) >= 4.5 else '#000000'   # 实色纸面按对比度选白字/黑字
            return dict(bg=bg, fg=fg, hd=fg, acc=fg, num=fg, lab=fg, mut=rgba(fg, .84), rule=fg, line=rgba(fg, .38))
        bg = T.get('TINT') or (P if sf == 'paper' else _mix(P, A, .07)) if sf == 'B' else P
        acc = A if contrast(A, bg) >= 5 else _on5(bg, T['G'], T['OCH'], INK)
        return dict(bg=bg, fg=INK, hd=A if contrast(A, bg) >= 3 else INK, acc=acc, num=A if contrast(A, bg) >= 3 else acc, lab=acc, mut=T['MUT'], rule=INK, line=rgba(INK, .22))
    if sf in ('A', 'B'):
        bg, other = (A, B) if sf == 'A' else (B, A)
        fg = _on5(bg, other, '#FFFFFF', INK, P)
        hd = other if contrast(other, bg) >= 4.5 else fg          # 彩色块上的彩色字要对比 ≥ 4.5 才用（经典撞色都过），不够就用白 / 墨
        sm = other if contrast(other, bg) >= 5 else fg          # 小字（标签、编号）要 ≥ 5:1，留出抗锯齿的余量
        return dict(bg=bg, fg=fg, hd=hd, acc=sm, num=hd, lab=sm, mut=rgba(fg, .86) if contrast(fg, bg) >= 9 else fg, rule=fg, line=rgba(fg, .38))
    if sf == 'image' and is_light_art():   # 浅色风格插画（papercut 等）当底：用深色字
        return dict(bg=P, fg=INK, hd=INK, acc=INK, num=A if contrast(A, P) >= 3 else INK, lab=INK, mut=T['MUT'], rule=INK, line=rgba(INK, .3))
    if sf == 'image':
        lt = max((A, B), key=lum); lt = lt if lum(lt) > .6 and MODE() == 'clash' else '#FFFFFF'   # 照片上的大数字：很浅的撞色（拿坡里黄、柠檬黄、鱼肚白）才用，否则白字
        acc = '#FFFFFF'
        if G.get('STYLE') == 'photo' and T.get('GOLD') and lum(T['GOLD']) > .4: lt = acc = T['GOLD']   # 国家地理式：照片上的 Day 大字、编号、时段标签、color: gold 用金色
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
    """variants = [(变体名, 主底色)]。页上写了 surface 就用对应的变体；否则不和上一页同底、A/B 色块交替、同版式再出现时换下一种。"""
    k = ST['count'].get(lay, 0); ST['count'][lay] = k + 1
    want = SURF_ALIAS.get(str(p.get('surface', '')).strip().lower())
    if want:   # 显式选底优先于用色档位的默认节制
        for v in variants:
            if v[1] == want: return v[0], v[1]
    if QUIET():   # 瑞士单色：没有主色整块，“A 色块”一律是纸色
        variants = list(dict.fromkeys((n, 'paper' if d == 'A' else d) for n, d in variants))
    elif MODE() != 'clash' and lay != 'FULL':   # 点缀档：主色整块只留给封面、章节页（FULL）；其他页的“A 色块”换成次级背景，强调色只上数字和线
        variants = list(dict.fromkeys((n, 'B' if d == 'A' else d) for n, d in variants))
    if p.get('surface') and not want: h.WARN.append(f'第{h.CURN}页：surface 只能写 paper / A / B / dark / image（或旧写法 brand / pop / split / tint），已忽略 {p["surface"]}')
    if want:
        for v in variants:
            if v[1] == want: return v[0], v[1]
        h.WARN.append(f'第{h.CURN}页 {lay}：这一页没有 surface: {p["surface"]} 的排法，按自动轮换来')
    rot = variants[k % len(variants):] + variants[:k % len(variants)]
    calm = 4 if ST['run'] >= 2 else 0   # 已经连着两页整页色块：这一页优先纸色（colorqa 的 60-30-10）
    best = max(enumerate(rot), key=lambda iv: (3 if iv[1][1] != ST['prev'] else 0) + (1 if iv[1][1] in ('A', 'B') and iv[1][1] != ST['last'] else 0)
               + (calm if iv[1][1] not in ('A', 'B') else 0) - iv[0] * .1)
    return best[1]
def used(dom):
    ST['prev'] = dom; ST['run'] = ST['run'] + 1 if dom in ('A', 'B') else 0
    if dom in ('A', 'B'): ST['last'] = dom
def field_color():   # 这一页要用色块时用哪一块：和上一次用的相反（点缀档：总是次级背景）
    return 'B' if MODE() != 'clash' else other(ST['last'])

# ---------------------------------------------------------------- 文字
def T_(s): return re.sub(r'\*\*(.+?)\*\*', r'<b class="cn-hl">\1</b>', h.esc(str(s))).replace('\n', '<br>')   # **…** → 强调色
def sid(n, k): return f'p{n}_{k}'
def stack(c0, c1, r, kids, top=None, bot=None, id_='', sf='paper', y0=None, y1=None, gold=None, inside=None, cls='', style='', free=False, floor=None):
    """文字栈：c0..c1 栏宽；top=从第几行起 / bot=到第几行止 / y0、y1=相对别的文字栈；gold=尽量从第几行起（放不下就往上让）"""
    pos = f'top:{y(top)}px;' if top is not None else f'bottom:{H - y(bot)}px;' if bot is not None else f'top:{TOP}px;'
    a = (f' id="{id_}"' if id_ else '') + f' data-anchor="{"bottom" if bot is not None and top is None else "top"}"'
    for k, v in (('y0', y0), ('y1', y1), ('gold', gold), ('in', inside)):
        if v is not None: a += f' data-{k}="{v}"'
    if free: a += ' data-free="1"'
    if floor is not None: a += f' data-floor="{floor}"'   # 不能高过第几行（上面有大号章节号等装饰）
    return f'<div class="cn-a cn-st {cls}"{a} style="left:{x(c0, r)}px;width:{wd(c0, c1)}px;{pos}{vs(sf)}{style}">{"".join(k for k in kids if k)}</div>'
def W_(cols): return f'width:{wd(1, cols)}px;' if cols else ''
def lab(t, m=0, deco=True): return f'<div class="cn-lab m{m}"{h.DECO if deco else ""}>{T_(t)}</div>' if t else ''
def disp(t, mx=112, cols=None, mn=None, m=0, lines=3, cls='', style=''):
    a = f' data-fit="{mx}"' + (f' data-min="{mn}"' if mn else '') + (f' data-lines="{lines}"' if lines != 3 else '')
    tt = T_(t)
    for ch in ('·', '，', '、', '：'):   # 允许在这些地方折行（中文其余地方不拆字，见 canon.css keep-all；空格本来就能折）。用零宽空格而不是 <wbr>：nowrap 时 <wbr> 仍会折行
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
def TX(v, m=0):   # 信息列表保留ul/li语义，不自动添加短横或步骤编号
    if v in (None, '', []): return ''
    return bullets(v, m, style='plain') if isinstance(v, list) else para(v, m=m)
def num(t, size=56, lh=None, cls='', deco=True, style=''):
    lh = lh or (size + 16 if size <= 80 else size)
    if size < 24: style = 'color:var(--acc);' + style   # 小号编号按小字的对比度要求取色
    return f'<div class="cn-num {cls}"{h.DECO if deco else ""} style="font-size:{size}px;line-height:{lh}px;{style}">{T_(t)}</div>'
def head(p, mx=112, cols=None, mn=None, intro=True, icols=None, lines=3):
    """页头：小标签 + 大标题（撑满栏宽）+ 副题 + 导语"""
    k = [lab(p.get('kicker')), disp(p.get('title'), mx, cols, mn, lines=lines), sub(p.get('en') or p.get('sub'), cols=cols)]
    if intro and p.get('intro'): k.append(lead(p['intro'], 1, icols or cols))
    return k
def stats_row(st, cols=6, size=48, m=1):
    if not st: return ''
    st = [s if isinstance(s, (list, tuple)) else [s, ''] for s in st][:4]
    cells = ''.join(f'<div>{num(a, size, size + 8, deco=False)}<div class="cn-cap">{T_(b)}</div></div>' for a, b in st)
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

# ---- 照片：自动双色调（褪色、过曝的照片做成 A/B 双色调）
_STATS = {}
def weak(path):
    """照片是不是“发灰发白”：亮而不饱和的像素占 30% 以上（褪色、过曝、雾面）"""
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
    """图片位里放什么：照片 / AI 配图 / 风格插画（无图风格）/ 色块 + 大号编号（照片风格没给图时，像是有意的设计，构建时提示补图）"""
    duo = None
    fit = v.get('fit', 'cover') if isinstance(v, dict) else 'cover'
    if isinstance(v, dict): f, (fx, fy), duo = v.get('src'), tuple(v.get('focus', [.5, .5])), v.get('duo')
    else: f, (fx, fy) = v, (.5, .5)
    if f and str(f).startswith('ai:'):
        f = h.AIFIG(f, w, hgt, '版式图位')
    if f and not h.is_art(f):
        rel = h.FIGIMG(f, w * 1.5)
        if not rel: return ''
        mode = str(h.BK.get('duotone', 'all' if BW() else 'auto')).lower()   # 瑞士单色、风格派：照片一律黑白
        if rel.endswith(('.jpg', '.jpeg', '.png')) and (duo is True or (duo is None and (mode == 'all' or (mode == 'auto' and weak(os.path.join(h.PROJ, rel)))))):
            rel = duotone(rel)
            if h.USE: h.USE[-1]['img'] = rel.split('/')[-1]; h.USE[-1]['duo'] = True
        return f'<img class="cn-img" alt="" src="{rel}" style="object-fit:{fit};object-position:{fx * 100:.0f}% {fy * 100:.0f}%">'
    if h.STYLE != 'photo' and not NOART():   # 无图风格：生成风格插画（瑞士单色档、风格派、孟菲斯不生成，用色块 + 编号）
        d = os.path.join(h.PROJ, 'img'); os.makedirs(d, exist_ok=True)
        key = hashlib.md5(repr((h.STYLE, sorted(h.TH_.items()), h.CURN, idx, round(w), round(hgt), os.path.getmtime(h.art.__file__))).encode()).hexdigest()[:10]
        out = os.path.join(d, f'slot_{key}.jpg')
        if not os.path.exists(out):
            h.art.make(h.STYLE, max(240, round(w * 2)), max(200, round(max(hgt, w * .8) * 2)), h.CURN * 31 + idx * 7, h.TH_, (0, 0, 1, .89)).save(out, quality=90)
        return f'<img class="cn-img" alt="" src="img/slot_{key}.jpg" style="object-position:80% 50%">'
    if h.CURN not in PHWARN and not NOART():
        PHWARN.add(h.CURN); h.WARN.append(f'第{h.CURN}页：有图片位没给照片，先排成色块 + 编号（照片到了写进 image / img / images）')
    t = tokens('B' if QUIET() else sf)
    label = label and not NOART()   # 瑞士 / 孟菲斯 / 风格派：没照片的图片位就是一块安静的色块（这些风格本来就用色块构图），不写占位编号
    return (f'<div class="cn-ph" style="background:{t["bg"]}">' + (f'<span class="cn-num deco"{h.DECO} style="color:{rgba(h.TH_["INK"], .16) if QUIET() else t["num"]};font-size:{min(220, max(64, round(min(w, max(hgt, 120)) * .7)))}px">{idx:02d}</span>' if label else '') + '</div>')
def has_photo(v): return bool(v) and not h.is_art(v if not isinstance(v, dict) else v.get('src'))

# ---- 满版照片走 hb 的烘焙流程（dark.py 会在白字下面渐进压暗，直到对比度达标）
def bake_full(n, p, v):
    f, focus = (v.get('src'), v.get('focus', [.5, .5])) if isinstance(v, dict) else (v, p.get('focus', [.5, .5]))
    name = f'p{n:02d}.jpg'
    h.bake(n, name, f if f else 'art', W, lambda X, Y: 0 * X, tuple(focus), p.get('target', [W / 2, H / 2]), p.get('zoom', 1.0), 'single', False, p.get('_artbox', (0, 0, 1, 1)))
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
    """自由内容块（title、p、cards、figure …）：flow.py 按 canon 的字号档和整行间距排"""
    import flow
    return flow.R(listify(bs), flow.ctx_of(c0, c1, r, sf))
def brand_logo(n, p, r, sf):
    """品牌包 logo：默认放在封面、封底（brand.yaml 的 logo.pages）；其他页写 logo: true；不要写 logo: false"""
    b = h.BRAND; lg = (b or {}).get('logo') or {}
    if not b or not lg.get('file') or p.get('logo') is False: return ''
    where = 'cover' if n == 1 else 'back' if p.get('_last') else 'page'
    if not p.get('logo') and where not in lg.get('pages', ['cover', 'back']): return ''
    t = tokens(sf); col = '#FFFFFF' if sf == 'image' and not is_light_art() else t['hd'] if sf in ('A', 'B') else t['acc']
    hh = round(float(lg.get('h', 24)) * (1.5 if where == 'cover' else 1))
    import brand as BR
    svg = BR.logo_svg(b, col, dark=lum(col) > .5)
    disc_left = p.get('layout') == 'FULL' and sf in ('A', 'B') and not r and p.get('deco', True) is not False and p.get('index') is None   # 左手页的字体海报：“日”在左上，logo 放右边
    pos = f'left:{x(1, r)}px' if not (p.get('header') or disc_left) else f'right:{W - xe(6, r)}px'
    return f'<div class="cn-a cn-logo"{h.DECO} style="{pos};top:{48 - hh // 2 if hh < 40 else 28}px;height:{hh}px;color:{col}">{svg}</div>'
def brand_contact(p):
    b = h.BRAND
    if not b or not b.get('contact') or not p.get('_last') or p.get('contact') is False: return ''
    return f'<div class="cn-tx cn-contact m1"{h.DECO}>' + '<br>'.join(T_(s) for s in listify(b['contact'])) + '</div>'
def emit(n, p, r, sf, body, dom, img=None, fsf=None, fspan=(1, 6), fo=True, side='S', hsf=None, hspan=(1, 6)):
    """一页：fsf / hsf = 页码 / 页眉所在的底（照片上用白字）；side = 跨页图片的哪一半（L / R，dark.py 用）"""
    bg = tokens(sf)['bg'] if sf != 'image' else ('#111111' if G.get('STYLE') != 'stijl' else __import__('stijl').seam())   # 照片页的缝：风格派按画法
    import stijl, geo
    import brand_graphic
    graphic = brand_graphic.render(n, p, h.BK, h.PROJ, W, H, tokens(sf)['acc'], h.BRAND_GRAPHICS)
    html = f'<div class="cn-v" style="display:contents;{vs("paper")}">{body}</div>' + graphic + stijl.accents(n, p, r, sf) + geo.accents(n, p, r, sf) + brand_logo(n, p, r, sf) + running(p, r, hsf or fsf or sf, hspan) + (folio(n, r, fsf or sf, fspan) if fo and p.get('folio', True) else '')
    h.page(n, html, img, side, bg, f' cn sf-{sf}' + (' paper' if sf == 'paper' else '') + (' cn-brand-layered' if graphic else ''), chapter=p.get('chapter', p.get('index')))
    used(dom); h.SURF_HIST.append(dom); LIGHT_ART[0] = False
def pg(n): return n % 2 == 1   # 单页（右手页）

# ================================================================ 8 个版式
# ---------------------------------------------------------------- FULL 全屏：封面 / 章节页 / 封底
def inset(p, r):
    """满版照片上的插图（旧写法 POSTER 里的 figure / gallery）：放进网格里的一格——切口一侧三栏、从第 1 行起，图注在图下一行；图组占满六栏"""
    out = ''
    for b in listify(p.get('inset')):
        c0, c1 = (1, 6) if 'gallery' in b else (4, 6) if r else (1, 3)
        out += stack(c0, c1, r, [blocks([b], c0, c1, r, 'image')], top=1, sf='image')
    return out
def FULL(n, p):
    if G.get('STYLE') == 'stijl':   # 风格派：封面、封底、章节页是一整幅构成
        import stijl; return stijl.FULL(n, p)
    r = pg(n); v = p.get('image'); photo = has_photo(v) or (h.STYLE != 'photo' and v is not False and not NOART())
    if p.get('inset') and not photo:   # 无图 POSTER 里的 figure/gallery 没有图位：明确报警，不静默丢内容
        h.WARN.append(f'第{n}页：这一页没有照片（photo 关），其中的 figure / gallery 没有图位、会被丢弃 → 改用 logos 块，或换成有图的版式（T / TWO / MIX）')
    chapter = p.get('index') is not None
    T = h.esc; kids_bot = []
    bottom_blocks = (blocks(p.get('bottom'), 1, 5, r, 'image' if (has_photo(v) or (h.STYLE != 'photo' and v is not False and not NOART())) else 'paper') if p.get('bottom') else '') + brand_contact(p)
    if photo:
        if chapter and not has_photo(v) and h.SD['tone'] != 'dark': p = dict(p, _artbox=(0, 0, 1, .5))   # 浅色风格插画：图形收在上半页，标题落在干净的下半页
        name, im = bake_full(n, p, v); body = im
        LIGHT_ART[0] = (not has_photo(v)) and h.SD['tone'] != 'dark'
        body += inset(p, r)
        cut = f'<div class="cn-a cn-field cn-paper" data-y0="{sid(n, "t")}.top-1" style="left:0;top:0;width:{W}px;height:{H}px;background:{h.TH_["PAPER"]}"></div>' if LIGHT_ART[0] else ''   # 浅色风格插画：插画停在文字上方一行，字落在干净的纸上（不和插画叠在一起）
        body += cut   # 放在文字栈前面：纸压住插画、字压住纸
        if chapter:   # 章节页（照片是主角）：章节号是文字栈里的一个大数字，和标题一起钉在版心下沿（dark.py 自动压暗），不压出页边、不压字
            ixs = round(144 * K)
            body += stack(1, 6, r, [f'<div class="cn-num cn-snap"{h.DECO} style="font-size:{ixs}px;line-height:{ixs}px;color:{tokens("image")["num"]};letter-spacing:-.03em">{T(str(p["index"]))}</div>',
                                    lab(p.get('kicker')), disp(p.get('title'), 112, 6), sub(p.get('en') or p.get('sub'), cols=6),
                                    lead(p.get('intro'), 1, 4), para(listify(p.get('text')), cols=4, m=1) if p.get('text') else '',
                                    stats_row(p.get('stats')), f'<div class="m1">{bottom_blocks}</div>' if bottom_blocks else ''], bot=LAST, sf='image', id_=sid(n, 't'))
            return emit(n, p, r, 'image', body, 'image', name)
        if MODE() != 'clash' or p.get('cover') == 'plain':   # 点缀档（或 cover: plain）：标题直接压在画面上，白字、下方渐暗，不盖色块
            if p.get('stats'):
                st = [s if isinstance(s, (list, tuple)) else [s, ''] for s in p['stats']][:4]
                body += stack(1, len(st), r, [f'<div class="cn-stats" style="grid-template-columns:repeat({len(st)},{COL}px);column-gap:{GUT}px">' +
                                              ''.join(f'<div>{num(a, 40, 48, deco=False)}<div class="cn-cap">{T(b)}</div></div>' for a, b in st) + '</div>'], top=0, sf='image', id_=sid(n, 's'))
            body += '<div class="cn-a deco" style="left:0;right:0;bottom:0;height:58%;background:linear-gradient(180deg,rgba(0,0,0,0),rgba(0,0,0,.55))"></div>' if has_photo(v) else ''
            body += stack(1, 6, r, [lab(p.get('kicker')), disp(p.get('title'), 120, 6, 56), sub(p.get('en') or p.get('sub'), cols=6),
                                    lead(p.get('intro'), 1, 5), para(listify(p.get('text')), cols=5, m=1) if p.get('text') else '',
                                    f'<div class="m1">{bottom_blocks}</div>' if bottom_blocks else ''], bot=LAST, sf='image', id_=sid(n, 't'))
            return emit(n, p, r, 'image', body, 'image', name)
        # 封面 / 封底：照片 + 一块出血的撞色色块，标题压在色块里（色块高度由内容决定，顶边落在行线上）
        bsf = 'A' if n == 1 else field_color()
        if p.get('stats'):
            st = [s if isinstance(s, (list, tuple)) else [s, ''] for s in p['stats']][:4]
            body += stack(1, len(st), r, [f'<div class="cn-stats" style="grid-template-columns:repeat({len(st)},{COL}px);column-gap:{GUT}px">' +
                                          ''.join(f'<div>{num(a, 40, 48, deco=False)}<div class="cn-cap">{T(b)}</div></div>' for a, b in st) + '</div>'], top=0, sf='image', id_=sid(n, 's'))
        t = tokens(bsf); ST['last'] = bsf
        if r: side, bw, pad_l = 'left:0', gc(5, r), x(1, r)            # 单页：色块从左边出血，盖住 1–5 栏
        else: side, bw, pad_l = 'right:0', W - gc(1, r), x(2, r) - gc(1, r)   # 双页：从右边出血，盖住 2–6 栏
        inner = ''.join(k for k in [lab(p.get('kicker')), disp(p.get('title'), 120, 5, 56), sub(p.get('en') or p.get('sub'), cols=5),
                                    lead(p.get('intro'), 1, 5), para(listify(p.get('text')), cols=5, m=1) if p.get('text') else '',
                                    f'<div class="m1">{bottom_blocks}</div>' if bottom_blocks else ''] if k)
        body += (f'<div class="cn-a cn-st cn-block" id="{sid(n, "t")}" data-anchor="bottom" style="{side};bottom:0;width:{bw}px;background:{t["bg"]};'
                 f'padding:{2 * LH}px 0 {H - y(LAST)}px {pad_l}px;{vs(bsf)}"><div style="width:{wd(1, 5)}px">{inner}</div></div>')
        return emit(n, p, r, 'image', body, 'image', name, fsf=bsf, fspan=(1, 5) if r else (2, 6), hsf='image')   # 页眉在照片 / 插画上，页码在色块里
    # 没有照片（照片风格）：整页撞色的字体海报——标题落在黄金分割附近，一轮“日”或章节号压出页边
    if chapter and not p.get('surface') and p.get('alternate') is not True:
        sf = 'paper' if QUIET() else 'A'   # 章节页默认统一 A 色块（四章翻起来一致；accent 档的 B 是浅色底，大章节号会看不见）。要轮换写 alternate: true，要指定底色写 surface
    elif QUIET(): sf = choose('FULL', p, [('A', 'A'), ('B', 'B')])[1] if n != 1 else 'paper'   # 单色：纸色或浅灰，强调色只给章节号和一个圆点
    else: sf = choose('FULL', p, [('A', 'A'), ('B', 'B')])[0] if n != 1 else 'A'
    t = tokens(sf); o = tokens(other(sf)); body = ''
    D = wd(1, 4)
    bot = [lead(p.get('intro'), 0, 4), para(listify(p.get('text')), cols=4, m=1) if p.get('text') else '', stats_row(p.get('stats')),
           f'<div class="m1">{bottom_blocks}</div>' if bottom_blocks else '']
    has_bot = any(bot)
    ixs, fl = (320, 13) if QUIET() or has_bot else (480, 19)
    if chapter:
        pos = f'right:{round(-48 * K)}px' if r else f'left:{round(-48 * K)}px'
        body += f'<div class="cn-a cn-num deco"{h.DECO} style="{pos};top:{y(0) - round(60 * K * ixs / 480)}px;font-size:{round(ixs * K)}px;line-height:{round(ixs * K)}px;color:{t["num"]};letter-spacing:-.04em">{T(str(p["index"]))}</div>'
    elif p.get('deco', True) is not False and G.get('STYLE') not in ('swiss', 'editorial'):
        body += f'<div class="cn-a deco" style="{"left" if r else "right"}:{W - D + round(90 * K)}px;top:{round(-90 * K)}px;width:{D}px;height:{D}px;border-radius:50%;background:{o["bg"]}"></div>'
        p = dict(p, header=None)   # 切口上角是一轮“日”：海报页不放页眉（页眉会压在圆上看不见）
    geo_ = G.get('STYLE') == 'geo'
    if geo_ and not chapter:   # 孟菲斯封面 / 封底：底边一条拼块带，文字让到拼块上方
        import geo; botl = geo.band_line()
    elif geo_:   # 孟菲斯章节页：切口下角一团拼块，文字让到它上方
        import geo; botl = geo.corner_line()
    else: botl = LAST
    if has_bot: body += stack(1, 6, r, bot, bot=botl, sf=sf, id_=sid(n, 'b'))
    body += stack(1, 6, r, [lab(p.get('kicker')), disp(p.get('title'), 96 if QUIET() and chapter else 160, 6, 56 if QUIET() and chapter else 64, lines=2 if chapter else 3), sub(p.get('en') or p.get('sub'))],
                  top=L(14), sf=sf, id_=sid(n, 't'), gold=L(fl) if chapter else L(14), floor=L(fl) if chapter else (L(10) if p.get('deco', True) is not False else None), y1=f'{sid(n, "b")}.top-2' if has_bot else None)   # 章节号 480px 占到第 18 行，标题从它下面开始
    emit(n, p, r, sf, body, sf, fo=not geo_)   # 孟菲斯封面 / 封底 / 章节页：底边、下角是拼块，不放页码

# ---------------------------------------------------------------- ONE 单栏：致辞、简介
def body_row(n, p, cols_if_short=6):
    """正文 + 引语：引语并列；多段中长文分两栏，短文使用整个版心。"""
    text = listify(p.get('text')); q = p.get('quote')
    if q:
        return (f'<div class="cn-2up m1" style="grid-template-columns:{wd(1, 3)}px {wd(1, 3)}px;column-gap:{GUT}px">'
                + (para(text) or '<div></div>') + quote(q, p.get('by')) + '</div>')
    flow = p.get('text_flow', 'auto')
    long_ = flow == 'columns' or (flow == 'auto' and chars(text) > (330 if h.CJK else 300) * (14 / BS) ** 2)
    return para(text, 'cn-cols2' if long_ else '', m=1, cols=6 if long_ else cols_if_short, flow=flow)
def ONE(n, p):
    h.BUDGET(p, ['intro', 'text', 'quote'], .7)
    r = pg(n); v = p.get('image'); B_ = sid(n, 'b')
    if v:
        name_sf = 'paper'
        body = box(0, 0, W, 10, pic(v, W, nrows(520, 18) * LH, 1, field_color()), 'cn-pic', y1r=f'{B_}.top-2', minh=nrows(200, 8) * LH)   # 主图带最小约 200px（A4 约 7 个行距）：再小就报 cn-small，别把合照裁成一条
        ix = num(p['index'], 56, 72) if p.get('index') is not None else ''
        body += stack(1, 6, r, [ix, lab(p.get('kicker')), disp(p.get('title'), 64, 6, 40), sub(p.get('en') or p.get('sub')), lead(p.get('intro'), 1, 6), body_row(n, p)], bot=LAST, id_=B_)
        return emit(n, p, r, 'paper', body, 'image')
    name, sf = choose('ONE', p, [('A', 'A'), ('B', 'B')])
    F_ = sid(n, 'f')
    body = field(0, 0, W, 10, sf, y1r=f'{B_}.top-2|{sid(n, "h")}.bottom+1', id_=F_, attr=f' data-clear="{B_}"')
    body += stack(1, 6, r, [body_row(n, p)], bot=LAST, id_=B_)
    ix = [num(str(p['index']), 80, 96)] if p.get('index') is not None else []
    body += stack(1, 6, r, ix + head(p, 112, 6, 56, icols=6), top=0, sf=sf, id_=sid(n, 'h'), inside=F_, y1=f'{B_}.top-4')
    emit(n, p, r, 'paper', body, sf)

# ---------------------------------------------------------------- CARDS 卡片：2–9 条并列短条目
def card_html(i, c, p, size, withimg=False, v=None):
    import stijl
    no = num(f'{i:02d}', size, size + 16, cls='cn-ino', style=stijl.bar(i - 1)) if p.get('num', True) is not False else ''
    k = lab(c.get('k'), deco=False) if c.get('k') else ''
    txt = f'{no}{k}<div class="cn-h cn-t20 cn-snap">{T_(c.get("t", ""))}</div>{TX(c.get("x"))}{TX(c.get("items"), 0)}'
    if withimg:
        return f'<div class="cn-card cn-top2 cn-flexcol"><div class="cn-ibox" data-minh="72">{pic(c.get("img"), 300, 200, i, "B" if i % 2 else "A")}</div><div class="cn-snap" style="padding-top:{LH // 2}px">{txt}</div></div>'
    return f'<div class="cn-card cn-top2 cn-snap">{txt}</div>'
def CARDS(n, p):
    cs = [IT(c) for c in listify(p.get('cards'))]; h.LIMIT('CARDS', cs, 2, 9, 'cards 卡片')
    if not cs: return
    k = len(cs); cols = max(1, min(3, int(p.get('cols') or (k if k <= 3 else 2 if k == 4 else 3)))); rows = -(-k // cols)
    span = 6 // cols
    withimg = any('img' in c for c in cs); line = p.get('style') == 'line'
    h.BUDGET(p, ['intro', 'cards', 'stats'], .55 if withimg else .9)
    r = pg(n); H_, C_ = sid(n, 'h'), sid(n, 'c')
    size = 56 if rows <= 2 else 40
    grid = f'display:grid;grid-template-columns:repeat({cols},{wd(1, span)}px);column-gap:{GUT}px;row-gap:{2 * LH}px'; gcls = f'cn-g{cols}'
    if line:   # 线条式（FAQ、须知）：条目钉在下沿、细线分隔；上方撞色色块装标题（色块吸收长短）
        sf = choose('CARDS', p, [('line', 'B'), ('line', 'A')])[1]; F_ = sid(n, 'f')
        cells = ''.join(f'<div class="cn-card cn-top1 cn-snap">{num(f"{i:02d}", 20, 36, deco=True) if p.get("num", True) is not False else ""}<div class="cn-h cn-t20 cn-snap">{T_(c.get("t", ""))}</div>{TX(c.get("x"))}{TX(c.get("items"))}</div>' for i, c in enumerate(cs, 1))
        body = field(0, 0, W, 10, sf, y1r=f'{C_}.top-2|{H_}.bottom+1', id_=F_, attr=f' data-clear="{C_}"')
        body += stack(1, 6, r, [f'<div class="{gcls}" style="{grid};row-gap:{LH}px">{cells}</div>'], bot=LAST, id_=C_)
        body += stack(1, 6, r, head(p, 112, 6, 44, icols=6) + [stats_row(p.get('stats'))], top=0, sf=sf, id_=H_, inside=F_, y1=f'{C_}.top-4')
        return emit(n, p, r, 'paper', body, sf)
    if withimg:   # 带图：页头在一条撞色色带里，卡片按行平分剩下的高度，图片吃掉多余的高度
        name, sf = choose('CARDS', p, [('band', 'A'), ('band', 'B')])
        body = field(0, 0, W, 10, sf, y1r=f'{H_}.bottom+1')
        body += stack(1, 6, r, head(p, 80, 6, 44, icols=6) + [stats_row(p.get('stats'))], top=0, sf=sf, id_=H_)
        rws = ''.join(f'<div class="cn-row {gcls}" style="{grid};align-items:stretch">' + ''.join(card_html(i, c, p, 40, True) for i, c in enumerate(cs[j * cols:(j + 1) * cols], j * cols + 1)) + '</div>' for j in range(rows))
        body += f'<div class="cn-a cn-rows" data-rows="1" data-gap="2" data-y0="{H_}.bottom+3" style="left:{x(1, r)}px;width:{wd(1, 6)}px;top:{y(L(10))}px;height:{y(LAST) - y(L(10))}px">{rws}</div>'
        return emit(n, p, r, 'paper', body, sf)
    name, sf = choose('CARDS', p, [('top', 'A'), ('full', 'B'), ('top', 'B'), ('full', 'A')])
    cells = ''.join(card_html(i, c, p, size) for i, c in enumerate(cs, 1))
    big = f'<div class="cn-a cn-num deco"{h.DECO} style="right:{round(-30 * K)}px;top:{round(-96 * K)}px;font-size:{round(480 * K)}px;line-height:{round(480 * K)}px;color:{tokens(sf)["num"]}">{k}</div>' if p.get('count', True) is not False and G.get('STYLE') != 'stijl' else ''
    hc = 6 if p.get('count', True) is False else 4 if r else 3
    hd = head(p, 112, hc, 40 if hc == 3 else 48, icols=hc) + [stats_row(p.get('stats'), hc)]   # 三栏宽的标题允许缩到 40px，免得在词中间断开
    if name == 'top':   # 上半页撞色色块（长到卡片上方 2 行）+ 巨型条目数；卡片钉在下沿
        body = field(0, 0, W, 10, sf, y1r=f'{C_}.top-2|{H_}.bottom+1', id_=sid(n, 'f'), attr=f' data-clear="{C_}"') + big
        body += stack(1, 6, r, [f'<div class="{gcls}" style="{grid}">{cells}</div>'], bot=LAST, id_=C_)
        body += stack(1, hc, r, hd, top=0, sf=sf, id_=H_, inside=sid(n, 'f'))
        return emit(n, p, r, 'paper', body, sf)
    body = big + stack(1, 6, r, [f'<div class="{gcls}" style="{grid}">{cells}</div>'], bot=LAST, sf=sf, id_=C_)   # 整页撞色
    body += stack(1, hc, r, hd, top=0, sf=sf, id_=H_, y1=f'{C_}.top-1')
    emit(n, p, r, sf, body, sf)

# ---------------------------------------------------------------- STAGGER 错位：2–4 组图文，棋盘式交替
def STAGGER(n, p):
    its = [IT(c) for c in listify(p.get('items'))]; h.LIMIT('STAGGER', its, 2, 4, 'items 条目'); h.BUDGET(p, ['intro', 'items'], .5)
    if not its: return
    r = pg(n); H_ = sid(n, 'h'); v = h.VAR('STAGGER', 2)
    name, dom = choose('STAGGER', p, [('check', 'A'), ('paper', 'paper')])
    body = stack(1, 6, r, head(p, 80, 6, 44, icols=4), top=0, id_=H_)
    first = field_color(); rows = []
    for i, it in enumerate(its):
        flip = (i + v + (0 if r else 1)) % 2 == 1          # 图在左 / 在右，逐行交替
        sf = (first if i % 2 == 0 else other(first)) if name == 'check' else 'paper'
        cut = gc(3, r)
        iw, tw = (W - cut, cut) if flip else (cut, W - cut)
        tl = 14 if not flip else (x(1, r)); tr = (W - xe(6, r)) if not flip else 14
        import stijl
        compact = len(its) >= 3
        number = num(f'{i + 1:02d}', round(28 * S) if compact else 56, LH if compact else 72,
                     cls='cn-entry-index' if compact else 'cn-ino', style=stijl.bar(i)) if p.get('num', True) is not False else ''
        heading = 'cn-t20' if compact else 'cn-t28'
        txt = number + lab(it.get('k'), deco=False) + f'<div class="cn-h {heading} cn-snap">{T_(it.get("t", ""))}</div>' + TX(it.get('x')) + TX(it.get('items'))
        im = f'<div class="cn-ibox" data-minh="96">{pic(it.get("img"), iw, 300, i + 1, other(sf) if sf != "paper" else "A")}</div>'
        pad = LH // 2 if compact else LH
        cell = f'<div class="cn-cell" style="background:{tokens(sf)["bg"]};{vs(sf)}padding:{pad}px {tr}px {pad}px {tl}px"><div class="cn-snap" style="width:{wd(1, 3)}px">{txt}</div></div>'
        rows.append(f'<div class="cn-row" style="display:grid;grid-template-columns:{iw if not flip else tw}px {tw if not flip else iw}px">{im if not flip else cell}{cell if not flip else im}</div>')
    body += f'<div class="cn-a cn-rows" data-rows="1" data-gap="0" data-y0="{H_}.bottom+2" style="left:0;width:{W}px;top:{y(L(8))}px;height:{y(LAST) - y(L(8))}px">{"".join(rows)}</div>'
    emit(n, p, r, 'paper', body, dom)

# ---------------------------------------------------------------- TWO 双栏：两三栏文字，或带图条目的格子
def col_html(c, rule='cn-top2'):
    return f'<div class="cn-card {rule} cn-snap">{lab(c.get("k"), deco=False)}<div class="cn-h cn-t20 cn-snap">{T_(c.get("t", ""))}</div>{TX(c.get("x"))}{TX(c.get("items"))}</div>'
def TWO(n, p):
    r = pg(n); H_, C_ = sid(n, 'h'), sid(n, 'c'); v = p.get('image')
    its = [IT(c) for c in listify(p.get('items'))]; withimg = any('img' in i for i in its)
    if p.get('columns') or not withimg:
        cs = [IT(c) for c in listify(p.get('columns'))] or its
        if p.get('columns'): h.LIMIT('TWO', cs, 2, 3, 'columns 栏')
        else: h.LIMIT('TWO', cs, 2, 8, 'items 条目')
        h.BUDGET(p, ['intro', 'columns', 'items'], .75)
        k = len(cs); nc = 3 if k == 3 or (k > 4 and k % 3 == 0) else 2; span = 6 // nc
        grid = f'<div class="cn-g{nc}" style="display:grid;grid-template-columns:repeat({nc},{wd(1, span)}px);column-gap:{GUT}px;row-gap:{2 * LH}px">' + ''.join(col_html(c) for c in cs) + '</div>'
        if v:   # 顶部出血照片，长到文字上方 2 行
            body = box(0, 0, W, 10, pic(v, W, nrows(420, 15) * LH, 1, field_color()), 'cn-pic', y1r=f'{C_}.top-2', minh=nrows(200, 8) * LH)
            body += stack(1, 6, r, head(p, 80, 6, 44, icols=6) + [f'<div class="m2">{grid}</div>'], bot=LAST, id_=C_)
            return emit(n, p, r, 'paper', body, 'image')
        name, sf = choose('TWO', p, [('top', 'A'), ('top', 'B')])
        F_ = sid(n, 'f')
        body = field(0, 0, W, 10, sf, y1r=f'{C_}.top-2|{H_}.bottom+1', id_=F_, attr=f' data-clear="{C_}"') + stack(1, 6, r, [grid], bot=LAST, id_=C_)
        body += stack(1, 6, r, head(p, 112, 6, 56, icols=6), top=0, sf=sf, id_=H_, inside=F_, y1=f'{C_}.top-4')
        return emit(n, p, r, 'paper', body, sf)
    h.LIMIT('TWO', its, 2, 8, 'items 条目'); h.BUDGET(p, ['intro', 'items'], .55)
    name, sf = choose('TWO', p, [('grid', 'A'), ('grid', 'B')])
    body = field(0, 0, W, 10, sf, y1r=f'{H_}.bottom+1') + stack(1, 6, r, head(p, 80, 5, 44, icols=4), top=0, sf=sf, id_=H_)
    rows = -(-len(its) // 2); out = []
    for j in range(rows):
        cells = []
        for i, it in enumerate(its[j * 2:j * 2 + 2], j * 2):
            up = (j + h.VAR('TWO', 2)) % 2 == 0     # 图在上 / 在下，逐行交替（锯齿）
            im = f'<div class="cn-ibox" data-minh="72">{pic(it.get("img"), 308, 200, i + 1, "A" if i % 2 else "B")}</div>'
            pd = f'{LH // 2}px 0 0' if up else f'0 0 {LH // 2}px'
            tx = f'<div class="cn-snap" style="padding:{pd}">{lab(it.get("k"), deco=False)}<div class="cn-h cn-t20 cn-snap">{T_(it.get("t", ""))}</div>{TX(it.get("x"))}{TX(it.get("items"))}</div>'
            cells.append(f'<div class="cn-flexcol">{im + tx if up else tx + im}</div>')
        out.append(f'<div class="cn-row" style="display:grid;grid-template-columns:repeat(2,{wd(1, 3)}px);column-gap:{GUT}px">{"".join(cells)}</div>')
    body += f'<div class="cn-a cn-rows" data-rows="1" data-gap="2" data-y0="{H_}.bottom+3" style="left:{x(1, r)}px;width:{wd(1, 6)}px;top:{y(L(10))}px;height:{y(LAST) - y(L(10))}px">{"".join(out)}</div>'
    emit(n, p, r, 'paper', body, sf)

# ---------------------------------------------------------------- GRID 网格：日程、费用、时间轴、目录、大量条目
GRIDKEYS = ('facts', 'table', 'timeline', 'items', 'notes', 'toc')
def chapters():
    """toc: auto —— 把带 index 的 FULL 页（章节页）收集成目录：(编号, 标题, 副题, 页码)"""
    out = []; m = 1
    for q in h.SPEC['pages']:
        lay = q.get('layout')
        if lay == 'FULL' and q.get('index') is not None:
            out.append([str(q['index']), q.get('title', ''), q.get('en') or q.get('sub') or q.get('intro') or '', m])
        m += h.LAY.get(lay, (None, 1))[1]
    return out
def toc_es(p):
    """目录条目 [编号, 标题, 描述, 页码]；toc: auto 从章节页收集"""
    if p['toc'] == 'auto': return chapters()
    return [list(e) + [''] * (4 - len(e)) if isinstance(e, (list, tuple)) else [e.get('no', ''), e.get('t', ''), e.get('x', ''), e.get('page', '')] for e in listify(p['toc'])]
TOC_DEG = [0]   # GRID.toc 容量降级档（sec_html 按页设置，GRID 读它决定去不去页头导语）：0 完整 · 1 描述截到一行 · 2 再降字号档 · 3 再去页头导语
def toc_need(es, p, big, clamp, intro):
    """粗估目录页要多少行：页头 9 行（+ 导语 3 行）+ 每块 2 行；每条目录大档 8 行 / 小档 4 行，标题、描述折行往上加（clamp：描述只算一行）"""
    L = 9 + (3 if intro else 0) + 2
    cpl = (wd(1, 3) + GUT) // BS if h.CJK else round((wd(1, 3) + GUT) / BS * 2.2)   # 中间一栏（标题 + 描述）每行约多少字
    for e in es:
        no, t, s = (list(e) + [''] * 3)[:3]
        body = 1 + -(-chars(t) // max(1, cpl)) + (0 if clamp or not s else -(-chars(s) // max(1, cpl)))
        L += max(8 if big else 4, body)
    return L
def toc_deg(es, p):
    """4 章目录 + 页头常超出版心（约 350px）→ 自动降级让位：① 描述截到一行（CSS 省略号，不改文字）② 字号降档（8 行/条 → 4 行/条）③ 去页头导语。
    按行数估算选档，不硬编码坐标；降完仍放不下就保持 3，由 fill.js 报溢出（提示拆成两页目录）。"""
    for d in (0, 1, 2, 3):
        if toc_need(es, p, d < 2, d >= 1, d < 3) <= LAST - 1: return d
    return 3
def sec_html(key, p, r):
    if key == 'facts':
        fs = [f if isinstance(f, (list, tuple)) else [f, ''] for f in listify(p['facts'])]
        nc = min(4, len(fs)) or 1; size = 80 if nc <= 3 else 56
        return f'<div class="cn-stats" style="grid-template-columns:repeat({nc},minmax(0,1fr));row-gap:{LH}px">' + ''.join(f'<div class="cn-top2 cn-snap" style="padding-top:{LH // 2}px">{num(a, size, size + 16, deco=False)}<div class="cn-cap">{T_(b)}</div></div>' for a, b in fs) + '</div>'
    if key == 'timeline':
        tl = [IT(t) if isinstance(t, dict) else dict(zip(('k', 't', 'x'), t)) if isinstance(t, (list, tuple)) else dict(t=t) for t in listify(p['timeline'])]
        k = len(tl); comp = k > 6 or GRID_TIGHT[0]
        rows = []
        for i, it in enumerate(tl):
            t_, x_ = str(it.get('t', '')), it.get('x')
            if x_ is None and ' · ' in t_ and not comp: t_, x_ = t_.split(' · ', 1)
            hot = bool(it.get('hot'))
            dot = 18 if hot else 10
            rows.append(f'<div class="cn-tl{" hot" if hot else ""}" style="grid-template-columns:{wd(1, 1) + GUT}px 1fr;min-height:{2 * LH if comp else 3 * LH}px;margin-top:{0 if i == 0 or comp else LH}px">'
                        f'<span class="cn-dot" style="left:{10 - dot // 2}px;top:{(LH // 2 if comp else round(LH * .75)) - dot // 2}px;width:{dot}px;height:{dot}px"></span>'
                        f'<div class="cn-lab" style="padding-left:34px;margin-top:{0 if comp else LH // 4}px">{T_(it.get("k", ""))}</div>'
                        f'<div><div class="cn-h {"" if comp else "cn-t28"}">{T_(t_)}</div>' + (f'<div class="cn-mut">{T_(x_)}</div>' if x_ else '') + '</div></div>')
        return f'<div class="cn-tls{" comp" if comp else ""}">{"".join(rows)}</div>'
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
        return f'<div class="cn-g{nc}" style="display:grid;grid-template-columns:repeat({nc},{wd(1, span)}px);column-gap:{GUT}px;row-gap:{LH}px">' + ''.join(col_html(c, 'cn-top1') for c in its) + '</div>'
    if key == 'notes':
        return f'<div class="cn-notes">{bullets(listify(p["notes"]))}</div>'
    if key == 'toc':
        es = toc_es(p)
        if p['toc'] == 'auto' and not es: h.WARN.append(f'第{h.CURN}页：toc: auto 没找到章节页（带 index 的 FULL 页）')
        TOC_DEG[0] = toc_deg(es, p)
        if TOC_DEG[0]:
            what = '描述截到一行' if TOC_DEG[0] == 1 else '字号降档' if TOC_DEG[0] == 2 else '去页头导语'
            more = '；降完仍超出版心，建议拆成两页目录' if toc_need(es, p, False, True, False) > LAST - 1 else '；还要完整显示就拆成两页目录'
            h.WARN.append(f'第{h.CURN}页：目录 + 页头超出版心，已自动降级（{what}）{more}')
        big = len(es) <= 5 and TOC_DEG[0] < 2
        clamp = TOC_DEG[0] >= 1
        def row(no, t, s, pg_):
            link = str(pg_).isdigit()   # 目录行可点（HTML 和 PDF 里都能跳页）
            pn = f'{int(pg_):02d}' if link else T_(pg_)
            return ((f'<a class="cn-tocr cn-top1 cn-snap" href="#p{int(pg_)}"' if link else '<div class="cn-tocr cn-top1 cn-snap"')
                    + f' style="grid-template-columns:{wd(1, 2) + GUT}px {wd(1, 3) + GUT}px {COL}px;min-height:{8 * LH if big else 4 * LH}px">'
                    + f'{num(no, 112 if big else 56, 120 if big else 72)}<div style="padding-top:{LH}px"><div class="cn-h {"cn-t40" if big else "cn-t28"}">{T_(t)}</div>'
                    + (f'<div class="cn-mut" style="{"white-space:nowrap;overflow:hidden;text-overflow:ellipsis" if clamp else ""}">{T_(s)}</div>' if s else '') + '</div>'
                    + f'<div class="cn-num" style="font-size:{round(28 * S)}px;line-height:{round(1.5 * LH)}px;text-align:right;padding-top:{LH}px;color:var(--fg)"{h.DECO}>{pn}</div>'
                    + ('</a>' if link else '</div>'))
        return '<div class="cn-toc">' + ''.join(row(*e) for e in es) + '</div>'
    return ''
GRID_TIGHT = [False]
def grid_lines(p):
    """粗估 GRID 一页要多少行（不含时间轴的压缩）：页头 + 各块；超过版心就把时间轴压成紧凑式"""
    L = 9 + (3 if p.get('intro') else 0)
    cpl = wd(1, 6) // BS if h.CJK else round(wd(1, 6) / BS * 2.2)
    for k in GRIDKEYS:
        if k not in p: continue
        L += 2
        v = listify(p[k]) if k != 'table' else None
        if k == 'timeline': L += 4 * len(v)
        elif k == 'table': tb = p['table']; L += 1.5 * (len((tb.get('rows') if isinstance(tb, dict) else tb) or []) + (1 if isinstance(tb, dict) and tb.get('head') else 0))
        elif k == 'facts': L += 5
        elif k == 'notes': L += sum(max(1, -(-chars(x) // cpl)) for x in v)
        elif k == 'items': L += 5 * -(-len(v) // 3)
        elif k == 'toc': L += (8 if len(v) <= 5 else 4) * len(v) if v != ['auto'] else 32
    return L
def GRID(n, p):
    h.BUDGET(p, ['intro'] + list(GRIDKEYS), 1.1)
    GRID_TIGHT[0] = grid_lines(p) > LAST - 1
    TOC_DEG[0] = 0   # 每页重置；sec_html('toc') 按容量设档，head 的导语跟着让位
    r = pg(n); M_, N_ = sid(n, 'm'), sid(n, 'n'); v = p.get('image')
    keys = [k for k in p if k in GRIDKEYS]
    if keys and set(keys) <= {'facts', 'notes'} and not v:   # 只有大数字：数字做成整页的主角（2×2，钉在下沿），页头在上
        name, sf = choose('GRID', p, [('full', 'A'), ('full', 'B')])
        fs = [f if isinstance(f, (list, tuple)) else [f, ''] for f in listify(p['facts'])][:6]
        nc = 2 if len(fs) in (2, 4) else 3; size = round((160 if nc == 2 and len(fs) <= 4 else 112) * K // 8 * 8) if K < 1 else (160 if nc == 2 and len(fs) <= 4 else 112)
        cw = (wd(1, 6) - (nc - 1) * GUT) / nc
        em = max(sum(.3 if ch in ',.:' else .66 for ch in str(a)) for a, _ in fs) or 1   # 最长的数字大约几个 em 宽（“30,000+”≈ 4.3em）
        if size * em > cw: size = max(40, int(cw / em) // 8 * 8)                          # 放不下就整组一起缩小，保持一样大
        cells = ''.join(f'<div class="cn-top2 cn-snap" style="padding-top:{LH // 2}px">{num(a, size, size + LH, deco=False)}<div class="cn-h cn-t20">{T_(b)}</div></div>' for a, b in fs)
        kids = [f'<div class="cn-stats" style="grid-template-columns:repeat({nc},minmax(0,1fr));row-gap:{2 * LH}px">{cells}</div>']
        if p.get('notes'): kids.append(f'<div class="cn-notes m2">{bullets(listify(p["notes"]))}</div>')
        body = stack(1, 6, r, kids, bot=LAST, sf=sf, id_=N_) + stack(1, 6, r, head(p, 112, 6, 48, icols=4), top=0, sf=sf, id_=M_)
        return emit(n, p, r, sf, body, sf)
    vs_ = [('full', 'A'), ('paper', 'paper'), ('full', 'B')] if not v else [('paper', 'paper'), ('full', 'A'), ('full', 'B')]
    name, sf = choose('GRID', p, vs_)
    notes_band = (name == 'paper' or QUIET()) and 'notes' in keys and not v   # 单色档没有整页色块：备注总是放进底部浅灰色带
    secs = [f'<div class="cn-sec cn-snap m2" data-g="2">{sec_html(k, p, r)}</div>' for k in keys if not (notes_band and k == 'notes')]
    main = head(p, 80, 6, 44, icols=6, intro=TOC_DEG[0] < 3) + secs   # 目录放不下时最后才去页头导语（TOC_DEG 3 档）
    body = ''
    if notes_band:   # 纸面 + 底部一条撞色色带装备注
        bsf = field_color()
        body += field(0, 10, W, H, bsf, y0r=f'{N_}.top-1', attr=f' data-below="{M_}"')   # QA：上面的正文不能压进色带
        body += stack(1, 6, r, [sec_html('notes', p, r)], bot=LAST, sf=bsf, id_=N_)
        body += stack(1, 6, r, main, top=0, sf='paper', id_=M_)
        return emit(n, p, r, 'paper', body, 'paper', fsf=bsf)
    body += stack(1, 6, r, main, top=0, sf=sf if name == 'full' else 'paper', id_=M_)
    if v and name == 'paper':
        body += box(0, 10, W, y(LAST), pic(v, W, nrows(300, 11) * LH, 1, field_color()), 'cn-pic', y0r=f'{M_}.bottom+2', minh=96)
    emit(n, p, r, sf if name == 'full' else 'paper', body, sf if name == 'full' else ('image' if v else 'paper'))

# ---------------------------------------------------------------- COLLAGE 拼贴：3–7 张照片满版拼接（3px 细缝）+ 一块撞色模块
# 每个格子：(类型, x0, x1, y0, y1)；x 用 'E0'/'E1'（页边）或栏号 k（第 k 栏右边栏间的中线）；y 用 0 / 'H'（页边）或行号
PART = {3: [('i', 'E0', 3, 0, 'H'), ('i', 3, 'E1', 0, 12), ('m', 3, 'E1', 12, 30), ('i', 3, 'E1', 30, 'H')],
        4: [('i', 'E0', 3, 0, 18), ('i', 'E0', 3, 18, 'H'), ('i', 3, 'E1', 0, 12), ('m', 3, 'E1', 12, 30), ('i', 3, 'E1', 30, 'H')],
        5: [('i', 'E0', 3, 0, 13), ('i', 3, 'E1', 0, 13), ('m', 'E0', 3, 13, 30), ('i', 3, 'E1', 13, 30), ('i', 'E0', 3, 30, 'H'), ('i', 3, 'E1', 30, 'H')],
        6: [('i', 'E0', 3, 0, 12), ('i', 3, 'E1', 0, 12), ('m', 'E0', 3, 12, 29), ('i', 3, 'E1', 12, 29), ('i', 'E0', 2, 29, 'H'), ('i', 2, 4, 29, 'H'), ('i', 4, 'E1', 29, 'H')],
        7: [('i', 'E0', 2, 0, 11), ('i', 2, 4, 0, 11), ('i', 4, 'E1', 0, 11), ('m', 'E0', 3, 11, 28), ('i', 3, 'E1', 11, 28), ('i', 'E0', 2, 28, 'H'), ('i', 2, 4, 28, 'H'), ('i', 4, 'E1', 28, 'H')]}
def COLLAGE(n, p):
    ims = listify(p.get('images')); h.LIMIT('COLLAGE', ims, 3, 7, 'images 图片'); h.BUDGET(p, ['intro', 'text'], .2)
    if not 3 <= len(ims) <= 7: return
    r = pg(n); flip = h.VAR('COLLAGE', 2) == 1
    caps = listify(p.get('captions')); msf = field_color(); S = 3
    def X(v): return 0 if v == 'E0' else W if v == 'E1' else gc(v, r)
    def Y(v): return 0 if v == 0 else H if v == 'H' else y(L(v))   # 行号按 A4 紧凑网格（38 行）写，换算到当前网格
    def M(v): return 'E1' if v == 'E0' else 'E0' if v == 'E1' else 6 - v      # 镜像：按栏号翻转，模块仍然对齐本页的栏
    body = ''; k = -1; M_ = sid(n, 'm')
    for kind, a, b, c, d in PART[len(ims)]:
        if flip: a, b = M(b), M(a)
        x0, x1, y0, y1 = X(a), X(b), Y(c), Y(d)
        x0 += S if x0 > 0 else 0; x1 -= S if x1 < W else 0; y0 += S if y0 > 0 else 0; y1 -= S if y1 < H else 0
        if kind == 'm':
            body += box(x0, y0, x1, y1, '', 'cn-field', f'background:{tokens(msf)["bg"]}', id_=M_ + 'f')
            c0, c1 = (1, 3) if a == 'E0' else (4, 6)
            legend = ''.join(f'<span class="cn-lg"><span class="cn-num" style="font-size:{BS}px;color:var(--acc)">{i + 1}</span> {T_(cp)}</span>' for i, cp in enumerate(caps[:len(ims)]) if cp)
            kids = [lab(p.get('kicker')), disp(p.get('title'), 64, 3, 32, lines=2), sub(p.get('en') or p.get('sub'), cols=3), para(listify(p.get('text')) or p.get('intro'), m=1, cols=3),
                    f'<div class="cn-cap cn-legend m1">{legend}</div>' if legend else '']
            body += stack(c0, c1, r, kids, top=L(c) + 1, sf=msf, id_=M_, inside=M_ + 'f')
            continue
        k += 1
        body += box(x0, y0, x1, y1, pic(ims[k], x1 - x0, y1 - y0, k + 1, msf if k % 2 else other(msf)), 'cn-pic')
        if k < len(caps) and caps[k]:   # 图上只放编号，图注集中写在模块里（图上不压字）
            body += f'<div class="cn-a cn-chip"{h.DECO} style="left:{x1 - 24}px;top:{y1 - 24}px">{k + 1}</div>'
    emit(n, p, r, 'image', body, 'image', fo=False)

# ---------------------------------------------------------------- MIX 组合：主图 + 撞色色带 + 分栏文字；或 竖叠照片 + 文字
def MIX(n, p):
    ss = [IT(c) for c in listify(p.get('sections'))]; h.LIMIT('MIX', ss, 1, 4, 'sections 分段')
    ims = listify(p.get('images')) or ([p['image']] if p.get('image') else [])
    kind = p.get('variant') or ('side' if len(ims) >= 2 else 'hero'); h.BUDGET(p, ['intro', 'sections', 'quote'], .55)
    r = pg(n); H_, C_ = sid(n, 'h'), sid(n, 'c')
    if kind == 'hero':
        sf = choose('MIX', p, [('hero', 'A'), ('hero', 'B')])[1]
        nc = len(ss) if len(ss) <= 3 else 2; span = 6 // nc
        cols = f'<div class="cn-g{nc}" style="display:grid;grid-template-columns:repeat({nc},{wd(1, span)}px);column-gap:{GUT}px;row-gap:{LH}px">' + ''.join(col_html(s) for s in ss) + '</div>'
        bot = [cols, quote(p.get('quote'), p.get('by'), 2) if p.get('quote') else '']
        body = stack(1, 6, r, bot, bot=LAST, id_=C_)
        body += box(0, 0, W, 10, pic(ims[0] if ims else None, W, nrows(420, 15) * LH, 1, other(sf)), 'cn-pic', y1r=f'{H_}.top-1', minh=nrows(200, 8) * LH)
        body += field(0, 10, W, 20, sf, y0r=f'{H_}.top-1', y1r=f'{H_}.bottom+1')
        body += stack(1, 6, r, head(p, 80, 6, 44, icols=6, lines=2), sf=sf, id_=H_, y1=f'{C_}.top-3')
        return emit(n, p, r, 'paper', body, 'image')
    # side：照片竖叠在切口一侧（满版出血、3px 细缝），有引语时换成一块撞色色块装引语；文字在订口一侧三栏
    sf = choose('MIX', p, [('side', 'A'), ('side', 'B')])[1]
    tc = side_cols(r, inner=True); cut = gc(3, r)
    ox0, ox1 = (cut, W) if r else (0, cut)
    tiles = ims[:3]; q = p.get('quote')
    rows = ''.join(f'<div class="cn-row"><div class="cn-ibox" data-minh="96" style="height:100%">{pic(v_, ox1 - ox0, nrows(300, 11) * LH, i + 1, other(sf))}</div></div>' for i, v_ in enumerate(tiles))
    if q:
        oc = (4, 6) if r else (1, 3); tx0 = ox0 + (3 if r else 0); tx1 = ox1 - (0 if r else 3)
        qs = (f'<div class="cn-row"><div class="cn-cell" style="height:100%;background:{tokens(sf)["bg"]};{vs(sf)}padding:{LH}px {tx1 - xe(oc[1], r)}px {LH}px {x(oc[0], r) - tx0}px">'
              f'<div class="cn-snap" style="width:{wd(*oc)}px">{quote(q, p.get("by"))}</div></div></div>')
        rows = rows + qs if len(tiles) < 3 else rows[:rows.rfind('<div class="cn-row">')] + qs
    body = f'<div class="cn-a cn-rows" data-rows="1" data-gap="6px" style="left:{ox0 + (3 if r else 0)}px;width:{ox1 - ox0 - 3}px;top:0;height:{H}px">{rows}</div>'
    secs = ''.join(f'<div class="cn-card cn-top2 cn-snap m{1 if i else 2}">{lab(s.get("k"), deco=False)}<div class="cn-h cn-t20 cn-snap">{T_(s.get("t", ""))}</div>{TX(s.get("x"))}{TX(s.get("items"))}</div>' for i, s in enumerate(ss))
    body += stack(*tc, r, head(p, 80, 3, 40, icols=3) + [secs], top=0, id_=H_)
    emit(n, p, r, 'paper', body, 'image', fspan=tc)

# ------------------------------------------------ 编辑型变奏：沿用六栏，内部 CSS Grid 自然流动。
# 结构只决定跨栏和阅读顺序；颜色、字体仍由 tokens / styles / fonts 接管。
def editorial_grid(cells, gap=1):
    """cells: (起栏, 占栏数, HTML, 起点错开行数)。不锁行高，不按字数截断。"""
    out = []
    for start, span, content, offset in cells:
        out.append(f'<div class="cn-ed-cell" style="grid-column:{start}/span {span};padding-top:{offset * LH}px">{content}</div>')
    return f'<div class="cn-ed-grid" style="row-gap:{gap * LH}px">{"".join(out)}</div>'

def editorial_surface(p):
    sf = SURF_ALIAS.get(str(p.get('surface', 'paper')).lower())
    if sf not in ('paper', 'A', 'B', 'dark'):
        raise ValueError('编辑阅读版式 surface 可选 paper / A / B / dark')
    return sf

def editorial_head(p, size=80):
    return [lab(p.get('kicker'), deco=False),
            '<div class="cn-ed-rule"></div>',
            disp(p.get('title'), round(size * K), 6, round(40 * K), m=1),
            sub(p.get('sub') or p.get('en'), m=1)]

def editorial_page(n, p, kids, sf=None):
    sf = sf or editorial_surface(p)
    body = stack(1, 6, pg(n), kids, top=0, sf=sf, cls='cn-editorial', id_=sid(n, 'editorial'))
    return emit(n, p, pg(n), sf, body, sf)

def editorial_quote(p):
    if not p.get('quote'): return ''
    return (f'<div class="cn-ed-pause cn-snap m2"><div class="cn-qt">{T_(p["quote"])}</div>'
            + (lab(p.get('by'), m=1, deco=False) if p.get('by') else '') + '</div>')

def RHYTHM(n, p):
    """侧导语 → 主要论述 → 跨栏停顿 → 错位双栏续读；适合有明确论述的短文章。"""
    text = listify(p.get('text'))
    kids = editorial_head(p, 96)
    opening = editorial_grid([(1, 2, para(p.get('intro'), flow='keep'), 0),
                              (3, 4, para(text[:1], flow='keep'), 1)])
    kids += [f'<div class="m2">{opening}</div>', editorial_quote(p)]
    if len(text) > 1:
        # 每个段落保持完整，Grid 按内容决定下一行高度，不把一个句子切去下一栏。
        cells = [(1 if i % 2 == 0 else 4, 3, para(t, flow='keep'), i % 2)
                 for i, t in enumerate(text[1:])]
        kids += [f'<div class="m2">{editorial_grid(cells)}</div>']
    return editorial_page(n, p, kids)

def MARGINALIA(n, p):
    """4+2 主文与旁注一一成组；旁注再长也不会掉到下一段旁边。"""
    sections = listify(p.get('sections'))
    if not sections: raise ValueError('MARGINALIA 需要 sections: [{t, x, note_title, note}]')
    kids = editorial_head(p)
    if p.get('intro'): kids.append(lead(p['intro'], 1, 4))
    for i, s in enumerate(sections):
        if not isinstance(s, dict): raise ValueError('MARGINALIA 的每个 section 需要 x 正文，可加 t / note_title / note')
        main = (f'<div class="cn-h cn-t20 cn-snap">{T_(s["t"])}</div>' if s.get('t') else '') + para(s.get('x'), m=1 if s.get('t') else 0, flow='keep')
        note = (lab(s.get('note_title'), deco=False) + para(s.get('note'), flow='keep'))
        aside = f'<aside class="cn-ed-note">{note}</aside>' if note else ''
        kids.append(f'<div class="m2">{editorial_grid([(1, 4, main, 0), (5, 2, aside, 1)])}</div>')
        if i == 0: kids.append(editorial_quote(p))
    return editorial_page(n, p, kids)

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
    # 文本仍在六轨版心；摄影区可独立延伸至裁切边，图注跟着所属figure。
    outer = f' style="position:relative;padding-top:{rows * LH}px"' if top else ''
    image_style = (f'position:absolute;top:{-top}px;' if top else 'position:relative;')
    image_style += f'left:{-left}px;width:{width}px;height:{height}px'
    tag = ' data-bleed="edge"' if any(bleed) else ''
    return (f'<figure class="cn-ed-figure" data-image-role="{role}"{outer}{tag}><div class="cn-pic" style="{image_style}">{im}</div>'
            + (f'<figcaption class="cn-cap m1">{T_(caption)}</figcaption>' if caption else '') + '</figure>')

def photo_bleed(n, p):
    mode = p.get('bleed', 'edge')
    if mode not in ('edge', 'inset'): raise ValueError('摄影布局 bleed 可选 edge（到裁切边）/ inset（明确的版心内构图）')
    return (x(1, pg(n)), W - xe(6, pg(n))) if mode == 'edge' else (0, 0)

def PLATE(n, p):
    """主图与编号解读：观察图 / 标本 / 器物 / 示意图；图文两侧各自自然流动。"""
    sf = editorial_surface(p)
    v = p.get('image')
    v = dict(v) if isinstance(v, dict) else dict(src=v)
    v.setdefault('fit', 'contain')
    v.setdefault('duo', False)   # 图解颜色可能承载含义；主题不自动把它改成双色。
    notes = []
    for i, a in enumerate(listify(p.get('annotations'))):
        a = IT(a)
        notes.append(f'<div class="cn-ed-note cn-snap">{lab(a.get("k", f"{i + 1:02d}"), deco=False)}'
                     + f'<div class="cn-h">{T_(a.get("t", ""))}</div>' + para(a.get('x'), flow='keep') + '</div>')
    figure = editorial_figure(v, 4, L(19), p.get('caption'))
    grid = editorial_grid([(1, 4, figure, 0), (5, 2, ''.join(notes), 1)])
    kids = editorial_head(p) + ([lead(p['intro'], 1, 4)] if p.get('intro') else [])
    kids += [f'<div class="m2">{grid}</div>', para(p.get('text'), m=2, cols=4, flow='keep')]
    return editorial_page(n, p, kids, sf)

def SEQUENCE(n, p):
    """一个主体、两个细节：非等分多图，图注保持与图像绑定。"""
    items = [IT(it) for it in listify(p.get('items'))]
    if len(items) != 3: raise ValueError('SEQUENCE 需要 3 个 items，每个含 img，可加 k / t / x；按主场景、细节、延伸编排')
    def text(it):
        return lab(it.get('k'), deco=False) + (f'<div class="cn-h cn-t20 cn-snap">{T_(it["t"])}</div>' if it.get('t') else '') + para(it.get('x'), m=1, flow='keep')
    first = editorial_grid([(1, 4, editorial_figure(items[0].get('img'), 4, L(11)), 0),
                            (5, 2, text(items[0]), 1)])
    second = editorial_grid([
        (1, 3, editorial_figure(items[1].get('img'), 3, L(8)) + text(items[1]), 0),
        (4, 3, editorial_figure(items[2].get('img'), 3, L(8)) + text(items[2]), 1)])
    return editorial_page(n, p, editorial_head(p, 64) + [f'<div class="m2">{first}</div>', f'<div class="m1">{second}</div>'])

def PHOTO_OPEN(n, p):
    """先看图片，再读标题：六栏主图，下接四栏标题和两栏短导语。"""
    left, right = photo_bleed(n, p)
    figure = editorial_figure(p.get('image'), 6, L(16), p.get('caption'), (left, right, TOP if left or right else 0))
    title = lab(p.get('kicker'), deco=False) + disp(p.get('title'), round(64 * K), 4, round(32 * K))
    title += sub(p.get('sub') or p.get('en'), m=1)
    opening = editorial_grid([(1, 4, title, 0), (5, 2, para(p.get('intro'), flow='keep'), 1)])
    kids = [figure, f'<div class="m1">{opening}</div>', para(p.get('text'), m=1, cols=4, flow='keep')]
    return editorial_page(n, p, kids)

def MASONRY(n, p):
    """六轨合并为三条独立图流：照片先行、接缝错开、下沿收齐，标题与索引在后。"""
    items = [IT(it) for it in listify(p.get('items'))]
    if len(items) != 6: raise ValueError('MASONRY 需要6个items，每个含img与可选caption；不以重复填图补数量')
    left, right = photo_bleed(n, p)
    cells, captions = [], []
    top = TOP if left or right else 0
    rows = L(28)
    gap = LH / 4
    extend = (GUT - gap) / 2
    # 图流共享上下边界，内部接缝不共享行线；外侧跨出页边距，内沿仍落在六轨上。
    for col, first in enumerate((L(10), L(17), L(7))):
        parts = []
        notes = []
        for row, height in enumerate((first, rows - first - gap / LH)):
            i = col * 2 + row
            it = items[i]
            ident = sid(n, 'photo_%s' % (i + 1))
            figure = editorial_figure(it.get('img'), 2, height, None,
                                      (left if col == 0 else extend, right if col == 2 else extend, top if row == 0 else 0), role='supporting')
            # 索引在共同的阅读区；关联保留到单张图，不让六条图注切断图流。
            parts.append(f'<div class="cn-masonry-item" role="group" aria-describedby="{ident}" style="margin-top:{gap if row else 0}px">{figure}</div>')
            notes.append(f'<div class="cn-cap" id="{ident}"><span{h.DECO} aria-hidden="true">{i + 1:02d}</span> {T_(it.get("caption") or "")}</div>')
        cells.append((1 + col * 2, 2, ''.join(parts), 0))
        captions.append((1 + col * 2, 2, ''.join(notes), 0))
    kids = [f'<div class="cn-masonry">{editorial_grid(cells)}</div>',
            lab(p.get('kicker'), m=1, deco=False),
            disp(p.get('title'), round(56 * K), 6, round(32 * K)),
            sub(p.get('sub') or p.get('en')),
            f'<div class="cn-masonry-legend m1">{editorial_grid(captions)}</div>']
    return editorial_page(n, p, kids)

def CONTACT(n, p):
    """大幅场景照片加两行六图索引；尺度、序列与图注共同建立阅读路径。"""
    items = [IT(it) for it in listify(p.get('items'))]
    if len(items) != 6: raise ValueError('CONTACT 需要image主图和6个含img的items')
    left, right = photo_bleed(n, p)
    hero = editorial_figure(p.get('image'), 6, max(7, L(8)), p.get('caption'), (left, right, 0))
    cells = []
    for i, it in enumerate(items):
        col = i % 3
        figure = editorial_figure(it.get('img'), 2, L(5), it.get('caption'),
                                  (left if col == 0 else 0, right if col == 2 else 0, 0), role='supporting')
        cells.append((1 + col * 2, 2, figure, 0))
    return editorial_page(n, p, editorial_head(p, 56) + [f'<div class="m1">{hero}</div>',
                                f'<div class="m1">{editorial_grid(cells)}</div>'])

def READING(n, p):
    """正文先进入视野，篇名与提示居侧栏；每个 YAML 页面保存明确的段落边界。"""
    if not p.get('text'): raise ValueError('READING 需要 text 段落列表；按完整段落分配续页，不把空页当续页')
    import flow
    sf = editorial_surface(p)
    series = p.get('series_header')
    if series:
        if p.get('title'): raise ValueError('READING 使用 series_header 时标题从 book.series 读取；续页小题写在 series_header.title')
        if series.get('continuation') and not os.environ.get('HB_PROOF'):
            current = next((i for i, page in enumerate(h.SPEC['pages']) if page is p), 0)
            key = (series.get('series'), str(series.get('item')))
            prior = [page.get('series_header') or {} for page in h.SPEC['pages'][:current] if page.get('layout') == 'READING']
            if not any((s.get('series'), str(s.get('item'))) == key and not s.get('continuation') for s in prior):
                raise ValueError('READING 续页前缺同一 series/item 的首页；先安排首页，再标 continuation: true')
        identity = flow.B({'series_header': dict(series, compact=True)}, {'w': wd(1, 2), 'sf': sf})
    else:
        if not p.get('title'): raise ValueError('READING 需要 title 或已登记的 series_header')
        identity = lab(p.get('kicker'), deco=False) + f'<div class="cn-h cn-ttl cn-t28">{T_(p["title"])}</div>'
    side = identity + ''.join(f'<div class="cn-ed-note m2">{para(note, flow="keep")}</div>' for note in listify(p.get('notes')))
    main = (lead(p['intro']) if p.get('intro') else '') + para(p.get('text'), m=1 if p.get('intro') else 0, flow='keep')
    offset = 1 if series and series.get('continuation') else L(3)
    grid = editorial_grid([(1, 2, side, offset), (3, 4, main, 0)])
    return editorial_page(n, p, [f'<div class="cn-reading">{grid}</div>'], sf)

RECIPES = {'FULL': FULL, 'ONE': ONE, 'TWO': TWO, 'CARDS': CARDS, 'STAGGER': STAGGER, 'GRID': GRID, 'COLLAGE': COLLAGE, 'MIX': MIX,
           'RHYTHM': RHYTHM, 'MARGINALIA': MARGINALIA, 'PLATE': PLATE, 'SEQUENCE': SEQUENCE,
           'PHOTO_OPEN': PHOTO_OPEN, 'READING': READING, 'MASONRY': MASONRY, 'CONTACT': CONTACT}
