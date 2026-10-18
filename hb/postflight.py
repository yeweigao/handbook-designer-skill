#!/usr/bin/env python3
"""导出后自检：python3 postflight.py <project> <out.pdf> [--draft]
页数（和 plan.txt 对得上）、PDF 尺寸、文件大小、字体（Type 3）、PDF 书签数（F09：断言 ≥ 1）、可点链接数（目录 + 网址）、
低清图片、图片来源 / 授权（F13：source 和 license 都查）→ .qa/postflight.md，并记进 .qa/log.md。
同时生成交印清单 .qa/print_checklist.md（F37/F38：低 DPI 图清单 + 装订建议），export.sh 会拷进 out/。"""
import sys, os, re, glob, time, json
P, PDF = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2]); DRAFT = '--draft' in sys.argv
Q = os.path.join(P, '.qa'); os.makedirs(Q, exist_ok=True); L = []; bad = 0
def add(ok, s):
    global bad
    L.append(('✓ ' if ok else '✗ ') + s); bad += (not ok)
def _oc(o):   # pypdf 的 outline 是嵌套列表，递归数条目
    return sum(_oc(x) for x in o) if isinstance(o, list) else 1
try:
    from pypdf import PdfReader
    r = PdfReader(PDF); n = len(r.pages); box = r.pages[0].mediabox; wmm, hmm = float(box.width) / 72 * 25.4, float(box.height) / 72 * 25.4
    links = ext = 0
    for pg in r.pages:
        for a in pg.get('/Annots') or []:
            a = a.get_object()
            if a.get('/Subtype') != '/Link': continue
            act = a.get('/A'); act = act.get_object() if act else {}
            if act and act.get('/URI'): ext += 1
            else: links += 1
    plan = os.path.join(P, 'plan.txt')
    want = sum(2 if re.match(r'^\d+-\d+', l) else 1 for l in open(plan, encoding='utf-8').read().splitlines() if l.strip()) if os.path.exists(plan) else n
    add(n == want, f'页数 {n}（排版计划 {want}）' + ('' if n % 4 == 0 else f'；骑马钉要 4 的倍数（差 {4 - n % 4}）'))
    add(True, f'成品尺寸 {wmm:.0f} × {hmm:.0f} mm')
    add(True, f'可点链接：页内跳转 {links} 个（目录）、网址 / 邮箱 {ext} 个')
    try: nb = _oc(r.outline)
    except Exception: nb = 0
    add(nb >= 1, f'PDF 书签：{nb} 个（封面 / 章节 / 页标题）' + ('' if nb else '（导出时可能缺 pikepdf：pip install pikepdf 后重新导出）'))
except ImportError:
    add(True, '（没有 pypdf，跳过页数 / 链接 / 书签检查：pip install pypdf）')
raw = open(PDF, 'rb').read(); t3 = len(re.findall(rb'/Subtype\s*/Type3', raw))
add(t3 == 0, '字体：全部可编辑 TrueType' if not t3 else f'字体：{t3} 处 Type 3（有字体没下载，回退到了系统字体）')
mb = os.path.getsize(PDF) / 1e6; add(mb < 40, f'PDF {mb:.1f} MB' + ('（大于 40MB，微信 / 邮件发不出去：图片太大，HB scale 调回 2）' if mb >= 40 else ''))
iy = os.path.join(P, 'images.yaml')
im = {}
if os.path.exists(iy):
    import yaml
    im = yaml.safe_load(open(iy, encoding='utf-8')) or {}
    imgs = im.get('images') or {}
    low = [k for k, v in imgs.items() if (v or {}).get('dpi') and v['dpi'] < 150]
    nosrc = [k for k, v in imgs.items() if not (v or {}).get('source') and not str(k).startswith(('ai_', 'logo'))]
    nolic = [k for k, v in imgs.items() if not (v or {}).get('license') and not str(k).startswith(('ai_', 'logo'))]
    add(not low, f'图片清晰度：{len(low)} 张低于 150dpi' + (f'（{", ".join(low[:5])}）→ 换原图或挪到小图位' if low else ''))
    miss = []   # F13：source 和 license 分别验证，缺哪项列哪项
    if nosrc: miss.append(f'{len(nosrc)} 张缺来源（{", ".join(nosrc[:5])}）')
    if nolic: miss.append(f'{len(nolic)} 张缺授权（{", ".join(nolic[:5])}）')
    add(not miss, '来源 / 授权：全部图片都写了来源与授权' if not miss else '来源 / 授权：' + '、'.join(miss) + ' → 在 images.yaml 的 source / license 里补上')
