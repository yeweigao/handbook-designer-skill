#!/usr/bin/env python3
"""当前五风格的克制配色与颜色角色。CLI: list / check / sheet；不再自动进入撞色。"""
import sys

PALETTES = {
    'nature': dict(zh='自然纪实', use='Photo，自然与户外', colors=dict(G='#24523E', OCH='#685022', GOLD='#E4B93D', INK='#18251F', MUT='#4A574F', PAPER='#FAF8F1')),
    'campus': dict(zh='学院墨蓝', use='Photo / Editorial，校园与指南', colors=dict(G='#253C4C', OCH='#665644', GOLD='#E4C68B', INK='#202B32', MUT='#4B575E', PAPER='#FBFAF7')),
    'ink': dict(zh='纸与墨', use='Editorial，连续阅读', colors=dict(G='#303A39', OCH='#665C50', GOLD='#DBD4C5', INK='#202625', MUT='#515957', PAPER='#F8F7F2')),
    'swiss': dict(zh='瑞士极简', use='中性纸面与一个砖红强调色', colors=dict(G='#A32F25', OCH='#A32F25', GOLD='#FFFFFF', INK='#151515', MUT='#50504D', PAPER='#FAFAF8', TINT='#F0F0EE')),
}
GRADIENTS = {}   # 当前五风格不再提供预设渐变标题。

def lum(h):
    h = h.lstrip('#'); c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    c = [x / 12.92 if x <= .03928 else ((x + .055) / 1.055) ** 2.4 for x in c]
    return .2126 * c[0] + .7152 * c[1] + .0722 * c[2]
def contrast(a, b): a, b = lum(a), lum(b); return (max(a, b) + .05) / (min(a, b) + .05)

CLASSIC = []   # 旧调用兼容；当前不提供经典撞色预设
DEFAULT = 'nature'

def pair(c):
    """内容版式的两个颜色角色：A 主色、B 强调色。没单独写时 A = G、B = GOLD。"""
    return c.get('A') or c['G'], c.get('B') or c['GOLD']

def on(bg, *cands):
    """在 bg 上可读的字色：按顺序取第一个对比度 ≥ 4.5 的；都不够就取对比度最高的"""
    for x in cands:
        if contrast(x, bg) >= 4.5: return x
    return max(cands, key=lambda x: contrast(x, bg))

# ---------------------------------------------------------------- 颜色角色（借 ppt-master：按角色给颜色，品牌色锁进对应角色）
ROLES = {'background': 'PAPER', 'secondary_bg': 'TINT', 'primary': 'A', 'accent': 'B', 'secondary_accent': 'OCH', 'body_text': 'INK'}
ROLE_ZH = {'background': '背景', 'secondary_bg': '次级背景', 'primary': '主色', 'accent': '强调色', 'secondary_accent': '次强调色', 'body_text': '正文'}
def mix(a, b, t):
    a, b = [[int(x.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4)] for x in (a, b)]
    return '#' + ''.join(f'{round(p + (q - p) * t):02X}' for p, q in zip(a, b))
def roles(c):
    A, B = pair(c); P = c.get('PAPER', '#FFFFFF')
    return dict(background=P, secondary_bg=c.get('TINT') or mix(P, A, .07), primary=A, accent=B, secondary_accent=c.get('OCH', A), body_text=c.get('INK', '#17211C'))
def _hsv(h):
    import colorsys
    return colorsys.rgb_to_hsv(*[int(h.lstrip('#')[i:i + 2], 16) / 255 for i in (0, 2, 4)])
MODES = ('accent', 'mono')
def mode(c, want=None):
    if want == 'clash': raise SystemExit('ERROR: color_mode: clash 已停用；请改用 accent（克制点缀）或 mono（单色）')
    if want and want != 'auto':
        if want not in MODES: raise SystemExit(f'ERROR: book.color_mode 可选 auto / {" / ".join(MODES)}，当前 {want}')
        return want, 'book.color_mode 指定'
    return 'accent', '默认克制点缀，不按色差自动切换撞色'

def resolve(spec, base):
    """book.colors 可以写：方案名（'nature'）、{preset: nature, G: '#...'}、或只写颜色键。base = 风格默认配色。"""
    out = dict(base)
    if spec is None: return out
    if isinstance(spec, str): spec = {'preset': spec}
    if not isinstance(spec, dict): raise SystemExit('ERROR: book.colors 要写配色方案名（如 nature）或颜色键字典（如 {G: "#1D5A43"}）')
    pid = spec.get('preset')
    if pid is not None:
        if pid not in PALETTES: raise SystemExit(f'ERROR: 未知配色方案 {pid}，可选：{", ".join(PALETTES)}（python3 hb/palettes.py list）')
        out.update(PALETTES[pid]['colors'])
    for k, v in spec.items():   # 角色写法（primary / accent / background …）映射到内部键
        if k == 'preset': continue
        out[ROLES.get(k, k)] = v
    if 'primary' in spec and 'G' not in spec: out['G'] = spec['primary']
    if 'accent' in spec and 'GOLD' not in spec: out['GOLD'] = spec['accent']
    return out

def gradient(spec, colors, dark):
    """返回 (css 渐变, 用于对比度 QA 的“最差”颜色)；spec = 渐变名 / 颜色列表 / {stops, angle}；dark = 文字所在的底是深色。"""
    if spec in (None, False, 'none'): return None
    if spec == 'brand':
        stops, angle = ([colors['GOLD'], '#FFFFFF'] if dark else [colors['G'], colors['OCH']]), 90
    elif isinstance(spec, str):
        if spec not in GRADIENTS: raise SystemExit(f'ERROR: 未知渐变 {spec}，可选：brand, {", ".join(GRADIENTS)}')
        stops, angle = GRADIENTS[spec]['stops'], GRADIENTS[spec]['angle']
    elif isinstance(spec, list): stops, angle = spec, 90
    else: stops, angle = spec['stops'], spec.get('angle', 90)
    worst = max(stops, key=lum) if not dark else min(stops, key=lum)    # 浅底上最亮的那一截最难看清，深底上反之
    return f'linear-gradient({angle}deg,{",".join(stops)})', worst

