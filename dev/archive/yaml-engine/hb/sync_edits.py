#!/usr/bin/env python3
"""把在线编辑页里的修改写回 book.yaml：python3 sync_edits.py <项目> edits.json
edits.json：在线编辑页数据库里的行（Claude 用 ArtifactData 读出来存成文件），两种写法都行：
  [ {path, lang, old, new, ...}, ... ]                       ← edits 集合
  {edits: [...], images: [{page, file, local, ...}, ...]}      ← 页面“导出修改”下载的文件；images 每行要有 local（下载到 photos/ 的新文件名）
  一个目录                                                      ← ArtifactData list 带 out_dir 存下来的：<目录>/edits/*.json、<目录>/images/*.json
做法：按 path（pages[4].cards[2].x）找到字段；多语言字段只改这一种语言；先核对现在的值和 old 一样（不一样 = 有人先改了，跳过并报告）；
在 book.yaml 原文里就地替换（保留注释和格式），换不了时才整份重写。写回后记进 .qa/edits_applied.json（原文核对把这些当用户认可的改动），
最后提示：bash hb/run.sh <项目> → 重新生成编辑页并发布到同一个地址。"""
import sys, os, re, json, time, yaml
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from i18n_pick import is_multi
P = os.path.abspath(sys.argv[1]); F = sys.argv[2]
Y = os.path.join(P, 'book.yaml')
if os.path.isdir(F):   # ArtifactData list 加 out_dir 存下来的目录：<dir>/edits/*.json、<dir>/images/*.json
    import glob
    rd = lambda c: [(lambda d: d.get('data', d))(json.load(open(f, encoding='utf-8'))) for f in sorted(glob.glob(os.path.join(F, c, '*.json')))]
    data = dict(edits=rd('edits'), images=rd('images'))
else: data = json.load(open(F, encoding='utf-8'))
edits = data if isinstance(data, list) else data.get('edits', [])
images = [] if isinstance(data, list) else data.get('images', [])
edits = [e for e in edits if e.get('status') != 'synced' and e.get('path')]
def keys(path):
    # 方括号表示列表下标；点号后的 '01' 仍是系列条目的字符串键。
    return [key if key else int(index) for key, index in re.findall(r'(?:^|\.)([^.\[\]]+)|\[(\d+)\]', path)]
def get(o, ks):
    for k in ks: o = o[k]
    return o
def setv(o, ks, v):
    for k in ks[:-1]: o = o[k]
    o[ks[-1]] = v
def norm(s): return re.sub(r'<[^>]+>|[​\s]+', '', str(s))
def page_region(text, i):
    """第 i 个页面在 book.yaml 文本里的起止位置"""
    m = re.search(r'(?m)^pages:\s*$', text)
    if not m: return 0, len(text)
    body = text[m.end():]; items = list(re.finditer(r'(?m)^(\s*)- ', body))
    if not items: return 0, len(text)
    ind = min(len(x.group(1)) for x in items); starts = [x.start() for x in items if len(x.group(1)) == ind]
    if i >= len(starts): return 0, len(text)
    a = m.end() + starts[i]; b = m.end() + starts[i + 1] if i + 1 < len(starts) else len(text)
    return a, b
def yq(s, ctx):
    """按原来的引号风格写新值"""
    if ctx == "'": return s.replace("'", "''")
    if ctx == '"': return json.dumps(s, ensure_ascii=False)[1:-1]
    if re.search(r"[:#,\[\]{}'\"&*!|>%@`]|^\s|\s$|^-", s): return "'" + s.replace("'", "''") + "'"
    return s
