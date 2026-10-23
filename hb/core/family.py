#!/usr/bin/env python3
"""家族与项目（S7）：
  python3 hb/core/family.py list
  python3 hb/core/family.py init <家族> <项目目录> --title <书名> [--langs zh-CN,en] [--mode carry]
  python3 hb/core/family.py fonts <项目目录>     重新生成项目字体（GB2312 常用字 + 拉丁 + 本项目用到的全部字符）

init 从 families/<家族>/ 复制 design.css（记录版本与哈希到 project.json），生成静态字体与授权文本、
最小作者源骨架（一页封面）、brief.md / page-plan.md 模板与 sources/ 目录。不覆盖已存在的项目文件。
字体来源（按顺序查找）：$HB_FONT_DIR、~/.cache/handbook-designer/fonts、用户字体目录、仓库 dev/fonts。开源字面可用 `fonts.py install` 补齐。
"""
import glob
import hashlib
import json
import os
import re
import shutil
import sys

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
FAMILIES = os.path.join(REPO, "families")
SEARCH = [os.environ.get("HB_FONT_DIR", ""), os.path.expanduser("~/.cache/handbook-designer/fonts"), os.path.join(REPO, "dev", "fonts")]


def charset(project=None):
    cs = set(chr(c) for c in range(0x20, 0x7F)) | set(chr(c) for c in range(0xA0, 0x180))
    cs |= set(chr(c) for c in range(0x2000, 0x2070)) | set(chr(c) for c in range(0x3000, 0x3040)) | set(chr(c) for c in range(0xFF00, 0xFFF0))
    cs |= set("←↑→↓×÷±√∞°′″℃№☆★○●◎◇◆□■△▲※✓✗·•")
    for hi in range(0xA1, 0xF8):
        for lo in range(0xA1, 0xFF):
            try:
                cs.add(bytes([hi, lo]).decode("gb2312"))
            except UnicodeDecodeError:
                pass
    if project:
        for pat in ("*.html", "copy/*.json", "*.css", "lang/*.css", "sources/*.md", "sources/original/*.md"):
            for f in glob.glob(os.path.join(project, pat)):
                try:
                    cs |= set(open(f, encoding="utf-8").read())
                except (OSError, UnicodeDecodeError):
                    pass
    return "".join(sorted(c for c in cs if c.isprintable() or c == " "))


def find_source(name):
    for d in SEARCH:
        if d and os.path.isfile(os.path.join(d, name)):
            return os.path.join(d, name)
    raise SystemExit(f"找不到字体 {name}：将已授权源字体放到 $HB_FONT_DIR 或 ~/.cache/handbook-designer/fonts（见 references/delivery.md）")


def name_static_instance(font, family, weight):
    """Give each static variable-font instance a unique, standards-safe PS name."""
    labels = {200: "ExtraLight", 250: "Weight250", 300: "Light", 400: "Regular", 500: "Medium",
              600: "SemiBold", 700: "Bold", 800: "ExtraBold", 900: "Black"}
    subfamily = labels.get(int(weight), f"Weight{weight}")
    full = f"{family} {subfamily}"
    compact = re.sub(r"[^A-Za-z0-9-]", "", family.replace(" ", ""))
    ps_name = f"{compact}-{weight}"
    unique_id = f"Folio {family} {weight}"
    names = font["name"]
    replacements = {1: family, 2: subfamily, 3: unique_id, 4: full, 6: ps_name, 16: family, 17: subfamily}
    for name_id, value in replacements.items():
        names.names = [record for record in names.names if record.nameID != name_id]
        names.setName(value, name_id, 3, 1, 0x409)
        names.setName(value, name_id, 1, 0, 0)


def build_fonts(project, fam, text):
    out = []
    os.makedirs(os.path.join(project, "assets", "fonts"), exist_ok=True)
    for f in fam["fonts"]:
        src = find_source(f["source"])
        prefix = f["family"].replace(" ", "")
        for w in f["weights"]:
            rel = f"assets/fonts/{prefix}-{w}.ttf"
            font = TTFont(src)
            opts = subset.Options()
            opts.layout_features = ["*"]
            opts.name_IDs = ["*"]
            opts.name_languages = ["*"]
            opts.notdef_outline = True
            opts.hinting = False
            sub = subset.Subsetter(options=opts)
            cmap = font.getBestCmap() or {}
            sub.populate(unicodes=[ord(c) for c in text if ord(c) in cmap])
            sub.subset(font)
            if "fvar" in font:
                loc = {a.axisTag: a.defaultValue for a in font["fvar"].axes}
                loc["wght"] = float(w)
                # STAT tables usually omit intermediate weights such as 250;
                # instance without STAT-name lookup, then assign unique static names.
                font = instancer.instantiateVariableFont(font, loc, updateFontNames=False)
                name_static_instance(font, f["family"], w)
            font.save(os.path.join(project, rel))
            out.append({"family": f["family"], "file": rel, "weight": str(w), "style": "normal"})
            print(f"  {rel}  {os.path.getsize(os.path.join(project, rel)) // 1024} KB")
        license_name = f.get("license")
        if license_name:
            lic = os.path.join(FAMILIES, "licenses", license_name)
            shutil.copyfile(lic, os.path.join(project, "assets", "fonts", license_name))
    return out


