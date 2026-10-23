#!/usr/bin/env python3
"""把「用户要用的 skill」单独打成一个 zip（与 hb/core/pack.py 的源文件包不同）。

仓库里同时住着两样东西：运行时（SKILL.md、hb、families、references、workflows、
templates、purposes、brands）和开发资产（dev 里的样册、测试、审计，docs）。用户不该
为了用一个 skill 去下整个仓库，也不该在 GitHub 上翻到一堆审计记录。

    python3 hb/core/pack_skill.py                 # 生成 dist/handbook-designer-skill-vX.zip
    python3 hb/core/pack_skill.py --list          # 只列出会打进包的文件
    python3 hb/core/pack_skill.py --with-samples  # 额外带上样册源码（不含照片与字体）

包含项由下面 RUNTIME / SHOWCASE / SAMPLES 三个清单决定，新增顶层目录时要同步。
文件清单优先取 `git ls-files`，所以不会有缓存、构建产物、照片混进来。
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 运行时：缺一个就跑不起来
RUNTIME = ("SKILL.md", "README.md", "LICENSE", "hb", "families", "references",
           "workflows", "templates", "purposes", "brands")
# 展示页：SKILL.md 让作者「先看原子、布局与组件展示」，属于使用路径的一部分
SHOWCASE = ("dev/folio-css",)
# 样册源码：可选的阅读材料，只有文本，没有照片与字体
SAMPLES = ("dev/samples/native/folio-swiss", "dev/samples/native/nature-camp")

ROOT_NAME = "handbook-designer-skill"


def family_version():
    path = os.path.join(ROOT, "families", "folio", "family.json")
    try:
        with open(path, encoding="utf-8") as f:
            return str(json.load(f).get("version") or "0")
    except (OSError, ValueError):
        return "0"


def tracked_files():
    try:
        out = subprocess.run(["git", "-C", ROOT, "ls-files", "-z"],
                             capture_output=True, check=True).stdout
        return [p.decode("utf-8") for p in out.split(b"\0") if p]
    except (OSError, subprocess.CalledProcessError):
        skip_dirs = {"__pycache__", "node_modules", ".git", ".build", ".qa", "out", "assets"}
        found = []
        for base, dirs, files in os.walk(ROOT):
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            for name in files:
                if name.endswith((".pyc", ".ttf", ".otf", ".jpg", ".png", ".pdf")):
                    continue
                found.append(os.path.relpath(os.path.join(base, name), ROOT).replace(os.sep, "/"))
        return found


def selected(with_samples=False):
    prefixes = list(RUNTIME) + list(SHOWCASE) + (list(SAMPLES) if with_samples else [])
    chosen = []
    for path in tracked_files():
        for prefix in prefixes:
            if path == prefix or path.startswith(prefix + "/"):
                chosen.append(path)
                break
    return sorted(chosen)


def build(destination, with_samples=False, quiet=False):
    files = selected(with_samples)
    if not files:
        raise SystemExit("没有可打包的文件：清单里的路径是否还存在？")

    os.makedirs(os.path.dirname(destination), exist_ok=True)
    total = 0
    stamp = (1980, 1, 1, 0, 0, 0)          # 固定时间戳，便于对比两次打包是否一致
    with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for rel in files:
            source = os.path.join(ROOT, rel)
            if not os.path.isfile(source):
                continue
            info = zipfile.ZipInfo(f"{ROOT_NAME}/{rel}", date_time=stamp)
            info.external_attr = 0o644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            with open(source, "rb") as f:
                payload = f.read()
            zf.writestr(info, payload)
            total += len(payload)

    with zipfile.ZipFile(destination) as zf:
        names = set(zf.namelist())
    must = {f"{ROOT_NAME}/SKILL.md", f"{ROOT_NAME}/hb/core/cli.mjs",
            f"{ROOT_NAME}/families/folio/design.css"}
    missing = sorted(must - names)
    if missing:
        raise SystemExit("打包缺少必需文件：" + "、".join(missing))

    if not quiet:
        print(f"已生成 {os.path.relpath(destination, ROOT)}")
        print(f"  {len(names)} 个文件，解压后 {total / 1048576:.1f} MB，"
              f"zip {os.path.getsize(destination) / 1048576:.1f} MB")
    return destination


def main(argv=None):
    parser = argparse.ArgumentParser(description="打包用户可直接使用的 skill")
    parser.add_argument("--out", default=os.path.join(ROOT, "dist"), help="输出目录")
    parser.add_argument("--with-samples", action="store_true", help="附带样册源码（无照片字体）")
    parser.add_argument("--list", action="store_true", help="只列出会打包的文件")
    args = parser.parse_args(argv)

    if args.list:
        files = selected(args.with_samples)
        for rel in files:
            print(rel)
        print(f"\n{len(files)} 个文件")
        return 0

    build(os.path.join(args.out, f"handbook-designer-skill-v{family_version()}.zip"),
          args.with_samples)
    return 0


if __name__ == "__main__":
    sys.exit(main())
