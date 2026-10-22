#!/usr/bin/env python3
"""页序检查（构建前跑，只提示不拦截）：python3 lint.py <project>
- 每页的 job:（这一页让读者做什么 / 知道什么）有没有写；写了 book.kind 时，job 要用 purposes/<kind>.yaml 的页面角色词
- 用途要求的页（封面、报名方式、封底……）有没有
- 节奏：每页按版式和字数归成 锚点 anchor / 密集 dense / 呼吸 breathing（页上可写 rhythm: 覆盖），
  连续 3 页以上密集、6 页以上没有锚点、连续 3 页同版式 → 提示
- 封面在第 1 页、封底在最后、页数是 4 的倍数
- 先设计再写 yaml：page-plan.md 有没有覆盖 book.yaml 的每一页（references/adaptation.md）
结果打印并写到 .qa/lint.txt。"""
import sys, os, re, yaml
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
P = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else '.')
spec = yaml.safe_load(open(os.path.join(P, 'book.yaml'), encoding='utf-8')) or {}
sys.path.insert(0, HERE)
from i18n_pick import first_lang
spec = first_lang(spec)
B = spec.get('book') or {}; pages = spec.get('pages') or []
SPAN2 = {'SPREAD_P', 'SPREAD_H', 'SPREAD_OPENER'}
ANCHOR = {'FULL', 'POSTER', 'COLLAGE', 'PLATE', 'SEQUENCE', 'PHOTO_OPEN', 'MASONRY', 'CONTACT'} | SPAN2
CJK = re.compile(r'[㐀-鿿]')
def size(o):
    if isinstance(o, str): return len(CJK.findall(o)) + len(re.findall(r'[A-Za-z]+', o)) * 0.6
    if isinstance(o, dict): return sum(size(v) for k, v in o.items() if k not in ('layout', 'image', 'images', 'note', 'job', 'surface', 'focus'))
    if isinstance(o, list): return sum(size(v) for v in o)
    return 0
def rhythm(p):
    if p.get('rhythm') in ('anchor', 'dense', 'breathing'): return p['rhythm']
    lay = p.get('layout'); s = size(p)
    if lay in ANCHOR: return 'anchor'
    if lay in ('GRID', 'TWO') or s > 420: return 'dense'
    if lay in ('CARDS', 'STAGGER') and s > 260: return 'dense'
    return 'breathing'
kind = B.get('kind'); roles = {}; must = []; K = {}
if kind:
    f = os.path.join(ROOT, 'purposes', f'{kind}.yaml')
    if os.path.exists(f):
        K = yaml.safe_load(open(f, encoding='utf-8')) or {}; roles = K.get('roles') or {}
        must = [r for r, v in roles.items() if (v or {}).get('must')]
out = []; warn = out.append
n = 1; seq = []; nojob = []; jobs = []
for i, p in enumerate(pages):
    span = 2 if p.get('layout') in SPAN2 else 1
    rh = rhythm(p); seq += [(n, p.get('layout'), rh)] * 1
    job = p.get('job')
    if not job: nojob.append(n)
    else:
        jobs.append(str(job).split()[0].split('·')[0].strip())
        if roles and jobs[-1] not in roles: warn(f'[job] 第{n}页 job: {job} —— 不是 {kind} 的页面角色词（{" / ".join(roles)}）。用角色词开头，后面可以写说明，如 job: why · 三个理由')
    n += span
total = n - 1
if nojob: warn(f'[job] {len(nojob)} 页没写 job:（第 {"、".join(map(str, nojob[:12]))} 页）→ 每页写一句“这一页让读者做什么 / 知道什么”，排版和审稿都按它判断')
for r in must:
    if r not in jobs: warn(f'[缺页] {K.get("name", kind)} 需要一页 {r}（{roles[r].get("zh", "")}），book.yaml 里没有 job: {r}')
if pages:
    if pages[0].get('layout') not in ('FULL', 'POSTER', 'PHOTO_OPEN') and not (pages[0].get('layout') == 'PAPER' and str(pages[0].get('job','')).startswith('cover')): warn('[封面] 第 1 页不是 FULL / POSTER / PHOTO_OPEN：封面要一张图或一个大标题，读者第一眼决定翻不翻')
    if len(pages) > 3 and pages[-1].get('layout') not in ('FULL', 'POSTER') and not (pages[-1].get('layout') == 'PAPER' and str(pages[-1].get('job','')).startswith('back')): warn('[封底] 最后一页不是 FULL / POSTER：封底放联系方式、二维码、下一步动作')
