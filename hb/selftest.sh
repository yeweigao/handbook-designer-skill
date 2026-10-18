#!/usr/bin/env bash
# 改了引擎 / 文档之后的自检：bash hb/selftest.sh [--quick]
#   1 代码能编译（python3 / node）  2 yaml 都能读（模板、品牌包、用途方法）  3 文档里提到的文件都存在
#   4 常驻文档（SKILL.md）没超预算    5 （非 --quick）所有模板中英构建 GATE PASS + 品牌包 + A5 / 小红书画布冒烟
# 全部通过才算改完（维护规则见 references/maintenance.md）。
set -o pipefail
HB="$(cd "$(dirname "$0")" && pwd)"; R="$(dirname "$HB")"; T="${TMPDIR:-/tmp}/hb_selftest_$$"; FAIL=0
ok(){ echo "  ✓ $1"; }; bad(){ echo "  ✗ $1"; FAIL=1; }
echo "1 · 编译"
for f in "$HB"/*.py; do python3 -m py_compile "$f" 2>/dev/null || bad "python 编译失败：$(basename "$f")"; done; ok "python $(ls "$HB"/*.py | wc -l | tr -d ' ') 个"
for f in editor.js shot.js pdf.js pngs.js; do node --check "$HB/$f" 2>/dev/null || bad "node 语法错误：$f"; done
node -e "const s=require('fs').readFileSync('$HB/fill.js','utf8').replace(/<\/?script>/g,'');new Function(s)" 2>/dev/null || bad "fill.js 语法错误"; ok "js"
echo "2 · yaml"
for f in "$R"/templates/*.yaml "$R"/brands/*.yaml "$R"/brands/*/brand.yaml "$R"/purposes/*.yaml; do python3 -c "import yaml,sys;yaml.safe_load(open(sys.argv[1],encoding='utf-8'))" "$f" 2>/dev/null || bad "yaml 读不了：${f#$R/}"; done; ok "模板 / 品牌包 / 用途方法"
python3 - "$R" <<'PY' || FAIL=1
import yaml, os, sys
R = sys.argv[1]; idx = yaml.safe_load(open(f'{R}/purposes/index.yaml', encoding='utf-8'))
for k in idx:
    d = yaml.safe_load(open(f'{R}/purposes/{k}.yaml', encoding='utf-8'))
    miss = [x for x in d.get('order', []) if x not in d.get('roles', {})]
    if miss: print(f'  ✗ purposes/{k}.yaml order 里有没定义的角色：{miss}'); sys.exit(1)
for k in yaml.safe_load(open(f'{R}/brands/index.yaml', encoding='utf-8')) or {}:
    if not os.path.exists(f'{R}/brands/{k}/brand.yaml'): print(f'  ✗ brands/index.yaml 列了 {k}，但没有 brands/{k}/brand.yaml'); sys.exit(1)
print('  ✓ 索引和文件对得上')
PY
echo "3 · 文档引用"
python3 - "$R" <<'PY' || FAIL=1
import re, os, sys, glob
R = sys.argv[1]; bad = []
for md in [f'{R}/SKILL.md'] + glob.glob(f'{R}/workflows/*.md') + glob.glob(f'{R}/references/*.md'):
    t = open(md, encoding='utf-8').read()
    for m in set(re.findall(r'(?<![\w/.])((?:hb|references|workflows|templates|brands|purposes)/[\w./-]+\.(?:py|sh|js|md|yaml|css|jpg))', t)):
        if not os.path.exists(os.path.join(R, m)): bad.append(f'{os.path.relpath(md, R)} → {m}')
for b in bad: print('  ✗ 文件不存在：' + b)
print('  ✓ 文档提到的文件都在' if not bad else ''); sys.exit(1 if bad else 0)
PY
echo "4 · 常驻文档预算"
C=$(wc -m < "$R/SKILL.md" | tr -d ' '); [ "$C" -le 12000 ] && ok "SKILL.md $C 字符（≤ 12000）" || bad "SKILL.md $C 字符，超过 12000：把细节挪到 workflows/ 或 references/，SKILL.md 只留路由和纪律"
[ "$1" = "--quick" ] && { [ $FAIL = 0 ] && echo "SELFTEST: PASS（quick）" || echo "SELFTEST: FAIL"; exit $FAIL; }
echo "5 · 构建回归"
mkdir -p "$T"
for y in "$R"/templates/book.*.yaml; do n=$(basename "$y" .yaml); mkdir -p "$T/$n"; cp "$y" "$T/$n/book.yaml"
  python3 -c "import yaml,sys;b=yaml.safe_load(open(sys.argv[1],encoding='utf-8'));sys.exit(0 if b.get('book',{}).get('style','photo')!='photo' or all(p.get('layout') in ('FULL','ONE','TWO','CARDS','STAGGER','GRID','COLLAGE','MIX','PAPER') for p in b['pages']) else 3)" "$y" || { echo "  - $n：需要照片，跳过"; continue; }
  bash "$HB/run.sh" "$T/$n" > "$T/$n.log" 2>&1 && ok "$n" || bad "$n（日志 $T/$n.log）"; done
mkdir -p "$T/brand"; python3 - "$R" "$T/brand" <<'PY'
import yaml, sys
t = yaml.safe_load(open(f'{sys.argv[1]}/templates/book.layouts.yaml', encoding='utf-8')); b = t['book']
[b.pop(k, None) for k in ('colors', 'fonts', 'style', 'folio')]; b['brand'] = 'allas'
yaml.safe_dump(t, open(f'{sys.argv[2]}/book.yaml', 'w', encoding='utf-8'), allow_unicode=True, sort_keys=False)
PY
bash "$HB/run.sh" "$T/brand" > "$T/brand.log" 2>&1 && ok "品牌包 allas（中英）" || bad "品牌包 allas（日志 $T/brand.log）"
python3 "$HB/subset.py" "$R" "$T/swiss" 1,5,9,10 --src "$R/templates/book.layouts.yaml" --lang zh style=swiss >/dev/null
bash "$HB/run.sh" "$T/swiss" > "$T/swiss.log" 2>&1 && ok "瑞士单色档" || bad "瑞士单色档（日志 $T/swiss.log）"
for st in stijl geo; do python3 "$HB/subset.py" "$R" "$T/$st" 1,4,5,6,9,10 --src "$R/templates/book.layouts.yaml" --lang en style=$st >/dev/null
  bash "$HB/run.sh" "$T/$st" > "$T/$st.log" 2>&1 && ok "风格 $st" || bad "风格 $st（日志 $T/$st.log）"; done
python3 "$HB/subset.py" "$R" "$T/stijl_beat" 1,4,5,6,9,16 --src "$R/templates/book.layouts.yaml" --lang zh style=stijl look=beat >/dev/null
bash "$HB/run.sh" "$T/stijl_beat" > "$T/stijl_beat.log" 2>&1 && ok "风格派节奏画法" || bad "风格派节奏画法（日志 $T/stijl_beat.log）"
for cv in a5 xhs; do python3 "$HB/subset.py" "$R" "$T/$cv" 1,4,13 --src "$R/templates/book.layouts.yaml" --lang zh canvas=$cv >/dev/null
  bash "$HB/run.sh" "$T/$cv" > "$T/$cv.log" 2>&1 && ok "画布 $cv" || bad "画布 $cv（日志 $T/$cv.log）"; done
[ $FAIL = 0 ] && { echo "SELFTEST: PASS"; rm -rf "$T"; } || echo "SELFTEST: FAIL（构建目录 $T 留着查）"
exit $FAIL
