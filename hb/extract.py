#!/usr/bin/env python3
"""从带图的资料里同时抽出“文字 + 图片”，并把两者按页对上：宣讲 PPT、Word、PDF → 手册素材。
  python3 hb/extract.py 资料.pptx|.docx|.pdf <project_dir> [--images-only]
  （new_project.sh 会自动调用：.pptx 走全套；.docx/.pdf 的正文由 doc2yaml 转换，这里只抽图片）

输出（都在 project_dir 里）：
  doc.md            原文（按页/按段顺序；<!-- 第 N 页 · 照片：s03_1.jpg · 图形：s03_2.png --> 注释标出每页对应的图片，原文核对会忽略注释）
  notes.md          PPT 的演讲者备注（不是正文，需要时再取用）
  photos/           可用图片，按出处命名：s03_1.jpg = 第 3 页第 1 张（Word 为 d012.jpg = 第 12 段附近）
  photos/_assets/   重复出现的元素（logo、页眉装饰、背景）和太小的图标——一般不用，封面/封底需要 logo 时从这里取
  images.md         图片清单：尺寸、类型（照片 / 图形）、在原页面里的占比、建议用法
  photos/_contact.jpg  缩略图总览（先看它再排版）
  .qa/artifacts.txt 页码 artifacts（页脚页码、居中短数字）：不是正文，check_copy 原文核对不要求出现

不需要额外安装：.pptx/.docx 直接解析文件结构；.pdf 用 poppler 的 pdftotext / pdfimages（mac：brew install poppler）。
EMF/WMF 矢量图会尝试用 LibreOffice 转 PNG，转不了就列在 images.md 里。
"""
import sys, os, re, io, zipfile, hashlib, shutil, subprocess, posixpath, tempfile
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image, ImageDraw, ImageFont

NS = dict(a='http://schemas.openxmlformats.org/drawingml/2006/main', p='http://schemas.openxmlformats.org/presentationml/2006/main',
          r='http://schemas.openxmlformats.org/officeDocument/2006/relationships', w='http://schemas.openxmlformats.org/wordprocessingml/2006/main',
          rel='http://schemas.openxmlformats.org/package/2006/relationships')
RID = '{%s}embed' % NS['r']
def q(tag): pre, t = tag.split(':'); return '{%s}%s' % (NS[pre], t)
PAGENO = re.compile(r'^\d{1,2}\s*/\s*\d{1,2}$|^\d{1,2}$')   # 页脚页码样式：「02 / 23」、居中短数字行
def is_pageno(line):
    t = re.sub(r'^(#{1,3}\s*|[-*•▶✓]\s+|\d+[.、)]\s+)', '', line.strip()).strip()
    return bool(PAGENO.match(t))

def rels(z, part):
    d, b = posixpath.split(part); rp = posixpath.join(d, '_rels', b + '.rels')
    if rp not in z.namelist(): return {}
    out = {}
    for r in ET.fromstring(z.read(rp)).iter(q('rel:Relationship')):
        t = r.get('Target'); out[r.get('Id')] = (posixpath.normpath(posixpath.join(d, t)) if r.get('TargetMode') != 'External' else None, r.get('Type', ''))
    return out

