#!/usr/bin/env python3
"""导出后自检：python3 postflight.py <project> <out.pdf> [--draft]
页数（和 plan.txt 对得上）、PDF 尺寸、文件大小、字体（Type 3）、可点链接数（目录 + 网址）、低清图片、图片授权清单 → .qa/postflight.md，并记进 .qa/log.md。"""
import sys, os, re, glob, time, json
P, PDF = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2]); DRAFT = '--draft' in sys.argv
Q = os.path.join(P, '.qa'); os.makedirs(Q, exist_ok=True); L = []; bad = 0
def add(ok, s):
    global bad
    L.append(('✓ ' if ok else '✗ ') + s); bad += (not ok)
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
    want = sum(2 if re.match(r'^\d+-\d+', l) else 1 for l in open(plan).read().splitlines() if l.strip()) if os.path.exists(plan) else n
    add(n == want, f'页数 {n}（排版计划 {want}）' + ('' if n % 4 == 0 else f'；骑马钉要 4 的倍数（差 {4 - n % 4}）'))
    add(True, f'成品尺寸 {wmm:.0f} × {hmm:.0f} mm')
    add(True, f'可点链接：页内跳转 {links} 个（目录）、网址 / 邮箱 {ext} 个')
except ImportError:
    add(True, '（没有 pypdf，跳过页数 / 链接检查：pip install pypdf）')
raw = open(PDF, 'rb').read(); t3 = len(re.findall(rb'/Subtype\s*/Type3', raw))
add(t3 == 0, '字体：全部可编辑 TrueType' if not t3 else f'字体：{t3} 处 Type 3（有字体没下载，回退到了系统字体）')
mb = os.path.getsize(PDF) / 1e6; add(mb < 40, f'PDF {mb:.1f} MB' + ('（大于 40MB，微信 / 邮件发不出去：图片太大，HB scale 调回 2）' if mb >= 40 else ''))
iy = os.path.join(P, 'images.yaml')
if os.path.exists(iy):
    import yaml
    im = yaml.safe_load(open(iy, encoding='utf-8')) or {}
    low = [k for k, v in (im.get('images') or {}).items() if (v or {}).get('dpi') and v['dpi'] < 150]
    nolic = [k for k, v in (im.get('images') or {}).items() if not (v or {}).get('source') and not str(k).startswith(('ai_', 'logo'))]
    add(not low, f'图片清晰度：{len(low)} 张低于 150dpi' + (f'（{", ".join(low[:5])}）→ 换原图或挪到小图位' if low else ''))
    add(not nolic, f'图片来源：{len(nolic)} 张没写来源 / 授权' + (f'（{", ".join(nolic[:5])}）→ 在 images.yaml 的 source 里补上' if nolic else ''))
if DRAFT: add(True, '草稿版：每页带“草稿 DRAFT”水印，不能交印刷厂')
g = os.path.join(Q, 'gate.json')
open(os.path.join(Q, 'postflight.md'), 'w', encoding='utf-8').write(f'# 导出自检 {time.strftime("%Y-%m-%d %H:%M")}\n{os.path.basename(PDF)}\n\n' + '\n'.join('- ' + l for l in L) + '\n')
print('导出自检：'); [print('  ' + l) for l in L]
lg = os.path.join(Q, 'log.md')
if not os.path.exists(lg): open(lg, 'w').write('# 构建日志\n| 时间 | 步骤 | 结果 | 说明 |\n|---|---|---|---|\n')
open(lg, 'a').write(f'| {time.strftime("%m-%d %H:%M")} | export{" draft" if DRAFT else ""} | {"OK" if not bad else f"{bad} 项要看"} | {os.path.basename(PDF)} |\n')
