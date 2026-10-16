#!/usr/bin/env python3
"""字体样张：把四套字体方案（magazine / serif / sans / hand）排在一页，直观比较。
  python3 hb/specimen.py <输出目录>        → <输出目录>/specimen.html（字体子集在 <输出目录>/fonts/）
需要的中文字体先用 python3 hb/fonts.py fetch 下载；没下载的会用系统字体代替。"""
import os, sys, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fonts as F

out = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else 'specimen'); os.makedirs(out, exist_ok=True)
SAMPLE = dict(
    title='研学手册 Field Guide', sub='A Letter Before Takeoff · 致同学',
    body='当课本走出教室，当课堂延伸到雨林，这场研学将带你走进真正的世界。Curiosity is the first step of learning — ask, observe, record.',
    label='Key Facts · 核心知识点', num='01 02 03 Day 5')
cards = []; css_all = []
for i, (pid, p) in enumerate(F.PRESETS.items()):
    text = ''.join(SAMPLE.values()) + p['zh']
    sub = os.path.join(out, pid); os.makedirs(sub, exist_ok=True)
    css, roles, miss = F.build_css(pid, text, sub, True, log=lambda m: None)
    css = css.replace('url(fonts/', f'url({pid}/fonts/').replace(':root{', f'.s{i}{{')
    css_all.append(css)
    names = ' · '.join(dict.fromkeys(F.FONTS[x]['name'].split(' ')[0] for r in ('title', 'body') for x in roles[r]))
    cards.append(f'''<section class="card s{i}"><div class="tag">{pid} · {p["zh"]}</div>
<div class="title">{SAMPLE["title"]}</div><div class="sub">{SAMPLE["sub"]}</div>
<div class="label">{SAMPLE["label"]}</div><p class="body">{SAMPLE["body"]}</p>
<div class="num">{SAMPLE["num"]}</div><div class="fonts">{names}{'（缺：' + '、'.join(miss) + '）' if miss else ''}</div></section>''')
# 其他可选字体（写在 book.fonts 的某个角色里，如 fonts: {preset: hand, title: [caveat, lxgw-marker-gothic, lxgw-wenkai]}）
EXTRA = ['geist', 'lxgw-marker-gothic', 'smiley-sans', 'ma-shan-zheng', 'zcool-kuaile', 'lxgw-neo-zhisong', 'lxgw-neo-xihei', 'eb-garamond', 'libre-baskerville', 'ibm-plex-sans', 'source-serif-4']
rows = []
for j, fid in enumerate(EXTRA):
    if not F.path_of(fid): F.fetch(fid, quiet=True)
    sub = os.path.join(out, 'x-' + fid); os.makedirs(sub, exist_ok=True)
    css, roles, miss = F.build_css({'preset': 'magazine', 'title': [fid], 'body': [fid], 'label': [fid], 'accent': [fid], 'css': {'title_w': 400}}, '欢迎来到新学期 Welcome to School 0123456789' + F.FONTS[fid]['zh'], sub, True, log=lambda m: None)
    css_all.append(css.replace('url(fonts/', f'url(x-{fid}/fonts/').replace(':root{', f'.x{j}{{'))
    rows.append(f'<div class="xrow x{j}"><span class="xn">{fid}<br>{F.FONTS[fid]["name"]}<br>{F.FONTS[fid]["zh"]}{"（未下载）" if miss else ""}</span>'
                f'<span class="xt">欢迎来到新学期 Welcome to School</span></div>')
cards.append('<section class="card wide"><div class="tag">其他可选字体：写进 book.fonts 的 title / body / label / accent 任一角色</div>' + ''.join(rows) + '</section>')
html = f'''<!doctype html><html lang="zh"><meta charset="utf-8"><title>字体方案样张</title><style>{''.join(css_all)}
body{{margin:0;background:#EEE;font:14px sans-serif;font-synthesis:none}}main{{display:grid;grid-template-columns:1fr 1fr;gap:18px;padding:24px;width:1160px}}
.card{{background:#FBFAF7;padding:26px 30px;border-radius:4px;color:#17211C}}
.tag{{font:11px monospace;color:#777;margin-bottom:14px}}
.title{{font-family:var(--f-title);font-weight:var(--title-w);font-size:40px;letter-spacing:.06em;line-height:1.2}}
.sub{{font-family:var(--f-accent);font-style:var(--accent-style);font-weight:600;font-size:17px;color:#7E560E;margin-top:6px}}
.label{{font-family:var(--f-label);text-transform:var(--label-case);letter-spacing:var(--label-track);font-size:calc(11px * var(--label-scale));font-weight:600;color:#1D5A43;margin-top:18px}}
.body{{font-family:var(--f-body);font-weight:var(--body-w);font-size:14px;line-height:1.8;margin:8px 0 0;text-align:justify}}
.body b{{font-weight:700}}
.num{{font-family:var(--f-accent);font-style:var(--accent-style);font-weight:var(--accent-w);font-size:30px;color:#1D5A43;margin-top:10px}}
.fonts{{font:11px monospace;color:#999;margin-top:12px}}.wide{{grid-column:1/3}}
.xrow{{display:grid;grid-template-columns:300px 1fr;align-items:center;border-top:1px solid #E5E2DA;padding:10px 0}}.xn{{font:11px/1.5 monospace;color:#777}}
.xt{{font-family:var(--f-title);font-size:30px;font-weight:400}}</style><main>{''.join(cards)}</main></html>'''
open(os.path.join(out, 'specimen.html'), 'w', encoding='utf-8').write(html)
print(os.path.join(out, 'specimen.html'))
