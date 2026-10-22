#!/usr/bin/env python3
"""沿用旧册：python3 reuse.py <旧项目> <新项目>（new_project.sh --from 调用）
- 新 book.yaml = 旧的 book: 设置 + 旧的页序骨架：版式、job、surface、mirror 等保留；文字换成 TODO；照片文件名保留（旧照片复制过来）
- 旧 book.yaml → 新项目的 book.prev.yaml（对照）；旧 brief.md → 新 brief.md（route: reuse，改动记录加一行）"""
import sys, os, re, shutil, time, yaml
OLD, NEW = map(os.path.abspath, sys.argv[1:3]); os.makedirs(NEW, exist_ok=True)
spec = yaml.safe_load(open(os.path.join(OLD, 'book.yaml'), encoding='utf-8')) or {}
shutil.copy(os.path.join(OLD, 'book.yaml'), os.path.join(NEW, 'book.prev.yaml'))
KEEP = {'layout', 'job', 'surface', 'mirror', 'variant', 'style', 'cols', 'count', 'deco', 'num', 'tone', 'focus', 'zoom', 'target', 'align',
        'image', 'images', 'img', 'src', 'duo', 'index', 'toc', 'folio', 'logo', 'contact', 'rhythm', 'columns', 'items_cols', 'widths', 'fit', 'h', 'w', 'mt', 'size'}
IMG = re.compile(r'\.(jpe?g|png|webp|svg|gif)$', re.I)
photos = set()
def blank(o, key=None):
    if isinstance(o, dict):
        return {k: (v if k in KEEP and not isinstance(v, (dict, list)) else blank(v, k) if k not in ('image', 'images', 'img') else note_img(v)) for k, v in o.items()}
    if isinstance(o, list): return [blank(v, key) for v in o]
    if isinstance(o, str):
        if IMG.search(o): photos.add(o); return o
        return 'TODO' if o.strip() else o
    return o
def note_img(v):
    def walk(x):
        if isinstance(x, str) and IMG.search(x): photos.add(x)
        elif isinstance(x, dict): [walk(y) for y in x.values()]
        elif isinstance(x, list): [walk(y) for y in x]
    walk(v); return v
pages = []
for p in spec.get('pages') or []:
    q = blank(p)
    if 'note' in p: q['note'] = f'〔沿用〕{p["note"] if isinstance(p["note"], str) else ""}'
    pages.append(q)
book = dict(spec.get('book') or {})
for k in ('title', 'folio', 'subtitle'):
    if k in book and not isinstance(book[k], (int, float)): book[k] = 'TODO'
yaml.safe_dump(dict(book=book, pages=pages), open(os.path.join(NEW, 'book.yaml'), 'w', encoding='utf-8'), allow_unicode=True, sort_keys=False, width=1000)
ph = book.get('photos', 'photos') if isinstance(book.get('photos', 'photos'), str) else 'photos'
os.makedirs(os.path.join(NEW, ph), exist_ok=True); n = 0
for f in photos:
    s, d = os.path.join(OLD, ph, f), os.path.join(NEW, ph, f)
    if os.path.exists(s) and not os.path.exists(d): os.makedirs(os.path.dirname(d), exist_ok=True); shutil.copy(s, d); n += 1
b = os.path.join(OLD, 'brief.md')
if os.path.exists(b):
    t = open(b, encoding='utf-8').read()
    t = re.sub(r'(?m)^route:.*$', 'route: reuse', t, count=1)
    t = t.rstrip() + f'\n- {time.strftime("%Y-%m-%d")} 沿用 {os.path.basename(OLD)} 的外观和页序，换新内容（新内容的沟通合同要重新和用户确认）\n'
    open(os.path.join(NEW, 'brief.md'), 'w', encoding='utf-8').write(t)
print(f'沿用旧册：{len(pages)} 个页面骨架（文字已换成 TODO），复制旧照片 {n} 张；旧 book.yaml → book.prev.yaml' + ('；brief.md 已复制（route: reuse）' if os.path.exists(b) else ''))
