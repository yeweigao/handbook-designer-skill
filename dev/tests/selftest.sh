#!/usr/bin/env bash
# 原生链路集成自检：--quick 仅静态与契约；完整模式另跑 core 回归和真实样册。
set -euo pipefail
TESTS="$(cd "$(dirname "$0")" && pwd)"
R="$(cd "$TESTS/../.." && pwd)"
cd "$R"
QUICK=0
if [ "${1:-}" = "--quick" ]; then QUICK=1; shift; fi
if [ "$#" -ne 0 ]; then echo '用法：bash dev/tests/selftest.sh [--quick]' >&2; exit 2; fi
T="$(mktemp -d "${TMPDIR:-/tmp}/hb-native-selftest.XXXXXX")"
echo "证据目录：$T"
trap 'echo "SELFTEST: FAIL（证据保留在 ${T}）" >&2' ERR
command -v node >/dev/null
command -v python3 >/dev/null
node --version
python3 --version

echo '1 · 文档、归档边界与语法'
python3 - "$R" <<'PY' | tee "$T/static.log"
import ast, json, re, subprocess, sys
from pathlib import Path
from urllib.parse import unquote
r = Path(sys.argv[1])
skill = (r/'SKILL.md').read_text()
assert len(skill) <= 12000, f'SKILL.md {len(skill)} 字符，超过 12000'
docs = [r/'SKILL.md', r/'dev/maintenance.md']
for d in ('workflows', 'references', 'templates', 'purposes', 'brands'):
    docs += sorted((r/d).rglob('*.md'))
for p in docs:
    text = p.read_text()
    assert 'book.yaml' not in text, f'{p}: 旧作者源引用'
    for link in re.findall(r'\[[^\]]*\]\(([^\s)]+)(?:\s+"[^"]*")?\)', text):
        if re.match(r'^[a-z][a-z0-9+.-]*:', link) or link.startswith('#'):
            continue
        target = unquote(link.split('#', 1)[0])
        assert (p.parent/target).exists(), f'{p}: 链接不存在 {target}'
assert not list((r/'templates').glob('*.yaml')), '旧模板仍在活跃入口'
assert not list((r/'purposes').glob('*.yaml')), '旧用途配置仍在活跃入口'
assert not list((r/'brands').rglob('*.yaml')), '旧品牌配置仍在活跃入口'
assert not [p for p in (r/'hb').iterdir() if p.suffix in ('.py', '.js', '.css', '.sh')], '旧引擎脚本仍在 hb 根目录'
archive = r/'dev/archive/yaml-engine'
v = json.loads((archive/'VERSION.json').read_text())
assert v['status'] == 'retired' and re.fullmatch('[0-9a-f]{40}', v['source_commit'])
for name in ('hb/run.sh', 'hb/hb.py', 'hb/fill.js', 'templates/book.layouts.yaml', 'dev/tests/test_adapt.py'):
    assert (archive/name).is_file(), f'归档缺失 {name}'
for p in sorted((r/'hb/core').rglob('*.py')) + sorted((r/'dev/tests/core').glob('*.py')):
    ast.parse(p.read_text(), filename=str(p), feature_version=(3,10))
for p in (r/'hb/core').rglob('*'):
    if p.is_file() and p.suffix in ('.mjs', '.py'):
        assert 'book.yaml' not in p.read_text(), f'{p}: 旧作者源引用'
for p in sorted((r/'hb/core').rglob('*.mjs')) + sorted((r/'dev/tests/core').glob('*.mjs')):
    subprocess.run(['node', '--check', str(p)], check=True)
print(f'PASS: SKILL.md {len(skill)} 字符，{len(docs)} 份文档链接、原生入口/归档边界、Python 3.10 语法与 JS 语法')
PY
echo '2 · 契约正例与反例'
python3 hb/core/validate.py dev/fixtures/contract/minimal-zh | tee "$T/validate-minimal.log"
python3 hb/core/validate.py dev/fixtures/contract/bilingual | tee "$T/validate-bilingual.log"
python3 -m unittest discover -s dev/tests/core -p 'test_*.py' 2>&1 | tee "$T/validate-tests.log"
if [ "$QUICK" -eq 1 ]; then
  echo "SELFTEST: PASS（quick；浏览器、PDF、导出与真实样册 unverified；证据 ${T}）"
  exit 0
fi

echo '3 · 浏览器、PDF 环境与 core 全链路回归'
for tool in pdfinfo pdftoppm pdffonts pdftotext; do command -v "$tool" >/dev/null; done
python3 -c 'import pikepdf, PIL, fontTools, numpy'
node --input-type=module -e "import { launch } from './hb/core/browser.mjs'; const r = await launch(); console.log(r.info); await r.browser.close();" | tee "$T/browser.log"
# 明确串行运行测试文件，避免多个 Chromium/字体扩充进程同时争用内存。
node --test --test-concurrency=1 dev/tests/core/*.test.mjs 2>&1 | tee "$T/core-tests.log"

echo '4 · 真实样册公开入口（隔离副本，不覆盖已审样册记录）'
python3 - "$R" "$T" <<'PY'
import shutil, sys
from pathlib import Path
r, t = map(Path, sys.argv[1:])
for name in ('product-brochure', 'nature-camp'):
    shutil.copytree(r/'dev/samples/native'/name, t/name, ignore=shutil.ignore_patterns('.build', '.qa', 'out'))
PY
for name in product-brochure nature-camp; do
  node hb/core/cli.mjs check "$T/$name" 2>&1 | tee "$T/$name-check.log"
  node hb/core/cli.mjs verify "$T/$name" 2>&1 | tee "$T/$name-verify.log"
done
echo "SELFTEST: PASS（技术回归；视觉审稿及外部 Folio 跳过项见日志；证据 ${T}）"