# ------------------------------------------------------------------ PPTX
def from_pptx(path):
    z = zipfile.ZipFile(path); pres = ET.fromstring(z.read('ppt/presentation.xml')); prel = rels(z, 'ppt/presentation.xml')
    sz = pres.find(q('p:sldSz')); SW, SH = (int(sz.get('cx')), int(sz.get('cy'))) if sz is not None else (12192000, 6858000)
    slides = [prel[s.get('{%s}id' % NS['r'])][0] for s in pres.iter(q('p:sldId'))]
    pages = []
    for i, part in enumerate(slides, 1):
        x = ET.fromstring(z.read(part)); rl = rels(z, part); lines = []; imgs = []
        for el in x.iter():
            if el.tag == q('p:sp'):
                ph = el.find('.//' + q('p:ph')); is_title = ph is not None and ph.get('type') in ('title', 'ctrTitle')
                if ph is not None and ph.get('type') in ('sldNum', 'dt', 'ftr'): continue
                for para in el.iter(q('a:p')):
                    t = ''.join(r.text or '' for r in para.iter(q('a:t'))).strip()
                    if not t: continue
                    pPr = para.find(q('a:pPr')); lvl = int(pPr.get('lvl', 0)) if pPr is not None else 0
                    body_ph = ph is not None and not is_title and ph.get('type') in (None, 'body', 'obj')          # 正文占位框：项目符号从母版继承
                    bullet = (pPr is None or pPr.find(q('a:buNone')) is None) and (body_ph or (pPr is not None and (pPr.find(q('a:buChar')) is not None or pPr.find(q('a:buAutoNum')) is not None)))
                    lines.append(('# ' if is_title else '  ' * lvl + ('- ' if bullet or lvl else '')) + t)
            elif el.tag == q('a:tbl'):
                for tr in el.iter(q('a:tr')):
                    cells = [' '.join((t.text or '').strip() for t in tc.iter(q('a:t'))).strip() for tc in tr.iter(q('a:tc'))]
                    if any(cells): lines.append('| ' + ' | '.join(cells) + ' |')
            elif el.tag == q('a:blip') and el.get(RID) in rl:
                tgt = rl[el.get(RID)][0]
                if tgt and tgt in z.namelist(): imgs.append((tgt, None))
        for pic in x.iter(q('p:pic')):                                           # 图片在页面上的占比（判断主图还是小图标）
            b = pic.find('.//' + q('a:blip')); ext = pic.find('.//' + q('a:ext'))
            if b is not None and ext is not None and b.get(RID) in rl:
                frac = int(ext.get('cx', 0)) * int(ext.get('cy', 0)) / (SW * SH)
                imgs = [(t, frac if t == rl[b.get(RID)][0] and f is None else f) for t, f in imgs]
        notes = ''
        for rid, (tgt, typ) in rl.items():
            if typ.endswith('/notesSlide') and tgt in z.namelist():
                nx = ET.fromstring(z.read(tgt)); ps = []
                for sp in nx.iter(q('p:sp')):
                    ph = sp.find('.//' + q('p:ph'))
                    if ph is not None and ph.get('type') in ('sldImg', 'sldNum', 'hdr', 'ftr', 'dt'): continue
                    ps += [''.join(r.text or '' for r in pp.iter(q('a:t'))).strip() for pp in sp.iter(q('a:p'))]
                notes = '\n'.join(p for p in ps if p)
        pages.append(dict(n=i, lines=lines, imgs=[(t, f, z.read(t)) for t, f in dict.fromkeys(imgs)], notes=notes))
    return pages, 's'

