#!/usr/bin/env python3
"""项目契约校验：python3 hb/core/validate.py <项目目录> [--json]

按 references/contract.md（contract 1）检查 project.json、作者源 HTML、作者 CSS、多语言文案。
只读，不修改任何文件。存在错误时退出码为 1；只有警告时为 0。
仅用 Python 标准库，兼容 Python 3.10。
"""
import json
import os
import re
import struct
import sys
from html.parser import HTMLParser

CONTRACT = 1
DEFAULT_FLOORS = {
    "body_px": 14, "key_px": 12, "aux_px": 10,
    "body_contrast": 4.5, "key_contrast": 4.5, "aux_contrast": 3.0, "display_contrast": 3.0,
}
ROLES = {"display", "body", "key", "aux", "deco"}
BINDINGS = {"digital", "loose", "saddle", "perfect"}
MODES = {"carry", "polish", "translate", "frozen"}
INLINE_OK = {"em", "strong", "a", "br", "sup", "sub", "span"}
FORBIDDEN_TAGS = {"script", "iframe", "object", "embed", "base", "style"}
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
FONT_EXT = {".ttf", ".otf", ".woff", ".woff2"}
PROJECT_KEYS = {"contract", "title", "entry", "styles", "languages", "default_language", "canvas",
                "binding", "first_page", "content_mode", "fonts", "readability", "readability_waiver", "family"}
LAYOUT_WORDS = {"layout", "layouts", "pages", "cells", "span", "blocks", "grid"}
PAGE_ID = re.compile(r"^[a-z0-9][a-z0-9-]*$")
SOURCE_ID = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
LANG_TAG = re.compile(r"^[A-Za-z]{2,3}(-[A-Za-z0-9]{2,8})*$")
NET = re.compile(r"^\s*(https?:|//|ftp:)", re.I)
URL_IN_CSS = re.compile(r"url\(\s*(['\"]?)(.*?)\1\s*\)", re.I)
IMPORT_IN_CSS = re.compile(r"@import\s+(?:url\(\s*)?(['\"])(.*?)\1", re.I)


class Report:
    def __init__(self):
        self.items = []

    def error(self, code, where, msg):
        self.items.append({"level": "error", "code": code, "where": where, "message": msg})

    def warn(self, code, where, msg):
        self.items.append({"level": "warning", "code": code, "where": where, "message": msg})

    @property
    def errors(self):
        return [i for i in self.items if i["level"] == "error"]


def inside(root, path):
    """path 解析后（含符号链接）是否仍在 root 内。"""
    real_root = os.path.realpath(root)
    real = os.path.realpath(path)
    return real == real_root or real.startswith(real_root + os.sep)


def check_ref(rep, root, base_dir, ref, where, must_exist=True, allow_link=False):
    """检查 HTML/CSS 中引用的本地文件。返回解析后的绝对路径或 None。"""
    ref = (ref or "").strip()
    if not ref or ref.startswith("#") or ref.startswith("data:"):
        return None
    if NET.match(ref):
        if allow_link:
            return None
        rep.error("ref.network", where, f"引用了网络地址：{ref}")
        return None
    if ref.startswith(("mailto:", "tel:")):
        if allow_link:
            return None
        rep.error("ref.scheme", where, f"不支持的引用：{ref}")
        return None
    if re.match(r"^[a-z][a-z0-9+.-]*:", ref, re.I):
        rep.error("ref.scheme", where, f"不支持的引用：{ref}")
        return None
    path_part = ref.split("#", 1)[0].split("?", 1)[0]
    if not path_part:
        return None
    if path_part.startswith("/") or re.match(r"^[A-Za-z]:\\", path_part):
        rep.error("ref.absolute", where, f"不允许绝对路径：{ref}")
        return None
    full = os.path.normpath(os.path.join(base_dir, path_part))
    if not inside(root, full):
        rep.error("ref.outside", where, f"引用了项目目录以外的文件：{ref}")
        return None
    if must_exist and not os.path.isfile(full):
        rep.error("ref.missing", where, f"文件不存在：{ref}")
        return None
    return full


