#!/usr/bin/env python3
"""最终 PDF 检查（S4）：python3 hb/core/postflight.py <项目> <构建 ID> <语言>

检查对象是 .build/<构建 ID>/<语言>/book.pdf 本身：哈希与渲染清单一致、页数、
每页 MediaBox/TrimBox 物理尺寸、装订页数、字体全部嵌入且无 Type 3；
并逐页抽取文字写入 pdf-text.json 供原文覆盖检查。
缺少 pikepdf 或 poppler 时相应项记为 unverified（硬项），不当作通过。
输出 .qa/<构建 ID>/<语言>/postflight.json；存在硬项 fail/unverified 时退出码 1。
环境变量 HB_POSTFLIGHT_NO_PIKEPDF=1 可模拟缺少 pikepdf（测试用）。
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys

MM = 72 / 25.4
TOL_MM = 0.05


def item(id_, status, msg, severity="hard", page=None, target=None, evidence=None):
    return {"id": id_, "status": status, "severity": severity, "page": page, "target": target,
            "evidence": evidence or {}, "message": msg}


def load_pikepdf():
    if os.environ.get("HB_POSTFLIGHT_NO_PIKEPDF") == "1":
        return None
    try:
        import pikepdf
        return pikepdf
    except ImportError:
        return None


def walk_fonts(res, seen, out):
    if res is None:
        return
    fonts = res.get("/Font")
    if fonts is not None:
        for _, f in fonts.items():
            key = f.objgen if hasattr(f, "objgen") else id(f)
            if key in seen:
                continue
            seen.add(key)
            out.append(f)
    xobjs = res.get("/XObject")
    if xobjs is not None:
        for _, x in xobjs.items():
            key = x.objgen if hasattr(x, "objgen") else id(x)
            if key in seen:
                continue
            seen.add(key)
            if x.get("/Subtype") == "/Form" and "/Resources" in x:
                walk_fonts(x["/Resources"], seen, out)


def font_info(f):
    sub = str(f.get("/Subtype", ""))
    name = str(f.get("/BaseFont", "")).lstrip("/")
    fd = None
    if sub == "/Type0":
        desc = f.get("/DescendantFonts")
        if desc is not None and len(desc):
            fd = desc[0].get("/FontDescriptor")
    else:
        fd = f.get("/FontDescriptor")
    embedded = fd is not None and any(k in fd for k in ("/FontFile", "/FontFile2", "/FontFile3"))
    return {"name": name, "subtype": sub.lstrip("/"), "embedded": embedded or sub == "/Type3"}


def main(project, build, lang):
    project = os.path.abspath(project)
    with open(os.path.join(project, "project.json"), encoding="utf-8") as fh:
        proj = json.load(fh)
    bdir = os.path.join(project, ".build", build, lang)
    qa = os.path.join(project, ".qa", build, lang)
    os.makedirs(qa, exist_ok=True)
    items = []
    pdf = os.path.join(bdir, "book.pdf")
    man_path = os.path.join(bdir, "manifest.json")
    if not os.path.isfile(man_path) or not os.path.isfile(pdf):
        items.append(item("pdf.exists", "fail", f"没有 {lang} 的 PDF 或渲染清单：先运行 render"))
        return write(qa, build, lang, items)
    with open(man_path, encoding="utf-8") as fh:
        man = json.load(fh)
    sha = hashlib.sha256(open(pdf, "rb").read()).hexdigest()
    if not man.get("pdf") or man["pdf"].get("sha256") != sha:
        items.append(item("pdf.hash", "fail", "PDF 与渲染清单记录的哈希不一致：渲染后被改动过，或渲染失败",
                          evidence={"pdf_sha256": sha, "manifest": (man.get("pdf") or {}).get("sha256")}))
    else:
        items.append(item("pdf.hash", "pass", "PDF 与渲染清单一致", evidence={"pdf_sha256": sha}))

    c = proj["canvas"]
    trim_w, trim_h = c["trim_mm"]
    bleed = c["bleed_mm"]
    media_w, media_h = trim_w + 2 * bleed, trim_h + 2 * bleed
    expected_pages = man.get("page_count")

    pk = load_pikepdf()
    if pk is None:
        for id_ in ("pdf.pages", "pdf.boxes", "pdf.binding", "pdf.fonts"):
            items.append(item(id_, "unverified", "缺少 pikepdf，无法检查 PDF 结构（pip install pikepdf）"))
    else:
        with pk.open(pdf) as d:
            n = len(d.pages)
            if n != expected_pages:
                items.append(item("pdf.pages", "fail", f"PDF 有 {n} 页，作者源有 {expected_pages} 个 .page",
                                  evidence={"pdf_pages": n, "source_pages": expected_pages}))
            else:
                items.append(item("pdf.pages", "pass", f"{n} 页", evidence={"pdf_pages": n}))
            binding = proj.get("binding")
            if binding == "saddle" and n % 4:
                items.append(item("pdf.binding", "fail", f"骑马钉需要 4 的倍数页，实际 {n} 页", evidence={"pages": n}))
            elif binding == "perfect" and n % 2:
                items.append(item("pdf.binding", "fail", f"胶装需要偶数页，实际 {n} 页", evidence={"pages": n}))
            else:
                items.append(item("pdf.binding", "pass", f"{binding}：{n} 页"))
            bad = []
            for i, pg in enumerate(d.pages, 1):
                mb = [float(v) for v in pg.mediabox]
                w, h = (mb[2] - mb[0]) / MM, (mb[3] - mb[1]) / MM
                if abs(w - media_w) > TOL_MM or abs(h - media_h) > TOL_MM:
                    bad.append(item("pdf.boxes", "fail", f"第 {i} 页 MediaBox {w:.2f}×{h:.2f}mm，应为 {media_w}×{media_h}mm",
                                    page=i, evidence={"media_mm": [round(w, 3), round(h, 3)]}))
                    continue
                if "/TrimBox" not in pg.obj:
                    bad.append(item("pdf.boxes", "fail", f"第 {i} 页缺少 TrimBox", page=i))
                    continue
                tb = [float(v) for v in pg.obj["/TrimBox"]]
                tw, th = (tb[2] - tb[0]) / MM, (tb[3] - tb[1]) / MM
                off = [(tb[0] - mb[0]) / MM, (tb[1] - mb[1]) / MM, (mb[2] - tb[2]) / MM, (mb[3] - tb[3]) / MM]
                if abs(tw - trim_w) > TOL_MM or abs(th - trim_h) > TOL_MM or any(abs(o - bleed) > TOL_MM for o in off):
                    bad.append(item("pdf.boxes", "fail", f"第 {i} 页 TrimBox {tw:.2f}×{th:.2f}mm 与成品 {trim_w}×{trim_h}mm / 出血 {bleed}mm 不符",
                                    page=i, evidence={"trim_mm": [round(tw, 3), round(th, 3)], "offsets_mm": [round(o, 3) for o in off]}))
            items.extend(bad or [item("pdf.boxes", "pass", f"每页媒体 {media_w}×{media_h}mm，成品 {trim_w}×{trim_h}mm")])
            fonts, seen = [], set()
            for pg in d.pages:
                walk_fonts(pg.obj.get("/Resources"), seen, fonts)
            info = [font_info(f) for f in fonts]
            t3 = sorted({f["name"] or "(未命名)" for f in info if f["subtype"] == "Type3"})
            unemb = sorted({f["name"] for f in info if not f["embedded"]})
            if t3:
                items.append(item("pdf.fonts", "fail", f"出现 {len(t3)} 个 Type 3 字体（通常是可变字体或位图字形）", evidence={"type3": t3}))
            if unemb:
                items.append(item("pdf.fonts", "fail", f"字体未嵌入：{'、'.join(unemb)}", evidence={"not_embedded": unemb}))
            if not t3 and not unemb:
                items.append(item("pdf.fonts", "pass", f"{len(info)} 个字体全部嵌入，无 Type 3",
                                  evidence={"fonts": sorted({f['name'] for f in info})}))

    # 逐页文字（供原文覆盖检查）
    if shutil.which("pdftotext"):
        r = subprocess.run(["pdftotext", "-enc", "UTF-8", pdf, "-"], capture_output=True, text=True)
        pages = r.stdout.split("\f")
        if pages and not pages[-1].strip():
            pages = pages[:-1]
        with open(os.path.join(qa, "pdf-text.json"), "w", encoding="utf-8") as fh:
            json.dump({"build_id": build, "lang": lang, "pdf_sha256": sha, "pages": pages}, fh, ensure_ascii=False, indent=1)
        items.append(item("pdf.text", "pass", f"已抽取 {len(pages)} 页文字", evidence={"file": "pdf-text.json"}))
    else:
        items.append(item("pdf.text", "unverified", "缺少 pdftotext（poppler），无法抽取 PDF 文字核对原文"))
    return write(qa, build, lang, items, sha)


def write(qa, build, lang, items, sha=None):
    blocking = [i for i in items if i["severity"] == "hard" and i["status"] != "pass"]
    rep = {"contract": 1, "check": "postflight", "build_id": build, "lang": lang, "pdf_sha256": sha,
           "status": "fail" if blocking else "pass", "items": items}
    with open(os.path.join(qa, "postflight.json"), "w", encoding="utf-8") as fh:
        json.dump(rep, fh, ensure_ascii=False, indent=2)
    for i in items:
        if i["status"] != "pass":
            print(f"{i['status'].upper()} {i['id']}: {i['message']}")
    print(f"postflight {lang}: {'通过' if not blocking else '不通过'}")
    return 1 if blocking else 0


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(*sys.argv[1:]))
