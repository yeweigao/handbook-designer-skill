#!/usr/bin/env python3
"""stijl.py —— 风格派（蒙德里安）：book.style: stijl。

底层思想（从“蒙德里安偷师版式”九幅图 + 三个杂志版式例子里总结的）：
  · 先分空间，再放内容，最后上颜色。网格是骨架：大格给主角，中格给图，窄格给正文，小格给页码、标签。
  · 线有层级，不是非此即彼：
      主结构（标题区和正文、图和字、页脚）→ 一条粗线，而且只有两三条，可以停在某一栏（T 形交接、不对称）；
      次要分隔（条目之间）→ 细线；其余的边界 → 只靠对齐，“心中有线”。
  · 颜色就是被粗线围出来的那一格，按角色给：红 = 主角区（封面书名就在红格里）、蓝 = 图片区 / 一道窄条、
    黄 = 页码、日期一类的小格、白 = 正文和留白。颜色少而准：阅读页只有两三小格，封面、章节页才是一整幅构成。
  · 不平均分：大配小、宽配窄、密配疏；一页一个主角；留白也是一格。
  · 节奏（Grid + Rhythm）：把蒙德里安的大色块缩成小色块，排成一列“节拍”——切口页边里沿着一条看不见的竖轴，
    小色块跟着条目走（每个标题、编号旁边一拍），大小不一（方块、扁条、长条），黄多、蓝次之、红最少，拍与拍之间留白；
    编号下的三原色色条是正文里的节拍。不是把黑线换成一串小色块。

怎么落到引擎上：
  封面 / 封底 / 章节页（FULL）：经典、无线画一整幅构成——所有格子都是色块或纸色的“场”，
    字放在格子里，格子的边由内容推出来（书名多高，红格就多高）；节奏画法见 FULL_beat()。
  其他页：沿用 8 个内容版式（canon.py），fill.js 的 sjStructure() 在排好之后量出结构：
    已有的色块、图片、条目行的边 → 粗线；没有分区的页，在页头（小标签 + 大标题 + 导语）下方补一条主线；
    切口一侧标题区那一格涂红，页脚一行：订口一小格蓝、切口一小格黄（页码就在黄格里）；切口页边一列节拍（sjRail）。
三种画法 book.look：
  classic 经典（默认）：粗黑线 + 三原色大格子，节拍稀；
  tone 无线：线退成细线，颜色退成深浅灰；
  beat 节奏：线细（2.5px），图片不描边；色块都缩小——切口上角一根红条挂在节拍轴上、页脚切口一格黄放页码、
    中间一列密的节拍（拍与拍之间偶尔一根细横线）；封面 = 页眉一行 + 红块 + 黑白大照片 + 大书名 + 订口一列节拍 + 页脚黄格。
照片一律转黑白（canon.BW）。
"""
import canon as C
from palettes import lum, contrast

h = C.h
LOOKS = ('classic', 'tone', 'beat')


def on(): return C.G.get('STYLE') == 'stijl'


def look():
    v = str(h.BK.get('look', 'classic')).lower()
    if v not in LOOKS: raise SystemExit(f'ERROR: book.look 可选 {" / ".join(LOOKS)}（style: stijl 的三种画法），当前 {v}')
    return v


def roles():
    """三原色按角色：D 主角 = 主色；X 辅助 = 浅的那个（黄）；S 第二视觉 = 另一个深色。无线画法：深浅不同的灰"""
    T = h.TH_
    if look() == 'tone': return '#D9D3C8', '#E4DFD6', '#CFC9BE'
    A, B = T['A'], T['B']
    third = T.get('OCH') or T.get('C') or T['G']                           # 换了配色方案时第三色取方案里的 OCH（风格默认的 C 是蒙德里安蓝，不能残留）
    if lum(B) > .45: return A, third, B
    return A, B, T.get('GOLD') or T.get('C') or '#F2C318'


def seam():
    """拼贴照片之间的缝：经典 = 墨色线，无线 = 浅色缝，节奏 = 纸色（留白多，线细）"""
    lk = look(); return {'classic': h.TH_['INK'], 'tone': '#FBF9F4', 'beat': h.TH_['PAPER']}[lk]


def bar(i):
    """编号下的色条（CSS 变量 --bar）：红、蓝、黄轮流"""
    return f'--bar:{roles()[i % 3]};' if on() else ''


def tok(sf):
    """格子的颜色和格子里的字色。彩色格只用墨色或白字；书名这种大字墨色对比 ≥ 3 就用墨色（黑字压红是蒙德里安海报的样子）"""
    T = h.TH_; INK = T['INK']; D, S, X = roles()
    bg = {'D': D, 'S': S, 'X': X}[sf]
    fg = INK if contrast(INK, bg) >= 4.5 else '#FFFFFF'
    return dict(bg=bg, fg=fg, hd=INK if contrast(INK, bg) >= 3 else fg, acc=fg, num=fg, lab=fg, mut=fg, rule=fg, line=C.rgba(fg, .4))


