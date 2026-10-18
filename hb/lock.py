#!/usr/bin/env python3
"""决策锁：python3 lock.py <project>
拿 <project>/brief.md（第 0 步用户确认过的决定，模板 templates/brief.md）顶部的设置和 book.yaml 的 book: 对一遍。
不一致 → 打印 [决策不一致] 并退出 1（run.sh 停下，不构建）。空值 / 占位行（（不适用）、待定、N/A…）→ 提示“第 N 行未确认项：删除该行”，同样退出 1。
没有 brief.md → 只提示。
页数只提示（实际页数和目标差 4 页以上才说）。"""
import sys, os, re, yaml
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from i18n_pick import first_lang
P = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else '.')
f = os.path.join(P, 'brief.md')
if not os.path.exists(f):
    print('决策锁：没有 brief.md（第 0 步确认的决定没记下来）→ 复制 templates/brief.md 到项目里填好；quick 路线可以不写'); sys.exit(0)
t = open(f, encoding='utf-8').read()
m = re.match(r'\s*---\n(.*?)\n---', t, re.S)
if not m: print('决策锁：brief.md 顶部没有 --- 设置块 ---，跳过'); sys.exit(0)
lock = yaml.safe_load(m.group(1)) or {}
BLK, BLK0 = m.group(1), m.start(1)   # 顶部设置块全文 + 它在 brief.md 里的偏移（算行号用）
spec = yaml.safe_load(open(os.path.join(P, 'book.yaml'), encoding='utf-8')) or {}
import brand as BR
B = BR.apply(spec.get('book') or {})[0]   # 品牌包里的默认设置也算
SPAN2 = {'SPREAD_P', 'SPREAD_H', 'SPREAD_OPENER'}
bad = []; unfirm = []
def norm(v):
    if isinstance(v, list): return [str(x) for x in v]
    return None if v is None else str(v)
def unconfirmed(v):
    """没确认的行：空值，或（不适用）/ 待定 / N/A / TODO 这类占位——占位不如删掉"""
    if v is None: return True
    s = str(v).strip().strip('（）()').strip()
    return (not s) or s in ('-', '—', '?', '？') or bool(re.fullmatch(r'不适用|待定|未定|暂无|无|n/?a|todo|tbd', s, re.I))
def brief_line(k):
    """brief.md 顶部设置块里这个键在第几行（1 起；找不到返回 0）"""
    q = re.search(r'(?m)^\s*' + re.escape(k) + r'\s*:', BLK)
    return t[:BLK0 + q.start()].count('\n') + 1 if q else 0
DEF = dict(purpose='workbook', style='photo', canvas='a4', color_mode='auto', look='classic')
for k in ('purpose', 'kind', 'brand', 'style', 'look', 'colors', 'color_mode', 'fonts', 'canvas', 'langs'):
    if k not in lock: continue
    if unconfirmed(lock[k]):
        unfirm.append((brief_line(k), k, lock[k])); continue
    if k == 'color_mode' and lock[k] == 'auto': continue
    want = norm(lock[k])
    if k == 'langs':
        have = norm(B.get('langs') or [B.get('lang', 'zh')])
    elif k == 'fonts':
        have_d = B.get('fonts') if isinstance(B.get('fonts'), dict) else {}
        want_d = lock[k] if isinstance(lock[k], dict) else {}
        diff = {a: (v, have_d.get(a)) for a, v in want_d.items() if str(have_d.get(a, '')) != str(v)}
        if diff: bad.append((k, ', '.join(f'{a}={v}' for a, (v, _) in diff.items()), ', '.join(f'{a}={h if h is not None else "（未设）"}' for _, h in diff.values())))
        continue
    elif k == 'colors' and isinstance(B.get('colors'), dict):
        have = norm(B['colors'].get('preset'))
        if have is None: continue          # 写了具体色值（品牌色）：不比
    else:
        have = norm(B.get(k, DEF.get(k)))
        if k == 'color_mode' and have == 'auto' and B.get('style') == 'swiss': have = 'mono'   # 瑞士风格默认单色档
    if k == 'brand' and want and have is None: have = None
    if want != have: bad.append((k, want, have))
for k, w, hv in bad:
    print(f'[决策不一致] brief.md 记的 {k}: {w}，book.yaml 里是 {hv} → 用户确认的是 {w}。'
          f'要么把 book.yaml 改回 {w}；要么先问用户，同意后在 brief.md 改 {k} 并在“改动记录”写一笔')
for n, k, v in unfirm:
    print(f'brief.md 第 {n} 行未确认项（{k}: {v if v is not None else "空"}）：删除该行，不要留空值/占位'
          f'（这一行没和用户确认过；确认后再写回来）')
if lock.get('pages'):
    n = sum(2 if p.get('layout') in SPAN2 else 1 for p in (first_lang(spec).get('pages') or []))
    if abs(n - int(lock['pages'])) >= 4: print(f'提示：brief.md 的目标页数是 {lock["pages"]}，现在排了 {n} 页 → 差得多时和用户说一声')
if bad or unfirm: sys.exit(1)
print(f'决策锁：book.yaml 与 brief.md 一致 ✓（{", ".join(k for k in lock if lock[k] is not None and k not in ("route", "pages"))}）')
