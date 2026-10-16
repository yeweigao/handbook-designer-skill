"""无图模式的“底图”生成器：照片的位置换成按风格程序绘制的画面（每页用页码做随机种子：同一本书一套语言、每页构图不同）。
make(style, w, h, seed, colors, box) -> PIL.Image（RGB，w×h 像素，已含 2 倍精度）

设计原则（每种风格的完整设计语言写在 references/style.md §1.1）：
- 只用 book.colors 里的颜色，按印刷“专色 + 网目”的思路取色：原色、或向纸色/白色调淡的固定档位，不做混浊的中间色。
- 平面图形全部用距离场（SDF）或 3 倍超采样绘制：边缘像矢量一样干净，不加噪点。
- 版面上文字都左对齐：主体图形放在可见区域（box）的右半部、竖向中段，左栏和顶部标题区保持干净。
- 平面风格（editorial / swiss / papercut / riso）由画面自己决定与纸面的边界（硬边、波浪边），纸面完全不透明，不半透明混色。
"""
import math, colorsys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

def hx(c): c = c.lstrip('#'); return np.array([int(c[i:i + 2], 16) for i in (0, 2, 4)], np.float32)
def mix(a, b, t): return a * (1 - t) + b * t
def rgb(a): return tuple(int(max(0, min(255, v))) for v in a)
WHITE = np.array([255, 255, 255], np.float32)
SS = 3                                      # 多边形/描边的超采样倍数

# ------------------------------------------------------------------ 画布与图元
class Cv:
    def __init__(s, w, h, base):
        s.w, s.h = w, h; s.img = np.zeros((h, w, 3), np.float32) + base
        s.y, s.x = np.mgrid[0:h, 0:w].astype(np.float32)
    def paint(s, a, col, op=1.0):            # 普通叠色
        a = (np.clip(a, 0, 1) * op)[..., None]; s.img = s.img * (1 - a) + np.asarray(col, np.float32) * a
    def multiply(s, a, col, op=1.0):         # 正片叠底：油墨套印
        a = (np.clip(a, 0, 1) * op)[..., None]; s.img = s.img * (1 - a) + s.img * (np.asarray(col, np.float32) / 255) * a
    def shadow(s, a, dx, dy, blur, col, op):  # 纸片投影：形状平移 + 高斯模糊
        m = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)).transform((s.w, s.h), Image.AFFINE, (1, 0, -dx, 0, 1, -dy))
        m = np.asarray(m.filter(ImageFilter.GaussianBlur(max(1, blur))), np.float32) / 255
        s.paint(m, col, op)
    def done(s): return s.img

def cov(d, soft=1.0): return np.clip(.5 - d / soft, 0, 1)          # 有符号距离 → 覆盖率（1px 抗锯齿）
def disc(cv, cx, cy, r): return cov(np.hypot(cv.x - cx, cv.y - cy) - r)
def ring(cv, cx, cy, r, t): return cov(np.abs(np.hypot(cv.x - cx, cv.y - cy) - r) - t / 2)
def box(cv, x0, y0, x1, y1, rad=0, ang=0):
    cx, cy, hw, hh = (x0 + x1) / 2, (y0 + y1) / 2, abs(x1 - x0) / 2, abs(y1 - y0) / 2
    X, Y = cv.x - cx, cv.y - cy
    if ang: c, s_ = math.cos(-ang), math.sin(-ang); X, Y = X * c - Y * s_, X * s_ + Y * c
    qx, qy = np.abs(X) - hw + rad, np.abs(Y) - hh + rad
    return cov(np.hypot(np.maximum(qx, 0), np.maximum(qy, 0)) + np.minimum(np.maximum(qx, qy), 0) - rad)
def arc(cv, cx, cy, r, t, a0, a1):            # 圆弧（角度弧度，顺时针为正，0 = 3 点钟方向），平头
    th = np.arctan2(cv.y - cy, cv.x - cx); mid = (a0 + a1) / 2; half = (a1 - a0) / 2
    dth = np.abs((th - mid + math.pi) % (2 * math.pi) - math.pi)
    return ring(cv, cx, cy, r, t) * cov((dth - half) * r)
def quarter(cv, cx, cy, r, q):                # 四分之一圆：圆心在格子角上，q=0..3 决定朝向
    sx, sy = [(1, 1), (-1, 1), (-1, -1), (1, -1)][q]
    return disc(cv, cx, cy, r) * cov(-(cv.x - cx) * sx) * cov(-(cv.y - cy) * sy)
