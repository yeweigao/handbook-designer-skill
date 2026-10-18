#!/usr/bin/env python3
"""读 QA 结果，给出“下一步改 book.yaml 的哪一项”。 python3 doctor.py <project_dir>"""
import sys,os,json,re
P=os.path.abspath(sys.argv[1] if len(sys.argv)>1 else '.'); Q=os.path.join(P,'.qa')
ov=json.load(open(os.path.join(Q,'overflow.json'), encoding='utf-8')) if os.path.exists(os.path.join(Q,'overflow.json')) else []
fails=[l for l in open(os.path.join(Q,'contrast.txt'), encoding='utf-8').read().splitlines() if re.match(r'p\d+ ',l)] if os.path.exists(os.path.join(Q,'contrast.txt')) else []
ok=True; nH=0; tips=[]   # H = 拦门禁的硬伤（nH 计数）；S = 只报告的提示（cn-fit / cn-small ≥120px / 留白），不算失败
for o in ov:
    pg=o[0]
    if o[1]=='cn-fit':   # 标题太长：渲染正常，只是提示
        tips.append(f'[标题太长] 第{pg}页 大标题“{o[3]}”缩到最小字号还放不下（不算失败，只是提示）→ 缩短 title（中文 ≤12 字，英文 ≤5 个词），细节写进 en / intro'); continue
    if o[1]=='cn-small':
        if o[2]<120:   # <120px 是真实视觉事故（照片带被挤没），拦门禁
            nH+=1; ok=False; print(f'[图太小] 第{pg}页 有图片位被文字挤到只剩 {o[2]}px 高 → 文字太多：减少条目或拆页；或去掉这一页的图')
        else:
            tips.append(f'[图太小] 第{pg}页 有图片位被文字挤到只剩 {o[2]}px 高（不算失败，只是提示）→ 文字还能再压：减少条目或拆页；或去掉这一页的图')
        continue
    nH+=1; ok=False
    if o[1]=='region': print(f'[溢出] 第{pg}页 文字区多出 {o[2]}px（“{o[3]}…”）→ 依次尝试：1) 把 fill 的最小值调小或删掉多余 lines；2) 减少 write 里的 field/lines；3) T 版把 split 调小 30–60；4) 把一部分内容挪到相邻页（不要删原文）')
    elif o[1]=='recipe': print(f'[溢出] 第{pg}页 内容版式放不下，已自动缩字到下限仍多出 {o[2]}px（“{o[3]}…”）→ 依次尝试：1) 拆成两页，用同一个版式（引擎自动换镜像）；2) 卡片/条目多的换 GRID，图多字多的换 TWO；3) 去掉 intro 或 stats；不要删原文')
    elif o[1]=='step': print(f'[溢出] 第{pg}页 任务“{o[3]}”内部多出 {o[2]}px → 减少该 step 的 write 行数，或给它加 grow: true')
    elif o[1]=='collide': print(f'[重叠] 第{pg}页 两个文字区互相压住（{o[3]}，重叠 {o[2]}px）→ 海报页：减少 top/bottom 的内容或调 top_y/bottom_y；T 版：on_photo 太长就加大 split；跨页：把部分内容挪到另一页')
    elif o[1]=='cn-over': print(f'[溢出] 第{pg}页 文字超出版心 {o[2]}px（“{o[3]}…”）→ 这一页内容太多：1) 拆成两页，用同一个版式（自动换镜像）；2) 条目多的换 GRID，长文换 TWO（columns）；3) 去掉 intro / stats。不要删原文')
    elif o[1]=='cn-in': print(f'[溢出] 第{pg}页 标题区超出它的色块 {o[2]}px（“{o[3]}…”）→ 标题或导语太长：缩短 title（≤12 字 / 5 个英文词），intro 挪进正文，或拆页')
    elif o[1]=='cn-band': print(f'[溢出] 第{pg}页 正文压进了底部色带 {o[2]}px（“{o[3]}…”）→ 这一页内容太多：拆成两页；或把 notes 挪到下一页、去掉 intro')
    elif o[1]=='cn-collide': print(f'[重叠] 第{pg}页 两组文字互相压住（{o[3]}，{o[2]}px）→ 这一页内容太多：拆页，或去掉 intro / stats / quote 之一')
    elif o[1]=='cn-row': print(f'[溢出] 第{pg}页 一行条目放不下（“{o[3]}…”多出 {o[2]}px）→ 条目文字太长：每条说明 ≤32 字 / 20 个英文词（book.body: 14 时 ≤40 字 / 25 词），或减少条目、拆页')
    elif o[1]=='cn-imgarea':   # 主图可见面积不足（fill.js 报）：真事故，拦门禁
        d=f'（{o[3]}）' if o[3] else ''
        print(f'[图太小] 第{pg}页 主图可见面积不足{d} → 减少该页文字/拆页，或换图多的版式（MIX / STAGGER）；不要删原文')
    elif o[1]=='cn-deco': print(f'[重叠] 第{pg}页 装饰大字压到了文字（{o[3]}，{o[2]}px）→ 缩短标题；或写 count: false / deco: false 去掉大字；或换镜像 mirror: true')
    else: print(f'[出界] 第{pg}页 “{o[2]}” 超出页面 → 缩短该行/换行，或减小 display 的 size')
