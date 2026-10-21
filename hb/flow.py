#!/usr/bin/env python3
"""flow.py —— 一个排版引擎：照片版式和自由内容块也排在 canon.py 的 6 栏网格上。

为什么：以前照片版式（POSTER / T / B / SL / SR / HOLE / PAPER / 跨页）和内容块（title、p、cards、figure、gallery …）
按像素摆——左右页边一样宽、字号各写各的、图片可以悬空插在底图上。现在它们和 8 个内容版式共用一套底层：
  · 网格：A4 6 栏（栏 80、栏间 32）、订口 50 / 切口 104、天头 88、行距 28；左右页镜像。照片的边落在栏线、行线上，或者满版出血。
  · 字号阶梯：小标签 / 正文 / 导语 / 小标题 / 页标题 / 展示大字，只有这几档（canon.css）；块与块之间隔整行。
    旧 yaml 里写的 size、h、mt、space（像素）自动吸到最近的一档、最近的整行，不用改 yaml。
  · 插图：照片只占整格（照片位）或满版；风格插画只出现在照片位里（没给照片时），不和照片、标题叠在一起。
    图上有字时照片烘焙成页面底图，dark.py 在字下面渐进压暗（对比度达标为止）。
  · 页眉、页码和内容版式同一位置、同一字号。
"""
import re, math, os
import canon as C
h = C.h

# ---------------------------------------------------------------- 尺寸吸附：像素 → 整行 / 整栏 / 字号档
def lines(px, d):
    """旧写法的间距（mt、space，像素）→ 整行数；不到半行算 0"""
    if px is None: return d
    try: v = float(px)
    except (TypeError, ValueError): return d
    return 0 if v < C.LH * .45 else max(1, round(v / C.LH))
def nrows(px, d, lo=2, hi=40):
    """旧写法的高度（h，像素）→ 整行数（照片、方框的高度落在行线上）"""
    try: v = float(px) if px is not None else d * C.LH
    except (TypeError, ValueError): v = d * C.LH
    return max(lo, min(hi, round(v / C.LH)))
def ncols(px, lo=1, hi=6):
    """旧写法的宽度（像素）→ 栏数"""
    try: v = float(px)
    except (TypeError, ValueError): return lo
    return max(lo, min(hi, round((v + C.GUT) / (C.COL + C.GUT))))
DISP = (56, 72, 96, 120, 160)   # 展示大字的几档（A4）；小画布按 K 等比
def tiers():
    """大字能用的字号档：网格字号的 23 · 33 · 47（= 20 / 28 / 40 × S，和 cn-t20 / t28 / t40 一样）+ 展示档 56 · 72 · 96 · 120 · 160"""
    return [round(a * C.S) for a in (20, 28, 40)] + [round(a * C.K) for a in DISP]
def dsize(px, d=56):
    try: v = float(px)
    except (TypeError, ValueError): v = d
    return min(tiers(), key=lambda a: (abs(a - v), -a))   # 正好在两档中间时取大的一档
def dlh(s): q = C.LH / 2; return int(math.ceil(s * 1.04 / q) * q)   # 大字的行高：半行的整数倍
def line_of(px, d):
    """旧写法的页面坐标（split、body_top，像素）→ 第几行"""
    try: v = float(px)
    except (TypeError, ValueError): return d
    return max(0, min(C.LAST, round((v - C.TOP) / C.LH)))
def photo_rows(p, dflt_px, dflt_rows, lo, hi):
    """照片带行数（T 上 / B 下）：
    photo_rows: N 是语义参数——照片带占几行（直接数行，递增单调有效）；
    split: 像素是旧写法——从页顶起算的像素，round((v-88)/28) 换算成行（同一个像素在 6~10 行间会落在同一行，调着纹丝不动）。
    两个参数都接受（都写了以 photo_rows 为准）；越界时收敛到合法范围 [lo, hi] 并 WARN「已按最小/最大照片带收敛」。"""
    if p.get('photo_rows') is not None:
        try: v = int(round(float(p['photo_rows'])))
        except (TypeError, ValueError): v = dflt_rows
        if v < lo: h.WARN.append(f'第{h.CURN}页：photo_rows: {p["photo_rows"]} 小于最小照片带 {lo} 行，已按最小照片带收敛'); v = lo
        elif v > hi: h.WARN.append(f'第{h.CURN}页：photo_rows: {p["photo_rows"]} 大于最大照片带 {hi} 行，已按最大照片带收敛'); v = hi
        return v
    return max(lo, min(hi, line_of(p.get('split', dflt_px), dflt_rows)))
def T(s): return C.T_(s)
def W_(c0, c1): return C.wd(c0, c1)

# ---------------------------------------------------------------- 内容块
# 每个块：第一个认识的键决定类型；渲染出来的东西只用 canon 的字号档和颜色变量（--fg 字 · --hd 标题 · --acc 强调 · --lab 小标签 · --mut 次要 · --rule 粗线 · --line 细线）
KINDS = ('series_header', 'display', 'title', 'en', 'kicker', 'worksheet', 'task', 'p', 'letter', 'items', 'kv', 'step', 'q', 'table', 'field', 'fields', 'lines', 'fill',
         'box', 'boxes', 'choice', 'blanks', 'sign', 'figure', 'gallery', 'stats', 'quote', 'cards', 'qr', 'bars', 'product', 'chips', 'cycle', 'timeline',
         'sheet', 'logos', 'space', 'html', 'caption')
GAP = {'series_header': 1, 'kicker': 1, 'worksheet': 1, 'display': 0, 'title': 1, 'en': 0, 'task': 1, 'p': 1, 'letter': 1, 'items': 1, 'kv': 1, 'step': 1, 'q': 1, 'cols': 1,
       'table': 1, 'field': 0, 'fields': 1, 'lines': 0, 'fill': 0, 'box': 1, 'boxes': 1, 'choice': 1, 'blanks': 1, 'sign': 2, 'figure': 1, 'gallery': 1,
       'stats': 1, 'quote': 2, 'cards': 1, 'qr': 1, 'bars': 1, 'product': 1, 'chips': 1, 'cycle': 1, 'timeline': 1, 'sheet': 1, 'logos': 1, 'space': 0,
       'html': 0, 'caption': 0}
TIGHT = {('kicker', 'title'), ('kicker', 'display'), ('worksheet', 'title'), ('worksheet', 'task'), ('title', 'en'), ('display', 'en'), ('display', 'title'),
         ('display', 'display'), ('kicker', 'task'), ('field', 'field'), ('lines', 'lines'), ('figure', 'caption'), ('gallery', 'caption')}
def kind(b):
    if isinstance(b, str): return 'p'
    if isinstance(b.get('cols'), list): return 'cols'
    for k in KINDS:
        if k in b: return k
    return None

def ln(n): return '<div class="cn-ln"></div>' + '<div class="cn-ln" data-x="1"></div>' * (int(n) - 1) if int(n) > 0 else ''   # data-x：页面放不下时可以收掉的书写线（至少留 1 行）
def fd(label, cls=''): return f'<div class="cn-fd {cls}"><span{h.DECO}>{T(label)}</span><i></i></div>'
def colon(s): return h.esc(str(s).rstrip('：: ')) + h.COLON
def accent_num(t, size, lh=None):
    return f'<span class="cn-num" style="font-size:{size}px;line-height:{lh or C.LH}px;color:var(--acc)">{T(t)}</span>'
