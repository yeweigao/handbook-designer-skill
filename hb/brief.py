#!/usr/bin/env python3
"""图片需求单：把版式里的 AI 配图位（image / figure / product 写 ai:编号）整理成一份可以直接拿去生图的清单。
  python3 hb/brief.py <project_dir>        （run.sh 构建后自动调用）→ <project_dir>/image_brief.md

每个图位给出：用在哪页、做什么用、要多大（按版式实际尺寸算：电子版 2 倍、印刷 300dpi）、比例、
文字会压在图的哪些区域（取自实际渲染的文字位置——这些区域要暗/亮且干净）、明暗、参考素材、提示词。
提示词与美术方向写在项目的 ai_images.yaml（见 SKILL.md“AI 配图”）；没写的图位只给尺寸与安全区，提示词留空。
生成好的图存成 photos/ai_<编号>.png（或 .jpg/.webp），重跑 run.sh 自动替换占位图。
"""
import os, sys, json
import yaml

W, H = 794, 1123
RATIOS = [('1:1', 1.0), ('2:3 竖', 2 / 3), ('3:2 横', 1.5), ('3:4 竖', .75), ('4:3 横', 4 / 3), ('9:16 竖', 9 / 16), ('16:9 横', 16 / 9)]

def zones(boxes, x0, y0, w, h):
    """把落在图上的文字框聚成几块，返回相对图片的百分比区域"""
    bs = sorted([b for b in boxes if b['x'] + b['w'] > x0 and b['x'] < x0 + w and b['y'] + b['h'] > y0 and b['y'] < y0 + h], key=lambda b: b['y'])
    cl = []
    for b in bs:
        r = [b['x'], b['y'], b['x'] + b['w'], b['y'] + b['h']]
        if cl and r[1] - cl[-1][3] < 46 and not (r[0] > cl[-1][2] + 60 or r[2] < cl[-1][0] - 60):
            c = cl[-1]; cl[-1] = [min(c[0], r[0]), min(c[1], r[1]), max(c[2], r[2]), max(c[3], r[3])]
        else: cl.append(r)
    pct = lambda v, o, s: max(0, min(100, round((v - o) / s * 100)))
    return [f'横 {pct(c[0], x0, w)}–{pct(c[2], x0, w)}%、竖 {pct(c[1], y0, h)}–{pct(c[3], y0, h)}%' for c in cl]

