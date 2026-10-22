#!/usr/bin/env python3
"""Folio 修改写回（S9）：python3 hb/core/folio_sync.py <项目> <Folio 下载的 HTML> [--dry-run]

三方比对：编辑包基准（.build/<构建 ID>/<语言>/folio-base.html）↔ Folio 交回的 HTML ↔ 当前作者源。
  改字   有 data-source-id 的内容节点：默认语言写回 book.html（按片段），其他语言合并片段后写回 copy/<语言>.json。
         文字按契约白名单清洗（b→strong、i→em、换行→<br>，其余标记去掉保留文字）。
  换图   有 data-edit-id 的图片：新图存为 assets/images/folio-<编辑 ID>-<哈希>.<扩展名>，改作者源 src 与 data-asset，
         并在 sources/assets.json 登记——授权留空，交付前必须确认（原文覆盖检查会拦下）。
  样式   Folio 的局部调整（data-folio-overrides）与批量规则（folio-shared-styles）→ edits.css，
         只针对有 data-edit-id / data-source-id 的元素或 .page；其他语言的调整限定在 html[lang] 下。
  冲突   作者源当前值与编辑包基准不同（导出编辑包之后源又被改过）→ 不覆盖，列为冲突。
  未写回 没有 ID 的改字、改图与样式，列出不处理。
用户改字记入 sources/user-edits.json（用户认可的改动），原文覆盖检查据此不报 MISSING / EXTRA。
报告写到 .qa/folio-sync/<时间>.json 与 .md；有冲突或未写回项时退出码 1（其余已写回）。
"""
import base64
import hashlib
import html as H
import json
import os
import re
import sys
import time
from html.parser import HTMLParser

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
INLINE = {"em", "strong", "a", "br", "sup", "sub", "span"}
EXT = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp", "image/gif": ".gif", "image/svg+xml": ".svg", "image/avif": ".avif"}


class Locator(HTMLParser):
    """记录每个元素的标签、属性与源文本偏移（开始标签起止、结束标签起止）。"""

    def __init__(self, text):
        super().__init__(convert_charrefs=False)
        self.text = text
        self.lines = [0]
        for m in re.finditer(r"\n", text):
            self.lines.append(m.end())
        self.stack, self.els = [], []
        self.feed(text)
        self.close()

    def off(self):
        line, col = self.getpos()
        return self.lines[line - 1] + col

    def handle_starttag(self, tag, attrs):
        start = self.off()
        end = start + len(self.get_starttag_text())
        el = {"tag": tag, "attrs": {k: (v or "") for k, v in attrs}, "s0": start, "s1": end, "e0": end, "e1": end, "parent": self.stack[-1] if self.stack else None}
        self.els.append(el)
        if tag not in VOID:
            self.stack.append(el)

    def handle_startendtag(self, tag, attrs):
        start = self.off()
        end = start + len(self.get_starttag_text())
        self.els.append({"tag": tag, "attrs": {k: (v or "") for k, v in attrs}, "s0": start, "s1": end, "e0": end, "e1": end,
                         "parent": self.stack[-1] if self.stack else None})

    def handle_endtag(self, tag):
        pos = self.off()
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i]["tag"] == tag:
                el = self.stack[i]
                el["e0"] = pos
                el["e1"] = self.text.index(">", pos) + 1
                del self.stack[i:]
                return

    def inner(self, el):
        return self.text[el["s1"]:el["e0"]]

    def ancestors(self, el):
        p = el["parent"]
        while p:
            yield p
            p = p["parent"]