def figure(f, hpx, b, width, cap=None):
    """照片 / 截图 / 图表：照片铺满（风格派、瑞士单色自动转黑白；没给图时是色块或风格插画），截图、图表、logo 写 fit: contain 不裁切"""
    fit = b.get('fit', 'cover'); frame = b.get('frame')
    if fit == 'contain' or frame or str(f).lower().endswith('.svg'):
        if str(f).startswith('ai:'): f = h.AIFIG(f, width, hpx, '插图')
        src = h.FIGIMG(f, width * 1.5) if f else ''
        fx, fy = b.get('focus', [.5, .5])
        im = f'<img class="cn-img" alt="" src="{src}" style="object-fit:{fit};object-position:{fx * 100:.0f}% {fy * 100:.0f}%">' if src else ''
    else:
        v = {'src': f, 'focus': b.get('focus', [.5, .5])} if b.get('focus') else f
        im = C.pic(v, width, hpx, 1, 'B', label=False)
    c = f'<div class="cn-cap"{h.DECO}>{T(cap)}</div>' if cap else ''
    primary = b.get('role') == 'primary' or ('h' not in b and width >= C.wd(1, 4))
    mn = min(hpx, max((8 if primary else 3) * C.LH, round(hpx * (.75 if primary else .45) / C.LH) * C.LH))
    return f'<figure class="cn-fig{" fr" if frame else ""}"><div class="cn-figi" data-fh="{hpx}" data-fmin="{mn}" style="height:{hpx}px">{im}</div>{c}</figure>'

# 行宽：导语中文至少四栏，西文至少三栏；西文按当前字号限到60ch，不固定空出右栏。
def wide(width): return width >= C.wd(1, 4 if h.CJK else 3) - 1
def measure(width): return 'max-width:60ch;' if not h.CJK else ''

def image_bleed(b, ctx):
    """出血是项目的图像策略；嵌在文字栏内的图和功能图不隐式越过相邻文字。"""
    bl = b.get('bleed')
    if bl is None and ctx['w'] >= C.wd(1, 6) - 1 and b.get('role') not in ('qr', 'logo', 'diagram'):
        bl = h.BK.get('image_bleed')
    st = ''
    if bl in ('left', 'both'): st += f'margin-left:-{ctx["bl"]}px;'
    if bl in ('right', 'both'): st += f'margin-right:-{ctx["br"]}px;'
    width = ctx['w'] + (ctx['bl'] if bl in ('left', 'both') else 0) + (ctx['br'] if bl in ('right', 'both') else 0)
    return bl, st, width