if DRAFT: add(True, '草稿版：每页带“草稿 DRAFT”水印，不能交印刷厂')
# ---- 交印清单（F37/F38）：低 DPI 图清单 + 装订建议 → .qa/print_checklist.md（export.sh 拷进 out/）
plan = os.path.join(P, 'plan.txt')
rows = [l for l in open(plan, encoding='utf-8').read().splitlines() if l.strip()] if os.path.exists(plan) else []
total = sum(2 if re.match(r'^\d+-\d+', l) else 1 for l in rows)
spreads = []   # 跨页照片页：(起始页, 结束页, 图文件名)
for l in rows:
    m = re.match(r'^(\d+)(?:-(\d+))?\s', l)
    if m and m.group(2):
        f = l.split()
        img = next((x for x in f[2:] if x.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))), '')
        spreads.append((int(m.group(1)), int(m.group(2)), img))
lowimg = sorted(((k, v['dpi'], v.get('pages') or []) for k, v in (im.get('images') or {}).items() if (v or {}).get('dpi') and v['dpi'] < 150), key=lambda x: x[1])
C = ['# 交印前检查清单（导出时自动生成，看完再送印）', '', f'## 1. 低清晰度图片（< 150dpi，共 {len(lowimg)} 张）']
if lowimg:
    C.append('| 图片 | 用在第几页 | 约 | 建议 |')
    C.append('|---|---|---|---|')
    for k, dpi, pgs in lowimg:
        C.append(f'| {k} | 第 {"、".join(map(str, pgs)) or "?"} 页 | {dpi}dpi | 换更大的原图，或挪到小图位；logo / 二维码类功能图改用矢量（SVG） |')
else:
    C.append('全部 ≥ 150dpi ✓')
C += ['', '## 2. 装订建议', f'- 共 {total} 页。']
if total % 4:
    C.append(f'- 骑马钉：页数必须是 4 的倍数 → 补 {4 - total % 4} 页（空白页 / 版权页 / 后记均可）或改无线胶装。')
else:
    C.append('- 骑马钉：页数是 4 的倍数 ✓（无线胶装无此要求）。')
if spreads:
    for a, b, img in spreads:
        C.append(f'- 跨页照片：第 {a}–{b} 页（{img or "见图"}）→ 跨页左页须为偶数页（装订后左右才对，引擎已保证）；中缝（两页接缝，装订公差约 3–5mm）附近避字、避人脸主体与重要 logo。')
else:
    C.append('- 没有跨页照片页（单页照片不受装订影响）。')
open(os.path.join(Q, 'print_checklist.md'), 'w', encoding='utf-8').write('\n'.join(C) + '\n')
g = os.path.join(Q, 'gate.json')
open(os.path.join(Q, 'postflight.md'), 'w', encoding='utf-8').write(f'# 导出自检 {time.strftime("%Y-%m-%d %H:%M")}\n{os.path.basename(PDF)}\n\n' + '\n'.join('- ' + l for l in L) + '\n')
print('导出自检：'); [print('  ' + l) for l in L]
lg = os.path.join(Q, 'log.md')
if not os.path.exists(lg): open(lg, 'w', encoding='utf-8').write('# 构建日志\n| 时间 | 步骤 | 结果 | 说明 |\n|---|---|---|---|\n')
open(lg, 'a', encoding='utf-8').write(f'| {time.strftime("%m-%d %H:%M")} | export{" draft" if DRAFT else ""} | {"OK" if not bad else f"{bad} 项要看"} | {os.path.basename(PDF)} |\n')
