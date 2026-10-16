#!/usr/bin/env python3
"""配色方案（book.colors）与渐变标题（book.gradient / 块的 gradient）。
  python3 hb/palettes.py list            列出所有配色与渐变
  python3 hb/palettes.py check           检查每套配色的对比度（印刷小字要求）
  python3 hb/palettes.py sheet <out.html> 生成色卡页（references/gallery/palettes.jpg 由它截图）

配色只有 6 个键（INK G OCH GOLD MUT PAPER，含义见 references/style.md §3）。经典撞色里的“原色”往往太亮，
直接做 10px 小字在纸上看不清——所以每套都拆成两种用法：原色放在 GOLD（深色底/底图上的大字与点缀、无图风格的大色块），
纸面上的小字用同色相加深的版本（G/OCH，对纸色 ≥ 5.5:1）。写进 book.colors 的单个键会覆盖方案里的同名键。
"""
import sys

PALETTES = {
  # ---- 设计圈经典撞色
  'klein':     dict(zh='克莱因蓝 × 拿坡里黄', use='艺术、设计、展览、高识别度活动', colors=dict(G='#002BA5', OCH='#6B4E00', GOLD='#FFE893', INK='#0A1433', MUT='#46506A', PAPER='#FFFBEB')),
  'hermes':    dict(zh='爱马仕橙 × 乌漆黑', use='高端品牌、时尚、精品活动', colors=dict(G='#000010', OCH='#A84300', GOLD='#FF770F', INK='#000010', MUT='#4A4038', PAPER='#FFF5EC')),
  'china-red': dict(zh='中国红 × 鱼肚白（配金）', use='节庆、传统文化、政企、开学典礼', colors=dict(G='#B5000C', OCH='#7A5A1E', GOLD='#F4C76B', INK='#1F1414', MUT='#574848', PAPER='#F7F7EE')),
  'lemon-violet': dict(zh='柠檬黄 × 帝王紫', use='潮流、青年、音乐节、社团招新', colors=dict(G='#6A0DAD', OCH='#6E5800', GOLD='#FFF300', INK='#1E0A33', MUT='#4E4560', PAPER='#FFFDE8')),
  'navy':      dict(zh='海军蓝 × 芥末黄 × 雾灰', use='学院、商务、航海、稳重正式', colors=dict(G='#114F99', OCH='#08337D', GOLD='#ECCA3E', INK='#0B2249', MUT='#4A5568', PAPER='#F5F4EF')),
  'tiffany':   dict(zh='蒂芙尼蓝 × 白', use='婚礼、女性向、轻奢、春夏', colors=dict(G='#00706A', OCH='#1F4F4B', GOLD='#81D8D0', INK='#14201F', MUT='#4A5655', PAPER='#F7FBFA')),
  'bordeaux':  dict(zh='勃艮第酒红 × 香槟金', use='晚宴、年会、颁奖、秋冬', colors=dict(G='#7B1E2B', OCH='#7A5C22', GOLD='#E9CF9B', INK='#2A1A1C', MUT='#5A4A4C', PAPER='#FBF7F0')),
  'bauhaus':   dict(zh='包豪斯三原色（红 · 黄 · 蓝）', use='设计教育、建筑、现代主义、儿童美育', colors=dict(G='#1E3F9C', OCH='#B01E17', GOLD='#F2C230', INK='#141414', MUT='#4A4A4A', PAPER='#F4EFE6')),
  'morandi':   dict(zh='莫兰迪灰调', use='生活方式、文艺、安静的长文、家居', colors=dict(G='#4F5C55', OCH='#6E5048', GOLD='#D9C4A9', INK='#2E3330', MUT='#5C625F', PAPER='#F2EFEA')),
  'chinese':   dict(zh='中国传统色（黛青 · 朱砂 · 藤黄 · 宣纸）', use='国学、非遗、书院、博物馆研学', colors=dict(G='#2C4A52', OCH='#A13D2D', GOLD='#F0C239', INK='#1E2422', MUT='#545B58', PAPER='#F6F1E4')),
  'terracotta': dict(zh='陶土 × 橄榄（大地色）', use='户外、手作、农场、可持续主题', colors=dict(G='#8E3B1E', OCH='#55612F', GOLD='#E9B44C', INK='#2B211C', MUT='#5B4F47', PAPER='#F8F2E9')),
  'sage':      dict(zh='鼠尾草绿 × 燕麦（北欧）', use='健康、亲子、自然教育、清新', colors=dict(G='#4A6652', OCH='#7C5135', GOLD='#E8D9B5', INK='#24302A', MUT='#56605A', PAPER='#F6F3EC')),
  'coral':     dict(zh='珊瑚橘 × 深海蓝', use='海洋、夏令营、运动、活力', colors=dict(G='#0F4C5C', OCH='#AD3A1E', GOLD='#FF7F5C', INK='#13262C', MUT='#4B5A5F', PAPER='#FFF8F4')),
  'lavender':  dict(zh='薰衣草紫 × 雾粉', use='女性向、艺术疗愈、温柔低龄', colors=dict(G='#5B4B8A', OCH='#8A4466', GOLD='#D9CCF2', INK='#221E2E', MUT='#57536A', PAPER='#FAF8FD')),
  # ---- 按主题（适合 photo 风格的照片手册；只覆盖强调色，纸色等沿用风格默认）
  'nature':    dict(zh='森林绿 × 赭石 × 金（photo 默认）', use='自然、户外、研学', colors=dict(G='#1D5A43', OCH='#7E560E', GOLD='#F2C14E')),
  'campus':    dict(zh='学院蓝 × 赭金', use='校园、学术、家长手册', colors=dict(G='#1F3A5F', OCH='#8A5A12', GOLD='#F2C14E')),
  'heritage':  dict(zh='砖红 × 棕金', use='人文、历史、东亚城市', colors=dict(G='#8E2F23', OCH='#6B4A1E', GOLD='#F4C76B')),
  'ocean':     dict(zh='海洋蓝 × 冰蓝', use='海洋、极地、科学', colors=dict(G='#1E5A7A', OCH='#2F6F6A', GOLD='#9FD8F0')),
  'art':       dict(zh='深紫 × 橙', use='艺术、设计、创意营', colors=dict(G='#5A2A6E', OCH='#A4471E', GOLD='#FFC56B')),
  'corporate': dict(zh='石墨蓝 × 明黄', use='企业、入职、培训', colors=dict(G='#243B53', OCH='#536270', GOLD='#FFD166')),
  'kids':      dict(zh='暖橙 × 青绿（更暖更亮）', use='低幼、亲子', colors=dict(G='#A3441D', OCH='#256B5B', GOLD='#FFD166', PAPER='#FFFDF7')),
}

