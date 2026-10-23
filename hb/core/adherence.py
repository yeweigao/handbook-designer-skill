"""样式一致性检查：本书 CSS 是否仍留在家族基因之内。

静态分析，不启动浏览器。判断的是"这一册有没有套掉 Folio"，不是好看不好看：

- 字号 / 间距 / 行距 / 基线 token 属于家族基因，本书 CSS 不得重定义（错误）。
- 颜色 token 可以按品牌覆写，但必须被看见（警告，并列出改了什么）。
- 字号只能取字阶值；裁字、填图字这类显式放大的装饰字允许取最大字阶的整数倍。
- 渐变、圆角、阴影、滤镜与大量自定义类不计错误，但会记下数量，供审稿判断"是不是换了一套视觉语言"。

需要保留旧行为时，在 project.json 写 `style_waiver`（附理由），本模块的硬项随之降为警告。
"""
import os
import re

SIZE_TOKEN = re.compile(r"--fl-size-([a-z0-9-]+)\s*:\s*([0-9.]+)px")
DECL = re.compile(r"(--fl-[a-z0-9-]+)\s*:\s*([^;}]+)")
FONT_SIZE = re.compile(r"font-size\s*:\s*([^;}]+)")
STYLE_ATTR = re.compile(r'style\s*=\s*"([^"]*)"')

RHYTHM_PREFIX = ("--fl-size-", "--fl-space-", "--fl-leading-", "--fl-tracking-",
                 "--fl-baseline", "--fl-gutter", "--fl-margin-", "--fl-measure")
COLOR_NAMES = {"paper", "soft", "ink", "muted", "accent", "dark", "on-dark",
               "on-dark-muted", "on-dark-accent", "line", "line-dark", "signal",
               "scrim-color", "scrim-stop", "grid-tint", "grid-line"}

DECOR = {"linear-gradient": "渐变", "radial-gradient": "渐变", "border-radius": "圆角",
         "box-shadow": "阴影", "backdrop-filter": "滤镜", "filter": "滤镜"}


def _family_css(root, p):
    """冻结的家族 CSS：优先 design.css，其次按 family.sha256 指纹找。"""
    styles = [s for s in (p.get("styles") or []) if isinstance(s, str)]
    for rel in styles:
        if os.path.basename(rel) == "design.css":
            return rel
    return styles[0] if styles else None


def _read(path):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except OSError:
        return ""


def _strip(css):
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    # 媒体查询里的字号同样算本书排版，保留；只去掉 @page 等已由其他检查负责的块
    return css


def family_ladder(css):
    """从家族 CSS 的 --fl-size-* 读出字阶（px）。"""
    values = set()
    for _, raw in SIZE_TOKEN.findall(css):
        try:
            values.add(round(float(raw), 2))
        except ValueError:
            pass
    return sorted(values)


def allowed_sizes(ladder):
    """字阶值 + 最大字阶的整数倍（显式放大的装饰字）。"""
    allowed = set(ladder)
    if ladder:
        top = ladder[-1]
        allowed.update({round(top * 2, 2), round(top * 3, 2)})
    return allowed


def _is_rhythm(name):
    return name.startswith(RHYTHM_PREFIX)


def _is_color(name):
    return name.replace("--fl-", "") in COLOR_NAMES


def collect_css(root, p, family_rel):
    """本书自己的 CSS 文本（不含家族 CSS）：styles 其余项 + lang/*.css + edits.css。"""
    out, seen = [], set()
    for rel in p.get("styles") or []:
        if isinstance(rel, str) and rel != family_rel and rel not in seen:
            seen.add(rel)
            out.append((rel, _strip(_read(os.path.join(root, rel)))))
    for sub in ("lang", "."):
        d = os.path.join(root, sub)
        if not os.path.isdir(d):
            continue
        for name in sorted(os.listdir(d)):
            if not name.endswith(".css") or name == os.path.basename(family_rel or ""):
                continue
            rel = os.path.join(sub, name) if sub != "." else name
            if rel in seen:
                continue
            seen.add(rel)
            out.append((rel, _strip(_read(os.path.join(d, name)))))
    return out