def _bbox(pts, w, h, pad):
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return max(0, int(min(xs) - pad)), max(0, int(min(ys) - pad)), min(w, int(max(xs) + pad) + 1), min(h, int(max(ys) + pad) + 1)
def poly(cv, pts):                            # 任意多边形（超采样）
    x0, y0, x1, y1 = _bbox(pts, cv.w, cv.h, 2); out = np.zeros((cv.h, cv.w), np.float32)
    if x1 <= x0 or y1 <= y0: return out
    m = Image.new('L', ((x1 - x0) * SS, (y1 - y0) * SS), 0)
    ImageDraw.Draw(m).polygon([((x - x0) * SS, (y - y0) * SS) for x, y in pts], fill=255)
    out[y0:y1, x0:x1] = np.asarray(m.resize((x1 - x0, y1 - y0), Image.BOX), np.float32) / 255; return out
def stroke(cv, pts, wd):                      # 等宽单线（圆头圆角），手账涂鸦、飞鸟
    x0, y0, x1, y1 = _bbox(pts, cv.w, cv.h, wd + 2); out = np.zeros((cv.h, cv.w), np.float32)
    if x1 <= x0 or y1 <= y0: return out
    m = Image.new('L', ((x1 - x0) * SS, (y1 - y0) * SS), 0); d = ImageDraw.Draw(m)
    q = [((x - x0) * SS, (y - y0) * SS) for x, y in pts]; r = wd * SS / 2
    d.line(q, fill=255, width=max(1, int(round(wd * SS))), joint='curve')
    for px, py in (q[0], q[-1]): d.ellipse([px - r, py - r, px + r, py + r], fill=255)
    out[y0:y1, x0:x1] = np.asarray(m.resize((x1 - x0, y1 - y0), Image.BOX), np.float32) / 255; return out
def bez(p0, p1, p2, p3, n=48):
    t = np.linspace(0, 1, n)[:, None]; P = [np.array(p, np.float32) for p in (p0, p1, p2, p3)]
    return [tuple(v) for v in ((1 - t) ** 3 * P[0] + 3 * (1 - t) ** 2 * t * P[1] + 3 * (1 - t) * t ** 2 * P[2] + t ** 3 * P[3])]
def tint(c, paper, t): return mix(c, paper, t)                   # 印刷网目：原色向纸色调淡 t
def wave(xs, rng, k=1.0):                     # 平滑起伏（三个正弦叠加），-1..1
    ph = rng.random(3) * 6.283; f = np.array([1.0, 2.2, 4.7]) * k * rng.uniform(.8, 1.2, 3)
    return .58 * np.sin(xs * f[0] + ph[0]) + .3 * np.sin(xs * f[1] + ph[1]) + .12 * np.sin(xs * f[2] + ph[2])

# ------------------------------------------------------------------ 风格
def grain(arr, rng, amt): return arr + rng.normal(0, amt, arr.shape[:2])[..., None]   # 只用于照片占位与弥散风（极细）

def photo(w, h, rng, C, B):          # 深色占位（照片之后再换）
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    t = (y / h)[..., None]; img = mix(C['G'] * .75 + C['INK'] * .1, C['G'] * .45, t)
    bx, by, bw, bh = B; cx, cy = bx + rng.uniform(.25, .75) * bw, by + rng.uniform(.3, .7) * bh
    r = np.exp(-(((x - cx) / (w * .35)) ** 2 + ((y - cy) / (h * .3)) ** 2))[..., None]
    img = img * (1 - .35 * r) + C['GOLD'] * .35 * r
    return grain(img, rng, 4)

def editorial(w, h, rng, C, B):
    """杂志：一整块深色纸面 + 12 栏发丝网格 + 一条基线；一枚被基线平分的发丝大圆，圆上一段金色弧线和一个金点（像刻度/轨道）。
    语言：发丝线（0.5pt）、栏网格、对齐与留白；只有一种强调色，只出现一次。"""
    bx, by, bw, bh = B; U = min(bw, bh) / 12; hair = max(1.6, w / 1000)
    deep = mix(C['G'], C['INK'], .35); cv = Cv(w, h, deep)
    cols = 12 if w > h else 6; step = w / cols
    for i in range(1, cols): cv.paint(cov(np.abs(cv.x - i * step) - hair / 2), WHITE, .08)
    yb = by + bh * rng.uniform(.56, .64); cv.paint(cov(np.abs(cv.y - yb) - hair / 2), WHITE, .22)
    R = min(U * rng.uniform(3.0, 3.6), bh * .36); cx = bx + bw - max(R * 1.05, bw * .25)
    cx = round(cx / step) * step                                            # 圆心落在栏线上
    cv.paint(ring(cv, cx, yb, R, hair * 1.1), WHITE, .55)
    if rng.random() < .5: cv.paint(ring(cv, cx, yb, R * .62, hair), WHITE, .25)
    a0 = rng.uniform(-2.6, -1.2); cv.paint(arc(cv, cx, yb, R, hair * 3.2, a0, a0 + .9), C['GOLD'])
    ex, ey = cx + R * math.cos(a0 + .9), yb + R * math.sin(a0 + .9); cv.paint(disc(cv, ex, ey, hair * 4.2), C['GOLD'])
    return cv.done()

