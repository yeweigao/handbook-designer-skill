#!/usr/bin/env python3
"""原文核对（交付前 MISSING 必须为 0；有 MISSING 时退出码为 1）。
  python3 check_copy.py <project_dir>                 # 对照 <project_dir>/doc.md
  python3 check_copy.py <project_dir> 旧版/book.html   # 改版时：对照上一版，找出被弄丢的文字（如签名栏、姓名栏）
MISSING：参照文本里的句子没出现在成品里（逐条给出）。
ORDER  ：句子都在，但先后顺序和参照文本不同（给出页码；可能是有意调整，逐条确认）。
EXTRA  ：成品里不在参照文本中的行 —— 自创句子要删。页眉、页脚、图注、小标签、填写提示等
         引擎标记为“装饰”的文字不列入 EXTRA，只计数。
页码 artifacts（页脚「02 / 23」、居中短数字）不算正文：extract.py 识别后写进 .qa/artifacts.txt，
         不列入 MISSING / EXTRA（成品用手册自动页码）。
中文与西文原文都支持（按句号/问号/叹号与换行切分）。
ADAPT  ：项目里有 adapt.yaml 时，声明过的“去掉编号前缀 / 版本标记（strip）、整行不进册子（omit）”不算 MISSING，明细写进 .qa/adapt-report.md；
         声明了却没命中、或声明去掉的文字仍印在成品里，输出 ADAPT WARN（写法见 references/adaptation.md「按产物适配」）。"""
import sys,os,re,html
P=os.path.abspath(sys.argv[1] if len(sys.argv)>1 else '.')
REF=sys.argv[2] if len(sys.argv)>2 else os.path.join(P,'doc.md')
STRIP=r'[｜→•✓✗▶☐\s—·\-–：:，,。.！!？?；;（）()“”"「」『』/、《》\'‘’\*\\#|>_＿]'   # 含下划线/全角填空线：原文的填空在成品里是书写线
def txt(s,drop_deco=False):
    s=re.sub(r'<style.*?</style>|<script.*?</script>|<title>.*?</title>','',s,flags=re.S)
    if drop_deco: s=re.sub(r'<(\w+)[^>]*data-deco[^>]*>.*?</\1>','',s,flags=re.S)
    s=re.sub(r'<br\s*/?>','\n',s); s=re.sub(r'</(p|div|span|section|li|td|th|figcaption|h\d)>','\n',s); s=re.sub(r'<[^>]+>','',s); return html.unescape(s).replace('\u200b','')
norm=lambda s:re.sub(STRIP,'',s).lower()
raw=open(os.path.join(P,'book.html'),encoding='utf-8').read()
pages=re.findall(r'<section class="page[^"]*"[^>]*data-n="(\d+)"[^>]*>(.*?)</section>',raw,flags=re.S)
# 整本的规范化文本 + 每个字符属于第几页
N=''; owner=[]
for n,body in pages:
    t=norm(txt(body)); N+=t; owner+= [int(n)]*len(t)
book_deco_free=txt(raw,drop_deco=True); n_deco=len(re.findall(r'data-deco',raw))
ref=open(REF,encoding='utf-8').read()
ref=re.sub(r'<!--.*?-->','',ref,flags=re.S); ref=re.sub(r'(?m)^\s*(!\[[^\]]*\]\([^)]*\)|<img\b[^>]*>)\s*$','',ref)   # extract.py 的页码/图片注释、Markdown 图片不算正文
if REF.endswith('.html'): ref=txt(ref)
_ART=set()   # 页码 artifacts（extract.py 写进 .qa/artifacts.txt）：页脚页码不当正文，从必含文本里排除（成品用手册自动页码）
for _f in (os.path.join(P,'.qa','artifacts.txt'),os.path.join(os.path.dirname(P),'.qa','artifacts.txt')):
    if not os.path.exists(_f): continue
    for _l in open(_f,encoding='utf-8'):
        _l=_l.strip()
        if _l and not _l.startswith('#'): _ART.add(_l.split('：',1)[-1].strip())
    break
def _noise(l):   # 页码样式行（「02 / 23」页脚、居中短数字）：原资料的页码，成品用手册自动页码
    t=re.sub(r'^(#{1,3}\s*|[-*•▶✓]\s+|\d+[.、)]\s+)','',l.strip()).strip()
    return t in _ART or bool(re.fullmatch(r'\d{1,2}\s*/\s*\d{1,2}|\d{1,2}',t))
