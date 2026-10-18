#!/usr/bin/env python3
"""生成固定测试照片（合成图，无版权问题：本脚本产物释放为 CC0 / 公有领域）。

用途：selftest 的 3 份照片模板（brochure / study-trip / family-handbook）不再因为"需要照片"被跳过。
  python3 hb/make_test_photos.py <project_dir> <book_yaml> [--out <photos_dir>] [--assets <dir>]

- 扫描 book.yaml 里引用的图片文件名（image / images / figure / gallery，含行内写法）；
- 缺哪张生成哪张（已存在不覆盖）：1600×1200 JPEG，四角带编号标记、色带与准星，
  裁切/压扁/双色调一眼可见；
- `--assets <dir>`：把一套固定命名的测试图生成到指定目录（供人工检查），不读写项目。
"""
import hashlib
import os
import re
import sys

from PIL import Image, ImageDraw, ImageFont

# 常用模板引用的一套固定文件名（模板更新时按扫描结果为准，这里只用于 --assets）
BASIC = ['aerial.jpg', 'eleye.jpg', 'g_aerial.jpg', 'journal.jpg', 'pano_nimman.jpg', 'trail.jpg',
         'gift.jpg', 'market.jpg', 'lab.jpg', 'class.jpg', 'g_wing.jpg', 'moat.jpg']

IMG_EXT = r'(?:jpe?g|png|webp|tiff?)'


def scan_names(book_yaml):
    """从 book.yaml 原文抓图片文件名（flow 列表 / 块写法都覆盖）"""
    try:
        t = open(book_yaml, encoding='utf-8').read()
    except OSError:
        return []
    names = set()
    for m in re.finditer(r'(?:^|[{,\s])(?:image|figure|img)\s*:\s*([^\s,}\]]+\.' + IMG_EXT + r')', t, re.I):
        names.add(os.path.basename(m.group(1)))
    for m in re.finditer(r'(?:images|gallery)\s*:\s*\[([^\]]*)\]', t, re.I):
        for x in re.split(r'[,，]', m.group(1)):
            x = x.strip().strip('\'"')
            if re.search(r'\.' + IMG_EXT + r'$', x, re.I):
                names.add(os.path.basename(x))
    for m in re.finditer(r'^\s*-\s*([^\s#]+\.' + IMG_EXT + r')\s*$', t, re.M | re.I):
        names.add(os.path.basename(m.group(1)))
    return sorted(n for n in names if n)


def _font(size):
    for f in ('/System/Library/Fonts/Helvetica.ttc', '/System/Library/Fonts/Supplemental/Arial.ttf',
              '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'):
        if os.path.exists(f):
            try:
                return ImageFont.truetype(f, size)
            except Exception:
                pass
    return ImageFont.load_default()


def make(path, seed_text=None):
    """生成一张 1600×1200 的合成测试照片"""
    key = seed_text or os.path.basename(path)
    h = hashlib.md5(key.encode('utf-8')).hexdigest()
    base = tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
    # 提亮背景、加深前景，保证照片可读、裁切明显
    bg = tuple(min(255, int(c * 0.35 + 150)) for c in base)
    fg = tuple(int(c * 0.55) for c in base)
    im = Image.new('RGB', (1600, 1200), bg)
    d = ImageDraw.Draw(im)
    # 三条色带（大面积色块，双色调/裁切最容易看出来）
    for i, y in enumerate((120, 520, 920)):
        d.rectangle([0, y, 1600, y + 200], fill=fg if i % 2 else tuple(int(c * 0.8) for c in bg))
    # 中心圆 + 十字准星（构图参考）
    cx, cy, r = 800, 600, 210
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline='white', width=12)
    d.line([cx - 300, cy, cx + 300, cy], fill='white', width=8)
    d.line([cx, cy - 300, cx, cy + 300], fill='white', width=8)
    # 四角编号（裁切后能判断少了哪块）
    f = _font(84)
    for label, pos in (('1 TL', (40, 40)), ('2 TR', (1320, 40)), ('3 BL', (40, 1030)), ('4 BR', (1290, 1030))):
        d.text(pos, label, fill='white', font=f, stroke_width=4, stroke_fill='black')
    # 文件名（小字，确认是哪张图）
    d.text((60, 620), key[:36], fill='white', font=_font(52), stroke_width=3, stroke_fill='black')
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    im.save(path, 'JPEG', quality=88)
    return path


def ensure(project, book_yaml, out_dir=None):
    spec = os.path.join(project, 'book.yaml')
    names = scan_names(book_yaml or spec)
    photos = out_dir or os.path.join(project, 'photos')
    made = []
    for n in names:
        p = os.path.join(photos, n)
        if not os.path.exists(p):
            make(p, n)
            made.append(n)
    return names, made


def main():
    a = sys.argv[1:]
    if not a:
        print(__doc__)
        return 1
    assets = None
    if '--assets' in a:
        i = a.index('--assets')
        assets = a[i + 1]
        del a[i:i + 2]
    out = None
    if '--out' in a:
        i = a.index('--out')
        out = a[i + 1]
        del a[i:i + 2]
    if assets:
        names = BASIC
        for n in names:
            make(os.path.join(assets, n), n)
        print(f'测试照片 {len(names)} 张 → {assets}（合成图，CC0）')
        return 0
    if len(a) < 1:
        print(__doc__)
        return 1
    project = os.path.abspath(a[0])
    book = a[1] if len(a) > 1 else os.path.join(project, 'book.yaml')
    names, made = ensure(project, book, out)
    print(f'图片引用 {len(names)} 张；新生成 {len(made)} 张（合成图，CC0）')
    return 0


if __name__ == '__main__':
    sys.exit(main())
