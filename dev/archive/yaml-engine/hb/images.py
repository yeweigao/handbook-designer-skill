#!/usr/bin/env python3
"""图片清单：python3 images.py <project>  → <project>/images.yaml（run.sh 每次构建后自动更新）
自动填：用在第几页、原图像素、印出来约多少 dpi、是否做了双色调。你填：source（来源）、license（授权）、credit（署名）——重跑不会覆盖。
同时提示：同一张图用了两次、低于 150dpi、photos/ 里没用上的图、没写来源的第三方图。
dpi 按实际渲染框算（F11）：解析 book.html 里每个图片的真实显示盒——figure 按 object-fit contain/cover 的可见区、
logo/卡片图按固定高度的实际显示尺寸、侧条/开窗按容器盒的裁切，而不是按容器宽估算（封底二维码 256px 显示 84×84 约 293dpi，
按宽容器会误报成 47dpi）。整页烘焙底图仍用 map.json 的估算值（hb.py 已按 box+zoom 算过）；解析不到显示盒时同样回退。"""
import sys, os, json, yaml, re
from html.parser import HTMLParser
P = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else '.')
m = os.path.join(P, 'map.json')
if not os.path.exists(m): sys.exit(0)
use = json.load(open(m, encoding='utf-8')).get('use') or []
f = os.path.join(P, 'images.yaml'); old = (yaml.safe_load(open(f, encoding='utf-8')) or {}).get('images', {}) if os.path.exists(f) else {}
spec = yaml.safe_load(open(os.path.join(P, 'book.yaml'), encoding='utf-8')) or {}
ph = (spec.get('book') or {}).get('photos', 'photos'); ph = ph if isinstance(ph, str) else 'photos'
from PIL import Image

# ---------------------------------------------------------------- F11：实际渲染盒（book.html → 显示尺寸）
class _ImgScan(HTMLParser):
    """扫 book.html：收集每个 img/ 图片的自身样式 + 祖先链（最近带内联宽高的容器 + 所在页）。"""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []; self.found = []
    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag == 'img' and str(d.get('src', '')).startswith('img/'):
            self.found.append((d['src'][4:], d.get('class', ''), d.get('style', ''), list(self.stack)))
        if tag not in ('img', 'br', 'meta', 'link', 'input', 'hr', 'source'):
            self.stack.append((tag, d))
    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]; break

def _px(style, prop):
    mm = re.search(prop + r':\s*([\d.]+)px', style or '')
    return float(mm.group(1)) if mm else None

def _dpi(iw, ih, dw, dh, fit):
    """源像素 (iw,ih) 显示在 (dw,dh) css px 里、按 fit 裁切后的有效印刷 dpi（1 css px = 1/96 英寸）。"""
    s = (min(dw / iw, dh / ih) if fit == 'contain' else max(dw / iw, dh / ih)) if iw and ih else 0
    return 96 / s if s > 0 else None

def _cells(gtc):
    """grid-template-columns → [(定宽px 或 None, fr 权重)]；展开 repeat(n, X)，minmax(0,1fr) 按 1fr 算。"""
    toks = []
    for m in re.finditer(r'repeat\(\s*(\d+)\s*,([^)]+)\)', gtc or ''):
        toks += m.group(2).split() * int(m.group(1))
    toks += [t for t in re.sub(r'repeat\([^)]*\)', '', gtc or '').split() if t]
    out = []
    for t in toks:
        mm = re.search(r'([\d.]+)\s*fr', t)
        if mm: out.append((None, float(mm.group(1))))
        elif t.endswith('px'): out.append((float(t[:-2]), 0))
        else: out.append((None, 0))
    return out

def render_boxes(html):
    """{图片文件名: [(页码, 显示宽, 显示高, object-fit)]}；整页烘焙底图（class=a）不收——它由 hb.py 按 box+zoom 估算。
    显示盒取自内联样式：自身宽高 → 最近祖先容器的宽高（grid 单元格按 grid-template-columns 折算）；
    容器高带 data-y0/data-y1（让位盒，内联高只是占位、真实高度由 fill.js 锚点算）时不收，回退 map.json 估算。"""
    gut = float((re.search(r'--gut:\s*([\d.]+)px', html) or [0, 32])[1])
    out = {}
    try:
        s = _ImgScan(); s.feed(html)
    except Exception:
        return out
    for name, cls, style, anc in s.found:
        if 'a' in cls.split(): continue   # 整页底图（IMGTAG）：烘焙合成图，DPI 语义不同
        pg = next((int(a['data-n']) for t, a in reversed(anc) if 'page' in (a.get('class') or '').split() and a.get('data-n')), None)
        ow, oh = _px(style, 'width'), _px(style, 'height')
        fit = (re.search(r'object-fit:\s*(\w+)', style or '') or [None, ''])[1]
        cw = ch = None; gtc = gappx = None; dyn = False; cw_at = gtc_at = -1
        for i, (t, a) in enumerate(reversed(anc)):   # 最近的内联宽/高容器（文字栈 / .cn-figi / .cn-pic / .cn-cardi / grid）
            st = a.get('style') or ''
            if cw is None:
                w = _px(st, 'width')
                if w is not None: cw, cw_at = w, i
            if ch is None:
                h = _px(st, 'height')
                if h is not None:
                    if a.get('data-y0') is not None or a.get('data-y1') is not None: dyn = True   # 让位盒：高由锚点算
                    else: ch = h
            if gtc is None:
                columns = re.search(r'(?:^|;)\s*grid-template-columns\s*:\s*([^;]+)', st)
                if columns: gtc, gtc_at, gappx = columns.group(1), i, _px(st, 'column-gap')
            if cw is not None and ch is not None and gtc is not None: break
        if gtc is not None and cw is not None and gtc_at < cw_at:   # grid 在宽容器内侧 → 宽按单元格折算
            cells = _cells(gtc)
            if cells and all(px for px, w in cells): cw = min(px for px, w in cells)
            elif cells and all(w > 0 for px, w in cells):
                gap = gappx if gappx is not None else gut
                cw = (cw - (len(cells) - 1) * gap) * min(w for px, w in cells) / sum(w for px, w in cells)
        if dyn: continue   # 高度是运行时锚点算出来的：静态值不可信，回退 map.json
        out.setdefault(name, []).append((pg, ow, oh, cw, ch, fit, any('cn-cardi' in (a.get('class') or '') for t, a in anc)))
    return out

