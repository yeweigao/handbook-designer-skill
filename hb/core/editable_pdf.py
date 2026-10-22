#!/usr/bin/env python3
"""可编辑 PDF（S8）：python3 hb/core/editable_pdf.py <项目> <普通版.pdf> <输出.pdf>

浏览器导出的 PDF 只嵌入书里用到的字（子集），在 PDF 编辑器里加没出现过的字会缺字形。
这里不重新渲染：把 PDF 里每个嵌入字体替换为同一项目字体的扩充版——GB2312 全部常用汉字与符号 + 拉丁字符 +
本书用字，用 fontTools 保留原字形编号（retain_gids），因此页面内容流里的字形编号不变，版式与普通版完全一致；
同时补全宽度表、去掉子集前缀（ABCDEF+）。
支持范围：Chrome 导出、字体为项目声明的静态 TrueType/OpenType 字体。替换后的结果由 export 实测（栅格与文字层一致）。
"""
import io
import json
import os
import sys

import pikepdf
from fontTools import subset
from fontTools.ttLib import TTFont


def common_charset():
    cs = set(chr(c) for c in range(0x20, 0x7F)) | set(chr(c) for c in range(0xA0, 0x180))
    for hi in range(0xA1, 0xF8):
        for lo in range(0xA1, 0xFF):
            try:
                cs.add(bytes([hi, lo]).decode("gb2312"))
            except UnicodeDecodeError:
                pass
    cs |= set("　、。·—～‖…‘’“”〔〕〈〉《》「」『』〖〗【】±×÷√∞°′″℃％‰§№☆★○●◎◇◆□■△▲※→←↑↓！＂＃￥＆＇（）＊＋，－．／０１２３４５６７８９：；＜＝＞？＠［＼］＾＿｀｛｜｝￣")
    return "".join(sorted(cs))


def expanded(path, extra_text):
    font = TTFont(path)
    opts = subset.Options()
    opts.retain_gids = True
    opts.layout_features = ["*"]
    opts.name_IDs = ["*"]
    opts.name_languages = ["*"]
    opts.notdef_outline = True
    opts.glyph_names = False
    opts.hinting = False   # Chrome（Skia/HarfBuzz）嵌入子集时去掉 hinting；保持一致，栅格才逐像素相同
    sub = subset.Subsetter(options=opts)
    cmap = font.getBestCmap() or {}
    sub.populate(unicodes=[ord(c) for c in set(common_charset() + extra_text) if ord(c) in cmap])
    sub.subset(font)
    return font


def parse_w(w):
    """解析 CIDFont 的 /W 数组：[c [w1 w2 …]] 或 [c_first c_last w]。"""
    out = {}
    if w is None:
        return out
    items = list(w)
    i = 0
    while i < len(items):
        c = int(items[i])
        nxt = items[i + 1]
        if isinstance(nxt, pikepdf.Array):
            for k, v in enumerate(nxt):
                out[c + k] = float(v)
            i += 2
        else:
            for k in range(c, int(nxt) + 1):
                out[k] = float(items[i + 2])
            i += 3
    return out


def main(project, src, out):
    project = os.path.abspath(project)
    proj = json.load(open(os.path.join(project, "project.json"), encoding="utf-8"))
    byname = {}
    for f in proj["fonts"]:
        p = os.path.join(project, f["file"])
        byname[TTFont(p, lazy=True)["name"].getDebugName(6)] = p
    pdf = pikepdf.open(src)
    used = ""
    try:
        import subprocess
        used = subprocess.run(["pdftotext", "-raw", "-enc", "UTF-8", src, "-"], capture_output=True, text=True).stdout
    except FileNotFoundError:
        pass
    cache, replaced, missing = {}, 0, set()
    for obj in pdf.objects:
        if not isinstance(obj, pikepdf.Dictionary) or obj.get("/Subtype") != "/Type0":
            continue
        base = str(obj.BaseFont).lstrip("/")
        clean = base.split("+", 1)[-1]
        path = byname.get(clean)
        if not path:
            missing.add(clean)
            continue
        desc = obj.DescendantFonts[0]
        if desc.get("/Subtype") != "/CIDFontType2":
            missing.add(clean + "（非 TrueType 字形，未替换）")
            continue
        if clean not in cache:
            font = expanded(path, used)
            buf = io.BytesIO()
            font.flavor = None
            font.save(buf)
            upm = font["head"].unitsPerEm
            hm = font["hmtx"].metrics
            order = font.getGlyphOrder()
            cache[clean] = (pdf.make_stream(buf.getvalue()), [round(hm[g][0] * 1000 / upm) if g in hm else 0 for g in order], len(order))
        stream, base_w, _ = cache[clean]
        # 宽度：保留 Chrome 写入的原值（PDF 阅读器按它排列字形，取整方式可能与 hmtx 不同），只给新增字形补宽度
        merged = list(base_w)
        for cid, w in parse_w(desc.get("/W")).items():
            if cid < len(merged):
                merged[cid] = w
        widths = pikepdf.Array([0, pikepdf.Array(merged)])
        fd = desc.FontDescriptor
        fd.FontFile2 = stream
        if "/CIDSet" in fd:
            del fd["/CIDSet"]
        desc.W = widths
        desc.CIDToGIDMap = pikepdf.Name("/Identity")
        name = pikepdf.Name("/" + clean)
        obj.BaseFont = name
        desc.BaseFont = name
        fd.FontName = name
        replaced += 1
    pdf.save(out, compress_streams=True, object_stream_mode=pikepdf.ObjectStreamMode.generate)
    report = {"replaced": replaced, "fonts": sorted(cache), "glyphs": {k: v[2] for k, v in cache.items()}, "not_replaced": sorted(missing),
              "bytes": os.path.getsize(out)}
    print(json.dumps(report, ensure_ascii=False))
    return 0 if not missing else 1


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(*sys.argv[1:]))
