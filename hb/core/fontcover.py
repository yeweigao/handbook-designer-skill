#!/usr/bin/env python3
"""字形覆盖：从标准输入读 {"fonts": [字体文件], "texts": {键: 文本}}，
输出 {键: "没有任何声明字体覆盖的字符"}。供 measure.mjs 说明字体回退的具体字符。"""
import json
import sys

from fontTools.ttLib import TTFont


def main():
    req = json.load(sys.stdin)
    covered = set()
    for f in req["fonts"]:
        try:
            covered |= set(TTFont(f, lazy=True).getBestCmap() or {})
        except Exception:
            pass
    out = {}
    for k, text in req["texts"].items():
        miss = sorted({c for c in text if not c.isspace() and ord(c) not in covered})
        out[k] = "".join(miss)
    json.dump(out, sys.stdout, ensure_ascii=False)


if __name__ == "__main__":
    main()
