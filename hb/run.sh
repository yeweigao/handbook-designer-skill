#!/usr/bin/env bash
# 一键构建 + QA：  bash hb/run.sh <project_dir>
# 依次：hb.py(排版+烘焙纸面) → shot bg → dark.py(渐进压暗) → shot(截图+溢出/重叠) → qa.py(对比度) → check_copy(原文核对) → montage(拼版图) → doctor(改法 + 总门禁)
# 退出码：0 = GATE PASS；非 0 = 构建出错或 GATE FAIL（溢出/重叠/对比度/缺字任一不为 0）。拼版图在 FAIL 时也会生成，方便看问题。
set -eo pipefail
HB="$(cd "$(dirname "$0")" && pwd)"; [ -n "$1" ] || { echo "用法：bash $0 <project_dir>"; exit 2; }
P="$(cd "$1" && pwd)"
source "$HB/env.sh"
python3 "$HB/hb.py" "$P"
mkdir -p "$P/.qa"; rm -f "$P"/.qa/pg*.png "$P"/.qa/bg*.png "$P"/.qa/copy.txt   # 清掉上一轮结果，防止页数变少后拼版里混进旧页
node "$HB/shot.js" "$P" bg >/dev/null
(cd "$P" && python3 "$HB/dark.py" | tail -3)
node "$HB/shot.js" "$P" | tail -1
(cd "$P" && { python3 "$HB/qa.py" > .qa/contrast.txt || true; } && tail -6 .qa/contrast.txt)
if [ -f "$P/doc.md" ]; then python3 "$HB/check_copy.py" "$P" > "$P/.qa/copy.txt" || true; cat "$P/.qa/copy.txt"; else echo "（没有 doc.md，跳过原文核对）"; fi
python3 "$HB/montage.py" "$P" >/dev/null && echo "看图：$(ls "$P"/.qa/review_*.jpg | tr '\n' ' ')"
python3 "$HB/brief.py" "$P"   # AI 配图位 → image_brief.md（没有配图位时不输出）
python3 "$HB/doctor.py" "$P"
