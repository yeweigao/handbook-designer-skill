#!/usr/bin/env python3
"""原稿提取（S5）：python3 hb/core/extract.py <原稿> <项目目录>

把 .md / .txt / .docx / .pdf / .pptx 提取为项目 sources/ 下的素材，不决定任何页面结构：
  sources/original/<原稿>    原稿副本
  sources/source.md          可读原文（PPT/PDF 带 <!-- 第 N 页 --> 注释）
  sources/segments.json      逐段稳定 ID：{id, kind, text, origin}；kind = heading / para / item / cell / artifact
  sources/images/            抽出的图片（PPT/Word/PDF）；images.md 为图片说明
  sources/assets.json        素材清单：新图片登记为待确认来源与授权（license 留空，交付前必须补全）
已有 segments.json 时整体重建（同一原稿得到相同 ID）；assets.json 只追加，不覆盖已填写的条目。
"""
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PAGENO = re.compile(r"^\d{1,2}\s*/\s*\d{1,2}$")   # 「02 / 23」式页脚；单独的短数字可能是正文统计，只按 Office 解析的版面位置判断
PAGE_MARK = re.compile(r"第\s*(\d+)\s*页")


def to_md(src):
    """.md/.txt 直接读；.docx/.pdf 依次尝试 markitdown → pandoc → python-docx。"""
    low = src.lower()
    if low.endswith((".md", ".txt", ".markdown")):
        with open(src, encoding="utf-8") as f:
            return f.read()
    for cmd in (["markitdown", src], ["pandoc", src, "-t", "gfm", "--wrap=none"]):
        try:
            r = subprocess.run(cmd, capture_output=True, text=True)
            if r.returncode == 0 and r.stdout.strip():
                return r.stdout
        except FileNotFoundError:
            pass
    if low.endswith(".docx"):
        try:
            import docx
        except ImportError:
            docx = None
        if docx:
            d = docx.Document(src)
            out = []
            for p in d.paragraphs:
                st = (p.style.name or "").lower()
                t = p.text.strip()
                if not t:
                    out.append("")
                    continue
                lv = next((int(c) for c in st if c.isdigit()), 1) if st.startswith(("heading", "标题")) else 0
                out.append(("#" * min(lv, 3) + " " if lv else "- " if "list" in st else "") + t)
            for tb in d.tables:
                for row in tb.rows:
                    out.append("| " + " | ".join(c.text.strip() for c in row.cells) + " |")
            return "\n".join(out)
    raise SystemExit(f"无法转换 {src}：请安装 markitdown（pip install 'markitdown[all]'）或 pandoc，或先另存为 .md/.txt")


def clean(s):
    s = re.sub(r"\*\*|__|`", "", s)
    s = re.sub(r"\\(?=[\\`*_{}\[\]()#+\-.!|>~<])", "", s)
    return s.strip()


def segment(md, artifacts=()):
    segs, para, page = [], [], None

    def flush():
        if para:
            text = clean("\n".join(para))
            if text:
                segs.append({"kind": "para", "text": text, "origin": {"page": page}})
            para.clear()

    for raw in md.splitlines():
        s = raw.strip()
        cm = re.match(r"^<!--(.*?)-->$", s)
        if cm:
            flush()
            m = PAGE_MARK.search(cm.group(1))
            if m:
                page = int(m.group(1))
            continue
        if not s or re.fullmatch(r"!\[[^\]]*\]\([^)]*\)|<img\b[^>]*>", s):
            flush()
            continue
        h = re.match(r"^(#{1,6})\s+(.*)$", s)
        li = re.match(r"^(?:[-*+•▶✓☐]|\d{1,3}[.)、])\s+(.*)$", s)
        if h:
            flush()
            segs.append({"kind": "heading", "text": clean(h.group(2)), "origin": {"page": page, "level": len(h.group(1))}})
        elif s.startswith("|") and s.endswith("|"):
            flush()
            cells = [clean(c) for c in s.strip("|").split("|")]
            if all(re.fullmatch(r":?-{2,}:?", c or "--") for c in cells):
                continue
            for c in cells:
                if c:
                    segs.append({"kind": "cell", "text": c, "origin": {"page": page}})
        elif li:
            flush()
            segs.append({"kind": "item", "text": clean(li.group(1)), "origin": {"page": page}})
        else:
            para.append(s)
    flush()
    for i, sg in enumerate(segs, 1):
        sg["id"] = f"s{i:04d}"
        if PAGENO.match(sg["text"]) or sg["text"] in artifacts:
            sg["kind"] = "artifact"
    return [{"id": s["id"], "kind": s["kind"], "text": s["text"], "origin": s["origin"]} for s in segs]


