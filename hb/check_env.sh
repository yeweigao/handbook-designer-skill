#!/usr/bin/env bash
# 环境自检：bash hb/check_env.sh     第一次在新环境使用本 skill 时跑一次
HB="$(cd "$(dirname "$0")" && pwd)"; ok=1
say(){ printf '%-6s %s\n' "$1" "$2"; }
command -v python3 >/dev/null && say OK python3 || { say FAIL "python3 未安装"; ok=0; }
python3 -c "import yaml,PIL,numpy,fontTools" 2>/dev/null && say OK "pyyaml / pillow / numpy / fonttools" || { say FAIL "pip install -r \"$HB/requirements.txt\""; ok=0; }
python3 -c "import brotli" 2>/dev/null && say OK "brotli（woff2）" || say WARN "没有 brotli：字体会存成稍大的 woff（pip install brotli）"
python3 -c "import pikepdf" 2>/dev/null && say OK "pikepdf（可编辑 PDF）" || say WARN "没有 pikepdf：不会生成可编辑 PDF（pip install pikepdf）"
python3 -c "import qrcode" 2>/dev/null && say OK "qrcode（二维码块）" || say WARN "没有 qrcode：不能用 qr 二维码块（pip install qrcode），可以改用二维码图片 + figure"
python3 -c "import spellchecker" 2>/dev/null && say OK "pyspellchecker（plan.py 英文拼写）" || say WARN "没有 pyspellchecker：plan.py 不查英文拼写（pip install pyspellchecker）"
command -v pdfimages >/dev/null && say OK "poppler（PDF 里的图片抽取）" || say WARN "没有 poppler：PDF 资料里的图片抽不出来（mac：brew install poppler）"
command -v node >/dev/null && say OK node || { say FAIL "node 未安装（需要 Node 18+）"; ok=0; }
( source "$HB/env.sh" >/dev/null && cd "$HB" && node -e "
const {chromium}=require('playwright');
chromium.launch({args:['--no-sandbox']}).then(b=>b.close()).catch(async e=>{
  const exe=require('child_process').execSync('which chromium || which chromium-browser || which google-chrome || true').toString().trim();
  if(!exe) throw e; const b=await chromium.launch({executablePath:exe,args:['--no-sandbox']}); await b.close();})
.then(()=>process.exit(0)).catch(e=>{console.error(String(e).slice(0,200));process.exit(1)})" ) \
  && say OK "playwright + chromium" || { say FAIL "playwright/chromium 不可用：cd \"$HB\" && npm install && npx playwright install chromium"; ok=0; }
python3 "$HB/fonts.py" list | sed -n '/^字体/,/^$/p' | grep -E "未下载" >/dev/null && say WARN "部分中文字体未下载（不影响构建，会用系统字体代替）：python3 $HB/fonts.py fetch" || say OK "字体齐全"
if command -v markitdown >/dev/null || command -v pandoc >/dev/null || python3 -c "import docx" 2>/dev/null; then say OK "docx 转换（markitdown / pandoc / python-docx 任一）"
else say WARN "无 docx 转换工具：pip install 'markitdown[docx]'（只有 .md/.txt 原文时可忽略）"; fi
[ $ok = 1 ] && echo "环境就绪 ✓" || { echo "请先修复 FAIL 项"; exit 1; }
