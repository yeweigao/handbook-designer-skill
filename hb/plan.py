#!/usr/bin/env python3
"""plan.py — 动手排版之前的“素材盘点 + 待确认清单”。  用法：python3 plan.py <project_dir>
读 new_project.sh 产出的 doc.md / images.md / photos/，写 <project_dir>/plan.md 并打印。
它只做机械的事：数字数、数图、按清晰度分档、按内容形状给每段建议一个内容版式、估页数、
找原文里的空白（____ / ¥ ___ / 待定）、重复段落、页码样式文字、缺的链接。
错别字、事实、语气这些判断留给你（agent）通读时补充。拿到 plan.md 后：写 2–3 个方案发给用户，等用户选定再排版（SKILL.md 第 0 步）。
"""
import sys, os, re, glob, collections
P = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else '.')
DOC = os.path.join(P, 'doc.md')
if not os.path.exists(DOC): sys.exit(f'找不到 {DOC}：先跑 new_project.sh <项目> <原文>')
md = open(DOC, encoding='utf-8').read()
CJK = re.compile(r'[㐀-鿿豈-﫿]')
def count(s):   # 中文按字，西文按词
    return len(CJK.findall(s)) + len(re.findall(r'[A-Za-z][A-Za-z\'’-]*', s))
def plain(s): return re.sub(r'\*\*|__|\\(?=\S)|^#+\s*|^[-*•▶✓]\s*|^\d+[.、)]\s*', '', s.strip())
zh = len(CJK.findall(md)); en = len(re.findall(r'[A-Za-z]+', md)); LANG = 'zh' if zh >= en * .6 else 'en'

# ---------------------------------------------------------------- 分段（按标题；PPT 按页）
secs = []; cur = None; srcpg = None
def new(t):
    global cur
    cur = dict(title=t, lines=[], src=srcpg); secs.append(cur)
for raw in md.splitlines():
    s = raw.strip()
    m = re.match(r'^<!--\s*第\s*(\d+)\s*[页节](.*?)-->$', s)
    if m: srcpg = (int(m.group(1)), m.group(2)); cur = None; continue      # PPT/PDF：每页一段
    if not s or s.startswith('<!--') or re.fullmatch(r'!\[[^\]]*\]\([^)]*\)|<img\b[^>]*>', s): continue
    h = re.match(r'^(#{1,3})\s+(.*)', s); bold = re.fullmatch(r'\*\*(.+)\*\*', s)
    if h or (bold and len(bold.group(1)) < 40):
        t = plain(h.group(2) if h else bold.group(1))
        if cur is not None and not cur['lines'] and cur['src'] == srcpg: cur['title'] += ' / ' + t   # 连续两行标题（主副标题）合成一段
        else: new(t)
        continue
    if cur is None: new(plain(s)[:30])
    cur['lines'].append(s)
for x in secs:
    L = x['lines']; x['n'] = count(' '.join(L)) + count(x['title'])
    x['items'] = [l for l in L if re.match(r'^([-*•▶✓]|\d+[.、)])\s*', l)]
    if not x['items']:   # 网页 / PPT 抄下来的稿子常常没有列表符号：一串短行（小标题 + 一句话）也当条目
        short = [l for l in L if count(l) <= 60]
        if len(short) >= 4 and len(short) >= len(L) * .5: x['items'] = [l for l in L if count(l) <= 24] or short
    x['paras'] = [l for l in L if l not in x['items'] and not l.startswith('|')]
    x['table'] = [l for l in L if l.startswith('|') and not re.fullmatch(r'\|[\s:|-]*\|', l)]
    x['times'] = len(re.findall(r'\b\d{1,2}[:：]\d{2}\b|Day\s*\d+|第\s*[一二三四五六七八九十\d]+\s*天|\b\d{4}[./-]\d{1,2}([./-]\d{1,2})?\b|\d{1,2}\s*月\s*\d{1,2}\s*日', ' '.join(L), re.I))
    x['nums'] = len(re.findall(r'(?<![\w.])\d[\d,.]*\s*(\+|%|％|万|千|人|所|名|年|个|天|校|国|countries|students|schools|years)', ' '.join(L), re.I))
    x['quote'] = bool(re.search(r'[“「"].{6,}[”」"]\s*(——|—|--)', ' '.join(L)))
    pm = re.search(r'照片：([^·]+)', x['src'][1]) if x['src'] else None
    x['photos'] = len(pm.group(1).strip().split('、')) if pm else 0

