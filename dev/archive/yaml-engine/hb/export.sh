#!/usr/bin/env bash
# 导出交付物：bash hb/export.sh <project_dir> [文件名] [--draft]
# 导出门禁：必须是 run.sh 通过（GATE PASS）之后、没再改过 book.yaml / 原文 / 照片的版本（gate.py check）。
#   只想先给人看一眼：--draft（不查门禁，每页打“草稿 DRAFT”水印，文件名带 _草稿/_draft）
# 导出后跑 postflight.py：页数、文件大小、字体、书签数、链接、低清图片 → .qa/postflight.md，并记进 .qa/log.md
#   同时生成 .qa/print_checklist.md（交印清单：低 DPI 图 + 装订建议）并拷进 out/
# → <project>/out/<名>.pdf（A4 校样 PDF：成品尺寸、无出血/裁切线，带书签与标签结构；字体为本书用字子集，文件小）
#   <名>_可编辑.pdf（同一版式，字体完整嵌入常用字库，拿到的人可直接在 PDF 编辑器里改字加字；较大，耗时 1–4 分钟；HB_NO_EDITABLE=1 跳过）
#   <名>.html（单文件，可直接发给别人在浏览器打开/打印）
#   <名>_源文件.zip / _source.zip（book.yaml + 实际使用的照片目录 + 烘焙图 + 字体 + 项目根目录的 .md：原文、图片来源/授权清单 images.yaml 等）
set -eo pipefail
HB="$(cd "$(dirname "$0")" && pwd)"
DRAFT=""; ARGS=(); for a in "$@"; do [ "$a" = "--draft" ] && DRAFT=1 || ARGS+=("$a"); done; set -- "${ARGS[@]}"
[ -n "$1" ] || { echo "用法：bash $0 <project_dir> [文件名] [--draft]"; exit 2; }
P="$(cd "$1" && pwd)"; N="${2:-handbook}"
source "$HB/env.sh"
[ -f "$P/book.html" ] || { echo "先运行 bash $HB/run.sh $P（多语言的书：导出 $P/<语言> 子目录）"; exit 1; }
if [ -n "$DRAFT" ]; then export HB_DRAFT=1; echo "草稿导出：不查门禁，每页带水印"
else python3 "$HB/gate.py" check "$P" || { echo "（只想先给人看：bash $0 $1 ${2:-handbook} --draft）"; exit 1; }; fi
read -r LANGV PHOTOS < <(python3 -c "import yaml,sys;b=(yaml.safe_load(open(sys.argv[1],encoding='utf-8')) or {}).get('book',{});print(str(b.get('lang','zh')).split('-')[0], b.get('photos','photos'))" "$P/book.yaml")
case "$LANGV" in zh|ja|ko) Z="${N}_源文件.zip"; [ -n "$DRAFT" ] && N="${N}_草稿";; *) Z="${N}_source.zip"; [ -n "$DRAFT" ] && N="${N}_draft";; esac
mkdir -p "$P/out"
node "$HB/pdf.js" "$P" "$P/out/$N.pdf"
python3 - "$P/out/$N.pdf" <<'PY'
import re,sys
b=open(sys.argv[1],'rb').read(); t3=len(re.findall(rb'/Subtype\s*/Type3',b))
if t3: print(f'警告：PDF 里有 {t3} 处 Type 3 字体（通常是某个字体没下载、回退到了系统字体），这些文字在 Acrobat 里无法编辑、部分印厂也会退稿。'
            '先运行 python3 hb/fonts.py fetch 下载字体，再重新 run.sh + export.sh。')
