#!/usr/bin/env python3
"""生成无版权（CC0 / 公有领域）的杂志级自然与校园合成配图。

用途：
1. 为 3 份带图模板（brochure / study-trip / family-handbook）提供版权完全干净的高清配图；
2. 供 dev/tests/selftest.sh 自动补齐模板图片并生成 dev/sample_photos/*.jpg。
  python3 dev/tests/make_test_photos.py <project_dir> <book_yaml> [--out <photos_dir>] [--assets <dir>]
"""
import array
import hashlib
import math
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HB = Path(__file__).resolve().parents[2] / 'hb'
sys.path.insert(0, str(HB))

BASIC = [
    'aerial.jpg', 'eleye.jpg', 'g_aerial.jpg', 'journal.jpg', 'pano_camp.jpg',
    'pano_nimman.jpg', 'trail.jpg', 'gift.jpg', 'market.jpg', 'lab.jpg',
    'class.jpg', 'g_wing.jpg', 'moat.jpg',
]

IMG_EXT = r'(?:jpe?g|png|webp|tiff?)'

# 每张配图绑定对应的主题色板：(顶部天空色, 地平线暖光色, 远山色, 近景山海色, 太阳/焦点色)
SCENE_PALETTES = {
    'aerial.jpg':      ((18, 46, 66),   (217, 130, 68),  (29, 78, 68),   (14, 38, 32),   (245, 203, 120)),
    'moat.jpg':        ((22, 38, 68),   (210, 118, 84),  (42, 68, 92),   (18, 32, 48),   (248, 198, 128)),
    'g_aerial.jpg':    ((26, 68, 88),   (168, 208, 198), (38, 96, 82),   (20, 52, 44),   (242, 193, 78)),
    'pano_camp.jpg':   ((20, 36, 62),   (224, 148, 86),  (36, 64, 88),   (16, 32, 46),   (246, 206, 118)),
    'pano_nimman.jpg': ((20, 36, 62),   (224, 148, 86),  (36, 64, 88),   (16, 32, 46),   (246, 206, 118)),
    'journal.jpg':     ((238, 232, 218),(218, 206, 184), (74, 108, 92),  (42, 68, 56),   (208, 106, 68)),
    'market.jpg':      ((242, 234, 220),(226, 198, 162), (142, 74, 56),  (62, 44, 38),   (232, 168, 72)),
    'eleye.jpg':       ((34, 68, 54),   (184, 206, 178), (46, 88, 64),   (22, 48, 34),   (238, 196, 106)),
    'lab.jpg':         ((18, 32, 58),   (64, 102, 148),  (32, 56, 92),   (12, 22, 42),   (242, 193, 78)),
    'trail.jpg':       ((24, 62, 48),   (162, 196, 168), (32, 78, 58),   (14, 38, 28),   (236, 198, 112)),
    'class.jpg':       ((228, 234, 242),(196, 210, 226), (52, 78, 108),  (28, 46, 68),   (218, 122, 74)),
    'gift.jpg':        ((236, 230, 216),(212, 198, 174), (82, 112, 92),  (46, 68, 54),   (198, 112, 72)),
    'g_wing.jpg':      ((10, 18, 38),   (36, 58, 98),    (20, 34, 62),   (8, 14, 28),    (242, 198, 102)),
}


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


