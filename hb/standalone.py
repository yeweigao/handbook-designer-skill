#!/usr/bin/env python3
"""单文件 HTML：图片与字体 base64 内嵌，可直接发给别人在浏览器打开/打印。
用法: python3 standalone.py <project>/book.html out.html
- 图片压到 ≤1600px 宽（屏幕看足够；印刷请用 PDF）
- 本书用到的字体子集（中西文）全部内嵌，换电脑打开字形不变；未下载的字体才回退到系统字体 / Google Fonts"""
import re, base64, io, os, sys
from PIL import Image
src, out = sys.argv[1:3]; base = os.path.dirname(os.path.abspath(src))
h = open(src, encoding='utf-8').read()
cache = {}
def img(m):
    p = os.path.join(base, m.group(1))
    if p not in cache:
        if p.lower().endswith('.svg'):
            cache[p] = 'data:image/svg+xml;base64,' + base64.b64encode(open(p, 'rb').read()).decode()
        else:
            im = Image.open(p); alpha = im.mode in ('RGBA', 'LA', 'P') and p.lower().endswith('.png')   # 透明图（logo、抠图）保留 PNG
            im = im.convert('RGBA' if alpha else 'RGB')
            if im.width > 1600: im = im.resize((1600, round(im.height*1600/im.width)), Image.LANCZOS)
            b = io.BytesIO(); im.save(b, 'PNG', optimize=True) if alpha else im.save(b, 'JPEG', quality=80, optimize=True)
            cache[p] = ('data:image/png;base64,' if alpha else 'data:image/jpeg;base64,') + base64.b64encode(b.getvalue()).decode()
    return f'src="{cache[p]}"'
MIME = {'.woff2': 'font/woff2', '.woff': 'font/woff', '.ttf': 'font/ttf', '.otf': 'font/otf'}
def font(m):
    p = os.path.join(base, m.group(1))
    return f'url(data:{MIME.get(os.path.splitext(p)[1], "font/ttf")};base64,' + base64.b64encode(open(p, 'rb').read()).decode() + ')'
h = re.sub(r'src="((?!data:|https?:)[^"]+)"', img, h)
h = re.sub(r'url\((fonts/[^)]+)\)', font, h)
h = h.replace('"Noto Serif CJK SC"', '"Noto Serif CJK SC","Noto Serif SC"').replace('"Noto Sans CJK SC"', '"Noto Sans CJK SC","Noto Sans SC"')
# 字体已在上面 base64 内嵌（woff2/woff），不再注入 Google Fonts 外链：离线可用，也不把收件人 IP/UA 暴露给第三方（F12）
STYLE = ('<meta name="viewport" content="width=840"><style>body{background:#8a8f8c}'
         '.page{margin:20px auto;box-shadow:0 4px 24px rgba(0,0,0,.25)}'
         '@media print{body{background:none}.page{margin:0;box-shadow:none}}</style>')
h = h.replace('<head>', '<head>' + STYLE, 1)
lic = os.path.join(base, 'fonts', 'LICENSES.txt')   # 字体许可随网页附上（IPA 字体用于网页嵌入时的要求；OFL 也建议附上）
if os.path.exists(lic):
    t = open(lic, encoding='utf-8').read().replace('&', '&amp;').replace('<', '&lt;')
    h = h.replace('</body>', '<footer style="max-width:794px;margin:12px auto 40px;font:11px/1.6 sans-serif;color:#eee;white-space:pre-wrap">'
                  '字体许可 / Font licenses\n' + t + '</footer><style>@media print{footer{display:none}}</style></body>', 1)
open(out, 'w', encoding='utf-8').write(h); print(out, len(h)//1024, 'KB')