def meta(n, p, full=False, chap=False):
    if not on(): return ''
    D, S, X = roles()
    return f'<i class="sj-meta" hidden data-c="{D},{S},{X}" data-ink="{h.TH_["INK"]}" data-look="{look()}" data-full="{1 if full else 0}" data-chap="{1 if chap else 0}"></i>'


# ---------------------------------------------------------------- 封面 / 封底 / 章节页：一整幅构成（经典、无线）
def FULL(n, p):
    if look() == 'beat': return FULL_beat(n, p)
    r = C.pg(n); v = p.get('image'); chapter = p.get('index') is not None; last = p.get('_last')
    X_ = lambda xo: xo if r else C.W - xo                                   # 按单页方向写的 x → 这一页
    sp = lambda a, b: (a, b) if r else (7 - b, 7 - a)                      # 栏号同理（双页镜像）
    g = lambda c: C.gc(c, True)                                            # 单页方向第 c 栏右边的栏间中线
    side = lambda k: f'padding-{"right" if r else "left"}:{k}px;'           # 靠线的一侧多留一点，字不贴线
    other = lambda k: f'padding-{"left" if r else "right"}:{k}px;'
    def fld(x0, x1, y0, y1, sf, **k):
        a, b = sorted((X_(x0), X_(x1))); return C.field(a, y0, b, y1, sf, **k)
    T_, M_, B_, K_ = C.sid(n, 't'), C.sid(n, 'm'), C.sid(n, 'b'), C.sid(n, 'k')
    bottoms = (C.blocks(p.get('bottom'), 1, 4, r) if p.get('bottom') else '') + C.brand_contact(p)
    stats = C.stats_row(p.get('stats'), 4) if p.get('stats') else ''
    body = ''
    if chapter or not (n == 1 or last):
        # 章节页：主角是章节号（红色巨字）+ 章名；切口上角一小格黄；下方导语在白格里，切口一侧一格蓝
        ix = p.get('index')
        kids = [C.lab(p.get('kicker'))] + ([f'<div class="cn-num sj-ix"{h.DECO} style="color:{roles()[0] if look() != "tone" else h.TH_["INK"]}">{C.T_(ix)}</div>'] if ix is not None else []) \
            + [C.disp(p.get('title'), 120, None, 56), C.sub(p.get('en') or p.get('sub'))]
        body += C.stack(*sp(1, 5), r, kids, top=C.L(2), y1=f'{B_}.top-2', id_=T_, style=side(16))   # 章名的下沿跟着导语格走，放不下先缩标题
        bot = [C.blocks(p.get('inset'), *sp(1, 3), r) if p.get('inset') else '', C.lead(p.get('intro'), 0), C.para(C.listify(p.get('text')), m=1) if p.get('text') else '', stats, f'<div class="m1">{bottoms}</div>' if bottoms else '']
        body += C.stack(*sp(1, 3), r, bot, bot=C.LAST, id_=B_, style=side(16))
        body += fld(g(5), C.W, 0, C.y(C.L(6)), 'X')
        body += fld(0, g(4), 10, C.H, 'paper', y0r=f'{B_}.top-1')
        if C.has_photo(v):   # 章节页给了照片：切口下面那一格放照片（黑白），不再是蓝格
            a, b = sorted((X_(g(4)), X_(C.W))); body += C.box(a, 10, b, C.H, C.pic(v, b - a, 400, 1, 'B'), 'cn-pic', y0r=f'{B_}.top-1')
        else: body += fld(g(4), C.W, 10, C.H, 'S', y0r=f'{B_}.top-1')
        return C.emit(n, dict(p, logo=False, header=None), r, 'paper', body + meta(n, p, True), 'paper', fo=False)
    # 封面 / 封底：书名一格（封面红、封底纸色）· 切口上角一窄格放小标签 · 中间 图（或一格色）| 导语 · 底行 补充信息 | 黄格
    photo = C.has_photo(v)
    tsf = 'D' if n == 1 else 'paper'
    body += C.stack(*sp(1, 5), r, [C.disp(p.get('title'), 128, None, 56)], top=C.L(3), id_=T_, style=side(24) + (f'--hd:{tok("D")["hd"]};' if tsf == 'D' else ''))
    body += C.stack(*sp(6, 6), r, [C.lab(p.get('kicker'))], top=C.L(1), id_=K_)
    body += fld(0, g(5), 0, 10, tsf, y1r=f'{T_}.bottom+1')
    body += fld(g(5), C.W, 0, 10, 'paper', y1r=f'{T_}.bottom+1')
    mid = [C.sub(p.get('en') or p.get('sub')), C.lead(p.get('intro'), 1), C.para(C.listify(p.get('text')), m=1) if p.get('text') else '']
    body += C.stack(*sp(4, 6), r, mid, y0=f'{T_}.bottom+2', id_=M_, style=other(16))
    logo = ''
    if h.BRAND and (h.BRAND.get('logo') or {}).get('file'):
        import brand as BR
        logo = f'<div class="sj-logo"{h.DECO} style="height:{round(float(h.BRAND["logo"].get("h", 24)) * 1.4)}px;color:{h.TH_["INK"]}">{BR.logo_svg(h.BRAND, h.TH_["INK"], dark=False)}</div>'
    body += C.stack(*sp(1, 4), r, [logo, stats, f'<div class="m1">{bottoms}</div>' if bottoms else ''], bot=C.LAST, id_=B_, style=side(16))
    if photo:
        a, b = sorted((X_(0), X_(g(3))))
        body += C.box(a, 10, b, 20, C.pic(v, b - a, 400, 1, 'B'), 'cn-pic', y0r=f'{T_}.bottom+1', y1r=f'{B_}.top-1', minh=120)
    else:
        body += fld(0, g(3), 10, 20, 'S' if n == 1 else 'D', y0r=f'{T_}.bottom+1', y1r=f'{B_}.top-1')
    body += fld(g(3), C.W, 10, 20, 'paper', y0r=f'{T_}.bottom+1', y1r=f'{B_}.top-1')
    body += fld(0, g(4), 10, C.H, 'paper', y0r=f'{B_}.top-1')
    body += fld(g(4), C.W, 10, C.H, 'X', y0r=f'{B_}.top-1')
    C.emit(n, dict(p, logo=False), r, 'paper', body + meta(n, p, True), 'paper', fo=False)


