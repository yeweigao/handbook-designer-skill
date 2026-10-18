#!/usr/bin/env python3
"""导出门禁。
  python3 gate.py write <project> PASS|FAIL [langs…]   run.sh 构建完写 .qa/gate.json（结果 + 输入指纹）
  python3 gate.py check <project>                     export.sh 导出前查：没跑过 / 没通过 / 跑完之后又改了东西 → 退出 1
指纹 = book.yaml + brief.md + doc*.md + 照片目录（文件名、大小、修改时间）。改了任何一个都要重新 run.sh 才能导出正式版；
只想先给人看一眼：bash export.sh <project> <名> --draft（每页打“草稿 DRAFT”水印）。"""
import sys, os, json, glob, hashlib, time, yaml
cmd, P = sys.argv[1], os.path.abspath(sys.argv[2]); G = os.path.join(P, '.qa', 'gate.json')
def fp(P):
    hsh = hashlib.sha1()
    for f in ['book.yaml', 'brief.md'] + sorted(os.path.basename(x) for x in glob.glob(os.path.join(P, 'doc*.md'))):
        q = os.path.join(P, f)
        if os.path.exists(q): hsh.update(f.encode()); hsh.update(open(q, 'rb').read())
    try: ph = (yaml.safe_load(open(os.path.join(P, 'book.yaml'), encoding='utf-8')) or {}).get('book', {}).get('photos', 'photos')
    except Exception: ph = 'photos'
    ph = ph if isinstance(ph, str) else 'photos'
    for d in (ph, 'ai'):
        for root, _, fs in os.walk(os.path.join(P, d), followlinks=True):
            for f in sorted(fs):
                st = os.stat(os.path.join(root, f)); hsh.update(f'{f}{st.st_size}{int(st.st_mtime)}'.encode())
    return hsh.hexdigest()[:16]
if cmd == 'write':
    os.makedirs(os.path.dirname(G), exist_ok=True)
    json.dump(dict(result=sys.argv[3], at=time.strftime('%Y-%m-%d %H:%M:%S'), fp=fp(P), langs=sys.argv[4:]), open(G, 'w', encoding='utf-8'), ensure_ascii=False)
    sys.exit(0)
if cmd == 'check':
    up = os.path.dirname(P); UG = os.path.join(up, '.qa', 'gate.json')
    if not os.path.exists(G) and os.path.exists(UG) and os.path.basename(P) in json.load(open(UG, encoding='utf-8')).get('langs', []):
        P, G = up, UG   # 多语言子项目（<project>/en）：看上层的门禁
    if not os.path.exists(G): print('导出门禁：还没跑过 run.sh → 先 bash hb/run.sh ' + P); sys.exit(1)
    g = json.load(open(G, encoding='utf-8'))
    if g.get('result') != 'PASS': print(f'导出门禁：上一次构建（{g.get("at")}）是 GATE FAIL → 按 doctor 的提示改完、run.sh 通过后再导出；只想先给人看：加 --draft'); sys.exit(1)
    if g.get('fp') != fp(P): print(f'导出门禁：{g.get("at")} 构建通过之后，book.yaml / 原文 / 照片又改过 → 重新 bash hb/run.sh {P}，通过后再导出'); sys.exit(1)
    print(f'导出门禁：{g.get("at")} 构建通过，之后没有改动 ✓'); sys.exit(0)
