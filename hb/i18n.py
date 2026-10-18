#!/usr/bin/env python3
"""多语言版本：在 book.yaml 层翻译（版式、图片、参数全部沿用，只换文字）。
1) python3 i18n.py extract <project>/book.yaml strings.json
      → strings.json = {"原文": ""}（按出现顺序去重）。把每个值填成译文；值留空 = 保留原文。
2) python3 i18n.py apply <project>/book.yaml strings.json <新项目目录> <lang>
      → <新项目目录>/book.yaml（book.lang=<lang>）＋ 链接原项目的 photos/。然后 bash hb/run.sh <新项目目录>
3) 一份 book.yaml 写多种语言（推荐，中英文经常要同时出）：任何文字都可以写成 {zh: 中文, en: English}，并在 book 里写 langs: [zh, en]。
   bash hb/run.sh <project> 会自动拆成 <project>/zh、<project>/en 两个子项目分别构建、分别跑完整检查，再出一张中英逐页对照图（.qa/compare_*.jpg）。
   手动拆：python3 i18n.py split <project>/book.yaml   → <project>/<lang>/book.yaml（photos 链接回原项目）
翻译要求：信达雅，意思不增不减；保留 <b> <br> 等内联标签；英文通常比中文长 30–60%，溢出时按 doctor 提示调 size / 挪内容。"""
import sys, os, json, yaml
SKIP = {'layout','image','window','widths','color','style','right_layout','photos','note','html','colors','lang','fonts','align','folio_style','gradient','figure','gallery','qr','fit','focus','frame','purpose','tone'}
def walk(o, fn, key=None):
    if isinstance(o, dict): return {k: (v if k in SKIP or (k in ('cols',) and isinstance(v, str)) else walk(v, fn, k)) for k, v in o.items()}
    if isinstance(o, list): return [walk(x, fn, key) for x in o]
    if isinstance(o, str) and o.strip(): return fn(o)
    return o
LANGS_ALL = {'zh', 'zh-hans', 'zh-hant', 'zh-tw', 'zh-hk', 'en', 'ja', 'ko', 'fr', 'de', 'es', 'it', 'pt', 'ru', 'th', 'vi', 'ms', 'ar'}
def is_multi(o): return isinstance(o, dict) and len(o) > 0 and all(str(k).lower() in LANGS_ALL for k in o)
def langs_of(spec):
    b = spec.get('book') or {}
    if b.get('langs'): return [str(x) for x in b['langs']]
    found = []
    def scan(o):
        if is_multi(o):
            for k in o:
                if str(k) not in found: found.append(str(k))
        elif isinstance(o, dict): [scan(v) for v in o.values()]
        elif isinstance(o, list): [scan(v) for v in o]
    scan(spec); return found or [str(b.get('lang', 'zh'))]
def pick(o, lang, miss, path=''):
    if isinstance(o, dict) and any(str(k).lower() in LANGS_ALL for k in o) and not is_multi(o) and any(v is None for v in o.values()):
        miss.append(f'{path}（{{zh: …, en: …}} 里的英文含逗号被拆开了 → 给那段文字加单引号：en: \'…, …\'）'); return pick({k: v for k, v in o.items() if v is not None}, lang, [], path)
    if is_multi(o):
        for k in o:
            if str(k).lower() == lang.lower(): return pick(o[k], lang, miss, path)
        for k in o:
            if str(k).lower().split('-')[0] == lang.lower().split('-')[0]: return pick(o[k], lang, miss, path)
        miss.append(path); return pick(next(iter(o.values())), lang, miss, path)
    if isinstance(o, dict): return {k: pick(v, lang, miss, f'{path}.{k}' if path else str(k)) for k, v in o.items()}
    if isinstance(o, list): return [pick(v, lang, miss, f'{path}[{i}]') for i, v in enumerate(o)]
    return o
cmd = sys.argv[1]; spec = yaml.safe_load(open(sys.argv[2], encoding='utf-8'))
if cmd == 'langs':
    print(' '.join(langs_of(spec))); sys.exit(0)
if cmd == 'split':
    src_proj = os.path.dirname(os.path.abspath(sys.argv[2])); ph = (spec.get('book') or {}).get('photos', 'photos')
    if isinstance(ph, dict): ph = 'photos'
    bad = 0
    for lang in (sys.argv[3:] or langs_of(spec)):
        miss = []; new = pick(spec, lang, miss); b = new.setdefault('book', {}); b['lang'] = lang; b.pop('langs', None)
        out = os.path.join(src_proj, lang); os.makedirs(out, exist_ok=True)
        for f in (ph, 'ai'):   # 照片、AI 配图目录链接回原项目
            if os.path.isdir(os.path.join(src_proj, f)) and not os.path.lexists(os.path.join(out, f)): os.symlink(os.path.join(src_proj, f), os.path.join(out, f))
        for f in (f'doc.{lang}.md', f'doc_{lang}.md'):   # 各语言的原文（原文核对用）
            if os.path.exists(os.path.join(src_proj, f)): import shutil; shutil.copy(os.path.join(src_proj, f), os.path.join(out, 'doc.md'))
        yaml.safe_dump(new, open(os.path.join(out, 'book.yaml'), 'w', encoding='utf-8'), allow_unicode=True, sort_keys=False, width=1000)
        print(f'→ {out}/book.yaml' + (f'  ERROR: 缺 {lang} 版本 {len(miss)} 处：' + '；'.join(miss[:12]) + ' → 在 book.yaml 对应位置补上 ' + lang + ': …' if miss else ''))
        bad += bool(miss)
    sys.exit(1 if bad else 0)
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
