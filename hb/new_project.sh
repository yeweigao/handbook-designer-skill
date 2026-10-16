#!/usr/bin/env bash
# 新建项目： bash hb/new_project.sh <project_dir> [原文.pptx|.docx|.pdf|.md|.txt] [图片目录]
# .pptx / 带图的 .docx .pdf：自动抽出图片到 photos/，清单 images.md，缩略图 photos/_contact.jpg（见 extract.py）
# 每轮“用户改版”新建一个目录（v1、v2…），旧版留着对照（check_copy.py 可以拿旧版 book.html 当参照）。
# 已有项目（目录里已有 book.yaml 或 doc.md）默认拒绝覆盖；确定要覆盖时：FORCE=1 bash hb/new_project.sh …
set -eo pipefail; HB="$(cd "$(dirname "$0")" && pwd)"
[ -n "$1" ] || { echo "用法：bash $0 <project_dir> [原文] [图片目录]"; exit 2; }
P="$1"
case "$(cd "$(dirname "$P")" 2>/dev/null && pwd)/$(basename "$P")" in /|/root|/home|"$HOME"|/Users|/tmp) echo "项目目录不能是 $P"; exit 2;; esac
if [ -z "$FORCE" ] && { [ -f "$P/book.yaml" ] || [ -f "$P/doc.md" ]; }; then
  echo "$P 已经是一个项目（有 book.yaml/doc.md）。请换一个新目录（如 _v2），或 FORCE=1 覆盖原文与骨架。"; exit 1; fi
[ -n "$2" ] && [ ! -f "$2" ] && { echo "找不到原文：$2"; exit 1; }
[ -n "$3" ] && [ ! -d "$3" ] && { echo "找不到图片目录：$3"; exit 1; }
mkdir -p "$P/photos"
if [ -n "$3" ]; then
  find "$3" -maxdepth 1 -type f \( -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.png' -o -iname '*.webp' \) -exec cp {} "$P/photos/" \;
  c=$(ls "$P/photos" | wc -l | tr -d ' '); echo "照片：$c 张"; [ "$c" -gt 0 ] || echo "警告：$3 里没有 jpg/png/webp 照片"
  ls "$3" | grep -iE 'credit|license|授权|来源|source' >/dev/null 2>&1 && cp "$3"/*[Cc]redit* "$3"/*[Ll]icen* "$3"/*授权* "$3"/*来源* "$P/" 2>/dev/null || true
fi
if [ -n "$2" ]; then
  case "$(echo "$2" | tr 'A-Z' 'a-z')" in
    *.pptx) python3 "$HB/extract.py" "$2" "$P" && python3 "$HB/doc2yaml.py" "$P/doc.md" "$P" ;;   # PPT：文字 + 图片 + 每页对应关系
    *.docx|*.pdf) python3 "$HB/doc2yaml.py" "$2" "$P"; python3 "$HB/extract.py" "$2" "$P" --images-only || echo "（图片抽取跳过：$2）" ;;
    *) python3 "$HB/doc2yaml.py" "$2" "$P" ;;
  esac
  [ -s "$P/doc.md" ] || { echo "原文转换结果为空，请检查 $2"; exit 1; }
elif [ ! -f "$P/book.yaml" ]; then   # 没给原文 = 试跑样例（无图风格，不需要照片）
  cp "$HB/../templates/book.nophoto.zh.yaml" "$P/book.yaml"
  echo "（未提供原文：已放入无图样例 book.yaml，可直接 run.sh 试跑）"
fi
echo "项目已建立：$P   下一步：照 book.draft.yaml 写 $P/book.yaml（结构参考 templates/），然后 bash $HB/run.sh $P"
