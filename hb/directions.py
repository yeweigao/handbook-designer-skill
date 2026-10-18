#!/usr/bin/env python3
"""方向样张（第 0 步第二轮）：同一份内容按 2–3 个方向各排一个封面 + 一个跨页，拼成一张对比图给用户选。
  python3 directions.py <project> "A=style:photo,colors:klein" "B=style:swiss,colors:hermes" "C=style:papercut,colors:china-red"
  可选：--title "书名" --sub "副题" --kicker "小标签"   （还没有 book.yaml 时，用模板的版式换上真实书名）
内容来源：<project>/book.yaml 的第 1–3 页；没有 book.yaml 时用 templates/book.layouts.yaml 的封面 + 第 4–5 页（章节页 | 卡片）。
方向里能写的键：style、colors、fonts、brand、duotone，以及任何 book: 设置（逗号分隔，冒号赋值）。
输出：<project>/.qa/directions.jpg（每行一个方向：封面 | 跨页），每个方向的小项目在 <project>/.dir/<名>/。"""
import sys, os, subprocess, glob, shutil, yaml, json
from PIL import Image, ImageDraw, ImageFont
HB = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HB)
a = sys.argv[1:]; opt = {}
for k in ('--title', '--sub', '--kicker', '--lang'):
    if k in a: i = a.index(k); opt[k[2:]] = a[i + 1]; del a[i:i + 2]
if len(a) < 2: sys.exit(__doc__)
P = os.path.abspath(a[0]); dirs = a[1:]
src = os.path.join(P, 'book.yaml'); PAGES = '1-3'; TEMPLATE = not os.path.exists(src)
if TEMPLATE:
    PAGES = '1,4-5'   # 模板：封面 + 章节页 | 卡片（撞色最能看出方向）
    t = yaml.safe_load(open(os.path.join(ROOT, 'templates', 'book.layouts.yaml'), encoding='utf-8'))
    if opt:
        p0 = t['pages'][0]
        p0.pop('stats', None); p0.pop('intro', None)
        for k in ('title', 'sub', 'kicker'):
            if k in opt: p0[k] = opt[k]
            elif k == 'sub': p0.pop('sub', None); p0.pop('en', None)
    os.makedirs(os.path.join(P, '.dir'), exist_ok=True); src = os.path.join(P, '.dir', 'source.yaml')
    yaml.safe_dump(t, open(src, 'w', encoding='utf-8'), allow_unicode=True, sort_keys=False, width=1000)
spec = yaml.safe_load(open(src, encoding='utf-8')); B = spec.get('book') or {}
lang = opt.get('lang') or str((B.get('langs') or [B.get('lang', 'zh')])[0])
rows = []
for d in dirs:
    name, _, kv = d.partition('=')
    sets = [s.replace(':', '=', 1) for s in kv.split(',') if s.strip()]
    out = os.path.join(P, '.dir', name); shutil.rmtree(out, ignore_errors=True)
    subprocess.run([sys.executable, os.path.join(HB, 'subset.py'), P, out, PAGES, '--src', src, '--lang', lang] + sets, check=True, stdout=subprocess.DEVNULL)
    r = subprocess.run(['bash', os.path.join(HB, 'run.sh'), out], env=dict(os.environ, HB_NOLOCK='1'), capture_output=True, text=True)
    gate = 'PASS' if 'GATE: PASS' in r.stdout else 'FAIL'
    if r.returncode and 'GATE' not in r.stdout: print(r.stdout[-1500:], r.stderr[-1500:]); sys.exit(f'方向 {name} 构建出错')
    pgs = sorted(glob.glob(os.path.join(out, '.qa', 'pg*.png')), key=lambda f: int(os.path.basename(f)[2:-4]))
    mp = json.load(open(os.path.join(out, 'map.json'))) if os.path.exists(os.path.join(out, 'map.json')) else {}
    cols = json.load(open(os.path.join(out, '.qa', 'ai_slots.json'))).get('colors', {}) if os.path.exists(os.path.join(out, '.qa', 'ai_slots.json')) else {}
    rows.append((name, kv, gate, pgs, cols, mp.get('color_mode', ''))); print(f'方向 {name}（{kv}）：{len(pgs)} 页 · GATE {gate} · 用色 {mp.get("color_mode", "")}')
w, g, lw = 397, 18, 180; f0 = rows[0][3][0] if rows and rows[0][3] else None; h = round(w * Image.open(f0).height / Image.open(f0).width) if f0 else 561
c = Image.new('RGB', (lw + 3 * w + 2 * g + g, len(rows) * (h + g) + g), '#404040'); dr = ImageDraw.Draw(c)
fnt = fs = None
sys.path.insert(0, HB); import fonts as FO
for fid in ('lxgw-neo-xihei', 'noto-sans-sc', 'inter'):   # 标签里有中文：先找中文字体
    try: p = FO.path_of(fid); fnt = ImageFont.truetype(p, 22); fs = ImageFont.truetype(p, 14); break
    except Exception: pass
import palettes as PAL
for i, (name, kv, gate, pgs, cols, cm) in enumerate(rows):
    y0 = g + i * (h + g)
    dr.text((g, y0 + 4), name, fill='#fff', font=fnt); [dr.text((g, y0 + 44 + j * 22), s.strip(), fill='#ddd', font=fs) for j, s in enumerate(kv.split(','))]
    if cols:   # 6 个颜色角色的色卡（借 ppt-master 的角色模型）：用户可以按角色单独改 book.colors
        rl = PAL.roles(cols); yy = y0 + 60 + 22 * len(kv.split(','))
        dr.text((g, yy), f'用色 {cm}', fill='#fff', font=fs); yy += 24
        for j, (k, v) in enumerate(rl.items()):
            dr.rectangle((g, yy + j * 34, g + 26, yy + j * 34 + 26), fill=v, outline='#888')
            dr.text((g + 34, yy + j * 34), PAL.ROLE_ZH[k], fill='#ddd', font=fs); dr.text((g + 34, yy + j * 34 + 14), v.upper(), fill='#aaa', font=fs)
    if gate != 'PASS': dr.text((g, y0 + h - 30), 'QA 未通过', fill='#f88', font=fs)
    if TEMPLATE: dr.text((g, y0 + h - 54), '跨页内容是模板示例', fill='#aaa', font=fs)
    for j, f in enumerate(pgs[:3]):
        x0 = lw + (0 if j == 0 else w + g + (j - 1) * w)
        c.paste(Image.open(f).convert('RGB').resize((w, h), Image.LANCZOS), (x0, y0))
os.makedirs(os.path.join(P, '.qa'), exist_ok=True); o = os.path.join(P, '.qa', 'directions.jpg'); c.save(o, quality=85); print(o)
