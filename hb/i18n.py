#!/usr/bin/env python3
"""多语言版本：在 book.yaml 层翻译（版式、图片、参数全部沿用，只换文字）。
1) python3 i18n.py extract <project>/book.yaml strings.json
      → strings.json = {"原文": ""}（按出现顺序去重）。把每个值填成译文；值留空 = 保留原文。
2) python3 i18n.py apply <project>/book.yaml strings.json <新项目目录> <lang>
      → <新项目目录>/book.yaml（book.lang=<lang>）＋ 链接原项目的 photos/。然后 bash hb/run.sh <新项目目录>
翻译要求：信达雅，意思不增不减；保留 <b> <br> 等内联标签；英文通常比中文长 30–60%，溢出时按 doctor 提示调 size / 挪内容。"""
import sys, os, json, yaml
SKIP = {'layout','image','window','widths','color','style','right_layout','photos','note','html','colors','lang','fonts','align','folio_style','gradient','figure','gallery','qr','fit','focus','frame','purpose','tone'}
def walk(o, fn, key=None):
    if isinstance(o, dict): return {k: (v if k in SKIP or (k in ('cols',) and isinstance(v, str)) else walk(v, fn, k)) for k, v in o.items()}
    if isinstance(o, list): return [walk(x, fn, key) for x in o]
    if isinstance(o, str) and o.strip(): return fn(o)
    return o
cmd = sys.argv[1]; spec = yaml.safe_load(open(sys.argv[2], encoding='utf-8'))
if cmd == 'extract':
    seen = {}
    walk(spec, lambda s: seen.setdefault(s, '') or s)
    json.dump(seen, open(sys.argv[3], 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    n_html = json.dumps(spec, ensure_ascii=False).count('"html"')
    print(f'{len(seen)} 条 → {sys.argv[3]}' + (f'；注意有 {n_html} 个 html 块需要手动翻译' if n_html else ''))
elif cmd == 'apply':
    M = json.load(open(sys.argv[3], encoding='utf-8')); out = os.path.abspath(sys.argv[4]); lang = sys.argv[5] if len(sys.argv) > 5 else 'en'
    miss = []
    def tr(s):
        t = M.get(s)
        if not t: miss.append(s); return s
        return t
    new = walk(spec, tr); new.setdefault('book', {})['lang'] = lang
    os.makedirs(out, exist_ok=True)
    src_proj = os.path.dirname(os.path.abspath(sys.argv[2])); ph = spec.get('book', {}).get('photos', 'photos')
    if not os.path.exists(os.path.join(out, ph)) and os.path.isdir(os.path.join(src_proj, ph)):
        os.symlink(os.path.join(src_proj, ph), os.path.join(out, ph))
    yaml.safe_dump(new, open(os.path.join(out, 'book.yaml'), 'w', encoding='utf-8'), allow_unicode=True, sort_keys=False, width=1000)
    print(f'→ {out}/book.yaml  lang={lang}；未翻译（保留原文）{len(miss)} 条' + (': ' + ' | '.join(miss[:20]) if miss else ''))