def swiss(w, h, rng, C, B):
    """瑞士网格：主色满版，所有形状落在 6 栏模块网格上；词汇只有圆、四分之一圆、方块、横杠；三选一构图，全书统一、每页不同。
    语言：纯平色、零装饰、不对称平衡、形状出血到页边；颜色比例 主色 70 / 墨色 20 / 纸色+强调 10。"""
    bx, by, bw, bh = B; cv = Cv(w, h, C['G']); avail = bh * .76; k = int(rng.integers(3))
    m = min(bw / 6, avail / (4.2, 3.2, 6.2)[k])     # 形状高度不超过可见区的 76%，避开页眉与底部文字
    circ = C['INK'] if abs(float(np.dot(C['INK'], [.3, .59, .11])) - float(np.dot(C['G'], [.3, .59, .11]))) > 30 else C['GOLD']   # 主色本身是黑色时，墨色形状改用强调色
    x1 = bx + bw; ym = by + bh * .54
    if k == 0:      # 大圆出血 + 横杠 + 小方块
        R = 2 * m; cx, cy = x1 - .9 * m, ym + .2 * m
        cv.paint(disc(cv, cx, cy, R), circ)
        cv.paint(box(cv, x1 - 3.4 * m, cy - .09 * m, x1 + 2, cy + .09 * m), C['PAPER'])
        cv.paint(box(cv, x1 - 3.4 * m, cy - 2.1 * m, x1 - 2.9 * m, cy - 1.6 * m), C['GOLD'])
    elif k == 1:    # 四分之一圆拼块：2 栏 × 3 行
        cols = [circ, C['PAPER'], C['GOLD']]; gx0 = x1 - 2 * m; gy0 = ym - 1.5 * m
        for r in range(3):
            for c in range(2):
                x, y = gx0 + c * m, gy0 + r * m; q = int(rng.integers(4)); col = cols[(r + c + int(rng.integers(2))) % 3]
                if (r + c) % 3 == 2: cv.paint(box(cv, x, y, x + m, y + m), col)
                else: cv.paint(quarter(cv, x + (m if q in (1, 2) else 0), y + (m if q in (2, 3) else 0), m, q), col)
    else:           # 同心半圆：从右页边长出来
        cx, cy = x1, ym; cs = [circ, C['PAPER'], C['GOLD'], C['G']]
        for i, R in enumerate([3.0 * m, 2.25 * m, 1.5 * m, .75 * m]): cv.paint(disc(cv, cx, cy, R), cs[i % 4])
    return cv.done()