run = 0; since = 0; same = 1
for k, (pn, lay, rh) in enumerate(seq):
    run = run + 1 if rh == 'dense' else 0
    since = 0 if rh == 'anchor' else since + 1
    same = same + 1 if k and lay == seq[k - 1][1] else 1
    if run == 4: warn(f'[节奏] 第{pn - 3}–{pn}页连续 4 页密集（{"、".join(s[1] for s in seq[k - 3:k + 1])}）→ 中间插一页 FULL / COLLAGE，或把一页换成 ONE / MIX')
    if since == 7: warn(f'[节奏] 第{pn - 6}–{pn}页 7 页没有锚点页 → 插一页 FULL（章节页）或 COLLAGE')
    if same == 3 and lay not in ('READING', 'PAPER'): warn(f'[节奏] 第{pn - 2}–{pn}页连续 3 页都是 {lay} → 换一种版式（CARDS ↔ STAGGER / TWO / GRID）')
# ---------------------------------------------------------------- 设计先行：page-plan.md 覆盖每一页（references/adaptation.md）
PL = os.path.join(P, 'page-plan.md')
if pages and not B.get('frozen') and os.path.basename(P) != '.proof':
    txt = open(PL, encoding='utf-8').read() if os.path.exists(PL) else ''
    covered = set(); done = set()
    def span(a_, b_): return set(range(int(a_), int(b_ or a_) + 1))
    for m in re.finditer(r'^\|\s*[pP第]?\s*(\d+)\s*(?:[–—~-]\s*(\d+))?\s*页?\s*\|(.*)$', txt, re.M):   # 页面总表的行（还是〔占位〕的不算）
        if '〔' not in m.group(3): covered |= span(m.group(1), m.group(2))
    for m in re.finditer(r'^#{2,4}\s*(?:第\s*|[pP]\.?\s*)(\d+)\s*(?:[–—~-]\s*(\d+))?\s*页?[^\n]*\n((?:(?!^#{1,4}\s).*\n?)*)', txt, re.M):   # 逐页小节
        body = m.group(3).strip()
        if body and '〔读者看完要知道' not in body: covered |= span(m.group(1), m.group(2)); done |= span(m.group(1), m.group(2))
    if not covered:
        warn('[设计] 还没有 page-plan.md 的逐页方案 → 先定整册节奏，再逐页写页面任务、文案分工（copy_map.md 的 S 编号）、视觉主角、视线、图文关系，最后才写 book.yaml（references/adaptation.md）')
    else:
        miss = [k for k in range(1, total + 1) if k not in covered]
        if miss: warn(f'[设计] page-plan.md 没有第 {"、".join(map(str, miss[:12]))} 页 → 先把这几页的方案写进 page-plan.md，再改 book.yaml')
        thin = [k for k in sorted(covered) if k not in done and k <= total]
        if thin and done: warn(f'[设计] page-plan.md 里第 {"、".join(map(str, thin[:12]))} 页只在总表里，还没有逐页小节（页面任务 / 文案分工 / 展示方案）')
# YAML 里没加引号的冒号会把整段变成映射，页面上直接印出 {...}
pn = 1
for p in pages:
    badk = [k for k in ('text', 'notes', 'intro', 'quote', 'by', 'caption', 'sub')
            if isinstance(p.get(k), dict) or (isinstance(p.get(k), list) and any(isinstance(v, dict) for v in p[k]))]
    if badk:
        warn(f'[文案] 第{pn}页 {"、".join(badk)} 里有 YAML 映射（多半是段落中的冒号没加引号）→ 用单引号包住整段，否则页面会印出 {{...}}')
    pn += 2 if p.get('layout') in SPAN2 else 1
todo = []
def find_todo(o, path):
    if isinstance(o, str) and o.strip() == 'TODO': todo.append(path)
    elif isinstance(o, dict): [find_todo(v, f'{path}.{k}') for k, v in o.items()]
    elif isinstance(o, list): [find_todo(v, f'{path}[{i}]') for i, v in enumerate(o)]
find_todo(pages, 'pages')
if todo: warn(f'[待填] 还有 {len(todo)} 处 TODO（沿用旧册时留的空）：{"、".join(todo[:6])}… → 从 doc.md 复制新文字填进去；用不上的键删掉')
if total % 4 and total > 4: warn(f'[页数] 共 {total} 页，骑马钉需要 4 的倍数（差 {4 - total % 4} 页）')
tgt = B.get('pages')
line = '节奏：' + ' '.join({'anchor': '■', 'dense': '▤', 'breathing': '□'}[r] for _, _, r in seq) + '  （■ 锚点  ▤ 密集  □ 呼吸）'
os.makedirs(os.path.join(P, '.qa'), exist_ok=True)
open(os.path.join(P, '.qa', 'lint.txt'), 'w', encoding='utf-8').write('\n'.join([line] + out) + '\n')
print(line)
for o in out: print(o)
if not out: print('页序检查：没有问题 ✓')