# ------------------------------------------------------------------ DOCX
def from_docx(path):
    z = zipfile.ZipFile(path); x = ET.fromstring(z.read('word/document.xml')); rl = rels(z, 'word/document.xml')
    body = x.find(q('w:body')); lines = []; marks = []; k = 0
    for el in body:
        if el.tag == q('w:p'):
            st = el.find('.//' + q('w:pStyle')); st = (st.get(q('w:val')) if st is not None else '') or ''
            t = ''.join(r.text or '' for r in el.iter(q('w:t'))).strip()
            lv = next((int(c) for c in st if c.isdigit()), 1) if re.match(r'(?i)heading|标题|title', st) else 0
            if t: lines.append(('#' * min(lv, 3) + ' ' if lv else '- ' if el.find('.//' + q('w:numPr')) is not None else '') + t); k += 1
            for b in el.iter(q('a:blip')):
                tgt = rl.get(b.get(RID), (None, ''))[0]
                if tgt and tgt in z.namelist(): marks.append((max(0, len(lines) - 1), tgt))   # 归到图片前面那一行所在的节
        elif el.tag == q('w:tbl'):
            for tr in el.iter(q('w:tr')):
                cells = [' '.join((t.text or '').strip() for t in tc.iter(q('w:t'))).strip() for tc in tr.iter(q('w:tc'))]
                if any(cells): lines.append('| ' + ' | '.join(cells) + ' |')
            for b in el.iter(q('a:blip')):
                tgt = rl.get(b.get(RID), (None, ''))[0]
                if tgt and tgt in z.namelist(): marks.append((max(0, len(lines) - 1), tgt))   # 归到图片前面那一行所在的节
    # Word 没有“页”：按标题切成节，每节当一页；图片挂在它出现的位置所在的节
    pages = []; cur = dict(n=1, lines=[], imgs=[], notes='', at=0)
    heads = [i for i, l in enumerate(lines) if l.startswith('#')] or [0]
    bounds = sorted(set([0] + heads)) + [len(lines) + 1]
    for j in range(len(bounds) - 1):
        a, b = bounds[j], bounds[j + 1]
        im = [(t, None, z.read(t)) for (pos, t) in marks if a <= pos < b or (j == len(bounds) - 2 and pos >= a)]
        if lines[a:b] or im: pages.append(dict(n=len(pages) + 1, lines=lines[a:b], imgs=list({t: (t, f, d) for t, f, d in im}.values()), notes=''))
    return pages, 'd'

# ------------------------------------------------------------------ PDF
def from_pdf(path, tmp):
    for tool in ('pdftotext', 'pdfimages'):
        if not shutil.which(tool): sys.exit(f'需要 poppler 的 {tool}（mac：brew install poppler；Ubuntu：apt install poppler-utils）')
    n = int(re.search(r'Pages:\s+(\d+)', subprocess.run(['pdfinfo', path], capture_output=True, text=True).stdout).group(1)) if shutil.which('pdfinfo') else 0
    lst = subprocess.run(['pdfimages', '-list', path], capture_output=True, text=True).stdout.splitlines()[2:]
    os.makedirs(tmp, exist_ok=True); subprocess.run(['pdfimages', '-all', '-p', path, os.path.join(tmp, 'im')], check=True)
    info = [l.split() for l in lst if l.strip()]
    byn = {}
    for f in os.listdir(tmp):                                                    # 文件名 im-页-编号.扩展名 → 编号
        m = re.match(r'im-(\d+)-(\d+)\.', f)
        if m: byn[int(m.group(2))] = f
    byp = {}
    for i, row in enumerate(info):
        if len(row) < 12 or row[2] != 'image' or int(row[1]) not in byn: continue
        f = byn[int(row[1])]; data = open(os.path.join(tmp, f), 'rb').read()
        nxt = info[i + 1] if i + 1 < len(info) else None
        if nxt and len(nxt) > 10 and nxt[2] == 'smask' and nxt[10] == row[10] and int(nxt[1]) in byn:   # 透明通道紧跟在图片后面、对象编号相同
            try:
                im = Image.open(io.BytesIO(data)).convert('RGB'); al = Image.open(os.path.join(tmp, byn[int(nxt[1])])).convert('L')
                if al.size != im.size: al = al.resize(im.size, Image.LANCZOS)
                im.putalpha(al); b = io.BytesIO(); im.save(b, 'PNG'); data = b.getvalue(); f = os.path.splitext(f)[0] + '.png'
            except Exception: pass
        byp.setdefault(int(row[0]), []).append((f, None, data))
    n = n or max(byp or [1])
    pages = []
    for i in range(1, n + 1):
        t = subprocess.run(['pdftotext', '-f', str(i), '-l', str(i), '-enc', 'UTF-8', path, '-'], capture_output=True, text=True).stdout
        lines = []
        for l in (x.strip() for x in t.splitlines()):
            if not l: continue
            l = re.sub(r'^[•●▪◦‣·▶■□\-–]\s*', '- ', l)
            prev = lines[-1] if lines else ''
            if prev and not l.startswith('- ') and not is_pageno(l) and len(prev.lstrip('- ')) >= 14 and not re.search(r'[。！？：:；;.!?」”）)]$', prev):
                lines[-1] = prev + ('' if re.search(r'[一-鿿]$', prev) and re.match(r'[一-鿿]', l) else ' ') + l   # 版面断行 → 接回一行
            else: lines.append(l)
        pages.append(dict(n=i, lines=lines, imgs=byp.get(i, []), notes=''))
    return pages, 'p'