def font_tables(path):
    """读取字体文件的表名集合；无法判断时返回 None。"""
    try:
        with open(path, "rb") as f:
            head = f.read(12)
            sig = head[:4]
            if sig in (b"\x00\x01\x00\x00", b"OTTO", b"true"):
                n = struct.unpack(">H", head[4:6])[0]
                data = f.read(16 * n)
                return {data[i * 16:i * 16 + 4].decode("latin-1") for i in range(n)}
            if sig == b"wOFF":
                f.seek(12)
                n = struct.unpack(">H", f.read(2))[0]
                f.seek(44)
                data = f.read(20 * n)
                return {data[i * 20:i * 20 + 4].decode("latin-1") for i in range(n)}
    except (OSError, struct.error):
        return None
    try:  # woff2 等：有 fontTools 时用它判断
        from fontTools.ttLib import TTFont
        return set(TTFont(path, lazy=True).keys())
    except Exception:
        return None


# ---------------------------------------------------------------- project.json

def check_project(rep, root):
    pj = os.path.join(root, "project.json")
    if not os.path.isfile(pj):
        rep.error("project.missing", "project.json", "找不到 project.json")
        return None
    try:
        with open(pj, encoding="utf-8") as f:
            p = json.load(f)
    except (OSError, ValueError) as e:
        rep.error("project.json", "project.json", f"无法解析：{e}")
        return None
    if not isinstance(p, dict):
        rep.error("project.type", "project.json", "顶层必须是对象")
        return None
    W = "project.json"
    for k in p:
        if k in LAYOUT_WORDS:
            rep.error("project.layout", W, f"不允许版面描述字段 `{k}`：版面写在 HTML/CSS 里")
        elif k not in PROJECT_KEYS:
            rep.error("project.unknown", W, f"未知字段 `{k}`")
    for k in ("contract", "title", "entry", "styles", "languages", "default_language", "canvas",
              "binding", "first_page", "content_mode", "fonts"):
        if k not in p:
            rep.error("project.required", W, f"缺少必填字段 `{k}`")
    if p.get("contract", CONTRACT) != CONTRACT:
        rep.error("project.contract", W, f"contract 必须为 {CONTRACT}")
    if "title" in p and (not isinstance(p["title"], str) or not p["title"].strip()):
        rep.error("project.title", W, "title 必须是非空字符串")

    entry = p.get("entry")
    if entry is not None:
        if not isinstance(entry, str) or not entry.lower().endswith((".html", ".htm")):
            rep.error("project.entry", W, "entry 必须是 .html 文件路径")
        else:
            check_ref(rep, root, root, entry, W + " entry")

    styles = p.get("styles")
    if styles is not None:
        if not isinstance(styles, list) or not styles or not all(isinstance(s, str) for s in styles):
            rep.error("project.styles", W, "styles 必须是非空的 CSS 路径列表")
        else:
            if len(set(styles)) != len(styles):
                rep.error("project.styles", W, "styles 有重复项")
            for s in styles:
                if not s.lower().endswith(".css"):
                    rep.error("project.styles", W, f"styles 只能是 .css：{s}")
                elif s.replace("\\", "/") == "edits.css" or s.replace("\\", "/").startswith("lang/"):
                    rep.error("project.styles", W, f"{s} 由渲染器自动追加，不要写进 styles")
                else:
                    check_ref(rep, root, root, s, W + " styles")

    langs = p.get("languages")
    if langs is not None:
        if not isinstance(langs, list) or not langs or not all(isinstance(x, str) for x in langs):
            rep.error("project.languages", W, "languages 必须是非空的语言标签列表")
            langs = None
        else:
            if len(set(langs)) != len(langs):
                rep.error("project.languages", W, "languages 有重复项")
            for x in langs:
                if not LANG_TAG.match(x):
                    rep.error("project.languages", W, f"不是有效的语言标签：{x}")
    dl = p.get("default_language")
    if dl is not None and langs and dl not in langs:
        rep.error("project.default_language", W, "default_language 必须在 languages 中")

    canvas = p.get("canvas")
    if canvas is not None:
        if not isinstance(canvas, dict):
            rep.error("project.canvas", W, "canvas 必须是对象")
        else:
            for k in canvas:
                if k not in ("trim_mm", "bleed_mm", "safe_mm"):
                    rep.error("project.canvas", W, f"canvas 未知字段 `{k}`")
            t = canvas.get("trim_mm")
            if not (isinstance(t, list) and len(t) == 2 and all(isinstance(v, (int, float)) and v > 0 for v in t)):
                rep.error("project.canvas", W, "canvas.trim_mm 必须是 [宽, 高]，正数")
            b = canvas.get("bleed_mm")
            if not (isinstance(b, (int, float)) and not isinstance(b, bool) and b >= 0):
                rep.error("project.canvas", W, "canvas.bleed_mm 必须是 ≥ 0 的数")
            s = canvas.get("safe_mm")
            ok = (isinstance(s, (int, float)) and not isinstance(s, bool) and s >= 0) or (
                isinstance(s, list) and len(s) == 4 and all(isinstance(v, (int, float)) and v >= 0 for v in s))
            if not ok:
                rep.error("project.canvas", W, "canvas.safe_mm 必须是 ≥ 0 的数或 [上, 右, 下, 左]")
            elif isinstance(t, list) and len(t) == 2 and all(isinstance(v, (int, float)) for v in t):
                sv = [s] * 4 if not isinstance(s, list) else s
                if sv[1] + sv[3] >= t[0] or sv[0] + sv[2] >= t[1]:
                    rep.error("project.canvas", W, "安全边距大于成品尺寸")

    if "binding" in p and p["binding"] not in BINDINGS:
        rep.error("project.binding", W, f"binding 必须是 {sorted(BINDINGS)} 之一")
    if "first_page" in p and p["first_page"] not in ("left", "right"):
        rep.error("project.first_page", W, "first_page 必须是 left 或 right")
    if "content_mode" in p and p["content_mode"] not in MODES:
        rep.error("project.content_mode", W, f"content_mode 必须是 {sorted(MODES)} 之一")

    fonts = p.get("fonts")
    if fonts is not None:
        if not isinstance(fonts, list) or not fonts:
            rep.error("project.fonts", W, "fonts 必须是非空列表")
        else:
            seen = set()
            for i, f in enumerate(fonts):
                w = f"{W} fonts[{i}]"
                if not isinstance(f, dict):
                    rep.error("project.fonts", w, "每项必须是对象")
                    continue
                for k in f:
                    if k not in ("family", "file", "weight", "style"):
                        rep.error("project.fonts", w, f"未知字段 `{k}`")
                fam, fil = f.get("family"), f.get("file")
                if not isinstance(fam, str) or not fam.strip():
                    rep.error("project.fonts", w, "family 必须是非空字符串")
                if not isinstance(fil, str) or os.path.splitext(fil)[1].lower() not in FONT_EXT:
                    rep.error("project.fonts", w, f"file 必须是 {sorted(FONT_EXT)} 字体文件")
                else:
                    full = check_ref(rep, root, root, fil, w)
                    if full:
                        tables = font_tables(full)
                        if tables is None:
                            rep.warn("font.unchecked", w, f"无法判断 {fil} 是否为可变字体")
                        elif "fvar" in tables:
                            rep.error("font.variable", w, f"{fil} 是可变字体：Chrome 导出 PDF 时会变成 Type 3。"
                                      f"先用 python3 hb/core/font_static.py 实例化为固定字重")
                wt = f.get("weight", "400")
                if not (isinstance(wt, (str, int)) and re.match(r"^\d{3}$", str(wt))):
                    rep.error("project.fonts", w, "weight 写成单个字重，如 \"400\"（字体必须是静态字体）")
                st = f.get("style", "normal")
                if st not in ("normal", "italic", "oblique"):
                    rep.error("project.fonts", w, "style 必须是 normal / italic / oblique")
                key = (fam, str(wt), st)
                if key in seen:
                    rep.error("project.fonts", w, f"重复声明字体 {fam} {wt} {st}")
                seen.add(key)

    floors = dict(DEFAULT_FLOORS)
    waiver = p.get("readability_waiver")
    if waiver is not None:
        if not isinstance(waiver, dict) or not all(isinstance(waiver.get(k), str) and waiver.get(k).strip()
                                                    for k in ("reason", "approved_by", "date")):
            rep.error("project.waiver", W, "readability_waiver 需要 reason、approved_by、date 与 values")
        vals = waiver.get("values") if isinstance(waiver, dict) else None
        if not isinstance(vals, dict) or not vals:
            rep.error("project.waiver", W, "readability_waiver.values 必须列出放宽后的值")
        else:
            for k, v in vals.items():
                if k not in DEFAULT_FLOORS or not isinstance(v, (int, float)) or v <= 0:
                    rep.error("project.waiver", W, f"readability_waiver.values 无效项 `{k}`")
                else:
                    floors[k] = v
            rep.warn("readability.waiver", W, f"已授权放宽可读性下限：{vals}（{waiver.get('reason', '')}）")
    r = p.get("readability")
    if r is not None:
        if not isinstance(r, dict):
            rep.error("project.readability", W, "readability 必须是对象")
        else:
            for k, v in r.items():
                if k not in DEFAULT_FLOORS:
                    rep.error("project.readability", W, f"readability 未知字段 `{k}`")
                elif not isinstance(v, (int, float)) or isinstance(v, bool):
                    rep.error("project.readability", W, f"readability.{k} 必须是数字")
                elif v < DEFAULT_FLOORS[k]:
                    rep.error("project.readability", W,
                              f"readability.{k}={v} 低于默认下限 {DEFAULT_FLOORS[k]}；只能提高。确需降低请用 readability_waiver")

    fam = p.get("family")
    if fam is not None and not (isinstance(fam, dict) and isinstance(fam.get("name"), str)):
        rep.error("project.family", W, "family 需要 name（以及 version、sha256）")
    return p