ref='\n'.join(l for l in ref.splitlines() if not _noise(l))
import json as _j   # 在线编辑页里用户改过、已写回 book.yaml 的文字（sync_edits.py 记的）：当作用户认可的改动，参照文本跟着换
for _f in (os.path.join(P,'.qa','edits_applied.json'),os.path.join(os.path.dirname(P),'.qa','edits_applied.json')):
    if not os.path.exists(_f): continue
    for _e in _j.load(open(_f,encoding='utf-8')):
        if _e.get('old') and _e.get('new') and (not _e.get('lang') or _e['lang']==os.path.basename(P) or _f.startswith(P)):
            _o,_n=[re.sub(r'<br\s*/?>','\n',str(x)) for x in (_e['old'],_e['new'])]
            ref=ref.replace(_o,_n) if _o in ref else ref.replace(re.sub(r'\s+',' ',_o),_n)
    break
# 版面适配声明（项目根目录 adapt.yaml；写法见 references/adaptation.md「按产物适配」）：
#   strip：去掉匹配到的部分（编号前缀「亮点一：高端品质」→「高端品质」；标题末尾的「（终稿v3）」）；omit：整行不进册子（备注、批注、给设计的指示）。
# 声明过的不算 MISSING，全部写进 .qa/adapt-report.md 交给用户确认；没声明的照旧报 MISSING。对照旧版 .html 时不套用。
import collections
ADAPT_S=[]; ADAPT_O=[]; ADAPT_W=[]
_af=next((os.path.join(_d,'adapt.yaml') for _d in (P,os.path.dirname(P)) if os.path.exists(os.path.join(_d,'adapt.yaml'))),None) if not REF.endswith('.html') else None
if _af:
    import yaml as _y
    try:
        _A=_y.safe_load(open(_af,encoding='utf-8')) or {}
        _sr=[(str(_e['match']),str(_e.get('why',''))) for _e in (_A.get('strip') or [])]
        _or=[]
        for _e in (_A.get('omit') or []):
            if _e.get('match'): _or.append(('match',str(_e['match']),str(_e.get('why',''))))
            else:
                if len(norm(str(_e['text'])))<4: raise ValueError('omit 的 text 太短（'+str(_e['text'])+'），会误伤别的行：写长一点，或改用 match 正则')
                _or.append(('text',str(_e['text']),str(_e.get('why',''))))
        for _p in [x[0] for x in _sr]+[x[1] for x in _or if x[0]=='match']:
            if not _p.strip(): raise ValueError('有一条正则是空的')
            re.compile(_p)
    except Exception as _ex:
        print(f'ADAPT ERROR: {_af} 读不了或格式不对（{type(_ex).__name__}: {_ex}）→ strip 每条要有 match（正则），omit 每条要有 text 或 match'); sys.exit(1)
    _hs=collections.Counter(); _ho=collections.Counter(); _out=[]
    for _l in ref.split('\n'):
        _m=re.match(r'^(\s*(?:#{1,3}\s+|[-*•▶✓]\s+|\d+[.、)]\s+)?(?:\*\*)?)(.*)$',_l); _lead,_body=_m.group(1),_m.group(2); _kb=norm(_body); _gone=False
        for _i,(_kd,_pt,_w) in enumerate(_or):
            if (_kd=='match' and re.match(_pt,_body)) or (_kd=='text' and _kb.startswith(norm(_pt))):
                _ho[_i]+=1; ADAPT_O.append((_body.strip(),_w)); _gone=True; break
        if _gone: continue
        for _i,(_pt,_w) in enumerate(_sr):
            _nb=re.sub(_pt,'',_body,count=1)   # 匹配到的部分被去掉：前缀用 ^ 开头，后缀（标题末尾的版本标记）用 $ 结尾；剥完为空的行不剥
            if _nb!=_body and norm(_nb):
                _hs[_i]+=1; ADAPT_S.append((_body.strip(),_nb.strip(),_w)); _l=_lead+_nb; break
        _out.append(_l)
    ref='\n'.join(_out)
    for _i,(_pt,_w) in enumerate(_sr):
        if not _hs[_i]: ADAPT_W.append(f'strip「{_pt}」没有命中任何一行 → 检查正则（行首的列表符号、# 和粗体已忽略；前缀要写 ^，后缀要写 $），或删掉这条')
    for _i,(_kd,_pt,_w) in enumerate(_or):
        if not _ho[_i]: ADAPT_W.append(f'omit「{_pt}」没有命中任何一行 → 检查写法（text 是行首文字，忽略标点空格；match 是行首正则），或删掉这条')
    for _o,_n,_w in ADAPT_S:
        if len(norm(_o))>=4 and norm(_o) in N: ADAPT_W.append(f'声明了去掉前缀，成品里却还印着「{_o[:30]}」→ 前缀不印，只留「{_n[:20]}」')
    for _o,_w in ADAPT_O:
        if len(norm(_o))>=6 and norm(_o) in N: ADAPT_W.append(f'声明了不进册子，成品里却还有「{_o[:30]}」→ 从 book.yaml 删掉这段，或从 adapt.yaml 去掉这条声明')
