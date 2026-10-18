#!/usr/bin/env bash
# 新建品牌包：bash hb/new_brand.sh <名字> "<品牌显示名>" [logo.svg] [A色] [B色]
#   → brands/<名字>/brand.yaml（从 allas 的结构复制，改好名字、色值）+ logo.svg（没给 logo 就用 Comfortaa 生成文字标占位）
#   → brands/index.yaml 加一条 → brands/<名字>/preview.jpg（封面 + 章节页 | 卡片 的样张）
# 之后打开 brand.yaml 补：字体、页脚、封底联系方式、口吻、禁忌（workflows/brand.md）。
set -eo pipefail
HB="$(cd "$(dirname "$0")" && pwd)"; R="$(dirname "$HB")"
[ -n "$2" ] || { echo "用法：bash $0 <名字> \"<品牌显示名>\" [logo.svg] [A色] [B色]"; exit 2; }
N="$1"; NAME="$2"; LOGO="$3"; A="${4:-#002BA5}"; B="${5:-#FFE893}"
case "$N" in ""|*[!A-Za-z0-9_-]*) echo "ERROR: 品牌名只允许字母/数字/下划线/连字符：$N"; exit 2;; esac   # 防 ../ 逃逸
D="$R/brands/$N"; [ -e "$D/brand.yaml" ] && { echo "品牌包 $N 已存在：$D"; exit 1; }
mkdir -p "$D"
if [ -n "$LOGO" ]; then cp "$LOGO" "$D/logo.svg"; else python3 "$HB/wordmark.py" "$NAME" comfortaa "$D/logo.svg" --weight 700; fi
python3 - "$R" "$N" "$NAME" "$A" "$B" <<'PY'
import sys, os, re, yaml
R, N, NAME, A, B = sys.argv[1:]
t = open(os.path.join(R, 'brands', 'allas', 'brand.yaml'), encoding='utf-8').read()
t = re.sub(r'^# All As AI 品牌包.*?\n(?=name:)', f'# {NAME} 品牌包\n', t, flags=re.S)
t = t.replace('All As AI', NAME).replace('Alpha International AI Edtech PTE LTD', '〔公司全称〕').replace('www.alphaedu.si', '〔网址〕')
t = re.sub(r"primary: '#[0-9A-Fa-f]+'.*", f"primary: '{A}'           # 主色", t); t = re.sub(r"accent: '#[0-9A-Fa-f]+'  .*", f"accent: '{B}'            # 强调色", t)
t = re.sub(r"    (secondary_bg|secondary_accent|MUT): '#[0-9A-Fa-f]+'.*\n", '', t)   # 其余角色由引擎推出（次级背景 = 背景混 7% 主色）；需要时按品牌规范加
t = re.sub(r"body_text: '#[0-9A-Fa-f]+'.*", "body_text: '#17211C'         # 正文：深墨", t)
t = re.sub(r"  color_mode: \w+.*", "  color_mode: auto     # auto：主色和强调色是撞色就 clash，同色系 / 对比不够就 accent（点缀）", t)
t = re.sub(r'voice:.*', 'voice: 〔品牌口吻一句话〕', t); t = re.sub(r'dont:\n(  - .*\n)+', 'dont:\n  - 〔禁忌〕\n', t)
open(os.path.join(R, 'brands', N, 'brand.yaml'), 'w', encoding='utf-8').write(t)
idx = os.path.join(R, 'brands', 'index.yaml')
open(idx, 'a', encoding='utf-8').write(f"{N}:\n  name: {NAME}\n  zh: 〔一句话介绍〕\n  use: 〔用在哪些材料〕\n  colors: '{A} × {B}'\n  logo: {'logo.svg' if sys.argv else ''}\n")
PY
mkdir -p "$D/.preview"; printf 'book:\n  brand: %s\n' "$N" > "$D/.preview/brand.yaml"
python3 "$HB/directions.py" "$D/.preview" "$N=brand:$N" --title "$NAME" >/dev/null && cp "$D/.preview/.qa/directions.jpg" "$D/preview.jpg" && rm -rf "$D/.preview"
echo "品牌包已建立：$D（样张 preview.jpg）。下一步：补全 brand.yaml 的字体、配色其余键、联系方式、口吻；书里写 book.brand: $N"