pgs={}
for l in fails: pgs.setdefault(int(l.split()[0][1:]),[]).append(l)
for pg,ls in sorted(pgs.items()):
    ok=False; nH+=1
    print(f'[看不清] 第{pg}页 {len(ls)} 处对比度不足，例：{ls[0]} → 照片上的白字：把文字挪到照片较暗/较简单的区域（改 focus/target），或换图；纸面上的深色字：T 版加大 split / HOLE 换 window 位置，让字完全落在纸面上；若是彩色小标签（kicker、编号、kv 左列）在纯纸面上也不过，说明 book.colors 的 G/OCH 太浅 → 加深一档（对纸色 ≥5.5:1）')
b3=os.path.join(Q,'b3.json')   # A4 印刷：小于 8pt（10.6px）的字印出来看不清
small=[b for b in (json.load(open(b3, encoding='utf-8')) if os.path.exists(b3) else []) if b.get('fs',99)<10.6]
if small:
    ok=False; nH+=1; pgs_=sorted({b['pg']+1 for b in small})
    print(f'[字太小] {len(small)} 处文字小于 8pt（A4 印刷看不清），在第 {"、".join(map(str,pgs_[:8]))} 页，例：“{small[0]["t"]}” {small[0]["fs"]:.1f}px → 不要手写小于 11px 的 size；内容版式里字多被自动缩小到下限时，拆页或换 GRID / TWO')
sp=os.path.join(Q,'sparse.json')
for pg,r in (json.load(open(sp, encoding='utf-8')) if os.path.exists(sp) else []):   # 不算失败，只是提示
    tips.append(f'[留白] 第{pg}页 内容只占到版面的 {r*100:.0f}% → 宣传册里显得空：给这页写 image（补位图带，吃掉剩余高度）；或和相邻页合并；或换成图更多的版式（MIX / STAGGER）。指南、任务册可以不管')
wp=os.path.join(Q,'warn.txt')
for w in (open(wp, encoding='utf-8').read().splitlines() if os.path.exists(wp) else []):   # hb.py 的构建警告（如无图页丢图）：只报告，不算失败
    if w.strip(): tips.append('[构建提示] ' + w.strip())
cc=os.path.join(Q,'copy.txt'); miss=None
if os.path.exists(cc):
    m=re.search(r'MISSING (\d+)',open(cc,encoding='utf-8').read()); miss=int(m.group(1)) if m else None
    if miss: ok=False; nH+=1; print(f'[缺字] 原文有 {miss} 处没出现在成品里（见上面的 MISSING 列表）→ 从 doc.md 复制补回；表格的表头/行名丢了时检查 table 块写法')
# 美化路线（book.frozen: true）：文字冻结——顺序不能动、不能加正文；PPT / PDF 原文一页对一页
import yaml as _y
try:
    _bk=(_y.safe_load(open(os.path.join(P,'book.yaml'),encoding='utf-8')) or {}).get('book',{})
except Exception: _bk={}
if _bk.get('frozen') and os.path.exists(cc):
    ct=open(cc,encoding='utf-8').read()
    no=int((re.search(r'ORDER (\d+)',ct) or [0,0])[1]); ne=int((re.search(r'EXTRA (\d+)',ct) or [0,0])[1])
    if no or ne: ok=False; nH+=1; print(f'[改动了原文] 美化模式（book.frozen: true）文字冻结：ORDER {no}、EXTRA {ne} 都必须是 0 → 照原文顺序排；不在原文里的正文删掉（页眉、页脚、图注这类装饰不算）')
    dm=os.path.join(P,'doc.md'); src_pages=len(re.findall(r'<!--\s*第\s*\d+\s*页',open(dm,encoding='utf-8').read())) if os.path.exists(dm) else 0
    pt=os.path.join(P,'plan.txt'); have=sum(2 if re.search(r'^\d+-\d+',l) else 1 for l in open(pt, encoding='utf-8').read().splitlines() if l.strip()) if os.path.exists(pt) else 0
    if src_pages and have!=src_pages: ok=False; nH+=1; print(f'[页数不对应] 美化模式一页对一页：原文 {src_pages} 页，成品 {have} 页 → 拆页、合页、删页都会退出美化模式；确实要改结构，先问用户，改走 new 路线（去掉 frozen）')
for t in tips: print(t)   # 提示级（cn-fit / cn-small ≥120px / 留白）：不算失败，只是提示
if ok: print('GATE: PASS —— 溢出 0、重叠 0、对比度 FAIL 0' + ('、MISSING 0' if miss==0 else '（没有 doc.md，未做原文核对）') + f'、提示 {len(tips)} 条。这只是自动检查，接下来逐页看 .qa/review_*.jpg')
else: print(f'GATE: FAIL —— 硬伤 {nH} 处、提示 {len(tips)} 条 → 按上面的提示改 book.yaml 后重跑'); sys.exit(1)