text = open(Y, encoding='utf-8').read(); spec = yaml.safe_load(text)
ok, skip, dumped = [], [], False
for e in edits:
    ks = keys(e['path']); lang = e.get('lang')
    try: v = get(spec, ks)
    except (KeyError, IndexError, TypeError): skip.append((e, '找不到这个字段（book.yaml 结构改过了）')); continue
    tks = ks + [k for k in v if str(k).lower() == str(lang).lower()][:1] if is_multi(v) else ks
    cur = get(spec, tks)
    new = str(e['new']).replace('\r', '').strip().replace('\n', '<br>')
    if isinstance(cur, (int, float)) and re.fullmatch(r'-?\d+(\.\d+)?', new): new = type(cur)(new)
    if norm(cur) == norm(new): ok.append(e); continue          # 已经是新值
    if norm(cur) != norm(e.get('old', cur)): skip.append((e, f'现在的值是“{str(cur)[:30]}”，和在线页改之前的“{str(e.get("old"))[:30]}”不一样（有人先改过）')); continue
    if re.search(r'<(b|strong|i|em)\b', str(cur)) and not re.search(r'<(b|strong|i|em)\b', str(new)): print(f'  注意：{e["path"]} 原来有加粗 / 斜体标记，在线改字后没了')
    i = ks[1] if ks[0] == 'pages' and len(ks) > 1 else None
    a, b = page_region(text, i) if i is not None else (0, len(text))
    seg = text[a:b]; raw = str(cur); hits = [m.start() for m in re.finditer(re.escape(raw), seg)]
    if len(hits) != 1:   # 原文里带引号转义的写法
        for alt in (raw.replace("'", "''"), json.dumps(raw, ensure_ascii=False)[1:-1]):
            hits = [m.start() for m in re.finditer(re.escape(alt), seg)]
            if len(hits) == 1: raw = alt; break
    replaced = False
    if len(hits) == 1:
        p0 = a + hits[0]; ctx = text[p0 - 1] if p0 > 0 and text[p0 - 1] in "'\"" and text[p0 + len(raw):p0 + len(raw) + 1] == text[p0 - 1] else ''
        cand = text[:p0] + yq(str(new), ctx) + text[p0 + len(raw):]
        try:
            if get(yaml.safe_load(cand), tks) == new: text = cand; replaced = True
        except Exception: pass
    if not replaced: setv(spec, tks, new); dumped = True
    else: spec = yaml.safe_load(text)
    ok.append(e)
# 换图：images 行要有 local（Claude 把 assets 里的图下载到 photos/ 后填的文件名）
mpf = [os.path.join(P, l, 'map.json') for l in os.listdir(P) if os.path.exists(os.path.join(P, l, 'map.json'))] + [os.path.join(P, 'map.json')]
img_ok = []
for r in images:
    if r.get('status') == 'synced': continue
    if not r.get('local'): skip.append((r, '换图没有 local：先把 asset 下载到 photos/，在这一行写上 local: 新文件名')); continue
    mp = next((json.load(open(f, encoding='utf-8')) for f in mpf if os.path.exists(f) and (not r.get('lang') or f'/{r["lang"]}/' in f or f == mpf[-1])), {})
    i = next((i for i, n, span in mp.get('pidx', []) if n <= int(r['page']) < n + span), None)
    a, b = page_region(text, i) if i is not None else (0, len(text))
    seg = text[a:b]
    if r['file'] not in seg: skip.append((r, f'第 {r["page"]} 页的 yaml 里找不到 {r["file"]}')); continue
    text = text[:a] + seg.replace(r['file'], r['local']) + text[b:]; spec = yaml.safe_load(text); img_ok.append(r)
if dumped:
    yaml.safe_dump(spec, open(Y, 'w', encoding='utf-8'), allow_unicode=True, sort_keys=False, width=1000)
    print('注意：有字段没法就地替换，book.yaml 整份重写了（注释会丢）')
else: open(Y, 'w', encoding='utf-8').write(text)
os.makedirs(os.path.join(P, '.qa'), exist_ok=True); A = os.path.join(P, '.qa', 'edits_applied.json')
log = json.load(open(A, encoding='utf-8')) if os.path.exists(A) else []
log += [dict(path=e['path'], lang=e.get('lang'), old=e.get('old'), new=e['new'], at=time.strftime('%Y-%m-%d %H:%M')) for e in ok]
log += [dict(image=r['file'], local=r['local'], page=r['page'], lang=r.get('lang'), at=time.strftime('%Y-%m-%d %H:%M')) for r in img_ok]
json.dump(log, open(A, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'写回 book.yaml：文字 {len(ok)} 处、照片 {len(img_ok)} 张；跳过 {len(skip)} 处')
for r, why in skip: print(f'  跳过 {r.get("path") or r.get("file")}：{why}')
print(f'下一步：bash {HERE}/run.sh {P} → python3 {HERE}/edit_page.py <语言子项目> → 发布到同一个地址；数据库里这些行标成 synced（或删掉）')
