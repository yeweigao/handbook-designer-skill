# 被 run.sh / export.sh / check_env.sh source：让 node 能找到 playwright。
# 先看 node 自己能不能找到；找不到再依次试常见位置。都没有 → 提示安装。
_hb_has_pw(){ node -e "require('playwright')" >/dev/null 2>&1; }
if ! _hb_has_pw; then
  for d in "$HB/node_modules" "$HB/../node_modules" "$PWD/node_modules" "$(npm root -g 2>/dev/null)" \
           /usr/local/lib/node_modules /usr/lib/node_modules /opt/homebrew/lib/node_modules; do
    [ -n "$d" ] && [ -d "$d/playwright" ] && export NODE_PATH="$d${NODE_PATH:+:$NODE_PATH}" && break
  done
fi
_hb_has_pw || { echo "找不到 playwright。安装：cd \"$HB\" && npm install && npx playwright install chromium"; exit 1; }
# playwright 自带 chromium 启动失败时的兜底浏览器：.app 不在 PATH 里，先按固定路径找，再找 PATH
if [ -z "$HB_CHROME" ]; then
  for c in "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
           "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge" \
           "/Applications/Chromium.app/Contents/MacOS/Chromium"; do
    [ -x "$c" ] && HB_CHROME="$c" && break
  done
  if [ -z "$HB_CHROME" ]; then
    for c in chromium chromium-browser google-chrome; do
      command -v "$c" >/dev/null 2>&1 && HB_CHROME="$(command -v "$c")" && break
    done
  fi
  [ -n "$HB_CHROME" ] && export HB_CHROME
fi