def notebook(w, h, rng, C, B):
    """手账：5mm 方格纸（每 5 格一条稍深的线）上贴一件文具，三选一按页轮换——便利贴 / 拍立得 / 带回形针的索引卡；
    配一条和纸胶带、等宽单线涂鸦（四角星、波浪线、三个圆点）。
    语言：文具平面插画——纯色块、统一的柔和投影（光从左上）、单线圆头 0.6pt；颜色 纸张/便利贴 GOLD · 胶带与照片 G · 贴纸与点 OCH。"""
    bx, by, bw, bh = B; U = min(bw, bh) / 12; paper = C['PAPER']; cv = Cv(w, h, paper)
    gs = 40.0; hair = 1.2
    gx = np.abs(((cv.x + gs / 2) % gs) - gs / 2); gy = np.abs(((cv.y + gs / 2) % gs) - gs / 2)
    cv.paint(np.maximum(cov(gx - hair / 2), cov(gy - hair / 2)), C['G'], .13)
    gx5 = np.abs(((cv.x + gs * 2.5) % (gs * 5)) - gs * 2.5); gy5 = np.abs(((cv.y + gs * 2.5) % (gs * 5)) - gs * 2.5)
    cv.paint(np.maximum(cov(gx5 - hair / 2), cov(gy5 - hair / 2)), C['G'], .12)
    k = int(rng.integers(3)); s = 3.3 * U; ink = C['INK']; lw = max(2.5, U * .075)
    sw_, sh_ = [(s, s), (s * .92, s * 1.12), (s * 1.3, s * .82)][k]
    cx, cy = bx + bw - max(sw_ * .62 + .9 * U, bw * .27), by + bh * rng.uniform(.42, .5); ang = math.radians(rng.uniform(-5, 5))
    ca, sa = math.cos(ang), math.sin(ang)
    def R(px, py): return cx + px * ca - py * sa, cy + px * sa + py * ca           # 物件坐标 → 画面坐标
    obj = box(cv, cx - sw_ / 2, cy - sh_ / 2, cx + sw_ / 2, cy + sh_ / 2, rad=U * .06, ang=ang)
    cv.shadow(obj, U * .08, U * .16, U * .22, ink, .16)
    if k == 0:                                                                  # 便利贴：浅黄 + 三条浅横线
        cv.paint(obj, tint(C['GOLD'], WHITE, .3))
        for i in range(3):
            x0, y0 = R(-sw_ * .36, -sh_ * .12 + i * sh_ * .2); x1, y1 = R(sw_ * .36, -sh_ * .12 + i * sh_ * .2)
            cv.paint(obj * stroke(cv, [(x0, y0), (x1, y1)], 1.4), ink, .14)
    elif k == 1:                                                                # 拍立得：白框 + 一幅极简小风景（太阳 + 两座山）
        cv.paint(obj, WHITE)
        m_ = sw_ * .07; px0, py0, px1, py1 = -sw_ / 2 + m_, -sh_ / 2 + m_, sw_ / 2 - m_, -sh_ / 2 + m_ + (sw_ - 2 * m_)
        win = poly(cv, [R(px0, py0), R(px1, py0), R(px1, py1), R(px0, py1)])
        cv.paint(win, tint(C['G'], WHITE, .72))
        sx_, sy_ = R(px1 - (px1 - px0) * .28, py0 + (py1 - py0) * .3); cv.paint(win * disc(cv, sx_, sy_, (px1 - px0) * .12), C['GOLD'])
        for (a0, a1, pk, col) in [(.05, .75, .45, tint(C['G'], WHITE, .35)), (.35, 1.0, .3, C['G'])]:
            pts = [R(px0 + (px1 - px0) * a0, py1), R(px0 + (px1 - px0) * (a0 + a1) / 2, py0 + (py1 - py0) * pk), R(px0 + (px1 - px0) * a1, py1)]
            cv.paint(win * poly(cv, pts), col)
        x0, y0 = R(-sw_ * .3, py1 + (sh_ / 2 - py1) * .5); x1, y1 = R(sw_ * .05, py1 + (sh_ / 2 - py1) * .5)
        cv.paint(stroke(cv, [(x0, y0), (x1, y1)], 1.6), ink, .3)
    else:                                                                       # 索引卡：白卡 + 一条红线 + 浅蓝横线 + 回形针
        cv.paint(obj, WHITE)
        for i in range(4):
            yy = -sh_ * .24 + i * sh_ * .17; x0, y0 = R(-sw_ * .44, yy); x1, y1 = R(sw_ * .44, yy)
            cv.paint(stroke(cv, [(x0, y0), (x1, y1)], 1.4), C['OCH'] if i == 0 else C['G'], .55 if i == 0 else .18)
        r, Lc = .3 * U, 1.3 * U; ox_, oy_ = sw_ * .28, -sh_ / 2 - Lc * .32      # 回形针：三段直线 + 三个 180° 圆弧
        top = lambda cx_, cy_, rr: [(cx_ + rr * math.cos(v), cy_ - rr * math.sin(v)) for v in np.linspace(math.pi, 0, 20)]
        bot = lambda cx_, cy_, rr: [(cx_ + rr * math.cos(v), cy_ - rr * math.sin(v)) for v in np.linspace(0, -math.pi, 20)]
        path = [(-.5 * r, .55 * Lc)] + top(0, r, .5 * r) + bot(-.25 * r, Lc - .75 * r, .75 * r) + top(0, r, r) + [(r, .8 * Lc)]
        path = [(ox_ + px, oy_ + py) for px, py in path]
        cv.paint(stroke(cv, [R(*p) for p in path], max(2.5, U * .07)), mix(ink, WHITE, .45))
    ta = ang + math.radians(rng.choice([-1, 1]) * rng.uniform(6, 11)); tl, tw = 2.4 * U, .6 * U      # 和纸胶带（锯齿端），压住上沿
    tx, ty = R(-sw_ * .18 if k == 2 else rng.uniform(-.15, .15) * sw_, -sh_ / 2); c2, s2 = math.cos(ta), math.sin(ta)
    pts = [(tl / 2 + (U * .07 if i % 2 else 0), -tw / 2 + tw * i / 6) for i in range(7)] + [(-tl / 2 - (U * .07 if i % 2 else 0), tw / 2 - tw * i / 6) for i in range(7)]
    tape = poly(cv, [(tx + px_ * c2 - py_ * s2, ty + px_ * s2 + py_ * c2) for px_, py_ in pts])
    cv.paint(tape, tint(C['G'], WHITE, .5), .9)
    X, Y = cv.x - tx, cv.y - ty; stripe = .5 + .5 * np.sin((X * (c2 - s2) + Y * (s2 + c2)) / (U * .1))
    cv.paint(tape * np.clip((stripe - .5) * 4 + .5, 0, 1), WHITE, .35)
    if k != 1:                                                                   # 圆贴纸（右下角）
        sx, sy = R(sw_ * .42, sh_ * .46); sr = .52 * U
        dsk = disc(cv, sx, sy, sr); cv.shadow(dsk, U * .05, U * .1, U * .14, ink, .14)
        cv.paint(dsk, tint(C['OCH'], WHITE, .15)); cv.paint(ring(cv, sx, sy, sr * .72, U * .045), WHITE, .9)
    L_, T_ = cx - sw_ / 2, cy - sh_ / 2
    for (px, py, r) in [(L_ - .15 * U, T_ - .05 * U, .5 * U), (L_ - .95 * U, T_ + .9 * U, .26 * U)]:   # 四角星（星形线）
        t = np.linspace(0, 2 * math.pi, 120); cv.paint(stroke(cv, list(zip(px + r * np.cos(t) ** 3, py + r * np.sin(t) ** 3)), lw), ink, .85)
    y0 = cy + sh_ / 2 + .55 * U; x0 = cx - sw_ * .5                             # 波浪下划线
    xs = np.linspace(0, sw_, 80); cv.paint(stroke(cv, list(zip(x0 + xs, y0 + U * .12 * np.sin(xs / sw_ * 3 * math.pi))), lw), ink, .85)
    for i in range(3): cv.paint(disc(cv, cx + sw_ * .5 + .55 * U + i * U * .32, T_ + .1 * U + i * U * .26, U * .1), C['OCH'])
    return cv.done()