class Clean(HTMLParser):
    """把编辑器里的富文本清洗成契约白名单的行内 HTML。"""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out, self.stack, self.dropped, self.blocks = [], [], set(), 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        tag = {"b": "strong", "i": "em"}.get(tag, tag)
        if tag in ("div", "p"):
            if self.blocks or self.out:
                self.out.append("<br>")
            self.blocks += 1
            self.stack.append(None)
            return
        if tag == "br":
            self.out.append("<br>")
            return
        if tag not in INLINE:
            self.dropped.add(tag)
            self.stack.append(None)
            return
        keep = []
        if tag == "a" and a.get("href") and not re.match(r"\s*(javascript|data|vbscript):", a["href"], re.I):
            keep.append(f' href="{H.escape(a["href"])}"')
        if tag == "span":
            for k in ("class", "lang"):
                if a.get(k) and not a[k].startswith("folio"):
                    keep.append(f' {k}="{H.escape(a[k])}"')
            if not keep:
                self.stack.append(None)
                return
        self.out.append(f"<{tag}{''.join(keep)}>")
        self.stack.append(tag)

    def handle_endtag(self, tag):
        tag = {"b": "strong", "i": "em"}.get(tag, tag)
        if tag == "br" or not self.stack:
            return
        t = self.stack.pop()
        if t:
            self.out.append(f"</{t}>")

    def handle_data(self, data):
        self.out.append(H.escape(data.replace(" ", " "), quote=False))


def clean(fragment):
    c = Clean()
    c.feed(fragment)
    c.close()
    s = "".join(c.out)
    for t in ("em", "strong", "sup", "sub"):
        s = s.replace(f"</{t}><{t}>", "")
    s = re.sub(r"\s+", " ", s).strip()
    s = re.sub(r"(<br>)+$", "", s)
    return s, c.dropped


def same(a, b):
    return clean(a)[0] == clean(b)[0]


def index(loc, attr):
    out = {}
    for el in loc.els:
        v = el["attrs"].get(attr)
        if v is not None:
            out.setdefault(v, []).append(el)
    return out


def frag_key(el):
    return (el["attrs"]["data-source-id"], el["attrs"].get("data-fragment") or "")


def text_of(fragment):
    return re.sub(r"\s+", " ", H.unescape(re.sub(r"<[^>]+>", "", fragment))).strip()


def target_selector(el, lang, default):
    a = el["attrs"]
    if "data-edit-id" in a:
        sel = f'[data-edit-id="{a["data-edit-id"]}"]'
    elif "data-source-id" in a:
        sel = f'[data-source-id="{a["data-source-id"]}"]' + (f'[data-fragment="{a["data-fragment"]}"]' if a.get("data-fragment") else "")
    elif "page" in a.get("class", "").split() and "data-page-id" in a:
        sel = f'.page[data-page-id="{a["data-page-id"]}"]'
    else:
        return None
    return (f'html[lang="{lang}"] ' if lang != default else "") + sel