# ---------------------------------------------------------------- HTML

class AuthorParser(HTMLParser):
    def __init__(self, rep, root, where):
        super().__init__(convert_charrefs=True)
        self.rep, self.root, self.where = rep, root, where
        self.base = root
        self.stack = []          # [(tag, attrs, flags)]
        self.pages = []          # [{id, spread, line}]
        self.sources = {}        # id -> [ {fragment, repeat, line} ]
        self.edit_ids = {}
        self.texts = {}          # source id -> 是否有文字
        self.saw_body = False

    def w(self):
        return f"{self.where}:{self.getpos()[0]}"

    def in_content(self):
        for tag, attrs, flags in reversed(self.stack):
            if "data-source-id" in attrs:
                return attrs["data-source-id"]
        return None

    def role(self):
        for tag, attrs, flags in reversed(self.stack):
            if "data-role" in attrs:
                return attrs["data-role"]
        return "body"

    def in_page(self):
        return any("page" in flags for _, _, flags in self.stack)

    def handle_starttag(self, tag, attrs_list):
        self._start(tag, attrs_list, selfclosing=tag in VOID)

    def handle_startendtag(self, tag, attrs_list):
        self._start(tag, attrs_list, selfclosing=True)

    def _start(self, tag, attrs_list, selfclosing):
        rep, w = self.rep, self.w()
        attrs = {k.lower(): (v if v is not None else "") for k, v in attrs_list}
        flags = set()
        if tag == "body":
            self.saw_body = True
        if tag in FORBIDDEN_TAGS:
            rep.error("html.forbidden", w, f"作者源不得包含 <{tag}>（样式写进 project.json 的 styles；页面保持静态）")
        if tag == "link" and "stylesheet" in attrs.get("rel", "").lower():
            rep.error("html.forbidden", w, "作者源不得用 <link rel=stylesheet>；样式写进 project.json 的 styles")
        for k in attrs:
            if k.startswith("on"):
                rep.error("html.handler", w, f"作者源不得有事件属性 {k}")

        # 资源引用
        allow_link = tag == "a" and "href" in attrs
        for k in ("src", "href", "poster", "xlink:href", "data"):
            if k in attrs:
                must = not (tag == "a" and k == "href")
                check_ref(self.rep, self.root, self.base, attrs[k], w, must_exist=must, allow_link=allow_link)
        if "srcset" in attrs:
            for part in attrs["srcset"].split(","):
                url = part.strip().split(" ")[0]
                check_ref(self.rep, self.root, self.base, url, w)
        if "style" in attrs:
            for m in URL_IN_CSS.finditer(attrs["style"]):
                check_ref(self.rep, self.root, self.base, m.group(2), w)

        content = self.in_content()
        if content is not None and tag not in INLINE_OK:
            rep.error("html.content-tag", w, f"内容节点 {content} 里不允许 <{tag}>（白名单：{sorted(INLINE_OK)}）")

        classes = attrs.get("class", "").split()
        if "page" in classes:
            flags.add("page")
            parent = self.stack[-1][0] if self.stack else None
            if self.in_page():
                rep.error("html.page-nested", w, ".page 不能嵌套")
            elif parent != "body":
                rep.error("html.page-parent", w, ".page 必须是 <body> 的直接子元素")
            pid = attrs.get("data-page-id")
            if not pid:
                rep.error("html.page-id", w, ".page 缺少 data-page-id")
            elif not PAGE_ID.match(pid):
                rep.error("html.page-id", w, f"data-page-id 格式不对：{pid}")
            elif any(pg["id"] == pid for pg in self.pages):
                rep.error("html.page-id", w, f"data-page-id 重复：{pid}")
            self.pages.append({"id": pid, "spread": attrs.get("data-spread") or None, "line": self.getpos()[0]})
        elif "data-page-id" in attrs:
            rep.error("html.page-id", w, "data-page-id 只能写在 .page 上")
        elif "data-spread" in attrs:
            rep.error("html.spread", w, "data-spread 只能写在 .page 上")

        if "data-role" in attrs and attrs["data-role"] not in ROLES:
            rep.error("html.role", w, f"data-role 取值必须是 {sorted(ROLES)}：{attrs['data-role']}")

        sid = attrs.get("data-source-id")
        if sid is not None:
            if not self.in_page():
                rep.error("html.source-outside", w, f"内容节点 {sid} 不在任何 .page 内")
            if not SOURCE_ID.match(sid):
                rep.error("html.source-id", w, f"data-source-id 格式不对：{sid}")
            if content is not None:
                rep.error("html.source-nested", w, f"内容节点 {sid} 嵌套在内容节点 {content} 里")
            eff_role = attrs.get("data-role") or self.role()
            if eff_role == "deco":
                rep.error("html.source-deco", w, f"内容节点 {sid} 处在 deco 装饰里：内容不能藏进装饰")
            if selfclosing:
                rep.error("html.source-void", w, f"内容节点 {sid} 不能是空元素 <{tag}>")
            frag = attrs.get("data-fragment")
            if frag is not None and not re.match(r"^[1-9]\d*$", frag):
                rep.error("html.fragment", w, f"data-fragment 必须是从 1 开始的整数：{frag}")
            self.sources.setdefault(sid, []).append(
                {"fragment": frag, "repeat": "data-repeat" in attrs, "line": self.getpos()[0]})
            self.texts.setdefault(sid, False)
        else:
            for k in ("data-fragment", "data-repeat"):
                if k in attrs:
                    rep.error("html.fragment", w, f"{k} 只能和 data-source-id 一起使用")

        eid = attrs.get("data-edit-id")
        if eid is not None:
            if not SOURCE_ID.match(eid):
                rep.error("html.edit-id", w, f"data-edit-id 格式不对：{eid}")
            elif eid in self.edit_ids:
                rep.error("html.edit-id", w, f"data-edit-id 重复：{eid}")
            self.edit_ids[eid] = self.getpos()[0]

        if "data-bleed" in attrs:
            toks = attrs["data-bleed"].split()
            if not toks or any(t not in ("top", "right", "bottom", "left", "all") for t in toks):
                rep.error("html.bleed", w, "data-bleed 取值为 top / right / bottom / left 的组合或 all")
        if "data-overlap" in attrs and not attrs["data-overlap"].strip():
            rep.error("html.overlap", w, "data-overlap 需要写允许重叠的元素 ID 或 *")
        if "data-flow" in attrs and not SOURCE_ID.match(attrs["data-flow"]):
            rep.error("html.flow", w, f"data-flow 名称格式不对：{attrs['data-flow']}")

        if not selfclosing:
            self.stack.append((tag, attrs, flags))

    def handle_endtag(self, tag):
        # 容忍省略的结束标签：弹到匹配的那个
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                return

    def handle_data(self, data):
        if data.strip():
            sid = self.in_content()
            if sid is not None:
                self.texts[sid] = True