def main(src, project):
    src = os.path.abspath(src)
    project = os.path.abspath(project)
    sdir = os.path.join(project, "sources")
    os.makedirs(os.path.join(sdir, "original"), exist_ok=True)
    dst = os.path.join(sdir, "original", os.path.basename(src))
    if os.path.abspath(dst) != src:
        shutil.copy2(src, dst)
    low = src.lower()
    artifacts, images_md = set(), None
    with tempfile.TemporaryDirectory() as tmp:
        if low.endswith((".pptx", ".docx", ".pdf")):
            args = [sys.executable, os.path.join(HERE, "office_extract.py"), src, tmp]
            if not low.endswith(".pptx"):
                args.append("--images-only")
            r = subprocess.run(args, capture_output=True, text=True)
            if r.returncode != 0:
                print(r.stdout + r.stderr)
                raise SystemExit("原稿解析失败")
        if low.endswith(".pptx"):
            with open(os.path.join(tmp, "doc.md"), encoding="utf-8") as f:
                md = f.read()
        else:
            md = to_md(src)
        art = os.path.join(tmp, ".qa", "artifacts.txt")
        if os.path.exists(art):
            for line in open(art, encoding="utf-8"):
                line = line.strip()
                if line and not line.startswith("#"):
                    artifacts.add(line.split("：", 1)[-1].strip())
        photos = os.path.join(tmp, "photos")
        if os.path.isdir(photos):
            dst = os.path.join(sdir, "images")
            os.makedirs(dst, exist_ok=True)
            for f in glob.glob(os.path.join(photos, "*")):
                if os.path.isfile(f):
                    shutil.copy2(f, dst)
        if os.path.exists(os.path.join(tmp, "images.md")):
            images_md = os.path.join(sdir, "images.md")
            shutil.copy2(os.path.join(tmp, "images.md"), images_md)
        notes = os.path.join(tmp, "notes.md")
        if os.path.exists(notes):
            shutil.copy2(notes, os.path.join(sdir, "notes.md"))

    with open(os.path.join(sdir, "source.md"), "w", encoding="utf-8") as f:
        f.write(md)
    segs = segment(md, artifacts)
    with open(os.path.join(sdir, "segments.json"), "w", encoding="utf-8") as f:
        json.dump({"contract": 1, "source": os.path.basename(src), "segments": segs}, f, ensure_ascii=False, indent=1)

    # 素材清单：只追加新图片，已填写的来源与授权不覆盖
    apath = os.path.join(sdir, "assets.json")
    assets = {"contract": 1, "assets": {}}
    if os.path.exists(apath):
        with open(apath, encoding="utf-8") as f:
            assets = json.load(f)
    imgdir = os.path.join(sdir, "images")
    added = 0
    for f in sorted(glob.glob(os.path.join(imgdir, "*"))) if os.path.isdir(imgdir) else []:
        aid = os.path.splitext(os.path.basename(f))[0]
        if aid not in assets["assets"]:
            assets["assets"][aid] = {"file": os.path.relpath(f, project).replace(os.sep, "/"),
                                     "source": f"原稿 {os.path.basename(src)}", "license": "", "credit": ""}
            added += 1
    with open(apath, "w", encoding="utf-8") as f:
        json.dump(assets, f, ensure_ascii=False, indent=2)
    kinds = {}
    for s in segs:
        kinds[s["kind"]] = kinds.get(s["kind"], 0) + 1
    print(f"提取 {os.path.basename(src)}：{len(segs)} 段 {kinds}；图片 {added} 张新登记（来源/授权待确认）")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(sys.argv[1], sys.argv[2]))
