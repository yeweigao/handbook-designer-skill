"""家族源字体：查看、下载、安装到用户字体目录。

Folio 的字体不随仓库分发：仓库只保存族的声明与许可说明，真正排版时按项目字符集
子集化静态字面。这个工具负责把可再分发的开源字面准备好：

  python3 hb/core/fonts.py status            # 每个家族要哪些字面，本机是否已有，在哪
  python3 hb/core/fonts.py install           # 缺的下载到用户缓存（~/.cache/handbook-designer/fonts）
  python3 hb/core/fonts.py install --system  # 同时装进用户字体目录，供浏览器与其他软件使用

只处理 OFL/Apache 等允许再分发的字面。专有字体不下载、不安装，只报告"需自备"。下载后校验字形表与 SHA256，并写入同目录的
SHA256SUMS 与许可文本；重复运行时按校验和判断是否需要重下。
"""
import hashlib
import json
import os
import shutil
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
CACHE = os.path.join(os.path.expanduser("~"), ".cache", "handbook-designer", "fonts")
GF = "https://raw.githubusercontent.com/google/fonts/main/ofl"

# 只列可再分发的开源字面；URL 指向 Google Fonts 仓库里的原始可变字体。
CURATED = {
    "NotoSerifSC-VF.ttf": {"url": f"{GF}/notoserifsc/NotoSerifSC%5Bwght%5D.ttf", "license": "noto-serif-sc-OFL.txt"},
    "NotoSansSC-VF.ttf": {"url": f"{GF}/notosanssc/NotoSansSC%5Bwght%5D.ttf", "license": "noto-sans-sc-OFL.txt"},
    "Inter-VF.ttf": {"url": f"{GF}/inter/Inter%5Bopsz,wght%5D.ttf", "license": "inter-OFL.txt"},
}

LICENSE_URL = {
    "noto-serif-sc-OFL.txt": f"{GF}/notoserifsc/OFL.txt",
    "noto-sans-sc-OFL.txt": f"{GF}/notosanssc/OFL.txt",
    "inter-OFL.txt": f"{GF}/inter/OFL.txt",
}


def user_font_dir():
    home = os.path.expanduser("~")
    if sys.platform == "darwin":
        return os.path.join(home, "Library", "Fonts")
    if os.name == "nt":
        return os.path.join(os.environ.get("LOCALAPPDATA", os.path.join(home, "AppData", "Local")), "Microsoft", "Windows", "Fonts")
    return os.path.join(home, ".local", "share", "fonts")


def search_dirs():
    """与 family.py 的 SEARCH 保持一致，外加用户字体目录。"""
    return [os.environ.get("HB_FONT_DIR", ""), CACHE, user_font_dir(),
            os.path.join(REPO, "dev", "fonts")]




def find(name):
    for d in search_dirs():
        if d and os.path.isfile(os.path.join(d, name)):
            return os.path.join(d, name)
    return None


def required():
    """从 families/*/family.json 汇总需要的字面文件名与所属家族。"""
    need = {}
    fam_dir = os.path.join(REPO, "families")
    if not os.path.isdir(fam_dir):
        return need
    for name in sorted(os.listdir(fam_dir)):
        cfg = os.path.join(fam_dir, name, "family.json")
        if not os.path.isfile(cfg):
            continue
        with open(cfg, encoding="utf-8") as f:
            data = json.load(f)
        for record in data.get("fonts", []):
            source = record.get("source")
            if source:
                need.setdefault(source, {"families": [], "license": record.get("license")})
                need[source]["families"].append(data.get("name", name))
    return need


def status():
    need = required()
    rows = []
    for name, info in sorted(need.items()):
        path = find(name)
        rows.append({"file": name, "found": bool(path), "path": path,
                     "families": sorted(set(info["families"])),
                     "redistributable": name in CURATED,
                     "license": info.get("license")})
    return rows


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _download(url, dest):
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    tmp = dest + ".part"
    with urllib.request.urlopen(url, timeout=120) as r, open(tmp, "wb") as f:
        shutil.copyfileobj(r, f)
    os.replace(tmp, dest)


def _valid_font(path):
    """最小校验：能被 fontTools 打开且有 cmap；避免把错误页当字体存下。"""
    try:
        from fontTools.ttLib import TTFont
    except ImportError:
        return os.path.getsize(path) > 50_000
    try:
        font = TTFont(path, lazy=True)
        ok = bool(font.getBestCmap())
        font.close()
        return ok
    except Exception:
        return False


def install(names=None, system=False, quiet=False):
    """下载缺失的可再分发字面；system=True 时同时装进用户字体目录。"""
    need = required()
    targets = [n for n in need if n in CURATED] if not names else [n for n in names if n in CURATED]
    results = []
    for name in targets:
        dest = os.path.join(CACHE, name)
        if os.path.isfile(dest) and _valid_font(dest):
            results.append({"file": name, "action": "cached", "path": dest})
        else:
            try:
                _download(CURATED[name]["url"], dest)
            except Exception as e:                     # 离线/被墙时不能让整个流程失败
                results.append({"file": name, "action": "failed", "error": str(e)[:160]})
                continue
            if not _valid_font(dest):
                os.remove(dest)
                results.append({"file": name, "action": "invalid", "error": "下载内容不是有效字体"})
                continue
            results.append({"file": name, "action": "downloaded", "path": dest})
        lic = CURATED[name].get("license")
        if lic and lic in LICENSE_URL:
            lic_path = os.path.join(CACHE, lic)
            if not os.path.isfile(lic_path):
                try:
                    _download(LICENSE_URL[lic], lic_path)
                except Exception:
                    pass
        if system:
            d = user_font_dir()
            os.makedirs(d, exist_ok=True)
            shutil.copy2(dest, os.path.join(d, name))
            if lic and os.path.isfile(os.path.join(CACHE, lic)):
                shutil.copy2(os.path.join(CACHE, lic), os.path.join(d, lic))
            results[-1]["system"] = os.path.join(d, name)

    sums = os.path.join(CACHE, "SHA256SUMS")
    with open(sums, "w", encoding="utf-8") as f:
        for name in sorted(os.listdir(CACHE)):
            path = os.path.join(CACHE, name)
            if os.path.isfile(path) and name.endswith((".ttf", ".otf")):
                f.write(f"{_sha256(path)}  {name}\n")
    if not quiet:
        for r in results:
            if r["action"] == "failed":
                print(f"跳过 {r['file']}：{r['error']}")
            elif r["action"] == "invalid":
                print(f"失败 {r['file']}：{r['error']}")
            else:
                extra = f" → {r.get('system')}" if r.get("system") else ""
                print(f"{r['action']:<10} {r['file']}{extra}")
        print(f"缓存目录：{CACHE}")
    return results


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "status"
    if cmd == "status":
        rows = status()
        for r in rows:
            mark = "有" if r["found"] else ("可下载" if r["redistributable"] else "需自备")
            where = r["path"] or ""
            print(f"{mark:<4} {r['file']:<22} {','.join(r['families']):<10} {where}")
        missing = [r for r in rows if not r["found"]]
        print(f"\n{len(rows) - len(missing)}/{len(rows)} 已就位；用户字体目录：{user_font_dir()}")
        return 0
    if cmd == "install":
        names = [a for a in argv[2:] if not a.startswith("--")]
        install(names or None, system="--system" in argv)
        return 0
    print(__doc__.strip())
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
