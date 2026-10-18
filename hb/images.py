#!/usr/bin/env python3
"""图片清单：python3 images.py <project>  → <project>/images.yaml（run.sh 每次构建后自动更新）
自动填：用在第几页、原图像素、印出来约多少 dpi、是否做了双色调。你填：source（来源）、license（授权）、credit（署名）——重跑不会覆盖。
同时提示：同一张图用了两次、低于 150dpi、photos/ 里没用上的图、没写来源的第三方图。"""
import sys, os, json, yaml
P = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else '.')
m = os.path.join(P, 'map.json')
if not os.path.exists(m): sys.exit(0)
use = json.load(open(m)).get('use') or []
f = os.path.join(P, 'images.yaml'); old = (yaml.safe_load(open(f, encoding='utf-8')) or {}).get('images', {}) if os.path.exists(f) else {}
spec = yaml.safe_load(open(os.path.join(P, 'book.yaml'), encoding='utf-8')) or {}
ph = (spec.get('book') or {}).get('photos', 'photos'); ph = ph if isinstance(ph, str) else 'photos'
from PIL import Image
out = {}
for u in use:
    k = u['file']; e = out.setdefault(k, dict(pages=[], dpi=None))
    if u['page'] not in e['pages']: e['pages'].append(u['page'])
    if u.get('dpi'): e['dpi'] = min(e['dpi'] or 9999, u['dpi'])
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
