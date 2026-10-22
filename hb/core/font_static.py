#!/usr/bin/env python3
"""把可变字体实例化为固定字重的静态字体：
python3 hb/core/font_static.py <可变字体> <输出目录> <字重>… [--prefix 文件名前缀]

例：python3 hb/core/font_static.py dev/fonts/NotoSansSC-VF.ttf assets/fonts 400 700
    → assets/fonts/NotoSansSC-400.ttf、NotoSansSC-700.ttf，并更新字体内部名称（如 NotoSansSC-Bold）。
"""
import os
import sys

from fontTools.ttLib import TTFont
from fontTools.varLib import instancer


def instantiate(src, out_dir, weights, prefix=None):
    prefix = prefix or os.path.splitext(os.path.basename(src))[0].replace("-VF", "").replace("[wght]", "")
    os.makedirs(out_dir, exist_ok=True)
    outs = []
    for w in weights:
        font = TTFont(src)
        axes = {a.axisTag: a for a in font["fvar"].axes} if "fvar" in font else {}
        if "wght" not in axes:
            raise SystemExit(f"{src} 没有 wght 轴，不是可变字重字体")
        loc = {"wght": float(w)}
        for tag, a in axes.items():  # 其他轴固定在默认值
            loc.setdefault(tag, a.defaultValue)
        try:
            inst = instancer.instantiateVariableFont(font, loc, updateFontNames="STAT" in font)
        except Exception:
            inst = instancer.instantiateVariableFont(TTFont(src), loc)
        out = os.path.join(out_dir, f"{prefix}-{int(w)}.ttf")
        inst.save(out)
        outs.append(out)
    return outs


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    prefix = None
    if "--prefix" in sys.argv:
        prefix = sys.argv[sys.argv.index("--prefix") + 1]
        args.remove(prefix)
    if len(args) < 3:
        print(__doc__)
        sys.exit(2)
    for o in instantiate(args[0], args[1], [int(x) for x in args[2:]], prefix):
        print(o)
