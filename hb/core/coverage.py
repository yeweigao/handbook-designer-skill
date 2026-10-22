#!/usr/bin/env python3
"""原文覆盖与素材来源（S5）：python3 hb/core/coverage.py <项目> <构建 ID> <语言>

依据三方证据判断内容是否真的展示给读者：
  sources/segments.json（原文）↔ 快照中可见的内容节点（排除 measure.json 判为不可见的）↔ 最终 PDF 文字（pdf-text.json）。
默认语言：MISSING（原文句子没在可见内容里）、PDF 缺失（可见内容没进 PDF 文字层）、ORDER、EXTRA（不在原文里的内容句）、
         无出处数字（提示）。其他语言：可见译文必须进入该语言 PDF。
素材：非装饰图片必须在 sources/assets.json 登记来源与授权。
内容模式（project.json content_mode）决定严重级别：
  carry、translate  MISSING 硬项；EXTRA 硬项（aux 角色或 sources/adapt.json 声明的除外）；ORDER 提示
                   （translate：默认语言是原文，按搬运检查；其他语言只核对译文是否进入 PDF）
  frozen           MISSING / EXTRA / ORDER 全为硬项，不接受 adapt.json
  polish           MISSING / EXTRA / ORDER 为提示（需另附逐段对照）
sources/adapt.json：{"omit": [{"segment": "s0003", "reason": "…"}], "strip": [{"segment": "s0010", "text": "亮点一："}],
                     "extra": [{"content": "cover-eyebrow", "reason": "…"}]}
输出 .qa/<构建 ID>/<语言>/coverage.json；硬项 fail 或 unverified 时退出码 1。
"""
import html
import json
import os
import re
import sys
import unicodedata
from html.parser import HTMLParser

STRIP = re.compile("[" + re.escape("｜→•✓✗▶☐—·-–‐‑：:，,。.！!？?；;（）()[]【】“”\"「」『』/、《》'‘’*\\#|>_＿…~～") + r"\s\u00ad\u200b\u2060\ufeff]")
SPLIT = re.compile(r"(?<=[。！？!?；;])|\n|(?<=[.!?])\s+")
NUM = re.compile(r"\d[\d,，.:：/%-]*\d|\d")


def norm(s):
    s = unicodedata.normalize("NFKC", s)
    s = re.sub(r"-\s*\n\s*", "", s)  # 英文断词连字符
    return STRIP.sub("", s).lower()


def sentences(text):
    return [t for t in (x.strip() for x in SPLIT.split(text)) if t and len(norm(t)) >= 2]


def item(id_, status, severity, msg, page=None, target=None, evidence=None):
    return {"id": id_, "status": status, "severity": severity, "page": page, "target": target,
            "evidence": evidence or {}, "message": msg}


VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}