# 渐变标题：on = 适合放在什么底上（light 浅色纸面/浅底图，dark 照片/深底图）；angle 为 CSS 角度（90 横向，180 竖向）
GRADIENTS = {
  'energy':    dict(zh='高能（橙 → 蓝）', stops=['#F06620', '#C9741F', '#164BC5', '#3F7FBF'], angle=100, on='light'),
  'mystic':    dict(zh='妙彩（紫 → 蓝 → 绿）', stops=['#8F63BA', '#7A6FBF', '#5E78AD', '#4F8045'], angle=90, on='light'),
  'cool':      dict(zh='拉风（深蓝竖向）', stops=['#024F97', '#1D6EB6'], angle=180, on='light'),
  'slate':     dict(zh='轻薄（石墨灰竖向）', stops=['#4E5D68', '#647582', '#7F8E9A'], angle=180, on='light'),
  'orchid':    dict(zh='写照（紫 → 洋红竖向）', stops=['#8846AA', '#B93886'], angle=180, on='light'),
  'spotlight': dict(zh='看我（蓝 → 紫 → 粉 → 橙）', stops=['#2F7FE8', '#7F50F3', '#D9418F', '#E0582E'], angle=90, on='light'),
  'ink':       dict(zh='墨（黑 → 灰蓝）', stops=['#111827', '#3B4A63'], angle=180, on='light'),
  'ocean':     dict(zh='深海（青 → 蓝）', stops=['#0F766E', '#1D4ED8'], angle=90, on='light'),
  'siri':      dict(zh='Siri（橙 → 粉 → 紫 → 蓝，亮色，用于深底）', stops=['#FD9F59', '#F487A3', '#C488C8', '#81C4FD'], angle=90, on='dark'),
  'sunset':    dict(zh='落日（金 → 珊瑚 → 玫红，用于深底）', stops=['#FFD36E', '#FF8A5B', '#F06BA8'], angle=90, on='dark'),
  'gold':      dict(zh='金属金（用于深底、中国红、黑底）', stops=['#F9E3A3', '#D9A84E', '#F7DC8C'], angle=180, on='dark'),
  'aurora':    dict(zh='极光（薄荷 → 天蓝 → 淡紫，用于深底）', stops=['#A8FFDF', '#8CC8FF', '#C9A7FF'], angle=90, on='dark'),
  # brand：用当前配色自动生成——浅底 G → OCH，深底 GOLD → 白
}