# ---------------------------------------------------------------- 节奏画法：大色块变成小色块
def FULL_beat(n, p):
    """节奏画法（Grid + Rhythm）的封面 / 封底 / 章节页。蒙德里安的大色块缩成小色块，排成一列节拍；线细；内容（照片、书名、正文）是主角。
    封面 / 封底：页眉一行（小标签 + 日期）· 切口上角一块红 · 订口一侧一列节拍（fill.js 排）· 黑白大照片 + 书名 + 导语 + 数字 ·
                页脚一行（和阅读页一样）：节拍列下面一小块红，切口一侧一格黄。
    章节页：红色巨号章节数 + 章名，其余和阅读页一样（页眉线、切口红条、节拍、黄格页码），由 fill.js 量好之后画。"""
    r = C.pg(n); v = p.get('image'); chapter = p.get('index') is not None; last = p.get('_last')
    X_ = lambda xo: xo if r else C.W - xo
    sp = lambda a, b: (a, b) if r else (7 - b, 7 - a)
    g = lambda c: C.gc(c, True)
    INK = h.TH_['INK']; TL = 2.5 / C.LH                                    # 细线 2.5px，换算成行
    ref = lambda i, side, off: f'{i}.{side}{off:+.3f}'
    T_, K_, B_, Y_ = C.sid(n, 't'), C.sid(n, 'k'), C.sid(n, 'b'), C.sid(n, 'y')
    def fld(x0, x1, y0, y1, sf, **k):
        a, b = sorted((X_(x0), X_(x1))); return C.field(a, y0, b, y1, sf, **k)
    def rule(x0, x1, at=None, y=None):                                      # 一根横的细线：at = (栈 id, top/bottom, 偏几行)
        a, b = sorted((X_(x0), X_(x1)))
        if at: return C.box(a, 0, b, 3, '', 'sj-rule', f'background:{INK};', y0r=ref(at[0], at[1], at[2]), y1r=ref(at[0], at[1], at[2] + TL))
        return C.box(a, round(y), b, round(y + 2.5), '', 'sj-rule', f'background:{INK};')
    bottoms = (C.blocks(p.get('bottom'), 1, 4, r) if p.get('bottom') else '') + C.brand_contact(p)
    st = p.get('stats'); stats = C.stats_row(st, 4) if st else ''
    logo = ''
    if h.BRAND and (h.BRAND.get('logo') or {}).get('file'):
        import brand as BR
        logo = f'<div class="sj-logo"{h.DECO} style="height:{round(float(h.BRAND["logo"].get("h", 24)) * 1.4)}px;color:{INK}">{BR.logo_svg(h.BRAND, INK, dark=False)}</div>'
    body = ''
    if chapter or not (n == 1 or last):
        ix = p.get('index')
        kids = [C.lab(p.get('kicker'))] + ([f'<div class="cn-num sj-ix"{h.DECO} style="color:{roles()[0]}">{C.T_(ix)}</div>'] if ix is not None else []) + [C.disp(p.get('title'), 120, None, 56)]
        body += C.stack(*sp(1, 5), r, kids, top=C.L(2), id_=T_)
        figs = ([{'figure': v.get('src') if isinstance(v, dict) else v, 'h': 8 * C.LH}] if C.has_photo(v) else []) + C.listify(p.get('inset'))   # 章节页的照片：导语上面一格（黑白）
        if len(figs) == 2 and all('figure' in f for f in figs):   # 照片 + 一张插图：并排一行（同高），不叠成两格
            figs = [{'gallery': [figs[0]['figure'], figs[1]['figure']], 'captions': [figs[0].get('caption'), figs[1].get('caption')], 'h': 8 * C.LH}]
        bc = sp(1, 5) if figs else sp(1, 4)
        bot = [C.blocks(figs, *bc, r) if figs else '', C.sub(p.get('en') or p.get('sub')), C.lead(p.get('intro'), 1), C.para(C.listify(p.get('text')), m=1) if p.get('text') else '', stats, f'<div class="m1">{bottoms}</div>' if bottoms else '']
        body += C.stack(*bc, r, bot, y0=f'{T_}.bottom+2', id_=B_)
        return C.emit(n, dict(p, logo=False), r, 'paper', body + meta(n, p, False, chap=True), 'paper')
    photo = C.has_photo(v)
    yf = C.y(C.LAST) + C.LH // 2                                            # 页脚线：和阅读页同一个位置
    hc, cc = ((1, 4), (2, 6)) if r else ((2, 5), (2, 5))                    # 页眉文字、正文的栏：左手页（封底）切口上角是红块，字从第 2 栏起，和正文对齐
    # 页眉：小标签 + 日期一行；切口上角一块红，底边和页眉文字齐；下面一根通栏细线
    body += C.stack(*sp(*hc), r, [C.lab(p.get('kicker')), C.sub(p.get('en') or p.get('sub'))], top=0, id_=K_)
    body += fld(g(5), C.W, 0, 10, 'D', y1r=ref(K_, 'bottom', 0))
    body += rule(0, C.W, (K_, 'bottom', 1))
    top = ref(K_, 'bottom', 2)
    # 正文区：书名、导语、数字压在页脚线上方；上面是黑白大照片（吸收剩下的高度）。没照片：封面放一块蓝（第 2–3 栏），封底留白
    mid = [logo, C.disp(p.get('title'), 128, None, 56), C.lead(p.get('intro'), 1), C.para(C.listify(p.get('text')), m=1) if p.get('text') else '',
           C.stats_row(st, cc[1] - cc[0] + 1, 48) if st else '', f'<div class="m1">{bottoms}</div>' if bottoms else '']
    body += C.stack(*sp(*cc), r, mid, bot=C.LAST, id_=T_)
    if photo:
        a, b = sorted((X_(C.x(cc[0], True)), X_(C.xe(cc[1], True))))
        body += C.box(a, 10, b, 20, C.pic(v, b - a, 400, 1, 'B'), 'cn-pic', y0r=top, y1r=f'{T_}.top-1', minh=C.LH * 6)
    elif n == 1:
        body += fld(C.x(cc[0], True), C.xe(cc[0] + 1, True), 10, 20, 'S', y0r=top, y1r=f'{T_}.top-1')
    # 页脚一行（和阅读页一样）：通栏细线；切口一侧一格黄；节拍列底下一小块红
    body += rule(0, C.W, y=yf)
    body += fld(g(5), C.W, yf, C.H, 'X')
    vx = X_(g(5)); body += C.box(round(vx - 1.25), yf, round(vx + 1.25), C.H, '', 'sj-rule', f'background:{INK};')
    body += fld(C.x(1, True), C.xe(1, True), C.H - C.LH * 3 // 2, C.H, 'D')
    # 节拍列：第 1 栏（订口一侧），从正文区顶到页脚线上一行
    a, b = sorted((X_(C.x(1, True)), X_(C.xe(1, True))))
    body += C.box(a, 10, b, yf - C.LH, '', 'sj-railbox', '', y0r=top, attr=f' data-dir="{-1 if r else 1}"')
    C.emit(n, dict(p, logo=False), r, 'paper', body + meta(n, p, True), 'paper', fo=False)


def accents(n, p, r, sf):
    """阅读页：结构线和色格由 fill.js 量好版面之后画（sjStructure）；这里只留颜色和画法给它"""
    if not on() or p.get('layout') == 'FULL': return ''
    return meta(n, p)
