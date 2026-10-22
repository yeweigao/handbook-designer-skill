#!/usr/bin/env python3
"""数字出处检查：python3 facts.py <project>
book.yaml 里出现的每个数字（日期、价格、人数、百分比……）都要能在原文 doc*.md 或调研记录 facts.md 里找到。
找不到的列成 [无出处数字]——可能是写错、记错，或者是你自己补的（不允许）。只提示，不拦截；结果写到 .qa/facts.txt。
facts.md（选题调研时用，见 workflows/research.md）每条一行：- 事实原句 —— 来源标题 网址（访问日期）"""
import sys, os, re, glob, yaml
P = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else '.')
spec = yaml.safe_load(open(os.path.join(P, 'book.yaml'), encoding='utf-8')) or {}
up = os.path.dirname(P)
srcs = glob.glob(os.path.join(P, 'doc*.md')) + glob.glob(os.path.join(P, 'facts*.md')) + glob.glob(os.path.join(up, 'doc*.md')) + glob.glob(os.path.join(up, 'facts*.md'))
if not srcs: print('（没有 doc.md / facts.md，跳过数字出处检查）'); sys.exit(0)
ref = re.sub(r'[,，\s]', '', ' '.join(open(f, encoding='utf-8').read() for f in srcs))
SKIP = {'display_weight', 'bleed', 'typography', 'layout', 'image', 'images', 'img', 'src', 'focus', 'target', 'zoom', 'surface', 'mirror', 'variant', 'style', 'cols', 'count', 'deco', 'num', 'tone',
        'index', 'toc', 'note', 'job', 'size', 'h', 'w', 'mt', 'spacing', 'lh', 'widths', 'columns', 'colors', 'fonts', 'scale', 'paper', 'pages', 'canvas', 'stroke', 'items_cols',
        'split', 'strip', 'body_top', 'top_y', 'bottom_y', 'kw', 'brand_graphic',
        'fill', 'space', 'lines', 'photo_rows'}   # fill/space/lines：块的行数（排版）；photo_rows：T 版照片带行数（排版）
nums = {}
def walk(o, path):
    if isinstance(o, dict): [walk(v, f'{path}.{k}') for k, v in o.items() if k not in SKIP and not (path.endswith('.series_header') and k in ('series', 'item'))]
    elif isinstance(o, list): [walk(v, f'{path}[{i}]') for i, v in enumerate(o)]
    elif isinstance(o, (int, float)) and not isinstance(o, bool): nums.setdefault(str(o), path)
    elif isinstance(o, str):
        for m in re.finditer(r'\d[\d,，.:：/%-]*\d|\d', o):
            t = m.group(0)
            if len(re.sub(r'\D', '', t)) >= 2 or re.search(r'%|万|千|亿', o[m.end():m.end() + 1]): nums.setdefault(t, path)
walk(spec.get('pages') or [], 'pages'); walk({k: v for k, v in (spec.get('book') or {}).items() if k in ('title', 'subtitle', 'folio', 'series')}, 'book')
miss = [(t, p) for t, p in nums.items() if re.sub(r'[,，\s]', '', t) not in ref and re.sub(r'[,，\s]', '', t).replace('：', ':') not in ref.replace('：', ':')]
out = [f'[无出处数字] {t}（{p}）→ 原文和 facts.md 里都没有：核对是不是写错了；调研来的数字记进 facts.md 并写明来源' for t, p in miss]
os.makedirs(os.path.join(P, '.qa'), exist_ok=True); open(os.path.join(P, '.qa', 'facts.txt'), 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print(f'数字出处：{len(nums)} 个数字，{len(miss)} 个在原文 / facts.md 里找不到' if miss else f'数字出处：{len(nums)} 个数字都能在原文 / facts.md 里找到 ✓')
for o in out[:12]: print('  ' + o)