def inkwash(w, h, rng, C, B):
    """新中式水墨：素净宣纸色 + 一轮淡朱色日 + 四层远山（山脊浓、向下化开成雾，越远越淡越偏青）+ 三只飞鸟 + 一方朱印。
    语言：大面积留白、墨分五色（浓淡层次而非线条）、朱红只出现在日与印章，飞鸟是唯一的线。"""
    bx, by, bw, bh = B; U = min(bw, bh) / 12; paper = C['PAPER']; cv = Cv(w, h, paper)
    sx, sy, sr = bx + bw * rng.uniform(.7, .8), by + bh * rng.uniform(.22, .3), 1.25 * U
    cv.paint(disc(cv, sx, sy, sr * .9), tint(C['OCH'], paper, .38))
    xs = cv.x[0] / w * 2 * math.pi
    for L in range(4):
        near = L / 3
        ridge = by + bh * (.5 + .1 * L) - bh * (.16 - .025 * L) * (wave(xs, rng, .55 + L * .3) + 1) / 2
        ridge = np.convolve(np.pad(ridge, 60, mode='edge'), np.ones(121) / 121, 'valid')          # 山脊线顺滑，不出锯齿
        depth = (cv.y - ridge[None, :]) / (bh * (.06 + .05 * near))
        a = cov(-(cv.y - ridge[None, :])) * np.exp(-np.clip(depth, 0, None) * 1.1)           # 山脊清晰最浓，向下化开成雾
        col = mix(mix(C['INK'], C['G'], .55 * (1 - near)), paper, .05)
        cv.paint(a, col, .2 + .45 * near ** 1.2)
        mist = np.exp(-((cv.y - ridge[None, :] - bh * (.07 + .03 * near)) / (bh * .035)) ** 2)    # 每层山脚一道雾，把层次分开
        cv.paint(mist, paper, .55)
    lw = max(2.0, U * .05)
    for i, (dx, dy, r) in enumerate([(-1.9, .5, .34), (-2.5, .95, .26), (-1.4, 1.2, .2)]):   # 飞鸟：两段弧
        px, py, R = sx + dx * U, sy + dy * U, r * U
        left = bez((px - R, py - R * .35), (px - R * .6, py - R * .55), (px - R * .2, py - R * .3), (px, py))
        right = bez((px, py), (px + R * .2, py - R * .3), (px + R * .6, py - R * .55), (px + R, py - R * .35))
        cv.paint(stroke(cv, left + right[1:], lw), C['INK'], .75)
    S = .62 * U; qx, qy = bx + bw - 1.6 * U, by + bh * .72                           # 朱印：实心方印 + 白框 + 一横一竖
    cv.paint(box(cv, qx, qy, qx + S, qy + S, rad=S * .06), C['OCH'])
    cv.paint(cov(np.maximum(np.abs(cv.x - qx - S / 2), np.abs(cv.y - qy - S / 2)) - S * .36) - cov(np.maximum(np.abs(cv.x - qx - S / 2), np.abs(cv.y - qy - S / 2)) - S * .31), paper, .92)
    cv.paint(box(cv, qx + S * .3, qy + S * .48, qx + S * .7, qy + S * .54), paper, .92); cv.paint(box(cv, qx + S * .47, qy + S * .3, qx + S * .53, qy + S * .7), paper, .92)
    return cv.done()