def main(P):
    sp = os.path.join(P, '.qa', 'ai_slots.json')
    if not os.path.exists(sp): return
    S = json.load(open(sp, encoding='utf-8')); slots = S['slots']
    if not slots:
        if os.path.exists(os.path.join(P, 'image_brief.md')): os.remove(os.path.join(P, 'image_brief.md'))
        return
    boxes = json.load(open(os.path.join(P, '.qa', 'b3.json'))) if os.path.exists(os.path.join(P, '.qa', 'b3.json')) else []
    spec = yaml.safe_load(open(os.path.join(P, 'ai_images.yaml'), encoding='utf-8')) if os.path.exists(os.path.join(P, 'ai_images.yaml')) else {}
    imgs = spec.get('images', {}) or {}; suffix = (spec.get('style') or '').strip(); neg = (spec.get('negative') or '').strip()
    seen = {}; out = ['# 图片需求单（hb/brief.py 按版式自动生成，重跑 run.sh 会更新）', '']
    if spec.get('direction'): out += ['## 美术方向（全书统一）', spec['direction'].strip(), '']
    if suffix: out += [f'**通用风格提示词**（每条提示词末尾都要带上）：`{suffix}`', '']
    if neg: out += [f'**避免**：`{neg}`', '']
    out += ['生成后存成 `photos/ai_<编号>.png`（或 .jpg / .webp），重跑 `run.sh` 自动替换占位图。图里不要放文字、logo、水印；版面上的字由排版引擎负责。', '',
            '| 编号 | 页 | 用途 | 状态 | 电子版尺寸 | 比例 |', '|---|---|---|---|---|---|']
    det = []
    for s in slots:
        k = s['id']
        if k in seen: seen[k]['page'] = f"{seen[k]['page']}、{s['page']}"; continue
        seen[k] = s; cw, ch = s['css']
        if s['where'] == '版式图片':
            bx = s.get('box', [0, 0, 1, 1]); vis_w, vis_h = cw * (bx[2] - bx[0]), H * (bx[3] - bx[1])
            px = (cw * 2, H * 2); pr = (round(cw * 3.125), round(H * 3.125))
        else:
            px = (cw * 2, ch * 2); pr = (round(cw * 3.125), round(ch * 3.125))
        ar = px[0] / px[1]; near = min(RATIOS, key=lambda r: abs(r[1] - ar))[0]
        it = imgs.get(k, {}) or {}
        out.append(f"| ai:{k} | {s['page']} | {it.get('use', s['where'])} | {'✅ 已有 ' + s['done'] if s.get('done') else '⏳ 待生成'} | {px[0]}×{px[1]} | {ar:.2f}（最接近 {near}）|")
        d = [f"### ai:{k} — {it.get('use', s['where'])}", '',
             f"- 位置：第 {s['page']} 页 · {s['where']}" + ('（跨页满版）' if cw > W + 10 else ''),
             f"- 文件名：`photos/ai_{k}.png`",
             f"- 尺寸：电子版 ≥ {px[0]}×{px[1]} px；印刷 ≥ {pr[0]}×{pr[1]} px（比例 {ar:.2f}，最接近 {near}；生成后按这个比例裁切）"]
        if s['where'] == '版式图片':
            pg = s['page'] - 1; bx = s.get('box', [0, 0, 1, 1])
            pb = [dict(b, x=b['x'] + (W if b['pg'] == pg + 1 else 0)) for b in boxes if b['pg'] in (pg, pg + 1 if cw > W + 10 else pg)]
            z = zones(pb, bx[0] * cw, bx[1] * H, cw * (bx[2] - bx[0]), H * (bx[3] - bx[1]))
            vis = f"画面只露出 横 {round(bx[0] * 100)}–{round(bx[2] * 100)}%、竖 {round(bx[1] * 100)}–{round(bx[3] * 100)}%，其余被纸面盖住" if bx != [0, 0, 1, 1] else '整页可见'
            d += [f"- 可见区域：{vis}；主体放在可见区域里", f"- 文字压在：{'；'.join(z) if z else '无'}——这些区域要{'暗' if it.get('tone', 'dark') == 'dark' else '亮'}、干净、没有细节，主体避开"]
        else:
            d += ['- 插图：主体完整居中，四周留 8–10% 空白；能出透明背景就出透明 PNG，不能就用干净的单色或渐变背景（与页面底色相近）']
        if it.get('tone'): d.append(f"- 明暗：{'暗调（上面压白字）' if it['tone'] == 'dark' else '亮调（上面压深色字）'}")
        if it.get('ref'): d.append(f"- 参考素材（图生图时一起上传）：{'、'.join('`photos/' + r + '`' for r in ([it['ref']] if isinstance(it['ref'], str) else it['ref']))}")
        if it.get('note'): d.append(f"- 说明：{it['note']}")
        if it.get('prompt'):
            d += ['- 提示词：', '', '```', (it['prompt'].strip() + (' ' + suffix if suffix else '')).strip(), '```']
            if neg: d += ['', f'  避免：{neg}']
        else: d.append('- 提示词：（ai_images.yaml 里还没写）')
        det += d + ['']
    open(os.path.join(P, 'image_brief.md'), 'w', encoding='utf-8').write('\n'.join(out + [''] + det))
    todo = sum(1 for s in seen.values() if not s.get('done'))
    print(f'AI 配图位 {len(seen)} 个（待生成 {todo}）→ image_brief.md')

if __name__ == '__main__':
    main(os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else '.'))
