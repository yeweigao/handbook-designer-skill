#!/usr/bin/env python3
"""plan.py — 动手排版之前的“素材盘点 + 文案清单”。  用法：python3 plan.py <project_dir>
读 new_project.sh 产出的 doc.md / images.md / photos/，写：
  plan.md       素材盘点：字数、图片分档、每段的形状和建议版式、页数估计、原文里的空白 / 重复 / 页码问题、要问用户的事
  copy_map.md   文案清单：每段一个编号 S01…，标出位置（原第几页 / 哪一节）、类型猜测（标题、数据、日程、联系方式、待填空白……）、字数
  page-plan.md  逐页方案的空骨架（只在还没有时生成；格式和写法见 references/adaptation.md）——写完它才写 book.yaml
它只做机械的事；层级、成组、阅读顺序、错别字、事实这些判断留给你（agent）通读时补到 copy_map.md / page-plan.md 里。
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
# 为 Word 排的原稿不等于为册子排的：编号标签（「亮点一：」）、内部备注、版本标记不该印给读者。
# 这里只报候选；要不要去、怎么去，写进 adapt.yaml（check_copy 认账并出适配报告），见 references/adaptation.md「按产物适配」
_ZH_STEM = r'亮点|特色|特点|优势|卖点|要点|理念|保障|价值|成果'   # 读者不需要看编号的标签；步骤/任务/练习/第N天 是读者要用的序号，不在其中
_EN_STEM = r'Highlights?|Features?|Benefits?|Reasons?|Advantages?'
_lab = collections.defaultdict(list)
for l in lines:
    _b = plain(l)
    _m = re.match(rf'^({_ZH_STEM})\s*([一二三四五六七八九十百]+|\d{{1,2}})\s*[：:、.．]\s*\S', _b) or re.match(rf'^({_EN_STEM})\s*(\d{{1,2}})\s*[:：.\-–—]\s*\S', _b, re.I)
    if _m: _lab[_m.group(1).lower()].append(_b[:24])
for _s, _ls in _lab.items():
    if len(_ls) >= 2:
        _rx = rf"(?i)^{_s}\s*[0-9一二三四五六七八九十百]+\s*[:：.．、\-–—]\s*" if re.match(r'[a-z]', _s) else rf"^{_s}\s*[一二三四五六七八九十百\d]+\s*[：:、.．]\s*"
        issues.append(('编号标签前缀', f'「{_ls[0]}…」等 {len(_ls)} 行是「{_s}+序号：标题」的写法；册子里序号多半没意义，只留冒号后的标题 → 确认后在 adapt.yaml 写 strip: match: \'{_rx}\'（任务册、指南里读者要照着做的步骤号别去）'))
_NOTE = re.compile(r'^[（(【\[]?\s*(备注|批注|编辑备注|内部备注|审核意见|修改意见|设计说明|设计要求|排版要求|给设计师?|修订记录|版本记录|文档说明|撰写说明|写作说明|待办|TODO)\s*[）)】\]]?\s*[：:]|^[（(【\[]\s*(此处|这里)(插入|放|配|添加)|^(配图|插图|图片建议)\s*[：:]', re.I)
for l in lines:
    if _NOTE.search(plain(l)): issues.append(('疑似非读者内容', f'{plain(l)[:50]}（备注、批注或给设计的指示？确认后在 adapt.yaml 写 omit，成品里不印）'))
for l in lines:
    if l.startswith('#') and re.search(r'[（(【\[]\s*(?:(?:终稿|定稿|初稿|修订稿|审核稿|最终版|final)\s*(?:v\s?\d+(?:\.\d+)*)?|v\s?\d+(?:\.\d+)*)\s*[）)】\]]|[_\-\s]v\d+(?:\.\d+)*\s*$', plain(l), re.I):
        issues.append(('标题带版本标记', f'{plain(l)[:50]}（Word 文件名式的标题？确认后在 adapt.yaml 写 strip: match: \'\\s*[（(【\\[][^）)】\\]]*(终稿|定稿|初稿|修订稿|审核稿|最终版|v\\d+)[^）)】\\]]*[）)】\\]]\\s*$\'，书名用不带标记的；或让用户给册子正式名称）'))
_artf = os.path.join(P, '.qa', 'artifacts.txt')
_arts = [l.strip().split('：', 1)[-1].strip() for l in open(_artf, encoding='utf-8')] if os.path.exists(_artf) else []
_arts = [a for a in _arts if a and not a.startswith('#')]
if _arts: issues.append(('页码 artifacts', f'{len(_arts)} 处已按页码排除（{"、".join(_arts[:6])}）：页脚页码不当正文，成品用手册自动页码；其中若混了真正文，改 doc.md 删掉该行'))
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

# ---------------------------------------------------------------- 文案清单 copy_map.md（每段一个编号，逐页设计时按编号分配）
def kind(l, t):
    if l: return '标题'
    if t.startswith('|'): return '表格'
    if re.search(r'_{3,}|＿{2,}|[:：]\s*$|[¥￥]\s*(?=[\s_]|$)|（\s*）|待定|TBD', t): return '待填空白'
    if re.search(r'@|微信|WeChat|电话|Tel|☎|www\.|https?://|\.com\b', t, re.I): return '联系方式'
    if re.search(r'\b\d{1,2}[:：]\d{2}\b|Day\s*\d|第\s*[一二三四五六七八九十\d]+\s*天|\b\d{4}[./-]\d{1,2}|\d{1,2}\s*月\s*\d{1,2}\s*日', t, re.I): return '日程/日期'
    if re.match(r'^([-*•▶✓]|\d+[.、)])\s*', t): return '列表项'
    if re.search(r'[“「"].{6,}[”」"]', t): return '引语'
    if re.search(r'\d', t) and count(t) < 30: return '数据'
    return '短句' if count(t) < 30 else '段落'
segs = []; where = '开头'; pgno = None
for raw in md.splitlines():
    s_ = raw.strip()
    m = re.match(r'^<!--\s*第\s*(\d+)\s*([页节])', s_)
    if m: pgno = f'原第 {m.group(1)} {m.group(2)}'; where = pgno; continue
    if not s_ or s_.startswith('<!--') or re.fullmatch(r'\|[\s:|-]*\|', s_) or re.fullmatch(r'!\[[^\]]*\]\([^)]*\)|<img\b[^>]*>', s_): continue
    h = re.match(r'^(#{1,3})\s+(.*)', s_); bold = re.fullmatch(r'\*\*(.+)\*\*', s_)
    lv = ('H' if h and len(h.group(1)) == 1 else 'h') if h else ('h' if bold and len(bold.group(1)) < 40 else '')
    t = plain(s_) if lv else re.sub(r'\*\*|__', '', s_)
    t = re.sub(r'\\([_*\-.#\[\]()!+])', r'\1', t)   # Markdown 转义（\_ \*）还原成原文字符
    if t.startswith('|'): t = '| ' + ' · '.join(c.strip() for c in t.strip('|').split('|'))   # 表格行：单元格用 · 隔开
    if lv and not pgno: where = t[:20]
    segs.append((where if not lv or pgno else t[:20], lv, t))
cm = ['# 文案清单（plan.py 自动生成；类型是猜的，层级、成组、阅读顺序请对照原文改对）', '',
      '写 page-plan.md 时，在页面总表里用 S 编号写“这一页放哪几段”；每个编号都要用到（原文一字不改，排不下就挪页，不删）。', '',
      '| # | 位置 | 类型 | 字数 | 文案 |', '|---|---|---|---|---|']
for k, (w, l, t) in enumerate(segs, 1):
    tt = t[2:] if t.startswith('| ') else t
    cm.append(f'| S{k:02d} | {w} | {kind(l, t)} | {count(tt)} | {tt.replace("|", "/")[:120]}{"…" if len(tt) > 120 else ""} |')
open(os.path.join(P, 'copy_map.md'), 'w', encoding='utf-8').write('\n'.join(cm) + '\n')

# ---------------------------------------------------------------- 写 plan.md；page-plan.md 只在没有时给一个骨架（不覆盖你写的方案）
o.append(f'\n文案逐段编号见 copy_map.md（共 {len(segs)} 段 S01–S{len(segs):02d}）；page-plan.md 里用 S 编号写每页放哪几段（references/adaptation.md）。')
open(os.path.join(P, 'plan.md'), 'w', encoding='utf-8').write('\n'.join(o) + '\n')
PP = os.path.join(P, 'page-plan.md')
if not os.path.exists(PP):
    open(PP, 'w', encoding='utf-8').write(
        '# 逐页方案 page-plan.md（先写完再写 book.yaml；格式与写法见 references/adaptation.md）\n\n'
        '## 整册翻页节奏\n- 叙事弧与高点：〔封面、章节开篇、最打动人的亮点、结尾号召〕\n- 跨页：〔几组、放在哪、各自的任务；左页偶数页〕\n'
        '- 密集 / 呼吸 / 锚点页怎么交替：〔〕\n- 配图：〔最好的照片给哪几页；横图 → 跨页，竖图 → 海报 / 侧条；一图一用〕\n- 字体分工：〔〕\n\n'
        '## 页面总表\n| 页 | 文案（S 编号） | job | 视觉主角 | 版式 | 图 |\n|---|---|---|---|---|---|\n| 1 | 〔S01–S03〕 | cover | 〔照片 / 大字 / 数据〕 | 〔FULL〕 | 〔〕 |\n\n'
        '## 第 1 页\n- 页面任务：〔读者看完要知道或做什么；只设一个主要焦点〕\n- 文案分工：〔主标题 / 栏目字 / 序号 / 导语 / 正文 / 数据 / 时间地点 / 行动信息〕\n'
        '- 采用文案：〔S 编号；有改写列原句 → 采用句〕\n- 展示方案：〔视觉主角；视线 第一眼 → 第二眼 → 第三眼；字放在照片哪块安静区；版式由此推出 + 理由〕\n'
        '- 留白与对齐：〔〕\n- 验收重点：〔〕\n')
print('\n'.join(o)); print(f'\n→ {P}/plan.md · {P}/copy_map.md' + ('' if os.path.exists(PP) and 'S01–S03〕' not in open(PP, encoding='utf-8').read() else f' · {P}/page-plan.md（骨架）'))