def papercut(w, h, rng, C, B):
    """剪纸拼贴：纯色天空 + 一轮双层纸太阳 + 一朵纸云 + 五层波浪纸片；最前一层就是纸面本身——画面用波浪边自然过渡到正文。
    语言：平涂纸色（原色与固定淡档）、统一的投影方向（光从下前方，影子落在后一层上）、圆润曲线、没有描边。"""
    bx, by, bw, bh = B; U = min(bw, bh) / 12; paper = C['PAPER']
    cv = Cv(w, h, tint(C['G'], paper, .9))
    sx, sy, sr = bx + bw * rng.uniform(.7, .8), by + bh * .3, 1.3 * U
    for r, col in [(sr * 1.35, tint(C['GOLD'], WHITE, .55)), (sr, C['GOLD'])]:
        d = disc(cv, sx, sy, r); cv.shadow(d, 0, U * .06, U * .18, C['INK'], .14); cv.paint(d, col)
    kx, ky = sx - 1.9 * U, sy + .55 * U                                          # 纸云：三个圆 + 圆角底
    cl = np.maximum.reduce([disc(cv, kx - .55 * U, ky, .42 * U), disc(cv, kx + .05 * U, ky - .25 * U, .58 * U), disc(cv, kx + .6 * U, ky + .02 * U, .4 * U),
                            box(cv, kx - .95 * U, ky, kx + 1.0 * U, ky + .42 * U, rad=.21 * U)])
    cv.shadow(cl, 0, U * .06, U * .16, C['INK'], .12); cv.paint(cl, WHITE)
    cols = [tint(C['G'], paper, .6), tint(C['GOLD'], paper, .25), tint(C['G'], paper, .25), tint(C['OCH'], paper, .3), paper]
    xs = np.linspace(-2, w + 2, 220)
    for i, col in enumerate(cols):
        top = by + bh * (.56 + .085 * i) + (bh * .02 if i == 4 else 0); amp = bh * (.035 if i < 4 else .022)
        ys = top + amp * wave(xs / w * 2 * math.pi, rng, 1.2 + .3 * i)
        lay = poly(cv, list(zip(xs, ys)) + [(w + 2, h + 2), (-2, h + 2)])
        cv.shadow(lay, 0, -U * .07, U * .2, C['INK'], .2); cv.paint(lay, col)
    return cv.done()