class Snapshot(HTMLParser):
    """按文档顺序收集内容节点（含文字）与图片。栈元素记录它所属的内容节点编号。"""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.nodes, self.images, self.page = [], [], [], None

    def _role(self, a):
        if "data-role" in a:
            return a["data-role"]
        for _, pa, _ in reversed(self.stack):
            if "data-role" in pa:
                return pa["data-role"]
        return "body"

    def _current(self):
        for _, _, idx in reversed(self.stack):
            if idx is not None:
                return idx
        return None

    def handle_starttag(self, tag, attrs):
        a = {k: (v or "") for k, v in attrs}
        if "page" in a.get("class", "").split() and "data-page-id" in a:
            self.page = a["data-page-id"]
        if tag == "img":
            self.images.append({"page": self.page, "src": a.get("src", ""), "asset": a.get("data-asset"),
                                "edit": a.get("data-edit-id"), "deco": self._role(a) == "deco"})
        if tag == "br":
            cur = self._current()
            if cur is not None:
                self.nodes[cur]["text"] += " "
        idx = None
        if "data-source-id" in a:
            idx = len(self.nodes)
            self.nodes.append({"id": a["data-source-id"], "fragment": a.get("data-fragment"), "repeat": "data-repeat" in a,
                               "role": self._role(a), "page": self.page, "text": ""})
        if tag not in VOID:
            self.stack.append((tag, a, idx))

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break

    def handle_data(self, data):
        cur = self._current()
        if cur is not None:
            self.nodes[cur]["text"] += data


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def main(project, build, lang):
    project = os.path.abspath(project)
    proj = load(os.path.join(project, "project.json"))
    mode = proj.get("content_mode", "carry")
    default = proj["default_language"]
    qa = os.path.join(project, ".qa", build, lang)
    os.makedirs(qa, exist_ok=True)
    items = []
    snap_path = os.path.join(project, ".build", build, lang, "snapshot.html")
    if not os.path.exists(snap_path):
        items.append(item("coverage.input", "unverified", "hard", "没有渲染快照，无法检查内容覆盖"))
        return write(qa, build, lang, items, {})
    sp = Snapshot()
    with open(snap_path, encoding="utf-8") as f:
        sp.feed(f.read())
    nodes = sp.nodes
    for n in nodes:
        n["text"] = html.unescape(n["text"]).strip()

    measure_path = os.path.join(qa, "measure.json")
    hidden = set()
    if os.path.exists(measure_path):
        for i in load(measure_path)["items"]:
            if i["id"] == "content.hidden" and i["status"] == "fail":
                hidden.add(i["target"])
    else:
        items.append(item("coverage.input", "unverified", "hard", "缺少 measure.json：无法排除不可见内容，先运行 measure"))
    pdf_path = os.path.join(qa, "pdf-text.json")
    pdf_norm = None
    if os.path.exists(pdf_path):
        pdf_norm = norm("\n".join(load(pdf_path)["pages"]))
    else:
        items.append(item("coverage.pdf", "unverified", "hard", "缺少 pdf-text.json：无法核对 PDF 文字层，先运行 postflight"))

    visible = [n for n in nodes if n["id"] not in hidden and not n["repeat"]]
    stats = {"content_nodes": len(nodes), "visible": len(visible), "hidden": sorted(hidden)}

    # 1. 可见内容必须进入最终 PDF 文字层（所有语言）
    if pdf_norm is not None:
        lost = []
        for n in visible:
            for s in sentences(n["text"]):
                if norm(s) not in pdf_norm:
                    lost.append((n, s))
        for n, s in lost[:50]:
            items.append(item("coverage.pdf", "fail", "hard", f"可见内容没有进入 PDF 文字层：「{s[:40]}」", n["page"], n["id"]))
        if not lost:
            items.append(item("coverage.pdf", "pass", "hard", "可见内容全部在 PDF 文字层中"))

    if lang == default:
        seg_path = os.path.join(project, "sources", "segments.json")
        if not os.path.exists(seg_path):
            items.append(item("coverage.source", "unverified", "hard",
                              "没有 sources/segments.json：原文未提取，无法核对内容完整性（python3 hb/core/extract.py <原稿> <项目>）"))
        else:
            check_source(project, proj, mode, visible, items, stats)
    check_assets(project, sp.images, items)
    return write(qa, build, lang, items, stats)


