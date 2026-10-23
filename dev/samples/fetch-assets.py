#!/usr/bin/env python3
"""把样册照片按 sources/assets.json 的来源记录重新取回本地。

仓库只保留可读源码：book.html / book.css / project.json / sources/*.json 与
各册的 Markdown 说明。照片与静态字体不入库，克隆后要重建样册时用本脚本恢复。

用法（仓库根目录）：

    python3 dev/samples/fetch-assets.py --status          # 每册缺哪些文件
    python3 dev/samples/fetch-assets.py --all             # 恢复全部可恢复的照片
    python3 dev/samples/fetch-assets.py --project folio-swiss

只处理 sources/assets.json 里带 Wikimedia Commons 链接的条目；没有链接的
（例如 folio-business、product-brochure 的历史素材）只报告"需自备"，不猜。

字体不在这里处理，用 hb/core/fonts.py：

    python3 hb/core/fonts.py install
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
NATIVE = os.path.join(ROOT, "dev", "samples", "native")
UA = "handbook-designer-skill/2.2 (sample asset restore; contact: repo owner)"
COMMONS = re.compile(r"https?://commons\.wikimedia\.org/wiki/File:([^\s（）()]+(?:\([^\s（）]*\)[^\s（）]*)*)")


def projects():
    if not os.path.isdir(NATIVE):
        return []
    return sorted(d for d in os.listdir(NATIVE) if os.path.isdir(os.path.join(NATIVE, d)))


def inventory(project):
    """返回 [(相对路径, 绝对路径, 是否已有, 可下载的文件名 or None)]。"""
    base = os.path.join(NATIVE, project)
    manifest = os.path.join(base, "sources", "assets.json")
    if not os.path.isfile(manifest):
        return []
    with open(manifest, encoding="utf-8") as f:
        data = json.load(f)
    rows = []
    for key, entry in (data.get("assets") or {}).items():
        rel = entry.get("file") or ""
        if not rel:
            continue
        path = os.path.join(base, rel)
        title = commons_title(entry.get("source", ""))
        rows.append((key, rel, path, os.path.isfile(path), title))
    return rows


def commons_title(source):
    m = COMMONS.search(source or "")
    if not m:
        return None
    name = urllib.parse.unquote(m.group(1)).rstrip("。，,.")
    return name.strip()


def download(title, dest, retries=2):
    url = "https://commons.wikimedia.org/wiki/Special:FilePath/" + urllib.parse.quote(title)
    request = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                payload = response.read()
            break
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
            if attempt == retries:
                return False, str(exc)
            time.sleep(2 + attempt * 2)
    if len(payload) < 20_000:
        return False, f"返回内容只有 {len(payload)} 字节，可能不是图片"
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "wb") as f:
        f.write(payload)
    return True, f"{len(payload) / 1048576:.1f} MB"


def status(only=None):
    missing_total = 0
    for project in projects():
        rows = inventory(project)
        if not rows or (only and project != only):
            continue
        have = sum(1 for r in rows if r[3])
        restorable = sum(1 for r in rows if not r[3] and r[4])
        other = sum(1 for r in rows if not r[3] and not r[4])
        print(f"{project:18} {have}/{len(rows)} 已在本地", end="")
        if restorable:
            print(f"，可下载 {restorable}", end="")
        if other:
            print(f"，需自备 {other}", end="")
        print()
        missing_total += len(rows) - have
        for key, rel, path, exists, title in rows:
            if exists:
                continue
            hint = "可下载" if title else "需自备（来源未记录 URL）"
            print(f"    - {rel:38} {hint}")
    return missing_total


def fetch(only=None, force=False, dry=False):
    ready = skipped = failed = 0
    for project in projects():
        if only and project != only:
            continue
        rows = inventory(project)
        if not rows:
            continue
        pending = [r for r in rows if force or not r[3]]
        if not pending:
            continue
        print(f"[{project}] {len(pending)} 项待恢复")
        for key, rel, path, exists, title in pending:
            if not title:
                print(f"  跳过 {rel}：来源未记录 URL，需自备")
                skipped += 1
                continue
            if dry:
                print(f"  将下载 {rel} ← {title}")
                ready += 1
                continue
            ok, detail = download(title, path)
            if ok:
                print(f"  已取回 {rel}（{detail}）")
                ready += 1
            else:
                print(f"  失败 {rel}：{detail}")
                failed += 1
    print(f"\n完成：{ready} 取回 / {skipped} 需自备 / {failed} 失败")
    return 0 if failed == 0 else 1


def main(argv=None):
    parser = argparse.ArgumentParser(description="恢复样册照片（仓库不含二进制资产）")
    parser.add_argument("--project", help="只处理某一册，例如 folio-swiss")
    parser.add_argument("--all", action="store_true", help="恢复全部可恢复的照片")
    parser.add_argument("--status", action="store_true", help="只报告缺失情况")
    parser.add_argument("--force", action="store_true", help="已存在的也重新下载")
    parser.add_argument("--dry-run", action="store_true", help="只列出将要下载什么")
    args = parser.parse_args(argv)

    if not args.all and not args.status and not args.project:
        parser.print_help()
        return 2
    if args.status:
        missing = status(args.project)
        print(f"\n共缺 {missing} 个文件" if missing else "\n全部就位")
        return 0
    return fetch(args.project, args.force, args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
