#!/usr/bin/env python3
"""离线单文件 HTML（S8）：python3 hb/core/offline_html.py <项目> <快照 snapshot.html> <输出.html>

把渲染快照依赖的全部本地资源内嵌：<link rel=stylesheet>（递归 @import）、CSS url()（字体、背景图）、
img src / srcset、元素 style 中的 url()、SVG href。去掉指向项目根目录的 <base>。
遇到无法内嵌的引用（网络地址、项目外文件、不存在的文件）报错退出，不留下半离线的文件。
图片按原文件内嵌，不压缩（与 PDF 同源，可用于核对）。
"""
import base64
import mimetypes
import os
import re
import sys

MIME = {".ttf": "font/ttf", ".otf": "font/otf", ".woff": "font/woff", ".woff2": "font/woff2", ".svg": "image/svg+xml",
        ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".webp": "image/webp", ".gif": "image/gif", ".avif": "image/avif"}
URL = re.compile(r"url\(\s*(['\"]?)(.*?)\1\s*\)", re.I)
IMPORT = re.compile(r"@import\s+(?:url\(\s*)?(['\"])(.*?)\1\s*\)?\s*;", re.I)


class OfflineError(Exception):
    pass


def resolver(root):
    real_root = os.path.realpath(root)

    def resolve(base_dir, ref):
        ref = ref.strip()
        if not ref or ref.startswith(("data:", "#")):
            return None
        if re.match(r"^[a-z][a-z0-9+.-]*:|^//", ref, re.I):
            raise OfflineError(f"无法离线内嵌网络或其他协议的引用：{ref}")
        p = os.path.realpath(os.path.join(base_dir, ref.split("#")[0].split("?")[0]))
        if not (p == real_root or p.startswith(real_root + os.sep)):
            raise OfflineError(f"引用了项目目录以外的文件：{ref}")
        if not os.path.isfile(p):
            raise OfflineError(f"文件不存在：{ref}")
        return p
    return resolve


def data_uri(path):
    ext = os.path.splitext(path)[1].lower()
    mime = MIME.get(ext) or mimetypes.guess_type(path)[0] or "application/octet-stream"
    with open(path, "rb") as f:
        return f"data:{mime};base64," + base64.b64encode(f.read()).decode()


def inline_css(css, base_dir, resolve, seen):
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)

    def imp(m):
        p = resolve(base_dir, m.group(2))
        if p is None:
            return ""
        if p in seen:
            raise OfflineError(f"CSS @import 循环：{p}")
        with open(p, encoding="utf-8") as f:
            return inline_css(f.read(), os.path.dirname(p), resolve, seen | {p})
    css = IMPORT.sub(imp, css)

    def url(m):
        p = resolve(base_dir, m.group(2))
        if p is None:
            return m.group(0)
        if os.path.splitext(p)[1].lower() == ".svg" and "#" in m.group(2):
            raise OfflineError(f"不支持内嵌带片段的外部 SVG：{m.group(2)}")
        return f'url("{data_uri(p)}")'
    return URL.sub(url, css)


def main(project, snapshot, out):
    root = os.path.abspath(project)
    resolve = resolver(root)
    html = open(snapshot, encoding="utf-8").read()
    html = re.sub(r'<base\b[^>]*data-hb="base"[^>]*>', "", html)
    net = re.findall(r'\s(?:src|poster|xlink:href|srcset)=["\']\s*((?:https?:)?//[^"\']+)', html)
    net += re.findall(r'<(?:link|use|image)\b[^>]*\shref=["\']\s*((?:https?:)?//[^"\']+)', html)
    if net:
        raise OfflineError(f"无法离线内嵌网络资源：{net[:3]}")

    def link(m):
        href = re.search(r'href="([^"]*)"', m.group(0))
        p = resolve(root, href.group(1)) if href else None
        if p is None:
            raise OfflineError(f"无法解析样式表：{m.group(0)[:80]}")
        with open(p, encoding="utf-8") as f:
            return "<style>\n" + inline_css(f.read(), os.path.dirname(p), resolve, {p}) + "\n</style>"
    html = re.sub(r'<link\b[^>]*rel="stylesheet"[^>]*>', link, html)
    html = re.sub(r"(<style\b[^>]*>)(.*?)(</style>)", lambda m: m.group(1) + inline_css(m.group(2), root, resolve, set()) + m.group(3), html, flags=re.S)

    def attr(m):
        p = resolve(root, m.group(3))
        return m.group(0) if p is None else f'{m.group(1)}={m.group(2)}{data_uri(p)}{m.group(2)}'
    html = re.sub(r'(\s(?:src|poster|href|xlink:href))=(["\'])((?!data:|#|https?:|mailto:|tel:)[^"\']+)\2',
                  lambda m: m.group(0) if m.group(1).strip() == "href" and not re.search(r"<(?:image|use|link)\b[^>]*$", html[max(0, m.start() - 200):m.start()]) else attr(m), html)

    def srcset(m):
        parts = []
        for item in m.group(2).split(","):
            bits = item.strip().split()
            if not bits:
                continue
            p = resolve(root, bits[0])
            parts.append(" ".join([data_uri(p) if p else bits[0]] + bits[1:]))
        return f'{m.group(1)}="{", ".join(parts)}"'
    html = re.sub(r'(\ssrcset)="([^"]*)"', srcset, html)
    html = re.sub(r'(\sstyle)="([^"]*)"', lambda m: m.group(1) + '="' + URL.sub(
        lambda u: (f"url(&quot;{data_uri(resolve(root, u.group(2).replace('&quot;', '')))}&quot;)" if resolve(root, u.group(2).replace('&quot;', '')) else u.group(0)),
        m.group(2)) + '"', html)
    leftovers = re.findall(r'\s(?:src|href|poster)="(?!data:|#|https?:|mailto:|tel:)([^"]+)"', html)
    leftovers = [x for x in leftovers if not x.startswith("data:")]
    if leftovers:
        raise OfflineError(f"仍有未内嵌的本地引用：{leftovers[:5]}")
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"离线 HTML：{os.path.getsize(out) // 1024} KB")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(__doc__)
        sys.exit(2)
    try:
        sys.exit(main(*sys.argv[1:]))
    except OfflineError as e:
        print(f"离线 HTML 失败：{e}", file=sys.stderr)
        sys.exit(1)