def check_source(project, proj, mode, visible, items, stats):
    segs = [s for s in load(os.path.join(project, "sources", "segments.json"))["segments"] if s["kind"] != "artifact"]
    adapt = {"omit": [], "strip": [], "extra": []}
    apath = os.path.join(project, "sources", "adapt.json")
    if os.path.exists(apath):
        if mode == "frozen":
            items.append(item("coverage.adapt", "fail", "hard", "内容冻结模式不接受 sources/adapt.json"))
        else:
            adapt.update(load(apath))
    omit = {o["segment"] for o in adapt.get("omit", [])}
    # 用户本人的改动（在线编辑写回）：改后的文字视为原文，改前的句子不再要求出现。所有内容模式都承认。
    user_new, user_old = [], set()
    upath = os.path.join(project, "sources", "user-edits.json")
    if os.path.exists(upath):
        for e in load(upath).get("edits", []):
            if e.get("lang") in (None, proj["default_language"]):
                user_new.append(e.get("new", ""))
                user_old.update(norm(x) for x in sentences(e.get("old", "")))
        stats["user_edits"] = len(load(upath).get("edits", []))
    strip = {}
    for st in adapt.get("strip", []):
        strip.setdefault(st["segment"], []).append(st["text"])
    extra_ok = {e["content"] for e in adapt.get("extra", [])}
    hard_missing = mode in ("carry", "translate", "frozen")
    order_sev = "hard" if mode == "frozen" else "hint"
    extra_sev = "hard" if mode in ("carry", "translate", "frozen") else "hint"

    book = norm("".join(n["text"] for n in visible))
    ref_parts = []
    missing, positions = [], []
    for sg in segs:
        if sg["id"] in omit:
            continue
        text = sg["text"]
        for t in strip.get(sg["id"], []):
            text = text.replace(t, "")
        ref_parts.append(text)
        for s in sentences(text):
            pos = book.find(norm(s))
            if pos < 0 and norm(s) in user_old:
                continue
            if pos < 0:
                missing.append((sg, s))
            else:
                positions.append((pos, sg, s))
    for sg, s in missing[:80]:
        items.append(item("coverage.missing", "fail", "hard" if hard_missing else "hint",
                          f"原文 {sg['id']} 没有出现在可见内容里：「{s[:40]}」", target=sg["id"], evidence={"segment": sg["id"]}))
    if not missing:
        items.append(item("coverage.missing", "pass", "hard", "原文全部出现在可见内容中"))
    inversions, top = [], -1
    for pos, sg, s in positions:
        if pos < top:
            inversions.append((sg, s))
        top = max(top, pos)
    for sg, s in inversions[:30]:
        items.append(item("coverage.order", "fail", order_sev, f"顺序与原文不同：{sg['id']}「{s[:30]}」排到了后文之前（有意调整请逐条确认）",
                          target=sg["id"]))
    if not inversions:
        items.append(item("coverage.order", "pass", order_sev, "顺序与原文一致"))

    facts = ""
    fpath = os.path.join(project, "sources", "facts.md")
    if os.path.exists(fpath):
        with open(fpath, encoding="utf-8") as f:
            facts = f.read()
    ref = norm("\n".join(ref_parts + user_new))
    ref_raw = re.sub(r"[\s,，]", "", unicodedata.normalize("NFKC", "\n".join(ref_parts) + facts))
    extras, nums = [], []
    for n in visible:
        allowed = n["id"] in extra_ok or (mode in ("carry", "translate") and n["role"] == "aux")
        for s in sentences(n["text"]):
            if norm(s) not in ref and not allowed:
                extras.append((n, s))
        for m in NUM.finditer(unicodedata.normalize("NFKC", n["text"])):
            t = m.group(0)
            if len(re.sub(r"\D", "", t)) >= 2 and re.sub(r"[\s,，]", "", t) not in ref_raw:
                nums.append((n, t))
    for n, s in extras[:50]:
        items.append(item("coverage.extra", "fail", extra_sev, f"内容不在原文里：「{s[:40]}」（自创句删掉；结构性文字标 data-role=\"aux\" 或在 adapt.json 声明）",
                          n["page"], n["id"]))
    if not extras:
        items.append(item("coverage.extra", "pass", extra_sev, "没有原文以外的内容句"))
    for n, t in nums[:30]:
        items.append(item("facts.number", "fail", "hint", f"[无出处数字] {t}：原文与 sources/facts.md 里都没有", n["page"], n["id"]))
    stats.update({"segments": len(segs), "omitted": len(omit), "missing": len(missing), "order": len(inversions),
                  "extra": len(extras), "unsourced_numbers": len(nums)})


def check_assets(project, images, items):
    apath = os.path.join(project, "sources", "assets.json")
    assets = load(apath).get("assets", {}) if os.path.exists(apath) else {}
    problems = 0
    for im in images:
        sev = "hint" if im["deco"] else "hard"
        aid = im["asset"]
        if not aid or aid not in assets:
            problems += 1
            items.append(item("asset.unregistered", "unverified", sev, f"图片 {im['src']} 没有在 sources/assets.json 登记（加 data-asset 并写明来源与授权）",
                              im["page"], im["edit"] or im["src"]))
            continue
        a = assets[aid]
        if not (a.get("source") or "").strip() or not (a.get("license") or "").strip():
            problems += 1
            items.append(item("asset.license", "unverified", sev, f"素材 {aid} 的来源或授权未确认（原稿抽取的照片也需确认商用版权与肖像权）",
                              im["page"], aid, {"source": a.get("source"), "license": a.get("license")}))
        if a.get("file") and os.path.normpath(a["file"]) != os.path.normpath(im["src"]):
            items.append(item("asset.file", "fail", "hint", f"素材 {aid} 登记的文件 {a['file']} 与页面使用的 {im['src']} 不同", im["page"], aid))
    if not problems:
        items.append(item("asset.license", "pass", "hard", f"{len(images)} 处图片都已登记来源与授权"))


def write(qa, build, lang, items, stats):
    blocking = [i for i in items if i["severity"] == "hard" and i["status"] != "pass"]
    rep = {"contract": 1, "check": "coverage", "build_id": build, "lang": lang, "status": "fail" if blocking else "pass",
           "stats": stats, "items": items}
    with open(os.path.join(qa, "coverage.json"), "w", encoding="utf-8") as f:
        json.dump(rep, f, ensure_ascii=False, indent=2)
    for i in items:
        if i["status"] != "pass":
            print(f"{i['severity']} {i['status'].upper()} {i['id']}: {i['message']}")
    print(f"coverage {lang}: {'通过' if not blocking else '不通过'}")
    return 1 if blocking else 0


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(*sys.argv[1:]))