def riso(w, h, rng, C, B):
    """复古孔版（Risograph）：暖纸 + 三色专色（黄 GOLD / 红 OCH / 蓝 G）正片叠底套印；黄色是半调网点的太阳，红色是拱门，蓝色是细条纹与一个圆点；
    每个色版有一点套色偏移，叠印处自然出现第四、第五种颜色。语言：专色、网点、叠印、错版；几何形、无描边、无渐变（渐变用网点表达）。"""
    bx, by, bw, bh = B; U = min(bw, bh) / 12; paper = C['PAPER']; cv = Cv(w, h, paper)
    def mis(): return rng.uniform(-.05, .05) * U, rng.uniform(-.05, .05) * U
    ax = bx + bw - max(1.9 * U, bw * .2); top = by + bh * .5; aw = 1.35 * U; bot = by + bh * .86
    sx, sy, sr = ax + .3 * U, by + bh * .36, 2.2 * U
    ox, oy = mis()                                                               # 黄版：半调网点太阳（中心实、边缘网点变小）
    cell = U * .17; th = math.radians(15); X, Y = cv.x - sx - ox, cv.y - sy - oy
    u = (X * math.cos(th) + Y * math.sin(th)) / cell; v = (-X * math.sin(th) + Y * math.cos(th)) / cell
    fu, fv = (u - np.round(u)) * cell, (v - np.round(v)) * cell
    tone = np.clip(1.15 - (np.hypot(X, Y) / sr) ** 2 * .8, 0, 1)
    dots = cov(np.hypot(fu, fv) - cell * .56 * np.sqrt(tone)) * disc(cv, sx + ox, sy + oy, sr)
    cv.multiply(np.maximum(dots, disc(cv, sx + ox, sy + oy, sr * .45)), C['GOLD'], .95)
    ox, oy = mis()                                                               # 红版：拱门
    arch = np.maximum(disc(cv, ax + ox, top + oy, aw), box(cv, ax - aw + ox, top + oy, ax + aw + ox, bot + oy))
    cv.multiply(arch, C['OCH'], .9)
    ox, oy = mis()                                                               # 蓝版：四条细条纹 + 一个圆点
    for i in range(4):
        yy = bot - U * (.35 + .32 * i) + oy
        cv.multiply(box(cv, ax - aw - .7 * U + ox, yy, min(bx + bw + 2, ax + aw + 1.6 * U) + ox, yy + U * .13), C['G'], .9)
    cv.multiply(disc(cv, ax - aw - .8 * U + ox, by + bh * .3 + oy, .42 * U), C['G'], .9)
    return cv.done()