def suggest(x):
    """内容形状 → 内容版式（只是起点，方案里可以改）"""
    it, n, avg = len(x['items']), x['n'], (sum(count(i) for i in x['items']) / max(1, len(x['items'])))
    if x['table'] or x['times'] >= 3: return 'GRID', '表格/日程/时间多'
    if n <= 25 and not x['items']: return 'FULL', '只有标题或一句话 → 章节页/封面式'
    if x['photos'] >= 3: return 'COLLAGE', f'这一段配了 {x["photos"]} 张照片'
    if 2 <= it <= 4 and avg > 40: return 'STAGGER', f'{it} 条、每条较长 → 图文错位'
    if 2 <= it <= 9: return 'CARDS', f'{it} 条短条目 → 卡片'
    if it > 9: return 'GRID', f'{it} 条条目 → 网格多栏（或拆两页 CARDS）'
    if x['quote'] and n < 400: return 'ONE', '有引语、字不多 → 单栏'
    if n > 600: return 'TWO', f'约 {n} 字长文 → 双栏'
    if x['photos'] >= 1: return 'MIX', '一段文字 + 配图 → 组合'
    return 'ONE', f'约 {n} 字段落 → 单栏'
for x in secs: x['lay'], x['why'] = suggest(x)

# ---------------------------------------------------------------- 图片
ph = os.path.join(P, 'photos'); kinds = {}
if os.path.exists(os.path.join(P, 'images.md')):
    for l in open(os.path.join(P, 'images.md'), encoding='utf-8'):
        c = [a.strip() for a in l.strip().strip('|').split('|')]
        if len(c) >= 4 and c[0] and not c[0].startswith(('文件', '---')): kinds[c[0]] = c[3]
imgs = []
try:
    from PIL import Image
    for f in sorted(glob.glob(os.path.join(ph, '*'))):
        b = os.path.basename(f)
        if b.startswith(('_', '.')) or not b.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')): continue
        try: w, h = Image.open(f).size
        except Exception: continue
        imgs.append((b, w, h, kinds.get(b, '照片')))
except ImportError: pass
pho = [i for i in imgs if i[3] == '照片']; gra = [i for i in imgs if i[3] != '照片']
big = [i for i in pho if max(i[1], i[2]) >= 2500]; mid = [i for i in pho if 1400 <= max(i[1], i[2]) < 2500]; small = [i for i in pho if max(i[1], i[2]) < 1400]
assets = [os.path.basename(f) for f in glob.glob(os.path.join(ph, '_assets', '*'))]

# ---------------------------------------------------------------- 原文问题（只照原文报告，不改）
lines = [l.strip() for l in md.splitlines() if l.strip() and not l.strip().startswith('<!--')]
issues = []
BL = re.compile(r'([:：]\s*_+\s*$|_{2,}|＿{2,}|（\s*）|\(\s*\)|【\s*】|\[\s*\]|\bTBD\b|\bTBC\b|待定|待确认|待补充|XX+|xx{2,}|[¥￥$€]\s*(?=[\s_]|$)|CNY\s*(?=[\s_]|$))')
for l in lines:
    if BL.search(l): issues.append(('空白/待定', l.lstrip('-*• ')[:70]))
seen = collections.Counter(re.sub(r'\s+', '', plain(l)) for l in lines if count(l) >= 6)
for k, v in seen.items():
    if v >= 2: issues.append(('重复出现', f'{k[:60]}（{v} 次）'))
tails = collections.Counter(re.sub(r'\s+', ' ', re.split(r'[:：]', plain(l), maxsplit=1)[1]).strip().lower() for l in lines if re.search(r'[:：]', plain(l)) and not re.search(r'https?:', l))
for k, v in tails.items():
    if v >= 2 and count(k) >= 4: issues.append(('同一内容出现在不同条目里', f'“{k[:60]}”（{v} 处）'))
for l in lines:
    if re.search(r'(?<![\d.:])\b\d{1,3}\s*/\s*\d{1,3}\b(?![\d/])', l) and not re.search(r'\d{4}', l): issues.append(('页码样式文字', plain(l)[:60]))
for m in re.finditer(r'\b(\w+)\s+\1\b', md, re.I):
    if not m.group(1).isdigit(): issues.append(('连续重复的词', m.group(0)))
try:
    from spellchecker import SpellChecker   # 可选：pip install pyspellchecker
    sc = SpellChecker(); words = set(w for w in re.findall(r'\b[a-z]{4,}\b', md))
    for w in sorted(sc.unknown(words))[:20]: issues.append(('英文拼写待查', f'{w} → {sc.correction(w)}?'))
except Exception: pass
urls = re.findall(r'https?://\S+|www\.\S+', md)
qr_hint = re.search(r'二维码|扫码|QR|scan', md, re.I)