def _checked_version(p):
    """2.2 起才把字阶与基线写成明确规则；更早的冻结项目按其当时版本审，不被本条追溯。"""
    version = str((p.get("family") or {}).get("version") or "0")
    try:
        major, minor = (version.split(".") + ["0"])[:2]
        return (int(major), int(minor)) >= (2, 2)
    except ValueError:
        return False


def check_style(rep, root, p):
    family_rel = _family_css(root, p)
    if not family_rel or not _checked_version(p):
        return
    family_css = _strip(_read(os.path.join(root, family_rel)))
    ladder = family_ladder(family_css)
    if len(ladder) < 6:            # 没有可判定的字阶，只做能否定性判断的部分
        ladder = []
    allowed = allowed_sizes(ladder)
    waiver = (p.get("style_waiver") or "").strip()

    def fail(code, where, msg):
        text = f"{msg}（已授权放宽：{waiver}）" if waiver else msg
        (rep.warn if waiver else rep.error)(code, where, text)

    rhythm_hits, color_hits, color_files = {}, {}, {}
    for rel, css in collect_css(root, p, family_rel):
        for name, raw in DECL.findall(css):
            if _is_rhythm(name):
                rhythm_hits.setdefault(name, rel)
            elif _is_color(name):
                color_hits.setdefault(name, raw.strip())
                color_files[name] = rel
        # 字号：只查 px，em/%/var() 无法静态求值
        for raw in (FONT_SIZE.findall(css) if ladder else ()):
            for num in re.findall(r"([0-9.]+)px", raw):
                value = round(float(num), 2)
                if value not in allowed:
                    fail("style.offladder", rel,
                         f"字号 {num}px 不在字阶上（{_fmt(ladder)}，或最大字阶的 2/3 倍）："
                         "本书排版应取家族字阶，不另造字号")
        counts = {label: css.count(k) for k, label in DECOR.items() if css.count(k)}
        if counts:
            total = sum(counts.values())
            rep.warn("style.decor", rel,
                     "本书 CSS 用了 " + "、".join(f"{k}{v} 处" for k, v in counts.items()) +
                     f"（共 {total} 处）：渐变/圆角/阴影/滤镜须能说明用途，否则改用排印与网格承担")
        custom = {c for c in re.findall(r"\.([a-z][a-z0-9-]*)", css) if not c.startswith("fl-")}
        if len(custom) >= 12:
            rep.warn("style.custom", rel,
                     f"本书 CSS 定义了 {len(custom)} 个自定义类：" +
                     "、".join(sorted(custom)[:6]) + " …：若整本视觉语言已由它们承担，"
                     "请确认这只是克制的品牌适配，而不是绕开家族规则")

    if rhythm_hits:
        fail("style.token", sorted(set(rhythm_hits.values()))[0],
             "本书 CSS 覆写了家族节奏 token（字号/间距/行距/基线属家族基因）：" +
             "、".join(f"{n}（{w}）" for n, w in sorted(rhythm_hits.items())[:8]) +
             (f" 等 {len(rhythm_hits)} 项" if len(rhythm_hits) > 8 else ""))
    if color_hits:
        rep.warn("style.brand", sorted({w for w in color_files.values()})[0],
                 f"本书 CSS 覆写了 {len(color_hits)} 个颜色 token（品牌适配允许，但需在 brief 记明并重测对比度）：" +
                 "、".join(sorted(color_hits)[:8]) + (" …" if len(color_hits) > 8 else ""))

    # 内联字号：书页里直接写死的 px 同样绕过字阶
    book = os.path.join(root, p.get("entry") or "book.html")
    for attr in (STYLE_ATTR.findall(_read(book)) if ladder else ()):
        for raw in FONT_SIZE.findall(attr):
            for num in re.findall(r"([0-9.]+)px", raw):
                value = round(float(num), 2)
                if value not in allowed:
                    fail("style.offladder", os.path.relpath(book, root),
                         f"内联字号 {num}px 不在字阶上：页面上的字号也应取家族字阶")


def _fmt(ladder):
    return " / ".join(f"{v:g}" for v in ladder) if ladder else "无"