else: print('PDF 字体检查：全部为可编辑的 TrueType 字体（无 Type 3）✓')
PY
# PDF 书签（F09）：pdf.js 的 Chromium 打印不产生 outline，用 pikepdf 补。
# 结构来源：plan.txt 的版式（FULL = 章节页）+ book.html 每页的标题元素（.cn-num 章节号 / .cn-disp 标题）。
# 一级：封面、章节页、封底；二级：有标题的内容页。没有 pikepdf：WARN 后跳过、不拦导出（postflight 会断言 outline ≥ 1）。
add_bookmarks() {
python3 - "$1" "$P/plan.txt" "$P/book.html" <<'PY'
import sys, re, os, html as H
pdf_path, plan_path, book_path = sys.argv[1:4]
try:
    import pikepdf
except ImportError:
    print('提示：PDF 书签需要 pikepdf（pip install pikepdf），本次跳过——目录链接仍可点'); sys.exit(0)
h = open(book_path, encoding='utf-8').read()
pages = {}   # 成品页码 → (章节号, 页面标题)
for seg in re.split(r'(?=<section)', h):
    m = re.search(r'data-n="(\d+)"', seg)
    if not m: continue
    body = seg[:seg.find('</section>')] if '</section>' in seg else seg
    num = re.search(r'class="cn-a cn-num[^"]*"[^>]*>([^<]*)<', body)
    chapter = re.search(r'data-chapter="([^"]+)"', body)
    disp = re.search(r'class="cn-disp[^"]*"[^>]*>(.*?)</div>', body, re.S)
    if not disp: disp = re.search(r'class="cn-h cn-ttl[^"]*"[^>]*>(.*?)</div>', body, re.S)
    t = H.unescape(re.sub(r'<[^>]+>', ' ', disp.group(1))) if disp else ''
    pages[int(m.group(1))] = (H.unescape(chapter.group(1)) if chapter else num.group(1).strip() if num else '', re.sub(r'\s+', ' ', t).strip(), bool(chapter))
lay = {}     # 成品页码 → 版式（跨页取起始页）
if os.path.exists(plan_path):
    for l in open(plan_path, encoding='utf-8'):
        f = l.split()
        if len(f) > 1 and re.match(r'^\d+(-\d+)?$', f[0]): lay[int(f[0].split('-')[0])] = f[1]
t0 = re.search(r'<title>(.*?)</title>', h)
ns = sorted(pages)
if not ns: sys.exit(0)
items = [(1, H.unescape(t0.group(1)).strip() if t0 else pages[ns[0]][1] or '封面', ns[0])]   # 一级：封面（用书名）
for n in ns[1:]:
    num, disp, chapter = pages[n]; L = lay.get(n, '')
    if chapter or L == 'FULL': items.append((1, (num + ' · ' if num else '') + (disp or f'第 {n} 页'), n))   # 一级：章节页（合并到PAPER/跨页也保留）
    elif n == ns[-1]: items.append((1, disp or '封底', n))                                    # 一级：封底
    elif disp: items.append((2, disp, n))                                                        # 二级：有标题的内容页
pdf = pikepdf.open(pdf_path)
try:
    with pdf.open_outline() as ol:
        ol.root.clear()
        stack = [ol.root]
        for lv, title, pg in items:
            it = pikepdf.OutlineItem(title, pg - 1)   # pikepdf 用 0 基页码
            while len(stack) > lv: stack.pop()
            stack[-1].append(it); stack.append(it.children)
    tmp = pdf_path + '.bm'; pdf.save(tmp); os.replace(tmp, pdf_path)   # pikepdf 不能原地保存
    print(f'PDF 书签：{len(items)} 个（封面 / 章节 / 页标题）✓')
except Exception as e:
    print(f'提示：PDF 书签补写失败（{type(e).__name__} {str(e)[:80]}），不影响导出')
PY
}
add_bookmarks "$P/out/$N.pdf"
python3 "$HB/standalone.py" "$P/book.html" "$P/out/$N.html"
if grep -q 'data-canvas="xhs"' "$P/book.html"; then node "$HB/pngs.js" "$P" "$P/out/${N}_小红书" 1080; fi   # 小红书画布：每页一张 1080×1440 图
if [ -z "$HB_NO_EDITABLE$DRAFT" ]; then   # 可编辑 PDF：字体完整嵌入常用字库（GB2312 6763 字），别人可以直接在 PDF 编辑器里改字
  if python3 -c "import pikepdf" 2>/dev/null; then
    if python3 "$HB/editable_pdf.py" "$P" "$P/out/${N}_可编辑.pdf" "$P/out/$N.pdf"; then
      add_bookmarks "$P/out/${N}_可编辑.pdf"
    else
      echo "提示：可编辑 PDF 生成失败（看上面的报错）；普通版 PDF 不受影响"
    fi
  else
    echo "提示：未生成可编辑 PDF（需要 pikepdf：pip install pikepdf）"
  fi
fi
cd "$P" && rm -f "out/$Z"
EXTRA=""; [ -f images.yaml ] && EXTRA="images.yaml"   # 逐图来源/授权/DPI/页码记录（F10：存在才打）
MDS=$(ls *.md 2>/dev/null || true)
zip -qry "out/$Z" book.yaml book.html map.json img fonts "$PHOTOS" $MDS $EXTRA -x 'img/*_base.jpg'   # -y：存符号链接本身（subset.py 会造链），不把外链目标内容打进交付包
rm -f "$P"/out/review_*.jpg 2>/dev/null || true
cp "$P"/.qa/review_*.jpg "$P/out/" 2>/dev/null || true
[ -n "$(ls "$P"/images.yaml "$P"/*credit* "$P"/*source* "$P"/*授权* "$P"/*来源* 2>/dev/null)" ] || echo "提示：项目里没有图片来源/授权清单（如 image_credits.md）。用了第三方照片时请补上再交付。"
python3 "$HB/postflight.py" "$P" "$P/out/$N.pdf" ${DRAFT:+--draft}
cp "$P"/.qa/print_checklist.md "$P/out/" 2>/dev/null || true   # 交印清单：低 DPI 图 + 装订建议（postflight 生成）
ls -lh "$P/out"
