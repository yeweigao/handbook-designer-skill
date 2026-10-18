#!/usr/bin/env python3
"""从一本书里取几页另建一个小项目（试排样张、方向对比都用它）。
  python3 subset.py <project> <out_dir> proof            # 封面 + 前两个跨页（第 1–5 页）
  python3 subset.py <project> <out_dir> 1,4-7            # 指定成品页码（跨页版式算两页）
  python3 subset.py <project> <out_dir> 1-3 style=swiss colors=hermes --lang zh   # 顺便改 book 里的设置、只取一种语言（方向样张）
源 yaml：<project>/book.yaml；没有时用 --src <文件>。照片 / AI 图目录链接回原项目；不带 doc.md（样张不做原文核对）。"""
import sys, os, yaml, re
args = sys.argv[1:]; SRC = None; LANG = None
if '--src' in args: i = args.index('--src'); SRC = args[i + 1]; del args[i:i + 2]
if '--lang' in args: i = args.index('--lang'); LANG = args[i + 1]; del args[i:i + 2]
if len(args) < 3: sys.exit(__doc__)
P, OUT, SPEC = os.path.abspath(args[0]), os.path.abspath(args[1]), args[2]
SRC = SRC or os.path.join(P, 'book.yaml')
spec = yaml.safe_load(open(SRC, encoding='utf-8')) or {}
if LANG:   # 只要一种语言（方向样张）
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from i18n_pick import pick
    spec = pick(spec, LANG); spec.setdefault('book', {})['lang'] = LANG; spec['book'].pop('langs', None)
SPAN2 = {'SPREAD_P', 'SPREAD_H', 'SPREAD_OPENER'}
def want_pages(s):
    if s == 'proof': return set(range(1, 6))
    out = set()
    for part in s.split(','):
        a, _, b = part.partition('-'); out |= set(range(int(a), int(b or a) + 1))
    return out
want = want_pages(SPEC); n = 1; keep = []
for p in spec.get('pages') or []:
    span = 2 if p.get('layout') in SPAN2 else 1
    if set(range(n, n + span)) & want: keep.append(p)
    n += span
book = dict(spec.get('book') or {})
for kv in args[3:]:
    k, _, v = kv.partition('=')
    book[k] = yaml.safe_load(v) if v else None
os.makedirs(OUT, exist_ok=True)
yaml.safe_dump(dict(book=book, pages=keep), open(os.path.join(OUT, 'book.yaml'), 'w', encoding='utf-8'), allow_unicode=True, sort_keys=False, width=1000)
base = os.path.dirname(os.path.abspath(SRC))
ph = book.get('photos', 'photos'); ph = ph if isinstance(ph, str) else 'photos'
for f in (ph, 'ai', 'brand'):
    s, d = (os.path.join(P, f) if os.path.isdir(os.path.join(P, f)) else os.path.join(base, f)), os.path.join(OUT, f)
    if os.path.isdir(s) and not os.path.lexists(d): os.symlink(s, d)
print(f'{OUT}/book.yaml：{len(keep)} 个页面（{SPEC}）')
