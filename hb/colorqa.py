#!/usr/bin/env python3
"""用色比例检查（只提示，不拦截）：python3 colorqa.py <project>
按截图量每页、整本的颜色构成：浅底（纸色、次级背景）/ 主色整块 / 强调色 / 深色（星云、照片暗部、深墨块）/ 其他（照片、插画）。
参照 60-30-10：浅底为主、主色做辅助、强调色点到为止。主色整块太多 → [颜色过重]，并列出是哪几页。阈值按用色档位：
  clash 撞色：主色 + 强调色整块合计 ≤ 60%，连续 3 页以上整页色块要提示
  accent 点缀：主色整块 ≤ 20%，强调色 ≤ 15%；超过的页列出来
结果写 .qa/color.json。"""
import sys, os, glob, json
import numpy as np
from PIL import Image
P = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else '.')
Q = os.path.join(P, '.qa')
pgs = sorted(glob.glob(os.path.join(Q, 'pg*.png')), key=lambda f: int(os.path.basename(f)[2:-4]))
ai = os.path.join(Q, 'ai_slots.json')
if not pgs or not os.path.exists(ai): sys.exit(0)
C = json.load(open(ai)).get('colors', {})
mode = json.load(open(os.path.join(P, 'map.json'))).get('color_mode', 'clash') if os.path.exists(os.path.join(P, 'map.json')) else 'clash'
hx = lambda h: np.array([int(h.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4)], np.float32)
A, B = hx(C.get('A', C.get('G', '#000000'))), hx(C.get('B', C.get('GOLD', '#FFFFFF')))
rows = []
for f in pgs:
    im = np.asarray(Image.open(f).convert('RGB').resize((80, 113)), np.float32)
    px = im.reshape(-1, 3); mx, mn = px.max(1), px.min(1); v = mx / 255; s = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1), 0)
    dA = np.linalg.norm(px - A, axis=1); dB = np.linalg.norm(px - B, axis=1)
    light = (v > .86) & (s < .16)
    a = (dA < 42) & ~light; b = (dB < 42) & ~light & ~a
    dark = (v < .3) & ~a & ~b
    other = ~(light | a | b | dark)
    rows.append({k: round(float(x.mean()), 3) for k, x in dict(light=light, primary=a, accent=b, dark=dark, other=other).items()})
tot = {k: round(float(np.mean([r[k] for r in rows])), 3) for k in rows[0]}
lim = dict(clash=dict(field=.60, page=.55), accent=dict(field=.20, page=.45), mono=dict(field=.20, page=.45))[mode if mode in ('clash', 'accent', 'mono') else 'clash']
field = tot['primary'] + (tot['accent'] if mode == 'clash' else 0)
heavy = [i + 1 for i, r in enumerate(rows) if r['primary'] + (r['accent'] if mode == 'clash' else 0) > lim['page']]
runs, cur = [], []
for pnum in heavy:
    cur = cur + [pnum] if cur and pnum == cur[-1] + 1 else [pnum]
    if len(cur) == 3: runs.append(cur[:])
out = []
line = f'用色比例（{mode}）：浅底 {tot["light"] * 100:.0f}% · 主色块 {tot["primary"] * 100:.0f}% · 强调色 {tot["accent"] * 100:.0f}% · 深色 {tot["dark"] * 100:.0f}% · 照片 / 插画 / 其他 {tot["other"] * 100:.0f}%'
if field > lim['field']:
    out.append(f'[颜色过重] 整本 {"主色 + 强调色" if mode == "clash" else "主色"}整块约占 {field * 100:.0f}%（{mode} 档建议 ≤ {lim["field"] * 100:.0f}%），整页色块在第 {"、".join(map(str, heavy[:12]))} 页 → '
               + ('几页写 surface: paper；或换 color_mode: accent' if mode == 'clash' else '这些页写 surface: paper，或换成图 / 纸色多的版式'))
if mode != 'clash' and tot['accent'] > .15: out.append(f'[颜色过重] 强调色约占 {tot["accent"] * 100:.0f}%（点缀档 ≤ 15%）：强调色只上数字、细线、标签')
for r in runs: out.append(f'[颜色过重] 第 {r[0]}–{r[-1]} 页连续整页色块 → 中间换一页纸色（surface: paper）')
json.dump(dict(mode=mode, total=tot, pages=rows, heavy=heavy, warn=out), open(os.path.join(Q, 'color.json'), 'w'), ensure_ascii=False)
print(line)
for o in out: print(o)