def main(project, edited_path, dry=False):
    root = os.path.abspath(project)
    proj = json.load(open(os.path.join(root, "project.json"), encoding="utf-8"))
    default = proj["default_language"]
    edited = open(edited_path, encoding="utf-8").read()
    meta = lambda n: (re.search(rf'<meta name="{n}" content="([^"]*)"', edited) or [None, None])[1]
    build, lang = meta("hb-build"), meta("hb-lang")
    report = {"edited": os.path.abspath(edited_path), "build": build, "lang": lang, "applied": [], "conflicts": [], "unmapped": [], "notes": []}
    if not build or not lang:
        report["conflicts"].append({"kind": "package", "message": "这不是 handbook-designer 编辑包（缺少 hb-build / hb-lang 标记）"})
        return finish(root, report, dry)
    base_path = os.path.join(root, ".build", build, lang, "folio-base.html")
    snap_path = os.path.join(root, ".build", build, lang, "snapshot.html")
    if not os.path.exists(base_path) or not os.path.exists(snap_path):
        report["conflicts"].append({"kind": "package", "message": f"找不到编辑包基准（构建 {build}）：.build 被清理过，无法安全比对"})
        return finish(root, report, dry)
    B, E, S = Locator(open(base_path, encoding="utf-8").read()), Locator(edited), Locator(open(snap_path, encoding="utf-8").read())

    book_file = os.path.join(root, proj["entry"])
    book = open(book_file, encoding="utf-8").read()
    A = Locator(book)
    edits = []  # (start, end, replacement) on book.html
    copy_updates = {}

    # ---- 改字
    bsrc = {frag_key(el): el for el in B.els if "data-source-id" in el["attrs"] and "data-repeat" not in el["attrs"]}
    esrc = {frag_key(el): el for el in E.els if "data-source-id" in el["attrs"] and "data-repeat" not in el["attrs"]}
    changed = [k for k in bsrc if k in esrc and not same(B.inner(bsrc[k]), E.inner(esrc[k]))]
    for k in esrc:
        if k not in bsrc:
            report["unmapped"].append({"kind": "text", "target": k[0], "message": "编辑包基准里没有这个内容节点"})
    if lang == default:
        asrc = {frag_key(el): el for el in A.els if "data-source-id" in el["attrs"] and "data-repeat" not in el["attrs"]}
        for k in changed:
            new, dropped = clean(E.inner(esrc[k]))
            a = asrc.get(k)
            if a is None or not same(A.inner(a), B.inner(bsrc[k])):
                report["conflicts"].append({"kind": "text", "target": "#".join(x for x in k if x), "message": "作者源在导出编辑包之后被改过（或片段已重排），未覆盖",
                                            "folio": text_of(new)})
                continue
            edits.append((a["s1"], a["e0"], new))
            report["applied"].append({"kind": "text", "target": "#".join(x for x in k if x), "old": text_of(B.inner(bsrc[k])), "new": text_of(new)})
            if dropped:
                report["notes"].append(f"{k[0]}：去掉了不允许的标记 {sorted(dropped)}")
    else:
        cfile = os.path.join(root, "copy", f"{lang}.json")
        copy = json.load(open(cfile, encoding="utf-8"))
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        ids = sorted({k[0] for k in changed})
        for sid in ids:
            def merged(loc, table):
                parts = sorted((k for k in table if k[0] == sid), key=lambda k: int(k[1] or 0))
                return clean("".join(loc.inner(table[k]) for k in parts))[0]
            old, new = merged(B, bsrc), merged(E, esrc)
            cur = clean(inject_like(copy["strings"].get(sid, "")))[0]
            if cur != old:
                report["conflicts"].append({"kind": "text", "target": sid, "message": f"copy/{lang}.json 在导出编辑包之后被改过，未覆盖", "folio": text_of(new)})
                continue
            copy_updates[sid] = new
            report["applied"].append({"kind": "text", "target": sid, "lang": lang, "old": text_of(old), "new": text_of(new)})
        if copy_updates and not dry:
            copy["strings"].update(copy_updates)
            json.dump(copy, open(cfile, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    # 没有 ID 的改字：比较每页正文里不属于内容节点的文字
    for page in [el for el in B.els if "data-page-id" in el["attrs"]]:
        pid = page["attrs"]["data-page-id"]
        ep = next((el for el in E.els if el["attrs"].get("data-page-id") == pid), None)
        if ep and loose_text(B, page) != loose_text(E, ep):
            report["unmapped"].append({"kind": "text", "target": pid, "message": "页面上没有内容 ID 的文字被改过，未写回"})

    # ---- 换图
    bimg = index(B, "data-edit-id")
    asset_updates = {}
    for el in E.els:
        eid = el["attrs"].get("data-edit-id")
        if el["tag"] != "img":
            continue
        if not eid:
            continue
        b = (bimg.get(eid) or [None])[0]
        if b is None or b["attrs"].get("src") == el["attrs"].get("src"):
            continue
        m = re.match(r"data:([^;,]+);base64,(.*)", el["attrs"].get("src", ""), re.S)
        if not m:
            report["unmapped"].append({"kind": "image", "target": eid, "message": "新图片不是内嵌数据，无法写回"})
            continue
        data = base64.b64decode(m.group(2))
        digest = hashlib.sha256(data).hexdigest()[:10]
        rel = f"assets/images/folio-{eid}-{digest}{EXT.get(m.group(1), '.bin')}"
        snap_src = next((x["attrs"].get("src") for x in S.els if x["attrs"].get("data-edit-id") == eid), None)
        a = next((x for x in A.els if x["attrs"].get("data-edit-id") == eid), None)
        if a is None or a["attrs"].get("src") != snap_src:
            report["conflicts"].append({"kind": "image", "target": eid, "message": "作者源里这张图在导出编辑包之后被改过，未覆盖"})
            continue
        tag = book[a["s0"]:a["s1"]]
        new_tag = re.sub(r'(\ssrc=")[^"]*(")', lambda mm: mm.group(1) + rel + mm.group(2), tag)
        aid = f"folio-{eid}-{digest}"
        new_tag = re.sub(r'(\sdata-asset=")[^"]*(")', lambda mm: mm.group(1) + aid + mm.group(2), new_tag) if "data-asset=" in new_tag else new_tag.replace("<img", f'<img data-asset="{aid}"', 1)
        edits.append((a["s0"], a["s1"], new_tag))
        if not dry:
            os.makedirs(os.path.join(root, "assets", "images"), exist_ok=True)
            open(os.path.join(root, rel), "wb").write(data)
        asset_updates[aid] = {"file": rel, "source": f"Folio 中替换的图片（{time.strftime('%Y-%m-%d')}，替换 {eid}）", "license": "", "credit": ""}
        report["applied"].append({"kind": "image", "target": eid, "new": rel})
        report["notes"].append(f"新图片 {rel} 的来源与授权需要确认（sources/assets.json 中 {aid}）")
    for el in E.els:
        if el["tag"] == "img" and not el["attrs"].get("data-edit-id"):
            fid = el["attrs"].get("data-folio-id")
            b = next((x for x in B.els if x["tag"] == "img" and x["attrs"].get("data-folio-id") == fid), None) if fid else None
            if b is None and el["attrs"].get("src", "").startswith("data:") and el["attrs"]["src"] not in {x["attrs"].get("src") for x in B.els if x["tag"] == "img"}:
                report["unmapped"].append({"kind": "image", "target": fid or "img", "message": "没有编辑 ID 的图片被替换，未写回"})

    # ---- 样式与位置 → edits.css
    rules = []
    for el in E.els:
        raw = el["attrs"].get("data-folio-overrides")
        if not raw:
            continue
        try:
            d = json.loads(H.unescape(raw))
        except ValueError:
            continue
        decl = [f"{k}: {v} !important;" for k, v in (d.get("styles") or {}).items()]
        if d.get("dx") or d.get("dy"):
            decl.append(f"transform: translate({d.get('dx') or 0}px, {d.get('dy') or 0}px) {d.get('baseTransform') or ''} !important;".replace("  ", " "))
        if not decl:
            continue
        sel = target_selector(el, lang, default)
        if not sel:
            report["unmapped"].append({"kind": "style", "target": el["attrs"].get("data-folio-id", el["tag"]), "message": "没有 ID 的对象做了位置/样式调整，未写回"})
            continue
        rules.append(f"{sel} {{ {' '.join(decl)} }}")
        report["applied"].append({"kind": "style", "target": sel, "new": " ".join(decl)})
        if d.get("graphicStyles"):
            report["unmapped"].append({"kind": "style", "target": sel, "message": "品牌图形内部样式未写回"})
    shared = next((el for el in E.els if el["attrs"].get("id") == "folio-shared-styles"), None)
    if shared:
        try:
            srules = json.loads(H.unescape(shared["attrs"].get("data-rules", "[]")))
        except ValueError:
            srules = []
        for r in srules:
            m = re.fullmatch(r'(?::where\(\[data-folio-page-key="([^"]+)"\]\) )?\[data-folio-(style|groups)(=|~=)"([^"]+)"\]', r.get("selector", ""))
            if not m:
                report["unmapped"].append({"kind": "style", "target": r.get("selector"), "message": "无法解析的批量规则，未写回"})
                continue
            page_key, kind, _, val = m.groups()
            hits = []
            for el in E.els:
                a = el["attrs"]
                ok = a.get("data-folio-style") == val if kind == "style" else val in a.get("data-folio-groups", "").split()
                if ok and page_key:
                    ok = any(x["attrs"].get("data-folio-page-key") == page_key for x in E.ancestors(el))
                if ok:
                    hits.append(el)
            sels = [target_selector(el, lang, default) for el in hits]
            if any(s is None for s in sels):
                report["unmapped"].append({"kind": "style", "target": r["selector"], "message": f"批量规则命中 {sum(1 for s in sels if s is None)} 个没有 ID 的对象，这部分未写回"})
            sels = [s for s in sels if s]
            decl = " ".join(f"{k}: {v} !important;" for k, v in (r.get("styles") or {}).items())
            if sels and decl and not r.get("graphic"):
                rules.append(f"{', '.join(sels)} {{ {decl} }}")
                report["applied"].append({"kind": "style", "target": f"{len(sels)} 个对象（批量）", "new": decl})

    # ---- 写入
    if not dry:
        if edits:
            for s0, s1, rep in sorted(edits, key=lambda e: -e[0]):
                book = book[:s0] + rep + book[s1:]
            open(book_file, "w", encoding="utf-8").write(book)
        if rules:
            ef = os.path.join(root, "edits.css")
            head = f"\n/* Folio 修改 · 基于构建 {build} · {lang} · {time.strftime('%Y-%m-%d %H:%M')}（待审阅：保留、改写进 book.css 或删除） */\n"
            with open(ef, "a", encoding="utf-8") as f:
                f.write(head + "\n".join(rules) + "\n")
        user_edits = [x for x in report["applied"] if x["kind"] == "text"]
        if user_edits:
            uf = os.path.join(root, "sources", "user-edits.json")
            ue = json.load(open(uf, encoding="utf-8")) if os.path.exists(uf) else {"contract": 1, "edits": []}
            for x in user_edits:
                ue["edits"].append({"target": x["target"], "lang": x.get("lang", lang), "old": x["old"], "new": x["new"],
                                    "via": "folio", "build": build, "date": time.strftime("%Y-%m-%d %H:%M")})
            os.makedirs(os.path.dirname(uf), exist_ok=True)
            json.dump(ue, open(uf, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        if asset_updates:
            af = os.path.join(root, "sources", "assets.json")
            assets = json.load(open(af, encoding="utf-8")) if os.path.exists(af) else {"contract": 1, "assets": {}}
            assets["assets"].update(asset_updates)
            os.makedirs(os.path.dirname(af), exist_ok=True)
            json.dump(assets, open(af, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    return finish(root, report, dry)


def loose_text(loc, page):
    """页面里不属于任何内容节点、也不在样式/脚本里的文字。"""
    s = page["s1"]
    text = loc.text[s:page["e0"]]
    text = re.sub(r"<(style|script)\b.*?</\1>", "", text, flags=re.S)
    # 去掉内容节点整体
    for el in loc.els:
        if "data-source-id" in el["attrs"] and page["s0"] < el["s0"] < page["e0"]:
            text = text.replace(loc.text[el["s0"]:el["e1"]], "")
    return re.sub(r"\s+", "", H.unescape(re.sub(r"<[^>]+>", "", text)))


def inject_like(s):
    """与 inject.mjs 的 sanitizeInline 等价：白名单标记保留，其余转义。"""
    out, last = [], 0
    for m in re.finditer(r"<(/?)(em|strong|a|br|sup|sub|span)\b([^<>]*?)(/?)>", s, re.I):
        out.append(H.escape(s[last:m.start()], quote=False))
        out.append(m.group(0))
        last = m.end()
    out.append(H.escape(s[last:], quote=False))
    return "".join(out)


def finish(root, report, dry):
    qa = os.path.join(root, ".qa", "folio-sync")
    os.makedirs(qa, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    report["dry_run"] = dry
    json.dump(report, open(os.path.join(qa, f"{stamp}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    lines = [f"# Folio 写回 · 构建 {report['build']} · {report['lang']}", "",
             f"写回 {len(report['applied'])} 处，冲突 {len(report['conflicts'])} 处，未写回 {len(report['unmapped'])} 处。", ""]
    for k, title in (("applied", "已写回"), ("conflicts", "冲突（未覆盖）"), ("unmapped", "未写回")):
        if report[k]:
            lines.append(f"## {title}")
            lines += [f"- [{x['kind']}] {x.get('target', '')}：{x.get('message') or ''}{(' 「' + str(x.get('old', ''))[:30] + '」→「' + str(x.get('new', ''))[:30] + '」') if 'new' in x else ''}" for x in report[k]]
            lines.append("")
    if report["notes"]:
        lines += ["## 提示"] + [f"- {n}" for n in report["notes"]] + [""]
    lines.append("下一步：node hb/core/cli.mjs check <项目>（改动后旧验收已失效），审阅 edits.css，确认新图片授权。")
    open(os.path.join(qa, f"{stamp}.md"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 1 if report["conflicts"] or report["unmapped"] else 0


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) != 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(args[0], args[1], "--dry-run" in sys.argv))