_sz = {}
def _size(name):
    if name not in _sz:
        try: _sz[name] = Image.open(os.path.join(P, 'img', name)).size
        except Exception: _sz[name] = None
    return _sz[name]

boxes = {}
bh = os.path.join(P, 'book.html')
if os.path.exists(bh):
    boxes = render_boxes(open(bh, encoding='utf-8').read())

out = {}
for u in use:
    k = u['file']; e = out.setdefault(k, dict(pages=[], dpi=None))
    if u['page'] not in e['pages']: e['pages'].append(u['page'])
    d = u.get('dpi'); nm = u.get('img')
    for pg, ow, oh, cw, ch, fit, cardi in boxes.get(nm, ()):   # 同一张图用多次：按当次显示盒重算，取最差
        if pg is not None and pg != u['page']: continue
        sz = _size(nm)
        if not sz: continue
        iw, ih = sz
        if ow and oh: dw, dh, fit = ow, oh, 'exact'           # 自身定了宽高：拉伸铺满
        elif oh: dw, dh, fit = oh * iw / ih, oh, 'exact'      # 只定了高（logo、卡片图）：宽 = 高×原图宽高比
        elif ow: dw, dh, fit = ow, ow * ih / iw, 'exact'
        elif cw and ch:                                        # 容器盒（figure / product / pic / cardi）
            if cardi and not fit: dw, dh, fit = ch * iw / ih, ch, 'exact'   # 卡片图 CSS：高 100%、宽 auto
            else: dw, dh, fit = cw, ch, fit or 'cover'
        else: continue
        dd = _dpi(iw, ih, dw, dh, fit)
        if dd: d = round(dd)   # 有实际渲染盒就以它为准（map.json 的估算是按容器宽的，contain/logo 会误报）
    if d: e['dpi'] = min(e['dpi'] or 9999, d)
    if u.get('duo'): e['duotone'] = True
for k, e in out.items():
    p = os.path.join(P, ph, k)
    try: e['px'] = 'x'.join(map(str, Image.open(p).size)) if not k.lower().endswith('.svg') else 'svg'
    except Exception: e['px'] = '?'
    o = old.get(k) or {}
    for kk in ('source', 'license', 'credit'): e[kk] = o.get(kk, '')
    if k.startswith('ai_') and not e['source']: e['source'] = 'AI 生成'
unused = []
d = os.path.join(P, ph)
if os.path.isdir(d):
    unused = sorted(x for x in os.listdir(d) if x.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.svg')) and x not in out and not x.startswith('_'))
head = ('# 图片清单（run.sh 每次构建后自动更新 pages / px / dpi；source 来源、license 授权、credit 署名由你填，重跑不会覆盖）\n'
        '# 交付前：第三方照片都要写 source + license；dpi < 150 的印刷会糊\n')
yaml.safe_dump(dict(images=out, unused=unused), open(f, 'w', encoding='utf-8'), allow_unicode=True, sort_keys=False, width=200)
s = open(f, encoding='utf-8').read(); open(f, 'w', encoding='utf-8').write(head + s)
twice = {k: e['pages'] for k, e in out.items() if len(e['pages']) > 1 and not k.lower().endswith('.svg')}
low = {k: e['dpi'] for k, e in out.items() if e['dpi'] and e['dpi'] < 150}
print(f'图片清单：{len(out)} 张在用' + (f'，{len(unused)} 张没用上' if unused else '') + ' → images.yaml')
for k, v in twice.items(): print(f'  [同图两用] {k} 用在第 {"、".join(map(str, v))} 页 → 换一张（读者会觉得素材不够）')
for k, v in low.items(): print(f'  [低清] {k} 约 {v}dpi → 印刷会软：换原图或挪到小图位')