# ------------------------------------------------------------------ 图片分析
def load(data, name):
    try: im = Image.open(io.BytesIO(data)); im.load(); return im
    except Exception:
        if name.lower().endswith(('.emf', '.wmf', '.svg')) and (shutil.which('soffice') or shutil.which('libreoffice')):
            with tempfile.TemporaryDirectory(prefix='hb-extract-') as d:   # 不落固定名目录：并发/异常退出也不会误建误删
                src = os.path.join(d, os.path.basename(name)); open(src, 'wb').write(data)
                subprocess.run([shutil.which('soffice') or shutil.which('libreoffice'), '--headless', '--convert-to', 'png', '--outdir', d, src], capture_output=True)
                png = os.path.splitext(src)[0] + '.png'
                if os.path.exists(png): im = Image.open(png); im.load(); return im
        return None

def kind(im):
    """照片 / 图形（截图、图表、插画、logo）。图形不能当满版照片用，只能放进 figure 插图块。"""
    a = im.convert('RGBA'); al = np.asarray(a)[..., 3]
    if (al < 250).mean() > .04: return 'graphic'                                # 有透明区域：抠图、logo、图标
    t = np.asarray(im.convert('RGB').resize((96, 96))) // 16
    c = np.bincount((t[..., 0].astype(int) * 256 + t[..., 1] * 16 + t[..., 2]).ravel(), minlength=4096)
    top8 = np.sort(c)[-8:].sum() / c.sum(); uniq = (c > 0).sum()
    return 'graphic' if top8 > .5 or uniq < 70 else 'photo'

def is_background(im):
    """弥散渐变、纯色光晕这类“只有颜色没有内容”的背景图：风格底图会替代它们，不当内容图用。"""
    g = np.asarray(im.convert('L').resize((128, 128), Image.BILINEAR), np.float32)
    detail = (np.abs(np.diff(g, axis=0)).mean() + np.abs(np.diff(g, axis=1)).mean()) / 2
    return detail < 1.2 and min(im.size) >= 400

def advice(w, h, k, frac):
    """按 A4 估算印出来的清晰度：≥150dpi 印刷清楚；96–150 屏幕看没问题、印刷偏软；<96 满版会糊。"""
    page = 96 * min(w / 796, h / 1125); spread = 96 * min(w / 1592, h / 1125); fig = 96 * w / 682
    if k == 'graphic': return '插图 figure（fit: contain）' if fig >= 96 else '小插图（figure 放半栏或更窄）'
    if w >= 1.3 * h and spread >= 150: return '跨页满版 ✓'
    if page >= 150: return '单页满版 ✓' + ('；跨页电子版可用' if w >= 1.3 * h and spread >= 96 else '')
    if page >= 96: return '单页满版：电子版 ✓、印刷偏软；或插图 figure'
    return '插图 figure / 图组 gallery（满版会糊）'

def ahash(im):
    g = np.asarray(im.convert('L').resize((12, 12), Image.BILINEAR), np.float32); return tuple((g > g.mean()).ravel())

