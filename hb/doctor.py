#!/usr/bin/env python3
"""读 QA 结果，给出“下一步改 book.yaml 的哪一项”。 python3 doctor.py <project_dir>"""
import sys,os,json,re
P=os.path.abspath(sys.argv[1] if len(sys.argv)>1 else '.'); Q=os.path.join(P,'.qa')
ov=json.load(open(os.path.join(Q,'overflow.json'))) if os.path.exists(os.path.join(Q,'overflow.json')) else []
fails=[l for l in open(os.path.join(Q,'contrast.txt')).read().splitlines() if re.match(r'p\d+ ',l)] if os.path.exists(os.path.join(Q,'contrast.txt')) else []
ok=True
for o in ov:
    ok=False; pg=o[0]
    if o[1]=='region': print(f'[溢出] 第{pg}页 文字区多出 {o[2]}px（“{o[3]}…”）→ 依次尝试：1) 把 fill 的最小值调小或删掉多余 lines；2) 减少 write 里的 field/lines；3) T 版把 split 调小 30–60；4) 把一部分内容挪到相邻页（不要删原文）')
    elif o[1]=='step': print(f'[溢出] 第{pg}页 任务“{o[3]}”内部多出 {o[2]}px → 减少该 step 的 write 行数，或给它加 grow: true')
    elif o[1]=='collide': print(f'[重叠] 第{pg}页 两个文字区互相压住（{o[3]}，重叠 {o[2]}px）→ 海报页：减少 top/bottom 的内容或调 top_y/bottom_y；T 版：on_photo 太长就加大 split；跨页：把部分内容挪到另一页')
    else: print(f'[出界] 第{pg}页 “{o[2]}” 超出页面 → 缩短该行/换行，或减小 display 的 size')
pgs={}
for l in fails: pgs.setdefault(int(l.split()[0][1:]),[]).append(l)
for pg,ls in sorted(pgs.items()):
    ok=False
    print(f'[看不清] 第{pg}页 {len(ls)} 处对比度不足，例：{ls[0]} → 照片上的白字：把文字挪到照片较暗/较简单的区域（改 focus/target），或换图；纸面上的深色字：T 版加大 split / HOLE 换 window 位置，让字完全落在纸面上；若是彩色小标签（kicker、编号、kv 左列）在纯纸面上也不过，说明 book.colors 的 G/OCH 太浅 → 加深一档（对纸色 ≥5.5:1）')
cc=os.path.join(Q,'copy.txt'); miss=None
if os.path.exists(cc):
    m=re.search(r'MISSING (\d+)',open(cc,encoding='utf-8').read()); miss=int(m.group(1)) if m else None
    if miss: ok=False; print(f'[缺字] 原文有 {miss} 处没出现在成品里（见上面的 MISSING 列表）→ 从 doc.md 复制补回；表格的表头/行名丢了时检查 table 块写法')
if ok: print('GATE: PASS —— 溢出 0、重叠 0、对比度 FAIL 0' + ('、MISSING 0' if miss==0 else '（没有 doc.md，未做原文核对）') + '。这只是自动检查，接下来逐页看 .qa/review_*.jpg')
else: print('GATE: FAIL —— 按上面的提示改 book.yaml 后重跑'); sys.exit(1)
