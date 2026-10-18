#!/usr/bin/env python3
"""原文核对（交付前 MISSING 必须为 0；有 MISSING 时退出码为 1）。
  python3 check_copy.py <project_dir>                 # 对照 <project_dir>/doc.md
  python3 check_copy.py <project_dir> 旧版/book.html   # 改版时：对照上一版，找出被弄丢的文字（如签名栏、姓名栏）
MISSING：参照文本里的句子没出现在成品里（逐条给出）。
ORDER  ：句子都在，但先后顺序和参照文本不同（给出页码；可能是有意调整，逐条确认）。
EXTRA  ：成品里不在参照文本中的行 —— 自创句子要删。页眉、页脚、图注、小标签、填写提示等
         引擎标记为“装饰”的文字不列入 EXTRA，只计数。
中文与西文原文都支持（按句号/问号/叹号与换行切分）。"""
import sys,os,re,html
P=os.path.abspath(sys.argv[1] if len(sys.argv)>1 else '.')
REF=sys.argv[2] if len(sys.argv)>2 else os.path.join(P,'doc.md')
STRIP=r'[｜→•✓✗▶☐\s—·\-–：:，,。.！!？?；;（）()“”"「」『』/、《》\'‘’\*\\#|>_＿]'   # 含下划线/全角填空线：原文的填空在成品里是书写线
def txt(s,drop_deco=False):
    s=re.sub(r'<style.*?</style>|<script.*?</script>|<title>.*?</title>','',s,flags=re.S)
    if drop_deco: s=re.sub(r'<(\w+)[^>]*data-deco[^>]*>.*?</\1>','',s,flags=re.S)
    s=re.sub(r'<br\s*/?>','\n',s); s=re.sub(r'</(p|div|span|section|li|td|th|h\d)>','\n',s); s=re.sub(r'<[^>]+>','',s); return html.unescape(s).replace('\u200b','')
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
import json as _j   # 在线编辑页里用户改过、已写回 book.yaml 的文字（sync_edits.py 记的）：当作用户认可的改动，参照文本跟着换
for _f in (os.path.join(P,'.qa','edits_applied.json'),os.path.join(os.path.dirname(P),'.qa','edits_applied.json')):
    if not os.path.exists(_f): continue
    for _e in _j.load(open(_f,encoding='utf-8')):
        if _e.get('old') and _e.get('new') and (not _e.get('lang') or _e['lang']==os.path.basename(P) or _f.startswith(P)):
            _o,_n=[re.sub(r'<br\s*/?>','\n',str(x)) for x in (_e['old'],_e['new'])]
            ref=ref.replace(_o,_n) if _o in ref else ref.replace(re.sub(r'\s+',' ',_o),_n)
    break
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
sys.exit(1 if miss else 0)