def lum(h):
    h = h.lstrip('#'); c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    c = [x / 12.92 if x <= .03928 else ((x + .055) / 1.055) ** 2.4 for x in c]
    return .2126 * c[0] + .7152 * c[1] + .0722 * c[2]
def contrast(a, b): a, b = lum(a), lum(b); return (max(a, b) + .05) / (min(a, b) + .05)

def resolve(spec, base):
    """book.colors 可以写：方案名（'klein'）、{preset: klein, G: '#...'}、或只写颜色键。base = 风格默认配色。"""
    out = dict(base)
    if spec is None: return out
    if isinstance(spec, str): spec = {'preset': spec}
    if not isinstance(spec, dict): raise SystemExit('ERROR: book.colors 要写配色方案名（如 klein）或颜色键字典（如 {G: "#1D5A43"}）')
    pid = spec.get('preset')
    if pid is not None:
        if pid not in PALETTES: raise SystemExit(f'ERROR: 未知配色方案 {pid}，可选：{", ".join(PALETTES)}（python3 hb/palettes.py list）')
        out.update(PALETTES[pid]['colors'])
    out.update({k: v for k, v in spec.items() if k != 'preset'})
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
        sw = ''.join(f'<span class="sw" style="background:{c[k]}"><b style="color:{"#fff" if lum(c[k]) < .3 else "#111"}">{k}<br>{c[k]}</b></span>' for k in ('G', 'OCH', 'GOLD', 'INK', 'MUT', 'PAPER') if k in c)
        cards.append(f'<div class="pc" style="background:{c.get("PAPER", "#FBFAF7")};color:{c.get("INK", "#17211C")}"><div class="t" style="color:{c["G"]}">{H.escape(p["zh"])}</div>'
                     f'<div class="id">colors: {pid} · {H.escape(p["use"])}</div><div class="row">{sw}</div></div>')
    gr = []
    for gid, g in GRADIENTS.items():
        css = f'linear-gradient({g["angle"]}deg,{",".join(g["stops"])})'
        bg = '#FFFFFF' if g['on'] == 'light' else '#14161C'
        gr.append(f'<div class="gc" style="background:{bg}"><span class="gt" style="background-image:{css}">渐变标题 Title</span><span class="gid" style="color:{"#666" if g["on"] == "light" else "#AAA"}">gradient: {gid} · {H.escape(g["zh"])}</span></div>')
    page = f'''<!doctype html><html lang="zh"><meta charset="utf-8"><style>
body{{margin:0;background:#E9E9E9;font-family:"Noto Sans SC","PingFang SC",sans-serif;width:1240px;padding:24px;box-sizing:border-box}}
h2{{font-size:15px;margin:6px 0 12px;color:#333}}.grid{{display:grid;grid-template-columns:1fr 1fr;gap:12px}}
.pc{{padding:16px 18px;border-radius:6px}}.t{{font-size:19px;font-weight:800}}.id{{font:11px monospace;opacity:.75;margin:4px 0 10px}}
.row{{display:flex;gap:6px}}.sw{{flex:1;height:58px;border-radius:4px;display:flex;align-items:flex-end;padding:5px;box-shadow:inset 0 0 0 1px rgba(0,0,0,.08)}}
.sw b{{font:600 9.5px/1.3 monospace}}
.gc{{padding:16px 20px;border-radius:6px;display:flex;align-items:center;gap:18px}}.gt{{font-size:34px;font-weight:900;-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}}
.gid{{font:11px monospace}}</style>
<h2>配色方案 book.colors（色块：G 小标签/编号 · OCH 斜体强调 · GOLD 深底大字与点缀 · INK 正文 · MUT 次要 · PAPER 纸色）</h2><div class="grid">{"".join(cards)}</div>
<h2 style="margin-top:22px">渐变标题 book.gradient / 块的 gradient（可选）</h2><div class="grid">{"".join(gr)}</div></html>'''
    open(out, 'w', encoding='utf-8').write(page); print(out)

if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'list'
    if cmd == 'list':
        print('配色方案（book.colors: <名字>）：')
        for pid, p in PALETTES.items(): print(f'  {pid:13s} {p["zh"]} —— {p["use"]}')
        print('\n渐变标题（book.gradient: <名字>，或块里写 gradient:）：\n  brand         用当前配色自动生成')
        for gid, g in GRADIENTS.items(): print(f'  {gid:13s} {g["zh"]}')
    elif cmd == 'check': sys.exit(1 if check() else 0)
    elif cmd == 'sheet': sheet(sys.argv[2] if len(sys.argv) > 2 else 'palettes.html')