def main(src, P, images_only=False):
    P = os.path.abspath(P); ph = os.path.join(P, 'photos'); assets = os.path.join(ph, '_assets'); os.makedirs(assets, exist_ok=True)
    ext = src.lower().rsplit('.', 1)[-1]
    if ext == 'pptx': pages, pre = from_pptx(src)
    elif ext == 'docx': pages, pre = from_docx(src)
    elif ext == 'pdf': pages, pre = from_pdf(src, os.path.join(P, '.extract_tmp'))
    else: sys.exit('支持 .pptx / .docx / .pdf（.ppt/.doc 先另存为新格式，或 soffice --headless --convert-to pptx 文件）')
    seen = {}; hashes = {}; count = {}
    for pg in pages:                                                             # 统计每张图出现在几页（logo、装饰会反复出现）
        for t, f, d in pg['imgs']: count.setdefault(hashlib.md5(d).hexdigest(), set()).add(pg['n'])
    rows = []; md = []; notes = []; arts = []
    for pg in pages:
        names = []; k_ = 0
        keep = []
        for l in pg['lines']:   # 页码 artifacts（页脚页码、居中短数字）不当正文：记下来，原文核对不要求它们出现
            if is_pageno(l): arts.append((pg['n'], l.strip()))
            else: keep.append(l)
        pg['lines'] = keep
        for t, frac, data in pg['imgs']:
            h5 = hashlib.md5(data).hexdigest()
            if h5 in seen: names.append(seen[h5]); continue
            im = load(data, t)
            if im is None: rows.append((t, pg['n'], '—', '无法读取', '', '格式不支持，需要的话手工另存为 PNG')); continue
            w, h = im.size; k_ += 1; kd = kind(im)
            rep = len(count[h5]) >= 3 and len(count[h5]) >= .3 * len(pages)
            bg = im.mode not in ('RGBA', 'LA') and is_background(im)
            tiny = min(w, h) < 160 or (frac is not None and frac < .015)
            ah = ahash(im)
            if ah in hashes and not rep: seen[h5] = hashes[ah]; names.append(hashes[ah]); continue   # 近似重复（同图不同压缩）
            fmt = 'png' if im.mode in ('RGBA', 'LA', 'P') else 'jpg'   # 透明抠图一律保留 PNG
            name = f'{pre}{pg["n"]:02d}_{k_}.{fmt}' if pre != 'd' else f'd{pg["n"]:02d}_{k_}.{fmt}'
            sub = '_assets/' if rep or tiny or bg else ''
            out = os.path.join(ph, sub + name)
            if fmt == 'jpg': im.convert('RGB').save(out, quality=94)
            else: im.save(out)
            seen[h5] = sub + name; hashes[ah] = sub + name; names.append(sub + name)
            why = '重复出现（logo / 装饰）' if rep else '太小（图标）' if tiny else '弥散/纯色背景（风格底图会替代）' if bg else ''
            rows.append((sub + name, pg['n'], f'{w}×{h}', '照片' if kd == 'photo' else '图形', f'{frac * 100:.0f}%' if frac is not None else '', why or advice(w, h, kd, frac)))
        use = [x for x in dict.fromkeys(names) if not x.startswith('_assets/')]
        kinds = {r[0]: r[3] for r in rows}
        pho = [x for x in use if kinds.get(x) == '照片']; gra = [x for x in use if kinds.get(x) == '图形']
        md.append(f'<!-- 第 {pg["n"]} {"页" if pre != "d" else "节"}' + (f' · 照片：{"、".join(pho)}' if pho else '') + (f' · 图形：{"、".join(gra)}' if gra else '') + ' -->')
        md += pg['lines'] + ['']
        if pg['notes']: notes += [f'## 第 {pg["n"]} 页', pg['notes'], '']
    if not images_only: open(os.path.join(P, 'doc.md'), 'w', encoding='utf-8').write('\n'.join(md))
    qa = os.path.join(P, '.qa'); os.makedirs(qa, exist_ok=True)   # 页码 artifacts：从必含文本排除的依据（check_copy.py 读）
    open(os.path.join(qa, 'artifacts.txt'), 'w', encoding='utf-8').write(
        '# 页码 artifacts（extract.py 识别：页脚页码、居中短数字；不是正文，check_copy 原文核对不要求出现）\n' + ''.join(f'第 {n} 页：{t}\n' for n, t in arts))
    if notes: open(os.path.join(P, 'notes.md'), 'w', encoding='utf-8').write('# 演讲者备注（不是正文；需要时取用，取用的句子要写进 doc.md 才会被原文核对覆盖）\n\n' + '\n'.join(notes))
    tbl = ['| 文件 | 出处 | 尺寸 | 类型 | 原页面占比 | 建议用法 |', '|---|---|---|---|---|---|'] + [f'| {a} | 第 {b} 页 | {c} | {d} | {e} | {f} |' for a, b, c, d, e, f in rows]
    open(os.path.join(P, 'images.md'), 'w', encoding='utf-8').write(
        '# 图片清单（extract.py 生成）\n\n照片：按“建议用法”放进版式的 image；图形（截图、图表、插画）只放进 figure 插图块，不做满版。\n'
        '尺寸按 A4 估算：单页满版 ≥ 1600px 宽较稳，跨页 ≥ 3000px；低于这个印出来会发软。\n\n' + '\n'.join(tbl) + '\n')
    contact(ph, rows, os.path.join(ph, '_contact.jpg'))
    shutil.rmtree(os.path.join(P, '.extract_tmp'), ignore_errors=True)
    n_use = sum(1 for r in rows if not r[0].startswith('_assets/') and r[2] != '—')
    print(f'{len(pages)} 页 → doc.md；图片 {n_use} 张可用（photos/），{sum(1 for r in rows if r[0].startswith("_assets/"))} 张 logo/装饰/图标（photos/_assets/）')
    if arts: print(f'页码 artifacts {len(arts)} 处（页脚页码不当正文，已排除出原文核对）→ .qa/artifacts.txt')
    print(f'先看 photos/_contact.jpg 和 images.md，再排版。' + (' 演讲者备注在 notes.md。' if notes else ''))