CJK=len(re.findall(r'[一-鿿]',ref))>len(re.findall(r'[A-Za-z]',ref))/4   # 原文以中日韩文字为主？
D=norm(re.sub(r'[•✓✗→▶☐｜]','',ref))
segs=[]
for seg in re.split(r'\n|▶|\||(?<=[。！？])|(?<=[.!?])\s+',ref):
    seg=re.sub(r'(\\_){2,}|_{2,}|＿{2,}','  ',seg)   # 填空线 → 分段：“姓名：＿＿　班级：＿＿” 拆成两个标签分别核对
    seg=re.sub(r'\*\*|\\_|\\|[•✓✗→☐｜#>]','',seg).strip()
    for part in re.split(r'\s{2,}|(?<=[。！？；])',seg):
        k=norm(part)
        if len(k)>1: segs.append((part.strip(),k))
miss=[]; found=[]; cur=0
for part,k in segs:
    i=N.find(k,cur)                 # 优先找“上一句之后”的出现位置（同一词可能在前文被引用过）
    if i<0: i=N.find(k)
    if i<0: miss.append(part); continue
    if len(k)>=4 and N.count(k)==1:  # 很短或在成品里出现不止一次的片段（目录、章节页摘要），不参与顺序判断
        found.append((i,part))
        if i>=cur: cur=i+len(k)
# 顺序：最长递增子序列之外的片段 = 位置“倒退”的片段
pos=[owner[i] for i,_ in found]; L=len(pos); best=[1]*L; prev=[-1]*L   # 按页比较：同一页里的先后由版式决定（标题、正文栈的排法），只查跨页的倒退
for a in range(L):
    for b in range(a):
        if pos[b]<=pos[a] and best[b]+1>best[a]: best[a]=best[b]+1; prev[a]=b
keep=set(); a=max(range(L),key=lambda x:best[x]) if L else -1
while a>=0: keep.add(a); a=prev[a]
order=[(pos[i],found[i][1]) for i in range(L) if i not in keep]
extra=[]
for line in dict.fromkeys(l.strip() for l in book_deco_free.split('\n')):
    if not line: continue
    if CJK:   # 中文原文：先整行比对；不在原文时再去掉英文字母串比对
        if norm(line) in D: continue
        k=norm(re.sub(r'[A-Za-z][A-Za-z&; .]{2,}','',line))
        if len(k)>=4 and not re.fullmatch(r'[a-z0-9&;. ]+',k) and k not in D: extra.append(line)
    else:
        k=norm(line)
        if len(k)>=8 and k not in D: extra.append(line)
print(f'MISSING {len(miss)}（参照：{os.path.basename(REF)}）'); [print('  MISSING:',m) for m in miss]
print(f'ORDER {len(order)}（顺序与参照文本不同；若是有意挪动请在回复里说明）'); [print(f'  ORDER: 第{p}页 {t}') for p,t in order[:40]]
print(f'EXTRA {len(extra)}（不在参照文本中的正文行：自创句子必须删；另有 {n_deco} 处页眉/页脚/图注/小标签/填写提示未列出）'); [print('  EXTRA:',e) for e in extra[:80]]
if _af:
    print(f'ADAPT strip {len(ADAPT_S)} omit {len(ADAPT_O)}（按 adapt.yaml：去掉编号或版本标记 {len(ADAPT_S)} 行、未进册子 {len(ADAPT_O)} 行；明细 .qa/adapt-report.md，交付时列给用户）')
    for _w in ADAPT_W: print('ADAPT WARN:',_w)
    _q=os.path.join(P,'.qa'); os.makedirs(_q,exist_ok=True); _c=lambda s:str(s).replace('|','/').replace('\n',' ')
    _rp=['# 适配报告（check_copy 自动生成，依据 adapt.yaml）','','交付时把这里列给用户；要放回的，删掉 adapt.yaml 里对应的条目再重建。','',
         f'## 去掉的编号 / 标签 / 版本标记（{len(ADAPT_S)} 行）','','| 原文 | 成品采用 | 原因 |','|---|---|---|']
    _rp+=[f'| {_c(a)} | {_c(b)} | {_c(w)} |' for a,b,w in ADAPT_S]
    _rp+=['',f'## 未进册子的内容（{len(ADAPT_O)} 行）','','| 原文 | 原因 |','|---|---|']
    _rp+=[f'| {_c(a)} | {_c(w)} |' for a,w in ADAPT_O]
    open(os.path.join(_q,'adapt-report.md'),'w',encoding='utf-8').write('\n'.join(_rp)+'\n')
sys.exit(1 if miss else 0)