def check(quiet=False):
    bad = []
    for pid, p in PALETTES.items():
        c = p['colors']; paper = c.get('PAPER', '#FBFAF7')
        r = {k: contrast(c[k], paper) for k in ('G', 'OCH', 'INK', 'MUT') if k in c}
        need = dict(G=5.5, OCH=5.5, INK=7, MUT=4.5)
        fails = [f'{k} {v:.1f}' for k, v in r.items() if v < need[k]]
        if 'GOLD' in c and contrast(c['GOLD'], c['G']) < 3: fails.append(f'GOLD/G {contrast(c["GOLD"], c["G"]):.1f}')   # 深色底图（swiss 等）上的强调大字
        a, b_ = pair(c)
        if contrast(a, b_) < 3: fails.append(f'A/B {contrast(a, b_):.1f}')   # 撞色块上的大字（A 上用 B、B 上用 A）
        if fails: bad.append((pid, fails))
        if not quiet: print(f'{pid:13s} ' + '  '.join(f'{k} {v:4.1f}' for k, v in r.items()) + ('   ✗ ' + ', '.join(fails) if fails else '   ✓'))
    for gid, g in GRADIENTS.items():
        bg = '#FFFFFF' if g['on'] == 'light' else '#1A1A1A'
        w = min(contrast(s, bg) for s in g['stops'])
        if w < 3: bad.append((gid, [f'最弱一截 {w:.1f}']))
        if not quiet: print(f'渐变 {gid:10s} 在{"浅" if g["on"] == "light" else "深"}底上最弱一截 {w:.1f}:1' + ('  ✗' if w < 3 else '  ✓'))
    return bad

def sheet(out):
    import html as H
    cards = []
    for pid, p in PALETTES.items():
        c = p['colors']
        sw = ''.join(f'<span class="sw" style="background:{c[k]}"><b style="color:{"#fff" if lum(c[k]) < .3 else "#111"}">{k}<br>{c[k]}</b></span>' for k in ('A', 'B', 'G', 'OCH', 'GOLD', 'INK', 'MUT', 'PAPER') if k in c)
        cards.append(f'<div class="pc" style="background:{c.get("PAPER", "#FBFAF7")};color:{c.get("INK", "#17211C")}"><div class="t" style="color:{c["G"]}">{H.escape(p["zh"])}</div>'
                     f'<div class="id">colors: {pid} · {H.escape(p["use"])}</div><div class="row">{sw}</div></div>')
    gr = []
    for gid, g in GRADIENTS.items():
        css = f'linear-gradient({g["angle"]}deg,{",".join(g["stops"])})'
        bg = '#FFFFFF' if g['on'] == 'light' else '#14161C'
        gr.append(f'<div class="gc" style="background:{bg}"><span class="gt" style="background-image:{css}">渐变标题 Title</span><span class="gid" style="color:{"#666" if g["on"] == "light" else "#AAA"}">gradient: {gid} · {H.escape(g["zh"])}</span></div>')
    gradient_section = ('<h2 style="margin-top:22px">渐变标题（显式扩展）</h2><div class="grid">' + ''.join(gr) + '</div>') if gr else ''
    page = f'''<!doctype html><html lang="zh"><meta charset="utf-8"><style>
body{{margin:0;background:#E9E9E9;font-family:"Noto Sans SC","PingFang SC",sans-serif;width:1240px;padding:24px;box-sizing:border-box}}
h2{{font-size:15px;margin:6px 0 12px;color:#333}}.grid{{display:grid;grid-template-columns:1fr 1fr;gap:12px}}
.pc{{padding:16px 18px;border-radius:6px}}.t{{font-size:19px;font-weight:800}}.id{{font:11px monospace;opacity:.75;margin:4px 0 10px}}
.row{{display:flex;gap:6px}}.sw{{flex:1;height:58px;border-radius:4px;display:flex;align-items:flex-end;padding:5px;box-shadow:inset 0 0 0 1px rgba(0,0,0,.08)}}
.sw b{{font:600 9.5px/1.3 monospace}}
.gc{{padding:16px 20px;border-radius:6px;display:flex;align-items:center;gap:18px}}.gt{{font-size:34px;font-weight:900;-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}}
.gid{{font:11px monospace}}</style>
<h2>配色方案 book.colors（色块：G 小标签/编号 · OCH 斜体强调 · GOLD 深底大字与点缀 · INK 正文 · MUT 次要 · PAPER 纸色）</h2><div class="grid">{"".join(cards)}</div>
{gradient_section}</html>'''
    open(out, 'w', encoding='utf-8').write(page); print(out)

if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'list'
    if cmd == 'list':
        print('配色方案（book.colors: <名字>；不写时沿用风格默认）')
        for pid, p in PALETTES.items(): print(f'  {pid:13s} {p["zh"]} —— {p["use"]}')
        print('\n当前不推荐渐变标题；Swiss 禁用渐变。')
        for gid, g in GRADIENTS.items(): print(f'  {gid:13s} {g["zh"]}')
    elif cmd == 'check': sys.exit(1 if check() else 0)
    elif cmd == 'sheet': sheet(sys.argv[2] if len(sys.argv) > 2 else 'palettes.html')