def contact(ph, rows, out):
    items = [r for r in rows if r[2] != '—']
    if not items: return
    C, TW, TH = 4, 300, 230; im = Image.new('RGB', (C * TW + 20, ((len(items) + C - 1) // C) * (TH + 54) + 20), (236, 236, 236)); d = ImageDraw.Draw(im)
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import fonts as F
        fp = F.path_of('lxgw-neo-xihei') or F.path_of('noto-sans-sc'); font = ImageFont.truetype(fp, 15) if fp else ImageFont.load_default()
    except Exception: font = ImageFont.load_default()
    for i, (name, pgn, size, kd, frac, adv) in enumerate(items):
        x, y = 10 + (i % C) * TW, 10 + (i // C) * (TH + 54)
        try:
            t = Image.open(os.path.join(ph, name)).convert('RGBA'); bg = Image.new('RGBA', t.size, (255, 255, 255, 255)); bg.alpha_composite(t); t = bg.convert('RGB'); t.thumbnail((TW - 12, TH - 12))
            im.paste(t, (x + (TW - t.width) // 2, y + (TH - t.height) // 2))
        except Exception: pass
        col = (30, 30, 30) if not name.startswith('_assets/') else (150, 150, 150)
        d.text((x + 6, y + TH + 2), f'{name}  {size}  {kd}', fill=col, font=font)
        d.text((x + 6, y + TH + 22), adv[:22], fill=(110, 110, 110), font=font)
    im.save(out, quality=88)

if __name__ == '__main__':
    a = [x for x in sys.argv[1:] if not x.startswith('--')]
    if len(a) < 2: sys.exit(__doc__)
    main(a[0], a[1], images_only='--images-only' in sys.argv)   # --images-only：只抽图片（原文已由 doc2yaml 转好时用）
