"""品牌包（brands/<名字>/brand.yaml）：book.brand: allas → 默认配色、字体、页脚、logo、封底联系方式。
hb.py / lock.py 调用 apply(book)：品牌包里 book: 下的设置作为默认值，book.yaml 里写了的优先。"""
import os, re, yaml
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def index():
    f = os.path.join(ROOT, 'brands', 'index.yaml')
    return (yaml.safe_load(open(f, encoding='utf-8')) or {}) if os.path.exists(f) else {}
def load(name):
    n = str(name)
    if not re.fullmatch(r'[\w-]+', n):   # 防 ../ 逃逸：品牌名只允许字母数字下划线连字符
        raise SystemExit(f'ERROR: 品牌名不合法：{name}（只允许字母/数字/下划线/连字符）；已有：{", ".join(index()) or "无"}')
    d = os.path.join(ROOT, 'brands', n); f = os.path.join(d, 'brand.yaml')
    if not os.path.exists(f):
        raise SystemExit(f'ERROR: 找不到品牌包 {name}（brands/{name}/brand.yaml）。已有：{", ".join(index()) or "无"}；新建见 workflows/brand.md')
    b = yaml.safe_load(open(f, encoding='utf-8')) or {}; b['_dir'] = d; b['_name'] = str(name)
    return b
def kind_defaults(book):
    """book.kind（purposes/ 里的用途方法）：没写 purpose 时用它的 purpose"""
    k = (book or {}).get('kind')
    if not k: return book
    f = os.path.join(ROOT, 'purposes', f'{k}.yaml')
    if not os.path.exists(f):
        raise SystemExit(f'ERROR: 未知 book.kind {k}，可选 {", ".join(x[:-5] for x in sorted(os.listdir(os.path.join(ROOT, "purposes"))) if x.endswith(".yaml") and x != "index.yaml")}')
    if 'purpose' not in book: book = dict(book, purpose=(yaml.safe_load(open(f, encoding='utf-8')) or {}).get('purpose', 'brochure'))
    return book
def apply(book):
    """返回 (合并后的 book, 品牌包 dict 或 None)。顺序：品牌包默认 → book.yaml → 用途方法补 purpose"""
    name = (book or {}).get('brand')
    if not name: return kind_defaults(book or {}), None
    b = load(name); out = dict(b.get('book') or {})
    for k, v in (book or {}).items():
        if k == 'colors' and isinstance(v, dict) and isinstance(out.get('colors'), dict): out['colors'] = dict(out['colors'], **v)
        else: out[k] = v
    return kind_defaults(out), b
def logo_svg(b, color, dark=False):
    """内联 SVG（PDF 里是矢量）。mono：所有颜色换成 currentColor，跟着当页字色走。"""
    lg = (b or {}).get('logo') or {}
    f = lg.get('dark') if dark and lg.get('dark') else lg.get('file')
    if not f: return ''
    p = os.path.join(b['_dir'], f)
    if not os.path.exists(p): return ''
    s = open(p, encoding='utf-8').read()
    s = re.sub(r'<\?xml.*?\?>|<!--.*?-->', '', s, flags=re.S).strip()
    if lg.get('mono', True):
        s = re.sub(r'fill="(?!none)[^"]*"', 'fill="currentColor"', s); s = re.sub(r'stroke="(?!none)[^"]*"', 'stroke="currentColor"', s)
        s = re.sub(r'fill:\s*#[0-9a-fA-F]{3,8}', 'fill:currentColor', s)
    s = re.sub(r'<svg\b', '<svg style="height:100%;width:auto;display:block;overflow:visible"', s, count=1)
    s = re.sub(r'(<svg[^>]*?)\s(width|height)="[^"]*"', r'\1', s); s = re.sub(r'(<svg[^>]*?)\s(width|height)="[^"]*"', r'\1', s)
    return s
