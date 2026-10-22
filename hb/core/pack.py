#!/usr/bin/env python3
"""源文件包（S8）：python3 hb/core/pack.py <项目> <构建 ID> <输出.zip>

打包能在另一台机器上重建同一本书的全部作者源：构建清单里的全部输入文件（project.json、作者 HTML/CSS、
lang/、copy/、edits.css、字体、图片）+ brief.md / page-plan.md / experience.md + sources/ 全部 + 字体与素材旁的授权文本，
再写入 REBUILD.md（重建命令、预期构建 ID、工具版本）。不含 .build/ .qa/ out/，不含符号链接与项目外文件。
"""
import json
import os
import sys
import zipfile


def main(project, build, out):
    root = os.path.abspath(project)
    proj = json.load(open(os.path.join(root, "project.json"), encoding="utf-8"))
    man = json.load(open(os.path.join(root, ".build", build, proj["default_language"], "manifest.json"), encoding="utf-8"))
    files = {i["path"] for i in man["inputs"]}
    for extra in ("brief.md", "page-plan.md", "experience.md"):
        if os.path.isfile(os.path.join(root, extra)):
            files.add(extra)
    for base in ("sources",):
        for dp, _, fs in os.walk(os.path.join(root, base)):
            for f in fs:
                files.add(os.path.relpath(os.path.join(dp, f), root).replace(os.sep, "/"))
    for rel in list(files):  # 授权文本：与字体、图片同目录的 .txt / .md
        d = os.path.dirname(os.path.join(root, rel))
        if rel.startswith("assets/") and os.path.isdir(d):
            for f in os.listdir(d):
                if f.lower().endswith((".txt", ".md")):
                    files.add(os.path.relpath(os.path.join(d, f), root).replace(os.sep, "/"))
    bad = [f for f in files if os.path.islink(os.path.join(root, f)) or f.startswith(("..", "/", ".build/", ".qa/", "out/"))]
    if bad:
        print(f"源文件包不能包含：{bad}", file=sys.stderr)
        return 1
    tools = man["tools"]
    rebuild = f"""# 重建说明

本包是《{proj['title']}》的完整作者源。在装有 handbook-designer Skill 的环境中：

```bash
bash <skill>/hb/core/setup_env.sh          # 首次：安装锁定版本的浏览器
node <skill>/hb/core/cli.mjs check .       # 渲染 + 全部检查
```

预期构建 ID：`{build}`（同一份源、同一版本的工具与浏览器得到同一 ID；工具或浏览器版本不同时 ID 会变化，需重新验收）。

工具版本：Playwright {tools['playwright']}，Chromium {tools['chromium']}，Node {tools['node']}，渲染工具哈希 `{tools['tool_hash'][:12]}`。
"""
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(files):
            z.write(os.path.join(root, f), f)
        z.writestr("REBUILD.md", rebuild)
    print(f"源文件包：{len(files)} 个文件，{os.path.getsize(out) // 1024} KB")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(*sys.argv[1:]))