def _render_ppm_bytes(key, W=1600, H=1200):
    """生成 1600×1200 杂志风山海/自然渐变风景 PPM 字节流（零第三方依赖，CC0 无版权）"""
    h = int(hashlib.md5(key.encode('utf-8')).hexdigest()[:8], 16)
    c_top, c_hor, c_mid, c_fg, c_sun = SCENE_PALETTES.get(
        key,
        ((20, 42, 68), (210, 138, 82), (34, 72, 68), (16, 36, 34), (242, 193, 78))
    )
    # 预计算每一列的远山和近景山脊高度
    ph1 = (h % 97) * 0.064
    ph2 = ((h >> 8) % 89) * 0.071
    ridge1 = [int(H * 0.56 + math.sin(x / 210.0 + ph1) * 55 + math.cos(x / 95.0 - ph2) * 22) for x in range(W)]
    ridge2 = [int(H * 0.72 + math.sin(x / 170.0 + ph2) * 44 + math.sin(x / 75.0 + ph1) * 18) for x in range(W)]
    sx = int(W * (0.62 + (h % 19) * 0.01))
    sy = int(H * (0.28 + ((h >> 4) % 13) * 0.01))
    sr2 = (int(min(W, H) * 0.095)) ** 2

    buf = bytearray(W * H * 3)
    # 先按行填充天空渐变，再叠加太阳与两层山脊
    for y in range(H):
        t = y / float(H - 1)
        if t < 0.58:
            u = t / 0.58
            br = int(c_top[0] * (1 - u) + c_hor[0] * u)
            bg = int(c_top[1] * (1 - u) + c_hor[1] * u)
            bb = int(c_top[2] * (1 - u) + c_hor[2] * u)
        else:
            u = (t - 0.58) / 0.42
            br = int(c_hor[0] * (1 - u) + c_mid[0] * u)
            bg = int(c_hor[1] * (1 - u) + c_mid[1] * u)
            bb = int(c_hor[2] * (1 - u) + c_mid[2] * u)
        row_bytes = bytes((br, bg, bb)) * W
        row_start = y * W * 3
        buf[row_start:row_start + W * 3] = row_bytes

    # 绘制太阳圆盘
    y0, y1 = max(0, sy - 160), min(H, sy + 160)
    x0, x1 = max(0, sx - 160), min(W, sx + 160)
    for y in range(y0, y1):
        dy2 = (y - sy) ** 2
        row_start = y * W * 3
        for x in range(x0, x1):
            d2 = dy2 + (x - sx) ** 2
            if d2 <= sr2:
                idx = row_start + x * 3
                buf[idx] = c_sun[0]
                buf[idx + 1] = c_sun[1]
                buf[idx + 2] = c_sun[2]

    # 绘制远山与近山层
    for x in range(W):
        r1 = ridge1[x]
        r2 = ridge2[x]
        x3 = x * 3
        for y in range(max(0, r1), min(H, r2)):
            idx = y * W * 3 + x3
            buf[idx] = c_mid[0]
            buf[idx + 1] = c_mid[1]
            buf[idx + 2] = c_mid[2]
        for y in range(max(0, r2), H):
            idx = y * W * 3 + x3
            buf[idx] = c_fg[0]
            buf[idx + 1] = c_fg[1]
            buf[idx + 2] = c_fg[2]

    header = f"P6\n{W} {H}\n255\n".encode('ascii')
    return header + bytes(buf)


def make(path, seed_text=None):
    """生成一张 1600×1200 的无版权杂志风合成插画配图（CC0）"""
    key = os.path.basename(seed_text or path)
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    # 优先使用 PIL（若当前 Python 环境已安装），否则用纯标准库 PPM + macOS sips 转 JPEG
    try:
        from PIL import Image
        ppm_data = _render_ppm_bytes(key)
        import io
        im = Image.open(io.BytesIO(ppm_data))
        im.save(path, 'JPEG', quality=90)
        return path
    except ImportError:
        ppm_data = _render_ppm_bytes(key)
        with tempfile.NamedTemporaryFile(suffix='.ppm', delete=False) as tf:
            tf.write(ppm_data)
            tmp_ppm = tf.name
        try:
            subprocess.run(['/usr/bin/sips', '-s', 'format', 'jpeg', tmp_ppm, '--out', path],
                           check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        finally:
            if os.path.exists(tmp_ppm):
                os.remove(tmp_ppm)
        return path


def ensure(project, book_yaml, out_dir=None):
    spec = os.path.join(project, 'book.yaml')
    names = scan_names(book_yaml or spec)
    # 编辑样册的语义图解需保留 SVG；它不是摄影占位图。
    source = open(book_yaml or spec, encoding='utf-8').read()
    if 'leaf-study.svg' in source:
        import shutil
        photos = out_dir or os.path.join(project, 'photos')
        os.makedirs(photos, exist_ok=True)
        target = os.path.join(photos, 'leaf-study.svg')
        if not os.path.exists(target):
            shutil.copyfile(str(HB.parent / 'dev' / 'sample_photos' / 'leaf-study.svg'), target)
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
        print(f'合成样张配图 {len(names)} 张 → {assets}（CC0 无版权）')
        return 0
    if len(a) < 1:
        print(__doc__)
        return 1
    project = os.path.abspath(a[0])
    book = a[1] if len(a) > 1 else os.path.join(project, 'book.yaml')
    names, made = ensure(project, book, out)
    print(f'图片引用 {len(names)} 张；新生成 {len(made)} 张（CC0 无版权）')
    return 0


if __name__ == '__main__':
    sys.exit(main())
