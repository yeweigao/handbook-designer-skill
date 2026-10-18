#!/usr/bin/env python3
"""在线编辑页：python3 edit_page.py <项目或语言子项目> [输出.html]
在 run.sh 构建好的 book.html 基础上：每段文字标上它在 book.yaml 里的位置（pages[4].cards[2].x），照片标上原文件名，
内嵌图片和字体成单文件，再加上 editor.js（改字、换图、批注、当场重排检查）。默认输出 <项目>/out/edit_<语言>.html。
发布（Claude 用 Artifact 工具）：capabilities = {db: {}, user: {}, assets: {}, comments: {composer_only: true}, downloads: true}
同步回 book.yaml：workflows/edit-online.md（读 db → edits.json → sync_edits.py → run.sh → 重新生成本页并发布到同一个地址）。"""
import sys, os, re, json, html as H, subprocess, yaml
HB = os.path.dirname(os.path.abspath(__file__))
P = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else '.')
if not os.path.exists(os.path.join(P, 'book.html')):
    langs = [d for d in os.listdir(P) if os.path.exists(os.path.join(P, d, 'book.html'))]
    sys.exit(f'{P} 里没有 book.html：先 run.sh；多语言的书指定语言子目录，如 {os.path.join(P, langs[0]) if langs else P + "/zh"}')
spec = yaml.safe_load(open(os.path.join(P, 'book.yaml'), encoding='utf-8')) or {}
B = spec.get('book') or {}; lang = str(B.get('lang', 'zh'))
mp = json.load(open(os.path.join(P, 'map.json'), encoding='utf-8'))
pidx = {i: list(range(n, n + span)) for i, n, span in mp.get('pidx', [])}
SKIP = {'layout', 'image', 'images', 'img', 'src', 'focus', 'target', 'zoom', 'surface', 'mirror', 'variant', 'style', 'cols', 'count', 'deco', 'num', 'tone',
        'note', 'job', 'align', 'rhythm', 'index', 'toc', 'duo', 'folio', 'logo', 'contact', '_last', 'widths', 'columns', 'items_cols', 'fit', 'h', 'w', 'mt',
        'size', 'spacing', 'lh', 'stroke', 'frame', 'grow', 'split', 'window', 'colors', 'figure', 'logos', 'qr', 'gradient', 'html'}
IMG = re.compile(r'\.(jpe?g|png|webp|svg|gif)$', re.I)
def norm(s): return re.sub(r'[​\s]+', '', H.unescape(re.sub(r'<[^>]+>', '', str(s))))
leaves = []
def walk(o, path, pages):
    if isinstance(o, dict):
        for k, v in o.items():
            if k not in SKIP: walk(v, f'{path}.{k}', pages)
    elif isinstance(o, list):
        for j, v in enumerate(o): walk(v, f'{path}[{j}]', pages)
    elif isinstance(o, (str, int, float)) and not isinstance(o, bool):
        s = str(o)
        if s.strip() and not IMG.search(s) and not s.startswith(('ai:', 'placeholder')) and len(norm(s)) >= 1:
            leaves.append(dict(path=path, pages=pages, text=s, norm=norm(s)))
for i, p in enumerate(spec.get('pages') or []):
    walk(p, f'pages[{i}]', pidx.get(i, []))
imgs = {}
for u in mp.get('use') or []:
    if u.get('img'): imgs[u['img']] = u['file']
src = open(os.path.join(P, 'book.html'), encoding='utf-8').read()
src = re.sub(r'<img\b([^>]*?)src="img/([^"]+)"', lambda m: f'<img{m.group(1)}data-name="{m.group(2)}" src="img/{m.group(2)}"', src)
src = re.sub(r'data-fit="(\d+)"', r'data-fit="\1" data-fit0="\1"', src)   # 原始字号上限：改字后重排要从它重新开始缩
tmp = os.path.join(P, '.edit_src.html'); open(tmp, 'w', encoding='utf-8').write(src)
out = os.path.abspath(sys.argv[2]) if len(sys.argv) > 2 else os.path.join(P, 'out', f'edit_{lang}.html')
os.makedirs(os.path.dirname(out), exist_ok=True)
subprocess.run([sys.executable, os.path.join(HB, 'standalone.py'), tmp, out], check=True, stdout=subprocess.DEVNULL); os.remove(tmp)
h = open(out, encoding='utf-8').read()
title = str(B.get('title') or 'Handbook')
cfg = json.dumps(dict(lang=lang, title=H.escape(re.sub(r'<[^>]+>', '', title)), leaves=leaves, imgs=imgs), ensure_ascii=False).replace('</', '<\\/')
js = open(os.path.join(HB, 'editor.js'), encoding='utf-8').read()
h = re.sub(r'<title>.*?</title>', f'<title>{H.escape(re.sub(r"<[^>]+>", "", title))} · 在线编辑</title>', h, count=1, flags=re.S)
h = h.replace('</body>', f'<script>window.HB_EDIT={cfg};</script><script>{js}</script></body>', 1)
open(out, 'w', encoding='utf-8').write(h)
print(f'{out}：{len(leaves)} 段可改文字、{len(imgs)} 张可换照片，{len(h) // 1024} KB'
      + ('（超过 16MB，发布不了：先把 book.scale 调回 2）' if len(h) > 16e6 else ''))