# ---------------------------------------------------------------- 页数估计
body = sum(1 for x in secs if x['n'] > 0 or x['lines'])
full = body + 2                      # + 封面 + 封底
def r4(n): return max(4, -(-n // 4) * 4)
lite = max(4, r4(round(body * .5) + 2))

# ---------------------------------------------------------------- 写 plan.md
o = []
o.append('# 素材盘点（plan.py 自动生成，给你写方案用；不要原样发给用户）\n')
o.append(f'- 原文：约 {count(md)} {"字" if LANG == "zh" else "词"}，语言 {"中文" if LANG == "zh" else "英文"}，{len(secs)} 段' + (f'，来自 {max((x["src"][0] for x in secs if x["src"]), default=0)} 页 PPT/PDF' if any(x['src'] for x in secs) else ''))
o.append(f'- 照片：{len(pho)} 张（≥2500px 可印满版 {len(big)} · 1400–2500px 满版只够电子版、印刷改半版/插图 {len(mid)} · <1400px 只做小图 {len(small)}）；图形/截图 {len(gra)} 张；logo/装饰 {len(assets)} 个')
if not pho: o.append('- 没有照片 → 方案里给无图风格（editorial / swiss / notebook / aurora …，按受众选），或 photo + 占位等用户补图，或 AI 配图（问用户）')
o.append(f'- 页数估计：完整版约 {full} 页 → 骑马钉 {r4(full)} 页；精简版 {lite} 页（只留亮点、日程、费用、报名）')
o.append('\n## 每段内容的形状 → 建议版式\n')
o.append('| # | 原文段落 | 字数 | 形状 | 建议版式 |\n|---|---|---|---|---|')
for i, x in enumerate(secs, 1):
    o.append(f'| {i} | {x["title"][:28]}{" （原第 %d 页）" % x["src"][0] if x["src"] else ""} | {x["n"]} | {x["why"]} | {x["lay"]} |')
o.append('\n建议版式只是起点：相邻两段同版式时引擎会自动换镜像；宣传册里每 3–4 页穿插一张 FULL 或跨页大图，节奏模板见 references/rhythms.md。')
o.append('\n## 需要用户确认的原文问题（照原文排，不擅自改）\n')
if issues:
    for k, v in issues: o.append(f'- 【{k}】{v}')
else: o.append('- 脚本没找到空白、重复或页码问题。')
o.append('- 【你来通读】错别字、前后矛盾、过时信息、事实（开放时间、价格、日期）——脚本查不出来，读一遍补到这里。')
if qr_hint and not urls: o.append('- 【缺链接】原文提到二维码/扫码，但没有链接：问用户要报名链接，或直接用原资料里的二维码图片。')
import yaml as _y
_R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_K = _y.safe_load(open(os.path.join(_R, 'purposes', 'index.yaml'), encoding='utf-8')) or {}
_B = _y.safe_load(open(os.path.join(_R, 'brands', 'index.yaml'), encoding='utf-8')) or {}
o.append('\n## 第 1 轮（沟通合同）里要问的（只问会影响结果的；流程见 workflows/new.md）\n')
o.append('1. 沟通合同：读者、场景、读完要做的事、语气、必须出现、不能出现——你先按原文填一版，让用户改')
o.append('2. 用途方法 book.kind：' + ' / '.join(f'{k} {v.get("zh", "")}' for k, v in _K.items()) + '（都不像就只写 purpose：任务册 workbook / 指南 guide / 宣传册 brochure——拿不准时问“读者需要在册子上写字吗？”）')
if _B: o.append('   品牌包 book.brand：' + ' / '.join(f'{k}（{v.get("name", "")}）' for k, v in _B.items()) + '——原文或用户提到这个品牌就直接用')
o.append('3. 语言：只做原文语言，还是中英两版（同一套版式、一份 yaml 出两本；翻译部分会单独标出）')
o.append('4. 视觉（第 2 轮用 directions.py 出三个方向的样张让用户看图选）：有好照片 → photo；没有 → photo 撞色字体海报，或 1–2 种无图风格（references/gallery/style_*.jpg）。配色先推荐四组经典撞色：克莱因蓝 × 拿坡里黄（默认 klein）/ 爱马仕橙 × 乌漆嘛黑（hermes）/ 中国红 × 鱼肚白（china-red）/ 柠檬黄 × 帝王紫（lemon-violet），见 references/gallery/palettes_overview.jpg；有品牌色就用品牌色')
o.append('5. 上面的原文问题：改还是照原文')
o.append('6. 图片不够/不清晰时：用户补原图，还是 AI 补图（AI 图会标注）')
o.append('7. 打印还是电子版；骑马钉要 4 的倍数页')
open(os.path.join(P, 'plan.md'), 'w', encoding='utf-8').write('\n'.join(o) + '\n')
print('\n'.join(o)); print(f'\n→ {P}/plan.md')