def B(b, ctx):
    """一个块 → HTML（不含块与块之间的间距）"""
    if isinstance(b, str): b = {'p': b}
    k = kind(b); g = b.get; width = ctx['w']
    if k is None: h.ERR.append(f'第{h.CURN}页：未知内容块 {list(b)[:3]}'); return ''
    if k == 'series_header':
        q = b[k]; name, item = q['series'], str(q['item'])
        series = h.BK.get('series', {}).get(name)
        if not series or item not in series.get('items', {}):
            raise ValueError(f'series_header 找不到 book.series.{name}.items.{item}')
        title = series['items'][item]
        attrs = f' data-series="{h.esc(name)}" data-item="{h.esc(item)}"'
        if q.get('compact'):
            if q.get('title') and not q.get('continuation'):
                raise ValueError('系列首页标题统一从 book.series 读取，不在单页覆盖')
            suffix = (' · 续读' if h.CJK else ' · CONTINUED') if q.get('continuation') else ''
            label = f'{series["label"]} {item}{suffix}'
            return (f'<div class="cn-series-header cn-series-compact"{attrs}>' + C.lab(label)
                    + f'<div class="cn-h cn-ttl cn-t28">{T(q.get("title", title))}</div></div>')
        if q.get('continuation'):
            label = f'{series["label"]} {item} · CONTINUED'
            return (f'<div class="cn-series-header cn-series-cont"{attrs}>' + C.lab(label)
                    + f'<div class="cn-h cn-ttl cn-t40">{T(q.get("title", title))}</div></div>')
        if q.get('title'): raise ValueError('系列首页标题统一从 book.series 读取，不在单页覆盖')
        label = C.lab(series['label'])
        return (f'<div class="cn-series-header"{attrs}>{label}<div class="cn-series-grid" '
                f'style="grid-template-columns:{C.COL}px minmax(0,1fr)">'
                f'<div class="cn-series-index">{T(item)}</div>'
                f'<div class="cn-h cn-ttl cn-t40">{T(title)}</div></div></div>')
    if k == 'display':
        s = dsize(g('size'), 56); col = 'var(--acc)' if g('color') == 'gold' else 'var(--hd)'
        if g('stroke'):
            tk = C.tokens(ctx['sf']); c = tk['acc'] if g('color') == 'gold' else tk['hd']
            return f'<div class="cn-disp" aria-label="{h.esc(str(b["display"]))}" style="line-height:0">{h.OUTLINE(str(b["display"]), s, g("stroke"), c, g("spacing", 0))}</div>'
        inner = h.GT(b, ctx['sf'] == 'image', T(b['display']))
        return f'<div class="cn-disp cn-wrap cn-snap" style="font-size:{s}px;line-height:{dlh(s)}px;color:{col}">{inner}</div>'
    if k == 'title':
        sz = g('size')
        cls = 'cn-t28' if sz is not None and float(sz) <= 30 else 'cn-t40'
        big = sz is not None and float(sz) >= 52
        hd = (f'<div class="cn-disp cn-wrap cn-snap" style="font-size:{dsize(sz)}px;line-height:{dlh(dsize(sz))}px">{h.GT(b, ctx["sf"] == "image", T(b["title"]))}</div>' if big else
              f'<div class="cn-h cn-ttl {cls} cn-snap">{h.GT(b, ctx["sf"] == "image", T(b["title"]))}</div>')
        return (C.lab(g('kicker')) if g('kicker') else '') + hd + (f'<div class="cn-sub"{h.DECO}>{T(g("sub"))}</div>' if g('sub') else '')
    if k == 'en': return f'<div class="cn-sub"{h.DECO}>{T(b["en"])}</div>'
    if k == 'kicker': return C.lab(b['kicker'])
    if k == 'worksheet': return C.lab(f'Worksheet · {b["worksheet"]}')
    if k == 'caption': return f'<div class="cn-cap"{h.DECO}>{T(b["caption"])}</div>'
    if k == 'task':
        return (f'<div class="cn-task">{accent_num(b["task"], round(56 * C.K), 2 * C.LH)}<div class="cn-h cn-t28">{T(g("name", ""))}</div></div>'
                + (C.lab(g('sub'), deco=False) if g('sub') else ''))
    if k == 'p':
        lead = f'<b class="cn-lead">{colon(g("lead"))}</b>' if g('lead') else ''
        big = g('size') is not None and float(g('size')) >= 18 and wide(width)
        st = f'font-weight:{g("weight")};' + measure(width)
        return f'<div class="cn-tx{" cn-t20" if big else ""}"{C.reading(g("flow", "keep" if big else None))} style="{st}"><p>{lead}{T(b["p"])}</p></div>'
    if k == 'letter':
        ps = ''.join(f'<p>{T(x)}</p>' for x in C.listify(b['letter']))
        sg = (f'<div class="cn-cap" style="margin-top:{C.LH // 2}px;color:var(--fg)">' + '<br>'.join(T(x) for x in C.listify(b['sign'])) + '</div>') if g('sign') else ''   # 落款：独立小字号块吸在正文下方，不占 letter 的 42px 行距
        return f'<div class="cn-tx{" cn-t20" if wide(width) else ""} cn-letter"{C.reading(g("flow"))} style="{measure(width)}">{ps}{sg}</div>'
    if k == 'items':
        its = C.listify(b['items']); hd = f'<div class="cn-h cn-t20">{T(g("heading"))}</div>' if g('heading') else ''
        if g('style') in ('bullet', 'plain'):
            return hd + f'<ul class="cn-li cn-list-{g("style")}">' + ''.join(f'<li>{T(t)}</li>' for t in its) + '</ul>'
        if g('style') == 'big':
            t20 = ' cn-t20' if wide(width) else ''
            return hd + '<ol class="cn-ol big">' + ''.join(f'<li>{accent_num(f"{i:02d}", round(28 * C.S), round(1.5 * C.LH))}<span class="cn-h{t20}">{T(t)}</span></li>' for i, t in enumerate(its, 1)) + '</ol>'
        return hd + '<ol class="cn-ol">' + ''.join(f'<li><span class="cn-oln">{i}</span><span>{T(t)}</span></li>' for i, t in enumerate(its, 1)) + '</ol>'
    if k == 'kv':
        kw = C.wd(1, ncols(g('kw', 90)))
        return '<div class="cn-tb cn-kv">' + ''.join(f'<div class="cn-tr" style="grid-template-columns:{kw}px 1fr"><span class="cn-h" style="color:var(--acc)">{T(a)}</span><span>{T(v)}</span></div>' for a, v in b['kv']) + '</div>'
    if k in ('step', 'q'):
        if k == 'step':
            no = accent_num(f'{b["step"]:02d}' if str(b['step']).isdigit() else b['step'], round(28 * C.S), round(1.5 * C.LH))
            t = (f'<b class="cn-lead">{colon(g("lead"))}</b>' if g('lead') else '') + T(g('text', ''))
            wr = g('write', [])
        else:
            no = f'<span class="cn-lab" style="color:var(--acc)">Q{h.esc(str(b["q"]))}</span>'; t = T(g('text', '')); wr = g('write', [{'fill': 64}])
        grow = g('grow') or k == 'q'
        inner = R(wr, dict(ctx, w=width - 2 * C.LH)) if wr else ''
        return (f'<div class="cn-step{" grow" if grow else ""}"><div class="cn-stepr">{no}<div class="cn-tx"><p>{t}</p></div></div>'
                + (f'<div class="cn-stepw">{inner}</div>' if inner else '') + '</div>')
    if k == 'cols':
        cs = b['cols']; wds = g('widths', ' '.join(['1fr'] * len(cs)))
        return f'<div class="cn-cols" style="grid-template-columns:{wds}">' + ''.join(f'<div class="cn-colf">{R(c, dict(ctx, w=width / len(cs)))}</div>' for c in cs) + '</div>'
    if k == 'table':
        cols = b['table']; n = int(g('lines', 1)); wds = g('widths', ' '.join(['1fr'] * len(cols)))
        out = ''.join(f'<div class="cn-th"{h.DECO}>{T(c)}</div>' for c in cols)
        for rw in g('rows', []):
            out += f'<div class="cn-wtl cn-h" style="height:{C.LH * n}px">{T(rw)}</div>' + ''.join(f'<div>{ln(n)}</div>' for _ in cols[1:])
        return f'<div class="cn-wt" style="grid-template-columns:{wds}">{out}</div>'
    if k == 'field': return fd(b['field'])
    if k == 'fields':
        xs = C.listify(b['fields']); wds = g('cols', ' '.join(['1fr'] * len(xs)))
        return f'<div class="cn-cols" style="grid-template-columns:{wds}">' + ''.join(fd(x) for x in xs) + '</div>'
    if k == 'lines': return ln(b['lines'])
    if k == 'fill': return f'<div class="fill cn-fill" style="min-height:{nrows(b["fill"], 2, 1) * C.LH}px"></div>'
    if k == 'box': return f'<div class="cn-bx" style="height:{nrows(g("h", 140), 5) * C.LH}px"><span class="cn-cap"{h.DECO}>{T(b["box"])}</span></div>'
    if k == 'boxes':
        xs = C.listify(b['boxes']); wds = g('cols', ' '.join(['1fr'] * len(xs)))
        return f'<div class="cn-cols" style="grid-template-columns:{wds}">' + ''.join(f'<div class="cn-bx" style="height:{nrows(g("h", 110), 4) * C.LH}px"><span class="cn-cap"{h.DECO}>{T(x)}</span></div>' for x in xs) + '</div>'
    if k == 'choice':
        return f'<div class="cn-choice"><span class="cn-cap">{T(b["choice"])}</span>' + ''.join(f'<span class="cn-h">{T(o)}</span>' for o in g('options', [])) + '</div>'
    if k == 'blanks':
        w = g('w', 180); return '<div class="cn-blank">' + ''.join(f'<span class="cn-h">{colon(l)}</span><i style="width:{w}px"></i>' for l in C.listify(b['blanks'])) + '</div>'
    if k == 'sign':
        return (f'<div class="cn-tx"><p>{T(b["sign"])}</p></div><div class="cn-blank" style="margin-top:{C.LH}px"><span class="cn-h">{colon(g("label", "签名" if h.CJK else "Signature"))}</span>'
                f'<i style="width:{g("w", 240)}px"></i></div>')
    if k == 'figure':
        bl, st, w = image_bleed(b, ctx)
        if bl == 'page':
            if width < C.wd(1, 6) - 1: raise ValueError('bleed: page 只能放在整版心中，不能放在文字分栏内')
            if g('caption'): raise ValueError('整页出血图版的说明请移到相邻页，不能追加在满页图片下方')
            return (f'<div data-bleed="page" style="position:absolute;left:-{ctx["bl"]}px;top:-{C.TOP}px;width:{C.W}px;height:{C.H}px">'
                    + figure(b['figure'], C.H, b, C.W, g('caption')) + '</div>')
        hp = g('h')
        if hp is None:
            try:
                from PIL import Image
                with Image.open(os.path.join(h.SRC, str(b['figure']))) as im: hp = width * im.height / im.width
            except (OSError, ValueError): hp = 8 * C.LH
        limit = min(10, C.LAST - 2) if g('role') == 'supporting' else C.LAST - 2
        return f'<div data-bleed="{bl or "none"}" style="{st}">' + figure(b['figure'], nrows(hp, 8, hi=limit) * C.LH, b, w, g('caption')) + '</div>'
    if k == 'gallery':
        fs = C.listify(b['gallery']); caps = C.listify(g('captions')) + [None] * len(fs); n = len(fs)
        bl, st, w = image_bleed(b, ctx)
        wds = g('widths', ' '.join(['1fr'] * n)); hpx = nrows(g('h', 160), 6) * C.LH
        gap = 0 if bl in ('left', 'right', 'both') else C.GUT
        return (f'<div data-bleed="{bl or "none"}" class="cn-cols cn-gal" style="{st}grid-template-columns:{wds};column-gap:{gap}px">'
                + ''.join(figure(f, hpx, b, (w - gap * (n - 1)) / n, c) for f, c in zip(fs, caps)) + '</div>')
    if k == 'stats':
        st = [s if isinstance(s, (list, tuple)) else [s, ''] for s in C.listify(b['stats'])]
        nc = int(g('cols', len(st)) or 1); sz = min(round(72 * C.K), max(round(40 * C.S), dsize(g('size', 56))))   # 关键数字：47 · 56 · 72
        sup = lambda v: re.sub(r'([+＋%])$', r'<sup>\1</sup>', h.esc(str(v)))
        cells = ''.join(f'<div class="cn-top2 cn-snap" style="padding-top:{C.LH // 2}px"><div class="cn-num" style="font-size:{sz}px;line-height:{dlh(sz)}px">{h.GT(b, ctx["sf"] == "image", sup(a))}</div>'
                        f'<div class="cn-cap">{T(x[1]) if len(x) > 1 else ""}</div></div>' for x in st for a in [x[0]])
        return f'<div class="cn-stats" style="grid-template-columns:repeat({nc},minmax(0,1fr));row-gap:{C.LH}px">{cells}</div>'
    if k == 'quote':
        qt, by = str(b['quote']).strip(), g('by')
        if not by:
            m_ = re.match(r'^(.*?)\s*(?:——|—|--)\s*([^—]{1,30})$', qt, re.S)
            if m_: qt, by = m_.group(1), m_.group(2)
        qt = re.sub(r'^[“「『"]+|[”」』"]+$', '', qt.strip())
        return C.quote(qt, by)
    if k == 'cards':
        cs = C.listify(b['cards']); nc = int(g('cols') or (2 if len(cs) in (2, 4) else min(3, len(cs))))
        rule = 'cn-top1' if g('style') == 'line' else 'cn-top2'
        def cell(i, c):
            if isinstance(c, dict): k_, t_, x_, im_ = c.get('k'), c.get('t', ''), c.get('x'), c.get('img')
            else: k_, t_, x_, im_ = None, c[0], (c[1] if len(c) > 1 else None), (c[2] if len(c) > 2 else None)
            meta = ('<div class="cn-cardmeta">' + ''.join(f'<span class="cn-cap">{T(x)}</span>' for x in c.get('meta', [])) + '</div>') if isinstance(c, dict) and c.get('meta') else ''
            im = f'<div class="cn-cardi" style="height:{2 * C.LH}px"><img alt="" src="{h.FIGIMG(im_, 120)}"></div>' if im_ else ''
            no = f'<span class="cn-cardn">{i:02d}</span>' if g('num') else ''   # 编号和标题同一行（省出一行，编号用强调色）
            if g('balance') and nc == 2 and len(cs) % 2 and i == len(cs) and not im_:
                return (f'<div class="cn-card {rule} cn-snap" style="grid-column:1 / -1"><div class="cn-cols" style="grid-template-columns:repeat(2,minmax(0,1fr))">'
                        + f'<div>{C.lab(k_, deco=False) if k_ else ""}<div class="cn-h cn-t20">{no}{T(t_)}</div>{meta}</div><div>{C.TX(x_) if x_ else ""}</div></div></div>')
            return f'<div class="cn-card {rule} cn-snap">{im}{C.lab(k_, deco=False) if k_ else ""}<div class="cn-h cn-t20">{no}{T(t_)}</div>{meta}{C.TX(x_) if x_ else ""}</div>'
        return f'<div class="cn-cols" data-rg="1" style="grid-template-columns:repeat({nc},minmax(0,1fr));row-gap:{C.LH}px">' + ''.join(cell(i, c) for i, c in enumerate(cs, 1)) + '</div>'   # data-rg：放不下时行间距收到 0（卡片自带顶线分隔）
    if k == 'qr':
        try: import qrcode, qrcode.image.svg
        except ImportError: h.ERR.append('二维码块需要 qrcode：pip install qrcode（或把二维码图片放进 photos/，用 figure 块）'); return ''
        n = nrows(g('size', 104), 4, 3, 8) * C.LH; pad = C.LH // 4; s = n - 2 * pad
        sv = qrcode.make(str(b['qr']), image_factory=qrcode.image.svg.SvgPathImage, border=0).to_string(encoding='unicode')
        sv = re.sub(r'<\?xml[^>]*>', '', sv); sv = re.sub(r'width="[^"]*" height="[^"]*"', f'width="{s}" height="{s}"', sv, count=1)
        sv = sv.replace('<path ', f'<path fill="{h.INK}" ')   # 永远深色码 + 白底静区：反色码很多扫码软件认不出
        return f'<div class="cn-qr"><div class="cn-qrt" style="padding:{pad}px;width:{n}px;height:{n}px">{sv}</div>' + (f'<div class="cn-cap"{h.DECO}>{T(g("caption"))}</div>' if g('caption') else '') + '</div>'
    if k == 'bars':
        sr = g('series', ['', '']); un = g('unit', '%'); mx = g('max', 100)
        rws = ''.join(f'<div class="cn-bar"><div>{T(rw[0])}</div><div class="cn-bart"><span class="trk"><i style="width:{rw[1] / mx * 100:.1f}%"></i></span><span class="cn-cap">{h.esc(str(rw[1]))}{h.esc(un)}</span></div>'
                      f'<div class="cn-bart b2"><span class="trk"><i style="width:{rw[2] / mx * 100:.1f}%"></i></span><span class="cn-cap">{T(sr[1])}{h.COLON}{h.esc(str(rw[2]))}{h.esc(un)}</span></div></div>' for rw in b['bars'])
        lg = f'<div class="cn-cap"{h.DECO}><span class="cn-barl"></span>{T(sr[0])}　<span class="cn-barl b2"></span>{T(sr[1])}</div>' if sr[0] else ''
        return f'<div class="cn-bars">{lg}{rws}</div>'
    if k == 'product':
        im_ = g('image')
        if im_ and str(im_).startswith('ai:'): im_ = h.AIFIG(im_, width, g('h', 200), '产品卡插图')
        src = h.FIGIMG(im_, width) if im_ else ''
        pic = f'<div class="cn-figi cn-prodi" style="height:{nrows(g("h", 200), 7) * C.LH}px"><img class="cn-img" alt="" src="{src}" style="object-fit:{g("fit", "contain")}"></div>' if src else ''
        return (f'<div class="cn-card cn-top2 cn-snap">{pic}' + (C.lab(g('tag')) if g('tag') else '') + f'<div class="cn-h cn-t20">{T(b["product"])}</div>'
                + (C.TX(g('text')) if g('text') else '') + '</div>')
    if k == 'chips':
        return f'<div class="cn-chips"{h.DECO}>' + ''.join(f'<span class="{"on" if i == g("on") else ""}">{T(c)}</span>' for i, c in enumerate(b['chips'], 1)) + '</div>'
    if k == 'cycle':
        ns = b['cycle']; S_ = nrows(g('size', 300), 10, 6, 20) * C.LH; rr = S_ * .38; c = S_ / 2; n = len(ns); tk = C.tokens(ctx['sf'])
        pts = [(c + rr * math.sin(2 * math.pi * i / n), c - rr * math.cos(2 * math.pi * i / n)) for i in range(n)]
        arcs = ''.join(f'<path d="M{pts[i][0]:.1f},{pts[i][1]:.1f} A{rr:.1f},{rr:.1f} 0 0 1 {pts[(i + 1) % n][0]:.1f},{pts[(i + 1) % n][1]:.1f}" fill="none" stroke="{tk["acc"]}" stroke-width="1.5"/>' for i in range(n))
        nodes = ''.join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{S_ * .08:.1f}" fill="{tk["acc"] if i == 0 else tk["bg"]}" stroke="{tk["acc"]}" stroke-width="1.5"/>'
                        f'<text x="{x:.1f}" y="{y + 5:.1f}" text-anchor="middle" class="cn-cyt" fill="{tk["bg"] if i == 0 else tk["fg"]}">{h.esc(str(nd[0]))}</text>'
                        + (f'<text x="{x:.1f}" y="{y + S_ * .13:.1f}" text-anchor="middle" class="cn-cys" fill="{tk["mut"]}">{h.esc(str(nd[1]))}</text>' if len(nd) > 1 else '')
                        for i, (nd, (x, y)) in enumerate(zip(ns, pts)))
        ctr = f'<text x="{c}" y="{c + 6}" text-anchor="middle" class="cn-cyc" fill="{tk["hd"]}">{h.esc(str(g("center", "")))}</text>'
        return f'<div class="cn-cyc0"{h.DECO}><svg width="{S_}" height="{S_}" viewBox="0 0 {S_} {S_}">{arcs}{nodes}{ctr}</svg></div>'
    if k == 'timeline':
        tl = b['timeline']; v = g('direction', 'h' if len(tl) <= 5 else 'v') == 'v'
        if g('style') == 'axis':
            rows = []
            for item in tl:
                d = item if isinstance(item, dict) else dict(zip(('k', 't', 'x'), item))
                details = C.TX(d.get('x'))
                if d.get('period'):
                    details += f'<div class="cn-cap cn-axisperiod">{T(d["period"])}</div>'
                if d.get('events'):
                    details += '<ul class="cn-axis-events">' + ''.join(f'<li>{T(x)}</li>' for x in d['events']) + '</ul>'
                rows.append(f'<div class="cn-axisrow" style="grid-template-columns:{C.wd(1, 1) + C.GUT}px minmax(0,1fr)">'
                            + f'<span class="cn-axisdot"></span><div class="cn-axisdate cn-h cn-t28">{T(d.get("k", ""))}</div>'
                            + f'<div><div class="cn-h cn-t20">{T(d.get("t", ""))}</div>{details}</div></div>')
            end = f'<div class="cn-axismore cn-cap"{h.DECO}>{T(g("next"))}</div>' if g('next') else ''
            return '<div class="cn-timeaxis">' + ''.join(rows) + end + '</div>'
        if v:
            big = g('size') is not None and float(g('size')) >= 18 and wide(width)
            rows = []
            for item in tl:
                d, t = item[:2]
                detail = f'<div class="cn-tx">{T(item[2])}</div>' if len(item) > 2 else ''
                rows.append(f'<div class="cn-tr" style="grid-template-columns:{C.wd(1, 1) + C.GUT}px 1fr"><span class="cn-h cn-t20" style="color:var(--acc)">{T(d)}</span><div class="{"cn-t20" if big else ""}">{T(t)}{detail}</div></div>')
            return '<div class="cn-tb cn-top2">' + ''.join(rows) + '</div>'
        return (f'<div class="cn-cols" style="grid-template-columns:repeat({len(tl)},minmax(0,1fr))">'
                + ''.join(f'<div class="cn-top2 cn-snap" style="padding-top:{C.LH // 2}px"><div class="cn-h cn-t20" style="color:var(--acc)">{T(d)}</div><div>{T(t)}</div></div>' for d, t in tl) + '</div>')
    if k == 'sheet':
        hd = C.listify(g('head')); rws = b['sheet']; n_ = max([len(rw) for rw in rws] + [len(hd)])
        tpl = g('widths') or (f'{C.wd(1, 2)}px ' + ' '.join(['1fr'] * (n_ - 1)) if n_ > 1 else '1fr')
        out = (f'<div class="cn-tr cn-th" style="grid-template-columns:{tpl}">' + ''.join(f'<span{h.DECO}>{T(c)}</span>' for c in hd) + '</div>') if hd else ''
        out += ''.join(f'<div class="cn-tr" style="grid-template-columns:{tpl}">' + ''.join(f'<span class="{"cn-h" if j == 0 else ""}">{T(c)}</span>' for j, c in enumerate(rw)) + '</div>' for rw in rws)
        return f'<div class="cn-tb cn-top2">{out}</div>'
    if k == 'logos':
        hp = max(C.LH // 2, round(float(g('h', 40)) / (C.LH / 2)) * C.LH // 2)
        mat = f' style="background:#FFFFFF;padding:{C.LH // 2}px;width:fit-content;max-width:100%"' if g('frame') else ''
        return f'<div class="cn-logos"{mat}>' + ''.join(f'<img alt="" src="{h.FIGIMG(x, hp * 4)}" style="height:{hp}px">' for x in C.listify(b['logos'])) + '</div>'
    if k == 'space': return ''
    if k == 'html': return b['html']
    return ''

def R(bs, ctx):
    """一列块 → HTML。块与块之间隔整行（标签和标题、标题和副题之间不隔）；旧写法的 mt、space 吸到整行"""
    out = []; prev = None
    for b in (bs or []):
        if b is None: continue
        if isinstance(b, str): b = {'p': b}
        k = kind(b)
        if k == 'space': sp = lines(b["space"], 1); out.append(f'<div class="cn-b" data-g="{sp}" data-gk="h" style="height:{sp * C.LH}px"></div>'); prev = k; continue
        if prev is None: gap = 0
        elif (prev, k) in TIGHT or prev in ('kicker', 'worksheet'): gap = 0   # 小标签贴着它标注的内容
        else: gap = GAP.get(k, 1) if b.get('mt') is None else lines(b['mt'], GAP.get(k, 1))
        cls = 'cn-b cn-b-' + str(k) + (' grow' if k == 'fill' or (k in ('step', 'q') and (b.get('grow') or k == 'q')) else '')
        out.append(f'<div class="{cls}"' + (f' data-g="{gap}"' if gap > 1 else '') + f' style="margin-top:{gap * C.LH}px">{B(b, ctx)}</div>')   # data-g：放不下时空行先收（fill.js canon）
        prev = k
    return ''.join(out)
def ctx_of(c0, c1, r, sf):
    return dict(w=C.wd(c0, c1), bl=C.x(c0, r), br=C.W - C.xe(c1, r), sf=sf)
def grows(bs): return any(kind(b) in ('fill', 'q') or (kind(b) == 'step' and b.get('grow')) or kind(b) == 'cols' and any(grows(c) for c in b['cols']) for b in (bs or []) if b is not None)

def region(c0, c1, r, bs, top, bot, sf='paper', id_='', align=None, after=None):
    """一块文字区：c0..c1 栏、第 top 行到第 bot 行（bot 是下沿的行线）。
    有书写线（fill）或可伸展的任务（grow）时是定高的竖排区，fill 吃掉剩下的高度；否则是普通文字栈（顶部对齐，或 align: bottom 贴底）。
    after=另一块文字区的 id：上沿取 max(第 top 行, 那一块的下沿 + 1 行)（开窗版旁边一栏写长了，下面的整宽区跟着往下让）"""
    if not bs: return ''
    html = R(bs, ctx_of(c0, c1, r, sf))
    y0 = f'{top}|{after}.bottom+1' if after else None
    if grows(bs):
        a = f' data-y0="{y0}" data-y1="{bot}"' if y0 else ''
        return (f'<div class="cn-a cn-st cn-flow" id="{id_}" data-anchor="top"{a} style="left:{C.x(c0, r)}px;width:{C.wd(c0, c1)}px;top:{C.y(top)}px;'
                f'height:{C.y(bot) - C.y(top)}px;{C.vs(sf)}">{html}</div>')
    if align == 'bottom': return C.stack(c0, c1, r, [html], bot=bot, sf=sf, id_=id_)
    return C.stack(c0, c1, r, [html], top=top, sf=sf, id_=id_, y0=y0)

# ---------------------------------------------------------------- 照片版式（都在 6 栏网格上）
def F(p): return tuple(p.get('focus', [.5, .5]))
def light_art(v): return (not C.has_photo(v)) and h.SD['tone'] != 'dark'
def bake_page(n, p, v, box, target=None, name=None, mask=None, bake_box=None):
    """照片烘焙成整页底图（图上有字时用：dark.py 会在字下面渐进压暗）；box 是照片露出来的区域（0–1），风格插画在这个区域里构图。
    瑞士单色、风格派、孟菲斯没有插画：没给照片时这一格是浅灰色块 + 淡灰编号（返回的 name 是 None）"""
    if not C.has_photo(v) and C.NOART():
        C.LIGHT_ART[0] = False
        x0, y0, x1, y1 = box[0] * C.W, box[1] * C.H, box[2] * C.W, box[3] * C.H
        return None, C.box(round(x0), round(y0), round(x1), round(y1), C.pic(None, x1 - x0, y1 - y0, 1, 'B', label=False), 'cn-pic')   # 这一格上面要压字：不放占位编号
    name = name or f'p{n:02d}.jpg'
    h.bake(n, name, v, C.W, mask or (lambda X, Y: 0 * X), F(p), target or p.get('target', [C.W * (box[0] + box[2]) / 2, C.H * (box[1] + box[3]) / 2]), p.get('zoom', 1.0), 'single', True, bake_box or box)
    C.LIGHT_ART[0] = light_art(v)
    return name, h.IMGTAG(name)
def osf(name):
    """图上的字用哪种底的颜色：照片 / 深色插画 = 白字（image）；浅色插画 = 深色字；没有插画的风格（灰色占位格）= 浅灰底的字"""
    return 'image' if name else 'B'
def cut(n, k, y_end):
    """浅色风格插画上有字时：插画停在字的上方一行，下面换成纸（字不压在插画上）"""
    if not C.LIGHT_ART[0]: return ''
    return f'<div class="cn-a cn-field cn-paper" data-y0="{C.sid(n, k)}.top-1" style="left:0;top:0;width:{C.W}px;height:{round(y_end)}px;background:{C.tokens("paper")["bg"]}"></div>'
def paper(x0, y0, x1, y1): return C.box(round(x0), round(y0), round(x1), round(y1), '', 'cn-field cn-paper', f'background:{C.tokens("paper")["bg"]}')
# ---------------------------------------------------------------- photo 风格（国家地理式）：照片淡进半透明纸面，不切硬边
def soft(v):
    """photo 风格有照片时：照片和纸面的交界不是硬边，照片在交界处（约 1.5 行）慢慢淡进半透明纸面（book.paper，默认 0.9），
    写字的纸面上照片淡淡透出来；交界落在行线上，过渡带里不放字。book.edge: hard → 回到不透明纸面 + 硬边"""
    return h.STYLE == 'photo' and C.has_photo(v) and str(h.BK.get('edge', 'soft')).lower() != 'hard'
def _ss(e0, e1, x): return h.wash.ss(e0, e1, x)
def fade_down(yS, bb):
    """照片在上：第 yS 行线以上是照片，往下 1.5 行内淡进纸面（不透明度 book.paper）；照片铺到 bb，bb 前 4 行再淡成纯纸"""
    A, L = h.wash.A, C.LH
    return lambda X, Y: h.wash.np.maximum(A * _ss(yS - L * .5, yS + L, Y), _ss(bb - 5 * L, bb - L, Y))
def fade_up(yS, tt):
    A, L = h.wash.A, C.LH
    return lambda X, Y: h.wash.np.maximum(A * (1 - _ss(yS - L, yS + L * .5, Y)), 1 - _ss(tt + L, tt + 5 * L, Y))
def zone(x0, y0, x1, y1): return C.box(round(x0), round(y0), round(x1), round(y1), '', 'cn-pic cn-zone')   # 烘焙底图里照片露出来的那一格：给版面结构（风格派的线和色格）用，不画东西

def poster_fields(p):
    """POSTER 的内容块 → FULL 的空位（小标签、章节号、书名、副题、导语、正文、数字）；放不进空位的块原样放进 bottom"""
    q = {k: v for k, v in p.items() if k not in ('top', 'bottom', 'layout', 'fig', 'top_y', 'bottom_y')}
    q['layout'] = 'FULL'; texts = []; extra = []
    for b in list(p.get('top') or []) + list(p.get('bottom') or []):
        if b is None: continue
        if isinstance(b, str): b = {'p': b}
        k = kind(b)
        if k == 'kicker' and 'kicker' not in q: q['kicker'] = b['kicker']; continue
        if k == 'display' and not b.get('stroke'):
            s = str(b['display']).replace('<br>', '\n')
            if len(s) <= 8 and re.match(r'^(\d+|[A-Z]|Day ?\d+|Unit ?\d+|第.{1,4}[章天单元部分])$', s.strip(), re.I) and 'index' not in q: q['index'] = s.strip(); continue
            if 'title' not in q: q['title'] = s; continue
        if k == 'title' and 'title' not in q:
            q['title'] = b['title']
            if b.get('kicker') and 'kicker' not in q: q['kicker'] = b['kicker']
            if b.get('sub') and 'en' not in q: q['en'] = b['sub']
            continue
        if k == 'en' and 'en' not in q: q['en'] = b['en']; continue
        if k == 'p' and not b.get('lead'): texts.append(b['p']); continue
        if k == 'letter': texts += C.listify(b['letter']) + C.listify(b.get('sign')); continue   # sign 落款跟着信件文字走（POSTER 里没有独立落款位，不当内容丢掉）
        if k == 'stats' and 'stats' not in q: q['stats'] = b['stats']; continue
        if k in ('figure', 'gallery'): q.setdefault('inset', []).append(b); continue   # 海报上的插图：放进网格里的一格（切口一侧三栏），不跟着文字栈走
        extra.append(b)
    if texts: q['intro'] = texts[0]
    if len(texts) > 1: q['text'] = texts[1:]
    if p.get('fig'): extra.append({'caption': p['fig']})
    if extra: q['bottom'] = extra
    return q, texts

def POSTER(n, p):
    """满版照片页（封面、章节扉页、致辞、封底）= FULL；致辞这类长文字 = 照片在上的 ONE"""
    q, texts = poster_fields(p)
    if sum(C.chars(t) for t in texts) > 220 and q.get('index') is None and not (n == 1 or p.get('_last')):
        q['layout'] = 'ONE'; q['text'] = texts; q.pop('intro', None)
        if q.get('bottom'): q['text'] = texts
        return C.ONE(n, q)
    return C.FULL(n, q)

def PAPER(n, p):
    """纯纸面页：页头 + 内容块排满 6 栏"""
    r = C.pg(n); top = line_of(p.get('body_top'), 0) if p.get('body_top') and float(p['body_top']) > C.TOP + C.LH else 0
    sf = C.SURF_ALIAS.get(str(p.get('surface', 'paper')).strip().lower())
    if sf not in ('paper', 'A', 'B', 'dark'):
        raise ValueError('PAPER surface 可选 paper / A / B / dark')
    C.emit(n, p, r, sf, region(1, 6, r, p.get('body'), top, C.LAST, sf=sf, id_=C.sid(n, 'b'), align=p.get('align')), sf)

def T_(n, p, bottom=False):
    """T：照片在上（满版出血，下沿落在行线上），纸面在下；B：反过来。图上的字（on_photo）压在照片里、贴着照片的边"""
    r = C.pg(n); v = p.get('image')
    if not bottom:
        Ls = photo_rows(p, 330, 9, 6, C.LAST - 8)   # 照片带 6~LAST-8 行；photo_rows: N（行数）或 split: 像素（旧写法）
        if p.get('body_top'): Ls = max(Ls, line_of(p['body_top'], Ls) - 1)
        yS = C.y(Ls)
        if soft(v):   # 照片往下多铺一段（约到剩余纸面的一半），淡淡透在纸面后面
            bb = yS + .55 * (C.H - yS); name, body = bake_page(n, p, v, (0, 0, 1, yS / C.H), p.get('target'), mask=fade_down(yS, bb), bake_box=(0, 0, 1, bb / C.H))
            body += zone(0, 0, C.W, yS)
        else:
            name, body = bake_page(n, p, v, (0, 0, 1, yS / C.H), p.get('target'))
            body += paper(0, yS, C.W, C.H) + zone(0, 0, C.W, yS)
        if p.get('on_photo'): body += cut(n, 'o', yS) + region(1, 6, r, p['on_photo'], 0, Ls - 1, sf=osf(name), align='bottom', id_=C.sid(n, 'o'))
        body += region(1, 6, r, p.get('body'), Ls + 1, C.LAST, id_=C.sid(n, 'b'))
        return C.emit(n, p, r, 'paper', body, 'image', name, hsf='image' if name else 'paper')
    Ls = photo_rows(p, 760, 24, 8, C.LAST - 6)   # 照片带 8~LAST-6 行（上面至少留 6 行给文字）
    yS = C.y(Ls)
    if soft(v):
        tt = .45 * yS; name, body = bake_page(n, p, v, (0, yS / C.H, 1, 1), p.get('target'), mask=fade_up(yS, tt), bake_box=(0, tt / C.H, 1, 1))
        body += zone(0, yS, C.W, C.H)
    else:
        name, body = bake_page(n, p, v, (0, yS / C.H, 1, 1), p.get('target'))
        body += paper(0, 0, C.W, yS) + zone(0, yS, C.W, C.H)
    body += region(1, 6, r, p.get('body'), 0, Ls - 1, id_=C.sid(n, 'b'))
    if p.get('on_photo'): body += region(1, 6, r, p['on_photo'], Ls + 1, C.LAST, sf=osf(name), id_=C.sid(n, 'o'))
    C.emit(n, p, r, 'paper', body, 'image', name, fsf='image' if name else 'paper', hsf='paper')

def SIDE(n, p, right=False):
    """SL / SR：照片竖条在左 / 右（出血到页边，内沿落在栏间中线上），文字在另外几栏"""
    r = C.pg(n); v = p.get('image'); k = 3 if float(p.get('strip', 270)) >= 340 else 2
    if not right: x0, x1, cols = 0, C.gc(k, r), (k + 1, 6)
    else: x0, x1, cols = C.gc(6 - k, r), C.W, (1, 6 - k)
    name = None
    if soft(v):   # 照片铺满整页，在竖条内沿外淡进纸面
        A, L = h.wash.A, C.LH
        m = (lambda X, Y: A * _ss(x1 - L, x1 + 8, X)) if not right else (lambda X, Y: A * (1 - _ss(x0 - 8, x0 + L, X)))
        name, body = bake_page(n, p, v, (x0 / C.W, 0, x1 / C.W, 1), mask=m, bake_box=(0, 0, 1, 1)); body += zone(x0, 0, x1, C.H)
    else:
        body = C.box(round(x0), 0, round(x1), C.H, C.pic(v, x1 - x0, C.H, 1, C.field_color()), 'cn-pic')
    body += region(*cols, r, p.get('body'), 0, C.LAST, id_=C.sid(n, 'b'), align=p.get('align'))
    C.emit(n, p, r, 'paper', body, 'image', name, fspan=cols, hspan=cols)

def HOLE(n, p):
    """开窗：照片是版心里的一格（3 栏 × 若干行，四个角之一），旁边一栏文字，另一边整宽文字"""
    r = C.pg(n); v = p.get('image'); win = str(p.get('window', 'tr'))
    sw, sh = (p.get('size') or [300, 250])[:2]
    k = max(2, min(3, ncols(sw))); m = max(5, min(18, round(float(sh) / C.LH)))   # 窗最宽 3 栏：旁边一栏至少 3 栏宽（中文每行 ≥ 19 字）
    right = win.endswith('r'); topw = win.startswith('t')
    wc = (7 - k, 6) if right else (1, k); bc = (1, 6 - k) if right else (k + 1, 6)
    l0, l1 = (0, m) if topw else (C.LAST - m, C.LAST)
    name = None
    if soft(v):   # 照片铺满整页，窗里清楚、窗外淡进半透明纸面（窗边 1 行的柔边）
        X0, Y0, X1, Y1, A, L = C.x(wc[0], r), C.y(l0), C.xe(wc[1], r), C.y(l1), h.wash.A, C.LH
        e = 4 * L; B0, B1, B2, B3 = max(0, X0 - e), max(0, Y0 - e), min(C.W, X1 + e), min(C.H, Y1 + e)   # 照片只往窗外多铺 4 行（不整页放大，窗里的构图不变）
        def mk(X, Y):
            win = _ss(X0, X0 + L, X) * (1 - _ss(X1 - L, X1, X)) * _ss(Y0, Y0 + L, Y) * (1 - _ss(Y1 - L, Y1, Y))
            keep = 1.0   # 照片多铺出来的那一圈：在外沿 3 行内淡成纯纸（贴页边的那一侧照片出血，不淡）
            if B0 > 0: keep = keep * _ss(B0, B0 + 3 * L, X)
            if B2 < C.W: keep = keep * (1 - _ss(B2 - 3 * L, B2, X))
            if B1 > 0: keep = keep * _ss(B1, B1 + 3 * L, Y)
            if B3 < C.H: keep = keep * (1 - _ss(B3 - 3 * L, B3, Y))
            return h.wash.np.maximum(A * (1 - win), 1 - keep)
        name, body = bake_page(n, p, v, (X0 / C.W, Y0 / C.H, X1 / C.W, Y1 / C.H), mask=mk, bake_box=(B0 / C.W, B1 / C.H, B2 / C.W, B3 / C.H)); body += zone(X0, Y0, X1, Y1)
    else:
        body = C.box(C.x(wc[0], r), C.y(l0), C.xe(wc[1], r), C.y(l1), C.pic(v, C.wd(*wc), m * C.LH, 1, C.field_color()), 'cn-pic')
    body += region(*bc, r, p.get('beside'), l0, l1, id_=C.sid(n, 's'), align=None if topw else 'bottom')
    if topw: body += region(1, 6, r, p.get('body'), m + 1, C.LAST, id_=C.sid(n, 'b'), after=C.sid(n, 's') if p.get('beside') else None)
    else: body += region(1, 6, r, p.get('body'), 0, C.LAST - m - 1, id_=C.sid(n, 'b'))
    C.emit(n, p, r, 'paper', body, 'image', name)

# ---------------------------------------------------------------- 跨页：一张横图烘焙成两页宽，两页各排各的文字栈
def spread_bake(n, p, box, mask=None, bake_box=None):
    """横图烘焙成两页宽的底图；box 是照片露出来的区域（0–1，按两页宽算）。
    瑞士 / 孟菲斯 / 风格派没给照片：两页各一块安静的色块（name 是 None）"""
    if not C.has_photo(p.get('image')) and C.NOART():
        C.LIGHT_ART[0] = False
        def half(off):
            x0, x1 = max(0, box[0] * 2 * C.W - off), min(C.W, box[2] * 2 * C.W - off)
            if x1 <= x0: return ''
            return C.box(round(x0), round(box[1] * C.H), round(x1), round(box[3] * C.H), C.pic(None, x1 - x0, (box[3] - box[1]) * C.H, 1, 'B', label=False), 'cn-pic')
        return None, half(0), half(C.W)
    name = f's{n:02d}.jpg'
    h.bake(n, name, p.get('image'), 2 * C.W, mask or (lambda X, Y: 0 * X), F(p), p.get('target', [C.W, C.H * (box[1] + box[3]) / 2]), p.get('zoom', 1.0), 'spread', True, bake_box or box)
    C.LIGHT_ART[0] = light_art(p.get('image'))
    return name, h.IMGTAG(name, -2, 2 * C.W + 4), h.IMGTAG(name, -C.W - 2, 2 * C.W + 4)
def cutb(n, k, y_start):
    """浅色插画上、顶部对齐的字：从 y_start 到字的下方一行换成纸，插画在字下面露出来"""
    if not C.LIGHT_ART[0]: return ''
    return f'<div class="cn-a cn-field cn-paper" data-y1="{C.sid(n, k)}.bottom+1" style="left:0;top:{round(y_start)}px;width:{C.W}px;height:{C.H}px;background:{C.tokens("paper")["bg"]}"></div>'
def poster_side(n, q, r, img, name, side, la=False):
    """跨页的海报那一页：上面的块从第 0 行往下排，下面的块贴着版心下沿；图注放在最后一行。
    la = 底图是浅色插画：两组字各自垫一块纸（插画夹在中间露出来），字用深色"""
    C.LIGHT_ART[0] = la; sf = osf(name); body = img
    bot = list(q.get('bottom') or []) + ([{'caption': q['fig']}] if q.get('fig') else [])
    if q.get('top'): body += cutb(n, 't', 0) + region(1, 6, r, q['top'], 0, C.LAST, sf=sf, id_=C.sid(n, 't'))
    if bot: body += cut(n, 'u', C.H) + region(1, 6, r, bot, 0, C.LAST, sf=sf, align='bottom', id_=C.sid(n, 'u'))
    C.emit(n, q, r, sf, body, 'image', name, side=side)

def SPREAD_P(n, p):
    name, a, b = spread_bake(n, p, (0, 0, 1, 1)); L, Rr = p.get('left', {}), p.get('right', {}); la = C.LIGHT_ART[0]
    poster_side(n, L, False, a, name, 'L', la); poster_side(n + 1, Rr, True, b, name, 'R', la)

def SPREAD_H(n, p):
    """横图贯穿两页上半部（下沿落在行线上）；左页标题压在图的上部，右页的字贴着图的下沿；下半是纸面"""
    if p.get('image_position') == 'bottom':
        Ls = max(8, min(C.LAST - 8, line_of(p.get('split', 564), 17))); yS = C.y(Ls); sft = soft(p.get('image')); tt = .45 * yS
        name, a, b = spread_bake(n, p, (0, yS / C.H, 1, 1), **(dict(mask=fade_up(yS, tt), bake_box=(0, tt / C.H, 1, 1)) if sft else {}))
        for k, (img, side, q) in enumerate([(a, 'L', p.get('left', {})), (b, 'R', p.get('right', {}))]):
            m = n + k; r = m % 2 == 1
            body = img + ('' if sft else paper(0, 0, C.W, yS)) + zone(0, yS, C.W, C.H)
            body += region(1, 6, r, q.get('body'), 0, Ls - 1, id_=C.sid(m, 'b'))
            C.emit(m, q, r, 'paper', body, 'image', name, side=side, fsf=osf(name))
        return
    Ls = max(8, min(C.LAST - 8, line_of(p.get('body_top', 548), 16) - 1)); yS = C.y(Ls)
    sft = soft(p.get('image')); bb = yS + .55 * (C.H - yS)
    name, a, b = spread_bake(n, p, (0, 0, 1, yS / C.H), **(dict(mask=fade_down(yS, bb), bake_box=(0, 0, 1, bb / C.H)) if sft else {})); L, Rr = p.get('left', {}), p.get('right', {}); la = C.LIGHT_ART[0]
    for k, (img, side, q) in enumerate([(a, 'L', L), (b, 'R', Rr)]):
        m = n + k; r = m % 2 == 1; C.LIGHT_ART[0] = la
        body = img + ('' if sft else paper(0, yS, C.W, C.H)) + zone(0, 0, C.W, yS)
        if q.get('on_photo'):
            top_ = side == 'L'
            body += (cutb(m, 'o', 0) if top_ else cut(m, 'o', yS)) + region(1, 6, r, q['on_photo'], 0, Ls - 1, sf=osf(name), align=None if top_ else 'bottom', id_=C.sid(m, 'o'))
        body += region(1, 6, r, q.get('body'), Ls + 1, C.LAST, id_=C.sid(m, 'b'))
        C.emit(m, q, r, 'paper', body, 'image', name, side=side, hsf=osf(name))

def SPREAD_OPENER(n, p):
    """左页开篇海报，照片延伸到右页：右页 SL = 订口一侧两栏宽的照片竖条，T = 上部照片；其余是纸面"""
    kind_ = p.get('right_layout', 'SL'); L, Rr = p.get('left', {}), p.get('right', {})
    sft = soft(p.get('image')); A_, L_ = h.wash.A, C.LH; W_ = C.W + 2; cut0 = C.gc(2, True)
    Ls = max(6, min(C.LAST - 8, line_of(Rr.get('body_top', 300), 7))); yS = C.y(Ls)
    if kind_ == 'SL':   # 照片从左页铺过订口，在右页竖条内沿外淡进纸面
        mk = lambda X, Y: A_ * _ss(W_ + cut0 - L_, W_ + cut0 + 8, X)
        bx, bbx = (0, 0, .5 + (cut0 / (2 * C.W)), 1), (0, 0, 1, 1)
    else:              # 右页上部是照片，往下淡进半透明纸面（左页整页照片不动）
        mk = lambda X, Y: A_ * _ss(yS - L_ * .5, yS + L_, Y) * (X > W_)
        bx, bbx = (0, 0, 1, 1), None
    name, a, b = spread_bake(n, p, bx, **(dict(mask=mk, bake_box=bbx) if sft else {})); la = C.LIGHT_ART[0]
    poster_side(n, L, False, a, name, 'L', la)
    m = n + 1; r = True; C.LIGHT_ART[0] = la
    if kind_ == 'SL':
        cut_ = C.gc(2, r); body = b + ('' if sft else paper(cut_, 0, C.W, C.H)) + zone(0, 0, cut_, C.H) + region(3, 6, r, Rr.get('body'), 0, C.LAST, id_=C.sid(m, 'b'))
        return C.emit(m, Rr, r, 'paper', body, 'image', name, side='R', fspan=(3, 6), hspan=(3, 6))
    body = b + ('' if sft else paper(0, yS, C.W, C.H)) + zone(0, 0, C.W, yS)
    if Rr.get('on_photo'): body += cut(m, 'o', yS) + region(1, 6, r, Rr['on_photo'], 0, Ls - 1, sf=osf(name), align='bottom', id_=C.sid(m, 'o'))
    body += region(1, 6, r, Rr.get('body'), Ls + 1, C.LAST, id_=C.sid(m, 'b'))
    C.emit(m, Rr, r, 'paper', body, 'image', name, side='R', hsf=osf(name))

LAYOUTS = {'POSTER': (POSTER, 1), 'PAPER': (PAPER, 1), 'T': (T_, 1), 'B': (lambda n, p: T_(n, p, True), 1), 'SL': (SIDE, 1), 'SR': (lambda n, p: SIDE(n, p, True), 1),
           'HOLE': (HOLE, 1), 'SPREAD_P': (SPREAD_P, 2), 'SPREAD_H': (SPREAD_H, 2), 'SPREAD_OPENER': (SPREAD_OPENER, 2)}