def check_html(rep, root, p):
    entry = p.get("entry")
    if not isinstance(entry, str):
        return None
    path = os.path.join(root, entry)
    if not os.path.isfile(path) or not inside(root, path):
        return None
    with open(path, encoding="utf-8") as f:
        html = f.read()
    ap = AuthorParser(rep, root, entry)
    ap.base = os.path.dirname(path)
    ap.feed(html)
    ap.close()
    if not ap.saw_body:
        rep.error("html.body", entry, "缺少 <body>")
    if not ap.pages:
        rep.error("html.pages", entry, "没有任何 .page")

    # 内容 ID：唯一 / 片段 / 有意重复
    for sid, occ in ap.sources.items():
        frags = [o for o in occ if o["fragment"] is not None]
        plain = [o for o in occ if o["fragment"] is None]
        if frags and plain and any(not o["repeat"] for o in plain):
            rep.error("html.fragment", f"{entry}:{occ[0]['line']}", f"{sid} 同时有片段和非片段写法")
        if frags:
            nums = sorted(int(o["fragment"]) for o in frags if re.match(r"^\d+$", o["fragment"] or ""))
            if nums != list(range(1, len(nums) + 1)):
                rep.error("html.fragment", f"{entry}:{frags[0]['line']}", f"{sid} 的片段编号必须从 1 连续：{nums}")
        firsts = [o for o in plain if not o["repeat"]]
        if not frags and len(firsts) != 1:
            if len(firsts) == 0:
                rep.error("html.repeat", f"{entry}:{occ[0]['line']}", f"{sid} 只有 data-repeat，没有首次出现")
            else:
                rep.error("html.source-dup", f"{entry}:{firsts[1]['line']}",
                          f"data-source-id 重复：{sid}（有意重复的请在后续出现处加 data-repeat）")
        if not ap.texts.get(sid):
            rep.warn("html.source-empty", f"{entry}:{occ[0]['line']}", f"内容节点 {sid} 没有文字")

    # 跨页
    first_right = p.get("first_page", "right") == "right"
    groups = {}
    for idx, pg in enumerate(ap.pages):
        if pg["spread"]:
            groups.setdefault(pg["spread"], []).append(idx)
    for sp, idxs in groups.items():
        if len(idxs) != 2 or idxs[1] != idxs[0] + 1:
            rep.error("html.spread", entry, f"跨页 {sp} 必须恰好是相邻的两页")
            continue
        n = idxs[0] + 1  # 1-based 页码
        left_first = (n % 2 == 0) if first_right else (n % 2 == 1)
        if not left_first:
            rep.error("html.spread", entry, f"跨页 {sp} 从第 {n} 页开始，但这一页在右侧；跨页须左页在前")

    count = len(ap.pages)
    b = p.get("binding")
    if b == "saddle" and count % 4:
        rep.warn("binding.count", entry, f"骑马钉需要 4 的倍数页，目前 {count} 页（最终以 PDF 检查为准）")
    if b == "perfect" and count % 2:
        rep.warn("binding.count", entry, f"胶装需要偶数页，目前 {count} 页（最终以 PDF 检查为准）")
    return ap


