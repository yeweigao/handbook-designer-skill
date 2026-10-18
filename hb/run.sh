#!/usr/bin/env bash
# 一键构建 + QA：  bash hb/run.sh <project_dir> [--proof]
#   --proof   只排封面 + 前两个跨页（第 1–5 页）到 <project>/.proof，给用户确认方向用（16 页以上的书，全本排之前先做这一步）
# 依次：lock.py(和 brief.md 的决定对一遍) → lint.py(页序/节奏提示) → hb.py(排版+烘焙纸面) → shot bg → dark.py(渐进压暗)
#       → shot(截图+溢出/重叠) → qa.py(对比度) → check_copy(原文核对) → montage(拼版图) → doctor(改法 + 总门禁)
#       → gate.json（导出门禁用的指纹）+ .qa/log.md（每次构建记一行，断点续跑看它）
# 退出码：0 = GATE PASS；非 0 = 构建出错或 GATE FAIL。拼版图在 FAIL 时也会生成，方便看问题。
set -eo pipefail
HB="$(cd "$(dirname "$0")" && pwd)"; [ -n "$1" ] || { echo "用法：bash $0 <project_dir> [--proof]"; exit 2; }
P="$(cd "$1" && pwd)"; MODE="$2"
source "$HB/env.sh"
log() { mkdir -p "$P/.qa"; [ -f "$P/.qa/log.md" ] || printf '# 构建日志\n| 时间 | 步骤 | 结果 | 说明 |\n|---|---|---|---|\n' > "$P/.qa/log.md"; echo "| $(date '+%m-%d %H:%M') | $1 | $2 | $3 |" >> "$P/.qa/log.md"; }
if [ "$MODE" = "--proof" ]; then
  rm -rf "$P/.proof"; python3 "$HB/subset.py" "$P" "$P/.proof" proof
  [ -f "$P/brief.md" ] && cp "$P/brief.md" "$P/.proof/"
  RC=0; HB_PROOF=1 bash "$0" "$P/.proof" || RC=$?
  log proof "$([ $RC = 0 ] && echo PASS || echo FAIL)" "样张：.proof/.qa/review_*.jpg"
  echo "试排样张：$(ls "$P"/.proof/.qa/review_*.jpg "$P"/.proof/.qa/compare_*.jpg 2>/dev/null | tr '\n' ' ')"
  echo "→ 发给用户看：方向、字号、撞色、照片处理对不对。确认后在 brief.md 第 3 节记下意见，再排全本：bash $0 $1"
  exit $RC
fi
# 决策锁：brief.md 里用户确认过的设置 vs book.yaml（不一致直接停）
if [ -z "$HB_SUB$HB_NOLOCK" ]; then python3 "$HB/lock.py" "$P" || { log build FAIL "决策不一致（brief.md ≠ book.yaml）"; exit 1; }; fi
# 一份 book.yaml 写了多种语言（{zh: …, en: …} + book.langs）→ 拆成 <project>/<lang> 分别构建、分别检查，最后出逐页对照图
LANGS=$(python3 "$HB/i18n.py" langs "$P/book.yaml")
if [ "$(echo $LANGS | wc -w)" -gt 1 ] && [ -z "$HB_SUB" ]; then
  python3 "$HB/lint.py" "$P" || true
  python3 "$HB/i18n.py" split "$P/book.yaml" || exit 1
  RC=0; for L in $LANGS; do echo "================ $L ================"; HB_SUB=1 bash "$0" "$P/$L" || RC=1; done
  python3 "$HB/compare.py" "$P" $LANGS && echo "中英对照：$(ls "$P"/.qa/compare_*.jpg | tr '\n' ' ')"
  python3 "$HB/gate.py" write "$P" $([ $RC = 0 ] && echo PASS || echo FAIL) $LANGS
  log build "$([ $RC = 0 ] && echo PASS || echo FAIL)" "$LANGS"
  [ $RC = 0 ] && echo "ALL LANGS: GATE PASS" || echo "ALL LANGS: GATE FAIL —— 看上面各语言的提示"
  exit $RC
fi
[ -z "$HB_SUB$HB_PROOF" ] && { python3 "$HB/lint.py" "$P" || true; }
python3 "$HB/hb.py" "$P" || { [ -z "$HB_SUB" ] && log build ERROR "hb.py 报错（看上面的 ERROR）"; exit 1; }
mkdir -p "$P/.qa"; rm -f "$P"/.qa/pg*.png "$P"/.qa/bg*.png "$P"/.qa/copy.txt   # 清掉上一轮结果，防止页数变少后拼版里混进旧页
node "$HB/shot.js" "$P" bg >/dev/null
(cd "$P" && python3 "$HB/dark.py" | tail -3)
node "$HB/shot.js" "$P" | awk '/^\[(字号|书写线)收紧\]/||/^overflow/'
(cd "$P" && { python3 "$HB/qa.py" > .qa/contrast.txt || true; } && tail -6 .qa/contrast.txt)
if [ -f "$P/doc.md" ]; then python3 "$HB/check_copy.py" "$P" > "$P/.qa/copy.txt" || true; cat "$P/.qa/copy.txt"; else echo "（没有 doc.md，跳过原文核对）"; fi
python3 "$HB/montage.py" "$P" >/dev/null && echo "看图：$(ls "$P"/.qa/review_*.jpg | tr '\n' ' ')"
python3 "$HB/brief.py" "$P"   # AI 配图位 → image_brief.md（没有配图位时不输出）
python3 "$HB/images.py" "$P" | tail -4 || true
python3 "$HB/facts.py" "$P" || true
python3 "$HB/colorqa.py" "$P" || true   # 用色比例（60-30-10）：主色整块太多 → [颜色过重]   # 成品里的数字都能在原文 / facts.md 里找到吗   # 图片清单 images.yaml（来源、授权、用在哪页、清晰度）
RC=0; python3 "$HB/doctor.py" "$P" || RC=$?
if [ -z "$HB_SUB" ]; then python3 "$HB/gate.py" write "$P" $([ $RC = 0 ] && echo PASS || echo FAIL); log build "$([ $RC = 0 ] && echo PASS || echo FAIL)" "$(grep -c '' "$P/plan.txt" 2>/dev/null) 个页面"; fi
exit $RC
