#!/usr/bin/env bash
# 导出交付物：bash hb/export.sh <project_dir> [文件名]
# → <project>/out/<名>.pdf（A4 校样 PDF：成品尺寸、无出血/裁切线，带书签与标签结构；字体为本书用字子集，文件小）
#   <名>_可编辑.pdf（同一版式，字体完整嵌入常用字库，拿到的人可直接在 PDF 编辑器里改字加字；较大，耗时 1–4 分钟；HB_NO_EDITABLE=1 跳过）
#   <名>.html（单文件，可直接发给别人在浏览器打开/打印）
#   <名>_源文件.zip / _source.zip（book.yaml + 实际使用的照片目录 + 烘焙图 + 字体 + 项目根目录的 .md：原文、图片来源/授权清单等）
set -eo pipefail
HB="$(cd "$(dirname "$0")" && pwd)"; [ -n "$1" ] || { echo "用法：bash $0 <project_dir> [文件名]"; exit 2; }
P="$(cd "$1" && pwd)"; N="${2:-handbook}"
source "$HB/env.sh"
[ -f "$P/book.html" ] || { echo "先运行 bash $HB/run.sh $P"; exit 1; }
read -r LANGV PHOTOS < <(python3 -c "import yaml,sys;b=(yaml.safe_load(open(sys.argv[1],encoding='utf-8')) or {}).get('book',{});print(str(b.get('lang','zh')).split('-')[0], b.get('photos','photos'))" "$P/book.yaml")
case "$LANGV" in zh|ja|ko) Z="${N}_源文件.zip";; *) Z="${N}_source.zip";; esac
mkdir -p "$P/out"
node "$HB/pdf.js" "$P" "$P/out/$N.pdf"
python3 - "$P/out/$N.pdf" <<'PY'
import re,sys
b=open(sys.argv[1],'rb').read(); t3=len(re.findall(rb'/Subtype\s*/Type3',b))
if t3: print(f'警告：PDF 里有 {t3} 处 Type 3 字体（通常是某个字体没下载、回退到了系统字体），这些文字在 Acrobat 里无法编辑、部分印厂也会退稿。'
            '先运行 python3 hb/fonts.py fetch 下载字体，再重新 run.sh + export.sh。')
else: print('PDF 字体检查：全部为可编辑的 TrueType 字体（无 Type 3）✓')
PY
python3 "$HB/standalone.py" "$P/book.html" "$P/out/$N.html"
if [ -z "$HB_NO_EDITABLE" ]; then   # 可编辑 PDF：字体完整嵌入常用字库（GB2312 6763 字），别人可以直接在 PDF 编辑器里改字
  python3 -c "import pikepdf" 2>/dev/null && python3 "$HB/editable_pdf.py" "$P" "$P/out/${N}_可编辑.pdf" "$P/out/$N.pdf" \
    || echo "提示：未生成可编辑 PDF（需要 pip install pikepdf）"
fi
cd "$P" && rm -f "out/$Z"
MDS=$(ls *.md 2>/dev/null || true)
zip -qr "out/$Z" book.yaml book.html map.json img fonts "$PHOTOS" $MDS -x 'img/*_base.jpg'
cp "$P"/.qa/review_*.jpg "$P/out/" 2>/dev/null || true
[ -n "$(ls "$P"/*credit* "$P"/*source* "$P"/*授权* "$P"/*来源* 2>/dev/null)" ] || echo "提示：项目里没有图片来源/授权清单（如 image_credits.md）。用了第三方照片时请补上再交付。"
ls -lh "$P/out"