# ---------------------------------------------------------------- CSS

def strip_comments(css):
    return re.sub(r"/\*.*?\*/", "", css, flags=re.S)


def check_css(rep, root, rel, seen):
    path = os.path.normpath(os.path.join(root, rel))
    if path in seen or not os.path.isfile(path) or not inside(root, path):
        return
    seen.add(path)
    with open(path, encoding="utf-8") as f:
        css = strip_comments(f.read())
    where = os.path.relpath(path, root)
    if re.search(r"@page\b", css):
        rep.error("css.page", where, "作者 CSS 不得写 @page：纸张由 project.json 的 canvas 生成")
    if re.search(r"@font-face\b", css, re.I):
        rep.error("css.font-face", where, "作者 CSS 不得写 @font-face：字体在 project.json 的 fonts 声明")
    base = os.path.dirname(path)
    for m in IMPORT_IN_CSS.finditer(css):
        full = check_ref(rep, root, base, m.group(2), where)
        if full:
            check_css(rep, root, os.path.relpath(full, root), seen)
    for m in URL_IN_CSS.finditer(css):
        check_ref(rep, root, base, m.group(2), where)


# ---------------------------------------------------------------- 多语言

class InlineCheck(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.bad = set()

    def handle_starttag(self, tag, attrs):
        if tag not in INLINE_OK:
            self.bad.add(tag)


def check_copy(rep, root, p, ap):
    langs = p.get("languages") if isinstance(p.get("languages"), list) else []
    dl = p.get("default_language")
    ids = set(ap.sources) if ap else set()
    copy_dir = os.path.join(root, "copy")
    if os.path.isdir(copy_dir):
        for name in sorted(os.listdir(copy_dir)):
            if name.startswith("."):
                continue
            lang = name[:-5] if name.endswith(".json") else None
            if lang is None or lang not in langs:
                rep.error("copy.unknown", f"copy/{name}", "不属于 languages 中任何语言的文案文件")
            elif lang == dl:
                rep.error("copy.default", f"copy/{name}", "默认语言的文案写在 book.html，不要另建 copy 文件")
    lang_dir = os.path.join(root, "lang")
    if os.path.isdir(lang_dir):
        for name in sorted(os.listdir(lang_dir)):
            if name.startswith("."):
                continue
            lang = name[:-4] if name.endswith(".css") else None
            if lang is None or lang not in langs:
                rep.error("lang.unknown", f"lang/{name}", "不属于 languages 中任何语言的样式文件")
            else:
                check_css(rep, root, os.path.join("lang", name), set())
    for lang in langs:
        if lang == dl:
            continue
        rel = f"copy/{lang}.json"
        path = os.path.join(root, rel)
        if not os.path.isfile(path):
            rep.error("copy.missing", rel, f"缺少 {lang} 文案文件")
            continue
        try:
            with open(path, encoding="utf-8") as f:
                c = json.load(f)
        except (OSError, ValueError) as e:
            rep.error("copy.json", rel, f"无法解析：{e}")
            continue
        if not isinstance(c, dict) or c.get("contract") != CONTRACT or c.get("lang") != lang \
                or not isinstance(c.get("strings"), dict):
            rep.error("copy.shape", rel, f"格式应为 {{\"contract\": 1, \"lang\": \"{lang}\", \"strings\": {{…}}}}")
            continue
        strings = c["strings"]
        for k in sorted(ids - set(strings)):
            rep.error("copy.untranslated", rel, f"缺译：{k}")
        for k in sorted(set(strings) - ids):
            rep.error("copy.extra", rel, f"多余译文（book.html 中没有这个内容 ID）：{k}")
        for k, v in strings.items():
            if not isinstance(v, str):
                rep.error("copy.value", rel, f"{k} 的值必须是字符串")
                continue
            if not v.strip():
                rep.warn("copy.empty", rel, f"{k} 的译文为空")
            ic = InlineCheck()
            ic.feed(v)
            if ic.bad:
                rep.warn("copy.markup", rel, f"{k} 含白名单外的标记 {sorted(ic.bad)}，渲染时会按文本转义")


# ---------------------------------------------------------------- 入口

def validate(root):
    rep = Report()
    root = os.path.abspath(root)
    if not os.path.isdir(root):
        rep.error("project.dir", root, "不是目录")
        return rep
    p = check_project(rep, root)
    if p is None:
        return rep
    ap = check_html(rep, root, p)
    seen = set()
    for s in p.get("styles") or []:
        if isinstance(s, str):
            check_css(rep, root, s, seen)
    if os.path.isfile(os.path.join(root, "edits.css")):
        check_css(rep, root, "edits.css", seen)
    check_copy(rep, root, p, ap)
    return rep


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    if len(args) != 1:
        print(__doc__.strip().splitlines()[0])
        return 2
    rep = validate(args[0])
    if "--json" in argv:
        print(json.dumps({"contract": CONTRACT, "items": rep.items}, ensure_ascii=False, indent=2))
    else:
        for i in rep.items:
            tag = "ERROR" if i["level"] == "error" else "WARN "
            print(f"{tag} {i['code']:<22} {i['where']}: {i['message']}")
        n_e = len(rep.errors)
        n_w = len(rep.items) - n_e
        print(f"契约校验：{'不通过' if n_e else '通过'}（{n_e} 个错误，{n_w} 个警告）")
    return 1 if rep.errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