def nebula(w, h, rng, C, B):
    """深色星云（科技品牌）：深墨夜色底 + 三团弥散光（主色靛蓝、强调紫、由强调色推出的兰紫）+ 稀疏的粒子星点 + 一道极细的轨道环。
    语言：光是“加”上去的（滤色叠加，越叠越亮不发灰）；星点大小 0.5–1.5pt、亮度有层次，只有少数几颗带光晕；左栏星点更稀更暗，给文字让位。"""
    bx, by, bw, bh = B; S = max(bw, bh); U = min(bw, bh) / 12
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    night = mix(C['INK'], np.zeros(3, np.float32), .35)
    img = mix(night, mix(night, C['G'], .12), (y / h)[..., None])
    hh, ll, ss = colorsys.rgb_to_hls(*(C['OCH'] / 255))
    orchid = np.array(colorsys.hls_to_rgb((hh + .08) % 1, min(.62, ll + .1), min(1, ss + .1)), np.float32) * 255
    def light(cx, cy, rx, ry, col, a):                                           # 滤色叠加：1-(1-底)(1-光)
        nonlocal img; g = (np.exp(-(((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2)) * a)[..., None]
        img = 255 - (255 - img) * (1 - g * col / 255)
    gx, gy = bx + bw * rng.uniform(.68, .82), by + bh * rng.uniform(.32, .5)
    light(gx, gy, S * .3, S * .26, C['OCH'], .62)
    light(gx + bw * .06, gy - bh * .07, S * .13, S * .11, orchid, .45)
    light(bx + bw * rng.uniform(.0, .2), by + bh * rng.uniform(.85, 1.0), S * .32, S * .2, C['G'], .32)
    light(gx - bw * .03, gy + bh * .03, S * .05, S * .05, np.array([255, 255, 255], np.float32), .14)   # 光心
    R = min(bw, bh) * rng.uniform(.34, .42)                                        # 轨道环（极细，斜椭圆）
    th = rng.uniform(-.5, -.2); X, Y = x - gx, y - gy; xr, yr = X * math.cos(th) + Y * math.sin(th), -X * math.sin(th) + Y * math.cos(th)
    ringd = np.abs(np.hypot(xr / R, yr / (R * .38)) - 1) * R * .5
    img = mix(img, mix(C['GOLD'], WHITE, .4), (cov(ringd - 1.0) * .16)[..., None])
    n = int(bw * bh / 9000); pts = []                                            # 粒子星点：越靠近光团越密
    while len(pts) < n:
        px, py = rng.uniform(0, w), rng.uniform(by, by + bh)
        dens = np.exp(-(((px - gx) / (S * .45)) ** 2 + ((py - gy) / (S * .4)) ** 2))
        if rng.random() < .18 + .82 * dens: pts.append((px, py))
    cv = Cv(w, h, 0); cv.img = img
    for px, py in pts:
        left = px < bx + bw * .5
        r = rng.uniform(.6, 1.5) * w / 1600 * (.8 if left else 1); a = rng.uniform(.18, .55 if left else .9)
        x0, x1, y0, y1 = int(max(0, px - 4)), int(min(w, px + 5)), int(max(0, py - 4)), int(min(h, py + 5))
        d = np.hypot(cv.x[y0:y1, x0:x1] - px, cv.y[y0:y1, x0:x1] - py)
        cv.img[y0:y1, x0:x1] = mix(cv.img[y0:y1, x0:x1], mix(WHITE, C['GOLD'], rng.uniform(0, .5)), (cov(d - r) * a)[..., None])
    for _ in range(int(rng.integers(5, 9))):                                      # 几颗带光晕的亮星（只在右半）
        px, py = gx + rng.normal(0, S * .18), gy + rng.normal(0, S * .15)
        if px < bx + bw * .5: continue
        light(px, py, U * .22, U * .22, WHITE, .35)
    return cv.img

def aurora(w, h, rng, C, B):         # 弥散渐变（Aurora / Mesh Gradient）：暖光从上方洒下、冷蓝从下方升起，几束柔光
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    hh, _, _ = colorsys.rgb_to_hls(*(C['G'] / 255))
    tone = lambda l, s=1.0: np.array(colorsys.hls_to_rgb(hh, l, s), np.float32) * 255
    vivid, sky = tone(.5), tone(.84)                        # 由 G 推出的亮蓝、天空蓝（换品牌色跟着变）
    bx, by, bw, bh = B; S = max(bw, bh)
    img = np.zeros((h, w, 3), np.float32) + mix(C['PAPER'], WHITE, .4)
    def glow(cx, cy, rx, ry, col, a):
        nonlocal img; g = np.exp(-(((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2))[..., None] * a; img = mix(img, col, g)
    ry = max(bh, S * .6)                                    # 画面很扁（跨页顶部）时别把光晕压成横条
    glow(bx + bw * rng.uniform(.5, .85), by - bh * .05, S * .6, ry * .35, C['GOLD'], .95)    # 上方暖光
    glow(bx + bw * rng.uniform(.0, .3), by + bh * rng.uniform(.45, .6), S * .45, ry * .3, sky, .5)
    glow(bx + bw * rng.uniform(.4, .8), by + bh * 1.05, S * .75, ry * .42, sky, .95)          # 下方冷蓝
    glow(bx + bw * rng.uniform(.6, .9), by + bh * 1.08, S * .4, ry * .22, vivid, .45)
    # 光锥：从画面顶部上方一点向下呈扇形散开，角度与亮度都用宽高斯过渡，没有任何硬边或细线
    ox, oy = bx + bw * rng.uniform(.5, .7), by - bh * .25
    ang = np.arctan2(x - ox, np.maximum(y - oy, 1))                                   # 相对竖直方向的角度
    cone = np.exp(-(ang / .22) ** 2) * np.exp(-((y - by - bh * .35) / (bh * .55)) ** 2)
    img = mix(img, mix(C['GOLD'], WHITE, .45), (cone * .55)[..., None])
    img = np.asarray(Image.fromarray(img.clip(0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(max(2, w / 400)))).astype(np.float32)
    return grain(img, rng, 1.6)

STYLES = dict(photo=photo, editorial=editorial, swiss=swiss, notebook=notebook, inkwash=inkwash, papercut=papercut, riso=riso, aurora=aurora, nebula=nebula)
TONE = dict(photo='dark', editorial='dark', swiss='dark', notebook='light', inkwash='light', papercut='light', riso='light', aurora='light', nebula='dark')

def make(style, w, h, seed, colors, box=(0, 0, 1, 1)):
    """box：画面里真正露出来的区域（0–1 比例），主体图形会放在这个区域里，避免被纸面淡出盖掉。"""
    C = {k: hx(v) for k, v in colors.items()}
    rng = np.random.default_rng(seed)
    if style not in ('photo', 'aurora', 'nebula') and box[3] - box[1] > .9:      # 整页高的画面（封面、封底、满版）：底部 26% 是文字区，图形在它上方收住
        box = (box[0], box[1], box[2], box[1] + (box[3] - box[1]) * .74)
    B = (box[0] * w, box[1] * h, (box[2] - box[0]) * w, (box[3] - box[1]) * h)
    arr = STYLES[style](w, h, rng, C, B)
    return Image.fromarray(np.asarray(arr).clip(0, 255).astype(np.uint8))