def load_family(name):
    d = os.path.join(FAMILIES, name)
    if not os.path.isfile(os.path.join(d, "family.json")):
        raise SystemExit(f"没有家族 {name}（可用：{', '.join(list_families())}）")
    return d, json.load(open(os.path.join(d, "family.json"), encoding="utf-8"))


def list_families():
    return sorted(n for n in os.listdir(FAMILIES) if os.path.isfile(os.path.join(FAMILIES, n, "family.json")))


def write_new(path, content):
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        open(path, "w", encoding="utf-8").write(content)


def init(name, project, title, langs, mode):
    d, fam = load_family(name)
    project = os.path.abspath(project)
    os.makedirs(project, exist_ok=True)
    css = open(os.path.join(d, "design.css"), encoding="utf-8").read()
    write_new(os.path.join(project, "design.css"), css)
    write_new(os.path.join(project, "book.css"), f"/* 《{title}》专属构图。家族原语见 families/{name}/README.md */\n")
    esc = title.replace("&", "&amp;").replace("<", "&lt;")
    write_new(os.path.join(project, "book.html"), f"""<!DOCTYPE html>
<html lang="{langs[0]}">
<head>
<meta charset="utf-8">
<title>{esc}</title>
</head>
<body>
<section class="page" data-page-id="p-cover">
  <div class="area">
    <h1 class="display" data-role="display" data-source-id="title">{esc}</h1>
  </div>
</section>
</body>
</html>
""")
    for lang in langs[1:]:
        write_new(os.path.join(project, "copy", f"{lang}.json"), json.dumps({"contract": 1, "lang": lang, "strings": {"title": title}}, ensure_ascii=False, indent=1) + "\n")
    write_new(os.path.join(project, "brief.md"), "# 简报\n\n- 读者：\n- 阅读任务（读完要做什么）：\n- 已有授权与约束：\n- 重要假设：\n")
    write_new(os.path.join(project, "page-plan.md"), "# 页面计划\n\n视觉主张：\n\n| 页 | 任务 | 内容 | 构图要点 |\n|---|---|---|---|\n")
    os.makedirs(os.path.join(project, "sources"), exist_ok=True)
    fonts = build_fonts(project, fam, charset(project))
    pj = os.path.join(project, "project.json")
    if not os.path.exists(pj):
        p = {"contract": 1, "title": title, "entry": "book.html", "styles": ["design.css", "book.css"], "languages": langs,
             "default_language": langs[0], "canvas": fam["canvas"], "binding": "digital", "first_page": "right", "content_mode": mode,
             "fonts": fonts, "family": {"name": name, "version": fam["version"], "sha256": hashlib.sha256(css.encode()).hexdigest()}}
        json.dump(p, open(pj, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"已从家族 {name} v{fam['version']} 创建项目：{project}")


def refresh_fonts(project):
    project = os.path.abspath(project)
    p = json.load(open(os.path.join(project, "project.json"), encoding="utf-8"))
    name = (p.get("family") or {}).get("name")
    if not name:
        raise SystemExit("project.json 没有记录家族，无法按家族重建字体")
    _, fam = load_family(name)
    p["fonts"] = build_fonts(project, fam, charset(project))
    json.dump(p, open(os.path.join(project, "project.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("字体已更新")


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a[0] not in ("list", "init", "fonts"):
        print(__doc__)
        sys.exit(2)
    if a[0] == "list":
        for n in list_families():
            print(n, "—", load_family(n)[1]["title"])
    elif a[0] == "fonts":
        refresh_fonts(a[1])
    else:
        opt = lambda k, dflt: a[a.index(k) + 1] if k in a else dflt
        init(a[1], a[2], opt("--title", "未命名手册"), opt("--langs", "zh-CN").split(","), opt("--mode", "carry"))
